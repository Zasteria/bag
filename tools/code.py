#!/usr/bin/env python3
"""Ask the generators where something is, instead of reading them.

`tools/kb.py` did this for the documents and left the larger half untouched:
`mods/where_to_produce/tools/generate.py` alone is six thousand lines and about
eighty-five thousand tokens — more than every document in this repository put
together — with no index at all. A session that needs one effect greps for it
and then reads two-hundred-line slices blind, which cost five to seven thousand
tokens before the question is even answered. That was measured on 2026-09-04,
answering one question about `_edit_drop`.

    python3 tools/code.py edit_drop         where it is, what it costs, what it does
    python3 tools/code.py --show FILE:LINE  print exactly that block
    python3 tools/code.py --map             every generator, every block

The generators are already cut the right way — a function per generated file,
and every emitted script name carries a comment above it — so the index is
mechanical. Four kinds of entry are indexed:

  * a Python `def`, which is what writes a file;
  * an emitted script name, `{MOD_ID}_<name> = {{` inside an f-string, which is
    what the game calls. This is the one a session usually wants, because an
    error log names the script and never the generator;
  * a `window` or a `type` in a hand-written `.gui`;
  * **a comment block in a hand-written `.gui`**, which is where that half of
    the repository keeps what its runs cost. A window is four thousand tokens
    and nobody reads one to find a rule; the paragraph above the widget is the
    rule, and until 2026-09-05 nothing indexed it. `bag_wtp_plan_window.gui`
    had carried «coloured the word with `§Y...§!`, which this widget prints
    literally» since the first build, and the session that needed it put `§`
    into a hundred keys instead.

Sizes are estimated the same way `kb.py` estimates them, and mean the same
thing: what asking for that block will cost.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The generators **and the hand-written interface files**, which is the half this
# index used to miss.
#
# The line here read «a mod's `in_game/` is generated output — greppable, never
# worth indexing», and that was wrong about the windows: five of the six `.gui`
# in `where_to_produce` are written by hand and carry 516 lines of comment
# between them, every line of it something a run paid for. **Nothing indexed
# them.** `kb.py` covers `docs/`, this covered the generators, and the rules
# living in a window's comments were reachable only by knowing they were there.
#
# It cost a whole round trip on 2026-09-05. `bag_wtp_plan_window.gui` had
# carried, since the first build, «coloured the word with `§Y...§!`, which this
# widget prints literally» — correct, and invisible to every tool. The same
# session put `§` into a hundred keys.
#
# Generated files are skipped by their own banner, so a file that says it was
# generated is never indexed twice.
SOURCES = ("mods/*/tools/*.py", "mods/*/in_game/gui/*.gui")

GENERATED = "Do not edit by hand"

DEF = re.compile(r"^def\s+(\w+)")
# `{MOD_ID}_edit_drop = {{` and friends, at the start of a line inside an
# f-string. The trailing brace is doubled because the generator is writing one.
EMIT = re.compile(r"^\{MOD_ID\}_(\w+)\s*=\s*\{\{")
# A window is indexed by the `name` it registers itself under, because that is
# what `scripted_widgets/` and every error names. A `type` by its own name.
GUI_TYPE = re.compile(r"^\s*type\s+(\w+)\s*=")
GUI_WINDOW = re.compile(r'^\s*name\s*=\s*"([^"]+)"')


def estimate(text: str) -> int:
    """Tokens, near enough to choose between two blocks. Same rule as kb.py."""
    cyrillic = sum(1 for c in text if "Ѐ" <= c <= "ӿ")
    return int(cyrillic / 2.2 + (len(text) - cyrillic) / 3.9)


class Block:
    def __init__(self, path: Path, line: int, kind: str, name: str, note: str):
        self.path, self.line, self.kind, self.name, self.note = path, line, kind, name, note
        self.end = line

    @property
    def where(self) -> str:
        return f"{self.path.relative_to(ROOT).as_posix()}:{self.line}"

    def body(self) -> str:
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return "\n".join(lines[self.line - 1:self.end])

    def cost(self) -> int:
        return estimate(self.body())


def generators() -> list[Path]:
    seen: list[Path] = []
    for pattern in SOURCES:
        for path in sorted(ROOT.glob(pattern)):
            if GENERATED in path.read_text(encoding="utf-8-sig")[:400]:
                continue
            seen.append(path)
    return seen


def _slug(note: str) -> str:
    """A short handle for a comment block, from its own opening words.

    Search scores the name first and the note second, so the handle only has to
    be recognisable in a list; the sentence beside it is what actually matches.
    """
    words = re.findall(r"[\w`]+", note.strip("* "))[:4]
    return "_".join(w.strip("`").lower() for w in words if w) or "note"


def note_above(lines: list[str], i: int) -> str:
    """The first real sentence of the comment block above a definition.

    A generator's comments are its documentation — `# {good} out of this
    location, town side.` is exactly what a searcher needs and the code below it
    is not. Banner lines and `Scope:` markers are skipped: they repeat.
    """
    out = []
    j = i - 1
    while j >= 0 and (lines[j].lstrip().startswith("#") or not lines[j].strip()):
        text = lines[j].lstrip().lstrip("#").strip()
        if not text or set(text) <= set("-=# "):
            j -= 1
            continue
        if text.startswith("Scope:"):
            j -= 1
            continue
        out.append(text)
        j -= 1
        if len(out) > 6:
            break
    return " ".join(reversed(out))[:150]


def docstring_of(lines: list[str], i: int) -> str:
    """A `def`'s first docstring line, which is how these functions announce
    themselves: `\"\"\"The pickers, folded shut the first time…\"\"\"`."""
    for k in range(i + 1, min(i + 4, len(lines))):
        s = lines[k].strip()
        if s.startswith(('"""', "'''")):
            return s.strip('"\'').strip()[:150]
        if s and not s.startswith("#"):
            return ""
    return ""


def index() -> list[Block]:
    blocks: list[Block] = []
    for path in generators():
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        here: list[Block] = []
        for i, line in enumerate(lines):
            if path.suffix == ".gui":
                # **A comment block is the unit worth indexing here**, not the
                # window. A window is one four-thousand-token block: knowing it
                # exists helps nobody. What a session needs is the paragraph
                # that says *why* a widget is shaped the way it is, and those
                # are exactly the notes runs were spent on. The rule that cost
                # 2026-09-05 was one of them, sitting unreachable inside a
                # `window` nobody could afford to read.
                if (line.lstrip().startswith("#")
                        and (i == 0 or not lines[i - 1].lstrip().startswith("#"))):
                    run = []
                    j = i
                    while j < len(lines) and lines[j].lstrip().startswith("#"):
                        text = lines[j].lstrip().lstrip("#").strip()
                        if text and not set(text) <= set("-=# "):
                            run.append(text)
                        j += 1
                    if len(run) >= 2:
                        note = " ".join(run)
                        here.append(Block(path, i + 1, "note",
                                          _slug(note), note))
                    continue
                # A window's own `name` sits a line or two inside its block, so
                # the comment to quote is the one above the `window = {`.
                if m := GUI_WINDOW.match(line):
                    # Walk back to the `window = {` line: the comment worth
                    # quoting stands above it, not above the `name`.
                    start = i
                    while start > 0 and not lines[start].lstrip().startswith("window"):
                        start -= 1
                        if i - start > 4:
                            start = i
                            break
                    here.append(Block(path, i + 1, "window", m.group(1),
                                      note_above(lines, start)))
                elif m := GUI_TYPE.match(line):
                    here.append(Block(path, i + 1, "type", m.group(1),
                                      note_above(lines, i)))
            elif m := DEF.match(line):
                here.append(Block(path, i + 1, "def", m.group(1), docstring_of(lines, i)))
            elif m := EMIT.match(line):
                here.append(Block(path, i + 1, "script", m.group(1), note_above(lines, i)))
        # A block runs until the next one starts; the last runs to the end.
        for a, b in zip(here, here[1:]):
            a.end = b.line - 1
        if here:
            here[-1].end = len(lines)
        blocks.extend(here)
    return blocks


def score(block: Block, terms: list[str]) -> tuple[int, int]:
    """Name first, then the comment. A session searching `edit_drop` wants the
    thing called that, not the twenty blocks that mention it."""
    name = block.name.lower()
    note = block.note.lower()
    exact = sum(2 for t in terms if t == name) + sum(1 for t in terms if t in name)
    return exact, sum(1 for t in terms if t in note)


def render(block: Block) -> str:
    kind = {"def": "  ", "script": "· ", "window": "▣ ", "type": "▢ ",
            "note": "¶ "}.get(block.kind, "· ")
    # **Scored whole, shown short.** The note is what a search actually matches
    # -- a rule is remembered by its middle, not its opening words -- so it is
    # kept entire on the block and cut only here. Truncating it at index time
    # hid the `§` rule from the very search written to find it.
    head = block.note if len(block.note) <= 150 else block.note[:147] + "…"
    return f"{block.where:<46} ~{block.cost()}t  {kind}{block.name}" + (
        f"  — {head}" if head else "")


def search(terms: list[str], limit: int) -> int:
    terms = [t.lower() for t in terms]
    hits = [b for b in index() if any(score(b, terms))]
    hits.sort(key=lambda b: (-score(b, terms)[0], -score(b, terms)[1], b.cost()))
    if not hits:
        print("nothing. `--map` lists every block; grep the mod's in_game/ for "
              "generated output, which is not indexed here.")
        return 1
    for b in hits[:limit]:
        print(render(b))
    if len(hits) > limit:
        print(f"\n… and {len(hits) - limit} more; --limit to widen")
    print(f"\nread one: python3 tools/code.py --show {hits[0].where}")
    return 0


def show(where: str) -> int:
    try:
        name, line = where.rsplit(":", 1)
        want = int(line)
    except ValueError:
        print(f"expected FILE:LINE, got {where!r}", file=sys.stderr)
        return 2
    for b in index():
        if b.path.relative_to(ROOT).as_posix() == name and b.line == want:
            print(f"# {b.where} — {b.name}" + (f"\n# {b.note}" if b.note else ""))
            print(b.body())
            return 0
    print(f"no block starts at {where}. `--map` says where they start.", file=sys.stderr)
    return 1


def show_map() -> int:
    """Every block, named and priced — **and the notes cut short here.**

    `--map` is the last resort and has to stay affordable. Indexing the
    hand-written windows added a hundred comment blocks whose whole text is
    searchable, and printing all of it took the map from a page to seventeen
    thousand tokens. The map's job is to say what exists and what it costs; the
    sentence that explains a block is what `code.py <words>` prints.
    """
    current = None
    for b in index():
        path = b.path.relative_to(ROOT).as_posix()
        if path != current:
            current = path
            print(f"\n{path}")
        head = b.note if len(b.note) <= 60 else b.note[:57] + "…"
        kind = {"def": "  ", "script": "· ", "window": "▣ ", "type": "▢ ",
                "note": "¶ "}.get(b.kind, "· ")
        print(f"  {b.where:<46} ~{b.cost()}t  {kind}{b.name}"
              + (f"  — {head}" if head else ""))
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("terms", nargs="*", help="words to look for")
    p.add_argument("--show", metavar="FILE:LINE", help="print one block")
    p.add_argument("--map", action="store_true", help="every generator, every block")
    p.add_argument("--limit", type=int, default=10, help="how many hits (default 10)")
    a = p.parse_args(argv)
    if a.show:
        return show(a.show)
    if a.map:
        return show_map()
    if not a.terms:
        p.print_help()
        return 2
    return search(a.terms, a.limit)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

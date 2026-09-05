#!/usr/bin/env python3
"""Ask the game what exists: effects, triggers, event targets, on_actions, GUI functions.

The game prints its own API. `-debug_mode`, then `script_docs` and
`dump_data_types` in the console, and the dumps land in
`Documents/Paradox Interactive/Europa Universalis V/`; they live here under
`reference/game/docs/`.

This replaces the rule that shaped most of this repository — "if vanilla or one
of the reference mods does not use it, treat it as unproven". That rule cost
real work: subsidies were written off as GUI-only because nothing in `common/`
touched them, and `set_subsidized` was in the game the whole time. Ask here
first; the tree is only evidence of what somebody happened to use.

    python3 tools/api.py set_subsidized          exact name, in every dump
    python3 tools/api.py --find subsid           substring, anywhere
    python3 tools/api.py --scope building        everything that takes a scope
    python3 tools/api.py --gui IsAvailable       GUI data functions only
    python3 tools/api.py --says "Пересчитать"    which key holds this text, and where
    python3 tools/api.py --where checkbutton     every file that mentions the name

**And every answer ends with what was not searched.** That footer is the point
of this tool as much as the search is. Two claims made from memory on
2026-09-05 cost the owner two round trips: that a button was called
«Пересчитать» (it is, but in another window — `--says` answers that in one
call), and that the game has no checkmark character (the character is missing
from the font; the game draws checkmarks as textures — `--where` would have
found them). **A search that finds nothing is evidence about the tree, never
about the game**, and the tree is demonstrably partial: `button_regular` works
and is used 114 times with no declaration anywhere in `reference/`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import refs  # noqa: E402

DOCS = refs.GAME / "docs"
DATA_TYPES = DOCS / "data_types"

# Each dump writes its entries differently. The pattern captures one entry's
# name, and entries run to the next name or a blank-line separator.
DUMPS = (
    ("effect", DOCS / "effects.log", re.compile(r"^## (\S+)\s*$", re.M)),
    ("trigger", DOCS / "triggers.log", re.compile(r"^## (\S+)\s*$", re.M)),
    ("event target", DOCS / "event_targets.log", re.compile(r"^### (\S+)\s*$", re.M)),
    ("on_action", DOCS / "on_actions.log", re.compile(r"^(\w+):\s*$", re.M)),
    ("modifier", DOCS / "modifiers.log", re.compile(r"^Tag: (\w+),", re.M)),
    ("custom localization", DOCS / "custom_localization.log", re.compile(r"^## (\S+)\s*$", re.M)),
)


def entries(path: Path, pattern: re.Pattern) -> list[tuple[str, str]]:
    """Every (name, body) in one dump, body running to the next entry."""
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    found = []
    matches = list(pattern.finditer(text))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        found.append((match.group(1), text[match.start():end].strip()))
    return found


def gui_entries() -> list[tuple[str, str]]:
    """The data type dumps, which are blocks separated by a rule of dashes."""
    found = []
    for path in sorted(DATA_TYPES.glob("*.txt")):
        for block in path.read_text(encoding="utf-8", errors="replace").split("-----------------------"):
            block = block.strip()
            if block:
                found.append((block.splitlines()[0].strip(), block))
    return found


def says(needle: str) -> int:
    """Which localization key holds this text, and which file draws that key.

    **The question «what is this button actually called» has one honest answer
    and it is not memory.** Localization values are what the player reads;
    keys are what the interface names. This walks the values, then looks for
    the key in the mods' own `.gui` and script, so an answer is «this text is
    `bag_wtp_plan_refresh`, drawn by `bag_wtp_plan_window.gui`» rather than a
    recollection.
    """
    roots = [refs.REPO / "mods", refs.GAME, refs.REPO / "reference" / "mods"]
    want = needle.lower()
    found = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.yml")):
            for number, line in enumerate(
                    path.read_text(encoding="utf-8-sig", errors="replace").split("\n"),
                    start=1):
                if ":" not in line or want not in line.lower():
                    continue
                key, _, value = line.partition(":")
                text = value.strip().strip('"').strip()
                if want not in text.lower():
                    continue
                # **A button's own name ranks first.** The question this answers
                # is «what is this control called», and a value that *is* the
                # text beats a paragraph that merely mentions it -- which is the
                # difference between finding `bag_wtp_plan_refresh` and finding
                # four tooltips that use the word in a sentence.
                rank = (0 if text.lower() == want else
                        1 if text.lower().startswith(want) else
                        2 if len(text) < 60 else 3)
                found.append((rank, len(text), key.strip(), _rel(path), number, text))
    if not found:
        print("no localization value contains %r." % needle)
        return 1
    for rank, _, key, path, number, text in sorted(found)[:25]:
        print("--- %s\n    %s:%d\n    %s" % (key, path, number, text[:200]))
        for drawn in _drawn_by(key):
            print("    drawn by %s" % drawn)
        print()
    if len(found) > 25:
        print("… and %d more values mention it" % (len(found) - 25))
    return 0


def _rel(path: Path) -> str:
    try:
        return path.relative_to(refs.REPO).as_posix()
    except ValueError:
        return path.as_posix()


def _drawn_by(key: str) -> list[str]:
    """The mod files that name this key, so the answer says where it appears."""
    out = []
    for root in (refs.REPO / "mods",):
        for path in sorted(root.rglob("*")):
            if path.suffix not in (".gui", ".txt") or not path.is_file():
                continue
            if key in path.read_text(encoding="utf-8-sig", errors="replace"):
                out.append(_rel(path))
    return out[:4]


def where(needle: str) -> int:
    """Every file under `reference/` and `mods/` that mentions the name.

    For the questions the dumps cannot answer: does this widget type exist, is
    there a texture for this, does any mod declare this texticon. The dumps
    hold effects and functions; a `.gui` type or a `.dds` path is only ever
    found by looking.
    """
    counts: dict[str, int] = {}
    for root in (refs.REPO / "reference", refs.REPO / "mods"):
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in (
                    ".gui", ".txt", ".yml", ".log", ".info", ".json"):
                continue
            try:
                text = path.read_text(encoding="utf-8-sig", errors="replace")
            except OSError:
                continue
            n = text.lower().count(needle.lower())
            if n:
                counts[_rel(path)] = n
    if not counts:
        print("no file under reference/ or mods/ mentions %r." % needle)
        return 1
    for path, n in sorted(counts.items(), key=lambda kv: -kv[1])[:25]:
        print("%5d  %s" % (n, path))
    if len(counts) > 25:
        print("… and %d more files" % (len(counts) - 25))
    return 0


# **The footer is not politeness, it is the point.** Both claims that cost a
# round trip on 2026-09-05 were «I looked and it is not there» after looking in
# one place. Printed under every answer, including the empty ones.
FOOTER = """
searched: %s
not searched: the game's gfx (no .dds in this tree), its fonts, and whatever the
extraction left out. `reference/` is demonstrably partial — `button_regular`
works and is used 114 times while being declared nowhere in it.
**An empty result is a fact about this tree. It is not a fact about the game.**"""


def show(kind: str, name: str, body: str) -> None:
    print(f"--- {kind}: {name}")
    print(body)
    print()


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    needle = args[0].lower()

    if "--says" in argv:
        code = says(args[0])
        print(FOOTER % "every .yml under mods/, the game, and reference/mods")
        return code
    if "--where" in argv:
        code = where(args[0])
        print(FOOTER % "every .gui/.txt/.yml/.log under reference/ and mods/")
        return code

    if not DOCS.is_dir():
        raise SystemExit(
            "no dumps under %s — run `script_docs` and `dump_data_types` in the\n"
            "game console with -debug_mode, then copy them here" % DOCS)

    sources: list[tuple[str, list[tuple[str, str]]]]
    if "--gui" in argv:
        sources = [("gui", gui_entries())]
    else:
        sources = [(kind, entries(path, pattern)) for kind, path, pattern in DUMPS]
        sources.append(("gui", gui_entries()))

    hits = 0
    for kind, found in sources:
        for name, body in found:
            if "--find" in argv:
                match = needle in name.lower() or needle in body.lower()
            elif "--scope" in argv:
                match = re.search(r"Scopes.*\b%s\b" % re.escape(needle), body, re.I) is not None
            else:
                match = name.lower() == needle
            if match:
                show(kind, name, body if len(body) < 1200 else body[:1200] + " ...")
                hits += 1
                if hits >= 40:
                    print("(stopped at 40)")
                    return 0

    if not hits:
        print("nothing named %r in the dumps. Try --find for a substring, "
              "--where to look in the files." % args[0])
        print(FOOTER % "the game's own API dumps under reference/game/docs")
        return 1
    print(FOOTER % "the game's own API dumps under reference/game/docs")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except BrokenPipeError:
        import os
        os._exit(0)

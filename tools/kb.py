#!/usr/bin/env python3
"""Ask the documents a question instead of reading them.

This repository's knowledge is worth about ninety thousand tokens. A session
that reads two of them end to end because another one told it to has
spent a third of an hour's budget before writing a line, and pays for them
again on every turn after, because the context is resent each time.

So the documents are not read. They are asked:

    python3 tools/kb.py widget leak        which sections talk about this
    python3 tools/kb.py --show docs/PITFALLS.md:112     print one section
    python3 tools/kb.py --map              every document, every section
    python3 tools/kb.py --mod nd_ru        one mod's brief and open questions

A search prints one line per matching section — where it is, what it is called,
how big it is — and nothing else. Reading is then a deliberate act on one
section, priced in advance. `~1200t` in a listing is the cost of asking for it.

The size estimate counts Cyrillic at 2.2 characters per token and everything
else at 3.9, which is close enough to choose between two sections and not a
promise about anybody's billing.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import refs  # noqa: E402

# What counts as the knowledge base. Everything else in the tree is code, game
# files, or a mod's own contents — greppable, but not something to rank.
SOURCES = (
    "CLAUDE.md",
    "docs/*.md",
    "docs/pitfalls/*.md",
    "docs/research/*.md",
    "docs/investigations/*.md",
    "docs/archive/*.md",
    "mods/*/CLAUDE.md",
    "mods/*/README.md",
    "mods/*/GLOSSARY.md",
    "reference/README.md",
)

HEADING = re.compile(r"^(#{1,4})\s+(.*)$")
WORD = re.compile(r"[\w-]+", re.UNICODE)


def estimate(text: str) -> int:
    """Roughly what this costs to put in a context window."""
    cyrillic = len(re.findall(r"[А-Яа-яЁё]", text))
    return int(cyrillic / 2.2 + (len(text) - cyrillic) / 3.9)


class Section:
    def __init__(self, path: Path, line: int, level: int, title: str):
        self.path = path
        self.line = line
        self.level = level
        self.title = title
        self.lines: list[str] = []

    @property
    def where(self) -> str:
        return "%s:%d" % (self.path.relative_to(refs.REPO).as_posix(), self.line)

    @property
    def body(self) -> str:
        return "\n".join(self.lines)

    @property
    def cost(self) -> int:
        return estimate(self.title + "\n" + self.body)


def documents() -> list[Path]:
    found: list[Path] = []
    for pattern in SOURCES:
        found.extend(sorted(refs.REPO.glob(pattern)))
    return found


def split(path: Path) -> list[Section]:
    """Every heading in a document is a section, ending at the next heading of
    the same level or shallower. A `##` therefore holds its `###` children, and
    both are offered separately — a query about the whole subject wants the
    parent, one about a detail wants the child."""
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    open_sections: list[Section] = []
    done: list[Section] = []

    preamble = Section(path, 1, 0, "(intro)")
    open_sections.append(preamble)

    for number, line in enumerate(lines, 1):
        match = HEADING.match(line)
        if match:
            level = len(match.group(1))
            while open_sections and open_sections[-1].level >= level:
                done.append(open_sections.pop())
            section = Section(path, number, level, match.group(2).strip())
            for parent in open_sections:
                parent.lines.append(line)
            open_sections.append(section)
            continue
        for section in open_sections:
            section.lines.append(line)

    done.extend(open_sections)
    return [s for s in done if s.body.strip() or s.level]


def index() -> list[Section]:
    sections: list[Section] = []
    for path in documents():
        sections.extend(split(path))
    return sections


def score(section: Section, terms: list[str]) -> tuple[int, int, float]:
    """How many of the asked-for words this section has, where, and how densely.

    Distinct words first: a section holding every word beats one holding the
    commonest word twenty times. Then the heading, because a heading says what
    the section is *about* rather than what it mentions in passing. Then
    density — hits per thousand tokens — which is what stops a long chapter
    that mentions the word once from outranking the paragraph that is the
    answer. Ranking by raw counts put the largest document first every time.
    """
    title = section.title.lower()
    body = section.body.lower()
    distinct = 0
    in_title = 0
    total = 0
    for term in terms:
        title_hits = title.count(term)
        body_hits = body.count(term)
        if title_hits or body_hits:
            distinct += 1
        in_title += title_hits
        total += title_hits + body_hits
    return distinct, in_title, total * 1000 / max(section.cost, 1)


def searchable(sections: list[Section]) -> list[Section]:
    """A document's own title holds every word in it, so it wins every search
    and answers none. Offer the parts, unless the document has no parts."""
    by_document: dict[Path, list[Section]] = {}
    for section in sections:
        by_document.setdefault(section.path, []).append(section)
    keep: list[Section] = []
    for parts in by_document.values():
        inner = [s for s in parts if s.level >= 2]
        keep.extend(inner or parts)
    return keep


def search(terms: list[str], limit: int, everything: bool) -> int:
    hits = []
    for section in searchable(index()):
        distinct, in_title, density = score(section, terms)
        if distinct == 0:
            continue
        if not everything and distinct < len(terms) and len(terms) > 1:
            continue
        hits.append((distinct, in_title, density, section))
    if not hits and not everything and len(terms) > 1:
        print("nothing holds all of %s — trying any of them" % ", ".join(terms))
        return search(terms, limit, everything=True)
    if not hits:
        print("nothing in the documents matches %s" % " ".join(terms))
        print("the game's own files are a different question: python3 tools/api.py --find %s"
              % terms[0])
        return 1

    hits.sort(key=lambda hit: (-hit[0], -hit[1], -hit[2], hit[3].cost))
    shown = hits[:limit]
    width = max(len(hit[-1].where) for hit in shown)
    for _, _, _, section in shown:
        print("%-*s  %5s  %s%s" % (
            width, section.where, "~%dt" % section.cost,
            "  " * max(section.level - 1, 0), section.title))
    if len(hits) > limit:
        print("... and %d more (--limit %d)" % (len(hits) - limit, len(hits)))
    print()
    print("read one: python3 tools/kb.py --show %s" % shown[0][-1].where)
    return 0


def show(where: str) -> int:
    if ":" not in where:
        print("--show wants file:line, as a search result prints it", file=sys.stderr)
        return 1
    name, _, number = where.rpartition(":")
    path = refs.REPO / name
    if not path.exists():
        print("no such document: %s" % name, file=sys.stderr)
        return 1
    wanted = int(number)
    for section in split(path):
        if section.line == wanted:
            print("%s — %s" % (section.where, section.title))
            print()
            print(section.body.strip())
            return 0
    print("%s has no section starting at line %s. Its sections:" % (name, number),
          file=sys.stderr)
    for section in split(path):
        print("  %s  %s" % (section.where, section.title), file=sys.stderr)
    return 1


def show_map(path_filter: str | None) -> int:
    total = 0
    for path in documents():
        where = path.relative_to(refs.REPO).as_posix()
        if path_filter and path_filter not in where:
            continue
        sections = split(path)
        whole = max((s.cost for s in sections if s.level == 0), default=0)
        top = [s for s in sections if s.level in (1, 2)]
        total += estimate(path.read_text(encoding="utf-8-sig"))
        print("%s  ~%dt" % (where, whole or estimate(path.read_text(encoding='utf-8-sig'))))
        for section in top:
            if section.level == 1:
                continue
            print("    %-6s ~%-6s %s" % (str(section.line), "%dt" % section.cost,
                                         section.title))
    print()
    print("the whole base is ~%dt; a session should spend a small fraction of it" % total)
    return 0


def brief(mod: str) -> int:
    """Everything about one mod, in the order a session needs it."""
    folder = refs.REPO / "mods" / mod
    if not folder.is_dir():
        available = sorted(p.name for p in (refs.REPO / "mods").iterdir() if p.is_dir())
        print("no mod called %s. There are: %s" % (mod, ", ".join(available)),
              file=sys.stderr)
        return 1
    for name in ("CLAUDE.md", "README.md"):
        path = folder / name
        if path.exists():
            print("=== mods/%s/%s ===" % (mod, name))
            print(path.read_text(encoding="utf-8-sig").strip())
            print()
            break
    else:
        print("mods/%s has no CLAUDE.md and no README.md" % mod)
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Ask this repository's documents instead of reading them.")
    parser.add_argument("terms", nargs="*", help="words to look for")
    parser.add_argument("--show", metavar="FILE:LINE",
                        help="print one section, as a search result names it")
    parser.add_argument("--map", action="store_true",
                        help="every document and section, with what each costs")
    parser.add_argument("--mod", metavar="NAME", help="one mod's brief")
    parser.add_argument("--limit", type=int, default=8, help="how many hits (default 8)")
    parser.add_argument("--any", dest="any_term", action="store_true",
                        help="sections holding any word, not all of them")
    args = parser.parse_args(argv[1:])

    if args.show:
        return show(args.show)
    if args.mod:
        return brief(args.mod)
    if args.map:
        return show_map(args.terms[0] if args.terms else None)
    if not args.terms:
        parser.print_help()
        return 0
    return search([t.lower() for t in args.terms], args.limit, args.any_term)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

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
        print("nothing named %r. Try --find for a substring." % args[0])
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except BrokenPipeError:
        import os
        os._exit(0)

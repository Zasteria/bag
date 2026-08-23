#!/usr/bin/env python3
"""Ask how the game itself says something in Russian.

The mod's text is English and names the game's own concepts in plain prose, so
translating it needs the word the player already sees on screen.  This matches
an English value against the game's English localization and prints the Russian
value of the same key.

    python3 mods/nd_ru/tools/term.py levies
    python3 mods/nd_ru/tools/term.py --key ADVANCES
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LOC = REPO / "reference/game/main_menu/localization"
KEY_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*(?:\d+\s+)?"(.*)"\s*$')


def load(lang: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for path in (LOC / lang).rglob("*.yml"):
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            match = KEY_LINE.match(line)
            if match:
                values.setdefault(match.group(1), match.group(2))
    return values


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        raise SystemExit(__doc__)
    english, russian = load("english"), load("russian")
    by_key = argv[1] == "--key"
    needle = " ".join(argv[2:] if by_key else argv[1:])

    if by_key:
        hits = [k for k in english if k.lower() == needle.lower()]
    else:
        low = needle.lower()
        exact = [k for k, v in english.items() if v.lower() == low]
        hits = exact or [k for k, v in english.items() if low in v.lower()][:20]

    if not hits:
        print(f"нет совпадений для {needle!r}")
        return 1
    for key in hits[:20]:
        print(f"{key}\n    en: {english[key]}\n    ru: {russian.get(key, '— нет ключа —')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

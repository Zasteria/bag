#!/usr/bin/env python3
"""List the keys of a names-first pass, and how much of it is already done.

The player asked for names before descriptions: what a country is called, what
its advances and modifiers are called, what an event is titled.  This picks
exactly those keys out of the base mod and reports them per file, so the work
can be taken a file at a time and resumed in a later session.

    python3 mods/nd_ru/tools/scope.py            # progress per file
    python3 mods/nd_ru/tools/scope.py <stem>     # the untranslated keys of one file
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
REPO = MOD.parent.parent
BASE = REPO / "reference/mods/National Destinies - Formables Content/main_menu/localization/english"
KEY_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*(?:\d+\s+)?"(.*)"\s*$')
MARKUP = re.compile(r"\[[^\]]*\]|\$[^$]*\$|@\w+!|#[A-Za-z_]+|#!|\\n")

# A description, a tooltip, or the body of an event: prose, not a name.
PROSE = re.compile(r"(_desc|_tooltip|_effect|_text)$|\.\d+\.(?!t$)\w+$")


def is_name(key: str, value: str) -> bool:
    if PROSE.search(key):
        return False
    if key.startswith(("STATIC_MODIFIER_DESC_", "AUTO_MODIFIER_DESC_")):
        return False
    return bool(re.search(r"[A-Za-z]{2}", MARKUP.sub("", value)))


def read(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = KEY_LINE.match(line)
        if match:
            out[match.group(1)] = match.group(2)
    return out


def main(argv: list[str]) -> int:
    stems = {p.name[: -len("_l_english.yml")]: p for p in sorted(BASE.glob("*_l_english.yml"))}

    if len(argv) > 1:
        stem = argv[1]
        if stem not in stems:
            raise SystemExit(f"no such file: {stem}")
        english = read(stems[stem])
        source = MOD / "translations" / f"{stem}.yml"
        done = read(source) if source.exists() else {}
        for key, value in english.items():
            if is_name(key, value) and key not in done:
                print(f'{key}\t{value}')
        return 0

    total = left = 0
    rows = []
    for stem, path in stems.items():
        english = read(path)
        names = {k: v for k, v in english.items() if is_name(k, v)}
        source = MOD / "translations" / f"{stem}.yml"
        done = set(read(source)) if source.exists() else set()
        missing = [k for k in names if k not in done]
        total += len(names)
        left += len(missing)
        if missing:
            rows.append((len(missing), stem))
    rows.sort(reverse=True)
    for count, stem in rows[:25]:
        print(f"{count:>5}  {stem}")
    if len(rows) > 25:
        print(f"... ещё {len(rows) - 25} файлов")
    print(f"\nназваний всего: {total}, осталось: {left}, готово: {total - left}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

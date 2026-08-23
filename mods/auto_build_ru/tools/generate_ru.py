#!/usr/bin/env python3
"""Build the Russian localization file for EU5 Advanced Auto Build.

The base mod ships English and Simplified Chinese only, so every one of its keys
renders as the raw key for a player running the game in Russian.  This tool
takes the hand written translations in ``translations/ru.yml`` and emits
``main_menu/localization/russian/eu5ab_ru_generated_l_russian.yml`` against the
key list the base mod actually defines.

Usage:

    python3 mods/auto_build_ru/tools/generate_ru.py [<path to the base mod>]

It refuses to write a file that would show up wrong in game:

* every key the base mod defines has to be translated, and nothing else may be;
* the markup of a value -- ``[data functions]``, ``$key$`` references,
  ``@texticons!``, ``#format`` codes -- has to survive translation unchanged,
  because those are what the engine reads rather than displays;
* a stray double quote would truncate the line, and a square bracket added to
  plain text renders as ``ERROR:``, so both are checked.

Families of keys that differ only by a number -- the twenty template slots, the
step buttons -- are written once in ``ru.yml`` with ``{N}`` standing for the
number, and expanded here over exactly the numbers the base mod uses.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
REPO = MOD.parent.parent
DEFAULT_BASE = REPO / "reference" / "mods" / "Auto build by Lincoln Guang"
ENGLISH = "main_menu/localization/english/eu5ab_l_english.yml"
OUT = MOD / "main_menu/localization/russian/eu5ab_ru_generated_l_russian.yml"
SOURCE = MOD / "translations/ru.yml"

KEY_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-{}]+):\s*(?:\d+\s+)?"(.*)"\s*$')
FAMILY = re.compile(r"(?<=_)\d+(?=_|$)")
# What the engine reads instead of displaying, and so must come through a
# translation byte for byte.
MARKUP = re.compile(r"\[[^\]]*\]|\$[^$]*\$|@\w+!|#[A-Za-z_]+|#!|\\n")


def read_yml(path: Path) -> dict[str, str]:
    """Parse a Clausewitz localization file into an ordered key -> value dict."""
    values: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or re.match(r"^l_\w+:$", stripped):
            continue
        match = KEY_LINE.match(line)
        if not match:
            raise SystemExit(f"{path}:{number}: cannot parse: {line!r}")
        key, value = match.group(1), match.group(2)
        if key in values:
            raise SystemExit(f"{path}:{number}: duplicate key {key}")
        values[key] = value
    return values


def expand(source: dict[str, str], english: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """Resolve ``{N}`` families against the numbers the base mod really uses."""
    by_family: dict[str, list[str]] = {}
    for key in english:
        by_family.setdefault(FAMILY.sub("{N}", key), []).append(key)

    out = {key: value for key, value in source.items() if "{N}" not in key}
    problems: list[str] = []
    for key, value in source.items():
        if "{N}" not in key:
            continue
        members = by_family.get(key)
        if not members:
            problems.append(f"family {key} matches nothing in the base mod")
            continue
        filled = 0
        for member in members:
            numbers = FAMILY.findall(member)
            if len(set(numbers)) != 1:
                problems.append(f"{member}: a family key needs exactly one number")
                continue
            # An entry written out in full wins, so a family can cover the
            # regular members and leave an odd one out to be translated alone.
            if member in out:
                continue
            out[member] = value.replace("{N}", numbers[0])
            filled += 1
        if not filled:
            problems.append(f"family {key} adds nothing every member is already written out")
    return out, problems


def check(english: dict[str, str], russian: dict[str, str]) -> list[str]:
    problems: list[str] = []

    missing = [k for k in english if k not in russian]
    if missing:
        problems.append(f"{len(missing)} key(s) not translated, first: {missing[:8]}")
    extra = [k for k in russian if k not in english]
    if extra:
        problems.append(f"{len(extra)} key(s) the base mod does not define: {extra[:8]}")

    for key, value in russian.items():
        if key not in english:
            continue
        if '"' in value:
            problems.append(f"{key}: a double quote would truncate the line")
        if MARKUP.sub("", value).count("[") or MARKUP.sub("", value).count("]"):
            problems.append(f"{key}: a bare square bracket renders as ERROR:")
        want, got = Counter(MARKUP.findall(english[key])), Counter(MARKUP.findall(value))
        if want != got:
            lost = sorted((want - got).elements())
            gained = sorted((got - want).elements())
            problems.append(f"{key}: markup changed (lost {lost}, added {gained})")
    return problems


def main() -> int:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BASE
    english_path = base / ENGLISH
    if not english_path.is_file():
        raise SystemExit(f"no English localization at {english_path}")

    english = read_yml(english_path)
    russian, problems = expand(read_yml(SOURCE), english)
    problems += check(english, russian)
    if problems:
        print(f"{len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    lines = ["l_russian:"]
    lines += [f' {key}: "{russian[key]}"' for key in english]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("﻿" + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(REPO)}: {len(english)} keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

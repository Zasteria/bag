#!/usr/bin/env python3
"""Build the Russian localization files for EU5 National Destinies.

The base mod ships eleven languages whose files are byte identical to the
English ones -- only the ``l_<language>:`` header differs -- so a Russian game
renders every one of the mod's 40719 keys in English.  This tool takes the hand
written translations in ``translations/`` and emits one Russian file per base
file, checked against the keys the base mod actually defines.

Usage:

    python3 mods/nd_ru/tools/generate_ru.py [<path to the base mod>]

One source file per base file: ``translations/<stem>.yml`` is emitted as
``main_menu/localization/russian/<stem>_ru_generated_l_russian.yml`` from the
base mod's ``<stem>_l_english.yml``.  A base file with no source file yet is
simply not emitted, so the translation can be finished a batch at a time and
the coverage report says how far along it is.

It refuses to write a file that would show up wrong in game:

* a key the base mod does not define is invented and cannot render;
* a base key the source file misses stays with the base mod, and so stays
  English -- that is how a names-first pass is meant to work, so it is counted
  and reported rather than refused;
* the markup of a value -- ``[data functions]`` and ``[concept|e]`` links,
  ``$key$`` references, ``@texticons!``, ``#format`` codes, ``\\n`` -- is read by
  the engine rather than displayed and has to survive translation unchanged;
* a stray double quote truncates the line, and a square bracket added to plain
  text renders as ``ERROR:``;
* a character belonging to neither Russian nor the Latin the mod's proper names
  need has no business in the file -- a stray CJK ideograph slipped into three
  values on the first large batch and would have reached the player unnoticed.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
REPO = MOD.parent.parent
DEFAULT_BASE = REPO / "reference" / "mods" / "National Destinies - Formables Content"
ENGLISH_DIR = "main_menu/localization/english"
OUT_DIR = MOD / "main_menu/localization/russian"
SOURCE_DIR = MOD / "translations"

KEY_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*(?:\d+\s+)?"(.*)"\s*$')
# What the engine reads instead of displaying, and so must come through a
# translation byte for byte.
MARKUP = re.compile(r"\[[^\]]*\]|\$[^$]*\$|@\w+!|#[A-Za-z_]+|#!|\\n")


def read_yml(path: Path) -> dict[str, str]:
    """Parse a Clausewitz localization file into a key -> value dict."""
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


def prose(value: str) -> str:
    """The part of a value a player actually reads."""
    return MARKUP.sub("", value).strip()


def check(stem: str, english: dict[str, str], russian: dict[str, str]) -> list[str]:
    """Everything wrong with one file's translation, as printable lines."""
    problems: list[str] = []

    invented = [k for k in russian if k not in english]
    for key in invented:
        problems.append(f"  {key}: not a key of the base mod")

    for key, value in russian.items():
        if key not in english:
            continue
        want = Counter(MARKUP.findall(english[key]))
        got = Counter(MARKUP.findall(value))
        if want != got:
            for token in sorted((want - got).keys()):
                problems.append(f"  {key}: markup {token!r} lost in translation")
            for token in sorted((got - want).keys()):
                problems.append(f"  {key}: markup {token!r} invented")
        if '"' in value:
            problems.append(f"  {key}: a double quote would truncate the line")
        stray = prose(value)
        if "[" in stray or "]" in stray:
            problems.append(f"  {key}: a square bracket in plain text renders as ERROR:")
        if not value.strip():
            problems.append(f"  {key}: empty value")
        for char in set(value):
            point = ord(char)
            if not (0x0400 <= point <= 0x04FF          # Cyrillic
                    or 0x20 <= point <= 0x7E           # ASCII: names, markup
                    or 0x00C0 <= point <= 0x024F       # accented Latin
                    or char in "\u00ab\u00bb\u2014\u2013\u2026\u2018\u2019\u02bf\u02bd\u0301"):
                problems.append(
                    f"  {key}: stray character {char!r} (U+{point:04X})")

    return problems


def write_yml(path: Path, values: dict[str, str]) -> None:
    """Write a localization file the way the game wants it: BOM, one space."""
    body = ["l_russian:"]
    body += [f' {key}: "{value}"' for key, value in values.items()]
    path.write_text("\n".join(body) + "\n", encoding="utf-8-sig")


def main(argv: list[str]) -> int:
    base = Path(argv[1]) if len(argv) > 1 else DEFAULT_BASE
    english_dir = base / ENGLISH_DIR
    if not english_dir.is_dir():
        raise SystemExit(f"no English localization under {english_dir}")

    base_files = {p.name[: -len("_l_english.yml")]: p
                  for p in sorted(english_dir.glob("*_l_english.yml"))}
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sources = {p.stem: p for p in sorted(SOURCE_DIR.glob("*.yml"))}
    unknown = sorted(set(sources) - set(base_files))
    if unknown:
        raise SystemExit("no such file in the base mod: " + ", ".join(unknown))

    failed = False
    written: list[str] = []
    done_keys = done_words = 0
    for stem, source in sources.items():
        english = read_yml(base_files[stem])
        russian = read_yml(source)
        problems = check(stem, english, russian)
        if problems:
            failed = True
            print(f"{source}:", file=sys.stderr)
            for line in problems:
                print(line, file=sys.stderr)
            continue
        ordered = {key: russian[key] for key in english if key in russian}
        write_yml(OUT_DIR / f"{stem}_ru_generated_l_russian.yml", ordered)
        written.append(stem)
        done_keys += len(ordered)
        done_words += sum(len(prose(english[k]).split()) for k in ordered)

    # Anything emitted by an earlier run whose source file is gone.
    for stale in OUT_DIR.glob("*_ru_generated_l_russian.yml"):
        if stale.name[: -len("_ru_generated_l_russian.yml")] not in sources:
            stale.unlink()
            print(f"removed {stale.name}, no longer translated")

    total_keys = total_words = 0
    for path in base_files.values():
        values = read_yml(path)
        total_keys += len(values)
        total_words += sum(len(prose(v).split()) for v in values.values())

    print(f"файлов:  {len(written):>4} из {len(base_files)}"
          f"   ({100 * len(written) / len(base_files):.1f}%) затронуто")
    print(f"ключей:  {done_keys:>6} из {total_keys}"
          f" ({100 * done_keys / total_keys:.1f}%)")
    print(f"слов:    {done_words:>6} из {total_words}"
          f" ({100 * done_words / total_words:.1f}%)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

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

* every key the base mod defines has to be translated.  A key here the base mod
  *no longer* defines is a different matter: it is a line the mod deleted, the
  generated file never carries it, and nothing about the game is wrong -- so it
  is reported and the run goes on.  ``--prune`` takes those lines out of
  ``ru.yml``.  A rename shows up as both at once, and the missing half stops the
  run, which is the case that actually needs a human;
* a key whose English the base mod has *rewritten* is named, because the
  Russian under it may no longer say the same thing -- that is invisible
  otherwise, and 0.9.3 rewrote two of them under a translation that stayed
  put.  Check it against the base mod, fix the Russian, then record the new
  English with ``--accept``;
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
from hashlib import sha1
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
REPO = MOD.parent.parent
sys.path.insert(0, str(REPO / "tools"))
import refs  # noqa: E402  the reference tree, resolved by mod id

DEFAULT_BASE = refs.known("auto_build")
ENGLISH = "main_menu/localization/english/eu5ab_l_english.yml"
OUT = MOD / "main_menu/localization/russian/eu5ab_ru_generated_l_russian.yml"
SOURCE = MOD / "translations/ru.yml"
# key -> a digest of the English value it was translated from.
FINGERPRINTS = MOD / "english_generated_fingerprints.txt"

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


def expand(source: dict[str, str],
           english: dict[str, str]) -> tuple[dict[str, str], list[str], list[str]]:
    """Resolve ``{N}`` families against the numbers the base mod really uses.

    Returns the expanded translation, the problems that stop a run, and the
    ``{N}`` families the base mod has stopped defining altogether -- which is a
    deletion rather than a problem, and is reported with the other ones.
    """
    by_family: dict[str, list[str]] = {}
    for key in english:
        by_family.setdefault(FAMILY.sub("{N}", key), []).append(key)

    out = {key: value for key, value in source.items() if "{N}" not in key}
    problems: list[str] = []
    gone: list[str] = []
    for key, value in source.items():
        if "{N}" not in key:
            continue
        members = by_family.get(key)
        if not members:
            gone.append(key)
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
    return out, problems, gone


def check(english: dict[str, str],
          russian: dict[str, str]) -> tuple[list[str], list[str]]:
    """The problems that stop a run, and the keys the base mod has dropped."""
    problems: list[str] = []

    missing = [k for k in english if k not in russian]
    if missing:
        problems.append(f"{len(missing)} key(s) not translated, first: {missing[:8]}")
    gone = [k for k in russian if k not in english]

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
    return problems, gone


def prune(gone: list[str]) -> int:
    """Take the dropped keys out of ``translations/ru.yml``. Returns how many."""
    dropped = set(gone)
    kept: list[str] = []
    removed = 0
    for line in SOURCE.read_text(encoding="utf-8-sig").splitlines():
        match = KEY_LINE.match(line)
        if match and match.group(1) in dropped:
            removed += 1
            continue
        kept.append(line)
    SOURCE.write_text("\ufeff" + "\n".join(kept) + "\n", encoding="utf-8")
    return removed


def fingerprint(value: str) -> str:
    """A short digest of one English value, stable across runs."""
    return sha1(value.encode("utf-8")).hexdigest()[:12]


def read_fingerprints() -> dict[str, str]:
    """What English each translated key was last checked against."""
    if not FINGERPRINTS.exists():
        return {}
    recorded: dict[str, str] = {}
    for line in FINGERPRINTS.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            digest, _, key = line.partition("\t")
            recorded[key] = digest
    return recorded


def write_fingerprints(recorded: dict[str, str]) -> None:
    body = ["# Written by generate_ru.py -- do not edit by hand.",
            "# <digest of the English value>\t<key>, for every translated key.",
            "# A run whose digest differs names the key: the base mod rewrote its",
            "# English and the Russian may no longer say the same thing."]
    body += [f"{recorded[key]}\t{key}" for key in sorted(recorded)]
    FINGERPRINTS.write_text("\n".join(body) + "\n", encoding="utf-8")


def main() -> int:
    argv = list(sys.argv)
    accept = "--accept" in argv
    if accept:
        argv.remove("--accept")
    pruning = "--prune" in argv
    if pruning:
        argv.remove("--prune")
    base = Path(argv[1]) if len(argv) > 1 else DEFAULT_BASE
    english_path = base / ENGLISH
    if not english_path.is_file():
        raise SystemExit(f"no English localization at {english_path}")

    english = read_yml(english_path)
    russian, problems, gone = expand(read_yml(SOURCE), english)
    more, dropped = check(english, russian)
    problems += more
    gone += dropped
    if problems:
        print(f"{len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        if gone:
            # Said here as well, because a rename is a missing key *and* a
            # dropped one, and the dropped half is the clue to what it became.
            print(f"  (and {len(gone)} key(s) the base mod no longer defines —"
                  " a rename looks like this)", file=sys.stderr)
        return 1

    if gone and pruning:
        removed = prune(gone)
        print(f"--prune: {removed} строк(и) убрано из "
              f"{SOURCE.relative_to(REPO)}", file=sys.stderr)
        gone = []

    recorded = read_fingerprints()
    current: dict[str, str] = {}
    moved: list[str] = []
    for key in english:
        digest = fingerprint(english[key])
        was = recorded.get(key)
        if was is not None and was != digest and not accept:
            moved.append(key)
            current[key] = was     # keep flagging it until it is dealt with
        else:
            current[key] = digest
    write_fingerprints(current)

    lines = ["l_russian:"]
    lines += [f' {key}: "{russian[key]}"' for key in english]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("﻿" + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(REPO)}: {len(english)} keys")

    if gone:
        # Not a failure: the generated file is written from the base mod's own
        # key list, so a translation of a key it has deleted is never emitted
        # and nothing renders wrong. It is dead weight in ru.yml, and saying so
        # once is cheaper than a run that stops the whole refresh.
        print(f"базовый мод больше не определяет {len(gone)} ключ(ей) —"
              " перевод под ними лежит зря:", file=sys.stderr)
        for key in gone:
            print(f"  {key}", file=sys.stderr)
        print("  убрать их: generate_ru.py --prune", file=sys.stderr)

    if moved:
        print(f"английский оригинал изменился у {len(moved)} ключ(ей)"
              " — перевод мог устареть:", file=sys.stderr)
        for key in moved:
            print(f"  {key}", file=sys.stderr)
        print("  свериться с базовым модом, поправить перевод, затем "
              "generate_ru.py --accept", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

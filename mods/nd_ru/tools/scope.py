#!/usr/bin/env python3
"""List the keys of a names-first pass, and how much of it is already done.

The player asked for names before descriptions: what a country is called, what
its advances and modifiers are called, what an event is titled.  This picks
exactly those keys out of the base mod and reports them per file, so the work
can be taken a file at a time and resumed in a later session.

    python3 mods/nd_ru/tools/scope.py             # progress per file, names only
    python3 mods/nd_ru/tools/scope.py <stem>      # untranslated names of one file
    python3 mods/nd_ru/tools/scope.py --full <stem>   # every untranslated key of it
    python3 mods/nd_ru/tools/scope.py --plan      # what priority.txt still wants

``--full`` is for the files the player asked for whole rather than by name: the
situations and disasters that run for years, and each country's formation event.
``priority.txt`` fixes the order -- Europe before the rest, because that is where
this player plays -- so a later session picks up where this one stopped.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
REPO = MOD.parent.parent
sys.path.insert(0, str(REPO / "tools"))
import refs  # noqa: E402  the reference tree, resolved by mod id

BASE = refs.known("national_destinies") / "main_menu/localization/english"
KEY_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*(?:\d+\s+)?"(.*)"\s*$')
MARKUP = re.compile(r"\[[^\]]*\]|\$[^$]*\$|@\w+!|#[A-Za-z_]+|#!|\\n")

# A description, a tooltip, or the body of an event: prose, not a name.
PROSE = re.compile(r"(_desc|_tooltip|_effect|_text)$|\.\d+\.(?!t$)\w+$")


# The formation event: one per country, and the one the player is asked to
# choose a path in, so it is wanted whole rather than by its title.
FORMATION = re.compile(r"^nd_[a-z]+\.1\.")


def is_wanted(key: str, value: str) -> bool:
    """A country's working set: its names plus its formation event, whole."""
    if not re.search(r"[A-Za-z]{2}", MARKUP.sub("", value)):
        return False
    return is_name(key, value) or bool(FORMATION.match(key))


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


def priority() -> list[str]:
    """The stems priority.txt asks for, in its order."""
    path = MOD / "priority.txt"
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


def main(argv: list[str]) -> int:
    stems = {p.name[: -len("_l_english.yml")]: p for p in sorted(BASE.glob("*_l_english.yml"))}

    if len(argv) > 2 and argv[1] == "--full":
        stem = argv[2]
        if stem not in stems:
            raise SystemExit(f"no such file: {stem}")
        english = read(stems[stem])
        source = MOD / "translations" / f"{stem}.yml"
        done = read(source) if source.exists() else {}
        for key, value in english.items():
            if key not in done and re.search(r"[A-Za-z]{2}", MARKUP.sub("", value)):
                print(f"{key}\t{value}")
        return 0

    if len(argv) > 1 and argv[1] == "--plan":
        for stem in priority():
            if stem not in stems:
                print(f"{stem}: нет такого файла в моде")
                continue
            english = read(stems[stem])
            source = MOD / "translations" / f"{stem}.yml"
            done = set(read(source)) if source.exists() else set()
            wanted = {k for k, v in english.items() if is_wanted(k, v)}
            rest = {k for k, v in english.items()
                    if k not in wanted and re.search(r"[A-Za-z]{2}", MARKUP.sub("", v))}
            mark = "готово" if not wanted - done else ""
            print(f"{stem:14} нужно {len(wanted - done):>4}"
                  f"   остальной прозы {len(rest - done):>4}  {mark}")
        return 0

    if len(argv) > 1:
        stem = argv[1]
        if stem not in stems:
            raise SystemExit(f"no such file: {stem}")
        english = read(stems[stem])
        source = MOD / "translations" / f"{stem}.yml"
        done = read(source) if source.exists() else {}
        for key, value in english.items():
            if is_wanted(key, value) and key not in done:
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
    try:
        sys.exit(main(sys.argv))
    except BrokenPipeError:
        # `| head` closed the pipe. That is how this tool is normally read, so
        # it is not worth a traceback.
        os._exit(0)

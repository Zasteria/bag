#!/usr/bin/env python3
"""Russian for Glorp UI's societal value hints.

Glorp UI ships `glorpui_generated_societal_value_hints_l_english.yml` in
`main_menu/localization/english/` and nowhere else. Paradox games load the
localization folder of the selected language only, with no fallback to English,
so on a Russian client every `GLORP_UI_SVH_*` key is missing, the hint list
renders empty, and the tooltip says "Нет." — while `debug.log` collects one
`Missing loc key` line per key per load.

The hint strings are built from exactly three templates. Everything language
specific in them is the leading verb phrase: the reform, policy and privilege
names themselves come from `$key$` references the game resolves in the active
language. So the Russian file is the English file with those three phrases
replaced — which is why it survives a Glorp UI update that only adds hints.

Run it through `mods/glorpui_hints/tools/generate.py`, or on its own against a
different copy of the files:

    python3 mods/glorpui_hints/tools/translate_hints.py \
        --source <glorp ui>/main_menu/localization/english/glorpui_generated_societal_value_hints_l_english.yml \
        --output <mod>/main_menu/localization/russian/glorpui_generated_societal_value_hints_l_russian.yml
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# (english prefix, russian replacement). The prefix is everything up to the
# #TOOLTIP: token, which is where the language independent part starts.
TEMPLATES = [
    ("@hint! Grant #TOOLTIP:ESTATE_PRIVILEGE,",
     "@hint! Даровать привилегию #TOOLTIP:ESTATE_PRIVILEGE,"),
    ("@hint! Add the #TOOLTIP:GOVERNMENT_REFORM,",
     "@hint! Принять реформу правления #TOOLTIP:GOVERNMENT_REFORM,"),
    ("@hint! Enact the #TOOLTIP:POLICY,",
     "@hint! Ввести политику #TOOLTIP:POLICY,"),
]

# The English text also carries a trailing game concept token that only reads
# correctly in English word order ("Add the <name> government reform:"). Russian
# names the object type in the verb phrase instead, so the token is dropped.
CONCEPT_SUFFIXES = [
    ("#!#! [government_reform|e]:", "#!#!:"),
    ("#!#! [policy]:", "#!#!:"),
]

ENTRY_RE = re.compile(r'^ (GLORP_UI_SVH_\w+): "(.*)"\s*$')

SOURCE_NAME = "glorpui_generated_societal_value_hints_l_english.yml"
OUTPUT_NAME = "glorpui_generated_societal_value_hints_l_russian.yml"


class Unrecognised(Exception):
    """A hint Glorp UI now writes in a shape the table above does not cover."""


def translate(value: str) -> str:
    for english, russian in TEMPLATES:
        if value.startswith(english):
            value = russian + value[len(english):]
            for suffix, replacement in CONCEPT_SUFFIXES:
                value = value.replace(suffix, replacement)
            return value
    raise Unrecognised(value)


def render(source: Path) -> tuple[str, int, int]:
    """The Russian file's text, and how many hints and body keys went into it."""
    lines = source.read_text(encoding="utf-8-sig").split("\n")

    out: list[str] = []
    translated = bodies = 0
    for line in lines:
        if line.strip() == "l_english:":
            out.append("l_russian:")
            continue
        match = ENTRY_RE.match(line)
        if not match:
            out.append(line)
            continue
        key, value = match.groups()
        if key.startswith("GLORP_UI_SVH_BODY_"):
            # Pure [Player.Custom('...')] concatenations — language independent.
            bodies += 1
            out.append(line)
            continue
        try:
            out[len(out):] = [' %s: "%s"' % (key, translate(value))]
        except Unrecognised as exc:
            raise Unrecognised("%s: %s" % (key, exc)) from None
        translated += 1

    out[0] = ("# Russian for Glorp UI's societal value hints, written by "
              "mods/glorpui_hints/tools/translate_hints.py. Do not edit by hand.")
    out.insert(1, "# Source: Glorp UI %s" % source.name)
    return "\n".join(out), translated, bodies


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv[1:])

    try:
        text, translated, bodies = render(args.source)
    except Unrecognised as exc:
        print("unrecognised hint template — add it to TEMPLATES: %s" % exc,
              file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8-sig", newline="\n")
    print("translated %d hints, copied %d body keys" % (translated, bodies))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

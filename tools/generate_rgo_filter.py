#!/usr/bin/env python3
"""Generate the RGO bonus predicate from EU5 game data.

The interface knows which buildings gain production efficiency from raw
materials in the province — BuildingType.HasPossibleRGOBonus drives the shovel
badge — but that is a GUI data function, and list filters run script triggers.
So the same question gets answered from the game files instead: cross every
production method's goods inputs with the goods flagged as raw materials, and
emit scripted triggers a filter can call.

Usage:
    python3 tools/generate_rgo_filter.py <game>/in_game/common

where the common directory holds goods/, production_methods/ and
building_types/. Writes in_game/common/scripted_triggers/.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Keys inside a production method that carry a number but are not a goods input.
NON_INPUT_NUMERIC_KEYS = {"output"}

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = (
    REPO_ROOT / "in_game" / "common" / "scripted_triggers" / "bag_rgo_generated_triggers.txt"
)

TOKEN_RE = re.compile(r'"[^"]*"|[{}=]|[^\s{}=]+')
NUMBER_RE = re.compile(r"^-?\d+(\.\d+)?$")


def tokenize(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        hash_pos = line.find("#")
        if hash_pos != -1:
            line = line[:hash_pos]
        lines.append(line)
    return TOKEN_RE.findall("\n".join(lines))


def parse(tokens: list[str], pos: int = 0, depth: int = 0):
    """Parse a Paradox block into a list of (key, value) pairs.

    A value is either a string or a nested list of pairs. Bare tokens inside a
    block (list entries such as possible_production_methods) are recorded as
    (None, token).
    """
    entries = []
    while pos < len(tokens):
        token = tokens[pos]
        if token == "}":
            return entries, pos + 1
        if token == "{":
            # An anonymous nested block; skip over it.
            _, pos = parse(tokens, pos + 1, depth + 1)
            continue
        if pos + 1 < len(tokens) and tokens[pos + 1] == "=":
            key = token.strip('"')
            if pos + 2 < len(tokens) and tokens[pos + 2] == "{":
                value, pos = parse(tokens, pos + 3, depth + 1)
            else:
                value = tokens[pos + 2].strip('"') if pos + 2 < len(tokens) else ""
                pos = pos + 3
            entries.append((key, value))
            continue
        entries.append((None, token.strip('"')))
        pos += 1
    return entries, pos


def load(path: Path):
    entries, _ = parse(tokenize(path.read_text(encoding="utf-8-sig", errors="replace")))
    return entries


def load_dir(directory: Path):
    """Top level blocks across every .txt in a directory, minus readmes."""
    blocks = {}
    for path in sorted(directory.glob("*.txt")):
        if "readme" in path.name.lower():
            continue
        for key, value in load(path):
            if key is not None and isinstance(value, list):
                blocks[key] = value
    return blocks


def find(entries, name):
    return [value for key, value in entries if key == name]


def goods_inputs(method_entries) -> set[str]:
    """Goods a production method consumes, i.e. its numeric keys bar output."""
    inputs = set()
    for key, value in method_entries:
        if key is None or isinstance(value, list):
            continue
        if key in NON_INPUT_NUMERIC_KEYS:
            continue
        if NUMBER_RE.match(value):
            inputs.add(key)
    return inputs


def raw_material_goods(goods_dir: Path) -> set[str]:
    """Goods whose category is raw_material — the ones an RGO can produce.

    The category defaults to raw_material when omitted, per goods/readme.txt.
    """
    raw = set()
    for name, entries in load_dir(goods_dir).items():
        categories = find(entries, "category")
        if all(category == "raw_material" for category in categories):
            raw.add(name)
    return raw


def shared_methods(methods_dir: Path) -> dict[str, set[str]]:
    return {name: goods_inputs(entries) for name, entries in load_dir(methods_dir).items()}


def building_inputs(building_dir: Path, shared: dict[str, set[str]]) -> dict[str, set[str]]:
    """Every goods input each building type could ever consume."""
    result = {}
    for name, entries in load_dir(building_dir).items():
        inputs = set()
        for block in find(entries, "unique_production_methods"):
            for _, method in block:
                if isinstance(method, list):
                    inputs |= goods_inputs(method)
        for block in find(entries, "possible_production_methods"):
            for key, value in block:
                method_name = value if key is None else key
                inputs |= shared.get(method_name, set())
        result[name] = inputs
    return result


def build_index(common: Path):
    raw = raw_material_goods(common / "goods")
    shared = shared_methods(common / "production_methods")
    buildings = building_inputs(common / "building_types", shared)

    # Invert into raw material -> building types that consume it.
    by_good: dict[str, list[str]] = {}
    for building, inputs in buildings.items():
        for good in sorted(inputs & raw):
            by_good.setdefault(good, []).append(building)
    return raw, buildings, {good: sorted(names) for good, names in sorted(by_good.items())}


def render(by_good: dict[str, list[str]]) -> str:
    out = [
        "﻿# GENERATED by tools/generate_rgo_filter.py -- do not edit by hand.",
        "#",
        "# Answers, in script, the question the interface answers with",
        "# BuildingType.HasPossibleRGOBonus: does this building type consume a raw",
        "# material that the province can produce? One trigger per raw material lists",
        "# the building types consuming it, gathered from every production method the",
        "# type offers.",
        "",
    ]

    for good, buildings in by_good.items():
        out.append("# Scope: building_type")
        out.append("bag_rgo_consumes_%s = {" % good)
        out.append("\tOR = {")
        for building in buildings:
            out.append("\t\tthis = building_type:%s" % building)
        out.append("\t}")
        out.append("}")
        out.append("")

    out.append("# True when this location's raw material feeds the building type in root.")
    out.append("# Scope: location, root: building_type")
    out.append("bag_rgo_location_feeds_root = {")
    out.append("\tOR = {")
    for good in by_good:
        out.append("\t\tAND = {")
        out.append("\t\t\traw_material = goods:%s" % good)
        out.append("\t\t\troot = { bag_rgo_consumes_%s = yes }" % good)
        out.append("\t\t}")
    out.append("\t}")
    out.append("}")
    out.append("")
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    common = Path(sys.argv[1])
    missing = [
        name
        for name in ("goods", "production_methods", "building_types")
        if not (common / name).is_dir()
    ]
    if missing:
        print("missing under %s: %s" % (common, ", ".join(missing)), file=sys.stderr)
        return 1

    raw, buildings, by_good = build_index(common)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render(by_good), encoding="utf-8")

    matched = sum(1 for inputs in buildings.values() if inputs & raw)
    print("raw material goods:      %d" % len(raw))
    print("building types:          %d" % len(buildings))
    print("  with a raw input:      %d" % matched)
    print("raw materials in use:    %d" % len(by_good))
    print("pairs:                   %d" % sum(len(v) for v in by_good.values()))
    print("wrote %s" % OUT_PATH.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

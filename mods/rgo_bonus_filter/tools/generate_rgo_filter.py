#!/usr/bin/env python3
"""Generate the RGO bonus predicate from EU5 game data.

The interface knows which buildings gain production efficiency from raw
materials in the province — BuildingType.HasPossibleRGOBonus drives the shovel
badge — but that is a GUI data function, and list filters run script triggers.
So the same question gets answered from the game files instead: cross every
production method's goods inputs with the goods flagged as raw materials, and
emit scripted triggers a filter can call.

Usage:
    python3 mods/rgo_bonus_filter/tools/generate_rgo_filter.py [<game>/in_game/common]

Defaults to the game files in `reference/`, so the argument is only for pointing
it at a different copy. The common directory has to hold goods/,
production_methods/ and building_types/. Writes
in_game/common/scripted_triggers/.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Keys inside a production method that carry a number but are not a goods input.
NON_INPUT_NUMERIC_KEYS = {"output"}

MOD_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MOD_ROOT.parent.parent / "tools"))
import refs  # noqa: E402  the reference tree, resolved by mod id

OUT_PATH = (
    MOD_ROOT / "in_game" / "common" / "scripted_triggers" / "bag_rgo_generated_triggers.txt"
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


def method_produces(method_entries) -> bool:
    """Whether a production method outputs a good rather than only upkeep.

    The game only badges a building with the shovel when it is producing —
    `And(BuildingType.IsProducing, BuildingType.HasPossibleRGOBonus(...))`. A
    monastery consumes clay through a maintenance method and gives nothing back,
    so it has no production efficiency for a raw material to improve. Methods
    carrying `produced` are the ones that count.
    """
    return any(key == "produced" for key, _ in method_entries)


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
    """Named production methods, skipping the ones that only cost upkeep."""
    return {
        name: goods_inputs(entries)
        for name, entries in load_dir(methods_dir).items()
        if method_produces(entries)
    }


def building_inputs(building_dir: Path, shared: dict[str, set[str]]) -> dict[str, set[str]]:
    """Goods each building type consumes while actually producing something.

    Building types with no producing method at all fall out with an empty set,
    which is what keeps upkeep-only buildings out of the filter.
    """
    result = {}
    for name, entries in load_dir(building_dir).items():
        inputs = set()
        for block in find(entries, "unique_production_methods"):
            for _, method in block:
                if isinstance(method, list) and method_produces(method):
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

    # The build panel filters locations against a fixed building type, so the
    # type comes from the global variable its probe writes. This is the pair
    # that has been seen working on screen.
    out.append("# True when this location's raw material feeds the building "
               "type being built.")
    out.append("# Scope: location")
    out.append("bag_rgo_location_feeds_build_type = {")
    out.append("\tOR = {")
    for good in by_good:
        out.append("\t\tAND = {")
        out.append("\t\t\traw_material = goods:%s" % good)
        out.append("\t\t\tglobal_var:bag_rgo_build_type = "
                   "{ bag_rgo_consumes_%s = yes }" % good)
        out.append("\t\t}")
    out.append("\t}")
    out.append("}")
    out.append("")

    # **И обратная пара -- та, что не работала, и теперь известно почему.**
    #
    # Панель зданий локации фильтрует типы против фиксированной локации, и
    # прежняя форма спрашивала тип через `root`, как обещает комментарий игры в
    # `58_building_type.txt`. Прогон 2026-09-09 (`where_to_produce`, фишка «Из
    # плана — сюда») показал, что `root` в фильтре -- **не** отфильтровываемый
    # объект: фишка на `root` не оставила ни одного здания при заведомо
    # заполненных данных, а всё, что спрашивает неявный `this`, работает. Игра и
    # сама пишет «root is player» в `06_country.txt`; про `scope:target` тот же
    # комментарий уже был неправ.
    #
    # Поэтому вопрос «потребляет ли этот тип сырьё G» задаётся **до** смены
    # скоупа, неявным `this`, а на локацию уходит уже литерал. Заодно это
    # дешевле прежнего: обход провинции идёт только по тем нескольким видам
    # сырья, которые этот тип действительно потребляет, а не по всем на каждую
    # локацию.
    for name, inside in (
        ("bag_rgo_has_local_bonus",
         "province = { any_location_in_province = { raw_material = goods:%s } }"),
        ("bag_rgo_has_local_bonus_here", "raw_material = goods:%s"),
    ):
        out.append("# %s" % (
            "Which building types gain from a raw material anywhere in the "
            "province the panel is showing." if name.endswith("bonus") else
            "Same, but only the location on screen counts."))
        out.append("# Scope: building_type")
        out.append("%s = {" % name)
        out.append("\thas_global_variable = bag_view_location")
        out.append("\tOR = {")
        for good in by_good:
            out.append("\t\tAND = {")
            out.append("\t\t\tbag_rgo_consumes_%s = yes" % good)
            out.append("\t\t\tglobal_var:bag_view_location = { %s }"
                       % (inside % good))
            out.append("\t\t}")
        out.append("\t}")
        out.append("}")
        out.append("")
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) > 2:
        print(__doc__)
        return 2

    common = Path(sys.argv[1]) if len(sys.argv) == 2 else refs.GAME_COMMON
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
    print("wrote %s" % OUT_PATH.relative_to(MOD_ROOT.parent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Read the parts of the EU5 game files this mod reasons about.

Point `load_game(path)` at `<EU5>/game/in_game/common` and it returns the goods
catalogue plus every production method, resolved per building type.

The one formula that matters, recovered by matching the game's own tooltips:

    RGO bonus % = RGO_MAX_BONUS * (locally available input amounts)
                                / (all input amounts)

Confirmed exactly against three in-game readings at 1.3.10:

    saltpeter_guild / saltpeter_guild_demands
        pottery 0.1961 + livestock 0.9804 = 1.1765
        livestock / total = 0.8333               -> 8.33%   tooltip +8.33%

    weapon_guild / weapon_smith_maintenance
        lumber 0.2521 + coal 0.3034 + tools 0.5050 = 1.0605
        coal / total = 0.2861                    -> 2.86%   tooltip +2.86%

    mason / clay_bricks
        clay alone                               -> 10.00%  tooltip +10.00%

Every input counts towards the denominator, including produced goods such as
tools that can never come from an RGO. That is why a method can have a ceiling
well below the full bonus: weapon_smith_maintenance tops out at 5.24%, because
tools carry nearly half its weight.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# The bonus a method reaches when every input is available locally. Matches the
# three readings above; the game presumably keeps it in a define.
RGO_MAX_BONUS = 10.0

TOKEN_RE = re.compile(r'"[^"]*"|[{}=]|[^\s{}=]+')
NUMBER_RE = re.compile(r"^-?\d+(\.\d+)?$")

# Numeric keys inside a production method that are not goods inputs.
NON_INPUT_KEYS = {"output"}


def tokenize(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        hash_pos = line.find("#")
        if hash_pos != -1:
            line = line[:hash_pos]
        lines.append(line)
    return TOKEN_RE.findall("\n".join(lines))


def parse(tokens: list[str], pos: int = 0):
    """Parse a Paradox block into (key, value) pairs; bare tokens key on None."""
    entries = []
    while pos < len(tokens):
        token = tokens[pos]
        if token == "}":
            return entries, pos + 1
        if token == "{":
            _, pos = parse(tokens, pos + 1)
            continue
        if pos + 1 < len(tokens) and tokens[pos + 1] == "=":
            key = token.strip('"')
            if pos + 2 < len(tokens) and tokens[pos + 2] == "{":
                value, pos = parse(tokens, pos + 3)
            else:
                value = tokens[pos + 2].strip('"') if pos + 2 < len(tokens) else ""
                pos += 3
            entries.append((key, value))
            continue
        entries.append((None, token.strip('"')))
        pos += 1
    return entries, pos


def load_dir(directory: Path) -> dict:
    """Top level blocks across every .txt in a directory, minus readmes."""
    blocks = {}
    for path in sorted(directory.glob("*.txt")):
        if "readme" in path.name.lower():
            continue
        entries, _ = parse(tokenize(path.read_text(encoding="utf-8-sig", errors="replace")))
        for key, value in entries:
            if key is not None and isinstance(value, list):
                blocks[key] = value
    return blocks


def find(entries, name):
    return [value for key, value in entries if key == name]


def scalar(entries, name):
    for key, value in entries:
        if key == name and not isinstance(value, list):
            return value
    return None


@dataclass
class Method:
    """One production method, as offered by one building type."""

    key: str
    building: str
    produced: str
    output: float
    inputs: dict[str, float] = field(default_factory=dict)

    @property
    def total_input(self) -> float:
        return sum(self.inputs.values())

    def raw_inputs(self, raw_goods: set[str]) -> dict[str, float]:
        """Inputs an RGO could supply. The rest can never be sourced locally."""
        return {g: a for g, a in self.inputs.items() if g in raw_goods}

    def bonus(self, available: set[str]) -> float:
        """The RGO bonus this method gets where `available` is produced."""
        total = self.total_input
        if not total:
            return 0.0
        covered = sum(a for g, a in self.inputs.items() if g in available)
        return RGO_MAX_BONUS * covered / total

    def ceiling(self, raw_goods: set[str]) -> float:
        """The best this method could ever reach, with every RGO input present."""
        return self.bonus(set(self.raw_inputs(raw_goods)))


@dataclass
class Game:
    raw_goods: set[str]
    methods: list[Method]

    def producing(self, good: str) -> list[Method]:
        """Methods that output `good` and could gain something locally, best first."""
        rows = [
            m for m in self.methods
            if m.produced == good and m.raw_inputs(self.raw_goods)
        ]
        return sorted(rows, key=lambda m: (-m.output, m.building, m.key))

    @property
    def goods_produced(self) -> list[str]:
        return sorted({m.produced for m in self.methods if m.raw_inputs(self.raw_goods)})


def _inputs(entries) -> dict[str, float]:
    out = {}
    for key, value in entries:
        if key is None or isinstance(value, list) or key in NON_INPUT_KEYS:
            continue
        if NUMBER_RE.match(value):
            out[key] = float(value)
    return out


def _raw_goods(goods_dir: Path) -> set[str]:
    """Goods an RGO can produce. `category` defaults to raw_material when absent."""
    raw = set()
    for name, entries in load_dir(goods_dir).items():
        if all(c == "raw_material" for c in find(entries, "category")):
            raw.add(name)
    return raw


def load_game(common: Path) -> Game:
    raw = _raw_goods(common / "goods")
    shared = load_dir(common / "production_methods")

    methods: list[Method] = []
    for building, entries in load_dir(common / "building_types").items():
        blocks: list[tuple[str, list]] = []
        for block in find(entries, "unique_production_methods"):
            blocks += [(name, body) for name, body in block if isinstance(body, list)]
        for block in find(entries, "possible_production_methods"):
            for key, value in block:
                name = value if key is None else key
                if name in shared:
                    blocks.append((name, shared[name]))

        for name, body in blocks:
            produced = scalar(body, "produced")
            if produced is None:
                # Upkeep only. The game gates its shovel badge on IsProducing,
                # and a building that outputs nothing has no efficiency to gain.
                continue
            output = scalar(body, "output")
            methods.append(Method(
                key=name,
                building=building,
                produced=produced,
                output=float(output) if output and NUMBER_RE.match(output) else 0.0,
                inputs=_inputs(body),
            ))
    return Game(raw_goods=raw, methods=methods)

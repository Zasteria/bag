"""Read the parts of the EU5 game files a mod is likely to reason about.

Point `load_game(path)` at `<EU5>/game/in_game/common` — or call it with no
argument for the copy in `reference/` — and it returns the goods catalogue plus
every production method, resolved per building type.

This outlived the mod it was written for. `where_to_produce` was removed in
August 2026 without ever working in game (see `docs/archive/where_to_produce.md`), but its data
layer was the half that was right: every number below was checked against the
game, and re-deriving them would cost another set of tooltip readings.

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


# The four groups the goods picker offers, keyed on the category of the building
# that makes the good. A good is filed under the category of its best yielding
# recipe, which settles the nine that several categories can produce.
CATEGORY_GROUPS = (
    ("rgo", "rgo_building_category"),
    ("basic", "basic_industry_category"),
    ("consumer", "consumer_goods_category"),
    ("weapons", "weapons_industry_category"),
)


@dataclass
class Method:
    """One production method, as offered by one building type."""

    key: str
    building: str
    building_category: str
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
class TownRight:
    """One urban right, and the goods whose output it raises.

    Only the output half is read. A right that grants building levels instead --
    Flemish cloth, the marketplace charters -- is a quantity where these are
    ratios, and `docs/investigations/town_rights.md` is why the two must not
    share a number. `levels` is kept so the omission is visible rather than
    silent.
    """
    key: str
    output: dict[str, float] = field(default_factory=dict)
    levels: dict[str, float] = field(default_factory=dict)
    penalty: bool = False
    # The advance that unlocks it, from `unlock_town_rights` in `common/advances`,
    # and the country condition the right carries itself. Both are how a right
    # that is somebody else's is kept off this country's list: Constantinople's
    # silk monopoly says `has_or_had_tag = BYZ`, and the Scandinavian privileges
    # say nothing but come from an advance only a Scandinavian takes.
    advance: str = ""
    potential: str = ""

    @property
    def general(self) -> bool:
        """Everybody's, eventually: the nine that one age-3 advance unlocks."""
        return self.advance == "town_rights_enable"


@dataclass
class Game:
    raw_goods: set[str]
    methods: list[Method]
    # What a unit of each good sells for, `default_market_price`. The only
    # honest way to add one good's output to another's.
    prices: dict[str, float] = field(default_factory=dict)
    town_rights: list[TownRight] = field(default_factory=list)
    # Every good in the catalogue, raw and produced alike. A mod naming a good
    # checks it against this rather than against its own memory: a good that a
    # patch renames goes silently dead otherwise.
    all_goods: set[str] = field(default_factory=set)

    def group_of(self, good: str) -> str:
        """Which picker group a good belongs in, or "" if none fits."""
        # A good is filed under the most specific industry that makes it. Masonry
        # comes from both a quarry and a mason's yard, and the game lists it under
        # basic industry, not raw materials -- so the industries outrank the RGO.
        known = {category: name for name, category in CATEGORY_GROUPS}
        found = {known[m.building_category] for m in self.producing(good)
                 if m.building_category in known}
        for name in ("weapons", "consumer", "basic", "rgo"):
            if name in found:
                return name
        # Plantation and village buildings carry categories of their own. What
        # they make -- cotton, sugar, livestock, fish -- is raw material, so it
        # belongs with the rest of it rather than in no group at all.
        return "rgo"

    def goods_by_group(self) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {name: [] for name, _ in CATEGORY_GROUPS}
        for good in self.goods_produced:
            group = self.group_of(good)
            if group:
                groups[group].append(good)
        return groups

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


def _inputs(entries, goods: set[str]) -> dict[str, float]:
    """Goods amounts a method consumes.

    Matched against the goods catalogue rather than "any numeric key": methods
    also carry bookkeeping numbers, and `debug_max_profit = -1` on the
    plantations is numeric enough to have turned four recipes' input weight
    negative before this was keyed on real goods.
    """
    out = {}
    for key, value in entries:
        if key is None or isinstance(value, list) or key in NON_INPUT_KEYS:
            continue
        if key in goods and NUMBER_RE.match(value):
            out[key] = float(value)
    return out


def _goods(goods_dir: Path) -> tuple[set[str], set[str], dict[str, float]]:
    """All goods, the subset an RGO can produce, and what each is worth.

    `category` defaults to raw_material when absent and `default_market_price`
    to 1, both per goods/readme.txt. The price is what makes goods addable: four
    books a level and 0.3 masonry a level are not one number without it.
    """
    every, raw, price = set(), set(), {}
    for name, entries in load_dir(goods_dir).items():
        every.add(name)
        if all(c == "raw_material" for c in find(entries, "category")):
            raw.add(name)
        found = [float(v) for v in find(entries, "default_market_price")]
        price[name] = found[0] if found else 1.0
    return every, raw, price


def _raw_potentials(rights_dir: Path) -> dict[str, str]:
    """Each right's `potential` block, as text, to be re-emitted verbatim.

    The loader turns a file into a structure, and what is wanted here is the
    trigger exactly as the game wrote it -- `OR = { has_or_had_tag = BYZ ... }`
    goes straight into a scripted trigger of ours. `potential` is country
    scoped, per `town_rights/readme.txt`, which is what makes that safe.
    """
    import re as _re
    out: dict[str, str] = {}
    if not rights_dir.is_dir():
        return out
    for path in sorted(rights_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8-sig")
        for match in _re.finditer(r"^(\w+)\s*=\s*\{", text, _re.M):
            depth, i = 0, match.end() - 1
            while i < len(text):
                depth += (text[i] == "{") - (text[i] == "}")
                if depth == 0 and text[i] == "}":
                    break
                i += 1
            body = text[match.end():i]
            block = _re.search(r"potential\s*=\s*\{", body)
            if not block:
                continue
            depth, j = 0, block.end() - 1
            while j < len(body):
                depth += (body[j] == "{") - (body[j] == "}")
                if depth == 0 and body[j] == "}":
                    break
                j += 1
            out[match.group(1)] = " ".join(body[block.end():j].split())
    return out


def _unlocked_by(advances_dir: Path) -> dict[str, str]:
    """Which advance unlocks each town right, by `unlock_town_rights`."""
    out: dict[str, str] = {}
    if not advances_dir.is_dir():
        return out
    for name, entries in load_dir(advances_dir).items():
        for right in find(entries, "unlock_town_rights"):
            out.setdefault(str(right), name)
    return out


def _town_rights(rights_dir: Path, advances_dir: Path) -> list[TownRight]:
    """Every urban right, with the goods it raises and the levels it grants.

    Read from the game rather than from `town_rights_l_english.yml`, which names
    every bundle in prose and is exactly the source this repository has a rule
    against believing.
    """
    if not rights_dir.is_dir():
        return []
    unlocked = _unlocked_by(advances_dir)
    potentials = _raw_potentials(rights_dir)
    out: list[TownRight] = []
    for name, entries in load_dir(rights_dir).items():
        right = TownRight(key=name, advance=unlocked.get(name, ""),
                          potential=potentials.get(name, ""))
        for block in find(entries, "location_modifier"):
            for key, value in block:
                if key is None or not isinstance(value, str):
                    continue
                if key == "local_production_efficiency":
                    right.penalty = True
                    continue
                if not key.startswith("local_"):
                    continue
                try:
                    amount = float(value)
                except ValueError:
                    continue
                body = key[len("local_"):]
                if body.endswith("_output_modifier"):
                    right.output[body[:-len("_output_modifier")]] = amount
                elif body.endswith("_building_levels"):
                    good = body[:-len("_building_levels")]
                    right.levels[good.removesuffix("_guild")] = amount
        if right.output or right.levels:
            out.append(right)
    return sorted(out, key=lambda r: r.key)


def load_game(common: Path | None = None) -> Game:
    if common is None:
        import refs  # local: only needed when no explicit copy was named
        common = refs.GAME_COMMON
    goods, raw, price = _goods(common / "goods")
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
                building_category=scalar(entries, "category") or "",
                produced=produced,
                output=float(output) if output and NUMBER_RE.match(output) else 0.0,
                inputs=_inputs(body, goods),
            ))
    return Game(raw_goods=raw, methods=methods, all_goods=goods, prices=price,
                town_rights=_town_rights(common / "town_rights",
                                         common / "advances"))

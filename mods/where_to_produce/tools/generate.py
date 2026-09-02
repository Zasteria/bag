#!/usr/bin/env python3
"""Generate everything `where_to_produce` cannot write by hand.

The mod answers one question: **for this good, where is the best place to make
it, and with what.** The player names a good; the mod finds, per location, the
best production method available for that good there, and ranks the locations by
what that method would earn from the raw materials the province supplies.

Choosing the method was the player's job for one round and it should not have
been: knowing which recipe suits which ground *is* the question the mod exists to
answer, so asking it back was asking the player to do the work first.

Four things come out of the game's own files rather than out of a list somebody
typed, so a patch that adds a method or renames a region is picked up by a
rebuild:

  - **The good picker.** Two lists, split the way the goods themselves are: the
    25 raw materials an RGO can also make, and the 22 things only a workshop
    makes. Lists rather than dropdowns -- CMF handles a dropdown option click
    through `CMM_MarkDropdownSelection_<index>` and defines twenty of them, so a
    dropdown is silently unclickable past its twentieth option. A list is handled
    to fifty.
  - **The zone.** The five land continents, ticked. Not a walk: a location's
    continent is one plain trigger, so nothing has to be marked in advance.
  - **The scoring.** One script value per method giving what it would earn here,
    and one effect per good that runs its methods over the candidates and keeps
    the best. That is where "the mod finds the method" actually happens.
  - **The result rows.** Fifty of them, each reading back a location, a number
    and the building that won it.

The formula is `eu5data.Method.bonus`, verified to the digit against three
in-game tooltips at 1.3.10. See `docs/research/engine.md`.

    python3 mods/where_to_produce/tools/generate.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
REPO = MOD.parent.parent
sys.path.insert(0, str(REPO / "tools"))

import eu5data  # noqa: E402
import refs  # noqa: E402

MOD_ID = "bag_wtp"

# How many rows any list has at most. CMF initialises list items through an
# unrolled chain of `if`s that ends at fifty, and handles a row click through
# `CMM_MarkListPosition_*`, which is unrolled to the same fifty. Raising this
# means leaving CMM, not editing this number.
LIST_CAP = 50
RESULT_ROWS = 50

# What `bag_wtp_m<n>` is multiplied by before anything ranks on it. A method's
# output is a fraction of a unit and the differences between two provinces are
# in its third decimal; nothing in the game or in `reference/` sorts on numbers
# that small. At 1000 the largest method in the game comes to about 4950, which
# is small enough to be nowhere near any fixed-point ceiling, and the smallest
# difference the bonus can make is still worth about half a unit.
RANK_SCALE = 1000

# Raw materials a single method can want. The widest recipe in the game takes
# five.
MAX_INPUTS = 5

# What counts as rural. `village_category` is the game's own: forest, market,
# farming and fishing villages, thirteen methods between them, each producing a
# fifth to a half of what a workshop of the same good does. They are scored on
# their own side so a village never displaces a guild in the ranking, and shown
# beside it because rural ground is built on too.
RURAL_CATEGORIES = ("village_category",)

# How many goods one urban right can favour. Three is the widest in the game --
# paper, books and dyes; cloth, fine cloth and dyes; three weapons; three
# drinks -- and a row holds a fixed number of answers rather than a variable
# one, because script has no list of tuples and the answers are flat variables
# on the location.
RIGHT_SLOTS = 3

# A bundle's total is a sum of `RANK_SCALE`d outputs times market prices, and it
# runs an order of magnitude higher than a single good's: textile rights with
# every input present come to 64 680, against a single method's 4 950. Whether
# the engine's fixed point is 32-bit is not knowable from here and 21 474 is
# where a 32-bit one ends, so the weights carry a tenth of `RANK_SCALE` -- worst
# case 6 468, and the smallest difference the bonus can make is still about 4.6.
RIGHT_SCALE = RANK_SCALE // 10

# The whole-map plan. How many rounds of allocation the player may ask for at
# most, and how many rows the plan window draws. The first is a ceiling on a
# setting rather than the setting itself: CMM clamps the number he chooses, and
# a `while` in an effect that cannot leave its condition is a hung game rather
# than an error in a log.
PLAN_ROUNDS = 12
# More than `RESULT_ROWS`, because a plan's row is a location where a ranking's
# is a province -- the same ground is four to eight times the rows. Only the
# datamodel decides what a scripted widget costs, and this list is filled on
# opening and emptied on closing like the other two.
PLAN_ROWS = 150

# The sweeps run in tiers, and a tier admits only goods that at most this many
# candidate locations could hold. **The scarce go first**: a good with one place
# in the whole ground takes it before a good with forty gets its second, which is
# the owner's «жёстко зарезервировать слоты». 0 is the last tier and means
# everything.
# What a building the ground does not feed is worth against one it does. The
# bonus itself is only a ten per cent band, so a penalty has to be an outright
# divisor rather than a difference in bonus: the owner wants the unfed case
# minimised, not forbidden.
UNFED_PENALTY = 2

# What one buildable good of a right's bundle is worth beside how good it is.
# Twice `RANK_SCALE`, so that a bundle a town can finish always outranks a bigger
# one it cannot, whatever the scores inside them.
RIGHT_FIT = 2000

PLAN_TIERS = (1, 2, 4, 8, 16, 0)

# The gain a placement has to reach to be made in this pass, out of `RANK_SCALE`.
# Descending, and the last is 0 because a good the ground feeds nothing is still
# a good that has to be produced. Five rather than ten: a band costs a sweep over
# every tier, and the plan is already the expensive button.
PLAN_BANDS = (800, 600, 400, 200, 0)

# The pass after all of them, with the quota lifted rather than a candidate count
# of its own. `is` on a sentinel and not a seventh number, because the tier value
# it writes is 0 like the last real tier's.
OPEN_TIER = object()

# The pass that keeps the covering constraint: only goods with nothing anywhere,
# at any gain, into any free slot. It is not a tier and not a band.
COVER_TIER = object()

# **The allocator's passes in order, and the one list both it and the dump read.**
# The bands wrap the scarcity tiers; then coverage, then the open pass. Written
# out here rather than built twice, because the dump numbers a pass by its place
# in this list and a diagnosis that names the wrong pass is worse than none.
PLAN_PASSES = ([(band, tier) for band in PLAN_BANDS for tier in PLAN_TIERS]
               + [(0, COVER_TIER), (0, OPEN_TIER)])


def pass_name(band: int, tier: object) -> str:
    """How a pass is written in the dump: the band it admits and the tier it is."""
    if tier is COVER_TIER:
        return "cover"
    if tier is OPEN_TIER:
        return "open"
    return f"band{band}/tier{tier if tier else 'all'}"

# The diagnostic dump: what one press writes into the log, and the caps on it.
# **A cap must never be silently the answer**, so every capped block prints how
# many it left out. `docs/pitfalls/diagnosis.md` has the whole instrument and the
# four things about `debug_log` that were measured rather than assumed.
DIAG_VERSION = 3
DIAG_LOCS = 60
DIAG_ROWS = 25
# The scratch globals a printed line reads through. **A `debug_log` string cannot
# reach the item a walk is standing on** -- measured 2026-09-02, `THIS.MakeScope`
# fails and the bracket is echoed literally -- so every number is parked in one of
# these first and printed from there. Sixteen because the widest line, a good's,
# has sixteen numbers on it.
DIAG_SCRATCH = 16

# The land continents, in the order the game's own localization lists them. The
# ocean continent is not offered: nothing is built there.
CONTINENTS = ("europe", "asia", "africa", "america", "oceania")

# One tab per job. A CMM tab is just a `tab_id` on the settings under it, so this
# costs nothing but the three localization keys -- and the first build had five
# groups stacked on one tab, which meant scrolling past the goods to reach the
# answer.
TAB_GOODS = "goods"
TAB_ZONE = "zone"
TAB_PLAN = "plan"

ZONE_OUT = MOD / "in_game/common/scripted_effects/bag_wtp_generated_zone.txt"
REGION_OUT = MOD / "in_game/common/scripted_effects/bag_wtp_generated_regions.txt"
PICKER_OUT = MOD / "in_game/common/scripted_effects/bag_wtp_generated_picker.txt"
SCORE_OUT = MOD / "in_game/common/scripted_effects/bag_wtp_generated_score.txt"
ROWS_OUT = MOD / "in_game/common/scripted_effects/bag_wtp_generated_rows.txt"
VALUES_OUT = MOD / "in_game/common/script_values/bag_wtp_generated_values.txt"
TRIGGERS_OUT = MOD / "in_game/common/scripted_triggers/bag_wtp_generated_triggers.txt"
GUIS_OUT = MOD / "in_game/common/scripted_guis/bag_wtp_generated_scripted_gui.txt"
LAYOUT_OUT = MOD / "in_game/common/scripted_effects/bag_wtp_generated_layout.txt"
RIGHTS_OUT = MOD / "in_game/common/scripted_effects/bag_wtp_generated_rights.txt"
PLAN_OUT = MOD / "in_game/common/scripted_effects/bag_wtp_generated_plan.txt"
PLAN_TRIGGERS_OUT = MOD / "in_game/common/scripted_triggers/bag_wtp_generated_plan_triggers.txt"
PLAN_LOC_OUT = MOD / "in_game/common/customizable_localization/bag_wtp_generated_plan_loc.txt"
DIAG_OUT = MOD / "in_game/common/scripted_effects/bag_wtp_generated_diag.txt"
LOC_OUT = MOD / "main_menu/localization/%s/bag_wtp_generated_l_%s.yml"
LOC_LANGUAGES = ("english", "russian")

BOM = "﻿"
HEADER = "# Generated by mods/where_to_produce/tools/generate.py. Do not edit by hand.\n"


def unlocks() -> dict[str, str]:
    """Production method -> the advance that unlocks it.

    Only ten methods are gated this way; the rest ride on their building's own
    unlock, of which there are 119 with an age attached. Both are asked through
    `can_build_building` in country scope and `has_advance`.
    """
    out: dict[str, str] = {}
    for path in (refs.GAME / "in_game/common/advances").glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig")
        for block in re.finditer(r"^([a-z0-9_]+)\s*=\s*\{(.*?)^\}", text, re.S | re.M):
            for method in re.findall(r"unlock_production_method\s*=\s*([a-z0-9_]+)",
                                     block.group(2)):
                out[method] = block.group(1)
    return out


UNLOCKS = unlocks()


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(BOM + body, encoding="utf-8")


# --------------------------------------------------------------------------
# What the game offers


def methods(game: eu5data.Game) -> list[eu5data.Method]:
    """Every method that could gain something from an RGO.

    A method with no raw-material input can never take the bonus, so scoring it
    would be scoring a zero.
    """
    rows = [m for m in game.methods if m.raw_inputs(game.raw_goods)]
    return sorted(rows, key=lambda m: (m.produced, m.building, m.key))


def fed_floor(method: eu5data.Method, game: eu5data.Game) -> float:
    """The `_m` a method has to beat before this ground counts as feeding it.

    **Half the bonus the recipe could ever earn, and that is the whole rule.**
    Before it the floor was the unbonused output, so one input out of three was
    enough: the twenty-fifth run's fine cloth put silk weavers at the top of a
    province that has dyes and no silk -- the silk half of the recipe unfed, the
    dyeing half fed, 1.78% of a possible 10 -- and the player's answer was that
    a silk weaver where there is no silk is not an answer at all. It is not a
    number the market can be asked about; the ground is what this mod can see,
    and a recipe whose bulk has to be shipped in is one the ground did not earn.

    Two things fall out of it that are worth keeping straight:

    - **an input the RGOs cannot supply does not count against a method.** The
      ceiling is already only what raw materials could ever add, so fine cloth
      from cloth -- cloth is made, not dug -- asks only for its dyes and passes
      on them. That is the answer the same province gets instead of the silk.
    - **a method with one raw input is unchanged**, because half of its ceiling
      is cleared by that one input or by nothing at all. The rule bites exactly
      where the eighteenth run's did not: recipes with a main ingredient and a
      garnish.

    The floor is put midway between the two nearest sums the goods can actually
    make, rather than at half the ceiling itself, so no combination of inputs can
    land on the boundary and be decided by the fixed point. The narrowest that
    gap gets is 0.12 of a scaled point, on the cannon maker's four inputs, against
    0.00025 of rounding in the `.4f` the script values are written with.
    """
    shares = sorted(v for good, v in method.shares().items()
                    if good in game.raw_goods)
    sums = {0.0}
    for share in shares:
        sums |= {s + share for s in sums}
    target = sum(shares) / 2
    below = max((s for s in sums if s < target), default=0.0)
    above = min((s for s in sums if s >= target), default=target)
    return method.output * RANK_SCALE * (1 + (below + above) / 2 / 100)


def endgame(rows: list[eu5data.Method], game: eu5data.Game) -> set[int]:
    """Which of `rows` are still buildable once every advance is in, by index.

    The game's own ladder, read off `obsolete`: guild -> workshop -> manufactory
    -> mill, thirty chains of it, and a building somebody obsoletes is one nobody
    builds at the end. Ninety-four of the two hundred and eighteen methods
    survive it, and no method that does not survive can beat one that does --
    checked at full bonus over every good and both sides -- so "the best of the
    survivors" is the answer the last age gives.

    **This is a second answer, not a better one.** Along the ladder the inputs
    move: bronze cannons want copper and tin, the cannon factory that replaces
    them wants lead and saltpetre; paper starts on cloth and ends on pure lumber;
    silk fine cloth tops out at 10% and the fine cloth mill at 0.63%. Fourteen of
    the forty-two goods shift their mix, five change it outright -- and for those
    the province that suits the guild is not the province that suits the mill,
    which is the whole reason a row carries both numbers.
    """
    return {index for index, method in enumerate(rows, start=1)
            if method.building not in game.obsoleted}


def goods_split(rows: list[eu5data.Method], game: eu5data.Game) -> dict[str, list[str]]:
    """The goods worth asking about, split into the two piles the player thinks in.

    A raw material is something an RGO also produces -- so a mason's yard and a
    quarry both make masonry, and the question "where should I make it" is a
    different one from "where should I make cannons".
    """
    goods = sorted({m.produced for m in rows})
    split = {
        "raw": [g for g in goods if g in game.raw_goods],
        "made": [g for g in goods if g not in game.raw_goods],
    }
    over = {k: len(v) for k, v in split.items() if len(v) > LIST_CAP}
    if over:
        raise SystemExit(f"a goods list is taller than CMM holds: {over}")
    return split


# --------------------------------------------------------------------------
# Output


def regions() -> dict[str, list[str]]:
    """Continent -> region keys, read off the game's own region localization.

    The file carries the hierarchy in its comments and it is the only place in
    `reference/` that knows it, because `map_data` is not in the tree. Two
    cautions, both paid for: five real regions sit under "Subcontinents" and
    `poland` is a region without the `_region` suffix, so the suffix is honoured
    wherever it appears and the Regions section counts on its own; and filtering
    water by name throws out `north_atlantic_islands_region`, which is dry land,
    so the file's own "Ocean Subcontinent" grouping does that job instead.
    """
    path = refs.GAME_LOCALIZATION / "english/region_names_l_english.yml"
    out: dict[str, list[str]] = {}
    seen: set[str] = set()
    section = continent = group = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("l_english"):
            continue
        indent = len(line) - len(line.lstrip())
        if stripped.startswith("#"):
            name = stripped.lstrip("#").strip()
            if indent <= 1:
                section, continent, group = name, None, None
            elif indent <= 2:
                continent, group = name, None
            else:
                group = name
            continue
        match = re.match(r"^([a-z0-9_]+):", stripped)
        if not match or continent is None:
            continue
        key = match.group(1)
        if not (key.endswith("_region") or section == "Regions"):
            continue
        if group == "Ocean Subcontinent" or key in seen:
            continue
        seen.add(key)
        out.setdefault(continent.lower(), []).append(key)
    over = {c: len(r) for c, r in out.items() if len(r) > LIST_CAP}
    if over:
        raise SystemExit(f"a continent has more regions than a CMM list holds: {over}")
    return {c: r for c, r in out.items() if c in CONTINENTS}


def region_file(by_continent: dict[str, list[str]]) -> str:
    """The regions, one list per continent, all on the zone tab.

    Ticking a whole continent paints the screen red and is a blunt frame; the
    good case is one region ticked, its ground offered and everything else left
    alone, with a neighbour addable beside it. Both are here: a continent row and
    a region row do the same thing to the same list.
    """
    out = [HEADER, "#\n# Scope: country\n"]
    for continent, keys in by_continent.items():
        out.append(f"""
{MOD_ID}_register_region_{continent}_list = {{
\tcmm_register_settings_list = {{
\t\tmod_id = {MOD_ID}
\t\tsetting_id = region_{continent}
\t\ttab_id = {TAB_ZONE}
\t\titem_count = {len(keys)}
\t\tis_ordered = 0
\t}}

""")
        for index, key in enumerate(keys, start=1):
            out.append(f"\tcmm_set_list_item_value = {{ mod_id = {MOD_ID} "
                       f"setting_id = region_{continent} item = {index} value = region:{key} }}\n")
        out.append("\n")
        for index, key in enumerate(keys, start=1):
            out.append(f"\tset_variable = {{ name = {MOD_ID}__region_{continent}_i{index}_name "
                       f"value = flag:{key} }}\n")
        out.append(f"""
\tcmm_register_list_bool_field = {{
\t\tmod_id = {MOD_ID}
\t\tsetting_id = region_{continent}
\t\tfield_id = pick
\t\tdefault_value = 0
\t}}
}}
""")

    out.append(f"\n# Scope: country\n{MOD_ID}_register_region_lists = {{\n")
    for continent in by_continent:
        out.append(f"\t{MOD_ID}_register_region_{continent}_list = yes\n")
    out.append("}\n")

    out.append(f"""
# The ticked regions, gathered beside the ticked continents. Both narrow the same
# search; a region is simply the finer of the two.
# Scope: country
{MOD_ID}_rebuild_regions = {{
\tclear_global_variable_list = {MOD_ID}_regions
\tset_global_variable = {{ name = {MOD_ID}_region_count value = 0 }}
""")
    for continent in by_continent:
        out.append(f"""\tif = {{
\t\tlimit = {{ has_variable_list = cmm_list_items_{MOD_ID}__region_{continent} }}
\t\tcmm_build_list_bool_list = {{ setting = {MOD_ID}__region_{continent} field_slot = 1 list_name = {MOD_ID}_region_{continent}_ticks }}
\t\tevery_in_list = {{
\t\t\tvariable = {MOD_ID}_region_{continent}_ticks
\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_regions target = this }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_region_count add = 1 }}
\t\t}}
\t}}
""")
    out.append("}\n")

    out.append(f"""
# Every land location of the ticked regions, for the ranking's fallback.
# Scope: country
{MOD_ID}_collect_regions = {{
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_regions
\t\tevery_location_in_region = {{
\t\t\tlimit = {{ {MOD_ID}_is_candidate = yes }}
\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_candidates target = this }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_candidate_count add = 1 }}
\t\t}}
\t}}
}}
""")
    return "".join(out)


def zone_file() -> str:
    """The zone: the continents to look inside, ticked.

    There is nothing to walk here. A location's continent is a plain trigger --
    `continent = continent:europe`, which vanilla uses seventy times -- so
    membership is asked at the moment it matters instead of being marked onto
    every location of a continent in advance. An earlier version did the walk,
    and ticking Europe would have meant setting a variable on some thousands of
    locations for nothing.
    """
    out = [HEADER, f"""#
# Scope: country
{MOD_ID}_register_zone_list = {{
\tcmm_register_settings_list = {{
\t\tmod_id = {MOD_ID}
\t\tsetting_id = continent
\t\ttab_id = {TAB_ZONE}
\t\titem_count = {len(CONTINENTS)}
\t\tis_ordered = 0
\t}}

"""]
    for index, key in enumerate(CONTINENTS, start=1):
        out.append(f"\tcmm_set_list_item_value = {{ mod_id = {MOD_ID} "
                   f"setting_id = continent item = {index} value = continent:{key} }}\n")
    out.append("\n")
    for index, key in enumerate(CONTINENTS, start=1):
        # The game's own key, so the row arrives named in the player's language
        # and nothing here carries a copy of it.
        out.append(f"\tset_variable = {{ name = {MOD_ID}__continent_i{index}_name "
                   f"value = flag:{key} }}\n")
    out.append(f"""
\tcmm_register_list_bool_field = {{
\t\tmod_id = {MOD_ID}
\t\tsetting_id = continent
\t\tfield_id = pick
\t\tdefault_value = 0
\t}}
}}

# Scope: country
{MOD_ID}_rebuild_zone = {{
\tclear_global_variable_list = {MOD_ID}_continents
\tset_global_variable = {{ name = {MOD_ID}_zone_count value = 0 }}

\tif = {{
\t\t# Registration may not have completed yet on the first pass.
\t\tlimit = {{ has_variable_list = cmm_list_items_{MOD_ID}__continent }}
\t\tcmm_build_list_bool_list = {{ setting = {MOD_ID}__continent field_slot = 1 list_name = {MOD_ID}_zone_ticks }}
\t\tevery_in_list = {{
\t\t\tvariable = {MOD_ID}_zone_ticks
\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_continents target = this }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_zone_count add = 1 }}
\t\t}}
\t}}
}}

# Every land location of the ticked continents, for when the player ranks a whole
# continent without narrowing it first.
# Scope: country
{MOD_ID}_collect_zone = {{
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_continents
\t\tevery_location_in_continent = {{
\t\t\tlimit = {{ {MOD_ID}_is_candidate = yes }}
\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_candidates target = this }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_candidate_count add = 1 }}
\t\t}}
\t}}
}}
""")
    return "".join(out)


def triggers_file(rows, split, game) -> str:
    out = [HEADER, f"""#
# Whether the map picker and the ranking offer this location at all.
#
# The ticked continents narrow it; with nothing ticked the whole world is on
# offer, because a picker that shows nothing until a checkbox somewhere else is
# set looks broken rather than empty. Ownership is deliberately never asked --
# the whole use is planning for ground that is not yours yet.
#
# Scope: location
{MOD_ID}_in_zone = {{
\tOR = {{
\t\tAND = {{
\t\t\tglobal_var:{MOD_ID}_zone_count = 0
\t\t\tglobal_var:{MOD_ID}_region_count = 0
\t\t}}
\t\tregion = {{ is_target_in_global_variable_list = {{ name = {MOD_ID}_regions target = this }} }}
"""]
    for key in CONTINENTS:
        out.append(f"""\t\tAND = {{
\t\t\tcontinent = continent:{key}
\t\t\tis_target_in_global_variable_list = {{ name = {MOD_ID}_continents target = continent:{key} }}
\t\t}}
""")
    out.append("\t}\n}\n")

    # "Only where it can be built today", per good. `can_build_building` is the
    # documented trigger and takes a literal building type, so the alternative --
    # walking `any_building_type` and asking what it produces -- would have needed
    # a trigger that does not exist.
    order = [good for kind in ("raw", "made") for good in split[kind]]
    by_good: dict[str, list[str]] = {}
    for method in rows:
        by_good.setdefault(method.produced, [])
        if method.building not in by_good[method.produced]:
            by_good[method.produced].append(method.building)

    out.append(f"""
# **`trigger_if`, not `if`.** A trigger has its own conditional: `if` is an
# effect and `else_if` is nothing at all, which the game says once per line at
# load -- `Unknown trigger type: else_if` -- and the whole of this then came
# back true, so "only where it can be built today" filtered nothing whatever it
# was set to, for as long as the tick has existed.
#
# Scope: location
{MOD_ID}_can_build_something = {{
""")
    first = True
    for index, right in enumerate(output_rights(rows, game), start=1):
        keyword = "trigger_if" if first else "trigger_else_if"
        first = False
        inner = " ".join(f"{MOD_ID}_can_build_{order.index(g) + 1} = yes"
                         for g in sorted(right.output) if g in order)
        out.append(f"\t{keyword} = {{ limit = {{ global_var:{MOD_ID}_right_index = {index} }} "
                   f"OR = {{ {inner} }} }}\n")
    for index, good in enumerate(order, start=1):
        keyword = "trigger_if" if first else "trigger_else_if"
        first = False
        out.append(f"\t{keyword} = {{ limit = {{ global_var:{MOD_ID}_good_index = {index} }} "
                   f"{MOD_ID}_can_build_{index} = yes }}\n")
    # **A `trigger_if` chain has to end in a `trigger_else`.** Without one the
    # game logs `PostValidate of trigger 'trigger_else_if' returned false` at the
    # last link and the whole trigger is void -- which is the twenty-third run's
    # one real line in `error.log`. Nothing ticked means nothing to build.
    out.append("\ttrigger_else = { always = no }\n")
    out.append("}\n")

    for index, good in enumerate(order, start=1):
        out.append(f"\n# {good}\n# Scope: location\n{MOD_ID}_can_build_{index} = {{\n\tOR = {{\n")
        for building in sorted(by_good.get(good, [])):
            out.append(f"\t\tcan_build_building = building_type:{building}\n")
        out.append("\t}\n}\n")

    # Which methods this country may actually run.
    #
    # 119 buildings in the game are unlocked by an advance with an age on it, and
    # ten production methods are unlocked separately, so `can_build_building` in
    # *country* scope -- "country checks the country scope requirements" -- is
    # what answers "is this available to me now". Without it the table happily
    # recommends a method three ages away, which is what the owner saw on beer.
    out.append("\n# Scope: country\n")
    for index, method in enumerate(rows, start=1):
        gate = UNLOCKS.get(method.key)
        extra = f"\n\thas_advance = {gate}" if gate else ""
        out.append(f"{MOD_ID}_avail_{index} = {{\n"
                   f"\tcan_build_building = building_type:{method.building}{extra}\n}}\n")

    return "".join(out)


def picker_file(split: dict[str, list[str]], rows: list[eu5data.Method]) -> str:
    """The good picker: two lists, and only one tick standing across both."""
    out = [HEADER, """#
# Two lists rather than a dropdown, and not by preference: CMF handles a dropdown
# option click through `CMM_MarkDropdownSelection_<index>` and defines exactly
# twenty of them, so the twenty-first option onwards renders, scrolls, and
# silently keeps the old selection.
#
# One answer across both lists. Ticking a second row anywhere leaves two ticks
# standing for the instant between the click and the callback; the tick that is
# not the stored answer wins and everything else is forced off, so the tick
# visibly moves to one row and stays there.
#
# The `root`s below are safe and are the only ones left in this mod: everything
# here is reached from a CMM callback, where `root` is the country. Nothing on
# this page is reachable from a generic action, which is where `root` is not --
# see the header of `{MOD_ID}_generated_score.txt`.
"""]

    order = [(kind, good) for kind in ("raw", "made") for good in split[kind]]
    index_of = {good: i for i, (_, good) in enumerate(order, start=1)}
    by_good_index: dict[str, list[int]] = {}
    for i, method in enumerate(rows, start=1):
        by_good_index.setdefault(method.produced, []).append(i)

    for kind in ("raw", "made"):
        goods = split[kind]
        out.append(f"""
# Scope: country
{MOD_ID}_register_good_{kind}_list = {{
\tcmm_register_settings_list = {{
\t\tmod_id = {MOD_ID}
\t\tsetting_id = good_{kind}
\t\ttab_id = {TAB_GOODS}
\t\titem_count = {len(goods)}
\t\tis_ordered = 0
\t}}

""")
        for row, good in enumerate(goods, start=1):
            out.append(f"\tcmm_set_list_item_value = {{ mod_id = {MOD_ID} "
                       f"setting_id = good_{kind} item = {row} value = goods:{good} }}\n")
        out.append("\n")
        for row, good in enumerate(goods, start=1):
            out.append(f"\tset_variable = {{ name = {MOD_ID}__good_{kind}_i{row}_name "
                       f"value = flag:{MOD_ID}_good_{good} }}\n")
        out.append(f"""
\tcmm_register_list_bool_field = {{
\t\tmod_id = {MOD_ID}
\t\tsetting_id = good_{kind}
\t\tfield_id = pick
\t\tdefault_value = 0
\t}}
}}
""")

    out.append(f"""
# Read both lists and settle on one good.
# Scope: country
{MOD_ID}_read_good = {{
\tset_variable = {{ name = {MOD_ID}_good_new value = 0 }}
\tset_variable = {{ name = {MOD_ID}_tick_count value = 0 }}
""")
    for kind in ("raw", "made"):
        out.append(f"""\tcmm_build_list_bool_list = {{ setting = {MOD_ID}__good_{kind} field_slot = 1 list_name = {MOD_ID}_good_{kind}_ticks }}
\tevery_in_list = {{
\t\tvariable = {MOD_ID}_good_{kind}_ticks
\t\troot = {{ change_variable = {{ name = {MOD_ID}_tick_count add = 1 }} }}
""")
        for good in split[kind]:
            index = index_of[good]
            out.append(f"\t\tif = {{ limit = {{ this = goods:{good} }} root = {{ "
                       f"if = {{ limit = {{ NOT = {{ var:{MOD_ID}_good_index = {index} }} }} "
                       f"set_variable = {{ name = {MOD_ID}_good_new value = {index} }} }} }} }}\n")
        out.append("\t}\n")
    out.append(f"""
\t# A tick that is not the stored answer is the new answer. Nothing new ticked
\t# means the player unticked the old one, and the answer goes with it.
\tif = {{
\t\tlimit = {{ var:{MOD_ID}_good_new > 0 }}
\t\tset_variable = {{ name = {MOD_ID}_good_index value = var:{MOD_ID}_good_new }}
\t}}
\telse_if = {{
\t\tlimit = {{ var:{MOD_ID}_tick_count = 0 }}
\t\tset_variable = {{ name = {MOD_ID}_good_index value = 0 }}
\t}}

\t# The same number as a global. `{MOD_ID}_can_build_something` is asked in a
\t# location's own scope, where a country variable is not reachable, and it was
\t# reading a global nothing ever wrote -- so every branch missed, the trigger
\t# came back true, and "only where it can be built today" filtered nothing.
\tset_global_variable = {{ name = {MOD_ID}_good_index value = var:{MOD_ID}_good_index }}

""")
    for good, index in ((g, index_of[g]) for _, g in order):
        keyword = "if" if index == 1 else "else_if"
        out.append(f"\t{keyword} = {{ limit = {{ var:{MOD_ID}_good_index = {index} }} "
                   f"set_global_variable = {{ name = {MOD_ID}_good value = goods:{good} }} }}\n")
    out.append("}\n")

    out.append(f"""
# Force every row but the answer off.
# Scope: country
{MOD_ID}_only_one_good = {{
""")
    for kind in ("raw", "made"):
        for row, good in enumerate(split[kind], start=1):
            out.append(f"""\tif = {{
\t\tlimit = {{ NOT = {{ var:{MOD_ID}_good_index = {index_of[good]} }} }}
\t\tcmm_set_list_data_value = {{ mod_id = {MOD_ID} setting_id = good_{kind} field_id = pick item = {row} value = 0 }}
\t}}
""")
    out.append("}\n")

    out.append(f"""
# Every good stays on the list, whatever age this country is in.
#
# Until the eighteenth run a good whose every recipe was still behind an advance
# was hidden here, and the owner went looking for cannons and firearms in the
# second age and found neither. Hiding was the right answer when a row could
# only say what you can build today; it is the wrong one now that a row also
# says what the ground gives at the end of the game, which is the same whatever
# age you are in -- and it was always the wrong one for a good another mod adds
# a building for.
#
# What is still not offered is a good no building makes at all: `goods_split`
# only ever lists what some method produces, so a pure RGO material is absent
# because there is nothing to choose, not because it is hidden.
# Scope: country
{MOD_ID}_refresh_goods = {{
""")
    for kind in ("raw", "made"):
        for row, _ in enumerate(split[kind], start=1):
            out.append(f"\tcmm_show_list_item = {{ mod_id = {MOD_ID} setting_id = good_{kind} item = {row} }}\n")
    out.append("}\n")
    return "".join(out)


def values_file(rows: list[eu5data.Method], split: dict[str, list[str]],
                game: eu5data.Game) -> str:
    """Two script values per method: what it would be worth here, and the bonus.

    **What it is worth is what it produces, not what percentage it gains.** The
    eighth run put a forest village at the top of a weaponry search: one raw
    input, a full 10%, and 0.2 goods a level against a weapon guild's 1.0. The
    bonus is production efficiency, so it multiplies output rather than standing
    in for it:

        effective output = output * (1 + bonus / 100)
        RGO bonus %      = {max:g} * (input amounts the province supplies) / (all inputs)

    Both divisions are done here, at generation time, so a location costs one
    addition per raw material the method wants.

    The province, not the location: the game credits a raw material worked
    anywhere in it -- and the whole province definition, both sides of any border
    that currently cuts it, because that is the ground once it is yours. Every
    input counts towards the denominator, produced goods included: an RGO can
    never supply tools, but tools still carry their weight, which is why a method
    can top out well below {max:g}%.
    """
    out = [HEADER, f"""#
# `{MOD_ID}_m<n>` ranks -- effective output. `{MOD_ID}_b<n>` is the bonus the row
# prints. Nothing reads `_b` until a method has won a row, so it costs nothing
# per candidate.
#
# **`_m` is the output times {RANK_SCALE}, and that is what makes it sortable.** In its own
# units a scriptorium runs from 0.3000 to 0.3129 across the whole of Europe, and
# ranking on that came back in map order: every `order_by` in the game and in
# every mod in `reference/` sorts on numbers in the thousands -- vanilla on
# `military_strength` and `country_tax_base`, Advanced Auto Build on a score
# built out of `add = 12000` -- and none on a fraction. Scaled, the same
# scriptorium runs 300.00 to 312.88 and the provinces separate. Nothing prints
# `_m`: the row's `×` is the method's own output, written out unscaled by
# `{MOD_ID}_store_winner`.
""".format(max=eu5data.RGO_MAX_BONUS)]
    for index, method in enumerate(rows, start=1):
        ceiling = method.ceiling(game.raw_goods)
        # What one raw material is worth here, in bonus points. For a building
        # that runs two methods at once this is already blended across the two
        # -- see `eu5data.Method.shares`.
        shares = {good: share for good, share in method.shares().items()
                  if good in game.raw_goods}
        out.append(f"\n# {method.building} / {method.key} -> {method.produced}, "
                   f"output {method.output:g}, ceiling {ceiling:.2f}% "
                   f"-> at best {method.output * (1 + ceiling / 100):.4f}\n")
        out.append(f"# Scope: location\n{MOD_ID}_m{index} = {{\n"
                   f"\tvalue = {method.output * RANK_SCALE:.4f}\n")
        for good, share in sorted(shares.items()):
            out.append(f"""\tif = {{
\t\tlimit = {{ province_definition = {{ any_location_in_province_definition = {{ raw_material = goods:{good} }} }} }}
\t\tadd = {method.output * RANK_SCALE * share / 100:.4f}
\t}}
""")
        out.append("}\n")
        out.append(f"# Scope: location\n{MOD_ID}_b{index} = {{\n\tvalue = 0\n")
        for good, share in sorted(shares.items()):
            out.append(f"""\tif = {{
\t\tlimit = {{ province_definition = {{ any_location_in_province_definition = {{ raw_material = goods:{good} }} }} }}
\t\tadd = {share:.4f}
\t}}
""")
        out.append("}\n")
        # **What the plan deals the ground by**: how much of the bonus this
        # recipe could ever earn, it earns here. A raw bonus does not compare
        # across goods -- the ceilings run from 2% to 10% and five goods are
        # capped under five -- and a `worth` normalized to the good's own best on
        # this ground compares even worse, squeezing everything into 0.909-1.000.
        # The fraction of a recipe's own ceiling is the one currency that is the
        # same question for every good: `docs/investigations/plan_formula.md`.
        if ceiling > 0:
            out.append(f"# Scope: location\n{MOD_ID}_g{index} = {{\n\tvalue = 0\n")
            for good, share in sorted(shares.items()):
                out.append(f"""\tif = {{
\t\tlimit = {{ province_definition = {{ any_location_in_province_definition = {{ raw_material = goods:{good} }} }} }}
\t\tadd = {share * RANK_SCALE / ceiling:.4f}
\t}}
""")
            out.append("}\n")
        else:
            out.append(f"# A recipe no RGO can feed: its gain is nought everywhere.\n"
                       f"# Scope: location\n{MOD_ID}_g{index} = {{ value = 0 }}\n")

    # The plan's orderings. `order_by` takes a script value and never a variable,
    # so "what is this ground worth to this good" needs a name of its own -- one
    # per good per side, plus a third that is the better of the two, which is
    # what the good is normalized by. `bag_wtp_generated_plan.txt` fills the
    # variables behind them.
    order = [g for kind in ("raw", "made") for g in split[kind]]
    plan_values = []
    for index, good in enumerate(order, start=1):
        plan_values.append(f"""
# {good}. **Divided by how much of it this province already has**, which is the
# whole of what keeps a province's locations from coming out identical: every
# location of a province is worth exactly the same to a good -- the bonus is a
# `province_definition`'s property -- so undivided, a good takes all of its best
# province before it looks at its second. And nothing is ever twice as good: the
# bonus is a ten per cent band (`docs/investigations/plan_formula.md`), so
# halving is decisive. `_pp<n>` is that count, kept on every location of the
# province so the ordering can read it without leaving the location's scope.
# The divisor is written inline rather than as a value of its own: a `divide`
# with a `value`/`min` block inside is the shape vanilla uses (`byz_values.txt`),
# and `divide = <a named script value>` bare has no precedent in the game.
# Scope: location
{MOD_ID}_ord{index} = {{
\tvalue = var:{MOD_ID}_p{index}
\tdivide = {{
\t\tvalue = 1
\t\tadd = var:{MOD_ID}_pp{index}
\t\tmin = 1
\t}}
}}
# Scope: location
{MOD_ID}_ordr{index} = {{
\tvalue = var:{MOD_ID}_pr{index}
\tdivide = {{
\t\tvalue = 1
\t\tadd = var:{MOD_ID}_pp{index}
\t\tmin = 1
\t}}
}}
# The undecayed pair, which is what the good is normalized by and what counts
# its candidates: the divisor is about where the next building goes, never about
# whether this ground can hold the good at all.
# Scope: location
{MOD_ID}_ordmax{index} = {{
\tvalue = var:{MOD_ID}_p{index}
\tif = {{
\t\tlimit = {{ var:{MOD_ID}_pr{index} > var:{MOD_ID}_p{index} }}
\t\tvalue = var:{MOD_ID}_pr{index}
\t}}
}}
""")

    # What a whole urban right is worth on this ground: its bundle's own
    # normalized scores added up. It costs no pass of its own -- every good in
    # the bundle was scored anyway -- and the right's own percentage is left out
    # on purpose, because it is the same everywhere and reorders nothing.
    for k, right in enumerate(output_rights(rows, game), start=1):
        bundle = sorted(right.output)
        def _reach(good: str) -> str:
            """Can this bundle good put something in a town — itself, or the
            input that would let it? The substitution below fills the slot
            either way, so the right must be scored as if it counts."""
            i = order.index(good) + 1
            feeder = market_inputs(game).get(good)
            j = order.index(feeder) + 1 if feeder in order else 0
            if j and plan_groups(rows, split, game).get((feeder, "t")):
                return (f"OR = {{ {MOD_ID}_plan_can_town_{i} = yes "
                        f"{MOD_ID}_plan_can_town_{j} = yes }}")
            return f"{MOD_ID}_plan_can_town_{i} = yes"

        adds = "".join(f"""\tif = {{
\t\tlimit = {{ {_reach(g)} }}
\t\tadd = {RIGHT_FIT}
\t\tadd = var:{MOD_ID}_p{order.index(g) + 1}
\t}}
""" for g in bundle)
        plan_values.append(f"""
# {right.key}: {", ".join(bundle)}.
#
# **What a town can actually finish, first; how good it would be, second.**
# A bundle good this town cannot build adds nothing at all, and the total is
# divided by the bundle's size, so the number is "how much of this right would
# really go up here" and only then "how well". The thirty-seventh run is why:
# forty-eight towns of Westphalia all took the masonry and glass charter, and not
# one of them got glass. That is the game's answer, not the plan's -- at the
# start the only unlocked glass building is the guild and it wants sand in the
# local market -- but handing out a bundle that cannot be finished, forty-eight
# times, was the plan's. Six other charters are wholly age-0 buildable.
#
# **Then divided by how often this right has already been granted**, the same
# shape as a good's province divisor and for the same reason: every town of a
# province scores identically, so undivided they all take the one right. A right
# that is genuinely better still wins; a tie spreads.
# Scope: location
{MOD_ID}_rq{k} = {{
\tvalue = 0
{adds}\tdivide = {len(bundle)}
\tdivide = {{
\t\tvalue = 1
\t\tadd = global_var:{MOD_ID}_rgiven{k}
\t\tmin = 1
\t}}
}}
""")
    plan_values = "".join(plan_values)

    out.append(f"""
# The better of the two sides -- built-up and village -- in each of the three
# ages a row carries. A province with nothing but a village to offer still
# deserves its row.
# Scope: location
{MOD_ID}_near_score = {{
\tvalue = 0
\tif = {{
\t\tlimit = {{ var:{MOD_ID}_best >= var:{MOD_ID}_best_rural }}
\t\tvalue = var:{MOD_ID}_best
\t}}
\tif = {{
\t\tlimit = {{ var:{MOD_ID}_best < var:{MOD_ID}_best_rural }}
\t\tvalue = var:{MOD_ID}_best_rural
\t}}
}}

# Scope: location
{MOD_ID}_mid_score = {{
\tvalue = 0
\tif = {{
\t\tlimit = {{ var:{MOD_ID}_mid_best >= var:{MOD_ID}_mid_best_rural }}
\t\tvalue = var:{MOD_ID}_mid_best
\t}}
\tif = {{
\t\tlimit = {{ var:{MOD_ID}_mid_best < var:{MOD_ID}_mid_best_rural }}
\t\tvalue = var:{MOD_ID}_mid_best_rural
\t}}
}}

# Scope: location
{MOD_ID}_end_score = {{
\tvalue = 0
\tif = {{
\t\tlimit = {{ var:{MOD_ID}_end_best >= var:{MOD_ID}_end_best_rural }}
\t\tvalue = var:{MOD_ID}_end_best
\t}}
\tif = {{
\t\tlimit = {{ var:{MOD_ID}_end_best < var:{MOD_ID}_end_best_rural }}
\t\tvalue = var:{MOD_ID}_end_best_rural
\t}}
}}

# **A column shrunk until it can only break a tie in the column above it.**
# Ranking by the last age puts every province that reaches the same endgame
# percentage on one number -- and where fine cloth ends in silk, that number is
# 0.00% for the whole table. What separates them then is the road there: ten
# percent until the fifth age beats nothing at all, and that is the choice the
# twentieth run asked to be able to make.
#
# A ten-thousandth of a score is at most 0.495 and the smallest step any raw
# material makes in the endgame set is 1.9, so this orders ties and can never
# reorder anything that is not tied.
# Scope: location
{MOD_ID}_mid_tiebreak = {{
\tvalue = {MOD_ID}_mid_score
\tmultiply = 0.0001
}}

# What the ranking sorts on. Two orders, one per «Считать» button: what you
# could build today, or what the ground gives at the end -- and where the end
# cannot tell two provinces apart, which it cannot whenever a ladder runs out
# (0.00% in every wool province for fine cloth), the road there decides.
#
# One operation per branch, because a script value that quietly does nothing
# logs nothing.
# Scope: location
{MOD_ID}_score = {{
\tvalue = 0
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_rank_by_end }} }}
\t\tvalue = {MOD_ID}_near_score
\t}}
\tif = {{
\t\tlimit = {{ has_global_variable = {MOD_ID}_rank_by_end }}
\t\tvalue = {MOD_ID}_end_score
\t}}
\tif = {{
\t\tlimit = {{ has_global_variable = {MOD_ID}_rank_by_end }}
\t\tadd = {MOD_ID}_mid_tiebreak
\t}}
}}

# The place the ranking gave this location, turned upside down, because
# `ordered_in_global_list` sorts **highest first** and rank 1 has to come out
# first. Ranking a list and then copying it with `every_in_global_list` is what
# lost the order once already: an unordered iterator promises nothing about the
# order it hands things back in, and the window draws its rows in the order the
# list holds them.
# Scope: location
{MOD_ID}_rank_order = {{
\tvalue = 0
\tsubtract = var:{MOD_ID}_rank
}}

# What the rights pass ranks on: every good of the bundle, each at its best
# method here, added through its price. Already scaled -- `_best` is.
#
# «На конец» adds the road there, shrunk until it can only break a tie -- and
# the tie it breaks is the whole table at once, because where no surviving
# recipe can be fed every province is worth exactly zero. A hundred-thousandth
# of a bundle's total is at most 0.065 and the smallest step a bundle's own
# total takes is about 0.6.
# Scope: location
{MOD_ID}_r_mid_tiebreak = {{
\tvalue = var:{MOD_ID}_r_mid_total
\tmultiply = 0.00001
}}

# Scope: location
{MOD_ID}_r_score = {{
\tvalue = var:{MOD_ID}_r_total
\tif = {{
\t\tlimit = {{ has_global_variable = {MOD_ID}_rank_by_end }}
\t\tadd = {MOD_ID}_r_mid_tiebreak
\t}}
}}

{plan_values}
# The same, for the quota: how many goods this ground can make at all. Divided by
# only under a `limit` that it is above zero, so the guard is the caller's.
{MOD_ID}_plan_scored_value = {{ value = global_var:{MOD_ID}_plan_scored }}

# How the plan's provinces are ordered: by how much of it landed in each, read
# off the one location that stands in for the province. Under the province model
# every province fills to its capacity, so this is size and contention together
# -- the «магнит» the feature is named for.
# Scope: location
{MOD_ID}_plan_prov_order = {{ value = var:{MOD_ID}_plan_prov_load }}

# And how a location's row is ordered: by its province's place, so a province's
# locations stay together, with its towns ahead of its villages. Negated because
# `ordered_in_global_list` sorts highest first and place 1 has to come out first.
#
# **Small numbers on purpose.** Packing the province's load and its place into
# one figure would run to five digits, and where the engine's fixed point ends is
# not knowable from here -- `RIGHT_SCALE` is in the generator for the same
# reason.
# Scope: location
{MOD_ID}_plan_order = {{
\tvalue = 0
\tsubtract = var:{MOD_ID}_plan_prank
\tif = {{
\t\tlimit = {{ {MOD_ID}_plan_is_town = yes }}
\t\tadd = 0.5
\t}}
}}

# And the copy into the window's datamodel keeps that order the way the
# ranking's does: highest first, so the rank is negated.
# Scope: location
{MOD_ID}_plan_rank_order = {{
\tvalue = 0
\tsubtract = var:{MOD_ID}_plan_rank
}}

{MOD_ID}_show_regions = {{ value = global_var:{MOD_ID}_zone_count }}
{MOD_ID}_show_candidates = {{ value = global_var:{MOD_ID}_candidate_count }}
{MOD_ID}_show_found = {{ value = global_var:{MOD_ID}_found }}
{MOD_ID}_show_picked = {{ value = global_var:{MOD_ID}_picked_count }}
{MOD_ID}_show_browse = {{ value = global_var:{MOD_ID}_browse_count }}
{MOD_ID}_show_live = {{ value = global_var:{MOD_ID}_live_runs }}

# Что показать на самой кнопке «Диагностика». Она пишет в лог, а лог не на
# экране: без этих пяти чисел нажатие ничем не отличается от кнопки, которая
# не работает.
{MOD_ID}_show_diag_runs = {{ value = global_var:{MOD_ID}_diag_runs }}
{MOD_ID}_show_diag_locs = {{ value = global_var:{MOD_ID}_diag_locs }}
{MOD_ID}_show_diag_towns = {{ value = global_var:{MOD_ID}_diag_towns }}
{MOD_ID}_show_diag_freet = {{ value = global_var:{MOD_ID}_diag_freet }}
{MOD_ID}_show_diag_freer = {{ value = global_var:{MOD_ID}_diag_freer }}

# The diagnosis reads through these sixteen and nothing else. **`value =
# global_var:x` and no guard inside the value**: the self-guarding form, `value =
# 0` with an `if` adding the global, returned zero for every reader on a plan
# that had just placed 417 buildings, and said nothing in any log. The guard is
# an `if` in the effect that fills the scratch global instead.
""" + "".join(f"{MOD_ID}_dg{i} = {{ value = global_var:{MOD_ID}_dv{i} }}\n"
               for i in range(1, DIAG_SCRATCH + 1)) + f"""

# What the plan pass counted, each of them printed on the button that ran it.
# The first zero among them is the diagnosis, which is the only debugging a
# player can be asked for: an effect that merely does nothing logs nothing.
{MOD_ID}_show_plan_scored = {{ value = global_var:{MOD_ID}_plan_scored }}
{MOD_ID}_show_plan_placed = {{ value = global_var:{MOD_ID}_plan_placed }}
{MOD_ID}_show_plan_found = {{ value = global_var:{MOD_ID}_plan_found }}
{MOD_ID}_show_plan_shown = {{ value = global_var:{MOD_ID}_plan_shown }}
{MOD_ID}_show_plan_rooms = {{ value = global_var:{MOD_ID}_plan_rooms }}
{MOD_ID}_show_plan_cap_rural = {{ value = global_var:{MOD_ID}_plan_cap_rural }}
{MOD_ID}_show_plan_cap_urban = {{ value = global_var:{MOD_ID}_plan_cap_urban }}
{MOD_ID}_show_plan_max = {{ value = global_var:{MOD_ID}_plan_max }}
# The fair share the quota came out at, on the header line: with the room count
# and the goods count beside it, it is the whole of `plan_quota` readable at a
# glance, and a quota of 1 says the ground is the binding constraint.
{MOD_ID}_show_plan_quota = {{ value = global_var:{MOD_ID}_plan_quota }}
{MOD_ID}_show_plan_sweeps = {{ value = global_var:{MOD_ID}_plan_sweeps }}
{MOD_ID}_show_plan_towns = {{ value = global_var:{MOD_ID}_plan_towns }}
{MOD_ID}_show_plan_provn = {{ value = global_var:{MOD_ID}_plan_provn }}
{MOD_ID}_show_plan_rightn = {{ value = global_var:{MOD_ID}_plan_rightn }}
""")
    return "".join(out)


def score_file(rows: list[eu5data.Method], split: dict[str, list[str]],
               game: eu5data.Game) -> str:
    """Finding the method, which is the thing the player should not have to do.

    **Two axes, and a row carries both.** Across one: the best village and the
    best of everything else, scored apart because a village produces a fifth of
    what a guild does and buried the guilds when they shared a list. Across the
    other, three ages of the same question:

    | prefix | column | the best method that is |
    | --- | --- | --- |
    | none | «Сейчас» | unlocked for this country today |
    | `mid_` | «По пути» | unlocked in *any* age -- and until which age it lasts |
    | `end_` | «В конце» | still buildable once every advance is in |

    The third column is what makes this a planning tool rather than a table.
    Fine cloth from wool has no rung above the workshop, so «В конце» is 0.00%
    in every wool province and choosing between them needs the other number:
    ten percent, until the fifth age. **Rank by the end, break the ties by the
    road there** -- which is what the twentieth run asked for in as many words.

    **A method the ground cannot feed is not an answer**, so every one of the
    three keeps only methods this province supplies the bulk of the raw materials
    for -- asked as `_try > <a literal>`, the literal being `fed_floor`. Each
    also keeps an `_any_` twin without that floor, which nothing ranks on: a
    column has to print something, and "the mill you cannot feed, at 0.00%" is an
    answer where a blank cell is not.

    All of it in one walk: a method's `_m<n>` is computed once and offered to
    every answer it qualifies for.
    """
    order = [good for kind in ("raw", "made") for good in split[kind]]
    by_good: dict[str, list[int]] = {}
    for index, method in enumerate(rows, start=1):
        by_good.setdefault(method.produced, []).append(index)
    rural = {index for index, method in enumerate(rows, start=1)
             if method.building_category in RURAL_CATEGORIES}
    last = endgame(rows, game)

    # Every answer a candidate carries, and what it is allowed to keep.
    ANSWERS = ("", "any_", "mid_", "end_", "end_any_")

    # And the plan's own four, which are a different question from all of them.
    #
    # **The plan splits by where a building may stand, not by what category it
    # is in.** The ranking's «village» side is `village_category` -- four
    # buildings -- and the owner's twenty-ninth screenshot is what that costs: a
    # rural province offered tools, jewelry and beer, all three of them
    # `market_village`, where a stone quarry, a clay pit and a lumber mill would
    # have been the honest answer. Thirty production buildings declare
    # `rural_settlement = yes` and only four are villages, so the plan asks the
    # building type itself (`eu5data.Method.rural` / `.urban`).
    PLAN_SIDES = (("_t", "urban"), ("_r", "rural"))

    def keep(indent: str, prefix: str, suffix: str, method_index: int,
             floor: float | None, extra: str = "", plan: bool = False) -> str:
        """Is this the best of its side so far, and can this ground feed it?

        `floor` is `fed_floor`: the `_m<n>` of a method the province supplies
        exactly half the possible bonus of. Anything above it is a recipe this
        ground supplies the bulk of.

        Without any floor the eighteenth run's fine cloth answered with silk
        weavers at 0.00% in provinces full of wool: 0.70 a level unfed beats 0.50
        a level at the full ten percent, so the ranking preferred a recipe the
        ground cannot supply and buried every province that could have run the
        other one. With a floor at the unbonused output it did the same thing
        again on one input out of three -- the twenty-fifth run, and why the
        floor is where it is now.
        """
        fed = f"var:{MOD_ID}_try > {floor:.4f} " if floor is not None else ""
        # **The method is chosen by worth and the placement is dealt by gain**,
        # and the two are different questions. Within one good a mill at 5% beats
        # a guild at 10%, so `_try` decides which recipe wins here. Across goods
        # what compares is the fraction of its own ceiling that recipe earns, so
        # the winner's `_g<n>` is kept beside it for the plan to deal by.
        gain = ("" if not plan else
                f"{indent}\tset_variable = {{ name = {MOD_ID}_{prefix}gain{suffix} "
                f"value = {MOD_ID}_g{method_index} }}\n")
        return (f"""{indent}if = {{
{indent}\tlimit = {{ {fed}var:{MOD_ID}_try > var:{MOD_ID}_{prefix}best{suffix}{extra} }}
{indent}\tset_variable = {{ name = {MOD_ID}_{prefix}best{suffix} value = var:{MOD_ID}_try }}
{indent}\tset_variable = {{ name = {MOD_ID}_{prefix}best_method{suffix} value = {method_index} }}
{gain}{indent}}}
""")

    out = [HEADER, f"""#
# **The country is saved, not reached for.** Every method's availability is a
# country trigger asked from inside a walk over locations, and it used to get
# there with `root`. From a Mod Menu button `root` is the country; from a map
# picker's generic action it is not, so the eleventh run's pass walked its
# 44 locations, found no method available in any of them -- «нашёл 0» -- and the
# window emptied itself the moment a border was drawn.
#
# Scope: country
{MOD_ID}_score_candidates = {{
\tsave_scope_as = {MOD_ID}_country
"""]
    for index, good in enumerate(order, start=1):
        keyword = "if" if index == 1 else "else_if"
        out.append(f"\t{keyword} = {{ limit = {{ var:{MOD_ID}_good_index = {index} }} "
                   f"{MOD_ID}_score_{index} = yes }}\n")
    out.append("}\n")

    for index, good in enumerate(order, start=1):
        methods_for = by_good.get(good, [])
        village = [i for i in methods_for if i in rural]
        out.append(f"\n# {good}, made {len(methods_for)} way(s), "
                   f"{len(village)} of them in a village.\n"
                   f"# Scope: country\n{MOD_ID}_score_{index} = {{\n")
        out.append(f"\tevery_in_global_list = {{\n\t\tvariable = {MOD_ID}_candidates\n")
        for prefix in ANSWERS:
            for suffix in ("", "_rural"):
                out.append(f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}best{suffix} value = 0 }}\n")
                out.append(f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}best_method{suffix} value = 0 }}\n")
        for prefix in ("pnow", "pend", "pnowany", "pendany"):
            for side, _ in PLAN_SIDES:
                out.append(f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}best{side} value = 0 }}\n")
                out.append(f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}best_method{side} value = 0 }}\n")
                out.append(f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}gain{side} value = 0 }}\n")

        for method_index in methods_for:
            suffix = "_rural" if method_index in rural else ""
            floor = fed_floor(rows[method_index - 1], game)
            out.append(f"\t\tset_variable = {{ name = {MOD_ID}_try value = {MOD_ID}_m{method_index} }}\n")
            # **Can this building stand here at all.** The ranking asked this of
            # nothing until the thirty-second load, and the owner caught it in as
            # many words: a stone quarry offered on ground that is flat all
            # through, because the province works wood. `can_build_building` in
            # the location's own scope is the terrain, the rank and the
            # building's `location_potential`, and never an advance -- so it is
            # as safe on «В конце» as on «Сейчас», and on ground nobody owns.
            stands = (f" can_build_building = building_type:"
                      f"{rows[method_index - 1].building}")
            # «По пути»: every age, so no gate on availability -- but the ground
            # still has to be able to hold it.
            out.append(keep("\t\t", "mid_", suffix, method_index, floor, stands))
            if method_index in last:
                out.append(keep("\t\t", "end_", suffix, method_index, floor, stands))
                out.append(keep("\t\t", "end_any_", suffix, method_index, None, stands))
            # The plan's endgame side needs no availability: it is what stands
            # once every advance is in.
            # **The plan keeps an unfloored twin of each side and the ranking
            # does not.** `fed_floor` is right for an answer to «where should I
            # make wine» and wrong for «fill this ground»: the owner settled it
            # on 2026-09-01 -- «бонус от рго это приоритет, а не железное
            # правило, без которого в локации домика существовать не может».
            # A location no RGO helps still has to be filled, and a right's
            # bundle goes up whether the ground feeds it or not.
            #
            # The floored answer is still what wins wherever there is one, so
            # the twenty-fifth run's silk weaver in a wool province stays
            # buried: the twin is a fallback, never a rival.
            for side, where in PLAN_SIDES:
                if getattr(rows[method_index - 1], where) and method_index in last:
                    out.append(keep("\t\t", "pend", side, method_index, floor, stands, plan=True))
                    out.append(keep("\t\t", "pendany", side, method_index, None, stands, plan=True))
            out.append(f"""\t\tif = {{
\t\t\tlimit = {{ scope:{MOD_ID}_country = {{ {MOD_ID}_avail_{method_index} = yes }} }}
""")
            out.append(keep("\t\t\t", "", suffix, method_index, floor, stands))
            out.append(keep("\t\t\t", "any_", suffix, method_index, None, stands))
            for side, where in PLAN_SIDES:
                if getattr(rows[method_index - 1], where):
                    out.append(keep("\t\t\t", "pnow", side, method_index, floor, stands, plan=True))
                    out.append(keep("\t\t\t", "pnowany", side, method_index, None, stands, plan=True))
            out.append("\t\t}\n")
        out.append("\t}\n}\n")

    def park(prefix: str, index: int, method: eu5data.Method, suffix: str) -> str:
        """One winner, written onto the location the window reads its row off.

        Each column keys on its own `_show`, which is the fed answer where the
        ground feeds one and the unfed one otherwise. `«По пути»` carries an age
        instead of a goods list: it is a number and a deadline, and the icons
        beside it would be the same icons twice.
        """
        raw = sorted(method.raw_inputs(game.raw_goods))
        # `_pm2` is the improvement half, and only eight buildings have one. The
        # key of a pair is "base+improvement" and names no production method the
        # game knows, so each half is written on its own.
        improvement = (f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}pm2{suffix} "
                       f"value = production_method:{method.parts[1].key} }}\n"
                       if len(method.parts) > 1 else "")
        body = [f"\tif = {{\n"
                f"\t\tlimit = {{ var:{MOD_ID}_{prefix}show{suffix} = {index} }}\n"
                f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}bt{suffix} value = building_type:{method.building} }}\n"
                f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}pm{suffix} value = production_method:{method.parts[0].key} }}\n"
                + improvement
                + f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}bonus{suffix} value = {MOD_ID}_b{index} }}\n"
                f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}out{suffix} value = {method.output:.4f} }}\n"]
        if prefix == "mid_":
            body.append(f"\t\tset_variable = {{ name = {MOD_ID}_mid_age{suffix} value = {game.last_age(method)} }}\n")
        else:
            body.append(f"\t\tset_variable = {{ name = {MOD_ID}_{prefix}goods_all{suffix} value = {len(raw)} }}\n")
            for good in raw:
                body.append(f"""\t\tif = {{
\t\t\tlimit = {{ province_definition = {{ any_location_in_province_definition = {{ raw_material = goods:{good} }} }} }}
\t\t\tadd_to_variable_list = {{ name = {MOD_ID}_{prefix}goods{suffix} target = goods:{good} }}
\t\t}}
""")
        body.append("\t}\n")
        return "".join(body)

    # column prefix -> (what it is, the fed answer, the unfed fallback, which
    # methods can appear in it)
    COLUMNS = (
        ("", "what you could build today", "best_method", "any_best_method", None),
        ("mid_", "the best this ground ever feeds, and until when", "mid_best_method", None, None),
        ("end_", "what stands once every advance is in", "end_best_method", "end_any_best_method", last),
    )
    for prefix, what, fed, unfed, only in COLUMNS:
        for suffix in ("", "_rural"):
            age = (f"\tset_variable = {{ name = {MOD_ID}_mid_age{suffix} value = 0 }}\n"
                   if prefix == "mid_" else "")
            fallback = (f"""\tif = {{
\t\tlimit = {{ var:{MOD_ID}_{prefix}show{suffix} = 0 }}
\t\tset_variable = {{ name = {MOD_ID}_{prefix}show{suffix} value = var:{MOD_ID}_{unfed}{suffix} }}
\t}}
""" if unfed else "")
            out.append(f"""
# {what.capitalize()}, on the {"village" if suffix else "built-up"} side.
# Scope: location
{MOD_ID}_store_winner_{prefix or "now_"}{suffix.lstrip("_") or "town"} = {{
\tset_variable = {{ name = {MOD_ID}_{prefix}show{suffix} value = var:{MOD_ID}_{fed}{suffix} }}
{fallback}\tclear_variable_list = {MOD_ID}_{prefix}goods{suffix}
\tremove_variable = {MOD_ID}_{prefix}bt{suffix}
\tremove_variable = {MOD_ID}_{prefix}pm{suffix}
\tremove_variable = {MOD_ID}_{prefix}pm2{suffix}
\t# Zeroed rather than left: nothing sets these where no method won at all, the
\t# window guards only on `_bt`, and a number left over from the last run is
\t# invisible there and wrong to everything that reads it.
\tset_variable = {{ name = {MOD_ID}_{prefix}bonus{suffix} value = 0 }}
\tset_variable = {{ name = {MOD_ID}_{prefix}out{suffix} value = 0 }}
\tset_variable = {{ name = {MOD_ID}_{prefix}goods_all{suffix} value = 0 }}
{age}""")
            for index, method in enumerate(rows, start=1):
                if (index in rural) != bool(suffix):
                    continue
                if only is not None and index not in only:
                    continue
                out.append(park(prefix, index, method, suffix))
            out.append("}\n")
    return "".join(out)


def market_inputs(game: eu5data.Game) -> dict[str, str]:
    """Good -> the good its buildings need *in the market* before they may stand.

    Read off `location_potential`, where four buildings in the game carry an
    `is_produced_in_(location_)market = goods:X`. Only a good whose buildings all
    carry one is listed, and never one that asks for itself: `horse_breeders`
    wants horses in the market to make horses, which nothing can bootstrap.

    **This exists because a right's bundle is mandatory and the ground can still
    refuse it.** Glass is the case, and the owner's rule, 2026-09-01: «стекло
    делать в любом случае НАДО и отказаться от него нельзя из-за отсутствия
    песка, ведь у него нет альтернативного варианта как у тонкого сукна». Sand is
    dug by a `sand_pit`, which stands at any rank and asks only that the location
    is not already a sand RGO — so where a granted right cannot have its glass,
    the plan puts the pit that makes glass possible instead.
    """
    directory = refs.GAME_COMMON / "building_types"
    text = "".join(path.read_text(encoding="utf-8-sig", errors="replace")
                   for path in sorted(directory.glob("*.txt")))
    gated: dict[str, set[str]] = {}
    for block in re.split(r"\n(?=[a-z_0-9]+ = \{)", text):
        match = re.match(r"([a-z_0-9]+) = \{", block)
        if not match or "location_potential" not in block:
            continue
        needs = set(re.findall(
            r"is_produced_in(?:_location)?_market = goods:(\w+)",
            block.split("location_potential", 1)[1][:250]))
        if needs:
            gated[match.group(1)] = needs
    out: dict[str, str] = {}
    for good in game.goods_produced:
        makers = {m.building for m in game.methods
                  if m.produced == good and m.raw_inputs(game.raw_goods)} & set(gated)
        if not makers:
            continue
        # **Any of its buildings, not all of them.** Whether the ungated ones are
        # reachable is an availability question and the runtime already answers
        # it: `_plan_can_town_<n>` is asked with the age's own methods, so the
        # substitution below only ever fires where the good really cannot stand.
        needs = set().union(*(gated[b] for b in makers)) - {good}
        if len(needs) == 1:
            out[good] = needs.pop()
    return out


def plan_groups(rows, split, game):
    """Per good and side, the buildings that could win it and by which methods.

    **The plan's unit is a building in a location.** One location holds one
    building of a type and a building runs one method, so two goods off the same
    building cannot both be built there. But **two locations of one province
    can each hold that building running a different method** -- a market village
    makes tools, jewelry, beer and pottery, and four villages of a province may
    take one each. That is why the rule is per location and not per province.

    Returns `{(good, side): {building: [method index, ...]}}`, side being "t" for
    what may stand in a town and "r" for a rural settlement. A method appears on
    both sides where its building declares both.
    """
    order = [good for kind in ("raw", "made") for good in split[kind]]
    groups: dict[tuple[str, str], dict[str, list[int]]] = {}
    for index, method in enumerate(rows, start=1):
        if method.produced not in order:
            continue
        for side, allowed in (("t", method.urban), ("r", method.rural)):
            if allowed:
                groups.setdefault((method.produced, side), {}) \
                      .setdefault(method.building, []).append(index)
    return groups


def plan_triggers_file(rows: list[eu5data.Method], split: dict[str, list[str]],
                       game: eu5data.Game) -> str:
    """Whether this location may still take this good on this side.

    One trigger per good per side, asked twice: as the `limit` of the ordered
    walk that picks the location, and again inside the effect that adds it, so
    that the urban-rights round can call the effect without repeating a word.

    Every condition is a plain read off the location in hand. The last of them is
    the building rule: a good whose winning building is already standing here is
    not an answer -- it would be a second one of that building, which the game
    does not offer. Which building would win is `_pm<n>` / `_prm<n>`, the method
    the harvest kept.
    """
    order = [good for kind in ("raw", "made") for good in split[kind]]
    groups = plan_groups(rows, split, game)
    out = [HEADER, f"""#
# **Written with OR and AND and never an `if`.** A scripted trigger takes an
# effect's `if` without complaining and answers true everywhere afterwards, which
# is what the buildable tick did for seventeen loads (`docs/PITFALLS.md`).
"""]
    for side, cap, listname, score, method_var, rank in (
            ("t", "urban", "town", "p", "pm", "yes"),
            ("r", "rural", "rural", "pr", "prm", "no")):
        for index, good in enumerate(order, start=1):
            by_building = groups.get((good, side), {})
            if not by_building:
                out.append(f"""
# {good}: no building that makes it may stand {"in a town" if side == "t" else "in a rural settlement"}.
# Scope: location
{MOD_ID}_plan_can_{listname}_{index} = {{ always = no }}
""")
                continue
            branches = ""
            for building, mis in sorted(by_building.items()):
                tests = "".join(
                    "\t\t\t\tvar:%s_%s%d = %d\n" % (MOD_ID, method_var, index, mi)
                    for mi in sorted(mis))
                branches += f"""\t\tAND = {{
\t\t\tOR = {{
{tests}\t\t\t}}
\t\t\tNOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_builds target = building_type:{building} }} }}
\t\t}}
"""
            out.append(f"""
# {good}, {"town" if side == "t" else "village"} side: {len(by_building)} building(s) could win it.
# Scope: location
{MOD_ID}_plan_can_{listname}_{index} = {{
\t# **A method won here, not "the ground pays for it".** A good the RGOs feed
\t# nothing still has a gain of zero and must still be placed: «не важно есть
\t# для них сырьё на этой земле или нет».
\tvar:{MOD_ID}_{method_var}{index} > 0
\t{MOD_ID}_plan_is_town = {rank}
\tvar:{MOD_ID}_load < global_var:{MOD_ID}_plan_cap_{cap}
\tNOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} }}
\tOR = {{
{branches}\t}}
}}
""")

    # And one per urban right: is there anything here for it to grant?
    #
    # **A right is no longer all or nothing.** It was, until the owner settled it
    # on 2026-09-01: «каждому городу будет выдано наиболее подходящее ему право.
    # Оно БУДЕТ выдано ОБЯЗАТЕЛЬНО.» Under the old rule a bundle of three against
    # an urban cap of three had to fit exactly, and the thirty-fourth run granted
    # **one** right across six towns. The arithmetic agrees with him: a right
    # grants +20% to +50% output where the whole RGO bonus is a ten per cent
    # band, so it is the largest thing in a town by a factor of two to five
    # (`docs/investigations/plan_formula.md`).
    #
    # So this asks only whether *any* good of the bundle can be made here. Which
    # right a town gets is still decided by `{MOD_ID}_rq<k>`, the bundle's own
    # scores added up, and a bundle whose goods mostly cannot stand here loses
    # that comparison on its own without needing a gate.
    for k, right in enumerate(output_rights(rows, game), start=1):
        bundle = sorted(right.output)
        wanted = [g for g in bundle if g in order and groups.get((g, "t"))]
        if not wanted:
            out.append(f"""
# {right.key}: no good of its bundle can stand in a town at all.
# Scope: location
{MOD_ID}_plan_right_fits_{k} = {{ always = no }}
""")
            continue
        tests = "".join(
            "\t\t%s_plan_can_town_%d = yes\n" % (MOD_ID, order.index(g) + 1)
            for g in wanted)
        out.append(f"""
# {right.key}: {", ".join(wanted)}. Granted if any one of them can be made here.
# Scope: location
{MOD_ID}_plan_right_fits_{k} = {{
\tOR = {{
{tests}\t}}
}}
""")
    return "".join(out)


def plan_loc_file(rows: list[eu5data.Method], game: eu5data.Game) -> str:
    """Which urban right a town was given, as text a row can print.

    A number on the location is all script can park there, and a row has to name
    the right. A `customizable_localization` of this mod's own is the way across
    -- defining one is fine; it is only overriding somebody else's that cannot be
    done (`CLAUDE.md`). The keys it points at are the ones the rights list on the
    mod page uses, icon and all.
    """
    rights = output_rights(rows, game)
    out = [HEADER, f"""#
# Every branch asks `has_variable` first. A row is drawn once a frame, and a
# comparison against a variable that is not there is an error per row per frame.
#
# Scope: location
{MOD_ID}_plan_right_label = {{
\ttype = location
"""]
    for k, right in enumerate(rights, start=1):
        out.append(f"""\ttext = {{
\t\ttrigger = {{ has_variable = {MOD_ID}_plan_right var:{MOD_ID}_plan_right = {k} }}
\t\tlocalization_key = {MOD_ID}_right_{right.key}
\t}}
""")
    out.append(f"""\ttext = {{
\t\tfallback = yes
\t\tlocalization_key = {MOD_ID}_plan_no_right
\t}}
}}
""")
    return "".join(out)


def plan_file(rows: list[eu5data.Method], split: dict[str, list[str]],
              game: eu5data.Game) -> str:
    """The whole-map plan: every good placed at once over the chosen ground.

    The owner's answers and the design are in
    `docs/investigations/whole_map_plan.md`. Five things belong in front of the
    code.

    **It is decided per location.** The plan spent one build deciding per
    province and giving every location of it the same list, and the thirty-second
    load is why it does not: a market village makes tools, jewelry, beer and
    pottery, so four villages of one province can take one each rather than all
    taking pottery. Provinces still read as coherent wherever they deserve to --
    every location of a province scores the same, so the ordered walk keeps
    coming back to it -- but that is now something that happens rather than
    something imposed.

    **An entry is a building, and a location holds one of each.** Two goods off
    the same building are one answer here; the same two goods in two locations
    are two.

    **Every building is one the game says may stand there.** `can_build_building`
    in a location's scope is the rank, the terrain and `location_potential`, and
    never an advance, so it is as true for ground nobody owns and for the plan
    aimed at the last age.

    **The score is normalized per good.** `out * (1 + bonus/100)` is in units of
    the good -- 1.0 of lumber against 0.2 of wine -- so each good is divided by
    its own best in this ground, one divisor for both sides, and only then do the
    numbers compare.

    **The scarce go first.** A good with one place in the whole ground that can
    hold it takes that place before a good with forty gets its second: the sweeps
    run in tiers, and a tier only admits goods that few locations can host. That
    is the owner's «жёстко зарезервировать слоты» and it costs one comparison.
    """
    order = [good for kind in ("raw", "made") for good in split[kind]]
    rights = output_rights(rows, game)
    groups = plan_groups(rows, split, game)

    out = [HEADER, f"""#
# Scope: country
{MOD_ID}_plan_run = {{
\tsave_scope_as = {MOD_ID}_country
\t{MOD_ID}_sync = yes
\t{MOD_ID}_collect_candidates = yes
\t{MOD_ID}_rebuild_browse = yes
\t{MOD_ID}_plan_prepare = yes
\t{MOD_ID}_plan_score = yes
\tif = {{
\t\tlimit = {{ has_global_variable = {MOD_ID}_plan_rights }}
\t\t{MOD_ID}_plan_place_rights = yes
\t}}
\t{MOD_ID}_plan_set_quota = yes
\t{MOD_ID}_plan_allocate = yes
\t{MOD_ID}_plan_rank = yes
\tcmf_log = {{ action = {MOD_ID}_log_plan }}
}}

# The ground this run works over, and everything the last one left on the map.
#
# `_plan_touched` is the previous run's locations, which a new choice on the map
# may no longer contain -- a location dropped out of the candidates would else
# keep its buildings, in the map mode as much as in the window.
#
# **`{MOD_ID}_force_town` and `_force_rural` are not among the things removed**:
# they are the player's answer to «what is this location», not the plan's.
# Scope: country
{MOD_ID}_plan_prepare = {{
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_touched
\t\tremove_variable = {MOD_ID}_load
\t\tremove_variable = {MOD_ID}_plan_rank
\t\tremove_variable = {MOD_ID}_plan_prank
\t\tremove_variable = {MOD_ID}_plan_right
\t\tremove_variable = {MOD_ID}_plan_town_row
\t\tremove_variable = {MOD_ID}_plan_prov_load
\t\tremove_variable = {MOD_ID}_plan_seen
\t\tclear_variable_list = {MOD_ID}_plan_goods
\t\tclear_variable_list = {MOD_ID}_plan_builds
\t}}
\tclear_global_variable_list = {MOD_ID}_plan_touched
\tclear_global_variable_list = {MOD_ID}_plan_prov_locs
\tclear_global_variable_list = {MOD_ID}_plan_ranked
\tclear_global_variable_list = {MOD_ID}_plan_results
\tset_global_variable = {{ name = {MOD_ID}_plan_placed value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_scored value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_found value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_shown value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_rooms value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_towns value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_provn value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_rightn value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_sweeps value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_band value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_cover value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_quota value = 1 }}
"""]
    for index, good in enumerate(order, start=1):
        out.append(f"\tset_global_variable = {{ name = {MOD_ID}_pn{index} value = 0 }}\n"
                   f"\tset_global_variable = {{ name = {MOD_ID}_pq{index} value = 1 }}\n"
                   f"\tset_global_variable = {{ name = {MOD_ID}_nrgo{index} value = 0 }}\n")
    # How many towns each right has been given, which its own score divides by.
    # A script value reading a global that is not there is the silent failure.
    for k in range(1, len(rights) + 1):
        out.append(f"\tset_global_variable = {{ name = {MOD_ID}_rgiven{k} value = 0 }}\n")
    # **What each pass of the allocator did, kept so the dump can print it.** Two
    # writes a pass and none per good or per location, so it costs nothing a
    # player can feel -- and it is the only part of the diagnosis that cannot be
    # read back afterwards: a pass that ran out of sweeps leaves no other trace.
    for i in range(1, len(PLAN_PASSES) + 1):
        out.append(f"\tset_global_variable = {{ name = {MOD_ID}_passsw{i} value = 0 }}\n"
                   f"\tset_global_variable = {{ name = {MOD_ID}_passpl{i} value = 0 }}\n")
    out.append(f"""
\t# Every candidate made ready. **Every counter a `limit` reads has to exist
\t# before the first round**: a comparison against a variable that is not there
\t# is the failure that logs nothing.
\t#
\t# `_plan_seen` marks the province through its first candidate, so
\t# `_plan_prov_locs` is one location per province -- what the row ordering
\t# walks, and the only thing the plan still asks a province.
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\tset_variable = {{ name = {MOD_ID}_load value = 0 }}
\t\tset_variable = {{ name = {MOD_ID}_plan_prank value = 9999 }}
\t\tremove_variable = {MOD_ID}_plan_right
\t\tclear_variable_list = {MOD_ID}_plan_goods
\t\tclear_variable_list = {MOD_ID}_plan_builds
\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_plan_touched target = this }}
\t\tif = {{
\t\t\tlimit = {{ {MOD_ID}_plan_is_town = yes }}
\t\t\tset_variable = {{ name = {MOD_ID}_plan_town_row value = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_rooms add = {MOD_ID}_show_plan_cap_urban }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_towns add = 1 }}
\t\t}}
\t\telse = {{
\t\t\tremove_variable = {MOD_ID}_plan_town_row
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_rooms add = {MOD_ID}_show_plan_cap_rural }}
\t\t}}
\t\tif = {{
\t\t\tlimit = {{ NOT = {{ has_variable = {MOD_ID}_plan_seen }} }}
\t\t\tprovince_definition = {{
\t\t\t\tevery_location_in_province_definition = {{
\t\t\t\t\tset_variable = {{ name = {MOD_ID}_plan_seen value = 1 }}
\t\t\t\t}}
\t\t\t}}
\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_plan_prov_locs target = this }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_provn add = 1 }}
\t\t}}
\t}}
}}

# One scoring pass per good, the harvest that makes the answers comparable, and
# the count of how few places can hold it.
#
# **This is the expensive half of the mod and the reason the plan is a button of
# its own.** A single-good run reads about five methods on each candidate; this
# reads all {len(rows)} of them, {len(order)} passes over the same ground.
# Scope: country
{MOD_ID}_plan_score = {{
""")
    for index, good in enumerate(order, start=1):
        out.append(f"\t{MOD_ID}_score_{index} = yes\n"
                   f"\t{MOD_ID}_plan_harvest_{index} = yes\n")
    out.append("}\n")

    for index, good in enumerate(order, start=1):
        # **One RGO already standing counts as one building of that good**, the
        # owner on 2026-09-01: «1 рго ты можешь рассматривать как один домик
        # локации… хочешь добывать глину 5 домиками на области, там уже есть 2
        # рго глины — тебе нужно всего 3 домика». So it is a count against the
        # quota and never a discount on the score. Only a raw good has an RGO to
        # count, and the engine already refuses to duplicate one: `clay_pit`,
        # `stone_quarry`, `sand_pit` and `bog_iron_smelter` all carry
        # `NOT = { raw_material = goods:<their own> }`.
        rgo_count = "" if good not in game.raw_goods else f"""\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\tlimit = {{ raw_material = goods:{good} }}
\t\tchange_global_variable = {{ name = {MOD_ID}_nrgo{index} add = 1 }}
\t}}"""
        out.append(f"""
# {good}: keep both sides and the method that won each, then divide the ground by
# the better of them, so that {RANK_SCALE} means "the location this good wants most" for
# every good alike. A good nothing here can make stays at zero and never picks.
#
# `_ng{index}` is how many candidates could hold it at all, which is what the
# tiers in `{MOD_ID}_plan_allocate` order the goods by.
# Scope: country
{MOD_ID}_plan_harvest_{index} = {{
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\t# The province decay counter, zeroed in this walk rather than in
\t\t# `_plan_prepare` because this one happens anyway. **It has to exist
\t\t# before the first round**: `{MOD_ID}_pdiv{index}` reads it on every
\t\t# ordering, and a script value reading a variable that is not there is
\t\t# the failure that logs nothing.
\t\tset_variable = {{ name = {MOD_ID}_pp{index} value = 0 }}
\t\t# **The two sides are "where may this building stand", not "is it a
\t\t# village".** Thirty production buildings declare `rural_settlement` and
\t\t# only four are villages, so the ranking's category split would leave a
\t\t# rural location with nothing but villages to be offered.
\t\tif = {{
\t\t\tlimit = {{ has_global_variable = {MOD_ID}_plan_by_end }}
\t\t\tset_variable = {{ name = {MOD_ID}_p{index} value = var:{MOD_ID}_pendgain_t }}
\t\t\tset_variable = {{ name = {MOD_ID}_pm{index} value = var:{MOD_ID}_pendbest_method_t }}
\t\t\tset_variable = {{ name = {MOD_ID}_pr{index} value = var:{MOD_ID}_pendgain_r }}
\t\t\tset_variable = {{ name = {MOD_ID}_prm{index} value = var:{MOD_ID}_pendbest_method_r }}
\t\t\t# **Nothing the ground feeds: take the recipe it does not.** A location
\t\t\t# no RGO helps still has to be filled, and a granted right's bundle goes
\t\t\t# up whether the bonus is there or not -- the owner, 2026-09-01. The
\t\t\t# fallback is divided by {UNFED_PENALTY} so that it is genuinely last in the
\t\t\t# queue: everything the ground earns is placed before anything it does
\t\t\t# not, which is «свести к минимуму» rather than forbid.
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_pm{index} = 0 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_p{index} value = var:{MOD_ID}_pendanygain_t }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_pm{index} value = var:{MOD_ID}_pendanybest_method_t }}
\t\t\t\tchange_variable = {{ name = {MOD_ID}_p{index} divide = {UNFED_PENALTY} }}
\t\t\t}}
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_prm{index} = 0 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_pr{index} value = var:{MOD_ID}_pendanygain_r }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_prm{index} value = var:{MOD_ID}_pendanybest_method_r }}
\t\t\t\tchange_variable = {{ name = {MOD_ID}_pr{index} divide = {UNFED_PENALTY} }}
\t\t\t}}
\t\t}}
\t\telse = {{
\t\t\tset_variable = {{ name = {MOD_ID}_p{index} value = var:{MOD_ID}_pnowgain_t }}
\t\t\tset_variable = {{ name = {MOD_ID}_pm{index} value = var:{MOD_ID}_pnowbest_method_t }}
\t\t\tset_variable = {{ name = {MOD_ID}_pr{index} value = var:{MOD_ID}_pnowgain_r }}
\t\t\tset_variable = {{ name = {MOD_ID}_prm{index} value = var:{MOD_ID}_pnowbest_method_r }}
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_pm{index} = 0 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_p{index} value = var:{MOD_ID}_pnowanygain_t }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_pm{index} value = var:{MOD_ID}_pnowanybest_method_t }}
\t\t\t\tchange_variable = {{ name = {MOD_ID}_p{index} divide = {UNFED_PENALTY} }}
\t\t\t}}
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_prm{index} = 0 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_pr{index} value = var:{MOD_ID}_pnowanygain_r }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_prm{index} value = var:{MOD_ID}_pnowanybest_method_r }}
\t\t\t\tchange_variable = {{ name = {MOD_ID}_pr{index} divide = {UNFED_PENALTY} }}
\t\t\t}}
\t\t}}
\t}}
\tset_global_variable = {{ name = {MOD_ID}_ng{index} value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_nrgo{index} value = 0 }}
\t# **Counted on the side the location actually is**, which `{MOD_ID}_ordmax{index}`
\t# does not do: it is the better of the two sides, so a good whose only
\t# buildings are rural counts as makeable on ground that is all towns. The
\t# thirty-sixth run is what that costs -- five towns of Münsterland reported
\t# «товаров 13» where at most eight could ever stand there, and the quota is
\t# divided by that number, so every good's share came out too small.
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\tlimit = {{
\t\t\tOR = {{
\t\t\t\tAND = {{
\t\t\t\t\t{MOD_ID}_plan_is_town = yes
\t\t\t\t\tvar:{MOD_ID}_pm{index} > 0
\t\t\t\t}}
\t\t\t\tAND = {{
\t\t\t\t\t{MOD_ID}_plan_is_town = no
\t\t\t\t\tvar:{MOD_ID}_prm{index} > 0
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t\tchange_global_variable = {{ name = {MOD_ID}_ng{index} add = 1 }}
\t}}
{rgo_count}
\t# **Nothing is normalized any more, and the pass that did it is gone.** The
\t# gain is already the same question for every good -- what fraction of this
\t# recipe's own ceiling this ground pays -- so the ordered walk that used to
\t# find each good's best on the ground, once per good, is 47 walks saved.
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_ng{index} > 0 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_scored add = 1 }}
\t}}
}}
""")

    # ---- adding a good to a location ---------------------------------------
    out.append(f"""
# One good, into the location in hand.
#
# **Guarded, and asked the same question the ordered walk used as its `limit`**,
# so the urban-rights round can call this on its own without repeating a word --
# and so a right whose second good wants a building the first took is simply not
# given it.
#
# The building goes into a list beside the good, because that is what a location
# can only hold one of. Which building it is comes off the method the harvest
# kept.
""")
    for side, listname, method_var in (("t", "town", "pm"), ("r", "rural", "prm")):
        for index, good in enumerate(order, start=1):
            by_building = groups.get((good, side), {})
            if not by_building:
                continue
            branches = ""
            for building, mis in sorted(by_building.items()):
                tests = "".join(
                    "\t\t\t\tvar:%s_%s%d = %d\n" % (MOD_ID, method_var, index, mi)
                    for mi in sorted(mis))
                branches += f"""\t\tif = {{
\t\t\tlimit = {{ OR = {{
{tests}\t\t\t}} }}
\t\t\tadd_to_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }}
\t\t\tadd_to_variable_list = {{ name = {MOD_ID}_plan_builds target = building_type:{building} }}
\t\t\t# Every location of the province, so the next building of this good
\t\t\t# finds the whole province worth half. Guarded on the variable being
\t\t\t# there: a province reaches locations that were never candidates.
\t\t\tprovince_definition = {{
\t\t\t\tevery_location_in_province_definition = {{
\t\t\t\t\tlimit = {{ has_variable = {MOD_ID}_pp{index} }}
\t\t\t\t\tchange_variable = {{ name = {MOD_ID}_pp{index} add = 1 }}
\t\t\t\t}}
\t\t\t}}
\t\t\tchange_variable = {{ name = {MOD_ID}_load add = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_placed add = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_added add = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_pn{index} add = 1 }}
\t\t}}
"""
            out.append(f"""# {good}, {"town" if side == "t" else "village"} side.
# Scope: location
{MOD_ID}_plan_try_{listname}_{index} = {{
\tif = {{
\t\tlimit = {{ {MOD_ID}_plan_can_{listname}_{index} = yes }}
{branches}\t}}
}}
""")

    # ---- the rights round --------------------------------------------------
    out.append(f"""
# Urban rights, before any good is placed and only in towns.
#
# **A right is chosen per town, not by rights taking turns.** There are {len(rights)} of
# them and rarely that many towns in a plan, so an order over rights would decide
# the outcome by its own arbitrariness. Asked the other way round -- which right
# does this ground suit best -- every town gets the answer that is true about it.
#
# **And a right is granted whether or not the whole bundle fits**, since
# 2026-09-01: «Оно БУДЕТ выдано ОБЯЗАТЕЛЬНО. И каждый такой город обязательно
# получит все здания из его бонуса.» The bundle's buildings go in before any
# ordinary good touches the town, and where the urban cap is smaller than the
# bundle the town simply runs out of room -- which is the thing the owner wants
# to see, at caps of 3, 4 and 5. Under the old all-or-nothing rule the
# thirty-fourth run granted one right across six towns.
#
# `{MOD_ID}_rq<k>` is the bundle's own normalized scores added up, which costs no
# pass -- the goods were scored anyway.
# Scope: country
{MOD_ID}_plan_place_rights = {{
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\tlimit = {{
\t\t\t{MOD_ID}_plan_is_town = yes
\t\t\tvar:{MOD_ID}_load = 0
\t\t}}
\t\tset_variable = {{ name = {MOD_ID}_rbest value = 0 }}
\t\tset_variable = {{ name = {MOD_ID}_rbest_k value = 0 }}
""")
    for k, right in enumerate(rights, start=1):
        bundle = sorted(right.output)
        gate = ("" if not right.potential
                else f"\t\t\t\tscope:{MOD_ID}_country = {{ AND = {{ {right.potential} }} }}\n")
        out.append(f"""\t\t# {right.key}: {", ".join(bundle)}
\t\tset_variable = {{ name = {MOD_ID}_rtry value = {MOD_ID}_rq{k} }}
\t\tif = {{
\t\t\tlimit = {{
\t\t\t\tvar:{MOD_ID}_rtry > var:{MOD_ID}_rbest
\t\t\t\t{MOD_ID}_plan_right_fits_{k} = yes
{gate}\t\t\t}}
\t\t\tset_variable = {{ name = {MOD_ID}_rbest value = var:{MOD_ID}_rtry }}
\t\t\tset_variable = {{ name = {MOD_ID}_rbest_k value = {k} }}
\t\t}}
""")
    # **A bundle good the ground refuses gets its input planted instead.** The
    # right's building is mandatory and the slot is the right's, so where glass
    # cannot stand the slot goes to the sand pit that would make it possible
    # rather than back to the ordinary goods -- the owner, 2026-09-01. Derived
    # rather than named: `market_inputs` finds one pair in the whole game.
    substitute = market_inputs(game)
    for k, right in enumerate(rights, start=1):
        bundle = sorted(right.output)
        lines = []
        for g in bundle:
            if not groups.get((g, "t")):
                continue
            i = order.index(g) + 1
            feeder = substitute.get(g)
            j = order.index(feeder) + 1 if feeder in order else 0
            if j and groups.get((feeder, "t")):
                lines.append(
                    f"\t\t\tif = {{\n"
                    f"\t\t\t\tlimit = {{ {MOD_ID}_plan_can_town_{i} = yes }}\n"
                    f"\t\t\t\t{MOD_ID}_plan_try_town_{i} = yes\n"
                    f"\t\t\t}}\n"
                    f"\t\t\telse = {{\n"
                    f"\t\t\t\t# {g} cannot stand here; plant the {feeder} that would let it.\n"
                    f"\t\t\t\t{MOD_ID}_plan_try_town_{j} = yes\n"
                    f"\t\t\t}}\n")
            else:
                lines.append(f"\t\t\t{MOD_ID}_plan_try_town_{i} = yes\n")
        adds = "".join(lines)
        out.append(f"""\t\tif = {{
\t\t\tlimit = {{ var:{MOD_ID}_rbest_k = {k} }}
{adds}\t\t\tset_variable = {{ name = {MOD_ID}_plan_right value = {k} }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_rgiven{k} add = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_rightn add = 1 }}
\t\t}}
""")
    out.append("\t}\n}\n")

    # ---- the quota ---------------------------------------------------------
    #
    # What «равномерно» means, and it is the same rule at both scales the owner
    # described. Three provinces and forty goods gives a quota under one, so
    # every good takes exactly one place and the small realm comes out mixed
    # rather than specialised; a large realm gives a quota of twenty-odd, so each
    # good takes its best twenty-odd places -- which are the ones its raw
    # materials lie under -- and then stops, and the rooms left over are what the
    # goods with no bonus anywhere fill. His answer 4, in one number.
    #
    # It is counted over the ground the rights have already taken their share of,
    # because a right is not optional and its buildings are not the quota's to
    # give away.
    quota_lines = "".join(
        f"""\tset_global_variable = {{ name = {MOD_ID}_pq{index} value = global_var:{MOD_ID}_plan_quota }}
\tchange_global_variable = {{ name = {MOD_ID}_pq{index} subtract = global_var:{MOD_ID}_nrgo{index} }}
\tchange_global_variable = {{ name = {MOD_ID}_pq{index} max = 1 }}
"""
        for index, good in enumerate(order, start=1))
    out.append(f"""
# How many buildings each good may claim before the ground is opened to all.
#
# `_plan_rooms` is every candidate's cap added up and `_plan_placed` is what the
# rights have already spent, so the division is the fair share of what is left.
# `_plan_scored` is how many goods this ground can make at all -- a good nothing
# here can produce must not take a share and shrink everyone else's.
#
# **`max = 1` is the floor and it is deliberate.** A ground too small to give
# every good one building still gives every good one building; what gives way
# then is the cap, not the spread, and the header line says so by showing more
# goods than rooms. The RGO discount comes off the same number.
# Scope: country
{MOD_ID}_plan_set_quota = {{
\tset_global_variable = {{ name = {MOD_ID}_plan_quota value = global_var:{MOD_ID}_plan_rooms }}
\tchange_global_variable = {{ name = {MOD_ID}_plan_quota subtract = global_var:{MOD_ID}_plan_placed }}
\tchange_global_variable = {{ name = {MOD_ID}_plan_quota max = 0 }}
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_plan_scored > 0 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_quota divide = {MOD_ID}_plan_scored_value }}
\t}}
\tchange_global_variable = {{ name = {MOD_ID}_plan_quota max = 1 }}
{quota_lines}}}
""")

    # ---- the sweeps --------------------------------------------------------
    out.append(f"""
# The rounds, in tiers, the scarce goods first.
#
# **A good with one place in the whole ground that can hold it takes that place
# before a good with forty gets its second.** That is the owner's «жёстко
# зарезервировать слоты», and iron is the case he named: without an RGO it comes
# from one building, `bog_iron_smelter`, which wants wetlands or a lake, so where
# it can go at all it must. A tier admits only goods `_ng<n>` says few locations
# can host; the last tier is everything.
#
# Within a tier the sweeps run until one adds nothing anywhere, so **a location
# the plan can feed is never left empty**. The sweep counter is a guard against a
# condition that cannot be left, not a design.
# Scope: country
{MOD_ID}_plan_allocate = {{
""")
    # **Dealt in bands, highest gain first, across every good at once.**
    # That is the optimum and the whole of it: by the time a good that would
    # gain a tenth of its ceiling reaches a location, the good that would have
    # gained nine tenths has already taken it. The opportunity cost is paid by
    # the ordering rather than by asking every other good what it would have
    # made of the place. `docs/investigations/plan_formula.md` derives it.
    #
    # A band costs a sweep, so there are five rather than ten. The last is 0,
    # which admits a good the RGOs feed nothing -- and it must, because every
    # good the ground can produce has to be produced.
    # The bands wrap the scarcity tiers only. **Then coverage, then the open
    # pass**, each once: the first is the owner's hard constraint -- every good
    # the ground can produce is produced -- and the second fills what is left.
    for number, (band, tier) in enumerate(PLAN_PASSES, start=1):
        out.append(f"\tset_global_variable = {{ name = {MOD_ID}_plan_band value = {band} }}\n")
        out.append(f"\tset_global_variable = {{ name = {MOD_ID}_plan_cover "
                   f"value = {1 if tier is COVER_TIER else 0} }}\n")
        if tier is COVER_TIER:
            out.append("""\t# **Every good the ground can produce is produced.** The owner's first
\t# requirement and the one the bands cannot keep on their own: a good that
\t# lost every band -- because the rights took the towns, or because it gains
\t# nothing and the ground filled -- takes a free slot here, anywhere, at any
\t# gain. «Все товары которые можно произвести на выбранной земле должны
\t# производиться, все.»
""")
            tier = 0
        # **The open pass raises every quota by one a round; it does not lift
        # them.** Lifting was the thirty-sixth run: five towns of Münsterland,
        # ten buildings in fifteen rooms and the same good standing in three of
        # them, because the first good down the list took every free room at
        # once. Raising fills the leftover ground a layer at a time instead, so
        # what is spare is spread the same way the quota itself is.
        raise_all = ""
        if tier is OPEN_TIER:
            raise_all = "".join(
                f"\t\tchange_global_variable = {{ name = {MOD_ID}_pq{i} add = 1 }}\n"
                for i in range(1, len(order) + 1))
            tier = 0
        out.append(f"""\tset_global_variable = {{ name = {MOD_ID}_plan_tier value = {tier} }}
\tset_global_variable = {{ name = {MOD_ID}_plan_go value = 1 }}
\t# **The guard is per tier and not across them.** It was one counter for all
\t# {len(PLAN_TIERS)} of them for one load, and the thirty-third run spent it on the scarce
\t# tiers: «кругов 12» on the screen, twenty-eight buildings out of a hundred
\t# and forty-four places, most locations holding one thing. The last tier --
\t# the one that fills the ground -- never ran at all.
\tset_global_variable = {{ name = {MOD_ID}_plan_tsweeps value = 0 }}
\twhile = {{
\t\tlimit = {{
\t\t\tglobal_var:{MOD_ID}_plan_go = 1
\t\t\tglobal_var:{MOD_ID}_plan_tsweeps < {PLAN_ROUNDS}
\t\t}}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_tsweeps add = 1 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_sweeps add = 1 }}
\t\tset_global_variable = {{ name = {MOD_ID}_plan_added value = 0 }}
{raise_all}""")
        for index, good in enumerate(order, start=1):
            out.append(f"\t\t{MOD_ID}_plan_pick_{index} = yes\n")
        out.append(f"""\t\tif = {{
\t\t\tlimit = {{ global_var:{MOD_ID}_plan_added = 0 }}
\t\t\tset_global_variable = {{ name = {MOD_ID}_plan_go value = 0 }}
\t\t}}
\t}}
\t# What this pass cost and what it had by the end of it. `_passsw` at
\t# {PLAN_ROUNDS} is a pass the guard cut off with work still to do, which is the
\t# one fault in here that leaves no other trace.
\tset_global_variable = {{ name = {MOD_ID}_passsw{number} value = global_var:{MOD_ID}_plan_tsweeps }}
\tset_global_variable = {{ name = {MOD_ID}_passpl{number} value = global_var:{MOD_ID}_plan_placed }}
""")
    out.append("}\n")

    for index, good in enumerate(order, start=1):
        town_side = "town" if groups.get((good, "t")) else ""
        rural_side = "rural" if groups.get((good, "r")) else ""
        out.append(f"""
# {good} takes the one location each side of it suits best, or neither.
#
# `max = 1` on an ordered walk is the engine doing the choosing, which is the
# only reason a sweep over {len(order)} goods twice is affordable. The tier gate above the
# walk is what holds a common good back while a scarce one is still placing.
# Scope: country
{MOD_ID}_plan_pick_{index} = {{
""")
        for side, order_value in ((town_side, f"{MOD_ID}_ord{index}"),
                                  (rural_side, f"{MOD_ID}_ordr{index}")):
            if not side:
                continue
            out.append(f"""\tif = {{
\t\tlimit = {{
\t\t\tOR = {{
\t\t\t\tglobal_var:{MOD_ID}_plan_tier = 0
\t\t\t\tglobal_var:{MOD_ID}_ng{index} <= global_var:{MOD_ID}_plan_tier
\t\t\t}}
\t\t\tOR = {{
\t\t\t\tglobal_var:{MOD_ID}_plan_max = 0
\t\t\t\tglobal_var:{MOD_ID}_pn{index} < global_var:{MOD_ID}_plan_max
\t\t\t}}
\t\t\t# The quota. **Never lifted** -- the open pass raises it by one a
\t\t\t# round instead, so leftover ground fills in even layers rather than
\t\t\t# going whole to whichever good the list happens to reach first.
\t\t\tglobal_var:{MOD_ID}_pn{index} < global_var:{MOD_ID}_pq{index}
\t\t\t# The covering pass admits only a good that has nothing at all.
\t\t\tOR = {{
\t\t\t\tglobal_var:{MOD_ID}_plan_cover = 0
\t\t\t\tglobal_var:{MOD_ID}_pn{index} = 0
\t\t\t}}
\t\t}}
\t\tordered_in_global_list = {{
\t\t\tvariable = {MOD_ID}_candidates
\t\t\t# **The band, and it is the whole of the optimum.** The ground is
\t\t\t# dealt in descending order of gain across every good at once, so by
\t\t\t# the time a good that would gain a tenth reaches a location, the good
\t\t\t# that would have gained nine tenths has already taken it. That is the
\t\t\t# opportunity cost, paid for by one comparison rather than by asking
\t\t\t# every other good what it would have made of the place.
\t\t\tlimit = {{
\t\t\t\t{MOD_ID}_plan_can_{side}_{index} = yes
\t\t\t\t{order_value} >= global_var:{MOD_ID}_plan_band
\t\t\t}}
\t\t\torder_by = {order_value}
\t\t\tmax = 1
\t\t\tcheck_range_bounds = no
\t\t\t{MOD_ID}_plan_try_{side}_{index} = yes
\t\t}}
\t}}
""")
        out.append("}\n")

    out.append(f"""
# The rows: one per location that got anything, its province's locations together.
#
# **Provinces are ranked first and their locations follow.** A sort on the
# location's own load ties nearly all of them and `ordered_in_global_list`
# promises nothing about ties, so two provinces would interleave. The provinces
# are put in order by how much the plan put in each, every location is told its
# province's place, and the rows sort on that with a province's towns ahead of
# its villages.
#
# A province's load is added up through a global, because a walk over its
# locations cannot write back to the scope that started it.
# Scope: country
{MOD_ID}_plan_rank = {{
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_prov_locs
\t\tset_global_variable = {{ name = {MOD_ID}_plan_count value = 0 }}
\t\tprovince_definition = {{
\t\t\tevery_location_in_province_definition = {{
\t\t\t\tlimit = {{ has_variable = {MOD_ID}_load }}
\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_count add = var:{MOD_ID}_load }}
\t\t\t}}
\t\t}}
\t\tset_variable = {{ name = {MOD_ID}_plan_prov_load value = global_var:{MOD_ID}_plan_count }}
\t}}
\tset_global_variable = {{ name = {MOD_ID}_plan_prov_n value = 0 }}
\tordered_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_prov_locs
\t\torder_by = {MOD_ID}_plan_prov_order
\t\tmax = 400
\t\tcheck_range_bounds = no
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_prov_n add = 1 }}
\t\tprovince_definition = {{
\t\t\tevery_location_in_province_definition = {{
\t\t\t\tlimit = {{ has_variable = {MOD_ID}_plan_prank }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_plan_prank value = global_var:{MOD_ID}_plan_prov_n }}
\t\t\t}}
\t\t}}
\t}}
\t# Counted before the rows are taken and separately from them: the walk below
\t# stops at {PLAN_ROWS}, and a count that stopped with it would say the plan used
\t# exactly as many locations as the window can draw, whatever it really used.
\tset_global_variable = {{ name = {MOD_ID}_plan_found value = 0 }}
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\tlimit = {{ var:{MOD_ID}_load > 0 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_found add = 1 }}
\t}}
\tset_global_variable = {{ name = {MOD_ID}_plan_shown value = 0 }}
\tordered_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\tlimit = {{ var:{MOD_ID}_load > 0 }}
\t\torder_by = {MOD_ID}_plan_order
\t\tmax = {PLAN_ROWS}
\t\tcheck_range_bounds = no
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_shown add = 1 }}
\t\tset_variable = {{ name = {MOD_ID}_plan_rank value = global_var:{MOD_ID}_plan_shown }}
\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_plan_ranked target = this }}
\t}}
}}

# The window's own list, filled on opening and emptied on closing -- the same
# contract as the other two windows and for the same reason: a scripted widget
# never comes down, so emptying the datamodel is the only thing that frees a row.
# Scope: country
{MOD_ID}_plan_show = {{
\tclear_global_variable_list = {MOD_ID}_plan_results
\tordered_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_ranked
\t\torder_by = {MOD_ID}_plan_rank_order
\t\tmax = {MOD_ID}_show_plan_shown
\t\tcheck_range_bounds = no
\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_plan_results target = this }}
\t}}
}}

# Scope: country
{MOD_ID}_plan_hide = {{
\tclear_global_variable_list = {MOD_ID}_plan_results
}}

# The same thing the window's own scripted GUI does, reachable from an effect,
# because a Mod Menu button is script and script cannot reach the interface's
# variable system.
# Scope: country
{MOD_ID}_open_plan_window_effect = {{
\t{MOD_ID}_plan_show = yes
\tremove_variable = {MOD_ID}_result_open
\tremove_variable = {MOD_ID}_right_open
\t{MOD_ID}_hide_results = yes
\tset_variable = {{ name = {MOD_ID}_plan_open value = 1 }}
}}
""")
    return "".join(out)


def rows_file() -> str:
    """The ranking pass. One row per province definition, best first.

    There is no Mod Menu table any more: it said the same thing as the window in
    one line each, and it was the only thing holding the answer to fifty rows.
    What is left is the list the window repeats over.
    """
    out = [HEADER, f"""#
# Ranking is the engine's: `ordered_in_global_list` takes `order_by` as a script
# value and sorts highest first -- vanilla proves the direction by writing
# `multiply = -1` on the one place it wants the weakest -- and pairs `max` with
# `check_range_bounds = no` when the list may be shorter than asked for.
#
# Scope: country
{MOD_ID}_clear_rows = {{
\tset_global_variable = {{ name = {MOD_ID}_found value = 0 }}
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_row_taken_locations
\t\tremove_variable = {MOD_ID}_row_taken
\t\tremove_variable = {MOD_ID}_rank
\t}}
\tclear_global_variable_list = {MOD_ID}_row_taken_locations
\t# `_ranked` is the answer and survives; `_results` is the copy the window
\t# repeats over, and it only exists while the window is open -- emptying the
\t# datamodel is the only thing that frees a scripted widget's rows.
\tclear_global_variable_list = {MOD_ID}_ranked
\tclear_global_variable_list = {MOD_ID}_results
\t# Both windows' lists, and forgetting the second one is what left the rights
\t# window drawing rows whose rank had just been taken off them.
\tclear_global_variable_list = {MOD_ID}_right_results
}}

# Scope: country
{MOD_ID}_fill_rows = {{
\t# `max` counts locations walked, not rows produced. Every location of a
\t# province scores the same and only the first of them takes a row, so fifty
\t# would have stopped at about a dozen provinces -- which is what the fifth run
\t# showed. Eight locations per province is above the game's widest.
\tordered_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\torder_by = {MOD_ID}_score
\t\tmax = {RESULT_ROWS * 8}
\t\tcheck_range_bounds = no
\t\t{MOD_ID}_store_row = yes
\t}}
}}

# Park one province's answer on the location the ranking kept, and remember that
# location in rank order.
#
# One row per province definition -- the province as the map draws it, whole,
# rather than the piece of it one country owns. The game splits a province by
# ownership: half of Bessarabia under Moldavia is its own `province`, named
# "Moldavian province Bessarabia", and the other half is another. Every location
# of one piece scores the same, so a row per piece is several ways of saying one
# thing -- and worse, the number itself would move on the day the pieces join,
# which is exactly the day this mod is planning for.
#
# Taken is marked on the locations rather than on the definition: a location
# certainly holds a variable, and this pass already has every one of them.
# Scope: location
{MOD_ID}_store_row = {{
\tif = {{
\t\tlimit = {{
\t\t\tglobal_var:{MOD_ID}_found < {RESULT_ROWS}
\t\t\t# Nothing won here on either side and in neither age -- which now means
\t\t\t# the good is made in no building this location could ever hold. A row
\t\t\t# for it would have no building and no method to print.
\t\t\t#
\t\t\t# The endgame halves are in the OR on purpose: in the first age most
\t\t\t# goods have nothing available yet, and dropping those rows would empty
\t\t\t# the second column exactly where it is worth most.
\t\t\tOR = {{
\t\t\t\tvar:{MOD_ID}_best_method > 0
\t\t\t\tvar:{MOD_ID}_best_method_rural > 0
\t\t\t\tvar:{MOD_ID}_mid_best_method > 0
\t\t\t\tvar:{MOD_ID}_mid_best_method_rural > 0
\t\t\t\tvar:{MOD_ID}_end_best_method > 0
\t\t\t\tvar:{MOD_ID}_end_best_method_rural > 0
\t\t\t}}
\t\t\tNOT = {{ has_variable = {MOD_ID}_row_taken }}
\t\t}}
\t\tprovince_definition = {{
\t\t\tevery_location_in_province_definition = {{
\t\t\t\tset_variable = {{ name = {MOD_ID}_row_taken value = 1 }}
\t\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_row_taken_locations target = this }}
\t\t\t}}
\t\t}}
\t\t# The winners are parked first and the row decided afterwards, because
\t\t# «is this province worth a row» is a question about the bonus, and the
\t\t# bonus is not known until the method that won is.
\t\t# Which of the three the row *names* follows the button. Ranked for the
\t\t# last age and still reading «Гильдия портных» off the near column is what
\t\t# the twenty-third run saw: the order was right and the building was the one
\t\t# you can build today. A variable on the row rather than a global read from
\t\t# the window, because a location variable is the one thing the GUI is proven
\t\t# to read.
\t\tif = {{
\t\t\tlimit = {{ has_global_variable = {MOD_ID}_rank_by_end }}
\t\t\tset_variable = {{ name = {MOD_ID}_row_end value = 1 }}
\t\t}}
\t\telse = {{
\t\t\tremove_variable = {MOD_ID}_row_end
\t\t}}
\t\t# **How many of the province's locations can actually hold this answer.**
\t\t# Every location of a province scores the same -- the bonus is the whole
\t\t# province's -- but they do not all pass `can_build_building`: the owner
\t\t# found a quarry offered for Sauerland where one of its seven locations is
\t\t# flat. The scoring pass has already asked that question of every
\t\t# candidate, so the count is free: the locations whose own winner is the
\t\t# same method as this row's are the ones the building may stand in.
\t\tset_global_variable = {{ name = {MOD_ID}_fit_method value = var:{MOD_ID}_best_method }}
\t\tset_global_variable = {{ name = {MOD_ID}_fit_method_rural value = var:{MOD_ID}_best_method_rural }}
\t\tset_global_variable = {{ name = {MOD_ID}_fit_n value = 0 }}
\t\tset_global_variable = {{ name = {MOD_ID}_fit_all value = 0 }}
\t\tprovince_definition = {{
\t\t\tevery_location_in_province_definition = {{
\t\t\t\tlimit = {{ has_variable = {MOD_ID}_best_method }}
\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_fit_all add = 1 }}
\t\t\t\tif = {{
\t\t\t\t\tlimit = {{
\t\t\t\t\t\tOR = {{
\t\t\t\t\t\t\tAND = {{
\t\t\t\t\t\t\t\tglobal_var:{MOD_ID}_fit_method > 0
\t\t\t\t\t\t\t\tvar:{MOD_ID}_best_method = global_var:{MOD_ID}_fit_method
\t\t\t\t\t\t\t}}
\t\t\t\t\t\t\tAND = {{
\t\t\t\t\t\t\t\tglobal_var:{MOD_ID}_fit_method_rural > 0
\t\t\t\t\t\t\t\tvar:{MOD_ID}_best_method_rural = global_var:{MOD_ID}_fit_method_rural
\t\t\t\t\t\t\t}}
\t\t\t\t\t\t}}
\t\t\t\t\t}}
\t\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_fit_n add = 1 }}
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t\tset_variable = {{ name = {MOD_ID}_fit value = global_var:{MOD_ID}_fit_n }}
\t\tset_variable = {{ name = {MOD_ID}_fit_of value = global_var:{MOD_ID}_fit_all }}
\t\t{MOD_ID}_store_winner_now_town = yes
\t\t{MOD_ID}_store_winner_now_rural = yes
\t\t{MOD_ID}_store_winner_mid_town = yes
\t\t{MOD_ID}_store_winner_mid_rural = yes
\t\t{MOD_ID}_store_winner_end_town = yes
\t\t{MOD_ID}_store_winner_end_rural = yes
\t\tif = {{
\t\t\tlimit = {{ {MOD_ID}_row_is_worth_it = yes }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_found add = 1 }}
\t\t\t# The place in the ranking, written down where the row can print it. The
\t\t\t# order a list is built in is not an order anything downstream promises
\t\t\t# to keep, so the answer says its own rank rather than where it sits.
\t\t\tset_variable = {{ name = {MOD_ID}_rank value = global_var:{MOD_ID}_found }}
\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_ranked target = this }}
\t\t}}
\t}}
}}
"""]
    return "".join(out)


def output_rights(rows: list[eu5data.Method], game: eu5data.Game) -> list[eu5data.TownRight]:
    """The urban rights this mod answers for: the ones that raise an output.

    A right that grants building levels instead is a quantity where these are
    ratios, and `docs/investigations/town_rights.md` is why the two must not
    share a number. Flemish cloth and the four marketplace charters are left out
    rather than scored badly.

    A good the game makes no method for would be an empty slot on every row, so
    it is dropped from the bundle, and a right left with nothing is dropped
    whole.
    """
    made = {m.produced for m in rows}
    keep = []
    for right in game.town_rights:
        bundle = {g: v for g, v in right.output.items() if g in made}
        if bundle:
            keep.append(eu5data.TownRight(key=right.key, output=bundle,
                                          levels=right.levels, penalty=right.penalty,
                                          advance=right.advance,
                                          potential=right.potential))
    return keep


def rights_file(rows: list[eu5data.Method], split: dict[str, list[str]],
                game: eu5data.Game) -> str:
    """Ranking ground for a whole urban right rather than for one good.

    **A right's percentage re-ranks nothing.** `+20% books` is the same +20% in
    every location on the map, and so is the efficiency penalty eleven of the
    seventeen share: multiply every candidate by one number and the order is
    what it was. What re-ranks is the *bundle*. Eight of the nine general rights
    favour two or three goods at once and a province's RGO bonus is per good --
    it can supply lumber and not dyes -- so «where do Printing Rights go» has a
    different answer from «where do I make books», and it is the only question
    here worth a pass of its own.

    **Goods are added through their price.** Four books a level and 0.3 masonry
    a level are not one number, which is the same mistake as ranking a forest
    village above a weapon guild. `default_market_price` is the weight, so the
    total a row carries is what the ground would earn a level rather than how
    many things it would make.

    Per candidate the pass reuses the per-good scorers already generated: each
    good of the bundle in turn, the better of its built-up and village answers
    kept in a slot, the slot values summed. The winning method is resolved into
    a building and a bonus only for the provinces that take a row, because the
    dispatch over 218 methods is far too wide to run per candidate.
    """
    rights = output_rights(rows, game)
    # Two lists, because the owner asked for two: everybody's nine, which one
    # age-3 advance unlocks, and the country-specific ones. What makes the split
    # data rather than opinion is `unlock_town_rights` -- a right the general
    # advance names is general and anything else is not.
    kinds = {"common": [r for r in rights if r.general],
             "unique": [r for r in rights if not r.general]}
    index_of_right = {r.key: i for i, r in enumerate(rights, start=1)}
    order = [good for kind in ("raw", "made") for good in split[kind]]
    index_of = {good: i for i, good in enumerate(order, start=1)}
    by_good_index: dict[str, list[int]] = {}
    for i, method in enumerate(rows, start=1):
        by_good_index.setdefault(method.produced, []).append(i)
    slots = range(1, RIGHT_SLOTS + 1)

    out = [HEADER, """#
# Two lists rather than one: the nine an age-3 advance gives everybody, and the
# handful that belong to one country or culture. Ticking either is one answer,
# the way the two goods lists are.
"""]
    for kind, group in kinds.items():
        out.append(f"""
# Scope: country
{MOD_ID}_register_right_{kind}_list = {{
\tcmm_register_settings_list = {{
\t\tmod_id = {MOD_ID}
\t\tsetting_id = right_{kind}
\t\ttab_id = {TAB_GOODS}
\t\titem_count = {max(len(group), 1)}
\t\tis_ordered = 0
\t}}

""")
        for row, right in enumerate(group, start=1):
            out.append(f"\tcmm_set_list_item_value = {{ mod_id = {MOD_ID} "
                       f"setting_id = right_{kind} item = {row} "
                       f"value = town_rights_type:{right.key} }}\n")
        out.append("\n")
        for row, right in enumerate(group, start=1):
            out.append(f"\tset_variable = {{ name = {MOD_ID}__right_{kind}_i{row}_name "
                       f"value = flag:{MOD_ID}_right_{right.key} }}\n")
        out.append(f"""
\tcmm_register_list_bool_field = {{
\t\tmod_id = {MOD_ID}
\t\tsetting_id = right_{kind}
\t\tfield_id = pick
\t\tdefault_value = 0
\t}}
}}
""")
    out.append(f"""

# Which right is ticked, settled exactly as the good is: a tick that is not the
# stored answer is the new answer, and nothing ticked at all means the player
# unticked the one that was.
# Scope: country
{MOD_ID}_read_right = {{
\tset_variable = {{ name = {MOD_ID}_right_new value = 0 }}
\tset_variable = {{ name = {MOD_ID}_right_ticks value = 0 }}
""")
    for kind, group in kinds.items():
        out.append(f"""\tcmm_build_list_bool_list = {{ setting = {MOD_ID}__right_{kind} field_slot = 1 list_name = {MOD_ID}_right_ticked }}
\tevery_in_list = {{
\t\tvariable = {MOD_ID}_right_ticked
\t\troot = {{ change_variable = {{ name = {MOD_ID}_right_ticks add = 1 }} }}
""")
        for right in group:
            index = index_of_right[right.key]
            out.append(f"\t\tif = {{ limit = {{ this = town_rights_type:{right.key} }} root = {{ "
                       f"if = {{ limit = {{ NOT = {{ var:{MOD_ID}_right_index = {index} }} }} "
                       f"set_variable = {{ name = {MOD_ID}_right_new value = {index} }} }} }} }}\n")
        out.append("\t}\n")
    out.append(f"""

\tif = {{
\t\tlimit = {{ var:{MOD_ID}_right_new > 0 }}
\t\tset_variable = {{ name = {MOD_ID}_right_index value = var:{MOD_ID}_right_new }}
\t}}
\telse_if = {{
\t\tlimit = {{ var:{MOD_ID}_right_ticks = 0 }}
\t\tset_variable = {{ name = {MOD_ID}_right_index value = 0 }}
\t}}

\t# Readable from a location's own scope, where a country variable is not.
\tset_global_variable = {{ name = {MOD_ID}_right_index value = var:{MOD_ID}_right_index }}
}}

# Force every row but the answer off.
# Scope: country
{MOD_ID}_only_one_right = {{
""")
    for kind, group in kinds.items():
        for row, right in enumerate(group, start=1):
            out.append(f"""\tif = {{
\t\tlimit = {{ NOT = {{ var:{MOD_ID}_right_index = {index_of_right[right.key]} }} }}
\t\tcmm_set_list_data_value = {{ mod_id = {MOD_ID} setting_id = right_{kind} field_id = pick item = {row} value = 0 }}
\t}}
""")
    out.append("}\n")

    out.append(f"""
# What this country is offered.
#
# The nine general ones stay on the page whatever the age: they are everybody's,
# one advance away, and this mod is for planning ahead -- hiding them until age
# three would leave an empty list where the answer belongs. **A unique right is
# another matter.** Wallachia has no business being shown Constantinople's silk
# monopoly, and the game already says so: the monopoly carries
# `potential = {{ OR = {{ has_or_had_tag = BYZ has_or_had_tag = ROM }} }}` and the
# Scandinavian privileges carry an advance nobody else takes. Both are asked
# here, and neither is this mod's opinion about who owns what.
# Scope: country
{MOD_ID}_refresh_rights = {{
""")
    for kind, group in kinds.items():
        for row, right in enumerate(group, start=1):
            # `potential` only, and never the unlocking advance. Whether a
            # right *could ever* be yours is a fact about the country -- a tag,
            # a religion -- and hiding one because you have not taken its
            # advance yet is hiding the plan from the planner, the same mistake
            # the goods list made until the eighteenth run.
            shown = ("always = yes" if not right.potential
                     else "AND = { %s }" % right.potential)
            out.append(f"""\tif = {{
\t\tlimit = {{ {shown} }}
\t\tcmm_show_list_item = {{ mod_id = {MOD_ID} setting_id = right_{kind} item = {row} }}
\t}}
\telse = {{
\t\tcmm_hide_list_item = {{ mod_id = {MOD_ID} setting_id = right_{kind} item = {row} }}
\t}}
""")
    out.append("}\n")

    # ---- the pass -------------------------------------------------------
    out.append(f"""
# Score every candidate for the ticked right.
# Scope: country
{MOD_ID}_score_right = {{
""")
    for index in range(1, len(rights) + 1):
        keyword = "if" if index == 1 else "else_if"
        out.append(f"\t{keyword} = {{ limit = {{ var:{MOD_ID}_right_index = {index} }} "
                   f"{MOD_ID}_score_right_{index} = yes }}\n")
    out.append("}\n")

    for index, right in enumerate(rights, start=1):
        bundle = sorted(right.output)
        pretty = ", ".join("%s +%g%%" % (g, right.output[g] * 100) for g in bundle)
        out.append(f"""
# {right.key} -- {pretty}
# Scope: country
{MOD_ID}_score_right_{index} = {{
\tsave_scope_as = {MOD_ID}_country
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\tset_variable = {{ name = {MOD_ID}_r_total value = 0 }}
\t\tset_variable = {{ name = {MOD_ID}_r_mid_total value = 0 }}
""")
        for k in slots:
            out.append(f"\t\tset_variable = {{ name = {MOD_ID}_r_method_{k} value = 0 }}\n")
        out.append("\t}\n")

        for k, good in enumerate(bundle, start=1):
            weight = (game.prices.get(good, 1.0) * (1 + right.output[good])
                      * RIGHT_SCALE / RANK_SCALE)
            out.append(f"""
\t# {good}: price {game.prices.get(good, 1.0):g} x (1 + {right.output[good]:g})
\t{MOD_ID}_score_{index_of[good]} = yes
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\t# **A right obeys the same two buttons as a good.** «Считать» reads the
\t\t# answer available today, «На конец» the one that survives every advance.
\t\t# The twenty-second run pressed the second and got the first, because this
\t\t# read `_best_method` and nothing else.
\t\t#
\t\t# The fallbacks are the same too: a slot the ground feeds nothing keeps its
\t\t# building and its icon and says 0.00%, and `_val` stays 0, so it is worth
\t\t# nothing to the ranking and a row of nothing but those still goes.
\t\tif = {{
\t\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_rank_by_end }} }}
			set_variable = {{ name = {MOD_ID}_r_method_{k} value = var:{MOD_ID}_best_method }}
			set_variable = {{ name = {MOD_ID}_r_val_{k} value = var:{MOD_ID}_best }}
			if = {{
				limit = {{ var:{MOD_ID}_best_rural > var:{MOD_ID}_best }}
				set_variable = {{ name = {MOD_ID}_r_method_{k} value = var:{MOD_ID}_best_method_rural }}
				set_variable = {{ name = {MOD_ID}_r_val_{k} value = var:{MOD_ID}_best_rural }}
			}}
			if = {{
				limit = {{ var:{MOD_ID}_r_method_{k} = 0 }}
				set_variable = {{ name = {MOD_ID}_r_method_{k} value = var:{MOD_ID}_any_best_method }}
			}}
			if = {{
				limit = {{ var:{MOD_ID}_r_method_{k} = 0 }}
				set_variable = {{ name = {MOD_ID}_r_method_{k} value = var:{MOD_ID}_any_best_method_rural }}
			}}
\t\t}}
\t\telse = {{
			set_variable = {{ name = {MOD_ID}_r_method_{k} value = var:{MOD_ID}_end_best_method }}
			set_variable = {{ name = {MOD_ID}_r_val_{k} value = var:{MOD_ID}_end_best }}
			if = {{
				limit = {{ var:{MOD_ID}_end_best_rural > var:{MOD_ID}_end_best }}
				set_variable = {{ name = {MOD_ID}_r_method_{k} value = var:{MOD_ID}_end_best_method_rural }}
				set_variable = {{ name = {MOD_ID}_r_val_{k} value = var:{MOD_ID}_end_best_rural }}
			}}
			if = {{
				limit = {{ var:{MOD_ID}_r_method_{k} = 0 }}
				set_variable = {{ name = {MOD_ID}_r_method_{k} value = var:{MOD_ID}_end_any_best_method }}
			}}
			if = {{
				limit = {{ var:{MOD_ID}_r_method_{k} = 0 }}
				set_variable = {{ name = {MOD_ID}_r_method_{k} value = var:{MOD_ID}_end_any_best_method_rural }}
			}}
\t\t}}
\t\t# And the road there, summed the same way. It only ever breaks a tie, and
\t\t# the ties it breaks are the ones «На конец» leaves: where nothing that
\t\t# survives can be fed, every province in the table is worth exactly zero.
\t\tset_variable = {{ name = {MOD_ID}_r_mid_{k} value = var:{MOD_ID}_mid_best }}
\t\tif = {{
\t\t\tlimit = {{ var:{MOD_ID}_mid_best_rural > var:{MOD_ID}_mid_best }}
\t\t\tset_variable = {{ name = {MOD_ID}_r_mid_{k} value = var:{MOD_ID}_mid_best_rural }}
\t\t}}
\t\tchange_variable = {{ name = {MOD_ID}_r_mid_{k} multiply = {weight:.4f} }}
\t\tchange_variable = {{ name = {MOD_ID}_r_mid_total add = var:{MOD_ID}_r_mid_{k} }}
\t\tchange_variable = {{ name = {MOD_ID}_r_val_{k} multiply = {weight:.4f} }}
\t\tchange_variable = {{ name = {MOD_ID}_r_total add = var:{MOD_ID}_r_val_{k} }}
\t}}
""")
        out.append("}\n")

    # ---- resolving one winning method into what a row prints ------------
    out.append(f"""
# One method, read out of `{MOD_ID}_w_method` into scratch. A dispatch over every
# method in the game is too wide to run per candidate, so it runs only for the
# provinces that took a row -- fifty of them, three slots each.
# Scope: location
{MOD_ID}_store_scratch = {{
\tclear_variable_list = {MOD_ID}_w_goods
\tremove_variable = {MOD_ID}_w_bt
\tremove_variable = {MOD_ID}_w_pm
\tset_variable = {{ name = {MOD_ID}_w_bonus value = 0 }}
\tset_variable = {{ name = {MOD_ID}_w_out value = 0 }}
\tset_variable = {{ name = {MOD_ID}_w_goods_all value = 0 }}
""")
    for i, method in enumerate(rows, start=1):
        raw = sorted(method.raw_inputs(game.raw_goods))
        out.append(f"\tif = {{\n"
                   f"\t\tlimit = {{ var:{MOD_ID}_w_method = {i} }}\n"
                   f"\t\tset_variable = {{ name = {MOD_ID}_w_bt value = building_type:{method.building} }}\n"
                   f"\t\tset_variable = {{ name = {MOD_ID}_w_pm value = production_method:{method.parts[0].key} }}\n"
                   f"\t\tset_variable = {{ name = {MOD_ID}_w_bonus value = {MOD_ID}_b{i} }}\n"
                   f"\t\tset_variable = {{ name = {MOD_ID}_w_out value = {method.output:.4f} }}\n"
                   f"\t\tset_variable = {{ name = {MOD_ID}_w_goods_all value = {len(raw)} }}\n")
        for good in raw:
            out.append(f"""\t\tif = {{
\t\t\tlimit = {{ province_definition = {{ any_location_in_province_definition = {{ raw_material = goods:{good} }} }} }}
\t\t\tadd_to_variable_list = {{ name = {MOD_ID}_w_goods target = goods:{good} }}
\t\t}}
""")
        out.append("\t}\n")
    out.append("}\n")

    for k in slots:
        out.append(f"""
# Scratch into slot {k}.
# Scope: location
{MOD_ID}_slot_{k}_from_scratch = {{
\tclear_variable_list = {MOD_ID}_r_goods_{k}
\tremove_variable = {MOD_ID}_r_bt_{k}
\tremove_variable = {MOD_ID}_r_pm_{k}
\tset_variable = {{ name = {MOD_ID}_r_bonus_{k} value = 0 }}
\tset_variable = {{ name = {MOD_ID}_r_out_{k} value = 0 }}
\tset_variable = {{ name = {MOD_ID}_r_goods_all_{k} value = 0 }}
\tif = {{
\t\tlimit = {{ has_variable = {MOD_ID}_w_bt }}
\t\tset_variable = {{ name = {MOD_ID}_r_bt_{k} value = var:{MOD_ID}_w_bt }}
\t\tset_variable = {{ name = {MOD_ID}_r_pm_{k} value = var:{MOD_ID}_w_pm }}
\t\tset_variable = {{ name = {MOD_ID}_r_bonus_{k} value = var:{MOD_ID}_w_bonus }}
\t\tset_variable = {{ name = {MOD_ID}_r_out_{k} value = var:{MOD_ID}_w_out }}
\t\tset_variable = {{ name = {MOD_ID}_r_goods_all_{k} value = var:{MOD_ID}_w_goods_all }}
\t\tevery_in_list = {{
\t\t\tvariable = {MOD_ID}_w_goods
\t\t\tprev = {{ add_to_variable_list = {{ name = {MOD_ID}_r_goods_{k} target = prev }} }}
\t\t}}
\t}}
}}
""")

    # Which good sits in which slot, per right -- the row prints its name.
    out.append(f"""
# The goods of the ticked right, parked on the winning location so the row can
# name them. Written per row rather than per candidate, like everything else
# here.
# Scope: location
{MOD_ID}_store_right_goods = {{
""")
    for index, right in enumerate(rights, start=1):
        bundle = sorted(right.output)
        out.append(f"\tif = {{\n\t\tlimit = {{ global_var:{MOD_ID}_right_index = {index} }}\n")
        for k in slots:
            if k <= len(bundle):
                out.append(f"\t\tset_variable = {{ name = {MOD_ID}_r_good_{k} value = goods:{bundle[k - 1]} }}\n")
            else:
                out.append(f"\t\tremove_variable = {MOD_ID}_r_good_{k}\n")
        out.append("\t}\n")
    out.append("}\n")

    out.append(f"""
# Park the whole answer for one province, slot by slot.
# Scope: location
{MOD_ID}_store_right_row = {{
""")
    for k in slots:
        out.append(f"""\tset_variable = {{ name = {MOD_ID}_w_method value = var:{MOD_ID}_r_method_{k} }}
\t{MOD_ID}_store_scratch = yes
\t{MOD_ID}_slot_{k}_from_scratch = yes
""")
    out.append(f"""\t{MOD_ID}_store_right_goods = yes
\t# What the row prints: the ranking number back in the unit it names, which is
\t# what one level of the whole bundle would earn here.
\tset_variable = {{ name = {MOD_ID}_r_value value = var:{MOD_ID}_r_total }}
\tchange_variable = {{ name = {MOD_ID}_r_value divide = {RIGHT_SCALE} }}
}}

# The ranking pass for a right. One row per province definition, as for a good,
# and the same fifty.
# Scope: country
{MOD_ID}_fill_rows_right = {{
\tordered_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\torder_by = {MOD_ID}_r_score
\t\tmax = {RESULT_ROWS * 8}
\t\tcheck_range_bounds = no
\t\t{MOD_ID}_store_right_row_if_worth_it = yes
\t}}
}}

# Scope: location
{MOD_ID}_store_right_row_if_worth_it = {{
\tif = {{
\t\tlimit = {{
\t\t\tglobal_var:{MOD_ID}_found < {RESULT_ROWS}
\t\t\t# Nothing in the bundle can be made here at all.
\t\t\tvar:{MOD_ID}_r_total > 0
\t\t\tNOT = {{ has_variable = {MOD_ID}_row_taken }}
\t\t}}
\t\tprovince_definition = {{
\t\t\tevery_location_in_province_definition = {{
\t\t\t\tset_variable = {{ name = {MOD_ID}_row_taken value = 1 }}
\t\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_row_taken_locations target = this }}
\t\t\t}}
\t\t}}
\t\t# The winners are parked before the province is judged: «is this ground
\t\t# worth a row» is a question about the bonuses, and a bonus is not known
\t\t# until the method that won it is.
\t\t{MOD_ID}_store_right_row = yes
\t\tif = {{
\t\t\tlimit = {{ {MOD_ID}_right_row_is_worth_it = yes }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_found add = 1 }}
\t\t\tset_variable = {{ name = {MOD_ID}_rank value = global_var:{MOD_ID}_found }}
\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_ranked target = this }}
\t\t}}
\t}}
}}
""")
    return "".join(out)


def list_settings(by_continent) -> list[tuple[str, str, str]]:
    """Every list this mod registers: its tab, its id, and what a tick in it runs.

    One table, two readers -- the `_on_changed` callbacks and the collapse pass
    below both have to name every list, and a list named in one and not the
    other is the kind of omission nothing reports.
    """
    return ([("zone", f"region_{c}", f"{MOD_ID}_zone_changed = yes") for c in by_continent]
            + [("zone", "continent", f"{MOD_ID}_zone_changed = yes"),
               ("goods", "good_raw", f"{MOD_ID}_good_changed = yes"),
               ("goods", "good_made", f"{MOD_ID}_good_changed = yes"),
               ("goods", "right_common", f"{MOD_ID}_right_changed = yes"),
               ("goods", "right_unique", f"{MOD_ID}_right_changed = yes")])


def layout_file(by_continent) -> str:
    """The pickers, folded shut the first time the mod page is built.

    Seven region lists and two goods lists, all open, is a page the owner scrolls
    through to reach anything -- and the answer he wants is two ticks in it.
    CMM keeps a group's folded state in `cmm_group_collapsed`, a variable map on
    the player keyed by `<mod>__<tab>__<group>`, and a list is filed under a
    group named after itself, so the key is knowable from here. `_on_changed`'s
    table is the same table, which is why both read `list_settings`.

    **This writes into CMF's own data, which no macro covers.** The map is
    documented in `cmm_settings_pane.gui` as what the header button toggles, and
    CMM_ToggleGroupCollapsed writes it exactly this way; it is a contract with a
    comment rather than with a macro, and a CMF that renames it would leave the
    groups open rather than break anything.

    Once, and then never again: `bag_wtp_folded_once` is what makes it a default
    rather than a decision retaken at every save load.
    """
    out = [HEADER, f"""#
# Scope: country
{MOD_ID}_fold_pickers = {{
\tif = {{
\t\tlimit = {{ NOT = {{ has_variable = {MOD_ID}_folded_once }} }}
\t\tset_variable = {{ name = {MOD_ID}_folded_once value = 1 }}
"""]
    for tab, setting, _ in list_settings(by_continent):
        out.append(f"\t\tadd_to_variable_map = {{ name = cmm_group_collapsed "
                   f"key = flag:{MOD_ID}__{tab}__{setting} value = 1 }}\n")
    out.append("\t}\n}\n")
    return "".join(out)


def guis_file(by_continent) -> str:
    """One `_on_changed` per list, and they are not optional.

    Registering a list marks the setting as having a scripted GUI, and CMM then
    draws the row only while `CMMGuiIsShown('<setting>_on_changed')`. Without one
    the whole widget is hidden, header included -- and because a list is filed
    under a group named after itself, the group header still renders, so a
    missing callback looks like an empty list rather than a missing one.
    """
    out = [HEADER, """#
# A list reaches nothing but its own `_on_changed`: bool, dropdown, numeric,
# slider and button settings auto-apply and reach `cmf_on_callback`, and a list
# reaches neither until `cmm_apply_list_change` is called here.
"""]
    for _, setting, after in list_settings(by_continent):
        body = f"\t\t{after}\n" if after else ""
        out.append(f"""
{MOD_ID}__{setting}_on_changed = {{
\tscope = country

\tis_shown = {{
\t\talways = yes
\t}}

\teffect = {{
\t\tcmm_apply_list_change = {{
\t\t\tsetting = {MOD_ID}__{setting}
\t\t}}
{body}\t}}
}}
""")
    return "".join(out)


def loc_file(language: str, rows: list[eu5data.Method], split: dict[str, list[str]],
             game: eu5data.Game) -> str:
    """The generated keys, identical in every language.

    Every name in here is the game's own, reached through `$key$` substitution or
    a data function, so this file needs no translating and cannot drift from what
    the game calls things.

    The fifty result-row keys are gone with the table they labelled: the window
    reads its row off the location's own scope and needs no key per row.
    """
    out = [f"l_{language}:\n"]

    for kind in ("raw", "made"):
        for good in split[kind]:
            out.append(f" {MOD_ID}_good_{good}: "
                       f'"@{good}! [ShowGoodsName(\'{good}\')]"\n')

    # A right is named by the game and iconed by the first good it favours, so
    # this needs no translating either.
    for right in output_rights(rows, game):
        icon = sorted(right.output)[0]
        out.append(f" {MOD_ID}_right_{right.key}: "
                   f'"@{icon}! [ShowTownRightsName(\'{right.key}\')]"\n')

    return "".join(out)


# ---------------------------------------------------------------- the diagnosis

def diag_file(rows: list[eu5data.Method], split: dict[str, list[str]],
              game: eu5data.Game) -> str:
    """«Диагностика»: one press, everything the mod knows, as text in the log.

    **This is an instrument, not a fix.** Four of the owner's runs went on four
    theories about one symptom and none of them on a measurement
    (`docs/pitfalls/diagnosis.md`); the rule that came out of it is that a cause
    nobody can name is measured rather than guessed. So this reads state and
    writes none of the plan's own, and every number it prints is uncompressed:
    a screenshot has to be read off pixels and a column has one cell, but text
    has no width.

    **It costs the plan nothing.** Everything except the per-pass counters is
    read back afterwards from what the plan parked on the locations, so the
    expensive button is exactly as expensive as it was and this one is pressed
    when there is something to look at.

    Four things about `debug_log` were measured on 2026-09-02 and all four shape
    this file:

    - `debug_log` writes on a normal build. So does `error_log`; the headline
      goes to both and the detail to `debug.log` alone, which halves a dump that
      the owner has to paste into a chat.
    - a global is reachable from the string, as
      `[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('<sv>')|0]`;
    - **the item a walk is standing on is not reachable at all** -- `THIS.MakeScope`
      fails and the bracket is echoed literally -- so every number is parked in
      one of fourteen scratch globals first and printed from there, and
      `debug_log_scopes` names the row;
    - and a script value of the form `value = 0` with `if = { ... add = ... }`
      reads zero in silence. Every reader here is `value = global_var:x` and
      every guard is in an effect, where `if` demonstrably works.
    """
    order = [good for kind in ("raw", "made") for good in split[kind]]
    kinds = {good: kind for kind in ("raw", "made") for good in split[kind]}
    groups = plan_groups(rows, split, game)
    last = endgame(rows, game)
    rights = output_rights(rows, game)

    def read(slot: int) -> str:
        """One number, as the string sees it."""
        return f"[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('{MOD_ID}_dg{slot}')|0]"

    def park(slot: int, source: str, scope: str = "global", tab: str = "\t") -> str:
        """Copy a number into a scratch global, or leave 0 where there is none.

        The guard is an `if` in an effect and not a fallback inside a script
        value: the value form that guards itself reads zero in silence, which is
        how the first dump reported nothing on a plan that had placed 417
        buildings.
        """
        has = {"global": f"has_global_variable = {source}",
               "var": f"has_variable = {source}"}[scope]
        get = {"global": f"global_var:{source}", "var": f"var:{source}"}[scope]
        return (f"{tab}set_global_variable = {{ name = {MOD_ID}_dv{slot} value = 0 }}\n"
                f"{tab}if = {{ limit = {{ {has} }} "
                f"set_global_variable = {{ name = {MOD_ID}_dv{slot} value = {get} }} }}\n")

    def flag(slot: int, trigger: str, tab: str = "\t") -> str:
        """1 or 0 for something that is a condition rather than a number."""
        return (f"{tab}set_global_variable = {{ name = {MOD_ID}_dv{slot} value = 0 }}\n"
                f"{tab}if = {{ limit = {{ {trigger} }} "
                f"set_global_variable = {{ name = {MOD_ID}_dv{slot} value = 1 }} }}\n")

    def say(text: str, both: bool = False, tab: str = "\t") -> str:
        """One line into the log. The headline goes to both sinks; detail to one.

        A dump sent as `error.log` alone still says which build wrote it and what
        the totals were, so a missing `debug.log` is never mistaken for a plan
        that did nothing.
        """
        line = f'{tab}debug_log = "WTP {text}"\n'
        if both:
            line += f'{tab}error_log = "WTP {text}"\n'
        return line

    out = [f"""#
# «Диагностика» -- one press, everything the mod knows, as text.
#
# Generated. What it prints and why each block is here:
# `docs/pitfalls/diagnosis.md`. **No `[THIS...]` anywhere below**: a `debug_log`
# string cannot reach the item a walk stands on. Numbers come from the sixteen
# `_dv` scratch globals through the `_dg` readers; names are baked in here.
#
# Scope: country
{MOD_ID}_diag = {{
"""]
    out.append("".join(f"\tset_global_variable = {{ name = {MOD_ID}_dv{i} value = 0 }}\n"
                       for i in range(1, DIAG_SCRATCH + 1)))
    # **Кнопка должна сама сказать, что она сработала.** 2026-09-02: он нажал её
    # и не увидел ничего -- отчёт ушёл в лог, а на экране не изменилось ничто, и
    # это неотличимо от кнопки, которая не работает. Счётчик нажатий и итоги
    # сбора печатаются в её собственном описании, тем же способом, каким это
    # делают «Считать» и «План».
    out.append(f"\tif = {{ limit = {{ NOT = {{ has_global_variable = {MOD_ID}_diag_runs }} }} "
               f"set_global_variable = {{ name = {MOD_ID}_diag_runs value = 0 }} }}\n")
    out.append(f"\tchange_global_variable = {{ name = {MOD_ID}_diag_runs add = 1 }}\n")
    out.append("\tdebug_log_date = yes\n")
    out.append(say(f"==== BEGIN v{DIAG_VERSION} ==== everything below to the next END "
                   "is one press. debug.log has it whole; error.log has the headline.",
                   both=True))
    out.append(f"""\t{MOD_ID}_diag_build = yes
\t{MOD_ID}_diag_state = yes
\t{MOD_ID}_diag_scan = yes
\t{MOD_ID}_diag_goods = yes
\t{MOD_ID}_diag_passes = yes
\t{MOD_ID}_diag_rights = yes
\t{MOD_ID}_diag_locations = yes
\t{MOD_ID}_diag_ranking = yes
""")
    out.append(say(f"==== END v{DIAG_VERSION} ====", both=True))
    out.append("}\n")

    # ---------------------------------------------------------------- the build
    #
    # What the generator decided, so a number in the log is never read against
    # the wrong constant. All of it static: nothing here can go stale between
    # the rebuild and the run.
    rural = sum(1 for m in rows if m.building_category in RURAL_CATEGORIES)
    bands = "/".join(str(b) for b in PLAN_BANDS)
    tiers = "/".join(str(t) for t in PLAN_TIERS)
    out.append(f"""
# The generator's own numbers. Static, so that a reading is never checked
# against the wrong constant.
# Scope: country
{MOD_ID}_diag_build = {{
""")
    out.append(say(f"BUILD methods={len(rows)} rural={rural} goods={len(order)} "
                   f"raw={len(split['raw'])} made={len(split['made'])} "
                   f"rights={len(rights)} gated={len(UNLOCKS)}", both=True))
    out.append(say(f"BUILD rounds={PLAN_ROUNDS} passes={len(PLAN_PASSES)} bands={bands} "
                   f"tiers={tiers} rows={PLAN_ROWS} result_rows={RESULT_ROWS} "
                   f"unfed_penalty={UNFED_PENALTY} right_fit={RIGHT_FIT} "
                   f"rank_scale={RANK_SCALE} right_slots={RIGHT_SLOTS}", both=True))
    out.append(say("BUILD passes in order: "
                   + ", ".join(f"{i}={pass_name(band, tier)}"
                               for i, (band, tier) in enumerate(PLAN_PASSES, start=1))))
    # **The self-test, and it is here to be thrown away.** Three of these four
    # are guesses about what a `debug_log` string resolves, and one run settles
    # them for good -- which is cheaper than a session reasoning about it and
    # cheaper than a run spent on a dump that printed brackets. Whatever the log
    # says goes into `docs/research/engine.md` and the losers come out.
    out.append(f"\tset_global_variable = {{ name = {MOD_ID}_dv1 value = 12345 }}\n")
    out.append(say(f"SELFTEST 1 global-through-player={read(1)} (expect 12345; "
                   "anything else and every number below is wrong)", both=True))
    out.append(say("SELFTEST 2 loc-key-as-message: " + MOD_ID + "_diag_selftest "
                   "(expect the sentence that key holds, not the key)"))
    out.append(say("SELFTEST 3 root-name=[ROOT.GetName] scope-name=[SCOPE.GetName] "
                   "(expect the country twice, or two echoed brackets)"))
    out.append("\tdebug_log_scopes = no\n")
    out.append(say("SELFTEST 4 the line above this one should name the country "
                   "-- that is debug_log_scopes, and it is how every row below "
                   "says which location it is"))
    out.append("}\n")

    # ---------------------------------------------------------------- the state
    out.append(f"""
# Everything chosen and everything the last plan counted. **A zero here is an
# answer**: pressed before a plan it prints zeros throughout, which says the pass
# never ran rather than that it found nothing.
# Scope: country
{MOD_ID}_diag_state = {{
""")
    for slot, (name, source, scope) in enumerate((
            ("good", f"{MOD_ID}_good_index", "var"),
            ("right", f"{MOD_ID}_right_index", "var"),
            ("continents", f"{MOD_ID}_zone_count", "global"),
            ("regions", f"{MOD_ID}_region_count", "global"),
            ("picked", f"{MOD_ID}_picked_count", "global"),
            ("provinces_picked", f"{MOD_ID}_browse_count", "global"),
            ("candidates", f"{MOD_ID}_candidate_count", "global"),
            ("runs", f"{MOD_ID}_live_runs", "global")), start=1):
        out.append(park(slot, source, scope))
    out.append(say("PICK good=%s right=%s continents=%s regions=%s picked=%s "
                   "provinces_picked=%s candidates=%s runs=%s"
                   % tuple(read(i) for i in range(1, 9)), both=True))
    for slot, (name, source) in enumerate((
            ("cap_rural", f"{MOD_ID}_plan_cap_rural"),
            ("cap_urban", f"{MOD_ID}_plan_cap_urban"),
            ("max_per_good", f"{MOD_ID}_plan_max")), start=1):
        out.append(park(slot, source))
    out.append(flag(4, f"has_global_variable = {MOD_ID}_plan_rights"))
    out.append(flag(5, f"has_global_variable = {MOD_ID}_plan_by_end"))
    out.append(flag(6, f"has_global_variable = {MOD_ID}_rank_by_end"))
    out.append(flag(7, f"has_global_variable = {MOD_ID}_only_buildable"))
    out.append(say("SET cap_rural=%s cap_urban=%s max_per_good=%s rights=%s "
                   "plan_by_end=%s rank_by_end=%s buildable_only=%s"
                   % tuple(read(i) for i in range(1, 8)), both=True))
    for slot, source in enumerate((
            f"{MOD_ID}_plan_placed", f"{MOD_ID}_plan_rooms", f"{MOD_ID}_plan_found",
            f"{MOD_ID}_plan_shown", f"{MOD_ID}_plan_towns", f"{MOD_ID}_plan_provn",
            f"{MOD_ID}_plan_scored", f"{MOD_ID}_plan_quota", f"{MOD_ID}_plan_rightn",
            f"{MOD_ID}_plan_sweeps", f"{MOD_ID}_found"), start=1):
        out.append(park(slot, source))
    out.append(say("PASS placed=%s rooms=%s used_locs=%s drawn=%s towns=%s provs=%s "
                   "goods_scored=%s quota=%s rights_given=%s sweeps=%s ranked_provs=%s"
                   % tuple(read(i) for i in range(1, 12)), both=True))
    out.append("}\n")

    # ----------------------------------------------------------------- the scan
    #
    # **The funnel, read back off the map rather than counted during the pass.**
    # One walk over the locations the plan touched, and for each good on each
    # side four questions: did a method win here, would the placement gate open
    # here *now*, did this good end up here, and what is the best this good could
    # have been ordered at. The four together say which stage a good is lost at
    # and how many locations it was lost at -- and the gate read afterwards is
    # what separates «the ground filled up» from «the allocator never gave it a
    # turn», which reading it on empty ground cannot do.
    out.append(f"""
# The funnel. One walk, and the plan pays nothing for it: everything here is
# what the plan already parked on the locations.
#
# `w` a method won, `g` the gate would still open, `p` it was placed, `o` the
# best ordering it ever had -- against `{MOD_ID}_plan_band`, which is what a
# band admits. A good whose `o` never reaches 200 has only the last band.
# Scope: country
{MOD_ID}_diag_scan = {{
\tset_global_variable = {{ name = {MOD_ID}_diag_locs value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_diag_towns value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_diag_freet value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_diag_freer value = 0 }}
""")
    for index in range(1, len(order) + 1):
        for side in ("t", "r"):
            for what in ("w", "r", "g", "p", "o"):
                out.append(f"\tset_global_variable = {{ name = {MOD_ID}_f{what}{side}{index} value = 0 }}\n")
    out.append(f"""\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_touched
\t\tchange_global_variable = {{ name = {MOD_ID}_diag_locs add = 1 }}
\t\tif = {{
\t\t\tlimit = {{ {MOD_ID}_plan_is_town = yes }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_diag_towns add = 1 }}
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_load < global_var:{MOD_ID}_plan_cap_urban }}
\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_diag_freet add = 1 }}
""")
    # **`r` is what separates a full ground from a starved good**, and it is the
    # one distinction the gate cannot draw on its own: the gate is a conjunction,
    # so `g = 0` means "no room" and "already here" and "that building is taken"
    # at once. Counted inside the room test, so a location with no room costs
    # nothing.
    for index in range(1, len(order) + 1):
        out.append(f"\t\t\t\tif = {{ limit = {{ var:{MOD_ID}_pm{index} > 0 }} "
                   f"change_global_variable = {{ name = {MOD_ID}_frt{index} add = 1 }} }}\n")
    out.append("\t\t\t}\n")
    for index, good in enumerate(order, start=1):
        out.append(f"""\t\t\tif = {{ limit = {{ var:{MOD_ID}_pm{index} > 0 }} change_global_variable = {{ name = {MOD_ID}_fwt{index} add = 1 }} }}
\t\t\tif = {{ limit = {{ {MOD_ID}_plan_can_town_{index} = yes }} change_global_variable = {{ name = {MOD_ID}_fgt{index} add = 1 }} }}
\t\t\tif = {{ limit = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} }} change_global_variable = {{ name = {MOD_ID}_fpt{index} add = 1 }} }}
\t\t\tif = {{
\t\t\t\tlimit = {{ {MOD_ID}_ord{index} > global_var:{MOD_ID}_fot{index} }}
\t\t\t\tset_global_variable = {{ name = {MOD_ID}_fot{index} value = 0 }}
\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_fot{index} add = {MOD_ID}_ord{index} }}
\t\t\t}}
""")
    out.append(f"""\t\t}}
\t\telse = {{
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_load < global_var:{MOD_ID}_plan_cap_rural }}
\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_diag_freer add = 1 }}
""")
    for index in range(1, len(order) + 1):
        out.append(f"\t\t\t\tif = {{ limit = {{ var:{MOD_ID}_prm{index} > 0 }} "
                   f"change_global_variable = {{ name = {MOD_ID}_frr{index} add = 1 }} }}\n")
    out.append("\t\t\t}\n")
    for index, good in enumerate(order, start=1):
        out.append(f"""\t\t\tif = {{ limit = {{ var:{MOD_ID}_prm{index} > 0 }} change_global_variable = {{ name = {MOD_ID}_fwr{index} add = 1 }} }}
\t\t\tif = {{ limit = {{ {MOD_ID}_plan_can_rural_{index} = yes }} change_global_variable = {{ name = {MOD_ID}_fgr{index} add = 1 }} }}
\t\t\tif = {{ limit = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} }} change_global_variable = {{ name = {MOD_ID}_fpr{index} add = 1 }} }}
\t\t\tif = {{
\t\t\t\tlimit = {{ {MOD_ID}_ordr{index} > global_var:{MOD_ID}_for{index} }}
\t\t\t\tset_global_variable = {{ name = {MOD_ID}_for{index} value = 0 }}
\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_for{index} add = {MOD_ID}_ordr{index} }}
\t\t\t}}
""")
    out.append("\t\t}\n\t}\n}\n")

    # ---------------------------------------------------------------- the goods
    out.append(f"""
# One line per good, town and village apart, every counter uncompressed. The
# ladder is m -> a -> w -> g/p: the first zero is the stage the good is lost at,
# and the number before it is how many locations got that far.
# Scope: country
{MOD_ID}_diag_goods = {{
""")
    out.append(say("GOODS legend: T=town R=village | m=methods(of them last-age) "
                   "a=country has the advance w=a method won here r=of those, "
                   "still has room g=the gate would still open p=placed "
                   "o=best ordering it ever had (a band admits >= its own number) "
                   "| ng=candidates that can make it q=quota n=placed both sides "
                   "rgo=locations already yielding it as an RGO"))
    out.append(say("GOODS reading it: the first zero left to right is the stage. "
                   "w>0 r=0 -- the ground filled up. w>0 r>0 g=0 -- the good or "
                   "its building is already in every place that has room. "
                   "g>0 p=0 -- the allocator never gave it a turn, so look at "
                   "q, ng against the tiers, and o against the bands."))
    for index in range(1, len(order) + 1):
        out.append(f"\t{MOD_ID}_diag_good_{index} = yes\n")
    out.append(f"""\t{MOD_ID}_diag_free = yes
}}

# Room left over when the plan stopped, which is what tells a starved good from
# a full ground.
# Scope: country
{MOD_ID}_diag_free = {{
""")
    for slot, source in enumerate((f"{MOD_ID}_diag_locs", f"{MOD_ID}_diag_towns",
                                   f"{MOD_ID}_diag_freet", f"{MOD_ID}_diag_freer"), start=1):
        out.append(park(slot, source))
    out.append(say("ROOM walked=%s towns=%s towns_with_room=%s villages_with_room=%s"
                   % tuple(read(i) for i in range(1, 5)), both=True))
    out.append("}\n")

    for index, good in enumerate(order, start=1):
        town = [i for methods_ in groups.get((good, "t"), {}).values() for i in methods_]
        village = [i for methods_ in groups.get((good, "r"), {}).values() for i in methods_]
        town_end = sum(1 for i in town if i in last)
        village_end = sum(1 for i in village if i in last)
        out.append(f"""
# Scope: country
{MOD_ID}_diag_good_{index} = {{
""")
        for slot, source in ((1, f"{MOD_ID}_fwt{index}"), (2, f"{MOD_ID}_fgt{index}"),
                             (3, f"{MOD_ID}_fpt{index}"), (4, f"{MOD_ID}_fot{index}"),
                             (5, f"{MOD_ID}_fwr{index}"), (6, f"{MOD_ID}_fgr{index}"),
                             (7, f"{MOD_ID}_fpr{index}"), (8, f"{MOD_ID}_for{index}"),
                             (9, f"{MOD_ID}_ng{index}"), (10, f"{MOD_ID}_pq{index}"),
                             (11, f"{MOD_ID}_pn{index}"), (12, f"{MOD_ID}_nrgo{index}"),
                             (15, f"{MOD_ID}_frt{index}"), (16, f"{MOD_ID}_frr{index}")):
            out.append(park(slot, source))
        # Availability is the country's advance and not the location's ground:
        # `can_build_building` asked here answers the advance, asked in a
        # location it answers the rank and the terrain. Two different questions
        # and the first dump conflated them, which put three goods the country
        # had not unlocked in the column that means "our scoring dropped it".
        for slot, side in ((13, town), (14, village)):
            if side:
                condition = " ".join(f"{MOD_ID}_avail_{i} = yes" for i in sorted(set(side)))
                out.append(flag(slot, f"OR = {{ {condition} }}"))
            else:
                out.append(f"\tset_global_variable = {{ name = {MOD_ID}_dv{slot} value = 0 }}\n")
        out.append(say(f"G{index} {good} {kinds[good]} "
                       f"| T m={len(town)}({town_end}) a={read(13)} w={read(1)} "
                       f"r={read(15)} g={read(2)} p={read(3)} o={read(4)} "
                       f"| R m={len(village)}({village_end}) a={read(14)} w={read(5)} "
                       f"r={read(16)} g={read(6)} p={read(7)} o={read(8)} "
                       f"| ng={read(9)} q={read(10)} n={read(11)} rgo={read(12)}"))
        out.append("}\n")

    # --------------------------------------------------------------- the passes
    #
    # **The one thing the dump cannot read back afterwards.** A pass that ran out
    # of sweeps with work still to do leaves nothing behind on the map; the two
    # counters per pass in `_plan_allocate` are what make it visible, and they
    # cost two writes each.
    out.append(f"""
# What each pass of the allocator did. `sweeps={PLAN_ROUNDS}` is a pass the guard
# cut off -- it wanted more rounds and was not given them -- and `placed` is the
# running total at the end of that pass, so the difference between two lines is
# what the second one put down.
# Scope: country
{MOD_ID}_diag_passes = {{
""")
    for number, (band, tier) in enumerate(PLAN_PASSES, start=1):
        out.append(park(1, f"{MOD_ID}_passsw{number}"))
        out.append(park(2, f"{MOD_ID}_passpl{number}"))
        out.append(say(f"P{number} {pass_name(band, tier)} sweeps={read(1)}"
                       f"/{PLAN_ROUNDS} placed={read(2)}"))
    out.append("}\n")

    # --------------------------------------------------------------- the rights
    #
    # `_rgiven<k>` has counted how many towns each right took since the day
    # rights were added -- the plan divides a right's score by it -- and nothing
    # ever showed it. One charter holding most of the towns is a fault a level
    # above any single good's row, and that is the level the reported symptom
    # lives on.
    out.append(f"""
# How many towns each urban right was granted in, and what it grants. A charter
# in twenty-one towns whose second good is nowhere is a plan-level fault and not
# a good's.
# Scope: country
{MOD_ID}_diag_rights = {{
""")
    for number, right in enumerate(rights, start=1):
        goods = ", ".join(sorted(right.output))
        out.append(park(1, f"{MOD_ID}_rgiven{number}"))
        out.append(say(f"RIGHT {number} {right.key} [{goods}] given={read(1)}"))
    out.append("}\n")

    # ------------------------------------------------------------ the locations
    out.append(f"""
# One block per location the plan filled, best first. The line above each block
# is the location itself, from `debug_log_scopes`; the `LG` lines under it are
# what was put there, one good a line -- which is the whole of the reported
# symptom in the one place it can be read.
# Scope: country
{MOD_ID}_diag_locations = {{
\tset_global_variable = {{ name = {MOD_ID}_diag_n value = 0 }}
\tordered_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_ranked
\t\torder_by = {MOD_ID}_plan_rank_order
\t\tmax = {DIAG_LOCS}
\t\tcheck_range_bounds = no
\t\tchange_global_variable = {{ name = {MOD_ID}_diag_n add = 1 }}
""")
    for slot, source in ((1, f"{MOD_ID}_plan_rank"), (2, f"{MOD_ID}_load"),
                         (3, f"{MOD_ID}_plan_right"), (4, f"{MOD_ID}_plan_prank"),
                         (5, f"{MOD_ID}_plan_prov_load")):
        out.append(park(slot, source, "var", tab="\t\t"))
    out.append(flag(6, f"{MOD_ID}_plan_is_town = yes", tab="\t\t"))
    out.append("\t\tdebug_log_scopes = no\n")
    out.append(say(f"L rank={read(1)} town={read(6)} load={read(2)} right={read(3)} "
                   f"prov_rank={read(4)} prov_load={read(5)}", tab="\t\t"))
    for good in order:
        out.append(f"\t\tif = {{ limit = {{ is_target_in_variable_list = "
                   f"{{ name = {MOD_ID}_plan_goods target = goods:{good} }} }} "
                   f'debug_log = "WTP LG {good}" }}\n')
    out.append("\t}\n")
    out.append(park(1, f"{MOD_ID}_diag_n"))
    out.append(park(2, f"{MOD_ID}_plan_found"))
    out.append(say(f"LOCS printed={read(1)} of={read(2)} cap={DIAG_LOCS} "
                   "-- a cap is never silently the answer", both=True))
    out.append("}\n")

    # -------------------------------------------------------------- the ranking
    out.append(f"""
# The single-good ranking's own answer, for the case where the plan is right and
# the table it is read against is not. A row is a province definition.
# Scope: country
{MOD_ID}_diag_ranking = {{
\tset_global_variable = {{ name = {MOD_ID}_diag_n value = 0 }}
\tordered_in_global_list = {{
\t\tvariable = {MOD_ID}_ranked
\t\torder_by = {MOD_ID}_rank_order
\t\tmax = {DIAG_ROWS}
\t\tcheck_range_bounds = no
\t\tchange_global_variable = {{ name = {MOD_ID}_diag_n add = 1 }}
""")
    for slot, source in ((1, f"{MOD_ID}_rank"), (2, f"{MOD_ID}_bonus"),
                         (3, f"{MOD_ID}_out"), (4, f"{MOD_ID}_bonus_rural"),
                         (5, f"{MOD_ID}_out_rural"), (6, f"{MOD_ID}_end_bonus"),
                         (7, f"{MOD_ID}_end_out"), (8, f"{MOD_ID}_mid_bonus"),
                         (9, f"{MOD_ID}_mid_age")):
        out.append(park(slot, source, "var", tab="\t\t"))
    out.append("\t\tdebug_log_scopes = no\n")
    out.append(say(f"R rank={read(1)} now_town={read(2)}/{read(3)} "
                   f"now_village={read(4)}/{read(5)} end_town={read(6)}/{read(7)} "
                   f"mid={read(8)} mid_age={read(9)}", tab="\t\t"))
    out.append("\t}\n")
    out.append(park(1, f"{MOD_ID}_diag_n"))
    out.append(park(2, f"{MOD_ID}_found"))
    out.append(say(f"ROWS printed={read(1)} of={read(2)} cap={DIAG_ROWS}", both=True))
    out.append("}\n")
    return "".join(out)


def main() -> int:
    game = eu5data.load_game()
    rows = methods(game)
    split = goods_split(rows, game)

    by_continent = regions()
    write(ZONE_OUT, zone_file())
    write(REGION_OUT, region_file(by_continent))
    write(TRIGGERS_OUT, triggers_file(rows, split, game))
    write(PICKER_OUT, picker_file(split, rows))
    write(VALUES_OUT, values_file(rows, split, game))
    write(SCORE_OUT, score_file(rows, split, game))
    write(ROWS_OUT, rows_file())
    write(GUIS_OUT, guis_file(by_continent))
    write(LAYOUT_OUT, layout_file(by_continent))
    write(RIGHTS_OUT, rights_file(rows, split, game))
    write(PLAN_OUT, plan_file(rows, split, game))
    write(PLAN_TRIGGERS_OUT, plan_triggers_file(rows, split, game))
    write(PLAN_LOC_OUT, plan_loc_file(rows, game))
    write(DIAG_OUT, diag_file(rows, split, game))
    for language in LOC_LANGUAGES:
        write(Path(str(LOC_OUT) % (language, language)),
              loc_file(language, rows, split, game))

    print(f"{sum(len(v) for v in by_continent.values())} regions in "
          f"{len(by_continent)} lists, {len(UNLOCKS)} methods gated by an advance")
    rural = sum(1 for m in rows if m.building_category in RURAL_CATEGORIES)
    print(f"{len(rows)} methods scored, {rural} of them in a village, "
          f"{len(split['raw'])} raw + {len(split['made'])} made goods, "
          f"{len(CONTINENTS)} continents, {RESULT_ROWS} provinces ranked, "
          f"{len(output_rights(rows, game))} urban rights")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

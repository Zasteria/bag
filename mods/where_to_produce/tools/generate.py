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


def values_file(rows: list[eu5data.Method], game: eu5data.Game) -> str:
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

{MOD_ID}_show_regions = {{ value = global_var:{MOD_ID}_zone_count }}
{MOD_ID}_show_candidates = {{ value = global_var:{MOD_ID}_candidate_count }}
{MOD_ID}_show_found = {{ value = global_var:{MOD_ID}_found }}
{MOD_ID}_show_picked = {{ value = global_var:{MOD_ID}_picked_count }}
{MOD_ID}_show_browse = {{ value = global_var:{MOD_ID}_browse_count }}
{MOD_ID}_show_live = {{ value = global_var:{MOD_ID}_live_runs }}
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
    three keeps only methods whose raw materials this province supplies -- asked
    as `_try > <the method's unbonused output>`, a literal. Each also keeps an
    `_any_` twin without that floor, which nothing ranks on: a column has to
    print something, and "the mill you cannot feed, at 0.00%" is an answer where
    a blank cell is not.

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

    def keep(indent: str, prefix: str, suffix: str, method_index: int,
             floor: float | None) -> str:
        """Is this the best of its side so far, and can this ground feed it?

        `floor` is what `_m<n>` comes to where the province supplies none of the
        method's raw materials -- the output alone, unbonused. Anything above it
        means at least one input is worked here.

        Without it the eighteenth run's fine cloth answered with silk weavers at
        0.00% in provinces full of wool: 0.70 a level unfed beats 0.50 a level at
        the full ten percent, so the ranking preferred a recipe the ground cannot
        supply and buried every province that could have run the other one. The
        smallest step any raw material adds is 0.56 across all methods and 1.9 in
        the endgame set, both far above the fixed point, so this never turns on
        rounding.
        """
        fed = f"var:{MOD_ID}_try > {floor:.4f} " if floor is not None else ""
        return (f"""{indent}if = {{
{indent}\tlimit = {{ {fed}var:{MOD_ID}_try > var:{MOD_ID}_{prefix}best{suffix} }}
{indent}\tset_variable = {{ name = {MOD_ID}_{prefix}best{suffix} value = var:{MOD_ID}_try }}
{indent}\tset_variable = {{ name = {MOD_ID}_{prefix}best_method{suffix} value = {method_index} }}
{indent}}}
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

        for method_index in methods_for:
            suffix = "_rural" if method_index in rural else ""
            floor = rows[method_index - 1].output * RANK_SCALE
            out.append(f"\t\tset_variable = {{ name = {MOD_ID}_try value = {MOD_ID}_m{method_index} }}\n")
            # «По пути»: every age, so no gate at all.
            out.append(keep("\t\t", "mid_", suffix, method_index, floor))
            if method_index in last:
                out.append(keep("\t\t", "end_", suffix, method_index, floor))
                out.append(keep("\t\t", "end_any_", suffix, method_index, None))
            out.append(f"""\t\tif = {{
\t\t\tlimit = {{ scope:{MOD_ID}_country = {{ {MOD_ID}_avail_{method_index} = yes }} }}
""")
            out.append(keep("\t\t\t", "", suffix, method_index, floor))
            out.append(keep("\t\t\t", "any_", suffix, method_index, None))
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


def main() -> int:
    game = eu5data.load_game()
    rows = methods(game)
    split = goods_split(rows, game)

    by_continent = regions()
    write(ZONE_OUT, zone_file())
    write(REGION_OUT, region_file(by_continent))
    write(TRIGGERS_OUT, triggers_file(rows, split, game))
    write(PICKER_OUT, picker_file(split, rows))
    write(VALUES_OUT, values_file(rows, game))
    write(SCORE_OUT, score_file(rows, split, game))
    write(ROWS_OUT, rows_file())
    write(GUIS_OUT, guis_file(by_continent))
    write(LAYOUT_OUT, layout_file(by_continent))
    write(RIGHTS_OUT, rights_file(rows, split, game))
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

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
#
# **On a big ground the guard is what decides whether the plan finishes.** A
# sweep places at most one building per good per side, so 970 buildings over 32
# goods needs thirty sweeps at the very least; at 12 the thirty-eighth run was
# cut off with 342 of 1312 rooms still empty -- «мод не справился досчитать всё
# как надо». It costs nothing where a pass has no work, because the `while`
# leaves the moment a sweep adds nothing, so it is only ever paid where there is
# something left to place.
#
# **Raised from 50 to 150 on 2026-09-03, and the report is what asked for it.**
# On 416 locations `open800` and `open600` both came back `sweeps=50/50` -- the
# guard cutting a pass off with work still to do, which is the one fault in the
# allocator that leaves no other trace. What they could not place at a high band
# fell through to a lower one, which is precisely the thing the banded open
# ladder exists to prevent. A pass with no work still costs exactly one sweep, so
# nothing else in the plan pays for this.
PLAN_ROUNDS = 150
# **One page of the plan window, and not the size of the answer.** Only the
# datamodel decides what a scripted widget costs, so this is the number of rows
# drawn at once; `PLAN_RANKED` below is how many the plan keeps, and the page
# buttons walk them one page at a time. More than `RESULT_ROWS` because a
# plan's row is a location where a ranking's is a province -- the same ground is
# four to eight times the rows.
PLAN_ROWS = 150
# How many locations one plan ranks into pages. The ranked list is a global
# variable list and two variables on each location, which is cheap beside the
# pass that filled them -- the window's datamodel is the thing that costs, and it
# never holds more than one page. Northern Germany, the largest ground he has
# run, is 416 locations; this leaves room for several times that before anything
# is dropped, and the header says how many were kept against how many the plan
# used.
PLAN_RANKED = 1500
# And how many provinces are put in order for those rows. A location's row sorts
# on its province's place, so a province past this cap keeps the 9999 the reset
# gave it and its locations land at the end together rather than in the wrong
# place among the others.
PLAN_PROVS = 600

# The sweeps run in tiers, and a tier admits only goods that at most this many
# candidate locations could hold. **The scarce go first**: a good with one place
# in the whole ground takes it before a good with forty gets its second, which is
# the owner's «жёстко зарезервировать слоты».
#
# **These are the scarce rungs only, and 0 -- "everything" -- is no longer one of
# them.** It was, and the run of 2026-09-03 measured what that cost: with the
# ladder written `for band: for tier:` the tier rungs of every band together
# placed **three buildings out of sixty-nine**, and all the rest went to the
# `tierall` rung of band 800 -- because a scarce good's gain is usually low
# (`iron` best 0 of 1000 over the whole ground, `stone` 372) and a rung is only
# entered when the gain clears the band. So iron never reached a rung above band
# 0, and by the time band 0 came round the four locations in Westphalia that can
# hold a bog iron smelter had been common goods' for twenty-five passes.
# `docs/investigations/plan_gaps.md`, fault B.
PLAN_TIERS = (1, 2, 4, 8, 16)

# The gain a placement has to reach to be made in this pass, out of `RANK_SCALE`.
# Descending, and the last is 0 because a good the ground feeds nothing is still
# a good that has to be produced. Five rather than ten: a band costs a sweep over
# every tier, and the plan is already the expensive button.
PLAN_BANDS = (800, 600, 400, 200, 0)

# How many towns a charter may be dealt one at a time before the rest are dealt
# at once. The charter ladder raises its ceiling by one and runs every band at
# each height, which is what makes the counts come out level; the guard is there
# because the ceiling it climbs to is towns divided by charters, and a country
# with many towns and two charters would otherwise walk its ground a hundred
# times over. Westphalia -- 48 towns, 9 charters -- climbs to 6.
RIGHT_LEVELS = 12

# The passes after all of them, with the quota raised a layer a round rather
# than with a candidate count of their own. `is` on a sentinel and not a sixth
# number, because the tier value they write is 0 like the `tierall` rung's.
OPEN_TIER = object()

# The pass that keeps the covering constraint: only goods with nothing anywhere,
# at any gain, into any free slot. It is not a tier and not a band.
COVER_TIER = object()

# **The allocator's passes in order, and the one list both it and the dump read.**
# Written out here rather than built twice, because the dump numbers a pass by its
# place in this list and a diagnosis that names the wrong pass is worse than none.
#
# **Four ladders, each of them five descending bands, and the order between them
# is the whole design.**
#
# 1. **coverage** -- every good the ground can produce takes one location, at the
#    highest band it can reach. **It runs FIRST, and the run of 2026-09-03 is
#    why.** It used to be pass 31 of 32, and by then the ground was 192 of 192
#    full: it placed **nothing**, `stone` finished the plan with **zero**
#    buildings on ground where nine locations could have made it, and no bog iron
#    smelter stood anywhere although only four locations in the whole selection
#    can host one. The owner, in capitals: «Где блядь хоть одна печка болотного
#    железа?.. Я бы никогда подобного не допустил во время игры!» A guarantee
#    that runs last is not a guarantee -- it is whatever the ground has left
#    over. It costs the ladders below one building per good, and those are the
#    cheapest buildings in the plan to give away, because each is the only one
#    its good will ever get if the ladder does not place it.
# 2. **the scarce**, tier by tier, five bands inside each -- a good only a
#    handful of locations can hold finishes its quota before a good with forty
#    starts on its own. «Дайте сначала сложным домикам их 2 провинции по
#    возможности, найдите минимум 20 локаций с болотами и зарезервируйте их под
#    железо», 2026-09-03.
# 3. **everything**, five bands -- the `tierall` rung, which is where the bulk of
#    a plan is placed and where gain alone decides.
# 4. **the open ladder**, five bands with the quota raised a layer a round --
#    what is left after every good has had its share.
#
# **The scarce ladder is a phase of its own and no longer a rung inside every
# band, and that is the correction of 2026-09-03.** Written `for band: for
# tier:`, a scarce good could only enter a rung whose band its gain cleared --
# and a scarce good's gain is usually low, because scarcity and a poor recipe
# have the same cause. Over that run the tier rungs of all five bands placed
# **three buildings of sixty-nine** and `band800/tierall` placed the rest; iron
# reached no rung above band 0, and by band 0 its four wetland locations had
# belonged to clay and cloth for twenty-five passes. Reserving before the common
# goods start is what the owner asked for and what «зарезервировать» means.
#
# **The open ladder is banded for the same reason the others are.** It was one
# pass at band 0, where gain does not enter at all, and on the thirty-eighth run
# that one pass placed **271 buildings of 770** -- more than a third of a large
# plan decided without the objective. Five bands cost four more passes and a pass
# with no work is very nearly free: the `while` leaves the moment a sweep adds
# nothing.
PLAN_PASSES = ([(band, COVER_TIER) for band in PLAN_BANDS]
               + [(band, tier) for band in PLAN_BANDS for tier in PLAN_TIERS]
               + [(band, 0) for band in PLAN_BANDS]
               + [(band, OPEN_TIER) for band in PLAN_BANDS])


def pass_name(band: int, tier: object) -> str:
    """How a pass is written in the dump: the band it admits and the tier it is.

    **Every pass has a name of its own.** The open ladder is five passes now, so
    a bare `open` would put the same word on five lines of the dump and the one
    thing the pass list exists for -- reading a number back against the pass that
    made it -- would be gone.
    """
    if tier is COVER_TIER:
        return f"cover{band}"
    if tier is OPEN_TIER:
        return f"open{band}"
    return f"band{band}/tier{tier if tier else 'all'}"

# The diagnostic dump: what one press writes into the log, and the caps on it.
# **A cap must never be silently the answer**, so every capped block prints how
# many it left out. `docs/pitfalls/diagnosis.md` has the whole instrument and the
# four things about `debug_log` that were measured rather than assumed.
DIAG_VERSION = 5
DIAG_LOCS = 200
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
EDITOR_OUT = MOD / "in_game/common/scripted_effects/bag_wtp_generated_editor.txt"
EDITOR_TRIGGERS_OUT = MOD / "in_game/common/scripted_triggers/bag_wtp_generated_editor_triggers.txt"
LOC_OUT = MOD / "main_menu/localization/%s/bag_wtp_generated_l_%s.yml"
LOC_LANGUAGES = ("english", "russian")

BOM = "﻿"
def goods_order(split: dict[str, list[str]]) -> list[str]:
    """The plan's own numbering: raw goods first, then made, each alphabetical.

    Every numbered thing in this mod -- `_pn<n>`, `_p<n>`, `_pool<n>`, the
    picker's cells -- is indexed by position in this list, so it has one
    definition rather than eight copies of the same comprehension.
    """
    return [good for kind in ("raw", "made") for good in split[kind]]


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


def locked_advances() -> dict[str, str]:
    """Advance -> the country condition it carries, for the ones that have one.

    **An advance with a `potential` is not one you will have by the end -- it is
    one you will never have.** 45 of the 181 advances that unlock a building or a
    method are locked to a tag, a culture group or a region: `copperworking` wants
    `is_capital_mesoamerica`, the porcelain kiln wants an east-Asian capital,
    Scottish whisky wants Scotland. The plan's «на конец» side assumed every
    advance is eventually in, so it offered all of them to everybody -- which is
    how five porcelain guilds landed in northern Germany.
    """
    out: dict[str, str] = {}
    for path in (refs.GAME / "in_game/common/advances").glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig")
        for block in re.finditer(r"^([a-z0-9_]+)\s*=\s*\{(.*?)^\}", text, re.S | re.M):
            gate = re.search(r"^\tpotential\s*=\s*\{(.*?)^\t\}", block.group(2), re.S | re.M)
            if not gate:
                continue
            # **Strip the game's own comments before collapsing to one line.**
            # `copperworking` carries a commented-out religion clause, and folded
            # flat the `#` swallowed the rest of the line -- closing braces
            # included. The file parsed as unbalanced and nothing would have said
            # so but `error.log`.
            body = " ".join(" ".join(line.split("#", 1)[0].split())
                            for line in gate.group(1).splitlines()).strip()
            body = " ".join(body.split())
            if body:
                out[block.group(1)] = body
    return out


LOCKED = locked_advances()


def building_unlocks() -> dict[str, str]:
    """Building -> the advance that unlocks it, the mirror of `unlocks()`."""
    out: dict[str, str] = {}
    for path in (refs.GAME / "in_game/common/advances").glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig")
        for block in re.finditer(r"^([a-z0-9_]+)\s*=\s*\{(.*?)^\}", text, re.S | re.M):
            for building in re.findall(r"unlock_building\s*=\s*([a-z0-9_]+)", block.group(2)):
                out[building] = block.group(1)
    return out


BUILDING_UNLOCKS = building_unlocks()


def method_advances(method: eu5data.Method) -> list[str]:
    """Every advance that gates this method: its own, its halves', its building's.

    **A pair's key is `base+improvement` and names no advance.** `copperworking`
    says `unlock_production_method = copper_base`, and the mod's four jewelry
    pairs are keyed `copper_base+amber_enhancement` and the like -- so the lookup
    missed them and Münster was offered a recipe only Mesoamerica can unlock, in
    the «сейчас» plan as much as at the end. Found 2026-09-03, by the owner:
    «этого метода не должно было быть как кандидата в принципе».
    """
    found = []
    for name in (method.key, *method.key.split("+")):
        advance = UNLOCKS.get(name)
        if advance and advance not in found:
            found.append(advance)
    advance = BUILDING_UNLOCKS.get(method.building)
    if advance and advance not in found:
        found.append(advance)
    return found

# **Two buildings the plan treats as always unlocked, at the owner's word.**
# The urban rights arrive with `town_rights_enable` in age 3; the first firearms
# building is age 1 and the first cannon building age 2, so by the time a
# weaponry charter can exist at all both have been buildable for an age or more.
# The plan already ignores that the rights themselves are not researched -- «мы
# же игнорируем тот факт, что гор права ещё не изучены… точно так же должны
# игнорировать» -- and ignoring it on one side while enforcing it on the other is
# what put cannons at zero under a granted weaponry charter.
#
# **Safe because neither building asks anything else of the country.** Both carry
# only rank gates -- `town`, `city`, `megalopolis` -- and no `potential` and no
# `allow`, checked in `production_cannons.txt` and `production_firearms.txt`, so
# the location side still decides where they may stand. Both advances are age 2
# and carry no `potential` either, so waiving them takes nothing from anyone.
#
# **`gun_smith` and not `hand_cannon_guild`, corrected 2026-09-03.** The hand
# cannon guild is age 1 and looked like the earlier firearms building, but its
# advance wants `original_capital ?= { sub_continent = east_asia }` -- putting it
# here handed a Chinese building to every country on the map. `gun_smith` is the
# first firearms building anyone else can have, and it is age 2 exactly as the
# owner said it was.
#
# Deliberately two names and not a rule: the owner asked for these as exceptions,
# and a rule would quietly take in whatever the next patch adds.
ALWAYS_AVAILABLE = ("gun_smith", "cannon_maker")


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


def clear_ticks_effect() -> str:
    """«Сбросить пометки город/село» -- по всему миру, разом.

    **Он существует, потому что различить их было нечем.** 2026-09-02: тумблеры
    стояли на четырнадцати локациях Трансильвании, он сбросил те, что видел в
    окне -- валашские, -- расширил область и пересчитал; трансильванские вошли в
    план впервые, встали наверх списка городами, и это неотличимо от «тумблеры
    вернулись сами». Отчёт это развёл (`docs/TESTLOG.md`), но развести должно
    было окно, а не отчёт.

    По всем пяти континентам, а не по отмеченным: пометка живёт на локации и
    переживает сохранение, поэтому «сбросить» обязано значить «везде», иначе
    остаётся ровно та же ловушка. Один обход по нажатию кнопки, без единого
    скриптового значения в `limit`, -- цена, которую платят раз.
    """
    walks = "".join(f"""\tcontinent:{name} = {{
\t\tevery_location_in_continent = {{
\t\t\tlimit = {{ OR = {{
\t\t\t\thas_variable = {MOD_ID}_force_town
\t\t\t\thas_variable = {MOD_ID}_force_rural
\t\t\t}} }}
\t\t\tremove_variable = {MOD_ID}_force_town
\t\t\tremove_variable = {MOD_ID}_force_rural
\t\t\tchange_global_variable = {{ name = {MOD_ID}_tick_count add = 1 }}
\t\t}}
\t}}
""" for name in CONTINENTS)
    return f"""#
# «Сбросить пометки город/село», по всему миру.
#
# The tick is a location variable and it outlives a save, so a reset that
# covered only what is on screen would leave the same trap it exists to remove:
# 2026-09-02 he cleared the fourteen he could see, widened the ground, and the
# fourteen he could not came into the plan looking exactly like a revert.
#
# Scope: country
{MOD_ID}_clear_ticks = {{
\tset_global_variable = {{ name = {MOD_ID}_tick_count value = 0 }}
{walks}}}
"""


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
        # The same trigger the scoring uses, so the buildable tick and the plan
        # cannot disagree about a location the player has ticked into a town.
        for building in sorted(by_good.get(good, [])):
            out.append(f"\t\t{MOD_ID}_stands_{building} = yes\n")
        out.append("\t}\n}\n")

    # Which methods this country may actually run.
    #
    # 119 buildings in the game are unlocked by an advance with an age on it, and
    # ten production methods are unlocked separately, so `can_build_building` in
    # *country* scope -- "country checks the country scope requirements" -- is
    # what answers "is this available to me now". Without it the table happily
    # recommends a method three ages away, which is what the owner saw on beer.
    # **What no advance can ever bring, and the «на конец» side has to ask it.**
    # An advance carrying a `potential` is not one you will hold eventually -- it
    # is one you will never hold. Without this the end-game plan offered every
    # country everything: five porcelain guilds in northern Germany, whose kiln
    # wants an east-Asian capital.
    # **Only the gated ones are written**, and `score_file` only asks where one
    # exists. `_reach_<n>` answers "could this country ever take the advance
    # behind this method"; for all but thirteen of the 241 the answer is yes by
    # construction, and writing those out was 228 scripted triggers saying
    # `always = yes` that the engine parses on every load and nothing ever calls.
    reach = {index: [LOCKED[a] for a in method_advances(method) if a in LOCKED]
             for index, method in enumerate(rows, start=1)}
    reach = {index: gates for index, gates in reach.items() if gates}
    out.append(f"\n# The {len(reach)} methods of {len(rows)} behind an advance somebody can never "
               f"take.\n# The rest are reachable by construction and are not written out.\n"
               f"# Scope: country\n")
    for index, gates in reach.items():
        method = rows[index - 1]
        body = "".join(f"\tAND = {{ {gate} }}\n" for gate in gates)
        out.append(f"# {method.building} / {method.key}: "
                   f"{', '.join(a for a in method_advances(method) if a in LOCKED)}\n"
                   f"{MOD_ID}_reach_{index} = {{\n{body}}}\n")

    out.append("\n# Scope: country\n")
    for index, method in enumerate(rows, start=1):
        if method.building in ALWAYS_AVAILABLE:
            out.append(f"# {method.building}: taken as given, `generate.ALWAYS_AVAILABLE`.\n"
                       f"{MOD_ID}_avail_{index} = {{\n\talways = yes\n}}\n")
            continue
        # `can_build_building` in country scope already answers the building's
        # own advance; this adds the *method's*, and `method_advances` is what
        # finds it through a pair's `base+improvement` key.
        extra = "".join(f"\n\thas_advance = {gate}" for gate in method_advances(method)
                        if gate in UNLOCKS.values())
        out.append(f"{MOD_ID}_avail_{index} = {{\n"
                   f"\tcan_build_building = building_type:{method.building}{extra}\n}}\n")

    # **The plan simulates ranks, and this is where.** The owner, 2026-09-02:
    # «Расчёт должен симулировать ранги. Если я поставил там город в моде — он
    # должен воспринимать это как город, значит должен дать права, должен
    # поставить нужные дома. И не важно что там стоит на самом деле.»
    #
    # `can_build_building` in a location's scope answers two things at once: the
    # rank flags a building declares (`town = yes`), and its `location_potential`
    # -- the terrain, the market and the one-RGO-per-location rule. **The tick is
    # meant to override the first and nothing else**, so where a location carries
    # one, this asks the potential directly and lets the tick answer the rank.
    #
    # That is the whole of the 2026-09-02 diagnosis: a ticked village was scored
    # as a town, granted a mandatory urban right, and then refused every guild --
    # `w=3` of 17 towns for twenty different goods, and the charter came out
    # half-made every time.
    #
    # Where the potential names a scope this one has not got -- `scope:actor`,
    # two buildings of a hundred and ten -- the game is asked as before. A
    # condition evaluated wrong is worse than a condition not overridden.
    out.append("\n# Scope: location\n")
    seen: dict[str, eu5data.Method] = {}
    for method in rows:
        seen.setdefault(method.building, method)
    for building, method in sorted(seen.items()):
        potential = " ".join(method.potential.split())
        # Two reasons to leave a building alone and ask the game as before: it
        # is gated by something besides the rank and the potential, or its
        # potential names a scope this one has not got. Twelve buildings of a
        # hundred and ten, all of them exotic -- a Japanese reform, an English
        # tag, the Spanish cloth industry.
        if method.extra_gates or "scope:" in potential:
            why = ("an `allow` or a `country_potential` gates it besides the rank"
                   if method.extra_gates else
                   "its potential names a scope this one has not got")
            out.append(f"# {why}, so the tick does not override it.\n"
                       f"{MOD_ID}_stands_{building} = {{\n"
                       f"\tcan_build_building = building_type:{building}\n}}\n")
        elif not potential:
            # The rank is the whole of what the game checks here, and the tick is
            # the answer to the rank. This is the manufacturing ladder.
            out.append(f"{MOD_ID}_stands_{building} = {{\n"
                       f"\tOR = {{\n"
                       f"\t\t{MOD_ID}_rank_is_ticked = yes\n"
                       f"\t\tcan_build_building = building_type:{building}\n"
                       f"\t}}\n}}\n")
        else:
            out.append(f"""{MOD_ID}_stands_{building} = {{
\tOR = {{
\t\tAND = {{
\t\t\t{MOD_ID}_rank_is_ticked = no
\t\t\tcan_build_building = building_type:{building}
\t\t}}
\t\tAND = {{
\t\t\t{MOD_ID}_rank_is_ticked = yes
\t\t\t# the building's own `location_potential`, copied from the game
\t\t\t{potential}
\t\t}}
\t}}
}}
""")

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
    # **What a good's gain is measured against: the best any recipe of that good
    # could ever earn, and not the recipe's own ceiling.** Dividing by its own was
    # the fault of 2026-09-03: a `fine_cloth_guild` running the plain base with a
    # fur trim has one raw input, fur, and a ceiling of 2.86% -- so a province
    # with fur and nothing else fed it whole and it scored **1000**, the same as a
    # perfect wool province, for 2.86% on an output of 0.7. «Туда встало тонкое
    # сукно... но там ничего для него нет, только мех для улучшения.»
    #
    # Against the good's best (10% for fine cloth) the same recipe reads 286 and a
    # wool province reads 833, which is the order he expects. **The reason to
    # normalize at all is untouched**: it is so a good whose *best* recipe tops
    # out at 5% still competes with one that reaches 10%, and that divisor is the
    # good's, not the method's.
    best_ceiling: dict[str, float] = {}
    for method in rows:
        best_ceiling[method.produced] = max(best_ceiling.get(method.produced, 0.0),
                                            method.ceiling(game.raw_goods))
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
                   f"output {method.output:g}, ceiling {ceiling:.2f}% of the "
                   f"good's {best_ceiling.get(method.produced, 0.0):.2f}% "
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
        # *good* could ever earn, this recipe earns here. A raw bonus does not
        # compare across goods -- the ceilings run from 2% to 10% and five goods
        # are capped under five -- and a `worth` normalized to the good's own best
        # on this ground compares even worse, squeezing everything into
        # 0.909-1.000. The divisor is the good's best ceiling in the game, for the
        # reason written where `best_ceiling` is built.
        divisor = best_ceiling.get(method.produced, 0.0)
        if divisor > 0:
            out.append(f"# Scope: location\n{MOD_ID}_g{index} = {{\n\tvalue = 0\n")
            for good, share in sorted(shares.items()):
                out.append(f"""\tif = {{
\t\tlimit = {{ province_definition = {{ any_location_in_province_definition = {{ raw_material = goods:{good} }} }} }}
\t\tadd = {share * RANK_SCALE / divisor:.4f}
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
# {good}: what this ground pays this good here, one side each -- the fraction of
# this recipe's own ceiling the province feeds, out of {RANK_SCALE}, **plus the weight the
# player put on this good**. `order_by` takes a script value and never a variable,
# which is the only reason these exist at all; the harvest puts the number on the
# location and this hands it to the walk.
#
# **`_pw<n>` is the hand regulator and it is in the same units as the gain**, so
# one step of {RANK_SCALE // 5} is exactly one band: a good moved up by one step is dealt with
# the band above its own. Nought by default and nothing else in the plan reads
# it, so the plan with every weight at nought is the plan the formula alone
# makes. **It cannot take a good's last building** -- the covering ladder runs
# before any band and gives every good one, whatever its weight.
#
# **Nothing divides it any more.** It used to be divided by `_pp<n>`, how many of
# that good already stood in the province, and that multiplier was the whole of
# the smear the owner reported on 2026-09-03: the second building of a good in a
# province scored half and the third a third, so a province that suited a good
# perfectly took two of it and handed its other fifteen rooms to whatever had not
# been there yet. Removed with the counter behind it,
# `docs/investigations/plan_formula.md`.
# Scope: location
{MOD_ID}_ord{index} = {{
\tvalue = var:{MOD_ID}_p{index}
}}
# Scope: location
{MOD_ID}_ordr{index} = {{
\tvalue = var:{MOD_ID}_pr{index}
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

        # **The same question asked of the score and not of the gate.**
        # `_plan_can_town_<i>` is a *placement* gate: it also asks whether the
        # town still has room and whether this good is already standing there.
        # At grant time the town is empty, so the gate reduces to exactly this --
        # but the dump runs after the plan, when every town is full, and the
        # first `WTP RQ` line came back as thirteen zeroes because of it
        # (2026-09-03). The twin has to read what was true when the grant was
        # made, which is «a town method for this good won here».
        def _won(good: str) -> str:
            i = order.index(good) + 1
            feeder = market_inputs(game).get(good)
            j = order.index(feeder) + 1 if feeder in order else 0
            if j and plan_groups(rows, split, game).get((feeder, "t")):
                return (f"OR = {{ var:{MOD_ID}_pm{i} > 0 "
                        f"var:{MOD_ID}_pm{j} > 0 }}")
            return f"var:{MOD_ID}_pm{i} > 0"

        # **One score for a right, and it is a gain like any good's.** Each
        # bundle good the town can make contributes its own gain; each it cannot
        # contributes nothing; the sum is divided by the *whole* bundle, so a
        # charter that delivers one good of three is worth a third of one that
        # delivers all three. A flat bonus for each good the town can actually
        # make used to sit on top of this and it is gone: dividing by the full
        # bundle already prices the gaps, and without it the number is on the same
        # 0..RANK_SCALE scale as a good's gain -- which is what lets the bands
        # admit a right and a good by the same threshold. **A constant the plan
        # no longer reads must not stay in the dump's BUILD line either**: that
        # line exists so a number is never checked against the wrong constant,
        # and `right_fit=2000` on it said the plan still used one.
        # **The weight reaches a charter through its bundle**, so that raising a
        # good raises the charters that favour it. Without this the regulator
        # could not touch Sauerland, where the charter round decides all 28
        # buildings and the allocator none of them.
        adds = "".join(f"""\tif = {{
\t\tlimit = {{ {_won(g)} }}
\t\tadd = var:{MOD_ID}_p{order.index(g) + 1}
\t}}
""" for g in bundle)
        plan_values.append(f"""
# {right.key}: {", ".join(bundle)}.
#
# **How much this ground would pay for this whole charter**, out of {RANK_SCALE},
# and nothing else in it. No divisor of any kind: **a right is a bundle of goods
# bound to a town and obeys the same rules a good does** (the owner, 2026-09-03),
# so what limits it is a quota over the whole ground -- `_rquota` in
# `_plan_place_rights` -- and never a penalty for having been granted next door.
#
# Both divisors it carried are gone and both were faults. Counting the **map**
# made the ranges disjoint -- a right granted once could never again win on merit
# -- so the rights were dealt round robin. Counting the **province** was the
# other end of the same mistake: it emptied a province of the one charter its
# ground was made for. «Где драг металы — ювелиркой всё затыкано.»
#
# **It asks `_pm<n>`, the scoring fact, and not `_plan_can_town_<n>`.** That one
# is a placement gate -- it also asks whether the town still has room -- and at
# grant time the town is empty, so the two agree; but the diagnosis reads this
# same value after the plan, when every town is full, and the gate would answer
# zero for all thirteen. It did, on 2026-09-03.
# Scope: location
{MOD_ID}_rq{k} = {{
\tvalue = 0
{adds}\tdivide = {len(bundle)}
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
# The band as a fraction of `RANK_SCALE`, for the open ladder's relative
# threshold. A `multiply` takes a script value, not a variable, which is why this
# has a name of its own -- the same shape `_plan_scored_value` has.
# Scope: country
{MOD_ID}_plan_bandf_value = {{ value = global_var:{MOD_ID}_plan_bandf }}
# What the editor's ordered walks sort on: what this location charges for the
# building being added, or `RANK_SCALE` minus the gain of the one being taken
# out. `order_by` reads a script value and never a variable, which is the whole
# reason this exists.
# Scope: location
{MOD_ID}_edit_order = {{ value = var:{MOD_ID}_esv }}
# How many rights this country could grant at all, which the rights' own
# quota divides by. Counted once a plan, in country scope.
{MOD_ID}_rgrant_value = {{ value = global_var:{MOD_ID}_rgrant }}

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
#
# **`_ord<n>` is the gain and nothing else now.** It used to be divided by
# `_pp<n>`, how many of that good already stood in the province, and that one
# multiplier was the whole of the smear the owner reported on 2026-09-03: a
# good's second building in a province scored half, its third a third, so a
# province that suited a good perfectly took two of it and gave the other
# fifteen rooms to whatever had not been there yet.
#
# **The quota and the concentration answer different questions, and confusing
# them was mine.** «Равномерно» is *how many* -- `_plan_quota`, 34 rooms a good
# on his ground -- and it is untouched. *Where* those 34 land is this value, and
# a province is 17.7 rooms, so a good can own two provinces outright without
# costing any other good a single room. His arithmetic, 2026-09-03, and it is
# right: «на всей общей земле от этого не пострадает ни один другой товар».
#
# **`_pp<n>` is gone with it.** It was still being written -- once per good per
# candidate to zero it, and a walk over every location of the province on every
# placement to raise it -- for a report that never read it. Nothing has read it
# since the divisor went, so nothing writes it either.
# Scope: location
{MOD_ID}_plan_order = {{
\tvalue = 0
\tsubtract = var:{MOD_ID}_plan_prank
\t# **A hundred a province, so the charter can order the towns inside one.**
\t# The owner, 2026-09-03: «мне отвратительно и неприятно видеть бесконечно
\t# чередующиеся права в одной провинции. Пиво-шкаф-пиво-шкаф... Надо как-то
\t# сортировать это, чтобы провинция так же показывала все свои локации вместе,
\t# но сами локации не стояли в таком порядке.»
\t#
\t# **And it is only the order of the rows.** Every location of a province is
\t# worth exactly the same to a charter -- `_rq<k>` reads the province's bonus --
\t# so which town of a province holds which charter is free, and sorting them
\t# changes no number in the plan. That is why this is a script value and not a
\t# change to the grant.
\tmultiply = 100
\tif = {{
\t\tlimit = {{ {MOD_ID}_plan_is_town = yes }}
\t\tadd = 50
\t}}
\t# Ascending by the charter's own number, so identical charters stand together.
\t# `has_variable` first: a village carries none, and a script value reading a
\t# variable that is not there is the failure that logs nothing.
\tif = {{
\t\tlimit = {{ has_variable = {MOD_ID}_plan_right }}
\t\tsubtract = var:{MOD_ID}_plan_right
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
{MOD_ID}_show_ticks = {{ value = global_var:{MOD_ID}_tick_count }}
# The editor's own numbers, for its window to print. **A plain script value over
# a global and no guard inside it**: the self-guarding form returned zero for
# every reader on a plan that had just placed 417 buildings and said so nowhere,
# which is the note below this block.
#
# `_edit_moved` is how many locations the last «показать изменения» found, and
# it is the number that condemned the weight regulator -- 42 of 48 on one press.
# `_edit_done` is whether the last «+1» or «−1» actually did anything: an effect
# that merely does nothing logs nothing at all, and a good whose last building
# may not be taken out is exactly such a case.
# Scope: country
{MOD_ID}_show_edit_moved = {{ value = global_var:{MOD_ID}_edit_moved }}
# Scope: country
{MOD_ID}_show_edit_saved = {{ value = global_var:{MOD_ID}_save_n }}
# Scope: country
{MOD_ID}_show_edit_done = {{ value = global_var:{MOD_ID}_edit_done }}
# Scope: country
{MOD_ID}_show_edit_reached = {{ value = global_var:{MOD_ID}_edit_reached }}
# **How many goods the picker was filled with.** On screen beside the list, and
# it is there to separate two failures that look identical: a list that was
# never filled, and a list that was filled and does not draw. The editor's goods
# vanished once already, and telling those apart cost a round trip.
# Scope: country
{MOD_ID}_show_edit_pooln = {{ value = global_var:{MOD_ID}_edit_pooln }}
# **How many presses the editor has taken since the window opened.** The probe
# that separates «кнопка не сработала» from «правило отказало»: if it does not
# move, the press never reached the effect at all.
# Scope: country
{MOD_ID}_show_edit_presses = {{ value = global_var:{MOD_ID}_edit_presses }}
# Scope: country
{MOD_ID}_show_edit_slot1 = {{ value = global_var:{MOD_ID}_sl1_n }}
# Scope: country
{MOD_ID}_show_edit_slot1_locs = {{ value = global_var:{MOD_ID}_sl1_locn }}
# Scope: country
{MOD_ID}_show_edit_slot2 = {{ value = global_var:{MOD_ID}_sl2_n }}
# Scope: country
{MOD_ID}_show_edit_slot2_locs = {{ value = global_var:{MOD_ID}_sl2_locn }}
# Scope: country
{MOD_ID}_show_edit_slot3 = {{ value = global_var:{MOD_ID}_sl3_n }}
# Scope: country
{MOD_ID}_show_edit_slot3_locs = {{ value = global_var:{MOD_ID}_sl3_locn }}

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
# Which page of the answer is on screen, out of how many, and the rows it covers.
# The window draws one page of {PLAN_ROWS} at a time; these four are what the page
# bar above the table prints, so «показано 150» is never read as the size of the
# plan again.
{MOD_ID}_show_plan_page = {{ value = global_var:{MOD_ID}_plan_page }}
{MOD_ID}_show_plan_pages = {{ value = global_var:{MOD_ID}_plan_pages }}
{MOD_ID}_show_plan_from = {{ value = global_var:{MOD_ID}_plan_from }}
{MOD_ID}_show_plan_to = {{ value = global_var:{MOD_ID}_plan_to }}
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
            # **Not `can_build_building` directly**: that answers the rank and
            # the `location_potential` in one breath, and the tick is meant to
            # override the rank alone. `{MOD_ID}_stands_<building>` splits them
            # where it can and asks the game as before where it cannot
            # (`triggers_file`, and `docs/SETTLED.md` for what it cost to find).
            stands = f" {MOD_ID}_stands_{rows[method_index - 1].building} = yes"
            # **Every answer below is an end-game one, and the one thing even the
            # end cannot bring is an advance this country may never take.**
            # `_reach_<n>` is `always = yes` for all but thirteen methods, so the
            # `if` costs nothing where nothing is locked.
            reachable = [a for a in method_advances(rows[method_index - 1]) if a in LOCKED]
            deep, shut = ("\t\t", "") if not reachable else ("\t\t\t", f"""\t\tif = {{
\t\t\tlimit = {{ scope:{MOD_ID}_country = {{ {MOD_ID}_reach_{method_index} = yes }} }}
""")
            out.append(shut)
            # «По пути»: every age, so no gate on availability -- but the ground
            # still has to be able to hold it.
            out.append(keep(deep, "mid_", suffix, method_index, floor, stands))
            if method_index in last:
                out.append(keep(deep, "end_", suffix, method_index, floor, stands))
                out.append(keep(deep, "end_any_", suffix, method_index, None, stands))
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
                    out.append(keep(deep, "pend", side, method_index, floor, stands, plan=True))
                    out.append(keep(deep, "pendany", side, method_index, None, stands, plan=True))
            if reachable:
                out.append("\t\t}\n")
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


def plan_right_gates(rows: list[eu5data.Method],
                     game: eu5data.Game) -> list[str]:
    """Per urban right, the country condition the plan grants it under.

    **The right's own `potential`, and never its unlocking advance.** Which is
    the same rule the rights *window* uses, and it was arrived at the hard way.

    On 2026-09-03 this asked `has_advance` on «Сейчас», on the argument that a
    plan is an answer about a moment and that refusing a cannon maker for want of
    an advance while handing out Discovery-age charters dated one answer two
    ways. **The run of the same day settled it, against that argument.** Münster
    holds `flemish_cloth_making` and not `town_rights_enable`, so the gate left
    it **one** grantable charter of thirteen -- and the rule every town gets one
    then gave the same charter to all forty-eight. Cloth stood in 48 locations of
    192, a quarter of the ground in one good, and the number of goods the plan
    produced fell from 35 to 30. Ungated, the same ground takes nine charters and
    spreads them.

    **The two are gated differently because they are different kinds of thing.**
    A building you cannot build today is not an answer to «what do I build»; a
    charter is not something you build. It is a property of a town that says
    which buildings belong in it, every country receives the nine general ones at
    one fixed age, and a plan is a target to build towards. That is exactly the
    reason already settled for the window -- «hiding them until age three would
    leave an empty list where the answer belongs» -- and it holds here for the
    same reason.

    **The advance is not lost, it is reported.** `WTP RIGHT` prints `unlocked=`
    beside `grantable=`, so the report says «the plan wants naval charters in
    Sauerland and you cannot grant one until Discovery» without the plan
    degrading into a monoculture to say it.
    """
    by_key = {r.key: r for r in game.town_rights}
    bodies = []
    for right in output_rights(rows, game):
        parts = [p for p in (by_key[right.key].potential,) if p]
        winner = by_key.get(PREFERRED_RIGHT.get(right.key, ""))
        if winner is not None:
            # A preferred right with no gate at all would be preferred always,
            # and the one it displaces would never be granted by anybody. Today
            # Flemish cloth carries a culture group; a silent `always = no` is
            # the worst way to learn that it had lost it.
            assert winner.potential, f"{winner.key} would displace {right.key} everywhere"
            parts.append("NOT = { %s }" % winner.potential)
        bodies.append("\n".join(f"\t{part}" for part in parts) or "\talways = yes")
    return bodies


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

    # And whether this country may grant it at all, at the age the plan is being
    # drawn for. `plan_right_gates` is why this is not the window's question.
    out.append(f"""
# **Who may grant which charter, and when.** One trigger a right, asked by the
# grant pass, by the quota that divides the towns between them and by the dump --
# three places that used to carry three copies of the same condition, one of
# which (the dump's) was not asked at all and printed charters nobody could have.
""")
    for k, (right, body) in enumerate(
            zip(output_rights(rows, game), plan_right_gates(rows, game)), start=1):
        out.append(f"""
# {right.key}{": " + right.advance if right.advance else ""}
# Scope: country
{MOD_ID}_plan_right_gate_{k} = {{
{body}
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
    # **The editor's own two branching labels.** A plain localization key reads a
    # number through a script value -- `{MOD_ID}_plan_pass_summary` is nothing but
    # those -- but it cannot choose between two sentences, and both of these have
    # to: an empty slot must not read «0 buildings in 0 locations», and a «+1»
    # that a rule refused must not look like one that worked.
    for n in range(1, EDIT_SLOTS + 1):
        out.append(f"""
# Slot {n}: what it holds, or that it holds nothing.
# Scope: country
{MOD_ID}_edit_slot{n}_label = {{
\ttype = country
\ttext = {{
\t\ttrigger = {{ global_var:{MOD_ID}_sl{n}_n > 0 }}
\t\tlocalization_key = {MOD_ID}_edit_slot{n}_full
\t}}
\ttext = {{
\t\tfallback = yes
\t\tlocalization_key = {MOD_ID}_edit_slot{n}_empty
\t}}
}}
""")
    out.append(f"""
# Whether the last «+1» or «−1» did anything. **An effect that merely does
# nothing logs nothing at all**, and both of them have rules that refuse: a good
# fitting nowhere on this ground, a good down to its last building, a building
# belonging to a charter's bundle. `_edit_done` is set to 0 before the walk and
# to 1 by the walk. **The branches name the cause, and they exist because a
# single «не дало правило» was read as the mod being stubborn when it was the
# ground.** He pressed «+1» on iron: four locations of Westphalia can make iron
# and iron stood in all four, so there was nowhere for a fifth. The editor has
# only the two rules he agreed to -- never a good's last building, never a
# charter bundle's -- and it reads no quota of the plan's at all.
#
# **`_edit_fail` is the branch that had to exist and did not.** The walk used to
# say «сделано» whenever it found a location, whether or not a building actually
# went in, so a press that evicted something and then failed to place read as a
# success. It cannot happen now -- the victim goes back -- but the window must
# still say that the press did nothing, and why.
# Scope: country
{MOD_ID}_edit_last_label = {{
\ttype = country
\ttext = {{
\t\ttrigger = {{ global_var:{MOD_ID}_edit_op = 0 }}
\t\tlocalization_key = {MOD_ID}_edit_last_none
\t}}
\ttext = {{
\t\ttrigger = {{ global_var:{MOD_ID}_edit_done = 1 global_var:{MOD_ID}_edit_norefill = 1 }}
\t\tlocalization_key = {MOD_ID}_edit_last_empty
\t}}
\ttext = {{
\t\ttrigger = {{ global_var:{MOD_ID}_edit_done = 1 }}
\t\tlocalization_key = {MOD_ID}_edit_last_done
\t}}
\ttext = {{
\t\ttrigger = {{ global_var:{MOD_ID}_edit_reached = 0 }}
\t\tlocalization_key = {MOD_ID}_edit_last_lost
\t}}
\ttext = {{
\t\ttrigger = {{ global_var:{MOD_ID}_edit_fail = 1 }}
\t\tlocalization_key = {MOD_ID}_edit_last_refill
\t}}
\ttext = {{
\t\ttrigger = {{ global_var:{MOD_ID}_edit_op = 1 global_var:{MOD_ID}_edit_fitn = 0 }}
\t\tlocalization_key = {MOD_ID}_edit_last_nowhere
\t}}
\ttext = {{
\t\ttrigger = {{ global_var:{MOD_ID}_edit_op = 1 global_var:{MOD_ID}_edit_cands = 0 }}
\t\tlocalization_key = {MOD_ID}_edit_last_novictim
\t}}
\ttext = {{
\t\ttrigger = {{ global_var:{MOD_ID}_edit_op = 2 global_var:{MOD_ID}_edit_fitn < 2 }}
\t\tlocalization_key = {MOD_ID}_edit_last_lastone
\t}}
\ttext = {{
\t\ttrigger = {{ global_var:{MOD_ID}_edit_op = 2 global_var:{MOD_ID}_edit_cands = 0 }}
\t\tlocalization_key = {MOD_ID}_edit_last_allcharter
\t}}
\ttext = {{
\t\tfallback = yes
\t\tlocalization_key = {MOD_ID}_edit_last_refused
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
\t# **A fresh plan is its own baseline.** «Показать изменения» right after one is
\t# empty, which is the true answer: nothing has been edited yet, and everything
\t# after this is measured against what the formula produced.
\t{MOD_ID}_edit_save = yes
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
\t\tremove_variable = {MOD_ID}_plan_pg
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
\tset_global_variable = {{ name = {MOD_ID}_plan_fed value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_gain value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_scored value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_found value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_shown value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_page value = 1 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_pages value = 1 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_pagec value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_from value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_to value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_rooms value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_towns value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_provn value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_rightn value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_sweeps value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_opensw value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_band value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_bandf value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_cover value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_quota value = 1 }}
"""]
    for index, good in enumerate(order, start=1):
        # `_pw<n>` is the player's own weight on this good and is **not** zeroed
        # here: it is a setting, not a counter, and outlives every plan. It is
        # created if it is missing, because a `limit` reading a global that is
        # not there is the failure that logs nothing.
        out.append(f"\tset_global_variable = {{ name = {MOD_ID}_pn{index} value = 0 }}\n"
                   f"\tset_global_variable = {{ name = {MOD_ID}_pq{index} value = 1 }}\n"
                   f"\tset_global_variable = {{ name = {MOD_ID}_nrgo{index} value = 0 }}\n"
                   f"\tset_global_variable = {{ name = {MOD_ID}_pbest{index} value = 0 }}\n"
                   f"\tset_global_variable = {{ name = {MOD_ID}_pth{index} value = 0 }}\n"
                   )
    # How many towns each right has been given. **The global is the dump's now
    # and no longer the score's** -- `_rq<k>` divides by `_rp<k>`, the count in
    # this province. A script value reading a global that is not there is the
    # silent failure, so it still has to be zeroed.
    for k in range(1, len(rights) + 1):
        out.append(f"\tset_global_variable = {{ name = {MOD_ID}_rgiven{k} value = 0 }}\n"
                   f"\tset_global_variable = {{ name = {MOD_ID}_rn{k} value = 0 }}\n")
    # The rights' band and quota, zeroed here for the same reason every other
    # counter is: a `limit` that reads a global which is not there fails silently.
    out.append(f"\tset_global_variable = {{ name = {MOD_ID}_rband value = 0 }}\n"
               f"\tset_global_variable = {{ name = {MOD_ID}_ropen value = 0 }}\n"
               f"\tset_global_variable = {{ name = {MOD_ID}_rlevel value = 0 }}\n"
               f"\tset_global_variable = {{ name = {MOD_ID}_rquota value = 1 }}\n"
               f"\tset_global_variable = {{ name = {MOD_ID}_rgrant value = 0 }}\n")
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
\t\t\t# **Nothing clears the floor: take the best recipe anyway.** A location
\t\t\t# no RGO helps still has to be filled, and a granted right's bundle goes
\t\t\t# up whether the bonus is there or not -- the owner, 2026-09-01.
\t\t\t#
\t\t\t# **And it keeps its own gain, undivided.** The score already *is* how
\t\t\t# much of its ceiling the ground pays: a recipe earning 4% of a possible
\t\t\t# 10 comes in at 400 and is behind everything better by that alone.
\t\t\t# Halving it on top counted the same fact twice and moved the building in
\t\t\t# the queue for want of raw materials, which is the one thing the owner
\t\t\t# forbade outright («не должно... смещён в очереди из-за этого»,
\t\t\t# 2026-09-01, confirmed 2026-09-02). The floor still chooses the method --
\t\t\t# that is the half of his rule that stands: «может влиять только на ВЫБОР
\t\t\t# метода производства в конкретном домике».
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_pm{index} = 0 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_p{index} value = var:{MOD_ID}_pendanygain_t }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_pm{index} value = var:{MOD_ID}_pendanybest_method_t }}
\t\t\t}}
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_prm{index} = 0 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_pr{index} value = var:{MOD_ID}_pendanygain_r }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_prm{index} value = var:{MOD_ID}_pendanybest_method_r }}
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
\t\t\t}}
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_prm{index} = 0 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_pr{index} value = var:{MOD_ID}_pnowanygain_r }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_prm{index} value = var:{MOD_ID}_pnowanybest_method_r }}
\t\t\t}}
\t\t}}
\t}}
\tset_global_variable = {{ name = {MOD_ID}_ng{index} value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_nrgo{index} value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_pbest{index} value = 0 }}
\t# **Counted on the side the location actually is**, and not on the better of
\t# the two: a good whose only buildings are rural would otherwise count as
\t# makeable on ground that is all towns. The
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
\t\t# **And the best this ground ever pays this good**, which is what the open
\t\t# ladder deals the leftovers by. Taken on the side the location actually is,
\t\t# inside the walk that was happening anyway: one comparison a candidate and
\t\t# no walk of its own. The dump has printed this number as `o` all along --
\t\t# read back off the map afterwards -- and afterwards is too late to
\t\t# allocate with.
\t\tif = {{
\t\t\tlimit = {{
\t\t\t\t{MOD_ID}_plan_is_town = yes
\t\t\t\tvar:{MOD_ID}_p{index} > global_var:{MOD_ID}_pbest{index}
\t\t\t}}
\t\t\tset_global_variable = {{ name = {MOD_ID}_pbest{index} value = var:{MOD_ID}_p{index} }}
\t\t}}
\t\tif = {{
\t\t\tlimit = {{
\t\t\t\t{MOD_ID}_plan_is_town = no
\t\t\t\tvar:{MOD_ID}_pr{index} > global_var:{MOD_ID}_pbest{index}
\t\t\t}}
\t\t\tset_global_variable = {{ name = {MOD_ID}_pbest{index} value = var:{MOD_ID}_pr{index} }}
\t\t}}
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
    for side, listname, method_var, gain_var, cap in (("t", "town", "pm", "p", "urban"),
                                                     ("r", "rural", "prm", "pr", "rural")):
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
\t\t\tchange_variable = {{ name = {MOD_ID}_load add = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_placed add = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_added add = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_pn{index} add = 1 }}
\t\t\t# **What this building gets out of standing here**, which is the question
\t\t\t# the owner asked of the whole plan on 2026-09-02: «какой процент из них
\t\t\t# получит выгоду от своего положения на карте». `_{gain_var}{index}` is the
\t\t\t# gain -- the fraction of this recipe's own ceiling the ground pays, out
\t\t\t# of {RANK_SCALE} -- so the two counters are «how many earn anything» and
\t\t\t# «what they earn on average». Two adds a placement and nothing per
\t\t\t# candidate: the plan does not get slower for being answerable.
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_gain add = var:{MOD_ID}_{gain_var}{index} }}
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_{gain_var}{index} > 0 }}
\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_fed add = 1 }}
\t\t\t}}
\t\t}}
"""
            out.append(f"""# {good}, {"town" if side == "t" else "village"} side.
# Scope: location
{MOD_ID}_plan_try_{listname}_{index} = {{
\tif = {{
\t\tlimit = {{ {MOD_ID}_plan_can_{listname}_{index} = yes }}
{branches}\t}}
}}

# {good}, {"town" if side == "t" else "village"} side, **for the editor**.
#
# **The same placement, asked a different question.** `_plan_can_*` is the plan's
# gate and it asks for a free room; the editor frees the room itself, an eviction
# at a time, so it asks `_edit_fits_*` -- the identical test with the room clause
# taken out. **The scan and the placement are then one predicate**, and cannot
# disagree: the walk chose this location *because* `_edit_fits_*` said yes, so a
# placement that then refuses is impossible by construction.
#
# The owner, 2026-09-04, after «поставить не удалось, и всё осталось как было»:
# «Там не должно быть вообще никаких ограничений и правил, кроме как что 1 домика
# не может быть меньше 1 и собственно самих правил наивыгоднейшей
# установки/удаления.» This is that, and the room is the walk's business.
# Scope: location
{MOD_ID}_edit_place_{listname}_{index} = {{
\tif = {{
\t\tlimit = {{
\t\t\t{MOD_ID}_edit_fits_{listname}_{index} = yes
\t\t\t# **The one invariant, asked again at the last moment.** A location holds
\t\t\t# `cap` buildings and no more. The walk frees the room before it places,
\t\t\t# so this passes by the time it is read -- and on 2026-09-04 it did not:
\t\t\t# 27 buildings went in over the cap, one location reaching 18 of 4, with
\t\t\t# nothing evicted at all. Whatever the walk got wrong, **a placement that
\t\t\t# cannot say no is a plan that can be corrupted**, and the diagnostics'
\t\t\t# `EDIT walk` line says which of the two failed.
\t\t\tvar:{MOD_ID}_load < global_var:{MOD_ID}_plan_cap_{cap}
\t\t}}
{branches}\t}}
}}
""")

    # ---- the row, in an order that does not move -----------------------------
    #
    # **`_plan_goods` is in placement order and that order is not reproducible.**
    # A plan appends a good the round it places it, so a location reads «пиво,
    # вино, спирт»; a slot restored appends in the goods' own numbering and the
    # same location reads «спирт, вино, пиво». Nothing about the plan differs —
    # the owner, 2026-09-03: «Одно и то же, но визуально сбивает с толку.»
    #
    # So the rows read a pair of their own, rebuilt in the goods' own order after
    # every plan, load and edit. `_plan_goods` stays the plan's working list,
    # where order means nothing; `_row_goods` and `_row_builds` are what a window
    # repeats over, and they line up because they are written in one step.
    #
    # **The building is re-derived from `_pm<n>` rather than copied.** That is the
    # same read the placement makes, and the scoring pass is the only thing that
    # writes it — no edit touches it — so the answer is the one that was placed.
    def row_entry(index: int, good: str, tab: str) -> str:
        """One good's cell: the good, then the building the method chose.

        **The side is asked, and it has to be.** The scoring pass writes both
        `_pm<n>` and `_prm<n>` on every candidate -- a location is scored as a
        town and as a village whatever it is now -- so a good whose town and
        village buildings run the same method number would be added twice
        without this. `_plan_try_*` asks the same question through
        `_plan_can_*`; here it is asked directly, because the room is not.
        """
        branches = ""
        for side, method_var, rank in (("t", "pm", "yes"), ("r", "prm", "no")):
            for building, mis in sorted(groups.get((good, side), {}).items()):
                tests = "".join(
                    "%s\t\t\tvar:%s_%s%d = %d\n" % (tab, MOD_ID, method_var, index, mi)
                    for mi in sorted(mis))
                branches += (f"{tab}\tif = {{\n{tab}\t\tlimit = {{\n"
                             f"{tab}\t\t\t{MOD_ID}_plan_is_town = {rank}\n"
                             f"{tab}\t\t\tOR = {{\n{tests}{tab}\t\t\t}}\n"
                             f"{tab}\t\t}}\n"
                             f"{tab}\t\tadd_to_variable_list = {{ name = {MOD_ID}_row_builds "
                             f"target = building_type:{building} }}\n{tab}\t}}\n")
        if not branches:
            return ""
        return (f"{tab}if = {{\n"
                f"{tab}\tlimit = {{\n"
                f"{tab}\t\tis_target_in_variable_list = "
                f"{{ name = {MOD_ID}_plan_goods target = goods:{good} }}\n"
                f"{tab}\t\tNOT = {{ is_target_in_variable_list = "
                f"{{ name = {MOD_ID}_row_goods target = goods:{good} }} }}\n"
                f"{tab}\t}}\n"
                f"{tab}\tadd_to_variable_list = {{ name = {MOD_ID}_row_goods "
                f"target = goods:{good} }}\n"
                f"{branches}{tab}}}\n")

    # **The charter's own goods go first, and that is the whole of the order he
    # asked for.** 2026-09-03, after the rows were made reproducible: «я привык
    # видеть например городские права на локации стекло и кладка -- дальше домики
    # в списке у локации обязательно сначала шли стекольный дом, каменный дом, а
    # потом товар x, товар y… Короче, красота опять попортилась, но уже в другом
    # месте.» The bundle is why the town has the charter, so it reads first; the
    # rest follow in the goods' own numbering, which is what makes the order the
    # same however the plan got there.
    #
    # **The second pass skips what the first already took**, through the `NOT` on
    # `_row_goods` -- a bundle good would otherwise be listed twice.
    bundles = ""
    for k, right in enumerate(output_rights(rows, game), start=1):
        inside = "".join(
            row_entry(order.index(good) + 1, good, "\t\t\t")
            for good in sorted(right.output) if good in order)
        if not inside:
            continue
        bundles += (f"\t\tif = {{\n\t\t\tlimit = {{ has_variable = {MOD_ID}_plan_right "
                    f"var:{MOD_ID}_plan_right = {k} }}\n{inside}\t\t}}\n")
    rest = "".join(row_entry(index, good, "\t\t")
                   for index, good in enumerate(order, start=1))
    out.append(f"""
# What a row draws, in an order that is the same however the plan got there.
# Scope: country
{MOD_ID}_plan_rows = {{
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_touched
\t\tclear_variable_list = {MOD_ID}_row_goods
\t\tclear_variable_list = {MOD_ID}_row_builds
{bundles}{rest}\t}}
}}

""")

    # ---- the rights round --------------------------------------------------
    #
    # A right the country cannot grant must not shrink the others' quota, so the
    # count asks each one's own gate -- **the very same trigger the grant asks**,
    # and not a second copy of the condition. On «Сейчас» that includes the
    # unlocking advance, so a country before the Discovery age divides its towns
    # between the charters it actually has rather than between all thirteen.
    grant_counts = "".join(
        f"\tif = {{\n\t\tlimit = {{ {MOD_ID}_plan_right_gate_{k} = yes }}\n"
        f"\t\tchange_global_variable = {{ name = {MOD_ID}_rgrant add = 1 }}\n\t}}\n"
        for k in range(1, len(rights) + 1))
    grant_zeroes = "".join(
        f"\tset_global_variable = {{ name = {MOD_ID}_rn{k} value = 0 }}\n"
        for k in range(1, len(rights) + 1))
    # **Every charter the country could grant is granted somewhere, and they
    # come out level.** The goods have had the covering rule since 2026-09-01 --
    # «все товары которые можно произвести на выбранной земле должны
    # производиться, все» -- and the owner asked the rights to obey the same one,
    # 2026-09-03: «какое-то количество оружейных прав должно было выделиться
    # каким-то городам обязательно».
    #
    # **The ladder is levels, not a cap.** A quota that is only a ceiling does
    # nothing for a charter nobody wants: the pass walks towns, each town takes
    # the best charter with room left, and one the ground pays 62 for is never
    # any town's best while a rival at 441 still has quota. On 48 towns and 9
    # charters that came out 6 6 6 6 6 6 6 3 3 -- the owner, 2026-09-03: «у пушек
    # ювелирки по 3 ... но вот с пушками я на такое не согласен, им есть чё взять».
    #
    # So the ceiling is raised one town at a time and the whole ladder of bands
    # runs at each height: **no charter takes an Nth town until every charter has
    # had the chance of its Nth.** Level 1 is exactly the covering ladder that
    # used to be a special case of its own -- `_rn<k> < 1` is `_rn<k> = 0` -- so
    # that case is gone and the flag with it.
    #
    # Inside a level the bands still decide *which* town, so a charter takes the
    # ground that pays it most before it takes ground that merely tolerates it.
    # That is what put the weaponry charter in Essen rather than in Elsfleth,
    # where it scores nothing: «КАК СУКА ТАК ПОЛУЧАЕТСЯ, ЧТО ЕДИНСТВЕННАЯ ХОРОШАЯ
    # ПРОВИНЦИЯ ДЛЯ ОРУЖЕЙНЫХ ПРАВ -- НЕ ПОЛУЧАЕТ ОРУЖЕЙНЫХ ПРАВ!?»
    #
    # **The price is a town that would rather have had another charter**, and the
    # owner set the price: «я не буду удовлетворён пока не увижу в вестфалии
    # относительно одинаковое количество каждого городского права… и мне похуй
    # что там в формулах».
    level_bands = "".join(
        f"\t\tset_global_variable = {{ name = {MOD_ID}_rband value = {band} }}\n"
        f"\t\tset_global_variable = {{ name = {MOD_ID}_ropen value = 0 }}\n"
        f"\t\t{MOD_ID}_plan_grant_pass = yes\n"
        for band in PLAN_BANDS)
    # The same ladder once more, off the loop, for a ground where the guard below
    # cut the levels short. `_rlevel` jumps to the quota so the count is the one
    # the quota always meant.
    final_bands = level_bands.replace("\t\t", "\t\t\t")
    # **The guard is the loop's, and it has to be there.** `_rquota` is towns
    # divided by charters, so a country with many towns and two charters would
    # otherwise walk its whole ground a hundred times over. {RIGHT_LEVELS} levels
    # is past any ground this has been run on -- 48 towns and 9 charters is 6.
    grant_passes = f"""\tset_global_variable = {{ name = {MOD_ID}_rlevel value = 0 }}
\twhile = {{
\t\tlimit = {{
\t\t\tglobal_var:{MOD_ID}_rlevel < global_var:{MOD_ID}_rquota
\t\t\tglobal_var:{MOD_ID}_rlevel < {RIGHT_LEVELS}
\t\t}}
\t\tchange_global_variable = {{ name = {MOD_ID}_rlevel add = 1 }}
{level_bands}\t}}
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_rlevel < global_var:{MOD_ID}_rquota }}
\t\tset_global_variable = {{ name = {MOD_ID}_rlevel value = global_var:{MOD_ID}_rquota }}
{final_bands}\t}}
"""
    # And the open pass: the quota and the band lifted together, so a town no
    # charter fits on merit still ends with one.
    grant_passes += (f"\tset_global_variable = {{ name = {MOD_ID}_rband value = 0 }}\n"
                     f"\tset_global_variable = {{ name = {MOD_ID}_ropen value = 1 }}\n"
                     f"\t{MOD_ID}_plan_grant_pass = yes\n")
    out.append(f"""
# Urban rights, before any good is placed and only in towns.
#
# **A right is a bundle of goods bound to a town, and obeys the rules a good
# obeys.** The owner, 2026-09-03: «права это просто связка товара, которая
# заложена в город. В остальном она подчиняется абсолютно тем же вещам что и
# простой товар.» So it is dealt exactly as a good is: **a quota over the whole
# ground says how many towns a right may take, and descending bands of gain say
# which towns those are.**
#
# **The quota is the "равномерно" half and it is the only limit.** Neither
# divisor this ever carried survives: the map-wide one made the ranges disjoint,
# so a right granted once could never again win on merit and they went round
# robin; the province-wide one emptied a province of the charter its ground was
# made for. The quota limits the count and leaves the placement to the ground,
# which is the whole distinction the owner drew.
#
# **The bands are what put a scarce charter where it belongs.** A town takes a
# right only where the ground pays at least the band, so the two towns on the map
# with silver under them are reached by the jewelry charter in band 800, before
# any town is handed a charter it merely tolerates. The last pass lifts the quota
# and the band together, so no town is left without one.
#
# **And a right is granted whether or not the whole bundle fits**, since
# 2026-09-01: «Оно БУДЕТ выдано ОБЯЗАТЕЛЬНО. И каждый такой город обязательно
# получит все здания из его бонуса.» The bundle's buildings go in before any
# ordinary good touches the town, and where the urban cap is smaller than the
# bundle the town simply runs out of room.
# Scope: country
{MOD_ID}_plan_place_rights = {{
\t# How many rights this country could grant at all. The quota is towns divided
\t# by that, so a country with three rights available spreads over three and not
\t# over the {len(rights)} the game defines.
\tset_global_variable = {{ name = {MOD_ID}_rgrant value = 0 }}
{grant_counts}\tset_global_variable = {{ name = {MOD_ID}_rquota value = global_var:{MOD_ID}_plan_towns }}
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_rgrant > 0 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_rquota divide = {MOD_ID}_rgrant_value }}
\t}}
\t# `max` is the floor on a variable operation -- `_plan_quota` above depends on
\t# the same and says so. A ground with fewer towns than rights still gives every
\t# charter one town to want.
\tchange_global_variable = {{ name = {MOD_ID}_rquota max = 1 }}
{grant_zeroes}{grant_passes}}}

# One pass of the rights round: every town still empty takes the best right the
# ground pays `_rband` for and whose quota is not spent.
# Scope: country
{MOD_ID}_plan_grant_pass = {{
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
\t\tlimit = {{
\t\t\t{MOD_ID}_plan_is_town = yes
\t\t\tvar:{MOD_ID}_load = 0
\t\t}}
\t\t# **Minus one and not nought.** The winner is taken with `rtry > rbest`, so
\t\t# a charter this ground pays exactly nothing for could never win even when it
\t\t# was the only one left: 2026-09-03, Westphalia has no precious metal at all,
\t\t# the jewelry charter scored 0 in all 48 towns, and even the covering ladder
\t\t# could not place it. `_rbest_k` still starts at 0, so a town where no charter
\t\t# fits gets none.
\t\tset_variable = {{ name = {MOD_ID}_rbest value = -1 }}
\t\tset_variable = {{ name = {MOD_ID}_rbest_k value = 0 }}
""")
    for k, right in enumerate(rights, start=1):
        bundle = sorted(right.output)
        gate = (f"\t\t\t\tscope:{MOD_ID}_country = "
                f"{{ {MOD_ID}_plan_right_gate_{k} = yes }}\n")
        out.append(f"""\t\t# {right.key}: {", ".join(bundle)}
\t\tset_variable = {{ name = {MOD_ID}_rtry value = {MOD_ID}_rq{k} }}
\t\tif = {{
\t\t\tlimit = {{
\t\t\t\tvar:{MOD_ID}_rtry > var:{MOD_ID}_rbest
\t\t\t\t{MOD_ID}_plan_right_fits_{k} = yes
\t\t\t\t# The band: what this ground has to pay before the charter is taken
\t\t\t\t# here at all. The open pass sets it to 0.
\t\t\t\tvar:{MOD_ID}_rtry >= global_var:{MOD_ID}_rband
\t\t\t\t# The level: how many towns any one charter may hold so far. It
\t\t\t\t# climbs by one at a time, so no charter takes an Nth town while
\t\t\t\t# another is still short of its Nth -- that, and not the quota it
\t\t\t\t# ends at, is what makes the counts come out level. The open pass
\t\t\t\t# lifts it: a town with no charter at all is worse than an uneven count.
\t\t\t\tOR = {{
\t\t\t\t\tglobal_var:{MOD_ID}_ropen = 1
\t\t\t\t\tglobal_var:{MOD_ID}_rn{k} < global_var:{MOD_ID}_rlevel
\t\t\t\t}}
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
\t\t\t# **One counter, over the whole ground.** `_rn<k>` is what the quota reads;
\t\t\t# `_rgiven<k>` is the same number for the dump, kept apart so that changing
\t\t\t# what the plan counts never quietly changes what the report prints.
\t\t\tchange_global_variable = {{ name = {MOD_ID}_rn{k} add = 1 }}
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
    # **The share is over the whole ground, and a charter's buildings are spent
    # out of the good's own share rather than added to it.** Both halves changed
    # on 2026-09-03 and the owner's arithmetic is the reason: «как будто бы 1
    # домик + 2 РГО не равняются 9, а равняются 3. Так почему? Почему РГО
    # внезапно стал весить 4 вместо 1?»
    #
    # He was reading a real fault. The share used to be *what the charters left*
    # divided by the goods -- on Westphalia 84 rooms over 35 goods, **2** -- and
    # then each good got its own charters added back. So wine, whose charter is
    # brewing, walked in at 2 + 6 = **8**, and iron, with two RGOs under it,
    # walked in at 2 - 2 = 0, floored to **1**. Nine wine and one iron is that
    # subtraction, not the ground: two RGOs did not cost iron two buildings, they
    # cost it seven, because the base they came off was 2.
    #
    # Now the share is 192 rooms over 35 goods, **5**, and what a charter put down
    # counts against it: wine walks in holding 6 of a share of 5 and takes no
    # more, iron gets 5 - 2 = **3**. That is his own rule -- one RGO is one
    # building -- doing what it says.
    #
    # **What this overturns, and why that is right.** The addition was put in
    # after the thirty-eighth run, where `tools` held six charter buildings
    # against a quota of 2 and so could not take a free room in Sauerland at a
    # gain of 799. That was a real fault of a share of **2**; against a share of
    # 5 a good already holding 6 is above its share, and stopping there is the
    # evenness rather than a bug. The old fault cannot recur and the new rule is
    # the one he asked for.
    #
    # `_pn<n>` is the rights' count and nothing else at this moment: `_plan_run`
    # calls this between `_plan_place_rights` and `_plan_allocate`, and nothing
    # else in the plan writes it -- so the allocator's own `_pn<n> < _pq<n>` is
    # what charges the charters to the share, with no second subtraction here.
    quota_lines = "".join(
        f"""\tset_global_variable = {{ name = {MOD_ID}_pq{index} value = global_var:{MOD_ID}_plan_quota }}
\tchange_global_variable = {{ name = {MOD_ID}_pq{index} subtract = global_var:{MOD_ID}_nrgo{index} }}
\tchange_global_variable = {{ name = {MOD_ID}_pq{index} max = 1 }}
"""
        for index, good in enumerate(order, start=1))
    out.append(f"""
# How many buildings each good may claim before the ground is opened to all.
#
# `_plan_rooms` is every candidate's cap added up and `_plan_scored` is how many
# goods this ground can make at all -- a good nothing here can produce must not
# take a share and shrink everyone else's. The division is the fair share of the
# whole ground, charters included, and what a charter already built is spent out
# of that share by the allocator rather than added to it here.
#
# **`max = 1` is the floor and it is deliberate.** A ground too small to give
# every good one building still gives every good one building; what gives way
# then is the cap, not the spread, and the header line says so by showing more
# goods than rooms. The RGO discount comes off the same number, one for one.
# Scope: country
{MOD_ID}_plan_set_quota = {{
\tset_global_variable = {{ name = {MOD_ID}_plan_quota value = global_var:{MOD_ID}_plan_rooms }}
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_plan_scored > 0 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_quota divide = {MOD_ID}_plan_scored_value }}
\t}}
\tchange_global_variable = {{ name = {MOD_ID}_plan_quota max = 1 }}
{quota_lines}}}
""")

    # ---- the threshold a pass admits a good at ------------------------------
    #
    # **One global per good, written per pass, and the pick reads only that.**
    # The band used to be one number for every good, which is right while the
    # quota is binding and wrong the moment it stops -- and on a realm-sized
    # ground it stops completely. Measured 2026-09-03 on 416 locations: the quota
    # came to 29 a good and no good reached it, so the band was the whole
    # allocator, and the 30 goods that touch 1000 somewhere averaged **42**
    # buildings against **12** for the eight that never do. `cannons` could stand
    # in 103 locations, had a quota of 160, and got **two**.
    #
    # So the absolute band deals the fair share and **the open ladder deals the
    # leftovers by each good's own best**: a good whose ceiling on this ground is
    # 362 enters `open800` at 290, which is its own top fifth, exactly as cloth
    # enters at 800. That is the second ladder
    # `docs/investigations/plan_gaps.md` D asked for, and the run above is the
    # measurement it was waiting for.
    absolute = "".join(
        f"\tset_global_variable = {{ name = {MOD_ID}_pth{i} value = global_var:{MOD_ID}_plan_band }}\n"
        for i in range(1, len(order) + 1))
    # `_pbest` plus the player's weight, floored at nought, times the band as a
    # fraction. Four writes a good and only in the open ladder.
    relative = "".join(
        f"\tset_global_variable = {{ name = {MOD_ID}_pth{i} value = global_var:{MOD_ID}_pbest{i} }}\n"
        f"\tchange_global_variable = {{ name = {MOD_ID}_pth{i} multiply = {MOD_ID}_plan_bandf_value }}\n"
        for i in range(1, len(order) + 1))
    out.append(f"""
# What a good has to reach to be placed in this pass, one global per good.
#
# **The absolute band, for every ladder but the last.** While the quota binds,
# the ground is contested and the biggest gain should win the room.
# Scope: country
{MOD_ID}_plan_th_absolute = {{
{absolute}}}

# **And each good's own best, scaled by the band, for the open ladder.** Once
# every good has had its share, the rooms left over are not contested in the same
# way: handing them to whoever has the largest ceiling is what put 108 cloth
# buildings and 2 cannon on the same ground. `_plan_bandf` is the band as a
# fraction, set by the pass.
# Scope: country
{MOD_ID}_plan_th_relative = {{
{relative}}}
""")

    # ---- the sweeps --------------------------------------------------------
    out.append(f"""
# The rounds: coverage, then the scarce goods, then everything, then what is left.
#
# **A good with one place in the whole ground that can hold it takes that place
# before a good with forty gets its second.** That is the owner's «жёстко
# зарезервировать слоты», and iron is the case he named: without an RGO it comes
# from one building, `bog_iron_smelter`, which wants wetlands or a lake, so where
# it can go at all it must. A tier admits only goods `_ng<n>` says few locations
# can host, and **the tiers are a phase before the common goods start rather than
# a rung inside every band** -- which is the one thing that makes the reservation
# real. `generate.PLAN_PASSES` has the measurement that settled it.
#
# Within a pass the sweeps run until one adds nothing anywhere, so **a location
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
    #
    # **All four ladders are banded, the open one included.** Coverage keeps the
    # owner's hard constraint, the scarce ladder reserves, the `tierall` ladder
    # places the bulk, and the open ladder fills what is left -- and each of them
    # deals its own share of the ground highest gain first.
    for number, (band, tier) in enumerate(PLAN_PASSES, start=1):
        out.append(f"\tset_global_variable = {{ name = {MOD_ID}_plan_band value = {band} }}\n")
        out.append(f"\tset_global_variable = {{ name = {MOD_ID}_plan_cover "
                   f"value = {1 if tier is COVER_TIER else 0} }}\n")
        # The threshold each good is admitted at in this pass: the band itself
        # everywhere but the open ladder, each good's own best there.
        if tier is OPEN_TIER:
            out.append(f"\tset_global_variable = {{ name = {MOD_ID}_plan_bandf "
                       f"value = {band / RANK_SCALE:g} }}\n"
                       f"\t{MOD_ID}_plan_th_relative = yes\n")
        else:
            out.append(f"\t{MOD_ID}_plan_th_absolute = yes\n")
        if tier is COVER_TIER:
            out.append("""\t# **Every good the ground can produce is produced.** The owner's first
\t# requirement and the one the bands cannot keep on their own: a good that
\t# lost every band -- because the rights took the towns, or because it gains
\t# nothing and the ground filled -- takes a free slot here, anywhere, at any
\t# gain. «Все товары которые можно произвести на выбранной земле должны
\t# производиться, все.»
""")
            tier = 0
        # **An open pass raises every quota by one a round; it does not lift
        # them.** Lifting was the thirty-sixth run: five towns of Münsterland,
        # ten buildings in fifteen rooms and the same good standing in three of
        # them, because the first good down the list took every free room at
        # once. Raising fills the leftover ground a layer at a time instead, so
        # what is spare is spread the same way the quota itself is -- and with
        # the band still on, the layer goes where the ground pays for it.
        raise_all = ""
        if tier is OPEN_TIER:
            # **And the count of those raises, because without it `q` in the
            # report cannot be read.** `_pq<n>` is dumped after the plan, so it
            # carries every layer this ladder added; the quota the allocator
            # actually enforced is `q` minus this number. Two reports of
            # 2026-09-03 were mis-read for want of it -- `clay q=2 rgo=2` beside
            # `PASS quota=2` looks like the RGO discount doing nothing, and is
            # the discount working and the open ladder adding one back.
            raise_all = "".join(
                f"\t\tchange_global_variable = {{ name = {MOD_ID}_pq{i} add = 1 }}\n"
                for i in range(1, len(order) + 1))
            raise_all += f"\t\tchange_global_variable = {{ name = {MOD_ID}_plan_opensw add = 1 }}\n"
            tier = 0
        out.append(f"""\tset_global_variable = {{ name = {MOD_ID}_plan_tier value = {tier} }}
\tset_global_variable = {{ name = {MOD_ID}_plan_go value = 1 }}
\t# **The guard is per pass and not across them.** It was one counter for all
\t# of them for one load, and the thirty-third run spent it on the scarce
\t# tiers: «кругов 12» on the screen, twenty-eight buildings out of a hundred
\t# and forty-four places, most locations holding one thing. The pass that
\t# fills the ground never ran at all.
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
\t\t\t# **The threshold, and it is the whole of the optimum.** The ground
\t\t\t# is dealt in descending order of gain across every good at once, so
\t\t\t# by the time a good that would gain a tenth reaches a location, the
\t\t\t# good that would have gained nine tenths has already taken it. That is
\t\t\t# the opportunity cost, paid for by one comparison rather than by
\t\t\t# asking every other good what it would have made of the place.
\t\t\t#
\t\t\t# `_pth<n>` and not `_plan_band`: the pass writes one threshold per
\t\t\t# good, the same band for all of them while the quota is binding and
\t\t\t# each good's own best once it is not. `_plan_th_absolute` and
\t\t\t# `_plan_th_relative` above.
\t\t\tlimit = {{
\t\t\t\t{MOD_ID}_plan_can_{side}_{index} = yes
\t\t\t\t{order_value} >= global_var:{MOD_ID}_pth{index}
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
	# **The rows first, and from here rather than from each caller.** Everything
	# that changes the plan ranks it afterwards -- the plan itself, a slot load,
	# «+1», «−1» -- so one call here is the whole of it, and no path can forget.
	{MOD_ID}_plan_rows = yes
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
\t\tmax = {PLAN_PROVS}
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
\t# stops at {PLAN_RANKED}, and a count that stopped with it would say the plan
\t# used exactly as many locations as the window can keep, whatever it really
\t# used.
\t#
\t# **And it walks `_plan_touched`, not `_candidates`.** The two are the same
\t# list for a plan just run -- the reset puts every candidate in it -- but a slot
\t# loaded from the editor puts a plan back on ground the picker may no longer
\t# hold, and walking the picker would then rank nothing while the map mode
\t# painted the plan. A plan is ranked over the ground it stands on.
\tset_global_variable = {{ name = {MOD_ID}_plan_found value = 0 }}
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_touched
\t\tlimit = {{ var:{MOD_ID}_load > 0 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_found add = 1 }}
\t}}
\t# **The rows are ranked whole and drawn a page at a time.** The datamodel is
\t# what costs, so the window still holds {PLAN_ROWS} rows at once -- but the plan
\t# has always used more ground than that, and cutting the list at the window's
\t# capacity is what made «показано всего 150 локаций» look like the answer
\t# stopping short. Every location keeps its place in the whole order and the page
\t# it falls on; the page buttons choose which of them the datamodel gets.
\t#
\t# The page is counted here rather than divided out afterwards: the counter is
\t# reset and the page stepped whenever a page fills, so the comparison is against
\t# a literal and there is no rounding to be wrong about.
\tset_global_variable = {{ name = {MOD_ID}_plan_shown value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_pages value = 1 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_pagec value = 0 }}
\tordered_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_touched
\t\tlimit = {{ var:{MOD_ID}_load > 0 }}
\t\torder_by = {MOD_ID}_plan_order
\t\tmax = {PLAN_RANKED}
\t\tcheck_range_bounds = no
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_shown add = 1 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_pagec add = 1 }}
\t\tif = {{
\t\t\tlimit = {{ global_var:{MOD_ID}_plan_pagec > {PLAN_ROWS} }}
\t\t\tset_global_variable = {{ name = {MOD_ID}_plan_pagec value = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_pages add = 1 }}
\t\t}}
\t\tset_variable = {{ name = {MOD_ID}_plan_rank value = global_var:{MOD_ID}_plan_shown }}
\t\tset_variable = {{ name = {MOD_ID}_plan_pg value = global_var:{MOD_ID}_plan_pages }}
\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_plan_ranked target = this }}
\t}}
\t# A new plan always opens on its first page; the old one's page may not exist.
\tset_global_variable = {{ name = {MOD_ID}_plan_page value = 1 }}
}}

# The window's own list, filled on opening and emptied on closing -- the same
# contract as the other two windows and for the same reason: a scripted widget
# never comes down, so emptying the datamodel is the only thing that frees a row.
#
# **One page of it, and the page bar says which.** `_plan_pg` was written on the
# location by the walk above, so choosing a page is one comparison per ranked
# location and no arithmetic at all -- the same shape as `var:{MOD_ID}_load <
# global_var:{MOD_ID}_plan_cap_urban`, which is the plan's own gate.
# Scope: country
{MOD_ID}_plan_show = {{
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_plan_page }} }}
\t\tset_global_variable = {{ name = {MOD_ID}_plan_page value = 1 }}
\t}}
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_plan_pages }} }}
\t\tset_global_variable = {{ name = {MOD_ID}_plan_pages value = 1 }}
\t}}
\t# **Clamped with an `if` and not with `min`/`max`.** `change_variable`'s
\t# `max = 1` is a floor -- `_plan_quota` above depends on it and says so -- but
\t# which way `min` runs is an inference and not a measurement, and getting it
\t# backwards here would jump the window to the last page on every open with
\t# nothing in any log to say why. A comparison between two globals is the form
\t# this file already lives on.
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_plan_page < 1 }}
\t\tset_global_variable = {{ name = {MOD_ID}_plan_page value = 1 }}
\t}}
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_plan_page > global_var:{MOD_ID}_plan_pages }}
\t\tset_global_variable = {{ name = {MOD_ID}_plan_page value = global_var:{MOD_ID}_plan_pages }}
\t}}
\t# The rows this page covers, for the bar above the table: it is the answer to
\t# «показано 150 из скольких» and it has to be readable without a log.
\tset_global_variable = {{ name = {MOD_ID}_plan_from value = global_var:{MOD_ID}_plan_page }}
\tchange_global_variable = {{ name = {MOD_ID}_plan_from subtract = 1 }}
\tchange_global_variable = {{ name = {MOD_ID}_plan_from multiply = {PLAN_ROWS} }}
\tset_global_variable = {{ name = {MOD_ID}_plan_to value = global_var:{MOD_ID}_plan_from }}
\tchange_global_variable = {{ name = {MOD_ID}_plan_to add = {PLAN_ROWS} }}
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_plan_to > global_var:{MOD_ID}_plan_shown }}
\t\tset_global_variable = {{ name = {MOD_ID}_plan_to value = global_var:{MOD_ID}_plan_shown }}
\t}}
\tchange_global_variable = {{ name = {MOD_ID}_plan_from add = 1 }}
\t# The bar itself is only drawn where there is more than one page, and a country
\t# variable is the one thing a `visible` can ask about without a data function.
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_plan_pages > 1 }}
\t\tset_variable = {{ name = {MOD_ID}_plan_paged value = 1 }}
\t}}
\telse = {{
\t\tremove_variable = {MOD_ID}_plan_paged
\t}}
\tclear_global_variable_list = {MOD_ID}_plan_results
\tordered_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_ranked
\t\tlimit = {{ var:{MOD_ID}_plan_pg = global_var:{MOD_ID}_plan_page }}
\t\torder_by = {MOD_ID}_plan_rank_order
\t\tmax = {PLAN_ROWS}
\t\tcheck_range_bounds = no
\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_plan_results target = this }}
\t}}
}}

# One page forward and one back, from the two buttons beside the page number.
# **Neither re-plans anything**: the answer is already ranked and every location
# knows its page, so a page turn is one walk over the ranked list.
# Scope: country
{MOD_ID}_plan_page_next_effect = {{
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_plan_page < global_var:{MOD_ID}_plan_pages }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_page add = 1 }}
\t\t{MOD_ID}_plan_show = yes
\t}}
}}

# Scope: country
{MOD_ID}_plan_page_prev_effect = {{
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_plan_page > 1 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_page subtract = 1 }}
\t\t{MOD_ID}_plan_show = yes
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


# **How many plans the mod keeps.** Three at the least, and the reason is his:
# «Т.е. ты говоришь, что я проебу свой сохранённый план, если захочу посмотреть
# какой-то план на другой земле - спасибо. … Слотов для планов должно быть
# минимум 3.» A slot is a global list of locations plus one list of goods on each
# of them, so the cost is per slot and per location the plan touched, and nothing
# at all for a slot never written.
EDIT_SLOTS = 3

# **The picker is rows, and the rows are cut here.** Ten cells of 104 plus their
# spacing is 1060 of the 1130 the window has; five rows hold the 47 goods this
# game has, and a ground that makes fewer simply leaves the last rows empty.
# Both wrapping widgets that would have made this one list are gone:
# `flowcontainer` crashed the game and `fixedgridbox` drew the cells on top of
# one another. `docs/pitfalls/interface.md`.
EDIT_ROW = 10
EDIT_ROWS = 5


# The picker's cells, generated into a `.gui` of types only.
#
# **A datamodel row cannot reach a numbered counter.** `_pn<n>` is how many
# buildings of a good the plan holds, and a row of a goods datamodel carries a
# scope: `Goods.Custom` does not exist, no global returns a good by key, and a
# variable map crashes the game. So the cell that has to print a number cannot
# be a datamodel row -- it has to be written out, one a good, which is what this
# does. `docs/pitfalls/interface.md`.
#
# **And writing them out removes the scope bridge as well.** A datamodel cell
# reached its effect through `AddScope('bag_wtp_good', Goods.MakeScope)`; a
# written cell calls `bag_wtp_pick_plus_<n>`, which knows its own number. One
# fewer thing between the press and the plan.
#
# Types live in their own file because `.gui` types are global once parsed --
# vanilla keeps its own in `gui/shared/` the same way -- and a file with no
# `window` in it needs no line in `scripted_widgets`.
EDIT_CELLS_OUT = MOD / "in_game/gui/bag_wtp_edit_cells.gui"


def edit_cells_file(order: list[str]) -> str:
    """Five rows of ten cells: «−1», the good's icon with its count, «+1».

    **Every cell is a static child of a plain `hbox`.** Both widgets that would
    have wrapped one list -- `flowcontainer`, `fixedgridbox` -- failed on their
    first load, one by crashing the game four builds running and one by drawing
    the cells on top of each other. Ten cells of 106 is 1060 of the 1130 the
    window has, and `ignoreinvisible` keeps the goods this ground cannot make
    from leaving holes.
    """
    rows = []
    for r in range(EDIT_ROWS):
        cells = ""
        for i in range(r * EDIT_ROW + 1, min((r + 1) * EDIT_ROW, len(order)) + 1):
            cells += f"""
		hbox = {{
			size = {{ 104 32 }}
			spacing = 1
			visible = "[GetPlayer.MakeScope.GetVariable('{MOD_ID}_pool{i}').IsSet]"

			widget = {{
				size = {{ 30 32 }}
				button_regular = {{
					size = {{ 28 26 }}
					parentanchor = center
					widgetanchor = center
					tooltip = "{MOD_ID}_edit_minus_tt"
					onclick = "[GetScriptedGui('{MOD_ID}_pick_minus_{i}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
					text_single = {{
						parentanchor = center
						widgetanchor = center
						autoresize = yes
						fontsize = 14
						text = "{MOD_ID}_edit_minus"
					}}
				}}
			}}

			widget = {{
				size = {{ 42 32 }}
				alwaystransparent = no
				tooltip = "{MOD_ID}_cell_tt"
				text_single = {{
					parentanchor = center
					widgetanchor = center
					autoresize = yes
					fontsize = 16
					text = "{MOD_ID}_cell_{i}"
				}}
			}}

			widget = {{
				size = {{ 30 32 }}
				button_regular = {{
					size = {{ 28 26 }}
					parentanchor = center
					widgetanchor = center
					tooltip = "{MOD_ID}_edit_plus_tt"
					onclick = "[GetScriptedGui('{MOD_ID}_pick_plus_{i}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
					text_single = {{
						parentanchor = center
						widgetanchor = center
						autoresize = yes
						fontsize = 14
						text = "{MOD_ID}_edit_plus"
					}}
				}}
			}}
		}}
"""
        rows.append(f"""
	# Goods {r * EDIT_ROW + 1}..{min((r + 1) * EDIT_ROW, len(order))} of the plan's own order.
	type {MOD_ID}_edit_row{r + 1} = hbox {{
		spacing = 2
		ignoreinvisible = yes
{cells}	}}
""")
    return (HEADER + f"""#
# The plan editor's picker, a cell a good. `{MOD_ID}_edit_window.gui` draws the
# five rows; this file only declares them, so it has no `window` and needs no
# line in `gui/scripted_widgets/`.

types BagWtpEditCells {{
{"".join(rows)}}}
""")


def editor_file(rows: list[eu5data.Method], split: dict[str, list[str]],
                game: eu5data.Game) -> tuple[str, str]:
    """Editing a plan that already exists, one building at a time.

    **The plan is state on the map, and this changes it in place.** The owner
    asked for this twice and the second time in nine numbered steps, 2026-09-03:
    «Мод не пересобирает весь план с 0, он просто точечно выбирает какой товар X
    менее болезненно удалить для наилучшей установки туда товара Y, без
    полномасштабного смещения всех товаров и прав.» What was built instead was a
    weight fed back into a full re-plan, and the run measured what that is worth:
    **42 locations of 48 changed** on a knob meant to move one.

    So «+1 домик» is exactly one building:

    1. every candidate is asked what it would cost to put this good there --
       nothing if the location has a free room, otherwise the gain of the
       cheapest building that may be taken out;
    2. the location where that costs least takes it;
    3. the victim comes out, the good goes in, and nothing else on the map moves.

    **What may not be taken out**, and neither rule is optional:

    - **a good's last building.** «Нельзя увеличивать число локаций чего-либо
      больше, если у какого-то товара будет угроза потерять последний домик» --
      so a good standing in exactly one place is never the victim, and the plan
      keeps its covering constraint through any amount of editing.
    - **a building the town's charter put there.** A charter is granted for its
      bundle; taking a bundle good out leaves the town holding a charter for
      something it does not make, which is worse than the edit is worth.

    **The picker is this window's own** and not the goods list the ranking uses --
    also his, and also from the second telling: «выбор товара для регуляции не
    должны быть в том же выборе товара для поиска лучшей локации».

    **And it is a window of its own, not a page of the mod's settings.** The
    first build put the picker and the buttons in the Mod Menu and he refused to
    open it, 2026-09-03: «Сейчас окно настроек мода - стало засраным и неудобным.
    Более того это именно что окно настроек и основных функций, я не хочу делать
    подобные вещи там.» So the goods are icons in `bag_wtp_edit_window.gui`, each
    chosen one gets a row with `-1`, its icon and `+1`, and the effects here are
    reached from those buttons through `{MOD_ID}_edit_set_good`, which takes the
    good as a scope instead of reading a dropdown.
    """
    order = [good for kind in ("raw", "made") for good in split[kind]]
    groups = plan_groups(rows, split, game)
    rights = output_rights(rows, game)

    def call(prefix: str, index: int, tab: str) -> str:
        """The two sides' effects, and only the ones that were generated.

        A good with no village building has no `_plan_try_rural_<n>`, and calling
        an effect that does not exist is the failure this repository names first:
        the block it sits in does nothing and the game says so nowhere useful.
        """
        good = order[index - 1]
        return "".join(
            f"{tab}{MOD_ID}_{prefix}_{listname}_{index} = yes\n"
            for side, listname in (("t", "town"), ("r", "rural"))
            if groups.get((good, side)))
    out = [HEADER, f"""#
# The plan editor. Everything here changes a plan that already exists and
# **nothing here re-runs the plan**: `{MOD_ID}_plan_run` is the only thing that
# does, and pressing it throws every edit away, which is why the save slot exists.
"""]
    gate = [HEADER, f"""#
# The editor's own questions. **Written with OR and AND and never an `if`**, the
# same rule every other scripted trigger here obeys.
"""]

    # ---- which good the editor is pointed at -------------------------------
    #
    # **It is a global, and the day it was a country variable cost three builds.**
    # `_edit_add` reads it in two scopes: at the top, where the scope is the
    # country, and again inside `ordered_in_global_list`, where the scope is the
    # **location** the walk stands on. A `var:` read there asks the location for
    # a variable only the country has, so `add_dispatch` matched nothing, ever --
    # the walk evicted a building, failed to place, and put the victim back. His
    # own report, 2026-09-04: `evicted=1 room=1 | placed_before=191
    # placed_after=192` with `done=0 fail=1`. Every «+1» and «−1» he pressed for
    # three builds died there.
    #
    # **A number the editor carries across scopes is a global. No exceptions.**
    #
    # **It is a number, and the buttons write it themselves.** An effect stood
    # here that took the good as a saved scope and walked 47 comparisons to turn
    # it into the plan's index, because every counter the plan keeps is numbered
    # -- `_pn<n>`, `_p<n>`, `_pm<n>` -- and a scope indexes none of them. The
    # picker stopped carrying scopes when its cells were written out, so
    # `_edit_plus_<n>` sets `_edit_good` to its own `n` and the bridge is gone.
    # `_edit_reached` stays: it is what tells «кнопка не донесла товар» apart
    # from a rule refusing, and the numbered effects set it.

    # ---- may this good stand here, room aside ------------------------------
    #
    # `_plan_can_*` is the placement gate and asks the room as well; an eviction
    # is precisely the case where there is no room, so the editor needs the same
    # question without that clause.
    for side, listname, method_var, rank in (("t", "town", "pm", "yes"),
                                             ("r", "rural", "prm", "no")):
        for index, good in enumerate(order, start=1):
            by_building = groups.get((good, side), {})
            if not by_building:
                gate.append(f"\n# Scope: location\n"
                            f"{MOD_ID}_edit_fits_{listname}_{index} = {{ always = no }}\n")
                continue
            branches = ""
            for building, mis in sorted(by_building.items()):
                tests = "".join("\t\t\t\tvar:%s_%s%d = %d\n" % (MOD_ID, method_var, index, mi)
                                for mi in sorted(mis))
                branches += (f"\t\tAND = {{\n\t\t\tOR = {{\n{tests}\t\t\t}}\n"
                             f"\t\t\tNOT = {{ is_target_in_variable_list = "
                             f"{{ name = {MOD_ID}_plan_builds target = building_type:{building} }} }}\n"
                             f"\t\t}}\n")
            gate.append(f"""
# {good}, {"town" if side == "t" else "village"} side, room not asked.
# Scope: location
{MOD_ID}_edit_fits_{listname}_{index} = {{
\tvar:{MOD_ID}_{method_var}{index} > 0
\t{MOD_ID}_plan_is_town = {rank}
\tNOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} }}
\tOR = {{
{branches}\t}}
}}
""")

    # ---- a bundle good of the charter granted here --------------------------
    #
    # **A charter's buildings are taken whole or not at all**, and this is the
    # second thing he said about them. On 2026-09-04 he struck the lock out --
    # «городские права и их домики не должны быть жёстко зарезервированы» -- and
    # then, having seen what that does, drew the line properly:
    #
    #   «Не должно происходить ситуации, когда в городе у которого допустим
    #    ремесленные права — он теряет все свои бонусные дома… Я бы предпочёл не
    #    забирать домики по частям у городских прав. Я бы скорее предпочёл
    #    забирать у города целиком всю связку право+его домики.»
    #
    # So piecemeal eviction is off again, and **taking the whole bundle is the
    # thing to build** -- «+1»/«−1» for the charters themselves, which he asked
    # for in the same breath. Until that exists this lock is the honest state:
    # a town keeps the buildings its charter is for.
    for index, good in enumerate(order, start=1):
        holders = [k for k, right in enumerate(rights, start=1) if good in right.output]
        if not holders:
            gate.append(f"\n# Scope: location\n"
                        f"{MOD_ID}_edit_locked_{index} = {{ always = no }}\n")
            continue
        tests = "".join(f"\t\tvar:{MOD_ID}_plan_right = {k}\n" for k in holders)
        gate.append(f"""
# {good} is in the bundle of the charter granted here, so the editor takes it out
# only with the charter itself -- never on its own.
# Scope: location
{MOD_ID}_edit_locked_{index} = {{
\thas_variable = {MOD_ID}_plan_right
\tOR = {{
{tests}\t}}
}}
"""  )


    # ---- the cheapest building this location could give up -----------------
    #
    # Good-independent, so it is worked out once a location and read by whichever
    # good is being added. Written as its own effect for that reason: inlined per
    # good it would be 47 x 94 blocks and the file would be unreadable.
    worst = {}
    for side, gain_var in (("t", "p"), ("r", "pr")):
        worst[side] = "".join(f"""\t\tif = {{
\t\t\tlimit = {{
\t\t\t\tis_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }}
\t\t\t\tglobal_var:{MOD_ID}_pn{index} > 1
\t\t\t\tNOT = {{ {MOD_ID}_edit_locked_{index} = yes }}
\t\t\t\tOR = {{
\t\t\t\t\tvar:{MOD_ID}_esw = -1
\t\t\t\t\tvar:{MOD_ID}_p{index} < var:{MOD_ID}_esw
\t\t\t\t}}
\t\t\t}}
\t\t\tset_variable = {{ name = {MOD_ID}_esw value = var:{MOD_ID}_{gain_var}{index} }}
\t\t\tset_variable = {{ name = {MOD_ID}_esg value = {index} }}
\t\t}}
""".replace(f"var:{MOD_ID}_p{index} < var:{MOD_ID}_esw",
            f"var:{MOD_ID}_{gain_var}{index} < var:{MOD_ID}_esw")
        for index, good in enumerate(order, start=1))
    out.append(f"""
# The building this location would give up most cheaply, and which good it is.
#
# `-1` in `_esw` means "nothing here may be taken out at all" -- every building
# is either its good's last on the ground or part of the town's charter bundle.
# **A gain of nought is a real answer and `-1` is not**, which is why the empty
# marker cannot be nought: a good the ground feeds nothing is exactly the one an
# edit should be taking out first.
# Scope: location
{MOD_ID}_edit_worst = {{
\tset_variable = {{ name = {MOD_ID}_esw value = -1 }}
\tset_variable = {{ name = {MOD_ID}_esg value = 0 }}
\tif = {{
\t\tlimit = {{ {MOD_ID}_plan_is_town = yes }}
{worst["t"]}\t}}
\telse = {{
{worst["r"]}\t}}
}}
""")

    # ---- what it would cost to put this good here --------------------------
    for index, good in enumerate(order, start=1):
        arms = []
        for side, listname, cap, gain_var in (("t", "town", "urban", "p"),
                                              ("r", "rural", "rural", "pr")):
            arms.append(f"""\t\tif = {{
\t\t\tlimit = {{ {MOD_ID}_edit_fits_{listname}_{index} = yes }}
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_load < global_var:{MOD_ID}_plan_cap_{cap} }}
\t\t\t\t# A free room costs nothing, so it always outbids an eviction.
\t\t\t\tset_variable = {{ name = {MOD_ID}_esc value = 1 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_esv value = var:{MOD_ID}_{gain_var}{index} }}
\t\t\t\tchange_variable = {{ name = {MOD_ID}_esv add = {RANK_SCALE} }}
\t\t\t}}
\t\t\telse_if = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_esw >= 0 var:{MOD_ID}_esg > 0 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_esc value = 1 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_esv value = var:{MOD_ID}_{gain_var}{index} }}
\t\t\t\tchange_variable = {{ name = {MOD_ID}_esv subtract = var:{MOD_ID}_esw }}
\t\t\t}}
\t\t}}
""")
        out.append(f"""
# {good}: what every candidate would charge for one more of it.
# Scope: country
{MOD_ID}_edit_scan_{index} = {{
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_candidates
{"".join(arms)}\t}}
}}
""")

    # ---- taking one building out -------------------------------------------
    for side, listname, method_var, gain_var in (("t", "town", "pm", "p"),
                                                 ("r", "rural", "prm", "pr")):
        for index, good in enumerate(order, start=1):
            by_building = groups.get((good, side), {})
            if not by_building:
                continue
            branches = ""
            for building, mis in sorted(by_building.items()):
                tests = "".join("\t\t\t\tvar:%s_%s%d = %d\n" % (MOD_ID, method_var, index, mi)
                                for mi in sorted(mis))
                branches += f"""\t\tif = {{
\t\t\tlimit = {{ OR = {{
{tests}\t\t\t}} }}
\t\t\tremove_list_variable = {{ name = {MOD_ID}_plan_builds target = building_type:{building} }}
\t\t}}
"""
            out.append(f"""
# {good} out of this location, {"town" if side == "t" else "village"} side.
#
# **Every counter the plan keeps is walked back**, because the report and the
# next edit both read them: the load, the total placed, this good's own count,
# and the two gain counters the header prints.
# Scope: location
{MOD_ID}_edit_remove_{listname}_{index} = {{
\tif = {{
\t\tlimit = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} }}
\t\tremove_list_variable = {{ name = {MOD_ID}_plan_goods target = goods:{good} }}
{branches}\t\tchange_variable = {{ name = {MOD_ID}_load subtract = 1 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_placed subtract = 1 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_pn{index} subtract = 1 }}
\t\tchange_global_variable = {{ name = {MOD_ID}_plan_gain subtract = var:{MOD_ID}_{gain_var}{index} }}
\t\tif = {{
\t\t\tlimit = {{ var:{MOD_ID}_{gain_var}{index} > 0 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_fed subtract = 1 }}
\t\t}}
\t}}
}}
""")

    # ---- the two operations -------------------------------------------------
    scan_dispatch = "".join(
        f"\t\tif = {{ limit = {{ global_var:{MOD_ID}_edit_good = {i} }} {MOD_ID}_edit_scan_{i} = yes }}\n"
        for i in range(1, len(order) + 1))
    # How many locations could hold this good at all, room and victims aside.
    fit_dispatch = "".join(
        f"\t\tif = {{\n\t\t\tlimit = {{ global_var:{MOD_ID}_edit_good = {i} }}\n"
        f"\t\t\tevery_in_global_list = {{\n"
        f"\t\t\t\tvariable = {MOD_ID}_candidates\n"
        f"\t\t\t\tlimit = {{ OR = {{ {MOD_ID}_edit_fits_town_{i} = yes "
        f"{MOD_ID}_edit_fits_rural_{i} = yes }} }}\n"
        f"\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_edit_fitn add = 1 }}\n"
        f"\t\t\t}}\n\t\t}}\n"
        for i in range(1, len(order) + 1))
    remove_dispatch = "".join(
        f"\t\t\tif = {{ limit = {{ var:{MOD_ID}_esg = {i} }}\n"
        f"{call('edit_remove', i, chr(9) * 4)}\t\t\t}}\n"
        for i in range(1, len(order) + 1))
    add_dispatch = "".join(
        f"\t\t\t\tif = {{ limit = {{ global_var:{MOD_ID}_edit_good = {i} }}\n"
        f"{call('edit_place', i, chr(9) * 5)}\t\t\t\t}}\n"
        for i in range(1, len(order) + 1))
    # The victim put back where it stood, keyed by `_esg` rather than by the
    # good the press asked for. Same effects: a building that stood here a
    # moment ago passes `_plan_can_*` again by construction.
    restore_dispatch = "".join(
        f"\t\t\t\t\tif = {{ limit = {{ var:{MOD_ID}_esg = {i} }}\n"
        f"{call('edit_place', i, chr(9) * 6)}\t\t\t\t\t}}\n"
        for i in range(1, len(order) + 1))
    held = "".join(
        f"\tif = {{ limit = {{ global_var:{MOD_ID}_edit_good = {i} }} "
        f"set_global_variable = {{ name = {MOD_ID}_edit_fitn "
        f"value = global_var:{MOD_ID}_pn{i} }} }}\n"
        for i in range(1, len(order) + 1))
    out.append(f"""
# How many buildings of the chosen good stand on the ground right now.
#
# `_edit_fitn` means «where could it go» for «+1» and «how many are there» for
# «−1», because the two answers are what the window has to say when a press does
# nothing and the two questions never both apply.
# Scope: country
{MOD_ID}_edit_count_held = {{
\tset_global_variable = {{ name = {MOD_ID}_edit_fitn value = 0 }}
{held}}}

""")

    out.append(f"""
# The walk's trace, cleared before every press.
#
# **Zero and «no walk happened» must not look alike.** `_ev_hit` is 0 when the
# ordered walk found no candidate at all, and 1 when it stood somewhere -- and
# then the rest of these say what it saw there. The diagnostics print them; that
# is the whole reason they exist. The owner, 2026-09-04: «Добавляй скан
# информации для себя в диагностике на функцию редактора, чтобы ты видел чё там
# происходит.»
# Scope: country
{MOD_ID}_edit_clear_trace = {{
\tset_global_variable = {{ name = {MOD_ID}_ev_hit value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_ev_town value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_ev_load value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_ev_load2 value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_ev_esg value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_ev_esw value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_evicted value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_room value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_mark value = 0 }}
}}

# **One more building of the chosen good, and exactly one.**
#
# The ordered walk is the whole of the choice: `_esv` is what each candidate
# charges -- a free room charges nothing and outbids everything, an eviction
# charges the victim's gain -- so the highest is the least painful place, and
# `max = 1` takes it and stops. Both sides' effects are called and the one whose
# side the location is not simply does nothing, which is cheaper than asking.
# Scope: country
{MOD_ID}_edit_add = {{
\t# **The press counter, and it is a probe rather than a nicety.** A press that
\t# never reaches its effect and a press that reaches it and is refused look the
\t# same on screen -- «ничего не изменилось» -- and telling them apart has cost
\t# two runs. The window prints this number, so one look answers it: click five
\t# times, the number does not move, the button is not wired.
\tchange_global_variable = {{ name = {MOD_ID}_edit_presses add = 1 }}
\t{MOD_ID}_edit_clear_trace = yes
\tset_global_variable = {{ name = {MOD_ID}_edit_done value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_fail value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_norefill value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_op value = 1 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_fitn value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_cands value = 0 }}
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_edit_good > 0 }}
\t\tevery_in_global_list = {{
\t\t\tvariable = {MOD_ID}_candidates
\t\t\tset_variable = {{ name = {MOD_ID}_esc value = 0 }}
\t\t\tset_variable = {{ name = {MOD_ID}_esv value = 0 }}
\t\t\t{MOD_ID}_edit_worst = yes
\t\t}}
{fit_dispatch}{scan_dispatch}\t\t# **Two counts, because two different things read as «не дало правило».**
\t\t# `_edit_fitn` is how many locations could hold this good at all -- the
\t\t# ground's own answer, and 0 means it already stands everywhere this land
\t\t# can make it. `_edit_cands` is how many of those had a free room or a
\t\t# building that may be taken out. The owner pressed «+1» on iron and was
\t\t# told a rule refused it; iron can be made in four locations of Westphalia
\t\t# and stood in all four. That is the ground, not a rule, and saying so
\t\t# needs the number.
\t\tevery_in_global_list = {{
\t\t\tvariable = {MOD_ID}_candidates
\t\t\tlimit = {{ var:{MOD_ID}_esc = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_edit_cands add = 1 }}
\t\t}}
\t\tordered_in_global_list = {{
\t\t\tvariable = {MOD_ID}_candidates
\t\t\tlimit = {{ var:{MOD_ID}_esc = 1 }}
\t\t\torder_by = {MOD_ID}_edit_order
\t\t\tmax = 1
\t\t\tcheck_range_bounds = no
\t\t\t# **One rule, and the walk owns the room.**
\t\t\t#
\t\t\t# The editor no longer asks the plan whether a building may stand here.
\t\t\t# `_plan_can_*` wants a free room; the editor makes the room itself, so it
\t\t\t# asks `_edit_fits_*` -- the same test with that clause removed -- and
\t\t\t# **the scan and the placement are then the same predicate**. They used to
\t\t\t# be two, and the day they disagreed the window said «поставить не
\t\t\t# удалось, и всё осталось как было» with nothing able to say why.
\t\t\t#
\t\t\t# So: evict when the location is full and has a victim, then place if the
\t\t\t# room is actually free. `_edit_worst` names a victim on every candidate
\t\t\t# -- the picker's markers need that -- so «full» and «has a victim» are
\t\t\t# asked here rather than assumed.
\t\t\t# **What the walk stood on, parked for the report.** A `debug_log` string
\t\t\t# cannot reach the item a walk is standing on, so the numbers that decide
\t\t\t# everything here -- the location's load, its victim, whether it counts as
\t\t\t# a town -- have to be copied into globals as they are read. Without this
\t\t\t# the editor is the one part of the mod the diagnostics cannot see, and
\t\t\t# 2026-09-04 is what that costs: 27 buildings over the cap and four
\t\t\t# theories about why.
\t\t\tset_global_variable = {{ name = {MOD_ID}_ev_hit value = 1 }}
\t\t\tset_global_variable = {{ name = {MOD_ID}_ev_town value = 0 }}
\t\t\tif = {{ limit = {{ {MOD_ID}_plan_is_town = yes }}
\t\t\t\tset_global_variable = {{ name = {MOD_ID}_ev_town value = 1 }} }}
\t\t\tset_global_variable = {{ name = {MOD_ID}_ev_load value = var:{MOD_ID}_load }}
\t\t\tset_global_variable = {{ name = {MOD_ID}_ev_esg value = var:{MOD_ID}_esg }}
\t\t\tset_global_variable = {{ name = {MOD_ID}_ev_esw value = var:{MOD_ID}_esw }}
\t\t\tset_global_variable = {{ name = {MOD_ID}_edit_evicted value = 0 }}
\t\t\tset_global_variable = {{ name = {MOD_ID}_edit_room value = 0 }}
\t\t\tif = {{
\t\t\t\tlimit = {{
\t\t\t\t\tvar:{MOD_ID}_esg > 0
\t\t\t\t\tOR = {{
\t\t\t\t\t\tAND = {{ {MOD_ID}_plan_is_town = yes
\t\t\t\t\t\t\tvar:{MOD_ID}_load >= global_var:{MOD_ID}_plan_cap_urban }}
\t\t\t\t\t\tAND = {{ {MOD_ID}_plan_is_town = no
\t\t\t\t\t\t\tvar:{MOD_ID}_load >= global_var:{MOD_ID}_plan_cap_rural }}
\t\t\t\t\t}}
\t\t\t\t}}
{remove_dispatch}\t\t\t\tset_global_variable = {{ name = {MOD_ID}_edit_evicted value = 1 }}
\t\t\t}}
\t\t\tif = {{
\t\t\t\tlimit = {{ OR = {{
\t\t\t\t\tAND = {{ {MOD_ID}_plan_is_town = yes
\t\t\t\t\t\tvar:{MOD_ID}_load < global_var:{MOD_ID}_plan_cap_urban }}
\t\t\t\t\tAND = {{ {MOD_ID}_plan_is_town = no
\t\t\t\t\t\tvar:{MOD_ID}_load < global_var:{MOD_ID}_plan_cap_rural }}
\t\t\t\t}} }}
\t\t\t\tset_global_variable = {{ name = {MOD_ID}_edit_room value = 1 }}
\t\t\t}}
\t\t\t# **And nothing is ever lost.** The count is taken after the eviction, so
\t\t\t# one comparison answers both cases: the plan grew, or it did not and the
\t\t\t# victim goes straight back. A press that cannot do what it says must cost
\t\t\t# nothing, and `_edit_fail` is what makes the window say so.
\t\t\tset_global_variable = {{ name = {MOD_ID}_edit_mark value = global_var:{MOD_ID}_plan_placed }}
\t\t\tif = {{
\t\t\t\tlimit = {{ global_var:{MOD_ID}_edit_room = 1 }}
{add_dispatch}\t\t\t}}
\t\t\tif = {{
\t\t\t\tlimit = {{ global_var:{MOD_ID}_plan_placed > global_var:{MOD_ID}_edit_mark }}
\t\t\t\tset_global_variable = {{ name = {MOD_ID}_edit_done value = 1 }}
\t\t\t}}
\t\t\telse = {{
\t\t\t\tset_global_variable = {{ name = {MOD_ID}_edit_fail value = 1 }}
\t\t\t\tif = {{
\t\t\t\t\tlimit = {{ global_var:{MOD_ID}_edit_evicted = 1 }}
{restore_dispatch}\t\t\t\t}}
\t\t\t}}
\t\t\tset_global_variable = {{ name = {MOD_ID}_ev_load2 value = var:{MOD_ID}_load }}
\t\t}}
\t}}
\t{MOD_ID}_plan_rank = yes
\t# **And the window's rows again.** A location the edit gave its first building
\t# is not in `_plan_results` and would not appear until something else refilled
\t# it; the goods already in a row read live off the location, so without this
\t# an edit is half-visible, which is the worst of the three states.
\t{MOD_ID}_plan_show = yes
}}

# **One building of the chosen good taken out, and the room given to whatever
# suits it best afterwards.** «Он уступает место тому у чего забрал слоты.»
#
# The walk takes the good's *worst* placement, which is why the scan stores
# `{RANK_SCALE} - gain`: `order_by` reads highest-first and there is no other way
# to ask it for a minimum.
# Scope: country
{MOD_ID}_edit_drop = {{
\tchange_global_variable = {{ name = {MOD_ID}_edit_presses add = 1 }}
\t{MOD_ID}_edit_clear_trace = yes
\tset_global_variable = {{ name = {MOD_ID}_edit_done value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_fail value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_norefill value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_op value = 2 }}
\t{MOD_ID}_edit_count_held = yes
\tset_global_variable = {{ name = {MOD_ID}_edit_cands value = 0 }}
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_edit_good > 0 }}
\t\tevery_in_global_list = {{
\t\t\tvariable = {MOD_ID}_candidates
\t\t\tset_variable = {{ name = {MOD_ID}_esc value = 0 }}
\t\t\tset_variable = {{ name = {MOD_ID}_esv value = 0 }}
\t\t}}
""")
    for index, good in enumerate(order, start=1):
        out.append(f"""\t\tif = {{
\t\t\tlimit = {{ global_var:{MOD_ID}_edit_good = {index} global_var:{MOD_ID}_pn{index} > 1 }}
\t\t\tevery_in_global_list = {{
\t\t\t\tvariable = {MOD_ID}_candidates
\t\t\t\tlimit = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_esc value = 1 }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_esv value = {RANK_SCALE} }}
\t\t\t\tif = {{
\t\t\t\t\tlimit = {{ {MOD_ID}_plan_is_town = yes }}
\t\t\t\t\tchange_variable = {{ name = {MOD_ID}_esv subtract = var:{MOD_ID}_p{index} }}
\t\t\t\t}}
\t\t\t\telse = {{
\t\t\t\t\tchange_variable = {{ name = {MOD_ID}_esv subtract = var:{MOD_ID}_pr{index} }}
\t\t\t\t}}
\t\t\t}}
\t\t}}
""")
    drop_dispatch = "".join(
        f"\t\t\tif = {{ limit = {{ global_var:{MOD_ID}_edit_good = {i} }}\n"
        f"{call('edit_remove', i, chr(9) * 4)}\t\t\t}}\n"
        for i in range(1, len(order) + 1))
    fill = "".join(
        f"\t\t\tif = {{\n"
        f"\t\t\t\tlimit = {{\n"
        # **Never the good that just left.** It fits by construction -- it stood
        # here a moment ago -- and it is almost always the best fit as well, so
        # without this «−1» removes a building and hands the room straight back
        # to the same good. The press then reports «сделано» and nothing on the
        # map has changed, which is what he saw on 2026-09-04.
        f"\t\t\t\t\tNOT = {{ global_var:{MOD_ID}_edit_good = {i} }}\n"
        f"\t\t\t\t\tOR = {{ {MOD_ID}_edit_fits_town_{i} = yes {MOD_ID}_edit_fits_rural_{i} = yes }}\n"
        f"\t\t\t\t\tOR = {{\n"
        f"\t\t\t\t\t\tAND = {{ {MOD_ID}_plan_is_town = yes var:{MOD_ID}_p{i} > var:{MOD_ID}_esw }}\n"
        f"\t\t\t\t\t\tAND = {{ {MOD_ID}_plan_is_town = no var:{MOD_ID}_pr{i} > var:{MOD_ID}_esw }}\n"
        f"\t\t\t\t\t}}\n"
        f"\t\t\t\t}}\n"
        f"\t\t\t\tif = {{ limit = {{ {MOD_ID}_plan_is_town = yes }}\n"
        f"\t\t\t\t\tset_variable = {{ name = {MOD_ID}_esw value = var:{MOD_ID}_p{i} }} }}\n"
        f"\t\t\t\telse = {{ set_variable = {{ name = {MOD_ID}_esw value = var:{MOD_ID}_pr{i} }} }}\n"
        f"\t\t\t\tset_variable = {{ name = {MOD_ID}_esg value = {i} }}\n"
        f"\t\t\t}}\n"
        for i in range(1, len(order) + 1))
    fill_dispatch = "".join(
        f"\t\t\tif = {{ limit = {{ var:{MOD_ID}_esg = {i} }}\n"
        f"{call('edit_place', i, chr(9) * 4)}\t\t\t}}\n"
        for i in range(1, len(order) + 1))
    out.append(f"""\t\tevery_in_global_list = {{
\t\t\tvariable = {MOD_ID}_candidates
\t\t\tlimit = {{ var:{MOD_ID}_esc = 1 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_edit_cands add = 1 }}
\t\t}}
\t\tordered_in_global_list = {{
\t\t\tvariable = {MOD_ID}_candidates
\t\t\tlimit = {{ var:{MOD_ID}_esc = 1 }}
\t\t\torder_by = {MOD_ID}_edit_order
\t\t\tmax = 1
\t\t\tcheck_range_bounds = no
{drop_dispatch}\t\t\t# The room is free now; the best good that may stand here takes it.
\t\t\tset_variable = {{ name = {MOD_ID}_esw value = -1 }}
\t\t\tset_variable = {{ name = {MOD_ID}_esg value = 0 }}
{fill}{fill_dispatch}\t\t\t# **Whether anything took the room.** «−1» has done its job either way --
\t\t\t# the building is out, which is what was asked -- but «освободилось и
\t\t\t# занять нечем» and «освободилось, встал такой-то» are different answers
\t\t\t# and the window has to give the right one.
\t\t\tif = {{
\t\t\t\tlimit = {{ var:{MOD_ID}_esg = 0 }}
\t\t\t\tset_global_variable = {{ name = {MOD_ID}_edit_norefill value = 1 }}
\t\t\t}}
\t\t\tset_global_variable = {{ name = {MOD_ID}_edit_done value = 1 }}
\t\t}}
\t}}
\t{MOD_ID}_plan_rank = yes
\t# **And the window's rows again.** A location the edit gave its first building
\t# is not in `_plan_results` and would not appear until something else refilled
\t# it; the goods already in a row read live off the location, so without this
\t# an edit is half-visible, which is the worst of the three states.
\t{MOD_ID}_plan_show = yes
}}
""")

    # ---- the save slot ------------------------------------------------------
    save_copy = "".join(
        f"\t\tif = {{ limit = {{ is_target_in_variable_list = "
        f"{{ name = {MOD_ID}_plan_goods target = goods:{good} }} }} "
        f"add_to_variable_list = {{ name = {MOD_ID}_save_goods target = goods:{good} }} }}\n"
        for good in order)
    out.append(f"""
# **The baseline every «изменено» is measured against.**
#
# Written by `{MOD_ID}_plan_run` as well, so a fresh plan is its own baseline and
# the changes list right after one is empty -- which is the true answer, since a
# new plan has not been edited. Saving a slot re-bases it too, and so does
# loading one: «показать изменения» always answers «что я поменял с тех пор, как
# сохранил или загрузил», and never «чем этот план отличается от какого-то
# другого».
#
# Only the goods are kept. The building each good used is `_pm<n>`, which the
# scoring pass writes and no edit touches, so restoring puts it back from the
# good alone and the baseline needs no second list.
# Scope: country
{MOD_ID}_edit_save = {{
\tclear_global_variable_list = {MOD_ID}_save_locs
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_touched
\t\tclear_variable_list = {MOD_ID}_save_goods
{save_copy}\t\tset_variable = {{ name = {MOD_ID}_save_load value = var:{MOD_ID}_load }}
\t\tremove_variable = {MOD_ID}_save_right
\t\tif = {{
\t\t\tlimit = {{ has_variable = {MOD_ID}_plan_right }}
\t\t\tset_variable = {{ name = {MOD_ID}_save_right value = var:{MOD_ID}_plan_right }}
\t\t}}
\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_save_locs target = this }}
\t}}
\tset_global_variable = {{ name = {MOD_ID}_save_n value = global_var:{MOD_ID}_plan_placed }}
}}
""")

    # **There is no «вернуть сохранённое» of its own any more.** It was a button
    # on the settings page and the slots do the same thing better: loading slot N
    # is restoring, and there are three of them. The baseline `_save_*` stays --
    # it is what «показать изменения» counts against -- but nothing puts it back
    # on the map, so the effect that did was removed rather than left unreachable.

    # ---- one pair of effects per good --------------------------------------
    #
    # **The good is named, not carried.** A picker cell is written out, so it
    # knows its own number and can call an effect that knows it too. The
    # datamodel cell it replaces had to hand the good over as a saved scope --
    # `AddScope('bag_wtp_good', Goods.MakeScope)` -- and a scope reaches no
    # numbered counter, so the count could never be drawn beside it. One fewer
    # thing between the press and the plan, and the number arrives with it.
    out.append("".join(
        f"""
# «+1» for {good}.
# Scope: country
{MOD_ID}_edit_plus_{i} = {{
\tset_global_variable = {{ name = {MOD_ID}_edit_good value = {i} }}
\tset_global_variable = {{ name = {MOD_ID}_edit_reached value = 1 }}
\t{MOD_ID}_edit_add = yes
}}

# «−1» for {good}.
# Scope: country
{MOD_ID}_edit_minus_{i} = {{
\tset_global_variable = {{ name = {MOD_ID}_edit_good value = {i} }}
\tset_global_variable = {{ name = {MOD_ID}_edit_reached value = 1 }}
\t{MOD_ID}_edit_drop = yes
}}
"""
        for i, good in enumerate(order, start=1)))

    # ---- the numbered slots -------------------------------------------------
    #
    # **Three plans kept side by side**, and the reason is his: «я проебу свой
    # сохранённый план, если захочу посмотреть какой-то план на другой земле».
    # A slot holds what the baseline holds -- the goods on each location the plan
    # touched, the load, the charter -- under a name of its own, and writing one
    # re-bases the changes list as well, so «показать изменения» after a save is
    # empty and after an edit is the edit.
    #
    # **A slot is restored through `_plan_try_*` and not by writing the lists
    # back.** The building a good uses is `_pm<n>`, which the scoring pass wrote
    # and no edit touches, so the good alone is enough to put the building back --
    # and a restored plan is then counted by the very same effects that counted
    # the planned one, with no second accounting to drift. The price is that a
    # slot saved on ground that has since been re-scored comes back scored the new
    # way, which is the honest answer rather than a stale one.
    for slot in range(1, EDIT_SLOTS + 1):
        keep = "".join(
            f"\t\tif = {{ limit = {{ is_target_in_variable_list = "
            f"{{ name = {MOD_ID}_plan_goods target = goods:{good} }} }} "
            f"add_to_variable_list = {{ name = {MOD_ID}_sl{slot}_goods target = goods:{good} }} }}\n"
            for good in order)
        given = "".join(
            f"\t\t\t\tif = {{ limit = {{ var:{MOD_ID}_sl{slot}_right = {k} }} "
            f"change_global_variable = {{ name = {MOD_ID}_rgiven{k} add = 1 }} }}\n"
            for k in range(1, len(rights) + 1))
        put = "".join(
            f"\t\t\tif = {{ limit = {{ is_target_in_variable_list = "
            f"{{ name = {MOD_ID}_sl{slot}_goods target = goods:{good} }} }}\n"
            f"{call('plan_try', i, chr(9) * 4)}\t\t\t}}\n"
            for i, good in enumerate(order, start=1))
        out.append(f"""
# Slot {slot}: the plan as it stands now, kept under a name of its own.
# Scope: country
{MOD_ID}_edit_store_{slot} = {{
\tclear_global_variable_list = {MOD_ID}_sl{slot}_locs
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_touched
\t\tclear_variable_list = {MOD_ID}_sl{slot}_goods
{keep}\t\tset_variable = {{ name = {MOD_ID}_sl{slot}_load value = var:{MOD_ID}_load }}
\t\tremove_variable = {MOD_ID}_sl{slot}_right
\t\tif = {{
\t\t\tlimit = {{ has_variable = {MOD_ID}_plan_right }}
\t\t\tset_variable = {{ name = {MOD_ID}_sl{slot}_right value = var:{MOD_ID}_plan_right }}
\t\t}}
\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_sl{slot}_locs target = this }}
\t}}
\tset_global_variable = {{ name = {MOD_ID}_sl{slot}_n value = global_var:{MOD_ID}_plan_placed }}
\tset_global_variable = {{ name = {MOD_ID}_sl{slot}_locn value = global_var:{MOD_ID}_plan_shown }}
\t# The saved plan is what the next «показать изменения» is measured against.
\t{MOD_ID}_edit_save = yes
}}

# Slot {slot} back onto the map, in place of whatever the plan holds now.
# Scope: country
{MOD_ID}_edit_load_{slot} = {{
\tif = {{
\t\tlimit = {{ global_var:{MOD_ID}_sl{slot}_n > 0 }}
\t\t{MOD_ID}_edit_clear_plan = yes
\t\tevery_in_global_list = {{
\t\t\tvariable = {MOD_ID}_sl{slot}_locs
\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_plan_touched target = this }}
\t\t\tif = {{
\t\t\t\tlimit = {{ has_variable = {MOD_ID}_sl{slot}_right }}
\t\t\t\tset_variable = {{ name = {MOD_ID}_plan_right value = var:{MOD_ID}_sl{slot}_right }}
\t\t\t\t# **The charter counters are rebuilt and not left where the last plan
\t\t\t\t# put them.** `_rgiven<k>` is what the diagnosis prints as «выдано» and
\t\t\t\t# `_plan_rightn` is the number on the window; a slot loaded over a plan
\t\t\t\t# for other ground would otherwise report that ground's charters, which
\t\t\t\t# is a wrong number rather than a missing one.
\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_plan_rightn add = 1 }}
{given}\t\t\t}}
{put}\t\t}}
\t\t{MOD_ID}_plan_rank = yes
\t\t{MOD_ID}_plan_show = yes
\t\t# The loaded plan is the baseline, so the changes list starts empty here.
\t\t{MOD_ID}_edit_save = yes
\t}}
}}
""")
    zero_counts = "".join(
        f"\tset_global_variable = {{ name = {MOD_ID}_pn{i} value = 0 }}\n"
        for i in range(1, len(order) + 1))
    zero_counts += "".join(
        f"\tset_global_variable = {{ name = {MOD_ID}_rgiven{k} value = 0 }}\n"
        for k in range(1, len(rights) + 1))
    out.append(f"""
# Every location the plan stands on emptied, and every counter with it. Shared by
# the restore and by each slot's load, because a plan half-cleared is the failure
# that shows up as a number rather than as an error.
# Scope: country
{MOD_ID}_edit_clear_plan = {{
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_touched
\t\tclear_variable_list = {MOD_ID}_plan_goods
\t\tclear_variable_list = {MOD_ID}_plan_builds
\t\tset_variable = {{ name = {MOD_ID}_load value = 0 }}
\t\tremove_variable = {MOD_ID}_plan_right
\t}}
\tclear_global_variable_list = {MOD_ID}_plan_touched
\tset_global_variable = {{ name = {MOD_ID}_plan_placed value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_gain value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_fed value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_plan_rightn value = 0 }}
{zero_counts}}}
""")

    # ---- the editor window's own two lists ----------------------------------
    #
    # **The picker offers what this ground can make and nothing else, and every
    # row of it carries its own «−1» and «+1».** 47 icons of which half are
    # impossible here is a worse picker than 20 that are all real, and `_ng<n>` --
    # how many candidates can make the good, counted by the plan's own scan -- is
    # the number that says which.
    #
    # **There is no second list of «goods being worked on» any more.** There was,
    # and clicking a good's icon put it there with the buttons beside it; he
    # opened the window and found no way in, 2026-09-03: «там только их иконки и
    # ничего больше, что могло бы дать мне инструмент влияния, никаких кнопочек
    # +1 или -1». Controls you have to discover by clicking are controls that are
    # not there. Now every good the ground can make has its buttons in place, one
    # row each, and nothing is hidden behind a first click.
    #
    # **`has_global_variable` before the comparison.** `_ng<n>` is written by the
    # scoring pass and by nothing else, so before the first plan of a save it does
    # not exist -- and a `limit` reading a global that is not there is the failure
    # this repository names first. Here the wrong answer and the right one happen
    # to agree (no plan, nothing to edit), which is how such a thing survives.
    # **The picker is dealt into rows here, in script, and not by the window.**
    # `EDIT_ROW` goods to a row, `EDIT_ROWS` rows, each its own list. That is
    # what lets the window draw the picker with an `hbox` over a datamodel --
    # the one horizontal list this mod has drawn correctly since its first
    # build, in every location's goods row -- instead of a wrapping widget.
    #
    # Two wrapping widgets were tried and both failed on their first load. A
    # `flowcontainer` with a datamodel killed the game outright, four builds
    # running, silently (`docs/pitfalls/interface.md`). A `fixedgridbox` did not
    # crash but laid the cells out wrong -- some past the window's right edge,
    # some underneath each other -- and its `addcolumn`/`addrow` are a pitch or
    # an increment depending on who you ask. **A row is a row.**
    rows = "".join(
        f"\tif = {{\n"
        f"\t\tlimit = {{ has_global_variable = {MOD_ID}_ng{i} "
        f"global_var:{MOD_ID}_ng{i} > 0 }}\n"
        f"\t\tchange_global_variable = {{ name = {MOD_ID}_edit_pooln add = 1 }}\n"
        f"\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_edit_pool "
        f"target = goods:{good} }}\n"
        f"\t\tset_variable = {{ name = {MOD_ID}_pool{i} value = 1 }}\n"
        f"\t}}\n\telse = {{ remove_variable = {MOD_ID}_pool{i} }}\n"
        for i, good in enumerate(order, start=1))
    clears = ""
    out.append(f"""
# The goods the editor offers, rebuilt whenever its window opens.
#
# `_edit_pool` is the whole of them, for the count and the empty state.
# `_pool<n>` is the same answer as a country flag, one a good, and **that is
# what the picker's cells ask**: the cells are written out rather than drawn
# from the list, because only a written cell can print `_pn<n>` beside the good.
# A cell whose flag is unset is invisible and its row closes the gap.
# Scope: country
{MOD_ID}_edit_fill_pool = {{
\tclear_global_variable_list = {MOD_ID}_edit_pool
{clears}\tset_global_variable = {{ name = {MOD_ID}_edit_pooln value = 0 }}
{rows}}}

""")

    # ---- what the editing changed ------------------------------------------
    changed = "".join(
        f"\t\t\t\tAND = {{ is_target_in_variable_list = {{ name = {MOD_ID}_save_goods target = goods:{good} }} "
        f"NOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} }} }}\n"
        f"\t\t\t\tAND = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} "
        f"NOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_save_goods target = goods:{good} }} }} }}\n"
        for good in order)
    lines = "".join(
        f'\t\t\tif = {{ limit = {{ is_target_in_variable_list = {{ name = {MOD_ID}_save_goods target = goods:{good} }} '
        f'NOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} }} }} '
        f'debug_log = "WTP LD -{good}" }}\n'
        f'\t\t\tif = {{ limit = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} '
        f'NOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_save_goods target = goods:{good} }} }} }} '
        f'debug_log = "WTP LD +{good}" }}\n'
        for good in order)
    rows = "".join(
        f"\t\tif = {{ limit = {{ is_target_in_variable_list = {{ name = {MOD_ID}_save_goods target = goods:{good} }} "
        f"NOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} }} }}\n"
        f"\t\t\tadd_to_variable_list = {{ name = {MOD_ID}_chg_out target = goods:{good} }}\n"
        f"\t\t\tchange_variable = {{ name = {MOD_ID}_chg_n add = 1 }}\n"
        f"\t\t}}\n"
        f"\t\tif = {{ limit = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} "
        f"NOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_save_goods target = goods:{good} }} }} }}\n"
        f"\t\t\tadd_to_variable_list = {{ name = {MOD_ID}_chg_in target = goods:{good} }}\n"
        f"\t\t\tchange_variable = {{ name = {MOD_ID}_chg_n add = 1 }}\n"
        f"\t\t}}\n"
        for good in order)
    out.append(f"""
# «Показать изменения»: every location where the plan now differs from the saved
# one, and nothing else.
#
# **It fills a window and writes the same report to the log.** The window is what
# he asked for -- «кнопка показать список изменений, которое откроет ещё одно
# окно» -- and the log line stays because `mods.bat -> «Забрать диагностику из игры»` and `tools/diag.py`
# already fold a location's `LD` lines into «изменено: убрано X; добавлено Y»,
# which is how a change gets into a session without a screenshot.
#
# **Two lists on the location and a count beside them.** `_chg_out` is what left,
# `_chg_in` is what arrived, and `_chg_n` is how many of both -- the count is
# there because a `limit` cannot ask whether a variable list is empty, and
# `{MOD_ID}_chg_locs` must hold only the locations that really moved. Only those
# are printed, so after one edit the whole report is two lines, which is the
# point of the thing.
# Scope: country
{MOD_ID}_edit_changes = {{
\tset_global_variable = {{ name = {MOD_ID}_edit_moved value = 0 }}
\tclear_global_variable_list = {MOD_ID}_chg_locs
\tdebug_log_date = yes
\terror_log = "WTP the changes list is in debug.log, tag WTP. mods.bat -> «Забрать диагностику из игры» takes it out."
\tdebug_log = "WTP ==== BEGIN v{DIAG_VERSION} ==== the plan against the saved one"
\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_touched
\t\tclear_variable_list = {MOD_ID}_chg_out
\t\tclear_variable_list = {MOD_ID}_chg_in
\t\tset_variable = {{ name = {MOD_ID}_chg_n value = 0 }}
{rows}\t\tif = {{
\t\t\tlimit = {{ var:{MOD_ID}_chg_n > 0 }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_edit_moved add = 1 }}
\t\t\tadd_to_global_variable_list = {{ name = {MOD_ID}_chg_locs target = this }}
\t\t\tdebug_log_scopes = no
\t\t\tdebug_log = "WTP L rank=0 town=0 load=0"
{lines}\t\t}}
\t}}
\tdebug_log = "WTP ==== END v{DIAG_VERSION} ===="
}}
"""

)

    # ---- the windows, and the counters they read ---------------------------
    row_inits = ""
    inits = "".join(
        f"\tif = {{\n"
        f"\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_sl{n}_n }} }}\n"
        f"\t\tset_global_variable = {{ name = {MOD_ID}_sl{n}_n value = 0 }}\n"
        f"\t\tset_global_variable = {{ name = {MOD_ID}_sl{n}_locn value = 0 }}\n"
        f"\t}}\n"
        for n in range(1, EDIT_SLOTS + 1))
    out.append(f"""
# The slots' counters, created before anything can read one.
#
# **`_sl<n>_n` is what «загрузить» tests before it throws the plan away**, and a
# `limit` that reads a global which is not there fails silently -- so an
# uninitialised slot would either read as empty for ever or clear a good plan for
# nothing. Written with `has_global_variable` so a save from an older build gains
# the slots without losing the one plan it had.
# Scope: country
{MOD_ID}_edit_init_slots = {{
{inits}\t# `_edit_done` and `_edit_good` are read by `{MOD_ID}_edit_last_label` every
\t# frame the editor is open, and the pool is read by its datamodel. A list is created by
\t# clearing it, and it must be cleared only once ever: doing it on every open
\t# would throw away the goods he had picked.
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_edit_done }} }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_done value = 0 }}
\t}}
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_edit_reached }} }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_reached value = 0 }}
\t}}
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_edit_pooln }} }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_pooln value = 0 }}
\t}}
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_edit_op }} }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_op value = 0 }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_fitn value = 0 }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_cands value = 0 }}
\t}}
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_edit_presses }} }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_presses value = 0 }}
\t\t{MOD_ID}_edit_clear_trace = yes
\t}}
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable = {MOD_ID}_edit_fail }} }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_fail value = 0 }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_norefill value = 0 }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_evicted value = 0 }}
\t\tset_global_variable = {{ name = {MOD_ID}_edit_mark value = 0 }}
\t}}
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable_list = {MOD_ID}_edit_pool }} }}
\t\tclear_global_variable_list = {MOD_ID}_edit_pool
{row_inits}\t}}
\tif = {{
\t\tlimit = {{ NOT = {{ has_global_variable_list = {MOD_ID}_chg_locs }} }}
\t\tclear_global_variable_list = {MOD_ID}_chg_locs
\t}}
}}

# The editor's window. **The plan on the map is what it edits**, so opening it
# neither plans nor loads: it fills the picker from the ground the last plan
# scored and shows whatever the plan holds now.
# Scope: country
{MOD_ID}_open_edit_window_effect = {{
\t# **The probe that lived here is gone and `check_script.py` holds its answer.**
\t# It logged one line a press, to separate "the button never reached the effect"
\t# from "the effect ran and the window did not draw". The log said the effect
\t# ran, the `.gui` had no error of any kind, and the window still did not exist:
\t# nothing had registered it in `gui/scripted_widgets/`, and the engine creates
\t# only what is registered there. That is a rule a checker can enforce, so it
\t# does, and a line in `error.log` on every press is noise once the answer is in.
\t{MOD_ID}_edit_init_slots = yes
\t# **The last-press line starts blank, and the press counter starts at zero.**
\t# Both are globals and both survive a save, so a «сделано» from an hour ago
\t# used to greet him on opening the window -- and it masked the branch that
\t# would have said the press never arrived. A window that opens is a window
\t# that has taken no presses yet, and it must say so.
\tset_global_variable = {{ name = {MOD_ID}_edit_presses value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_op value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_done value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_fail value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_norefill value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_edit_reached value = 1 }}
\t{MOD_ID}_edit_fill_pool = yes
\t{MOD_ID}_plan_show = yes
\tremove_variable = {MOD_ID}_result_open
\tremove_variable = {MOD_ID}_right_open
\tremove_variable = {MOD_ID}_plan_open
\t{MOD_ID}_hide_results = yes
\tset_variable = {{ name = {MOD_ID}_edit_open value = 1 }}
}}

# Scope: country
{MOD_ID}_close_edit_window_effect = {{
\tremove_variable = {MOD_ID}_edit_open
\tremove_variable = {MOD_ID}_chg_open
\t{MOD_ID}_plan_hide = yes
\tclear_global_variable_list = {MOD_ID}_chg_locs
}}

# «Показать изменения», and the window it opens. **The list is built here and
# not by the window**, because a datamodel cannot ask two variable lists to
# differ -- the effect does the comparing and leaves the answer on the locations.
# Scope: country
{MOD_ID}_open_changes_window_effect = {{
\t{MOD_ID}_edit_changes = yes
\tset_variable = {{ name = {MOD_ID}_chg_open value = 1 }}
}}

# Scope: country
{MOD_ID}_close_changes_window_effect = {{
\tremove_variable = {MOD_ID}_chg_open
\tclear_global_variable_list = {MOD_ID}_chg_locs
}}
""")

    return "".join(out), "".join(gate)


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


def excluded_rights() -> dict[str, str]:
    """Right the game forbids -> the right that forbids it, off the `allow` blocks.

    **Read for the check below and not for a rule.** The condition is
    `scope:target = { NOT = { has_town_rights = ... } }`, and `scope:target` is
    the *town*: it says a town may not hold both, and says nothing whatever about
    which of them a country should grant. The plan gives every town exactly one
    right, so **no pair in this map can ever bind on a plan**.
    """
    out: dict[str, str] = {}
    for path in sorted((refs.GAME_COMMON / "town_rights").glob("*.txt")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for block in re.finditer(r"^([a-z0-9_]+) = \{(.*?)^\}", text, re.S | re.M):
            allow = re.search(r"allow\s*=\s*\{(.*?)\n\t\}", block.group(2), re.S)
            if not allow:
                continue
            for victim in re.findall(
                    r"NOT\s*=\s*\{\s*has_town_rights\s*=\s*town_rights_type:([a-z0-9_]+)",
                    allow.group(1)):
                out[victim] = block.group(1)
    return out


# **The one charter the mod drops in favour of another, and it is the owner's
# ruling and not the game's rule.** 2026-09-03, on Flemish cloth against royal
# textile: «оно должно по сути заменять собой базовое текстильное право в расчёте
# везде, если оно вдруг становится доступным». Five levels of a guild beat +20%
# of its output until the guild's cap passes 25
# (`docs/investigations/town_rights.md`), and a cap that high wants a megalopolis,
# so in towns the level right is the better of the two nearly always. The mod
# scores no right by the size of its bonus -- settled 2026-09-02 -- so it cannot
# derive this, and a preference it cannot derive is written down as one.
#
# **It used to be derived, from `excluded_rights()`, and that was a real fault in
# the shipped build.** The game's `allow` is a *town* condition and eight pairs
# carry one; read as "the country grants the excluder instead" it also threw away
# `royal_naval_rights` (+30% naval supplies, +30% tar) and `royal_tooling_rights`
# (+30% tools) for every Scandinavian country, in favour of the two privileges
# that exclude them -- +20%/+20% and +10%. Scandinavia is the ground those two
# royal charters are best on, and no country that had them could be given one.
PREFERRED_RIGHT = {"royal_textile_rights": "flemish_cloth_industries_right"}


def output_rights(rows: list[eu5data.Method], game: eu5data.Game) -> list[eu5data.TownRight]:
    """The urban rights this mod answers for: every one that helps a good.

    **Output and levels alike, and scored the same way**, at the owner's word,
    2026-09-02: «не важно право это на бонус производительности или на лимит
    домиков — все полезны и все по идее должны использоваться». A right is
    scored on *which goods it favours* and never on the size of the favour, so
    the two kinds need no common unit -- which is what had kept the level half
    out. The mod must never read a building's levels either way
    (`docs/investigations/town_rights.md`): the cap moves as a location grows.

    In practice this admits exactly one more, `flemish_cloth_industries_right`.
    The four marketplace charters grant levels to a marketplace, which no method
    produces, so they fall out here as they always did -- trade and not
    production, and «вообще не про то».

    A good the game makes no method for would be an empty slot on every row, so
    it is dropped from the bundle, and a right left with nothing is dropped
    whole.
    """
    made = {m.produced for m in rows}
    by_key = {r.key: r for r in game.town_rights}
    # **The one preference the mod holds, checked against the game every build.**
    # It is a preference only because the game forbids the pair in one town; if a
    # patch drops that `allow`, the two stop being alternatives and the reason to
    # prefer either is gone with it.
    forbidden = excluded_rights()
    for victim, winner in PREFERRED_RIGHT.items():
        assert forbidden.get(victim) == winner or forbidden.get(winner) == victim, (
            f"the game no longer forbids {victim} beside {winner}; "
            f"`PREFERRED_RIGHT` is a ruling about a pair that has gone")
    keep = []
    for right in game.town_rights:
        favoured = {**right.levels, **right.output}
        bundle = {g: v for g, v in favoured.items() if g in made}
        if not bundle:
            continue
        # **One charter stands aside for another, and only where the owner said
        # so.** `PREFERRED_RIGHT` carries the reasoning; the rest of the game's
        # excluding pairs are a town's rule and not a country's, and the plan --
        # which gives a town one right -- can never break it.
        potential = right.potential
        winner = by_key.get(PREFERRED_RIGHT.get(right.key, ""))
        if winner is not None and winner.potential:
            gate = f"NOT = {{ {winner.potential} }}"
            potential = f"{potential} {gate}" if potential else gate
        keep.append(eu5data.TownRight(key=right.key, output=bundle,
                                      levels=right.levels, penalty=right.penalty,
                                      advance=right.advance, potential=potential))
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

    # **The picker's cell: the good's icon and how many buildings of it stand on
    # the ground.** He asked for the number three times -- «Я до сих пор не вижу
    # в редакторе сколько домиков какова вида стоит сейчас» -- and it could not
    # be drawn while the cells came from a datamodel, because a goods scope
    # reaches no numbered counter. A written cell reads `_pn<n>` straight.
    #
    # A texticon in a localization value is the game's own way of drawing a good
    # (`hint_eco_hint_text_2`), and it needs no scope at all -- which is the
    # whole reason the cell can be static.
    for i, good in enumerate(goods_order(split), start=1):
        out.append(f" {MOD_ID}_cell_{i}: "
                   f'"@{good}! [GuiScope.SetRoot(GetPlayer.MakeScope)'
                   f".ScriptValue('{MOD_ID}_show_pn{i}')|0]\"\n")

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
    # The unmerged rights, for the advance each one carries. `output_rights`
    # rewrites `potential` and the advance is not on its side of that.
    by_key = {r.key: r for r in game.town_rights}

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
        """One line into the log, and **exactly one**.

        `error_log` writes into `debug.log` as well as `error.log` -- measured
        2026-09-02, when every line marked "both sinks" arrived in the report
        twice. So the detail goes to `debug_log` alone and `error.log` gets one
        pointer, at the top, saying where the report is.

        `both` is kept in the signature because a line worth duplicating may come
        back; today nothing sets it.
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
    out.append(f'\terror_log = "WTP the report is in debug.log, tag WTP, '
               f'version {DIAG_VERSION}. mods.bat -> «Забрать диагностику из игры» takes it out."\n')
    out.append(say(f"==== BEGIN v{DIAG_VERSION} ==== everything to the next END is one "
                   "press. Take it out with mods.bat -> «Забрать диагностику из игры», or tools/diag.py."))
    out.append(f"""\t{MOD_ID}_diag_build = yes
\t{MOD_ID}_diag_state = yes
\t{MOD_ID}_diag_scan = yes
\t{MOD_ID}_diag_goods = yes
\t{MOD_ID}_diag_passes = yes
\t{MOD_ID}_diag_rights = yes
\t{MOD_ID}_diag_locations = yes
\t{MOD_ID}_diag_ranking = yes
""")
    out.append(say(f"==== END v{DIAG_VERSION} ===="))
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
                   f"rights={len(rights)} gated={len(UNLOCKS)}"))
    out.append(say(f"BUILD rounds={PLAN_ROUNDS} passes={len(PLAN_PASSES)} bands={bands} "
                   f"tiers={tiers} rows={PLAN_ROWS} ranked={PLAN_RANKED} "
                   f"result_rows={RESULT_ROWS} "
                   f"rank_scale={RANK_SCALE} right_slots={RIGHT_SLOTS}"))
    out.append(say("BUILD passes in order: "
                   + ", ".join(f"{i}={pass_name(band, tier)}"
                               for i, (band, tier) in enumerate(PLAN_PASSES, start=1))))
    # **Two self-tests, and there were four.** The other two asked what else a
    # `debug_log` string resolves, and the 2026-09-02 run answered both: a
    # localization key comes out as the key, and `ROOT.GetName` / `SCOPE.GetName`
    # do not exist ("Could not find data system function 'GetName'"). They are in
    # `docs/research/engine.md` now and out of here. What is left is the canary --
    # if this number is not 12345 nothing below it can be believed -- and the one
    # that names the scope, which every row depends on.
    out.append(f"\tset_global_variable = {{ name = {MOD_ID}_dv1 value = 12345 }}\n")
    out.append(say(f"SELFTEST 1 global-through-player={read(1)} (expect 12345; "
                   "anything else and every number below is wrong)"))
    out.append("\tdebug_log_scopes = no\n")
    out.append(say("SELFTEST 2 the line above this one names the country -- that is "
                   "debug_log_scopes, and it is how every row below says which "
                   "location it is"))
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
                   % tuple(read(i) for i in range(1, 9))))
    for slot, (name, source) in enumerate((
            ("cap_rural", f"{MOD_ID}_plan_cap_rural"),
            ("cap_urban", f"{MOD_ID}_plan_cap_urban")), start=1):
        out.append(park(slot, source))
    out.append(flag(3, f"has_global_variable = {MOD_ID}_plan_rights"))
    out.append(flag(4, f"has_global_variable = {MOD_ID}_plan_by_end"))
    out.append(flag(5, f"has_global_variable = {MOD_ID}_rank_by_end"))
    out.append(flag(6, f"has_global_variable = {MOD_ID}_only_buildable"))
    out.append(say("SET cap_rural=%s cap_urban=%s rights=%s "
                   "plan_by_end=%s rank_by_end=%s buildable_only=%s"
                   % tuple(read(i) for i in range(1, 7))))
    # **`ranked_provs` read `{MOD_ID}_found` for three builds**, which is the
    # single-good *ranking*'s province count and has nothing to do with a plan:
    # every report of 2026-09-03 printed `ranked_provs=0` beside `provs=8`,
    # because no ranking had been asked for. The number the line means is
    # `_plan_prov_n`, how many provinces `_plan_rank` put in order -- and a
    # province past `PLAN_PROVS` keeps the 9999 the reset gave it, so the two
    # differing is the one way that cap can be seen.
    for slot, source in enumerate((
            f"{MOD_ID}_plan_placed", f"{MOD_ID}_plan_rooms", f"{MOD_ID}_plan_found",
            f"{MOD_ID}_plan_shown", f"{MOD_ID}_plan_towns", f"{MOD_ID}_plan_provn",
            f"{MOD_ID}_plan_scored", f"{MOD_ID}_plan_quota", f"{MOD_ID}_plan_rightn",
            f"{MOD_ID}_plan_sweeps", f"{MOD_ID}_plan_prov_n",
            f"{MOD_ID}_plan_opensw", f"{MOD_ID}_rquota", f"{MOD_ID}_rlevel"), start=1):
        out.append(park(slot, source))
    # `rquota` is the towns each charter may end with, `rlevels` how many heights
    # the ladder actually climbed to. The two apart is the guard having cut it
    # short -- the one thing about the charter round that leaves no other trace.
    out.append(say("PASS placed=%s rooms=%s used_locs=%s drawn=%s towns=%s provs=%s "
                   "goods_scored=%s quota=%s rights_given=%s sweeps=%s "
                   "ordered_provs=%s open_sweeps=%s rquota=%s rlevels=%s"
                   % tuple(read(i) for i in range(1, 15))))
    # **What the ground actually pays**, and it is the owner's own question:
    # «какой процент из них получит выгоду от своего положения на карте».
    # `fed` is how many placed buildings earn any bonus at all; `gain` is the
    # sum of what they earn, out of RANK_SCALE apiece, so the average is one
    # division and `tools/diag.py` does it.
    for slot, source in enumerate((f"{MOD_ID}_plan_fed", f"{MOD_ID}_plan_gain",
                                   f"{MOD_ID}_plan_placed"), start=1):
        out.append(park(slot, source))
    out.append(say("GAIN fed=%s of placed=%s | gain_total=%s out of %d a building "
                   "-- fed is how many earn any bonus where they stand, gain is "
                   "what they earn in all" % (read(1), read(3), read(2), RANK_SCALE)))

    # **The editor, in three lines**, and it is here because he asked for it
    # after a session where 27 buildings went in over the cap and nothing in the
    # report could say how: «Добавляй скан информации для себя в диагностике на
    # функцию редактора, чтобы ты видел чё там происходит.»
    #
    # The three lines are the three stages of a press: what was asked, what the
    # scan found, and what the walk did where it stood. `_ev_*` are parked by the
    # walk itself, because a `debug_log` cannot reach the item a walk is on.
    out.append(say("EDIT legend: one press, three stages. asked -> scan -> walk. "
                   "op 1=«+1» 2=«−1» 0=nothing pressed yet. hit=0 means the walk "
                   "found no candidate at all, so load/esg/esw below are stale. "
                   "esg is the good the walk would evict (0 = none), esw its gain."))
    for slot, source in enumerate((f"{MOD_ID}_edit_presses", f"{MOD_ID}_edit_op",
                                   f"{MOD_ID}_edit_good", f"{MOD_ID}_edit_reached",
                                   f"{MOD_ID}_edit_done", f"{MOD_ID}_edit_fail",
                                   f"{MOD_ID}_edit_norefill"), start=1):
        out.append(park(slot, source))
    out.append(say("EDIT asked presses=%s op=%s good=%s reached=%s | outcome "
                   "done=%s fail=%s norefill=%s"
                   % tuple(read(i) for i in range(1, 8))))
    for slot, source in enumerate((f"{MOD_ID}_edit_fitn", f"{MOD_ID}_edit_cands",
                                   f"{MOD_ID}_ev_hit", f"{MOD_ID}_ev_town",
                                   f"{MOD_ID}_ev_load", f"{MOD_ID}_ev_esg",
                                   f"{MOD_ID}_ev_esw"), start=1):
        out.append(park(slot, source))
    out.append(say("EDIT scan fitn=%s cands=%s | walk hit=%s town=%s load=%s "
                   "esg=%s esw=%s"
                   % tuple(read(i) for i in range(1, 8))))
    for slot, source in enumerate((f"{MOD_ID}_edit_evicted", f"{MOD_ID}_edit_room",
                                   f"{MOD_ID}_edit_mark", f"{MOD_ID}_ev_load2",
                                   f"{MOD_ID}_plan_placed", f"{MOD_ID}_plan_cap_urban",
                                   f"{MOD_ID}_plan_cap_rural"), start=1):
        out.append(park(slot, source))
    # Field names have to be unique across the whole line: `tools/diag.py` reads
    # them by name, and a bare `after=` matched the wrong one first time out.
    out.append(say("EDIT walk evicted=%s room=%s | placed_before=%s placed_after=%s | "
                   "load_after=%s | cap_urban=%s cap_rural=%s"
                   % (read(1), read(2), read(3), read(5), read(4),
                      read(6), read(7))))
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
\tset_global_variable = {{ name = {MOD_ID}_diag_realt value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_diag_forced value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_diag_forcedr value = 0 }}
\tset_global_variable = {{ name = {MOD_ID}_diag_moved value = 0 }}
""")
    # **How many locations this plan put something different in.** One `OR` a
    # location over the two lists, in the walk the scan already makes, so the
    # count costs nothing the diagnosis was not already paying.
    moved_count = ("\t\tif = {\n\t\t\tlimit = { OR = {\n"
                   + "".join(
                       "\t\t\t\tAND = { is_target_in_variable_list = { name = %s_save_goods target = goods:%s } "
                       "NOT = { is_target_in_variable_list = { name = %s_plan_goods target = goods:%s } } }\n"
                       "\t\t\t\tAND = { is_target_in_variable_list = { name = %s_plan_goods target = goods:%s } "
                       "NOT = { is_target_in_variable_list = { name = %s_save_goods target = goods:%s } } }\n"
                       % (MOD_ID, good, MOD_ID, good, MOD_ID, good, MOD_ID, good)
                       for good in order)
                   + "\t\t\t} }\n\t\t\tchange_global_variable = { name = %s_diag_moved add = 1 }\n\t\t}\n"
                   % MOD_ID)
    for index in range(1, len(order) + 1):
        for side in ("t", "r"):
            for what in ("w", "r", "g", "p", "o"):
                out.append(f"\tset_global_variable = {{ name = {MOD_ID}_f{what}{side}{index} value = 0 }}\n")
    out.append(f"""\tevery_in_global_list = {{
\t\tvariable = {MOD_ID}_plan_touched
\t\tchange_global_variable = {{ name = {MOD_ID}_diag_locs add = 1 }}
{moved_count}
\t\t# **Тумблеры считаются здесь, до разделения на стороны**, и это
\t\t# сознательно: 2026-09-02 он сбросил их в «авто», а окно показало города
\t\t# снова. Счёт по обеим сторонам различает «переменная вернулась» и «окно
\t\t# врёт» -- по стороне это было бы неразличимо, потому что сброшенная
\t\t# локация уходит на сельскую сторону вместе со своим счётчиком.
\t\tif = {{
\t\t\tlimit = {{ has_variable = {MOD_ID}_force_town }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_diag_forced add = 1 }}
\t\t}}
\t\tif = {{
\t\t\tlimit = {{ has_variable = {MOD_ID}_force_rural }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_diag_forcedr add = 1 }}
\t\t}}
\t\tif = {{
\t\t\tlimit = {{ {MOD_ID}_plan_is_town = yes }}
\t\t\tchange_global_variable = {{ name = {MOD_ID}_diag_towns add = 1 }}
\t\t\t# **Городская сторона и городской ранг -- разные вещи.** Тумблер
\t\t\t# «сделать городом» переносит локацию на городскую сторону расчёта,
\t\t\t# но ранга в игре не меняет -- а гильдия объявлена `town = yes` и в
\t\t\t# `rural_settlement` не встанет никогда. 2026-09-02 весь симптом
\t\t\t# оказался в этом зазоре, и это число его называет.
\t\t\tif = {{
\t\t\t\tlimit = {{ NOT = {{ location_rank = location_rank:rural_settlement }} }}
\t\t\t\tchange_global_variable = {{ name = {MOD_ID}_diag_realt add = 1 }}
\t\t\t}}
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
    # **`q` is read after the plan, and the open ladder raised it.** It is the
    # only number in the report that is not what the pass it belongs to saw:
    # `_plan_set_quota` writes `quota + charters - RGOs` with a floor of one, and
    # then every sweep of the open ladder adds one to all of them. Without this
    # line the two are read against each other and neither makes sense --
    # Westphalia's `PASS quota=2` beside `clay q=2 rgo=2`, which looks like the
    # RGO discount doing nothing and is the open ladder having added one back.
    out.append(say("GOODS reading q: it is `PASS quota` + what the charters "
                   "placed for this good - `rgo`, floored at 1, and then + 1 for "
                   "each sweep of the open ladder -- which is `PASS open_sweeps`. "
                   "So the quota the allocator enforced is q - open_sweeps, and a "
                   "good with n at that number was stopped by its quota and not "
                   "by the ground."))
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
                                   f"{MOD_ID}_diag_freet", f"{MOD_ID}_diag_freer",
                                   f"{MOD_ID}_diag_realt", f"{MOD_ID}_diag_forced",
                                   f"{MOD_ID}_diag_forcedr", f"{MOD_ID}_diag_moved"), start=1):
        out.append(park(slot, source))
    out.append(say("ROOM walked=%s towns=%s towns_with_room=%s villages_with_room=%s "
                   "| town rank or above=%s | ticks now set: town=%s village=%s "
                   "-- read live, so this says what the ticks are at this moment "
                   "and not what the last plan saw | moved=%s locations differ from "
                   "the plan before this one" % tuple(read(i) for i in range(1, 9))))
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
        # **Круглые скобки, не квадратные.** `[glass, masonry]` в строке -- это
        # синтаксис data-функции: 2026-09-02 движок попытался вызвать функцию
        # `glass`, не нашёл, и `given=` уехало отдельной записью лога. Правило
        # записано в корневом CLAUDE.md, и оно про любую строку, а не только
        # про локализацию.
        goods = ", ".join(sorted(right.output))
        out.append(park(1, f"{MOD_ID}_rgiven{number}"))
        # **`given=0` had two meanings and they are not the same fault.** A
        # charter this country may grant and did not is the allocator's problem;
        # one it may never grant -- somebody else's tag, somebody else's culture
        # -- is not a problem at all. Four of the thirteen read `given=0` on every
        # report of 2026-09-03 and the report could not tell them apart.
        out.append(flag(2, f"{MOD_ID}_plan_right_gate_{number} = yes"))
        # **And `unlocked=` is the advance, which the plan deliberately ignores.**
        # The plan grants every charter the country could ever hold, because it is
        # a target to build towards and the nine general ones arrive at one fixed
        # age (`plan_right_gates`). That leaves a real question the owner can only
        # answer from here: *may I grant this today?* Gating the plan on it was
        # tried on 2026-09-03 and cost the plan a quarter of its ground; printing
        # it costs one flag.
        advance = by_key[right.key].advance
        out.append(flag(3, f"has_advance = {advance}" if advance else "always = yes"))
        out.append(say(f"RIGHT {number} {right.key} ({goods}) "
                       f"given={read(1)} grantable={read(2)} unlocked={read(3)}"))
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
""")
    # **The key before the numbers it unlocks.** It used to be printed after the
    # last location, where `tools/diag.py` swallowed it whole; and even reaching
    # the page it would have been a legend under two hundred rows of the thing it
    # explains.
    out.append(say("RQ legend: what the ground would pay for each charter in that "
                   "town, out of %d -- " % RANK_SCALE + ", ".join(
                       f"{number}={right.key}" for number, right in enumerate(rights, start=1))
                   + ". Each bundle good the town can make adds its own gain, each it "
                   "cannot adds nothing, and the sum is divided by the whole bundle. The "
                   "largest is the one the town took, unless its quota was already spent."))
    out.append(f"""\tordered_in_global_list = {{
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
    # **The gap the whole 2026-09-02 symptom lives in**, printed per row: which
    # side the plan put this location on, what rank the *game* thinks it is, and
    # whether the player's tick is what moved it. A guild is `town = yes` and
    # will not stand in a `rural_settlement` however the plan scores it.
    out.append(flag(7, "NOT = { location_rank = location_rank:rural_settlement }",
                    tab="\t\t"))
    out.append(flag(8, f"has_variable = {MOD_ID}_force_town", tab="\t\t"))
    out.append(flag(9, f"has_variable = {MOD_ID}_force_rural", tab="\t\t"))
    out.append("\t\tdebug_log_scopes = no\n")
    out.append(say(f"L rank={read(1)} town={read(6)} town_rank={read(7)} "
                   f"forced_town={read(8)} forced_village={read(9)} load={read(2)} "
                   f"right={read(3)} prov_rank={read(4)} prov_load={read(5)}",
                   tab="\t\t"))
    # **Why this town got this charter and not another one**, which is the one
    # question the report could not answer: the plan prints the winner and never
    # the field it beat. `_rq<k>` is what this ground would pay for the whole
    # charter, out of `RANK_SCALE`, so the line is the whole comparison the grant
    # made and a one-good right's number is that good's gain read off directly.
    #
    # Towns only, because a village never holds one. A script value is added into
    # the scratch global rather than parked: `park` asks `has_variable`, and a
    # script value is not a variable.
    out.append(f"\t\tif = {{\n\t\t\tlimit = {{ {MOD_ID}_plan_is_town = yes }}\n")
    for number in range(1, len(rights) + 1):
        out.append(f"\t\t\tset_global_variable = {{ name = {MOD_ID}_dv{number} value = 0 }}\n"
                   f"\t\t\tchange_global_variable = {{ name = {MOD_ID}_dv{number} "
                   f"add = {MOD_ID}_rq{number} }}\n")
    # **No second `debug_log_scopes` here, and the reports of 2026-09-03 are
    # why.** The effect writes one line naming the scope, and this block called
    # it again inside the same iteration -- so every location's name reached the
    # log twice, and `tools/diag.py`, which reads the unlabelled line before a
    # row as that row's name, gave every row from the second onwards **two**
    # names: «WTP L Район Липпштадт (980) Район Зост (981) rank=2». The owner,
    # looking for one town in it: «Понятия не имею где конкретно искать строку
    # Гослара». The `L` line above names this location already and `RQ` is the
    # next line of the same block.
    out.append(say("RQ " + " ".join(f"{number}={read(number)}"
                                    for number in range(1, len(rights) + 1)),
                   tab="\t\t\t"))
    out.append("\t\t}\n")
    for good in order:
        out.append(f"\t\tif = {{ limit = {{ is_target_in_variable_list = "
                   f"{{ name = {MOD_ID}_plan_goods target = goods:{good} }} }} "
                   f'debug_log = "WTP LG {good}" }}\n')
    # **And what this plan moved against the one before it.** `_save_goods` is the
    # previous plan's list, copied off the location before `_plan_prepare`
    # cleared it. Printed only for the locations that take a row, so a large
    # ground pays for at most `DIAG_LOCS` comparisons rather than all of them.
    for good in order:
        out.append(
            f"\t\tif = {{ limit = {{ "
            f"is_target_in_variable_list = {{ name = {MOD_ID}_save_goods target = goods:{good} }} "
            f"NOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} }} "
            f'}} debug_log = "WTP LD -{good}" }}\n')
        out.append(
            f"\t\tif = {{ limit = {{ "
            f"is_target_in_variable_list = {{ name = {MOD_ID}_plan_goods target = goods:{good} }} "
            f"NOT = {{ is_target_in_variable_list = {{ name = {MOD_ID}_save_goods target = goods:{good} }} }} "
            f'}} debug_log = "WTP LD +{good}" }}\n')
    out.append("\t}\n")
    out.append(park(1, f"{MOD_ID}_diag_n"))
    out.append(park(2, f"{MOD_ID}_plan_found"))
    out.append(say(f"LOCS printed={read(1)} of={read(2)} cap={DIAG_LOCS} "
                   "-- a cap is never silently the answer"))
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
    out.append(say(f"ROWS printed={read(1)} of={read(2)} cap={DIAG_ROWS}"))
    out.append("}\n")
    return "".join(out)


def main() -> int:
    game = eu5data.load_game()
    rows = methods(game)
    split = goods_split(rows, game)

    # **What the generator would otherwise get wrong quietly**, checked once here
    # rather than found in a log. Every one of these is a number the game supplies
    # and the mod caps; a patch that raises the game's side has to raise the cap
    # with it, and a build that says so is cheaper than a run that does not.
    rights = output_rights(rows, game)
    assert len(rights) <= DIAG_SCRATCH, (
        f"{len(rights)} urban rights and only {DIAG_SCRATCH} scratch globals: the "
        f"`WTP RQ` line parks one score per charter, so raise `DIAG_SCRATCH`")
    assert len(split["raw"]) + len(split["made"]) <= LIST_CAP, (
        f"{len(split['raw']) + len(split['made'])} goods against a list of "
        f"{LIST_CAP}: CMM handles a row click to fifty and no further")
    assert max(len(r.output) for r in rights) <= RIGHT_SLOTS, (
        f"a charter favours more than {RIGHT_SLOTS} goods the mod can make; a row "
        f"holds a fixed number of answers, so raise `RIGHT_SLOTS`")

    by_continent = regions()
    write(ZONE_OUT, zone_file() + clear_ticks_effect())
    write(REGION_OUT, region_file(by_continent))
    write(TRIGGERS_OUT, triggers_file(rows, split, game))
    write(PICKER_OUT, picker_file(split, rows))
    write(VALUES_OUT, values_file(rows, split, game) + "".join(
        f"# How many buildings of {good} the plan holds. Printed in the picker's\n"
        f"# own cell, which is why the cells are written out: a datamodel row\n"
        f"# carries a goods scope and a scope reaches no numbered counter.\n"
        f"# Scope: country\n"
        f"{MOD_ID}_show_pn{i} = {{ value = global_var:{MOD_ID}_pn{i} }}\n"
        for i, good in enumerate(goods_order(split), start=1)))
    write(SCORE_OUT, score_file(rows, split, game))
    write(ROWS_OUT, rows_file())
    write(GUIS_OUT, guis_file(by_continent) + "".join(
        f"""
# «{'+1' if what == 'plus' else '−1'}» for {good}, from the picker's own cell.
#
# **No saved scope.** The cell is written out and knows its number, so the
# bridge that carried `goods:{good}` as a scope is gone -- and with it the one
# thing between the press and the plan that could quietly not arrive.
{MOD_ID}_pick_{what}_{i} = {{
\tscope = country

\tis_shown = {{
\t\talways = yes
\t}}

\teffect = {{
\t\t{MOD_ID}_edit_{what}_{i} = yes
\t\t{MOD_ID}_recompute_live = yes
\t}}
}}
"""
        for i, good in enumerate(goods_order(split), start=1)
        for what in ("plus", "minus")))
    write(LAYOUT_OUT, layout_file(by_continent))
    write(RIGHTS_OUT, rights_file(rows, split, game))
    write(PLAN_OUT, plan_file(rows, split, game))
    write(PLAN_TRIGGERS_OUT, plan_triggers_file(rows, split, game))
    write(PLAN_LOC_OUT, plan_loc_file(rows, game))
    write(DIAG_OUT, diag_file(rows, split, game))
    effects, triggers = editor_file(rows, split, game)
    write(EDITOR_OUT, effects)
    write(EDITOR_TRIGGERS_OUT, triggers)
    write(EDIT_CELLS_OUT, edit_cells_file(goods_order(split)))
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

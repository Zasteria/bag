# Where To Produce

A planning tool for Europa Universalis V, in the Community Mod Framework's Mod
Menu. It does not build anything and does not automate anything: it answers one
question, in a table.

> I mean to take Northern Germany. When I have it, where do I put the weapon
> smiths?

## What it does

1. **Borders.** Tick regions, in six lists grouped by continent. Every region in
   the game is there, owned or not — the point is planning for ground you do not
   hold yet.
2. **What you want made.** A good, in two lists — the raw materials an RGO also
   produces and the things only a workshop makes — or a whole urban right, which
   is a bundle of two or three goods. Choosing the recipe is the mod's job, not
   yours: it scores all 218 methods that consume a raw material and keeps the
   best per location.
3. **Rank.** Press the button. Every location inside the ticked regions is
   scored, the best fifty provinces are listed, and the mod's own results window
   opens on them: one row per province with the efficiency it would give, the
   building and **which of its methods** won, and an icon for each raw material
   the province supplies to that method. A row expands into the province's
   locations, each with what it works now and a button to take it into the plan.
4. **In two ages.** Each row carries the answer twice: what you could build now,
   and what the ground gives once every advance is in — the best of the methods
   nothing makes obsolete. The second is written only where it differs, so an
   empty cell means the province does not change. It is not decoration: along
   the game's ladder the *inputs* move, not merely the output, so for a third of
   the goods the province that suits the guild is not the one that suits the
   mill. `docs/investigations/production_ladder.md` has the numbers.

## Why it is not the game's own build panel

The game already ranks locations for a building type, in
`build_location_lateralview.gui`, with a `production_efficiency` sort and an
RGO-aware tooltip. Two things it does not do:

- Its figure is `BuildingType.CalcHighestPossibleProductionEfficiency` — the
  **best** method the building could ever run. This tool answers for the method
  you actually mean to run, which is a different location whenever the two
  differ.
- It lists what you can build **now**. It cannot answer for land you have not
  taken yet, and that is the question a plan is made of.

It also cannot be extended in place: Glorp UI already replaces that panel's row
template and the type around it, so a second mod redefining either would fight
it. This one adds a Mod Menu tab and touches no vanilla file.

## The number

```
RGO bonus % = 10 * (input amounts the province supplies) / (all input amounts)
```

Verified to the digit against three in-game tooltips at 1.3.10; the derivation
is in `docs/research/engine.md` and the code is `tools/eu5data.py`. Two things
about it surprise people:

- **Every input counts towards the denominator, produced goods included.** An
  RGO can never supply tools, but tools still carry their weight — which is why
  a weapon smith's maintenance method tops out at 5.24% rather than 10%. The
  tooltip on the results table prints that ceiling for whatever method is
  chosen.
- **It is the province, not the location.** A raw material worked anywhere in
  the province counts, so every location of one province scores the same. What
  separates them afterwards is building slots, which this version does not
  model.
- **And the province is the whole province.** The game splits a province by
  ownership — half of Bessarabia under Moldavia is its own `province`, named
  «Молдавская провинция Бессарабия» — and this counts over the
  `province_definition`, both halves. That is the number the ground gives once
  it is yours, which is the only number a plan can be made of. Whether the
  engine's own bonus counts the same way is an open question with a one-hover
  test in `docs/research/engine.md`.

## Settled, and not to be re-litigated

Moved here from the mod's `CLAUDE.md` on 2026-09-03, at its budget. Each of these
cost a run or a redesign; none of them is a live question.

- **A window's datamodel is what costs**: a scripted widget never comes down, so
  only the list it repeats over decides the row count — `PLAN_ROWS` is one page
  and `PLAN_RANKED` the answer.
- **The bonus is province-level** — hence a row is a `province_definition`: the
  whole ground, not one owner's piece; what would separate its locations is
  building slots, which the game hides.
- **The selection is recorded twice**, only `bag_wtp_pick` / `_drop` writes it;
  **every column is a fixed width** (`docs/pitfalls/interface.md`); **the buildable
  tick is the location's** (`docs/SETTLED.md`).


## The whole plan

The fourth group on the Answer tab, and a second question rather than a bigger
version of the first: **every good at once over the chosen ground**, one building
at a time, under a cap per location.

**Seven steps, and the «План» button prints them too:**

1. **Score every good in every location** — the best method whose building may
   actually stand there, that the ground feeds, and that you could run: output
   times the bonus its raw materials earn.
2. **Read it as a fraction of what that good could ever earn.** The gain is
   `bonus ÷ the best ceiling any recipe of that good reaches in the game`, so
   1000 means "this ground feeds the recipe whole" for every good alike — and a
   good capped at 2% compares fairly with one that can reach 10% without the
   biggest recipe taking every contested location.
3. **Grant urban rights**, in towns only and one per town: a town takes the
   right its ground suits best among those the country could ever grant — the
   right's own `potential`, and never the advance that unlocks it, because a plan
   is a target to build towards and the nine general charters arrive at one fixed
   age. A bundle good that cannot stand there does not go up, and its slot falls
   to the raw material that would let it. On a small ground this round places
   more than half the plan.
4. **Every good the ground can produce takes one location, before anything
   else** — its own best, in descending bands of gain. That is the hard
   constraint: «все товары которые можно произвести на выбранной земле должны
   производиться, все».
5. **Then the scarce finish their share, before the common start theirs.** A
   good only a couple of locations can hold takes them while they are still
   free — the tiers are 1, 2, 4, 8, 16 candidate locations, five bands of gain
   inside each. Iron is the case: without an RGO it comes from one building,
   which wants wetlands or a lake.
6. **Then everything**, five bands, and this is where the bulk of a plan is
   placed. **A location holds one building of a type**, so a good whose building
   already stands there is not offered again — but the next location may take
   that building running another method.
7. **Then what is left, dealt by each good's own best rather than by the
   absolute band.** Once every good has had its share, handing every leftover
   room to the good with the largest ceiling is not opportunity cost but
   concentration: on 416 locations it put 108 cloth buildings on the map against
   2 cannon. Here a good whose best on this ground pays 362 competes for its own
   top fifth exactly as one that reaches 1000 does. Rounds until one adds
   nothing, so nothing the ground can feed is left empty.

## Editing a finished plan

**A plan is not a picture, it is state on the map, and the editor changes it one
building at a time.** For the disagreements a formula cannot settle — you want
iron in every bog, or you are tired of looking at naval supplies.

- **Its own good picker**, three dropdowns rather than the goods list the ranking
  uses, so choosing a good to edit does not throw the ranking's answer away.
- **«+1 домик»** asks every location what one more of that good would cost there:
  nothing where a room is free, otherwise the gain of the cheapest building that
  would have to come out. The cheapest wins, one building moves, the rest of the
  plan stays exactly where it was.
- **Two buildings are never taken out.** A good's last on the whole ground — so
  no amount of editing can break «все товары должны производиться» — and one
  belonging to the bundle of the charter granted in that town, which would leave
  the town holding a charter for something it no longer makes.
- **«−1 домик»** takes the good's worst placement and hands the room to whichever
  good suits it best.
- **«Сохранить план» and «Вернуть сохранённое».** A fresh plan saves itself, so
  it is its own baseline; saving again re-bases wherever the editing has got to.
- **«Показать изменения»** writes only the locations that differ from the save —
  after one edit that is two lines. `mods.bat → 8` takes it out.

**Pressing «Пересчитать» throws every edit away**, because that rebuilds the plan
from the formula. That is what the save slot is for.

- **Every building is one the game says may stand there.** `can_build_building`
  in the location's scope — terrain, rank, `location_potential`, and never an
  advance, so it is as true for ground you have not taken as for the last age. A
  bog iron smelter wants wetlands or a lake; a sugar plantation wants sugar
  growing overseas.
- **Two caps, set in the game**: buildings per rural location (3) and per town
  (4). The game exposes no building-slot count of any kind, so these are the
  player's figures; the pass prints the capacity of the chosen ground beside the
  goods asking for room in it.
- **Two buttons, now and at the end of the game**, the same pair the ranking has:
  along the ladder a recipe's inputs move, so the province that suits the guild
  is not the one that suits the mill.
- **Which locations count as towns is yours to override**, from a button on the
  row. No plan run clears it.
- **The answer is a table and a map.** Rows are locations ordered by province —
  provinces by how much the plan put in each, their locations together, towns
  first — and a map mode in the Economy category paints completeness.

**A province is coherent only where it deserves to be.** Every location of a
province is worth the same to a good, so the walk keeps returning to a province
it likes and its locations come out alike. Where the ground is tight it varies
them instead, which is the point: a market village here can make pottery while
the next makes jewelry.

**Everything the pass reads is a variable on a location.** `bag_wtp_load`,
`bag_wtp_plan_goods` and `bag_wtp_plan_builds` are the whole answer, the last of
them also being the set a location may hold only one of each from;
`bag_wtp_plan_prank` is what keeps a province's rows together. **Never on the
`province_definition`** — it holds no variable, and the plan that tried placed
nothing at all (`docs/PITFALLS.md`).
The design and the owner's answers behind it:
[`../../docs/investigations/whole_map_plan.md`](../../docs/investigations/whole_map_plan.md).

## What is deliberately not here yet

Any measure of what a building costs to put up. In the plan: a per-good weight
(«этому товару нужно больше места»), the discount an RGO already standing should
buy a good, choosing which goods to plan rather than all of them, ordering the
goods within a sweep by which of them would lose most, and asking whether a
location can actually hold what its province's list says — terrain and a
building's own requirements are not consulted when the lists are spent. The ranking still
walks the fifty best provinces by the *near* column unless told otherwise, so a
province that is poor now and first in the last age is only found with «Rank by
the last age» ticked.

## Two places the answer is shown

**A window of this mod's own** is the real one. A row there is a widget: it can
carry the province and the method and an icon per good, and it opens into the
province's locations. It repeats over `bag_wtp_results`, a plain global list, so
nothing about CMF bounds it.

**The fifty-row table in the Mod Menu** is the summary beside it, and fifty is
CMF's ceiling rather than this mod's: list items are initialised through an
unrolled chain of `if`s that stops at item 50, because a CMM list ordinal has to
be a literal — `item = var:x` is pasted verbatim into the macro and kills the
load. A row there is one localization key, which is the whole reason the window
exists: a key cannot hold an icon without a global variable per slot per row, and
it cannot expand at all.

The ranking pass walks eight times fifty candidates to fill those fifty rows.
`max` on `ordered_in_global_list` counts locations visited, not rows produced,
and only the first location of each province takes a row — at `max = 50` the
fifth run got about a dozen provinces into a table with fifty places.

## Layout

```
in_game/common/
  on_action/           CMF's registration and callback hooks
  scripted_effects/    registration, the ranking pass, and four generated files
  scripted_triggers/   which locations are worth ranking
  scripted_guis/       one _on_changed per list -- without them a list is invisible
  script_values/       the bonus, and the readings the row labels print
in_game/gui/
  bag_wtp_result_window.gui   the whole interface: the map pickers, and the
                              ranked provinces under them
main_menu/localization/{english,russian}/
tools/generate.py      everything above that comes out of the game's own files
```

## The answer lives on the location

`bag_wtp_fill_rows` parks it there; everything else reads it back:

| on the winning location | is |
| --- | --- |
| `bag_wtp_best` | `out * (1 + bonus/100) * RANK_SCALE` — what the ranking sorts on, never printed |
| `bag_wtp_rank` | the place it came in, 1 first — the «№» column |
| `bag_wtp_bt` / `_pm` | the building and the method that won |
| `bag_wtp_out` / `_bonus` | what it makes a level unscaled — the row's `×` — and the RGO bonus, its percentage |
| `bag_wtp_goods` / `_all` | the raw materials the province supplies, and how many it could |

`bag_wtp_mid_*` and `bag_wtp_end_*` are the same for the other two columns, plus
`bag_wtp_mid_age`; `_any_best*` is each column's unfed fallback, printed only,
and `bag_wtp_row_end` is which column the row prints. An urban right's are
`bag_wtp_r_*_<k>` for slot `k` of three (script has no list of tuples),
`_r_good_<k>` the good and `_r_total` what the ranking sorts on. All have a
`_rural` twin, all are read off the row's own scope: no globals per row, no
ceiling but `RESULT_ROWS`. Not built: what a building costs.

## Rebuilding

    python3 mods/where_to_produce/tools/generate.py

or `python3 tools/refresh.py` for this and every other mod in the repository.
The owner does it from `mods.bat`.

## State

Ten loads in. The scoring, the whole-province rule and the results window are
confirmed; the ranking by output, the two-line row and the pickers moving into
that window are not. See [`CLAUDE.md`](CLAUDE.md). See
[`CLAUDE.md`](CLAUDE.md) for what the next run has to answer and what is known
to be unproven.

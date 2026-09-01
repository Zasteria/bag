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

## The whole plan

The fourth group on the Answer tab, and a second question rather than a bigger
version of the first: **every good at once over the chosen ground**, one building
at a time, under a cap per location.

- **Chosen per province, spent per location.** A province takes two short lists —
  one for its towns, one for its villages, each as long as that side's cap — and
  every location of it then builds its side's list entire. So a province reads as
  one answer and its villages repeat each other, which is how the ground is
  actually developed; what differs is the next province.
- **A list entry is a building, not a good.** A location holds one building of a
  type and a building runs one production method, so tools, jewelry and beer —
  all three off a market village — are one answer and not three. The list carries
  the building beside the good and a good whose building is taken is not offered.
- **And every building is one that may actually stand there.** The plan asks the
  game's own `can_build_building` in the location's scope, which is the terrain,
  the rank and the building's `location_potential` — a bog iron smelter wants
  wetlands or a lake, a sugar plantation wants sugar growing overseas. It is not
  the country's advances, so it is as true for ground you have not taken as for
  the end of the game.
- **An urban right is all or nothing.** Its bonus obliges every good of the
  bundle to be made where it is granted, so a province that can take two of three
  is not offered it at all.
- **And the two sides are the building's own rank gates.** `rural_settlement` is
  declared by thirty production buildings and only four of them are villages, so
  a rural location is offered quarries, clay pits, lumber mills and masons as
  well — `eu5data.Method.rural` / `.urban`, and the plan has scoring accumulators
  of its own because the ranking's split is by category instead.
- **Two buttons, now and at the end of the game**, the same pair the ranking has
  and for the same reason: along the ladder a recipe's inputs move, so the
  province that suits the guild is not the one that suits the mill.
- **Two caps, set in the game**: goods per rural location (3) and per town (4).
  The game exposes no building-slot count of any kind, so these are the player's
  figures; what makes them choosable is that the pass prints the capacity of the
  chosen ground beside the number of goods asking for room in it.
- **It reuses the ranking's scoring.** `bag_wtp_score_<g>` already leaves the
  best method for good `g` on every candidate, on both sides, so the plan runs it
  once per good and keeps the two numbers in `bag_wtp_p<g>` and `bag_wtp_pr<g>`.
  No second scoring path exists.
- **Every good is divided by its own best in this ground**, one divisor for both
  sides. Output is in units of the good, so a raw score compares nothing across
  goods and the biggest recipe would take every contested province. Normalized,
  each good peaks at 1000 on the province that suits it most.
- **Sweeps until the ground is full.** Every good takes one town list and one
  village list, then every good takes another, until a whole sweep adds nothing.
  A location the plan can feed is never left empty. «Не больше стольких провинций
  на товар» is the one ceiling above that, and it is off by default.
- **An urban right is a town list**, taken whole and taken first, and which right
  a province gets is asked of the province rather than of the rights: twelve
  rights and rarely that many provinces means a turn order would be the whole
  outcome. Behind a switch, on by default.
- **The answer is a table and a map.** Rows are locations ordered by province —
  provinces by how much the plan put in each, their locations together, towns
  first — and a map mode of the mod's own in the Economy category paints
  completeness: green where a location is filled to its cap, red where the plan
  put nothing.

- **Which locations count as towns is yours to override.** The game's rank is
  only what is true today, and the mod cannot guess which village you mean to
  raise, so the rank icon on a plan row is a button: town → village → back to the
  game's own answer. No plan run clears it.

**Everything the pass reads is a variable on a location.** `bag_wtp_load` and the
`bag_wtp_plan_goods` list are the answer; `bag_wtp_plan_town` and
`bag_wtp_plan_rural` are the province's two lists, written onto *every* location
of the province, and `bag_wtp_plan_prank` is what keeps its rows together.
**Never on the `province_definition`** — it holds no variable, and the plan that
tried placed nothing at all (`docs/PITFALLS.md`).
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

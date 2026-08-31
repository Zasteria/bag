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

## What is deliberately not here yet

Priorities, mass distribution, building-slot capacity, and any measure of what a
building costs to put up. The ranking still walks the fifty best provinces by
the *near* column unless told otherwise, so a province that is poor now and
first in the last age is only found with «Rank by the last age» ticked.

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

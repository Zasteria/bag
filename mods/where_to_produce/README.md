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
2. **Building and method.** One dropdown, 218 entries: every production method
   in the game that consumes a raw material, sorted by the good it produces and
   labelled `<good> <building> — <method>`.
3. **Rank.** Press the button. Every location inside the ticked regions is
   scored and the fifty best are listed, each with the efficiency the chosen
   method would gain there and how many of the raw materials it wants that
   province supplies, out of how many it wants in all.

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

## What is deliberately not here yet

Town rights, upgrades, priorities, mass distribution, and building-slot
capacity. Also the borders themselves are regions rather than anything painted
on the map — that is the shape the owner asked for first, on the way to picking
locations directly.

## The fifty-row limit

The result table holds fifty rows. That ceiling is CMF's, not this mod's, and it
is in exactly one place: list items are initialised through an unrolled chain of
`if`s that stops at item 50, because a CMM list ordinal has to be a literal —
`item = var:x` is pasted verbatim into the macro and kills the load. The
interface side has no cap, and neither do dropdowns.

Raising it means either carrying a fork of two CMF files (~3200 lines, which
would ride over every other CMM mod in the playset on each CMF update) or
leaving CMM for a window of this mod's own over a plain global list, which is
what Construction Manager's hidden window already does. The second is the way,
and it is the next structural job.

## Layout

```
in_game/common/
  on_action/           CMF's registration and callback hooks
  scripted_effects/    registration, the ranking pass, and four generated files
  scripted_triggers/   which locations are worth ranking
  scripted_guis/       one _on_changed per list -- without them a list is invisible
  script_values/       the bonus, and the readings the row labels print
main_menu/localization/{english,russian}/
tools/generate.py      everything above that comes out of the game's own files
```

## Rebuilding

    python3 mods/where_to_produce/tools/generate.py

or `python3 tools/refresh.py` for this and every other mod in the repository.
The owner does it from `mods.bat`.

## State

Written, never loaded. See [`CLAUDE.md`](CLAUDE.md) for what the first run has
to answer and what is known to be unproven.

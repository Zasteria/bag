# RGO Bonus Filter

An EU5 mod that adds a **Local Raw Materials** filter to the building list of a
location, keeping only the buildings that gain production efficiency from raw
materials produced in the province — the ones the game badges with the shovel.
Combined with the `production_efficiency` sort the panel already has, it answers
"what is worth building *here*" without scrolling past everything that is not.

Requires the Community Mod Framework (`community_mod_framework` 2.\*).

> Not yet run in game. Every file has been syntax checked and the generated
> predicate cross-checked against the game data it came from, but nothing here
> has been loaded by EU5 itself.

## How it works

The filter appears as a normal chip in the funnel menu of the buildings panel,
next to vanilla's own building filters. **No vanilla file is replaced**, so the
mod does not collide with other interface mods.

Three pieces make that possible.

**The filter.** `in_game/gui/filters/bag_rgo_filters.txt` declares one filter
with `scope = building_type` and `tag = building`. Any list that asks for the
`building` tag picks it up, which includes `LocationProductionView` — the
"Buildings of <town>" panel. Filtering has to happen here rather than by hiding
rows: the list body is a `fixedgridbox` with a fixed row height, so a hidden row
would still occupy its cell and leave a hole.

**The predicate.** The game answers "does this building gain from local raw
materials" with `BuildingType.HasPossibleRGOBonus`, but that is a GUI data
function and filter triggers run script, with no script counterpart anywhere in
`common/scripted_triggers/`. So `tools/generate_rgo_filter.py` reconstructs it
from the game files: it reads every production method each building type
offers, takes the goods those methods consume, and keeps the ones flagged
`category = raw_material`. The result is one trigger per raw material listing
the building types that consume it, written to
`in_game/common/scripted_triggers/bag_rgo_generated_triggers.txt`.

**The location.** A filter is handed the building type as `root` and the country
as `scope:target` — never the location on screen. A scripted widget
(`in_game/gui/bag_rgo/bag_rgo_location_probe.gui`) watches
`LocationProductionView.GetSelectedLocation` and parks it on the player country
through a scripted GUI, so the trigger can reach it. Scripted widgets are
injected by the engine and need no vanilla file, and the state re-arms itself
rather than firing every frame.

## Regenerating the predicate

Needed after a game patch that touches building types, production methods or
goods:

```
python3 tools/generate_rgo_filter.py "<EU5>/game/in_game/common"
```

As of 1.3.10 that covers 465 building types, 317 of which consume at least one
of the 52 raw material goods, over 678 building/material pairs.

## Settings

Under **Filter → Range** in the Mod Menu:

- **This Location Only** — count only raw materials produced in this very
  location. Off by default, matching the game's own shovel badge, which counts
  the whole province.

CMM keeps setting values in a variable map that script triggers cannot read, so
`cmm_sync_bool_alias` mirrors this one onto a plain country variable, refreshed
from `cmf_on_callback` whenever the setting changes.

## Layout

```
.metadata/metadata.json                    mod descriptor
in_game/common/on_action/                  CMF registration and callback hooks
in_game/common/scripted_effects/           registration, setting alias sync
in_game/common/scripted_guis/              location probe bridges
in_game/common/scripted_triggers/          filter entry point + generated predicate
in_game/gui/filters/                       the filter itself
in_game/gui/bag_rgo/                       probe widget
in_game/gui/scripted_widgets/              probe registration
main_menu/localization/<lang>/             English and Russian
tools/generate_rgo_filter.py               predicate generator
docs/RESEARCH.md                           notes on the EU5 mod format and CMF
```

## Known gaps

- The predicate matches the shovel badge's *potential* reading: a building
  passes if any of its production methods could use a local raw material. It
  does not check whether the method currently selected is the one that does.
- Buildings whose production methods come from `possible_production_methods`
  resolve against `common/production_methods/`; anything a DLC adds elsewhere is
  invisible to the generator until it is pointed at those files too.

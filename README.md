# RGO Bonus Filter

An EU5 mod that filters the building list of a location down to buildings which
gain production efficiency from raw materials available in the province — the
ones the game badges with the shovel icon. Combined with the sort control that
vanilla already provides on `production_efficiency`, it answers "what is worth
building *here*" without scrolling past everything that is not.

Requires the [Community Mod Framework](https://steamcommunity.com/workshop/)
(`community_mod_framework` 2.\*), which provides the settings menu the mod
registers into.

## Status

Scaffolding and game logic are in place. The interface half is not yet written —
see [Remaining work](#remaining-work).

| Piece | State |
| --- | --- |
| `metadata.json`, folder layout, CMF dependency | done |
| CMF registration hook | done |
| Mod Menu settings | done |
| Filter state + scripted GUI bridges | done |
| English / Russian localization | done |
| Target panel and filter format identified | done |
| The filter itself | **blocked** — see [Remaining work](#remaining-work) |

## Layout

```
.metadata/metadata.json              mod descriptor
in_game/common/on_action/            hooks into cmf_on_mod_registration
in_game/common/scripted_effects/     registration, filter on/off
in_game/common/scripted_guis/        toggle + state queries for the GUI
in_game/gui/filters/                 declarative list filters (empty for now)
main_menu/localization/<lang>/       localization
docs/RESEARCH.md                     notes on the EU5 mod format and CMF
```

## How it is meant to work

The target panel is `location_production_lateralview.gui` (`LocationProductionView`),
the "Buildings of <town>" list. Its list already declares
`WithFilterTags('building')`, so a filter file dropped into
`in_game/gui/filters/` shows up in its existing funnel menu as a chip, next to
vanilla's own building filters. Sorting is untouched — the panel already offers
a `production_efficiency` sort key that orders both ways.

That is deliberately not a GUI override. The list body is a `fixedgridbox` with
a fixed row height, so hiding rows from the interface would leave holes in the
list; only a real filter removes items. It also keeps the mod compatible with
every other UI mod, since no vanilla file is replaced.

## Remaining work

The filter needs a `trigger` that answers "does this building type gain
efficiency from raw materials in this province". The game answers that question
in the interface — `BuildingType.HasPossibleRGOBonus(country, location)` drives
the shovel badge and `Building.IsUsingRGOBonus(country, location)` colours it —
but those are GUI data functions, and filter triggers run *script*. Nothing in
`common/scripted_triggers/` exposes the same thing.

Two ways forward, and which one applies is not yet decided:

1. **A script trigger exists.** Then the filter is one small file and the mod is
   essentially done. Settling this needs the engine's trigger list, which
   `script_docs` dumps to `logs/triggers.log`.
2. **No script trigger exists.** Then the predicate gets generated from game
   data: read which production methods each building type offers and which goods
   they consume, cross them with the raw materials a province can produce, and
   emit a generated scripted trigger. Glorp UI ships generated files
   (`glorpui_generated_trait_scripted_triggers.txt`) for much the same reason.
   This needs `common/building_types/`, `common/production_methods/` and
   `common/goods/` from the game folder.

One wrinkle either way: filter triggers get the building type as `root` and the
country as `scope:target` — never the location. The viewed location has to be
parked in a country variable first by a zero sized probe widget with
`trigger_on_create = yes`, the trick Glorp UI already uses to feed Construction
Manager's own R.G.O. filter. `bag_rgo_filter_toggle` and its siblings are the
scripted GUI side of that plumbing.

## Settings

Registered under **Buildings → Local Resource Filter** in the Mod Menu:

- **Enabled By Default** — start with the filter on each time the list opens.
- **Only Active Bonuses** — keep only buildings already using the local
  materials, instead of every building that could.


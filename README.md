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
| Filter button and row visibility in the building list | **not started** |

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

The location building list already knows which buildings benefit from local raw
materials — `BuildingType.HasPossibleRGOBonus(country, location)` drives the
shovel badge, and `Building.IsUsingRGOBonus(country, location)` decides whether
it is drawn green (bonus in use) or yellow (available but the current production
method does not take it).

The filter reuses those predicates. A toggle button in the list header calls the
`bag_rgo_filter_toggle` scripted GUI, which flips the `bag_rgo_filter_active`
country variable; rows then hide themselves while that variable is set and the
building fails the predicate. Sorting is untouched — vanilla's
`production_efficiency` sort key already orders ascending and descending.

## Settings

Registered under **Buildings → Local Resource Filter** in the Mod Menu:

- **Enabled By Default** — start with the filter on each time the list opens.
- **Only Active Bonuses** — keep only buildings already using the local
  materials, instead of every building that could.

## Remaining work

Writing the interface layer needs the vanilla `.gui` source for the location
building window, which is not in this repository:

1. Confirm which vanilla file owns the window and copy the widget type for a
   building row into `in_game/gui/`.
2. Add the toggle button next to the existing search field and sort buttons.
3. Gate each row on the filter state and the RGO predicate.
4. Decide between that override and a declarative entry in
   `in_game/gui/filters/` — cheaper and conflict-free, but only workable if a
   script-side trigger for the RGO bonus exists, since filter `trigger` blocks
   run script rather than GUI functions.

Overriding a vanilla `.gui` wholesale is what makes UI mods collide, so prefer
the declarative filter if the trigger turns out to exist.

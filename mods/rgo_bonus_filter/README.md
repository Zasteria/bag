# RGO Bonus Filter

An EU5 mod that cuts the noise out of both building lists, leaving only what
gains production efficiency from raw materials in the province — the buildings
the game badges with the shovel. Two filters, one per direction:

- **Local Raw Materials**, in a location's buildings panel — what is worth
  building *here*.
- **Local Raw Materials For This Building**, in the build panel — *where* in the
  realm to put a building you have already picked.

Both sit next to the sorts the panels already have, so sorting by production
efficiency or income turns either one into a ranked shortlist.

Requires the Community Mod Framework (`community_mod_framework` 2.\*).

> The buildings panel filter is working in game, lightly tested. The build panel
> filter is new and unverified.

## How it works

Each filter appears as a normal chip in its panel's funnel menu, next to
vanilla's own building filters.

Three pieces make that possible.

**The filters.** `in_game/gui/filters/bag_rgo_filters.txt` declares two, both
tagged `building`: one `scope = building_type` for `LocationProductionView`, the
buildings panel of a location, and one `scope = location` for
`BuildInLocationLateralView`, the panel that picks where to build. Both panels
request the same tag, so both filters are offered in both — each is only
meaningful in its own. Filtering has to happen here rather than by hiding rows:
the list bodies are `fixedgridbox`es with fixed row heights, so a hidden row
would still occupy its cell and leave a hole.

**The predicate.** The game answers "does this building gain from local raw
materials" with `BuildingType.HasPossibleRGOBonus`, but that is a GUI data
function and filter triggers run script, with no script counterpart anywhere in
`common/scripted_triggers/`. So `tools/generate_rgo_filter.py` reconstructs it
from the game files: it reads every production method each building type
offers, takes the goods those methods consume, and keeps the ones flagged
`category = raw_material`. Only methods that actually output a good count — the
game badges a building on `And(BuildingType.IsProducing, HasPossibleRGOBonus)`,
and a monastery burning clay for upkeep produces nothing for a raw material to
make more efficient. The result is one trigger per raw material listing the
building types that consume it, written to
`in_game/common/scripted_triggers/bag_rgo_generated_triggers.txt`.

**The missing half of the context.** Each filter is handed the object it tests
and little else. A `building_type` filter gets `root` alone — not even
`scope:target`, whatever vanilla's `58_building_type.txt` comment claims — so it
never learns which location is on screen. A `location` filter never learns which
building type is being placed. Both gaps are filled the same way: a probe widget
parks the missing half in a global variable through a scripted GUI, and the
trigger reads it back. Each probe re-arms itself rather than firing every frame.

Those probes are what cost vanilla files. A view object only resolves inside its
own panel — from a scripted widget it comes back null and logs an error every
frame — so each probe lives in a copy of the panel it watches:

| File | Probe stores |
| --- | --- |
| `in_game/gui/location_production_lateralview.gui` | the location being viewed |
| `in_game/gui/bag_rgo_build_location_window.gui` | the building type being placed |

**Redefine the window, not the panel's types.** Construction Manager and Glorp
UI both restyle the build panel by redefining `types buildLocationTypes` from
files of their own. Shipping a copy of vanilla's `build_location_lateralview.gui`
carried vanilla's version of those same types along with the probe, and
whichever loaded last won — which is how this mod was stripping Construction
Manager's mass-build button of its icon. The build panel is now 149 lines
holding the window alone, so every type is left to whoever wants it.

`location_production_lateralview.gui` is still a whole-file copy, because
nothing else touches that panel. Both are pinned to 1.3.10: re-copy after a
patch that changes them.

## Regenerating the predicate

Needed after a game patch that touches building types, production methods or
goods:

```
python3 mods/rgo_bonus_filter/tools/generate_rgo_filter.py "<EU5>/game/in_game/common"
```

As of 1.3.10 that reads 465 building types, of which 110 consume a raw material
while producing something, over 293 building/material pairs across 40 materials.

## Province or location

Each panel offers both as chips of its own rather than a chip and a setting:

- **Local Raw Materials** — the material is worked anywhere in the province.
  This is what the game's own shovel badge means.
- **Local Raw Materials (This Location)** — stricter; the location works it
  itself.

The mod has no settings. Putting the choice in the funnel next to the filter it
changes beats hiding it three menus away in the Mod Menu.

## Layout

```
.metadata/metadata.json                    mod descriptor
in_game/common/on_action/                  CMF registration and callback hooks
in_game/common/scripted_effects/           registration, setting alias sync
in_game/common/scripted_guis/              probe bridges for both panels
in_game/common/scripted_triggers/          filter entry points + generated predicate
in_game/gui/filters/                       the two filters
in_game/gui/location_production_lateralview.gui
                                           vanilla panel + location probe
in_game/gui/build_location_lateralview.gui
                                           vanilla panel + building type probe
main_menu/localization/<lang>/             English and Russian
tools/generate_rgo_filter.py               predicate generator
../docs/RESEARCH.md                        notes on the EU5 mod format and CMF
```

## Known gaps

- The predicate matches the shovel badge's *potential* reading: a building
  passes if any of its producing methods could use a local raw material. It does
  not check whether the method currently selected is the one that does.
- Buildings whose production methods come from `possible_production_methods`
  resolve against `common/production_methods/`; anything a DLC adds elsewhere is
  invisible to the generator until it is pointed at those files too.

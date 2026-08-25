# How the engine works

What EU5 itself gives a mod: where to ask what exists, how a mod is
laid out, how the interface is put together, and where the numbers live.

## The game prints its own API

With `-debug_mode` on the launch options, the console commands `script_docs` and
`dump_data_types` write the complete list of what the engine understands. Those
dumps are in the repository, under `reference/game/docs/`:

| File | Holds |
| --- | --- |
| `effects.log` | 1534 effects, each with its supported scopes and targets |
| `triggers.log` | 1798 triggers, the same |
| `event_targets.log` | scope links, with input and output scopes |
| `on_actions.log` | every on_action and its expected scope |
| `modifiers.log` | every modifier tag and its categories |
| `custom_localization.log` | the customizable localization keys |
| `data_types/` | every GUI data function, promote and return type |

Ask them rather than reading them:

```
python3 tools/api.py set_subsidized       exact name, across every dump
python3 tools/api.py --find subsid        substring, anywhere
python3 tools/api.py --scope building     everything taking that scope
python3 tools/api.py --gui IsAvailable    GUI data functions only
```

**This replaces the rule this repository ran on for months** — "if vanilla or one
of the reference mods does not use it, treat it as unproven". That rule is now
only about *usage*, not about existence, and the difference is expensive: half a
mod was scoped around subsidies being impossible from script, because nothing in
`common/` used `set_subsidized`. The engine had it all along.

What the dumps do *not* say is how something behaves, what a sensible argument
is, or whether an effect does anything useful in a given scope. That still comes
from vanilla and from the reference mods — and, in the end, from a run.

## Mod layout

EU5 splits a mod by *load context* at the top level, which is new compared to
EU4/CK3:

```
<mod>/
  .metadata/
    metadata.json          descriptor (replaces descriptor.mod)
    thumbnail.png
  in_game/                 loaded once a game session exists
    common/
      on_action/           event hooks
      scripted_effects/    reusable effects
      scripted_triggers/   reusable triggers
      scripted_guis/       is_shown / is_valid / effect bridges for the GUI
      script_values/       computed numbers
      game_concepts/
      customizable_localization/
    gfx/
    gui/
      filters/             data driven list filters
      scripted_widgets/
      *.gui                interface layout
  main_menu/               loaded at the launcher / main menu
    gfx/
    gui/
    localization/<lang>/*.yml
  loading_screen/
    data_binding/          GUI macros
    input_profile/         keybinds
```

`metadata.json` carries `id`, `version`, `game_id`, `supported_game_version`,
`tags` and a `relationships` array. Dependencies on other mods are declared
there:

```json
"relationships": [
    { "rel_type": "dependency", "id": "community_mod_framework",
      "display_name": "Community Mod Framework",
      "resource_type": "mod", "version": "2.*" }
]
```

Script and localization files carry a UTF-8 BOM. Localization keys take one
leading space under the `l_<language>:` header, as in earlier Clausewitz games.

## The RGO production efficiency bonus

The shovel badge on a building row is `gfx/interface/icons/sort/rgo.dds`. The
game exposes the state behind it through two GUI data functions, both of which
take the owning country and the location:

| Function | Object | Meaning |
| --- | --- | --- |
| `HasPossibleRGOBonus(country, location)` | `BuildingType` | The building *could* gain efficiency from raw materials present in the province |
| `IsUsingRGOBonus(country, location)` | `Building` | Its current production method actually consumes them |
| `HasBuildingRGOBonus(production_method)` | `Building` | Same, asked per production method |
| `ProductionEfficiencyInfo(country, location)` | `BuildingType` | String pair list used for the tooltip breakdown |
| `GetBuildingProductionEfficiencyInfo(production_method)` | `Building` | Per method variant of the same breakdown |

`location_window.gui` drives the badge with them — the icon is visible on
`And(BuildingType.IsProducing, BuildingType.HasPossibleRGOBonus(...))`, and it
is tinted green through `IsUsingRGOBonus` or yellow otherwise, with tooltip
strings `RGO_BONUS`, `PROD_METHOD_BONUS_ACTIVE` and `PROD_METHOD_BONUS_POTENTIAL`.
`building_view.gui` uses the per method pair to mark which production method
would pick the bonus up.

These are GUI data functions. There is no script-side counterpart in
`common/scripted_triggers/`, so a filter `trigger` cannot call them directly.

### The formula behind the number

The game shows the bonus only as tooltip text — "Coal in the Ore Mountains,
+2.86%". Recovered by matching those readings, and **verified to the digit
against three of them at 1.3.10**:

```
RGO bonus % = 10 * (input amounts the province supplies) / (all input amounts)
```

| Building / method | Available | Computed | Tooltip |
| --- | --- | --- | --- |
| `saltpeter_guild` / `saltpeter_guild_demands` | livestock | 8.33% | +8.33% |
| `weapon_guild` / `weapon_smith_maintenance` | coal | 2.86% | +2.86% |
| `mason` / `clay_bricks` | clay | 10.00% | +10.00% |

**Every input counts towards the denominator**, produced goods included — an RGO
can never supply tools, but tools still carry their weight:

```
weapon_smith_maintenance   lumber 0.2521 + coal 0.3034 + tools 0.5050 = 1.0605
                           lumber and coal are all an RGO can give
                           0.5555 / 1.0605  ->  ceiling 5.24%, not 10%
```

The bonus is production *efficiency*, so it multiplies output:
`volume = output * (1 + bonus / 100)`. That is the figure that compares two
buildings: a jeweller's guild and a village carver both reach 10%, but on outputs
of 1.0 and 0.1, so ranking on the percentage alone puts them level.

The community "Province Breakdown" spreadsheet tops out at 12.5% on single-input
buildings because it was built from patch 1.0.6; 1.3.10 tops out at 10%.

`tools/eu5data.py` holds all of this in code — it resolves every method per
building type, inline and shared, and skips upkeep methods that produce nothing.

## Which window is which

Three different panels list buildings, and they are easy to mix up:

| File | View object | Lists |
| --- | --- | --- |
| `location_production_lateralview.gui` | `LocationProductionView` | Buildings of one location — the "Buildings of <town>" panel |
| `production_lateralview.gui` | `ProductionView` | Buildings across the whole country (macrobuilder) |
| `build_location_lateralview.gui` | `BuildInLocationLateralView` | Locations to build one chosen building type in |
| `location_window.gui` | `LocationView` | The location panel itself, where the RGO badge is drawn |

`location_production_lateralview.gui` is the one to target for a
"only what is efficient here" filter. Its list is
`LocationProductionView.GetBuildingsSortSearch.WithFilterTags('building')`, its
items are `BuildingItem`, and its sort keys are `name`, `profit`, `income`,
`production_efficiency` and `level`. Glorp UI does not override this file.

## List filters

`in_game/gui/filters/*.txt` defines filters declaratively, and
`filters/readme.txt` documents the schema. The fields that matter:

| Field | Meaning |
| --- | --- |
| `scope` | Object type the filter runs on; `root` is that object |
| `trigger` | Script trigger deciding whether the object passes |
| `tag` | Pipe separated list; a view exposes filters whose tags intersect its `WithFilterTags(...)` call |
| `group` | Groups filters under one UI background |
| `exclusive_group` | Radio button behaviour inside the group |
| `invert` | Exclude by default, include when ticked |
| `enabled_at_start` | Initial tick state |
| `hidden_in_searchbar` | Filter works and appears in the side menu, but shows no chip — for panels with a dedicated button |
| `range` | `min` / `max` / `step` / `format`, exposes `scope:min_value` and `scope:max_value` to the trigger |

Localization keys are `search_filter_<key>_name`, `_desc` and `_format`.

Sub-items matter: "For lists with sub-items, if one of the sub-items pass the
filter, the entire item pass it." That is how one `building` tag serves filters
scoped to `building_type` (`58_building_type.txt`), `building`
(`42_building.txt`) and `location` (`05_location.txt`) at once.

For building scoped filters, `root` is the building or building type. **The
location is not passed in**, which is the awkward part for anything province
dependent — the viewed location has to be parked in a global variable by a
scripted GUI probe first. Glorp UI does much the same for Construction Manager's
own R.G.O. filter, storing the viewed building type through
`cm_rgob_store_selected_type` from a zero sized widget with
`trigger_on_create = yes`. What else a filter can read depends on its scope; see
[Filter scopes](#filter-scopes-what-a-trigger-actually-gets).

Filters are the right tool rather than hiding rows from the GUI: the list body
is a `fixedgridbox` with a fixed row height, so a hidden row still occupies its
cell and leaves a gap.

Not every filter key is script defined — `hide_estate_only_buildings` is
referenced by `SearchBar.EnableFilterByKey` in three panels but appears nowhere
in `gui/filters/`, so some are built into the engine.

## Filter scopes: what a trigger actually gets

`58_building_type.txt` opens with "root is the building_type / scope:target is
the country to filter". The second half does not hold: no vanilla
`building_type` filter ever reads `scope:target`, and one that does matches
nothing and logs an error on every pass of the list. Only the `building` and
`location` scoped files use it (`building_can_be_upgraded_by = scope:target`,
`owner = scope:target`), so treat it as available there and absent here.

A `building_type` filter therefore sees `root` and global variables, nothing
else. Anything else a filter needs — the location on screen, a user setting —
has to be parked in a global variable first. CMM settings registered with
`cmm_register_global_bool_setting` land in the global half of the `cmm` map, and
`cmm_sync_bool_alias` then mirrors them onto a plain global variable a trigger
can read.

Evaluating a view's data in a always-present widget needs a guard: reading
`LocationProductionView.GetSelectedLocation` while no buildings panel is open
logs an error every frame. Taking it as a `datacontext` on a child widget and
gating that child on `Location.IsValid` keeps it quiet.

Square brackets in a localization value are data function syntax, so a display
name like `[debug] location known` renders as `ERROR:` — brackets have to stay
out of plain text.

## View objects are panel scoped

`LocationProductionView`, and by the look of it the other `*View` objects, only
resolve inside the widget tree of their own panel. Vanilla never reads
`LocationProductionView.GetSelectedLocation` outside
`location_production_lateralview.gui`; other files only call the global
`ShowLocationProductionView(...)` to open it.

Reading one from a scripted widget fails, and fails loudly — a zero sized always
present widget doing so logs on every frame:

```
FetchData failed for 'Location.IsValid' - gui/bag_rgo/bag_rgo_location_probe.gui:22
Promote 'AddScope' returned nullptr, in 'GuiScope.SetRoot(GetPlayer.MakeScope).AddScope('bag_rgo_loc', Location.MakeScope).End'
```

The `datacontext` silently yields nothing, so every expression depending on it
fails. Scripted widgets themselves work fine — the file loads and its states run
— but anything panel scoped has to be injected into that panel's own file.

`error.log` names the file and line for GUI failures, which makes it the fastest
way to tell "the widget never loaded" from "the widget loaded and its
expressions fail". Script side failures show up there too; a filter trigger that
merely returns false logs nothing at all.

## Scripted widgets

`in_game/gui/scripted_widgets/*.txt` maps `<gui path> = <widget name>`, one per
line, and the engine instantiates those widgets into the running interface. That
is how a mod adds behaviour without copying a vanilla `.gui`. CMF registers
twelve of them this way; `python3 tools/guicost.py --drivers` lists what every
mod in the tree registers, so nothing here has to remember a count.

Global view objects such as `LocationProductionView` stay readable from any
widget, so a scripted widget can observe a panel it is not part of.

CMF's change detectors are the pattern to copy. `cmm_window_open_gate.gui` uses
`state = { trigger_when = "[...]" on_start = ... }`, which fires when the
condition turns true and re-arms once it goes false again — no polling, and no
`trigger_on_create` juggling. `cmf_country_transfer.gui` shows the older variant
built on `GetVariableSystem` plus `TriggerAnimation`.

**They never come down.** A scripted widget is registered for the session, not
for as long as it is useful, and hiding it with `visible = no` hides a live
widget tree whose `visible`, `enabled` and `datacontext` expressions are still
asked every frame. So the cost of one is its whole subtree, paid from load,
whether or not the player ever opens the mod. CMF's twelve come to 104 widgets
and Construction Manager's three to 96 — probes, which is the size a scripted
widget is meant to be. Advanced Auto Build registers seven whole windows,
**14 125 widgets**, against a vanilla interface of about 27 800 in total.

**`GetScriptedGui('x')` is the expensive expression.** It runs a script trigger
from the interface, entering the script engine, and vanilla uses it **nine
times** across 387 `.gui` files — it is not what the base game reaches for. A
count in the thousands means a mod has moved its logic into the interface layer
and is paying for it every frame the widget is alive.

**An animation state that names itself as its own `next` is a timer.** Inside an
always-live window that is a background worker with no off switch;
`eu5ab_engine_queue_window` runs eight of them at 0.15 s, each walking a
`datamodel` of locations × building types and calling
`GetBuildOrExpandBuildingCost`, `GetBuildingTypeProfitInLocation` and
`CanBuildOrExpandBuilding` per pair. The window keeps itself "visible" with
`[EqualTo_CFixedPoint('(CFixedPoint)0', '(CFixedPoint)0')]` and parks at
`position = { -10000 1 }` so it ticks offscreen.

`python3 tools/guicost.py` counts all three across the game and every mod in the
tree, with `--drivers` for the always-live windows and their loop periods. It was
written for the question *why does a panel open instantly in vanilla and with a
hitch under the playset*; the answer it gives is in
[`HANDOFF.md`](../HANDOFF.md#the-second-slowdown--panels-open-slower-with-mods-from-the-first-minute).

## Sorting

Sorting is already data driven. `sort_by_key_button` entries name a sort key,
and `production_efficiency` is one of the keys vanilla exposes on building
lists, with `gfx/interface/icons/sort/efficiency.dds` as its icon. Ascending /
descending toggling is built into the button. So the sorting half of a
"most efficient buildings here" workflow needs no new code — only the filter.

There is no built-in sort key for the RGO bonus itself. Sweeping every
`sort_by_key_button` in vanilla turns up `rgo_profit` and `rgo_income`, which
are about raw material output, not about a building picking the bonus up.

## Localization is code, and the Russian files do not compile

A `.yml` value is not text with decorations in it. `[...]` is a data function,
`$...$` quotes another key, `@name!` is a texticon and `#tag ... #!` is
formatting, and the engine parses all of it before anything reaches the screen.
When the parse fails the key produces nothing — not a fallback, not the English,
nothing — and the failure lands in `gui.log` as
`Failed parsing localized text: <key>` or in `error.log` as `FetchData failed
for '<expression>'` followed by `Data error in loc string '<key>'`.

The game's own Russian files fail this way in 146 places. What they get wrong is
worth knowing because a mod can get it wrong the same ways:

**Brackets have to balance.** Fifty-five keys do not. `|W ед.` was meant to be
`|W] ед.` and swallowed the rest of the sentence; `«[[FinishedWarUnitStats` has
one bracket too many.

**An accessor has to exist.** `dump_data_types` lists every one, root and member
alike, so `python3 tools/api.py <name>` settles it. Thirty-six Russian keys call
things like `GetAdjectvive`, `GetGovernnment`, `GerHerHis` and `GetFinishedDate`,
and the last of those is instructive: it is not a typo but a stale name, and the
English key of the same name uses `GetFinishedDateIncludingQueue`. **Comparing
the two languages' version of the same key is the cheapest bug finder there is.**

**A name accessor ends the chain.** `Country.GetName.Custom('CL_GEN')` cannot
work: `GetName` has produced text, and text has no members. Twenty-seven Russian
keys do exactly this.

**A custom localization declares the scope it runs in**, and
`reference/game/docs/custom_localization.log` says which — `Scope: country`,
`Scope: location`, `Scope: international_organization`. Handed anything else it
returns nothing. `[Loan.Custom('CL_DAT')]` asks a loan for a country's declension.

**A `$key$` reference is not always transparent.** In a search filter's name or
description it loses the object the filter is being built for, while a data
function written inline in the same string resolves normally. The evidence is
two keys four lines apart in `lists_l_russian.yml` doing the same job two ways,
one of which never fails and one of which always does. Assume the same anywhere
a string is built per object, and inline the data function.

**Some faults only the engine can see.** A promote that returns `nullptr`
(`TOWN_RIGHTS` where the key meant `TOWN_RIGHTS_TYPE`), a scope that is not
supplied (`LOCATION.GetProvince` in a tooltip whose context is `Location`), a
`Cabinet.` promote the engine explicitly refuses in a cabinet action's tooltip —
none of these are visible in the file. They are visible in the log, which is the
argument for reading it after every run rather than only when something looks
wrong.

`mods/ru_loc_fix/tools/locscan.py` is all of this written as rules, and can be
pointed at any localization tree.

## The interface is about 27 800 widgets, and nothing frees them

Two numbers worth carrying, both asked of the files rather than guessed.

**Every `.gui` the game ships declares roughly 27 800 widgets between them** —
that is the whole interface, every window, counted as widget declarations across
`in_game/gui/`. The heaviest single files are `ui_library.gui` (1 420),
`location_window.gui` (988), `alertmanager.gui` (770) and `cooltip.gui` (627).
A live session holds about 37 000 right after loading, so the multiplier from
`datamodel` instances is modest. When a count in
`performance_degradation.log` reaches six figures, that is instances piling up,
not a heavy panel.

**The engine exposes no way to release a widget.** `dump_data_types` has no
`Destroy`, `Clear`, `Free`, `Collect`, `Prune` or `Reset` on any GUI type — every
such name in the dumps belongs to a building, an asset editor, or a variable
system (`VariableSystem.Clear`, `UIVariables.ClearAll`). `PdxGuiWidget` offers
`Hide`, `FindChild`, `FindParent`, `GetChildrenCount`, `CountVisibleChildren`,
animation control and highlight setters, and nothing that unmakes anything. So a
mod can stop widgets being created, and cannot make existing ones go away.

`PdxGuiWidget.GetChildrenCount` is worth remembering anyway: it is the one hook a
mod has for measuring the size of a widget tree from inside the game.

## Defines, and where they actually live

Not under `common/defines/` where a Paradox habit would put them —
**`game/loading_screen/common/defines/`**, because they have to be read before
anything else loads. The tree carries them:

| | |
| --- | --- |
| `00_defines.txt` | the main file, ~148 KB, sections `NGame NGUI NText NCountry NAI NLocation NMarket NEconomy …` |
| `graphic/00_graphics.txt` | rendering |
| `jomini/00_tooltips.txt` | **tooltip timings** |
| `jomini/*.txt` | fog of war, rivers, roads, adjacencies, icons, map editor |

A defines file is overridable by a mod, and the game demonstrates it on itself:
`jomini/00_tooltips.txt` opens with `# This file overrides
cw/jomini/modules/tooltip_manager/data/common/defines/jomini/00_tooltips.txt`.

**`NGUI` holds nothing about widgets.** Twenty lines: rename length, how many
rows a breakdown shows, how many things Ctrl-click queues, side-menu margins,
food alert thresholds, hint carousel time. No pool, no cache, no arena, no limit.
So "raise the widget limit" has no knob — asked and answered, do not re-check.

One line in it is worth remembering anyway, because it shows the engine does
know how to evict things:

```
PURGE_COA_SEARCH_COUNT = 100 # How many COA entries we will search through in a frame for purging
```

Coats of arms get purged a hundred entries a frame. Widgets get no such
treatment, and nothing exposes one.

## The debug toolbox

`debug_mode` in the console, then a toolbox appears. As of 1.3.11:

```
TOOLBOX     Language  Environment  Map menu  Inspect  Explorer  Unit Viewer  Errors
2D Tools    UI Editor  Animator  UI Bounds  UI Library  Workbench  Reload GFX
3D Editors  E. Designer  Animation Edit  Particle Edit
```

`Tweaker`, `DrawCmdsViewer` and `ScriptProfilerGui` are types in the data dumps
but have no button here, so they are not reachable this way.

`UI Editor` is the live widget tree — the one tool that can name a widget that
should not exist. `UI Bounds` outlines every widget on screen. `Inspect` reports
what is under the cursor. `Errors` is `error.log` in a window.

## Building types, production methods and goods

`common/building_types/*.txt` defines each building type. Production methods
come from either of two fields, and a type can use both:

- `unique_production_methods = { <name> = { ... } }` — written inline
- `possible_production_methods = { <name> ... }` — names resolved against
  `common/production_methods/`

A production method lists its goods inputs as bare `<goods> = <amount>` pairs
alongside `produced`, `output`, `category` and `debug_max_profit`. Everything
numeric except `output` is a goods input:

```
saltpeter_guild_demands = {
	pottery = 0.1961
	livestock = 0.9804
	produced = saltpeter
	output = 1
	category = guild_input
}
```

`common/goods/*.txt` marks each good `category = raw_material` or `produced`,
defaulting to `raw_material` when omitted. A location's RGO good is its
`raw_material` scope link, and `province = { any_location_in_province = { ... } }`
walks the province from a location — the two pieces needed to ask whether the
province produces something a building type consumes. That reconstruction
matches the game: `saltpeter_guild` consumes `livestock`, and the tooltip in the
buildings panel credits "Livestock in the province" for its efficiency bonus.

Building types also carry `location_potential`, a trigger with the location as
root, which is how vanilla gates where a type may be built at all —
`saltpeter_guild` wants `livestock` and `clay` in the market.

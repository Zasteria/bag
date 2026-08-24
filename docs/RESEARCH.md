# EU5 modding notes

Findings from reading two shipped EU5 mods: **Community Mod Framework** 2.3.3
(`community_mod_framework`) and **Glorp UI** 1.3.10.1 (`glorp.ui`). Both target
game version 1.3.\*.

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

## Scripted widgets

`in_game/gui/scripted_widgets/*.txt` maps `<gui path> = <widget name>`, one per
line, and the engine instantiates those widgets into the running interface. That
is how a mod adds behaviour without copying a vanilla `.gui`. CMF registers four
of them this way.

Global view objects such as `LocationProductionView` stay readable from any
widget, so a scripted widget can observe a panel it is not part of.

CMF's change detectors are the pattern to copy. `cmm_window_open_gate.gui` uses
`state = { trigger_when = "[...]" on_start = ... }`, which fires when the
condition turns true and re-arms once it goes false again — no polling, and no
`trigger_on_create` juggling. `cmf_country_transfer.gui` shows the older variant
built on `GetVariableSystem` plus `TriggerAnimation`.

## Sorting

Sorting is already data driven. `sort_by_key_button` entries name a sort key,
and `production_efficiency` is one of the keys vanilla exposes on building
lists, with `gfx/interface/icons/sort/efficiency.dds` as its icon. Ascending /
descending toggling is built into the button. So the sorting half of a
"most efficient buildings here" workflow needs no new code — only the filter.

There is no built-in sort key for the RGO bonus itself. Sweeping every
`sort_by_key_button` in vanilla turns up `rgo_profit` and `rgo_income`, which
are about raw material output, not about a building picking the bonus up.

## Community Mod Framework

CMF sets `cmf_active` as a global variable and keeps `cmf_active_mod_ids` as a
global list, so mods can detect each other. Glorp UI uses exactly that to check
for Construction Manager:

```
is_target_in_global_variable_list = { name = cmf_active_mod_ids target = flag:cm }
```

### Hooks

CMF adds the on_actions vanilla lacks. The important ones:

| on_action | Scope | When |
| --- | --- | --- |
| `cmf_on_mod_registration` | country | New game, save load and country transfer, per human country |
| `on_game_start_after_lobby` | none | New game, after country selection |
| `on_game_start_after_lobby_human_country` | country | Same, per human country |
| `on_game_load_after_lobby` | none | Save load, past the country selection screen |
| `cmf_on_country_transfer` | country | After the player switches country |
| `cmf_on_callback` | country | A CMM setting changed, or an alert / action bar button was clicked |
| `cmf_yearly_human_country_pulse` | country | Yearly, players only |
| `cmf_monthly_human_country_pulse` | country | Monthly, players only |

Vanilla `on_game_start` fires *before* the country selection screen, so
`is_ai = no` matches nothing there — that is what the `_after_lobby` variants
exist for.

A mod opts in by declaring the same on_action in its own file and appending a
leaf action; the engine merges the `on_actions` lists.

### Mod Menu settings (CMM)

Registration effects, called from `cmf_on_mod_registration`:

- `cmm_register_bool_setting` / `cmm_register_global_bool_setting`
- `cmm_register_dropdown_setting` (+ `cmm_set_dropdown_multiselector`)
- `cmm_register_numeric_setting`, `cmm_register_slider_setting`
- `cmm_register_text_setting`, `cmm_register_button_setting`
- `cmm_begin_settings_list` / `cmm_add_settings_list_item` / `cmm_finish_settings_list`

`global` variants store one value for the session; the plain ones store per
country, which is what a per-player UI preference wants.

Keys are derived, and localization has to match:

| Thing | Key |
| --- | --- |
| Mod | `<mod_id>_name`, `<mod_id>_desc` |
| Tab | `<mod_id>__<tab_id>_name` |
| Group | `<mod_id>__<tab_id>__<group_id>_name` |
| Setting | `<mod_id>__<setting_id>_name`, `_desc` |
| Dropdown option | `<mod_id>__<setting_id>_option_<n>_name` |
| Button caption | `<mod_id>__<setting_id>_text` |

The GUI reads a setting back with `CMMSettingValue('<mod_id>__<setting_id>')`,
and `CMMSettingIsRegistered(...)` guards against the mod being absent.

Registering any CMM setting marks the mod active automatically;
`cmf_register_mod = { mod_id = ... }` does it explicitly.

### CMM list settings

A list setting is not like the others, in three ways that each fail silently.

**It is invisible without `<mod_id>__<setting_id>_on_changed`.** Registering a
list marks the setting as having a scripted GUI, and `CMMSettingRowVisible` then
gates the row on `CMMGuiIsShown(Concatenate(SettingKey, '_on_changed'))`. Absent
that scripted GUI the whole widget is hidden, header included. The *group*
header still renders, because `_cmm_register_setting_metadata` files a list under
`group_id = <setting_id>`, so a missing callback looks like an empty list rather
than a missing one.

**Lists have no auto-apply.** `cmm_core_auto_apply_scripted_gui.txt` covers
bool, dropdown, numeric, slider and button settings, and each of those fires
`cmf_on_callback`. A list does not: the widget marks the pending change and calls
that same `_on_changed` scripted GUI, which has to call `cmm_apply_list_change`
to commit it. Nothing about a list reaches `cmf_on_callback`.

**The dynamic builder runs once.** `cmm_begin_settings_list`, every
`cmm_add_settings_list_item` and `cmm_finish_settings_list` are gated on
`cmm_list_initialized_<setting>`, which `cmm_register_*_settings_list` sets. So
a list can be built dynamically *or* registered statically, never registered and
then refilled. For a list whose contents change, register it once at its full
height and write rows in place:

| Effect | Does |
| --- | --- |
| `cmm_set_list_item_value` | the scope or flag the row stands for |
| `cmm_set_list_data_value` | any field's value, bool fields included — they share one `cmm` variable map |
| `cmm_hide_list_item` / `cmm_show_list_item` | rows the current contents do not need |
| `set_variable = { name = <mod>__<setting>_i<n>_name value = flag:<key> }` | the row label, localized from the flag |
| `cmm_for_each_list_item` | calls an effect per row with the ordinal already resolved as `$i$` |
| `cmm_build_list_bool_list` | the values of the rows whose bool field is set |

Item ordinals must be literals — `item = var:x` is pasted into the macro verbatim
and dies at load with "More than one colon in event target link". CMF turns
counters into literals with a `switch`, and so should anything built on it.

Construction Manager is the working reference: `cm_cmm_effects.txt` registers
statically and `cm_cmm_scripted_gui.txt` holds one `_on_changed` per list.

### What CMM actually reads from localization

`cmm_setting_row.gui` builds a row's text from three suffixes and no others:
`CMMLocalizedSuffix(<setting key>, '_name')`, `..._desc` for the hover tooltip
and `..._text` for a button setting's caption. There is **no `_format` suffix
for a plain setting** — the only formatted values in CMM are *list fields*, and
those are opt-in through `cmm_set_list_field_format`, which sets prefix and
postfix keys per field. Advanced Auto Build ships five
`<mod>__<setting>_format` keys that nothing reads; they are harmless, but a
`_format` key is not the way to put a unit after a slider's number.

`_format` *is* real for a list filter, where `search_filter_<key>_format` goes
with a `range`. The two conventions are unrelated and easy to conflate.

### CMF's shared keys are overridable, for everyone

`CMM_NUMERIC_INCREASE_MAX` and `CMM_NUMERIC_DECREASE_MIN` are CMF's own keys and
are used by every mod's numeric settings. A mod can redefine them — Advanced
Auto Build does, to change the hint on its own sliders, wrapping the whole thing
in `SelectLocalization` on `Scope.GetFlagName` so other mods' settings fall back
to the original wording. It works, and whichever mod loads later wins the key,
so a translation of one mod has to reproduce the fallback in that language or
quietly change what every other mod's settings say.

### Localization goes in `main_menu/`

All three reference mods put every `.yml` under
`main_menu/localization/<lang>/`, including the text that only ever appears
in game — CMM settings, tooltips, filter chips. Both mods in this repository do
the same and work. Advanced Auto Build ships a byte-identical second copy under
`in_game/localization/`; nothing here needs it, and no reference mod does that.

### Other CMF facilities

- `cmf_add_action_bar_element` / `cmf_remove_action_bar_element` put a button on
  the shared action bar instead of every mod drawing its own.
- `cmf_log`, `cmf_log_with_args` write to the shared mod action log.
- `cmf_suppress` silences benign "variable never read" engine warnings.
- `in_game/gui/vanilla/*_vanilla_types.gui` holds copies of vanilla widget types
  so several mods can restyle the same window without overwriting each other's
  copy of the vanilla file.

## Translating a mod that ships without your language

A separate mod carrying one `.yml` is the whole job. It needs no dependency on
the mod it translates — the keys simply add, and nothing collides — and only a
CMF dependency if it redefines one of CMF's own shared keys. `auto_build_ru` is
the worked example; its `tools/generate_ru.py` is written against one mod but
the shape of it is reusable.

**A mod may ship a language that is only the English text.** National Destinies
ships eleven languages whose files are byte identical to the English ones apart
from the `l_<language>:` header, so it reads in English in a Russian game while
`localization/russian/` plainly exists. Diff against `english/` before believing
a language is present.

That changes the job from adding keys to **overriding** them, which is confirmed
working in game: a separate localization mod loaded after the base mod replaces
the base mod's values for the same keys. Load order decides, so the translation
declares a dependency on the mod it translates and has to sit below it in the
playset.

**Read the size before quoting one.** A mod's key count badly overstates the
work. Of Advanced Auto Build's 1201 keys, 372 were pure markup, 316 were
`$vanilla_key$` passthrough, and another 315 were families differing only by a
number — 883 strings of actual prose, and about 6000 words. Count what is left
after stripping `[...]`, `$...$`, `@icon!` and `#code`, not lines.

**Audit before translating.** Four checks, each cheap and each has caught
something:

1. Parse every language the mod ships and compare key sets. Equal sets mean the
   English is a complete translation and can be the source; a gap means the
   other language is the original and has to be consulted for those keys.
2. Collect every key its `.gui` files and scripts reference — `text`, `tooltip`,
   `raw_tooltip`, `custom_tooltip`, and `$...$` inside other values — and check
   each is defined. A dangling one renders raw in *every* language, and is the
   mod's bug rather than yours.
3. Derive the CMM keys from its registration effects (see
   [Mod Menu settings](#mod-menu-settings-cmm)) and check those too. This is
   where a real mod is likeliest to be missing one.
4. Look for keys that are not the mod's own. A mod may redefine a vanilla or CMF
   key, and translating it changes what every other mod says.

**Ask the game what it calls its own concepts.** A mod's prose names game
concepts in plain text — advances, levies, bureaucracy — and inventing a word for
them produces exactly the disease the translation is meant to cure: a private
term sitting in the middle of the game's own interface. The game's localization
answers it: match the English value against `localization/english`, read the
Russian value of the same key. In EU5 1.3.10 advances are «Улучшения», not
«достижения», which is what a session guessed before the game's files were in the
repository. `mods/nd_ru/tools/term.py` is that lookup.

Inside `[advances|e]` and other concept links the game substitutes the name
itself, so the word only has to be chosen where the mod writes it as prose.

**What must not be translated.** Each of these looks like text and is not:

| Looks like | Is | If translated |
| --- | --- | --- |
| `gold` under `<element>_color` | a CMF palette name | the action bar button vanishes |
| `@production_panel!` | a texticon | renders as literal text |
| `$farming_village$` | a reference to the game's own key | breaks; it was already in the player's language |
| `[GetPlayer.MakeScope...]` | a data function | `ERROR:` on screen |
| `#G ... #!` | a colour code | the colour is lost, or the text is |

Passthrough is the happy case: a mod that names its buildings
`$vanilla_key$` needs none of them translated.

**A mod of a hundred thousand words is a different job.** `auto_build_ru` was
6000 words and fitted in one sitting. National Destinies is 688 617 words of
prose across 220 files, which no subscription pays for in full. What that
changes:

- **Measure before promising.** Count prose words after stripping markup, not
  keys and not lines. Then convert to sessions: one session of steady work moved
  about 25 000 words, tooling and mistakes included. That number is the only
  honest basis for "how long will this take".
- **The order of work is a deliverable.** A file like `priority.txt` naming the
  stems in the order they matter — for a player, the region they actually play —
  lets any later session pick up without re-deciding anything.
- **Translate in layers, not files.** Names first (short, low judgement, most
  visible), then the events a player reads, then descriptions. A layer finished
  across the whole mod is worth more than a few files finished completely.
- **Look for the cheap thousands.** `nd_bureaucracy_impact_modifier_types` holds
  1770 keys built from three sentences; `nd_event_guards` holds 144 keys built
  from one. Both were generated from templates in minutes and fixed their line
  for every country at once. Before translating by hand, group the file's values
  by shape and see how many distinct sentences there really are.

**A key of a country need not live in that country's file.** Westphalia had 88
keys in `nd_wes` and 10 more in a shared modifier file. Checking one file and
declaring the country done is how a gap survives. Search every file for the tag.

**`_entry` keys are usually passthrough.** `nd_wes.1.entry: "$nd_wes.1.t$"` is a
reference to the event title, so translating the title makes the log entry
Russian by itself. Translating the entry as well is wasted work.

**Overriding another mod's localization works, and stacks with a third.** A
separate mod loaded later replaces the base mod's values for the same keys —
confirmed in game. That also means a hand translation can sit on top of somebody
else's machine translation of the same mod: theirs below, yours above, and the
player gets your keys where you have them and theirs everywhere else. Two
conditions: the overriding mod must load later, and **its file names must differ**,
because a file of the same name replaces the whole file rather than merging keys.
Naming the generated output `<stem>_ru_generated_l_russian.yml` keeps it clear of
both the base mod and any other translation.

**Generate rather than hand-write the final file.** Keep the prose in a source
file and emit the game's `.yml` from it, with the source checked against the
base mod's English: every key covered, no key invented, and the markup of each
value identical in both. That last check is the one that earns its keep — it
catches a bracket eaten while rewording, which is otherwise found by the player.
It also turns a base-mod update into one run that names the keys that moved.

**Families collapse.** Keys differing only by a number — twenty template slots,
step buttons, per-ordinal rows — are worth writing once with a placeholder and
expanding over the numbers the base mod actually uses. Collapse only when the
*values* match too: `eu5ab_building_age_1..6` share a key shape and are six
different ages.

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

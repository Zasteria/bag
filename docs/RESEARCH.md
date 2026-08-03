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
| `ProductionEfficiencyInfo(country, location)` | `BuildingType` | String pair list used for the tooltip breakdown |

`location_window.gui` drives the badge with them — the icon is visible on
`And(BuildingType.IsProducing, BuildingType.HasPossibleRGOBonus(...))`, and it
is tinted green through `IsUsingRGOBonus` or yellow otherwise, with tooltip
strings `RGO_BONUS`, `PROD_METHOD_BONUS_ACTIVE` and `PROD_METHOD_BONUS_POTENTIAL`.

This is the exact predicate a "local raw materials only" filter needs.

## List filters

`in_game/gui/filters/*.txt` defines filters declaratively:

```
glorpui_character_has_architectural_visionary = {
	scope = character
	group = 0
	exclusive_group = no
	tag = ruler
	trigger = { has_trait = architectural_visionary }
}
```

A list opts into a filter set by tag on its data context, e.g.
`ProductionView.GetBuildingsSortSearch.WithFilterTags('building')` in
`production_lateralview.gui` and
`BuildInLocationLateralView.GetItemsSortSearch.WithFilterTags('building')` in
the build-in-location view. Filters whose `tag` matches show up as removable
chips above the list — the vanilla "hide estate-only buildings" chip is one.

The catch: `trigger` is *script*, not GUI, so it can only use script triggers.
Whether a script-side equivalent of `HasPossibleRGOBonus` exists still has to be
checked against the vanilla files.

## Sorting

Sorting is already data driven. `sort_by_key_button` entries name a sort key,
and `production_efficiency` is one of the keys vanilla exposes on building
lists, with `gfx/interface/icons/sort/efficiency.dds` as its icon. Ascending /
descending toggling is built into the button. So the sorting half of a
"most efficient buildings here" workflow needs no new code — only the filter.

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

### Other CMF facilities

- `cmf_add_action_bar_element` / `cmf_remove_action_bar_element` put a button on
  the shared action bar instead of every mod drawing its own.
- `cmf_log`, `cmf_log_with_args` write to the shared mod action log.
- `cmf_suppress` silences benign "variable never read" engine warnings.
- `in_game/gui/vanilla/*_vanilla_types.gui` holds copies of vanilla widget types
  so several mods can restyle the same window without overwriting each other's
  copy of the vanilla file.

# Handoff

Where the two mods stand, and what a fresh session needs to carry on. Read this
first, then [`RESEARCH.md`](RESEARCH.md) for how EU5 modding actually works —
most of that was learnt the hard way and will save a repeat.

## State

**`rgo_bonus_filter/` — working, in use.** Two filter chips, one per building
list. Nothing outstanding.

**`where_to_produce/` — lists confirmed working; the table around them is new
and untested.** Screenshots at 1.3.10 showed both lists populating, the tick
driving the shortlist, and `Рудные горы / 10%` for silver jewellery — right to
the digit. What followed that is not yet in game: real method names, the recipe
on the row, multi-select, the volume columns and the sort order.

## What was wrong with the lists

Worth keeping because none of the three announced itself.

1. **No `<setting>_on_changed` scripted GUI, so neither list was drawn at all.**
   Registering a CMM list marks the setting as having a scripted GUI
   (`_cmm_mark_setting_has_sgui`, inside `_cmm_register_list_setting_internal`),
   and `CMMSettingRowVisible` then draws the row only when
   `CMMGuiIsShown('<mod>__<setting>_on_changed')`. With no such file the whole
   widget was hidden — its header included. What still rendered was the *group*
   header, which a list gets for free because `_cmm_register_setting_metadata`
   files it under `group_id = <setting_id>`, and that is why it looked like two
   empty lists rather than two missing ones.

   It is also the only route a click on a list takes into script. Lists have no
   CMM auto-apply — bool, dropdown, numeric, slider and button settings each
   have one in `cmm_core_auto_apply_scripted_gui.txt`, lists do not — so
   `cmf_on_callback` never fires for a list, and ticking a recipe reached
   nothing. The callback path itself was fine all along.

2. **CMM's dynamic list builder runs exactly once.**
   `cmm_begin_settings_list`, every `cmm_add_settings_list_item` and
   `cmm_finish_settings_list` are gated on `cmm_list_initialized_<setting>` —
   which `cmm_register_*_settings_list` sets itself. So registering the list and
   then filling it dynamically could never work: the second pass added nothing
   and reported nothing. Construction Manager is the working example, and it
   registers statically and writes rows in place; so do we now.

3. **`item = var:wtp_row_cursor` is not a thing.** The macro pastes it verbatim,
   which `game.log` reported at load as
   `More than one colon in event target link 'flag:wtp__provinces_ivar:wtp_row_cursor_f1'`.
   Row ordinals have to be literals. A counter becomes one through a `switch`;
   where the ordinal is only needed per existing row,
   `cmm_for_each_list_item` hands it over as `$i$` already resolved.

## Settled by the screenshots

- `[GetGlobalVariable('wtp_prov_row_1').GetProvince.GetName]` renders a province
  name. `GetProvince` on a variable exists, even though no vanilla `.gui` uses it.
- `ordered_in_global_list` with `order_by` sorts descending, and `max` takes the
  top of that.
- `cmm_set_list_data_value` with a literal ordinal reaches the column, and a
  `data` field renders whole percentages cleanly.
- A production method's key is its localization key: `silver_base` is
  "Ювелирные изделия из серебра", and 0.69 silver → 1 jewelry matches the
  building panel exactly.

## Untested, in order of doubt

1. `[GetGlobalVariable('wtp_meth_row_1').GetFlagName]` in a province row label.
   CMF localizes list rows through `GetFlagName` on a *country* variable, and
   this is the global equivalent — but a global one has not been seen doing it.
   If the shortlist rows come up as bare province names, that is where to look.
2. The per-province scoring loop: `save_scope_as` on the province, then
   `every_in_global_list` over the ticked recipes with `scope:… = { }` stepping
   back into it. Every piece is a normal construct, but the shape is new here.
   Watch `wtp_best_score` actually varying between provinces — if every row
   scores the same, the scope step is not landing.
3. Cost. The pass is provinces × ticked recipes, and the recipes arrive all
   ticked. Twenty recipes over a few hundred provinces on every tick, every
   good change and every sort change; if the menu stutters, the first move is to
   score only on the shortlist rebuild rather than on every callback.
4. Whether a `data` field renders two decimals for the volume columns. If it
   rounds to whole numbers the volumes are useless — most sit between 0.1 and
   4 — and they would have to be scaled by 100 and read as percent of one unit.

`error.log` names the file and line for GUI failures. A script effect that
merely does nothing logs nothing at all, which is what made all three of the
original bugs invisible — check `game.log` too, that is where the load-time
macro expansion error turned up.

## Files a new session must be given

None of this is in the repository, and nothing can be verified without it:

| What | Why |
| --- | --- |
| `<EU5>/game/in_game/gui/` | filters, panels, widget types |
| `<EU5>/game/in_game/common/` — `building_types`, `production_methods`, `goods` | everything the generators read |
| `<EU5>/game/in_game/common/` — `scripted_effects`, `scripted_triggers`, `on_action` | the only reference for what script can do |
| Community Mod Framework (workshop 3692202776) | the CMM API being used |
| Construction Manager (workshop 3736668860) | the only working example of CMM lists |
| Glorp UI (workshop 3601047146) | interface patterns; also what the filter mod must not collide with |
| `Documents/Paradox Interactive/Europa Universalis V/logs/` | how every bug so far was actually found |

Regenerate after any patch, and point the generator at CMF so it checks macro
argument names:

```
python3 rgo_bonus_filter/tools/generate_rgo_filter.py "<EU5>/game/in_game/common"
python3 where_to_produce/tools/generate.py "<EU5>/game/in_game/common" "<CMF>/in_game/common/scripted_effects"
```

## Decisions already made, worth not relitigating

- **Provinces, not locations.** The bonus is province wide; ten locations of one
  province would score identically.
- **Volume is what compares two recipes.** The bonus is production efficiency,
  so it multiplies output: a jeweller's guild at 10% turns out 1.10, a village
  carver at the same 10% turns out 0.11. Ranking on the percentage alone put
  them level, which is what "I want to see the volume too" was about.
- **Each province keeps one recipe, not a maximum per column.** Scoring picks
  the best ticked recipe by whatever is being ranked on and reports *that*
  recipe's figures. Taking the best percentage and the best volume independently
  would have been two different recipes on one row.
- **A recipe that gains nothing here is passed over.** Its volume is the plain
  output, which every other province matches, so it says nothing about the place.
- **A recipe is carried as the flag naming its own localization key**
  (`flag:wtp_recipe_<method>`). One value labels the row, tells the scoring which
  recipe it is, and keys both columns, so there is nothing to keep in step.
- **Row labels and tooltips are generated without words.** They are `$key$`
  references to the game's own method and goods names plus three captions written
  per language by hand, so one generated file serves every localization.
- **A good belongs to the most specific industry that makes it.** Masonry comes
  from a quarry and a mason's yard; the game files it under basic industry.
- **Only recipes that output something count.** A monastery burns clay for
  upkeep and produces nothing, so it has no efficiency to gain — which is why
  the game gates its own shovel badge on `IsProducing`.
- **The interface lives in the Mod Menu.** A custom window was built and thrown
  away: view objects only resolve inside their own panel, and CMM gives the
  framework's look for free.

## Loose ends, none blocking

- The recipe list is twenty rows because liquor has twenty recipes. The
  generator warns if a patch pushes a good past that, and also if the row
  writers or the `item_count` fall out of step; raising it means changing
  `RECIPE_ROWS`, the `item_count` in `wtp_registration.txt` and the run of
  `wtp_recipe_row_<n>` in `wtp_effects.txt`.
- `wtp_open_*` in localization is left over from the action bar button the Mod
  Menu replaced. Kept because the keys are what a shortcut back to the tab would
  need, and because the `_color` rule below is easy to lose.
- The generator now deletes the four generated files and the goods catalogue the
  old good-first ranking needed — about 3,500 lines the game no longer parses.
  Anything wanting "which good is this province best at" would have to
  regenerate that chain, not resurrect it.

## Hard-won facts that are easy to lose

- The RGO bonus formula, verified to the digit against three tooltips, is in
  [`../where_to_produce/README.md`](../where_to_produce/README.md). Every input
  counts in the divisor, produced goods included.
- A `building_type` filter receives `root` and nothing else — not `scope:target`,
  whatever vanilla's comment says. Reading it logs an error every pass.
- A CMF action bar element is drawn from localization: `_icon` takes a texticon
  like `@good!`, and `_color` must name one of CMF's palette entries or the
  button is invisible in the bottom bars.
- Square brackets in a localization value are data function syntax, so a plain
  `[debug]` in a label renders as `ERROR:`. The same syntax is what lets a row
  label read a global variable back.
- A CMM macro called with an argument name CMF does not declare fails silently
  and takes the rest of its effect with it. One `step` instead of `step_value`
  cost a full round. `generate.py` checks for this across both
  `scripted_effects/` and `scripted_guis/` when given CMF's path.

# Handoff

Where the two mods stand, and what a fresh session needs to carry on. Read this
first, then [`RESEARCH.md`](RESEARCH.md) for how EU5 modding actually works —
most of that was learnt the hard way and will save a repeat.

## State

**`rgo_bonus_filter/` — working, in use.** Two filter chips, one per building
list. Nothing outstanding.

**`where_to_produce/` — working end to end; the last round of tidying is
untested.** Screenshots at 1.3.10 showed both lists populating, multi-select
driving the shortlist, the volume columns and the sort order all correct —
`Рудные горы / Оружейные заводы / 1.88% / 4.075` reads exactly right. What the
same screenshots showed was that it was unreadable: every row a different font
size, lists that would not shrink or clear, and a wall of recipes the country
can never build. That is what the last round addressed, and none of it has been
in game yet.

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

## What made it unreadable, and what fixed it

- **A row is one line of text the engine shrinks to fit.** Writing the recipe
  into the label left every row at its own font size — that, not the wording, is
  what made the table look broken. The label is now the method's name and nothing
  else; the recipe moved to the tooltip.
- **A hidden row still takes its place.** `cmm_hide_list_item` sets a flag the
  row widget reads, but the vbox around it has no `ignoreinvisible`, so the panel
  kept its old height with the bottom half blank. Both lists are now *resized*:
  clear `cmm_list_items_<setting>`, remove `cmm_list_initialized_<setting>`,
  re-register at the height needed. `_cmm_reconcile_list_setting_item_growth`
  only ever adds rows, which is why removing the initialized flag is the only way
  down.
- **A list cannot be registered empty** — `item_count` clamps to one. What hides
  a list with nothing in it is `is_shown` on its `_on_changed` scripted GUI,
  which `CMMSettingRowVisible` already gates the whole widget on.
- **Nothing cleared the good.** `wtp_apply_pickers` only ever *set* it, so
  putting all four pickers back to "nothing chosen" left the last one standing.
  The pickers now behave as one choice: whichever moved wins and the other three
  are written back to 1 in CMM's `cmm` map, the same shape
  `cmm_auto_apply_dropdown` writes.

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

1. Re-registering a list at a new height. Clearing `cmm_list_items_<setting>` and
   removing `cmm_list_initialized_<setting>` sends registration back through its
   first-time branch, which is how it is meant to work — but CMF has no caller
   that does this, so nothing has exercised it. If the panel comes back with the
   wrong number of rows, or rows that render as raw keys, that is where to look.
2. `is_shown` on the two `_on_changed` scripted GUIs actually hiding an empty
   list. The group header is drawn from the tab structure and will still show,
   so the tidy empty state is a titled box with nothing in it.
3. Writing `cmm` map entries for the three pickers the player did not touch.
   Registration only seeds a dropdown when the key is absent, so it should
   survive a reload, but the menu has never been seen resetting its own dropdown.
4. Cost. The scoring pass is provinces × ticked recipes and the recipes arrive
   all ticked, plus a new pass over every owned location to work out which raw
   materials the realm has. If the menu stutters, the realm scan is the cheap
   thing to cache and the scoring is the expensive thing to move off the
   callback path.

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

## The one thing the game files here cannot answer

Production methods locked behind an advance. `ProductionMethod.IsAvailable`
exists as a GUI data function, so the game plainly knows, but nothing in
`building_types/` or `production_methods/` says which advance unlocks which
method — so a pre-Columbian or obsidian variant of a guild still shows for a
European player. It sits near the bottom, where its output puts it, but it is
noise.

Fixing it needs whatever holds the `has_advance` unlocks — `common/advances/`
and the technology folder beside it. With those, the same trick that copies
`country_potential` verbatim would copy the unlock condition too.

## Loose ends, none blocking

- The row writers stop at twenty because liquor has twenty recipes. The
  generator warns if a patch pushes a good past that, and checks that every
  branch of both switches in `wtp_effects.txt` is present; raising it means
  changing `RECIPE_ROWS` and extending `wtp_resize_recipe_list` and
  `wtp_place_recipe_row`.
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

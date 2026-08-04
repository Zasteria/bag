# Handoff

Where the two mods stand, and what a fresh session needs to carry on. Read this
first, then [`RESEARCH.md`](RESEARCH.md) for how EU5 modding actually works —
most of that was learnt the hard way and will save a repeat.

## State

**`rgo_bonus_filter/` — working, in use.** Two filter chips, one per building
list. Nothing outstanding.

**`where_to_produce/` — rewritten, not yet tested in game.** The data layer was
already solid and verified. The two lists were empty for three separate reasons,
all now fixed; the fixes below are reasoned from CMF's own source and the load
log, but no one has clicked through the menu yet.

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

## Untested, in order of doubt

1. `[GetGlobalVariable('wtp_prov_row_1').GetProvince.GetName]` as a province row
   label. Variables clearly expose one `Get<ScopeType>` accessor per scope type —
   `GetCountry`, `GetLocation`, `GetCharacter`, `GetReligion` and `GetRebel` all
   appear in vanilla `.gui` — but no vanilla file happens to use `GetProvince` on
   one. If the labels come up blank, that is where to look; the rows and the
   percentage column do not depend on it.
2. `ordered_in_global_list` sorting descending. Vanilla's
   `ordered_pop = { max = 1 order_by = pop_size }` picks the *biggest* pop, so
   descending is the default, but the shortlist has never actually been seen.
3. Whether a data field renders a sensible number of decimals. Both percentage
   columns now carry a `%` postfix through `cmm_set_list_field_format`.

`error.log` names the file and line for GUI failures. A script effect that
merely does nothing logs nothing at all, which is what made all three of the
bugs above invisible — check `game.log` too, that is where the load-time macro
expansion error turned up.

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
- **Recipe first, then provinces.** Ranking provinces by "the best recipe
  available there" made the ceiling column compare a different recipe on every
  row, which read as nonsense. The player picks the recipe; its output is then
  constant, leaving the bonus as the only thing to rank on.
- **A recipe is carried as the flag naming its own localization key**
  (`flag:wtp_recipe_<method>`). One value labels the row, tells the ranking which
  recipe was ticked, and keys the ceiling, so there is nothing to keep in step.
- **A good belongs to the most specific industry that makes it.** Masonry comes
  from a quarry and a mason's yard; the game files it under basic industry.
- **Only recipes that output something count.** A monastery burns clay for
  upkeep and produces nothing, so it has no efficiency to gain — which is why
  the game gates its own shovel badge on `IsProducing`.
- **The interface lives in the Mod Menu.** A custom window was built and thrown
  away: view objects only resolve inside their own panel, and CMM gives the
  framework's look for free.

## Loose ends, none blocking

- `wtp_generated_dispatch.txt`, `wtp_generated_goods_values.txt`,
  `wtp_generated_availability.txt` and every `wtp_output_*` are dead: they answer
  "the best recipe for this good *here*", which the recipe-first design stopped
  asking. Around 3,500 lines the game parses every load. Kept because they are
  the basis of any "which good is this province best at" view, but nothing reads
  them today.
- `wtp_build_goods_catalogue` is likewise unreferenced — it fed the goods grid
  of the custom window that was thrown away.
- The recipe list is twenty rows because liquor has twenty recipes. The
  generator warns if a patch pushes a good past that; raising it means changing
  `RECIPE_ROWS`, the `item_count` in `wtp_registration.txt` and the `switch` in
  `wtp_place_recipe_row`.

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

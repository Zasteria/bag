# Where To Produce

An EU5 mod for the question the game makes you answer one location at a time:
**this province is mine — what is actually worth building in it?**

Walk down region, area, province, and the last list ranks every building this
mod can say something about by what that province's own raw materials are worth
to it: the percentage of the recipe they cover, and the volume that turns into.

Requires the Community Mod Framework (`community_mod_framework` 2.\*).

The interface is a tab in CMF's Mod Menu: **Where To Produce → Plan**.

It answers the same question as the community "Production Efficiency /
Urbanization / Province Breakdown" spreadsheet, against the patch you are
actually playing rather than the one the sheet was built from — and only for
land you hold, so the list is short enough to read.

## Using it

**Mod Menu → Where To Produce → Plan.**

- **Region** — the regions you hold land in. Tick one.
- **Area** — the areas of that region you hold land in.
- **Province** — the provinces of that area.
- **Worth building here** — the answer. One row per building, ranked, under the
  game's own name for it. Hover a row for the recipe behind the figure: what it
  consumes, what it turns out, and which of its inputs the province supplies.
  Two columns, **Local %** and **Output**.
- **Display** — town buildings, rural ones or both; rank by percentage or by
  output; how many rows; and two filters, one for what this country can never
  build and one for what it has not reached yet.

Each list only appears once the one above it has a pick, so the tab starts as a
single list of your regions.

## The formula

The game shows a raw material bonus in the production efficiency tooltip —
"Coal in the Ore Mountains, +2.86%" — but exposes it only as tooltip text.
Recovered by matching those readings:

```
RGO bonus % = 10 * (input amounts available locally) / (all input amounts)
```

Verified exactly against three readings at 1.3.10:

| Building / method | Available | Computed | Tooltip |
| --- | --- | --- | --- |
| `saltpeter_guild` / `saltpeter_guild_demands` | livestock | 8.33% | +8.33% |
| `weapon_guild` / `weapon_smith_maintenance` | coal | 2.86% | +2.86% |
| `mason` / `clay_bricks` | clay | 10.00% | +10.00% |

**Every input counts towards the denominator**, including produced goods like
tools that an RGO can never supply. That is the part worth knowing: a method can
have a ceiling far below the full 10%.

```
weapon_smith_maintenance   lumber 0.2521 + coal 0.3034 + tools 0.5050 = 1.0605
                           lumber and coal are the only ones an RGO can give
                           0.5555 / 1.0605  ->  ceiling 5.24%
```

The community spreadsheet reaches 12.5% on single-input buildings; it was built
from patch 1.0.6. The three readings above are from 1.3.10, where the ceiling is
10%. Where the two disagree, this mod matches the game you are playing.

## Percentage or volume

The bonus is production *efficiency*, so it multiplies output:

```
volume = output x (1 + bonus% / 100)
```

That is the number that makes two buildings comparable. A jeweller's guild
working silver turns out 1.0 and reaches 10%, so 1.10. A village carver working
stone also reaches 10%, but from an output of 0.1, so 0.11. Ranked on the
percentage the two are level; ranked on output the guild is ten times the
carver. Both columns are on the answer and either can drive the order.

A building is worth what its *best* method is worth in that province, so the
runtime walks a building's methods and keeps the best — which is what the
spreadsheet does too. The tooltip shows the recipe of whichever method won, so
the figure and the recipe beside it always belong together.

## How it is put together

One province is scored at a time, which is what makes this cheap: a couple of
hundred script value reads for the whole answer, rather than one pass per
province in the realm.

```
wtp_scan_realm_materials   one walk over owned locations -> wtp_realm_has_<good>
wtp_fill_regions           owned locations -> region, deduped
wtp_fill_areas             ... limited to the picked region -> area
wtp_fill_provinces         ... limited to the picked area -> province
wtp_fill_top               every candidate building against the picked province
```

`wtp_fill_top` scores each building into three country variable maps keyed by the
building's flag — bonus, volume, and the tooltip of the method that won — and
then a twelve-pass selection sort writes the best into the rows. A selection sort
rather than `ordered_in_global_list`, because the ranking lives in a variable map
and an ordered iterator wants a script value it can evaluate on the iterated
scope.

## What gets hidden

Two filters, both on by default, because "never" and "not yet" are different
questions.

**Only what I have now** asks the engine directly:

```
can_build_building = building_type:<b>
NOT = { building_type_is_obsolete = building_type:<b> }
```

Both are country scoped triggers, so they move with your advances and ages
without this mod knowing anything about either — which is what keeps a fourth
tier mill out of the list of a country that has never left the fourth age. It
also drops what a successor has already replaced. The answer is refreshed on
CMF's yearly pulse as well as on every click, so it does not go stale while the
menu is shut.

**Only what I can build** drops three kinds of row:

- the building carries a `country_potential` this country fails — a Japanese
  clan reform, an English tag, a flat `always = no`. The generator copies each
  one verbatim into a scripted trigger, so the rule is the game's own;
- the building is `is_special` or `is_foreign`, so it is not something the
  player builds in the ordinary way;
- nowhere in the realm works any raw material it could take a bonus from, which
  is the only thing this mod has to say about it.

What neither can drop is one *method* of an unlocked building being locked
behind an advance. `ProductionMethod.IsAvailable` exists as a GUI data function,
but there is no script-side counterpart and nothing in `building_types` or
`production_methods` records the unlock, so a pre-Columbian variant of a guild
you do have still counts — sitting near the bottom, where its output puts it.
The building level is what the ages actually gate, so this is a much smaller
error than it was.

## How the lists work

Worth knowing before touching them, because none of it fails loudly.

**A CMM list setting is invisible until the mod supplies
`<mod>__<setting>_on_changed`.** Registering a list marks it as having a
scripted GUI, and `CMMSettingRowVisible` then draws the row only when that
scripted GUI reports `is_shown`. With no such file the whole widget is hidden —
header, rows and all — and nothing reaches any log. It is also the only route a
click on a list takes into script: unlike bool, dropdown, numeric and slider
settings, lists have no CMM auto-apply, so `cmf_on_callback` never fires for one.

That gate is also how a list disappears when it has nothing in it: `item_count`
is clamped to at least one, so a list can never be registered empty.

**CMM's dynamic list builder runs exactly once.** `cmm_begin_settings_list`, the
run of `cmm_add_settings_list_item` and `cmm_finish_settings_list` are each gated
on `cmm_list_initialized_<setting>`, which registration itself sets. A second
pass adds nothing and reports nothing.

**A hidden row still takes its place.** CMM draws rows from
`cmm_list_items_<setting>` and gates each on `CMMListItemIsVisible`, but the vbox
holding them has no `ignoreinvisible`, so hiding the surplus leaves the panel at
its old height with the bottom half blank. Every list is therefore *resized*: the
item list is cleared, `cmm_list_initialized_<setting>` removed, and the setting
re-registered at the height it needs — the same door the first registration goes
through. `_cmm_reconcile_list_setting_item_growth`, which handles a
re-registration, only ever adds rows.

**A row ordinal has to be a literal.** `item = var:wtp_row_cursor` is pasted into
the macro verbatim and comes back as

```
More than one colon in event target link 'flag:wtp__provinces_ivar:wtp_row_cursor_f1'
```

at load. Every ordinal therefore comes out of a `switch` on a counter, and
`wtp_generated_rows.txt` holds those — four lists, each needing one switch to
register itself at the right height and one to write a given row.

**A row label needs a localization key to point at.** A building type has one —
its own key — so the flag standing for the candidate labels the answer rows
directly. A region, an area and a province have none, so each picker row parks
its own in a global and a fixed key per ordinal reads it back:

```
[GetGlobalVariable('wtp_prov_row_1').GetProvince.GetName]
[GetGlobalVariable('wtp_area_row_1').GetArea.GetNameWithNoTooltip]
```

**Nothing generated is a word in any language.** Tooltips are built out of
`$key$` references to the game's own method and goods names plus three captions
defined per language by hand, so one generated file serves every localization the
mod ships.

## Notes for anyone extending this

Nothing of our own is drawn. A custom window was built and thrown away: view
objects only resolve inside their own panel, and the Mod Menu gives the
framework's look for free.

Two things that are known to be possible and are not done yet:

- **A button in the location panel** that jumps straight to the province you are
  looking at, instead of walking the three pickers. `scripted_widgets` maps a gui
  path to a widget and the engine instantiates it, which is how CMF adds four of
  its own.
- **Building from the row.** `construct_building = { building_type = X owner = Y
  payer = Z }` in a location scope queues a real construction — Construction
  Manager uses exactly that. The open question is not the effect but *which*
  location of the province to build in, which is the same problem the
  spreadsheet's "Ideal City Locations" column answers.

## Layout

```
.metadata/metadata.json                        mod descriptor
in_game/common/scripted_triggers/              generated: province materials, and
                                               whether a building is worth offering
in_game/common/script_values/                  generated: what a method scores here
in_game/common/scripted_effects/               the pickers, the scoring, the row writers
in_game/common/scripted_guis/                  the four list callbacks, without which
                                               no list is drawn at all
in_game/common/on_action/                      CMF registration and callback hooks
main_menu/localization/                        the captions, in English and Russian;
                                               everything generated is $key$ references
tools/eu5data.py                               reads the game files and holds the formula
tools/generate.py                              writes the script layer
```

Regenerate after a patch that touches goods, production methods or building
types:

```
python3 where_to_produce/tools/generate.py "<EU5>/game/in_game/common" \
    "<CMF>/in_game/common/scripted_effects"
```

The second argument is optional but worth passing: it checks every `cmm_` call
in the mod against the argument names CMF declares. A macro called with a name
CMF does not declare fails silently and takes the rest of its effect with it —
one `step` instead of `step_value` cost a full round. The same pass checks that
every row writer the generated switches call actually exists, and the generator
deletes what it no longer emits, so a file that disappears after a run was left
over from an earlier design rather than lost.

The bonus is linear in a method's inputs, so it lands in script as a sum of
`if` clauses over the province's raw materials, with the volume hanging off it:

```
wtp_bonus_weapon_smith_maintenance = {
    value = 0
    if = { limit = { wtp_province_has_coal = yes }   add = 0.3034 }
    if = { limit = { wtp_province_has_lumber = yes } add = 0.2521 }
    divide = 1.0605
    multiply = 10
}
wtp_volume_weapon_smith_maintenance = {
    value = wtp_bonus_weapon_smith_maintenance
    divide = 100
    add = 1
    multiply = 1
}
```

At 1.3.10: 40 raw materials referenced, 215 methods scored across 110 buildings
— 63 staffed by burghers, 47 by everyone else — and 8 buildings behind a
`country_potential`.

`tools/eu5data.py` is the source of truth for the numbers. Point it at
`<EU5>/game/in_game/common`; it resolves every production method per building
type, both inline `unique_production_methods` and the shared ones named through
`possible_production_methods`, and skips upkeep-only methods that output nothing
— the game gates its own shovel badge on `IsProducing` for the same reason.

Goods inputs are recognised by matching the goods catalogue, not by "any
numeric key". Methods carry bookkeeping numbers too, and `debug_max_profit = -1`
on the plantations is numeric enough to have made four recipes' input weight
come out negative before this was keyed on real goods.

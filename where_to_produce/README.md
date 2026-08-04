# Where To Produce

An EU5 mod for the question the game makes you answer one location at a time:
**I want more glass — where in my realm should it come from?**

Pick a good, tick one of the recipes that make it, and get a shortlist of the
provinces where that recipe would gain most from the raw materials on hand.
Provinces with no local bonus at all never appear.

Requires the Community Mod Framework (`community_mod_framework` 2.\*).

The interface is a tab in CMF's Mod Menu: **Where To Produce → Plan**.

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

So 2.86% out of a possible 5.24% is more than half of everything that method
will ever get, while 6% somewhere else might be nowhere near its own ceiling.
The shortlist reports the ceiling alongside the actual figure for exactly this
reason.

## How the shortlist is built

Recipe first, then provinces. Ranking provinces by "the best recipe available
there" made the ceiling column compare a different recipe on every row, which
read as nonsense. The player picks the recipe; its output is then the same
everywhere, leaving the bonus as the only thing left to rank on.

Provinces, not locations: the bonus is province wide, so ten locations of one
province would score identically and crowd everything else out.

`wtp_rebuild_shortlist` walks `every_owned_location`, steps up to its province,
and collects each one where the ticked recipe would gain anything.
`ordered_in_global_list` then takes the best few by `wtp_selected_bonus`, and
each survivor is written into one row of the shortlist.

A recipe travels as the flag naming its own localization key —
`flag:wtp_recipe_weapon_smith_maintenance`. That one value labels the row, tells
`wtp_selected_bonus` which recipe was ticked, and keys the ceiling column, so
there is nothing to keep in step between the three.

## Using it

**Mod Menu → Where To Produce → Plan.**

- **Good** — four pickers, one per category, the way the game already groups
  goods. Any one of them off "none" names the good.
- **Recipes** — every way to make it, best output first, with the most that
  recipe could ever gain from local raw materials beside it. Tick one; the
  column behaves as a radio button.
- **Best provinces** — where that recipe gains most, best first, with the bonus
  it actually gets there.
- **Display** — how many provinces to list, up to ten.

The ceiling is the column worth reading: 2.86% against a ceiling of 5.24% is
more than half of everything that recipe will ever give, while 6% on a different
recipe might be nowhere near its own limit.

## How the two lists work

Worth knowing before touching them, because none of it fails loudly.

**A CMM list setting is invisible until the mod supplies
`<mod>__<setting>_on_changed`.** Registering a list marks it as having a
scripted GUI, and `CMMSettingRowVisible` then draws the row only when that
scripted GUI reports `is_shown`. With no such file the whole widget is hidden —
header, rows and all — and nothing reaches any log. It is also the only route a
click on a list takes into script: unlike bool, dropdown, numeric and slider
settings, lists have no CMM auto-apply, so `cmf_on_callback` never fires for one.

**CMM's dynamic list builder runs exactly once.** `cmm_begin_settings_list`, the
run of `cmm_add_settings_list_item` and `cmm_finish_settings_list` are each gated
on `cmm_list_initialized_<setting>`, which registration itself sets. A second
pass adds nothing and reports nothing. Both lists are therefore registered once
at their full height — twenty recipe rows, ten province rows — and the rows are
written in place with `cmm_set_list_item_value` and `cmm_set_list_data_value`,
with `cmm_hide_list_item` for the ones a shorter good leaves over.

**A row ordinal has to be a literal.** `item = var:wtp_row_cursor` is pasted into
the macro verbatim and comes back as

```
More than one colon in event target link 'flag:wtp__provinces_ivar:wtp_row_cursor_f1'
```

at load. So a counter turns into a literal through a `switch`, the way CMF does
it everywhere. Where the ordinal is only needed per existing row,
`cmm_for_each_list_item` hands it over as `$i$` already resolved.

**A province has no localization key of its own.** Each shortlist row parks its
province in `wtp_prov_row_<n>` and the row label — a fixed key per ordinal —
reads it back with `[GetGlobalVariable('wtp_prov_row_1').GetProvince.GetName]`.

## Notes for anyone extending this

Nothing of our own is drawn. A custom window was built and thrown away: view
objects only resolve inside their own panel, and the Mod Menu gives the
framework's look for free.

Should the action bar ever be wanted again, an element registered through
`cmf_add_action_bar_element` is drawn entirely from localization keyed on the
element name — the `wtp_open_*` keys are still in place for it:

| Key | Holds |
| --- | --- |
| `<element>_icon` | text drawn in the button, so a texticon such as `@good!` |
| `<element>_color` | one of CMF's palette names — `blue`, `bone`, `gold`, … |
| `<element>_name` | tooltip title |
| `<element>_tooltip` | tooltip body |

`_color` is not cosmetic. CMF draws one button variant per colour and gates each
on the key matching, so an element without it is invisible in the bottom bars.
The top variant is a tab and skips that gate, which is why a missing `_color`
looks like "only works in one position".

Skins like `bg_paper_card` go on the widget as `using = bg_paper_card`. Wrapping
them in a `background = { }` block does nothing, and the panel draws its text
straight onto the map.

## Layout

```
.metadata/metadata.json                        mod descriptor
in_game/common/scripted_triggers/              generated: is this raw material in the province
in_game/common/script_values/                  generated: what a method scores here
in_game/common/scripted_effects/               registration, the row writers, the ranking pass
in_game/common/scripted_guis/                  the two list callbacks, without which
                                               neither list is drawn at all
in_game/common/on_action/                      CMF registration and callback hooks
main_menu/localization/                        English and Russian
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
one `step` instead of `step_value` cost a full round. The same pass warns if a
good has grown more recipes than the list has rows.

The bonus is linear in a method's inputs, so it lands in script as a sum of
`if` clauses over the province's raw materials:

```
wtp_bonus_weapon_smith_maintenance = {
    value = 0
    if = { limit = { wtp_province_has_coal = yes }   add = 0.3034 }
    if = { limit = { wtp_province_has_lumber = yes } add = 0.2521 }
    divide = 1.0605
    multiply = 10
}
wtp_ceiling_weapon_smith_maintenance = 5.2381
wtp_output_weapon_smith_maintenance = 1
```

At 1.3.10: 40 raw materials referenced, 215 methods scored, 47 goods reachable.
The generated script is replayed against the model over every combination of a
method's raw inputs — 824 checks, no mismatches.

`tools/eu5data.py` is the source of truth for the numbers. Point it at
`<EU5>/game/in_game/common`; it resolves every production method per building
type, both inline `unique_production_methods` and the shared ones named through
`possible_production_methods`, and skips upkeep-only methods that output nothing
— the game gates its own shovel badge on `IsProducing` for the same reason.

At 1.3.10 that comes to 52 raw material goods, 228 producing methods and 47
goods that can be made with some local bonus.

Goods inputs are recognised by matching the goods catalogue, not by "any
numeric key". Methods carry bookkeeping numbers too, and `debug_max_profit = -1`
on the plantations is numeric enough to have made four recipes' input weight
come out negative before this was keyed on real goods.

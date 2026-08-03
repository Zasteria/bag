# Where To Produce

An EU5 mod for the question the game makes you answer one location at a time:
**I want more glass — where in my realm should it come from?**

Pick a good, get a shortlist of locations where a building producing it would
actually gain from the raw materials on hand, ranked by output and by how much
of the recipe those materials cover. Locations with no local bonus at all never
appear.

Requires the Community Mod Framework (`community_mod_framework` 2.\*).

> Complete but unverified. Every piece is written — data, ranking, window,
> settings — and checked for syntax and cross-references, but the game has not
> loaded it once. Expect the first run to need fixes.

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

Provinces, not locations: the bonus is province wide, so ten locations of one
province would score identically and crowd everything else out.

`wtp_rebuild_shortlist` walks `every_owned_location`, steps up to its province,
and collects each one that could produce the chosen good at all. Then
`ordered_in_global_list` takes the best ten twice over — once ordered by what
the recipe yields, once by how much of it the local raw materials cover — and
the window shows the first N of whichever column is being sorted on.

The good the player picked sits in the `wtp_good` global as a goods scope.
`order_by` accepts a single script value, so the generated `wtp_current_output`
and `wtp_current_bonus` fan out from that one name to the chain for that good.

## Ranking

Two columns, sort by either:

- **Output** — what the method actually yields. A glass mill at 4.0 dwarfs a
  rural glassmaker at 0.2 whatever their percentages.
- **Local coverage** — the bonus above, against that method's ceiling.

The two disagree often, which is the point: iron gives a tools guild output 1.0,
stone tools only 0.25, and both can sit at the same 10%.

## Using it

The Community Mod Framework puts a **Where To Produce** button on its action
bar. The window lists every good something in the game could produce with a
local bonus; pick one and the shortlist fills in.

Four columns: the province, what the best available recipe there yields, the
bonus it actually gets, and the most that recipe could ever get. The last one
matters — 2.86% against a ceiling of 5.24% is more than half of everything that
recipe will ever give, while 6% elsewhere might be nowhere near its own limit.

Under **Shortlist → Display** in the Mod Menu: how many provinces to show, and
whether to rank by output or by local coverage.

## Layout

```
.metadata/metadata.json                        mod descriptor
in_game/common/scripted_triggers/              generated: is this raw material in the province
in_game/common/script_values/                  generated: what a method scores here
in_game/common/scripted_effects/               registration, the ranking pass
in_game/common/scripted_guis/                  what the window calls into
in_game/common/on_action/                      CMF registration and callback hooks
in_game/gui/wtp_window.gui                     the window, injected as a scripted widget
main_menu/localization/                        English and Russian
tools/eu5data.py                               reads the game files and holds the formula
tools/generate.py                              writes the script layer
```

Regenerate after a patch that touches goods, production methods or building
types:

```
python3 where_to_produce/tools/generate.py "<EU5>/game/in_game/common"
```

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

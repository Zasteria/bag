# Where To Produce

An EU5 mod for the question the game makes you answer one location at a time:
**I want more glass — where in my realm should it come from?**

Pick a good, get a shortlist of locations where a building producing it would
actually gain from the raw materials on hand, ranked by output and by how much
of the recipe those materials cover. Locations with no local bonus at all never
appear.

Requires the Community Mod Framework (`community_mod_framework` 2.\*).

> Early work in progress. The data layer is done and verified against the game;
> the window is not built yet.

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

## Ranking

Two columns, sort by either:

- **Output** — what the method actually yields. A glass mill at 4.0 dwarfs a
  rural glassmaker at 0.2 whatever their percentages.
- **Local coverage** — the bonus above, against that method's ceiling.

The two disagree often, which is the point: iron gives a tools guild output 1.0,
stone tools only 0.25, and both can sit at the same 10%.

## Layout

```
.metadata/metadata.json      mod descriptor
in_game/common/              script values, triggers, effects, scripted GUIs
in_game/gui/                 the window
main_menu/localization/      English and Russian
tools/eu5data.py             reads the game files: goods, methods, the formula
docs/                        notes
```

`tools/eu5data.py` is the source of truth for the numbers. Point it at
`<EU5>/game/in_game/common`; it resolves every production method per building
type, both inline `unique_production_methods` and the shared ones named through
`possible_production_methods`, and skips upkeep-only methods that output nothing
— the game gates its own shovel badge on `IsProducing` for the same reason.

At 1.3.10 that comes to 52 raw material goods, 228 producing methods and 47
goods that can be made with some local bonus.

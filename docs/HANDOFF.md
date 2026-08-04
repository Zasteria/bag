# Handoff

Where the two mods stand, and what a fresh session needs to carry on. Read this
first, then [`RESEARCH.md`](RESEARCH.md) for how EU5 modding actually works —
most of that was learnt the hard way and will save a repeat.

## State

**`rgo_bonus_filter/` — working, in use.** Two filter chips, one per building
list. Nothing outstanding.

**`where_to_produce/` — half working.** The data layer is solid and verified.
The Mod Menu tab renders: four goods pickers with real names, the numeric
setting, and both list headers. **The two lists never get any rows.**

## The open problem

Pick a good and the recipe list stays empty. `error.log` carries nothing from
the mod at all — no failures, so the rebuild is not *running* rather than
erroring.

Everything that fills a list hangs off `cmf_on_callback` →
`wtp_handle_callback`. The last change removed the `var:cmf_callback = flag:…`
matching from that path, on the theory that a comparison which never matches
looks exactly like this. **That change has not been tested in game yet** — try
it before assuming anything.

If the lists are still empty, the question moves one step earlier: does
`cmf_on_callback` reach the mod at all? Settle it rather than guessing —
`cmf_log = { … }` at the top of `wtp_handle_callback` writes to CMF's own log
panel, so one click on a picker either shows a line or it does not.

If the callback never fires for a dropdown, the fallback is CMM's auto-apply
(`cmm_core_auto_apply_scripted_gui.txt` in CMF), which is what makes a setting
change dispatch at all. Construction Manager registers its settings and gets
callbacks, so compare against `cm_cmm_effects.txt` and
`cm_cmm_custom_effects.txt` — that mod is the best reference for this API.

Untested beyond that, in order of doubt:

1. `cmm_build_list_bool_list` reading which recipe is ticked.
2. `cmm_set_list_data_value` with `item = var:wtp_row_cursor` — Construction
   Manager passes literal numbers, and a variable may not be accepted.
3. `cmm_add_global_settings_list_item` with `value = prev` inside
   `ordered_in_global_list`.

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
- **A good belongs to the most specific industry that makes it.** Masonry comes
  from a quarry and a mason's yard; the game files it under basic industry.
- **Only recipes that output something count.** A monastery burns clay for
  upkeep and produces nothing, so it has no efficiency to gain — which is why
  the game gates its own shovel badge on `IsProducing`.
- **The interface lives in the Mod Menu.** A custom window was built and thrown
  away: view objects only resolve inside their own panel, and CMM gives the
  framework's look for free.

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
  `[debug]` in a label renders as `ERROR:`.
- A CMM macro called with an argument name CMF does not declare fails silently
  and takes the rest of its effect with it. One `step` instead of `step_value`
  cost a full round.

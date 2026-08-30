# `where_to_produce` — brief

A planning tool in the Mod Menu, plus a window and a map mode of its own. Choose
the ground — regions, then provinces and locations inside them — pick a building
and the production method you mean to run it on, and get those locations ranked
by the RGO efficiency that method would gain.

**State: one load behind us, and it found a silent fault.** The first build put a
tab on screen with only the dropdown on it: `cmm_register_settings_list` declares
`is_ordered` and the call omitted it, so every list registration died where it
stood and took the rest of its effect with it. Fixed, and
`tools/check_cmm.py` now fails on a missing argument as well as an
unknown one — it only ever checked the second direction. **Nothing since that
load is confirmed.**

## What the next run has to answer

The Mod Menu tab prints the counters the pass leaves behind; the button
descriptions carry them.

1. **Do the six region groups appear at all**, with named rows? That is what the
   `is_ordered` fix was for.
2. **"Выбрать локации"** — does the window open, and does it list the provinces
   of the ticked regions?
3. **Does the map mode exist?** Geography map modes, "Где производить". Bright is
   chosen, dim is what you are choosing from.
4. **Does the result table read back** a location name and two numbers out of
   global variables? Still the one mechanism nothing here has proved.
5. **`error.log`** — seven region keys are unproven, and the window's widget
   types are copied from Advanced Auto Build rather than verified.

## What is known to be unproven

- **Seven of the seventy-seven region keys** are named by the game's
  localization but scoped into by nothing in `reference/`: `central_africa_region`,
  `central_india_region`, `macaronesia_region`, `micronesia_region`, `poland`,
  `polynesia_region`, `southern_africa_islands_region`. The generator prints them
  on every rebuild.
- **The whole window and the map mode.** Both are modelled on Advanced Auto
  Build, which is the only working example of either shape in the tree. The map
  mode's `index = 3` is copied from it and the two would collide if that mod were
  ever enabled alongside.
- **`can_build_building = global_var:bag_wtp_building`** — a global variable as a
  trigger target, reachable only with the "только там, где уже можно строить"
  tick on.

## Three things that are settled

- **The window's cost is its datamodel, not its file.** 79 widgets per province
  row, and a scripted widget never comes down — so `bag_wtp_browse` is filled
  when the window opens and emptied when it closes. Leaving it full of a ticked
  Europe is how this mod would become the thing
  [`../../docs/investigations/panel_hitch.md`](../../docs/investigations/panel_hitch.md)
  is about. The map's own tint reads `bag_wtp_in_zone` on the location instead,
  so it survives the window closing.
- **The selection is recorded twice and only `bag_wtp_pick` / `bag_wtp_drop` may
  write it** — a variable on the location for the map and the interface, a global
  list for the ranking walk. Anything writing one half desynchronises them.
- **The bonus is province-level.** Every location of one province scores the
  same; what separates them is building slots, which this version does not model.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, run from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

# `where_to_produce` — brief

A planning tool in the Mod Menu, plus a window and a map mode of its own. Choose
the ground — regions, then provinces and locations inside them — pick a building
and the production method you mean to run it on, and get those locations ranked
by the RGO efficiency that method would gain.

**State: two loads behind us, and between them the data half is proved.** The
result table read back location names and numbers out of global variables on
screen — "Бельцы — 9.25% (2/2)" — which was the one mechanism nothing here had
ever done. The region lists render with the game's own names. What those loads
broke, and what replaced it, is in `docs/TESTLOG.md`.

**Two CMM caps, and neither is written near the call that cares.** A list is
good to 50 rows; **a dropdown is clickable only to its twentieth option**,
because CMF handles an option click through `CMM_MarkDropdownSelection_<index>`
and defines twenty of them. A 218-option dropdown renders and scrolls and
silently refuses the 21st onwards. That is why the picker is two lists.

**Untested: the map picker and everything around it.**

## What the next run has to answer

1. **The map picker.** Three buttons in the selection window hand the game one of
   this mod's generic actions; the game answers with its own target panel —
   search, list, map highlight, map click. Does the panel open, does clicking add
   ground, and **does it stay open for a second click**? That last one is the
   only thing the files in `reference/` cannot say, and every clicking toggle is
   written so that the answer does not change the design either way.
2. **The picker funnel.** Tick a good; the second list should refill with the
   ways that good is made and hide the rest. Tick a recipe; a second tick
   anywhere in either list should move rather than add.
3. **The window's rows.** They collapsed to zero height last time because the
   item was wrapped in a `widget`, which does not size to its child.
4. **The map mode.** Geography map modes, "Где производить".

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

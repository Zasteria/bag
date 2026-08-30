# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method **available to you now** and ranks the locations by what that method would
earn from the raw materials the province supplies.

**State: four loads behind us, and the fourth was the first where the owner said
everything worked.** The goods tick moves, the scoring picks the method, the map
picker chooses ground, the map mode paints. What is in this build on top of that
run has not been loaded yet.

## What the fifth run has to answer

Everything below came out of the fourth run's feedback and none of it is tested.

1. **Tabs.** Goods, ground and the answer are three tabs now, not five groups on
   one scroll. A tab is just a `tab_id`, but the tab key and a setting key are
   both `<mod>__<id>_name`, so the zone setting had to be renamed `continent` to
   stop the tab and the list colliding on one key.
2. **Regions are back, beside the continents.** Five region lists on the ground
   tab; a ticked region wins over its continent. Ticking Europe painted the whole
   screen and the good case was one region.
3. **Availability.** Only methods whose building this country has unlocked are
   scored — `can_build_building` in country scope, plus `has_advance` for the ten
   methods the game gates directly. A tick turns it off for planning ages ahead.
   Goods nothing available can make are hidden from the pickers.
4. **One row per province.** Every location of a province scores identically, so
   fifty rows were fifty ways of saying one thing and the table ran out before
   the distinct answers did.

## Two CMM caps, neither written near the call that cares

- **A list is good to 50 rows** (`CMM_MarkListPosition_*` and the item chain are
  both unrolled to fifty).
- **A dropdown is clickable only to its twentieth option**
  (`CMM_MarkDropdownSelection_0` … `_19`). Every picker here is a list.

## Settled, and not to be re-litigated

- **The map picker closes after each pick.** That is the generic action's
  lifecycle; `fire_generic_action` executes with a supplied target rather than
  reopening the panel. Area granularity is the answer.
- **The window lists the provinces something is picked in** — its job is trimming
  a plan drawn on the map, and that also bounds a datamodel whose row is ~104
  widgets behind a scripted widget that never comes down.
- **The selection is recorded twice** — a variable on the location for the map
  and the interface, a global list for the ranking — and only `bag_wtp_pick` /
  `bag_wtp_drop` may write it.
- **No marked zone.** A location's continent and region are plain triggers, so
  nothing is written onto a continent's locations in advance.
- **The bonus is province-level**, which is why the table is per province.

## Still wanted, not built

- Icons in a result row for the winning building and the goods its method eats.
  A CMM row is one localization key, so per-row icons need one global per slot
  per row — about 250 variables. The good's icon is in the pickers already.
- A tighter reason than "the table holds fifty".

**Built by** `python3 mods/where_to_produce/tools/generate.py`, from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

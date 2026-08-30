# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method **available to you now** and ranks the locations by what that method would
earn from the raw materials the province supplies.

**State: eight loads in, and the answer half is finished** — icons, whole
provinces, no lakes, the window inside its frame, `error.log` clean of this mod
for the first time. «В остальном — круто.»

## What the ninth run has to answer

The selection window is a **tree** now: Регионы → Области → Провинции → Локации,
four columns, a name opening the next one, «Всё» on any row taking or dropping
that whole geography, and hovering any row highlighting it on the map.

1. **The columns fill** as rows are opened, and the first one holds what the zone
   tab ticked (or a whole continent's regions, or the world).
2. **«Всё» toggles**, and the mod's map mode shows the result.
3. **The hover highlight** is the game's own — `PdxGuiWidget.SetHighlight*`.
4. **`gui.log` no longer names `bag_wtp_select_window.gui`**: a button anchored
   inside an hbox logged 124 lines last run.
5. Still never reported: the region lists, the age filter.

**Clicking the map with a window open is not possible** and is not to be
attempted again — see `docs/research/interface.md`. The game's own panels are
view objects, and no on_action carries a map click. The generic action's picker,
which closes after each pick, is the whole of what script has.

## Three CMM caps, none written near the call that cares

A list is good to **50 rows**, a dropdown clickable to its **twentieth option**
(so every picker here is a list), and a button and a list **may not share a
setting id** — same `<mod>__<id>_name` collision as a tab and a setting, which is
why the window's button is `show`. The window itself has no cap; the ranking pass
bounds it.

## Settled, and not to be re-litigated

- **The map picker closes after each pick** — the generic action's lifecycle,
  not a fault, and the only map-click channel a mod has at all.
- **A window's datamodel is what costs.** A scripted widget never comes down, so
  only the list it repeats over decides how many rows are alive. Both windows
  fill their lists on opening and empty them on closing.
- **The selection is recorded twice** — a variable on the location for the map
  and the interface, a global list for the ranking — and only `bag_wtp_pick` /
  `bag_wtp_drop` may write it.
- **No marked zone.** A location's continent and region are plain triggers, so
  nothing is written onto a continent's locations in advance.
- **The bonus is province-level**, which is why a row is a province rather than
  a location. What would separate two locations of one province is building
  slots, and the game exposes no slot count to script or to the interface.
- **And the province is the `province_definition`**, not the `province`: the
  latter is one owner's piece of it. A planning tool answers for the ground as it
  will be, not for the border as it stands.
- **The owner's flag under an expanded row stays.** «Нахер не нужно, но и не
  мешает» — asked and answered, seventh run.

## The answer lives on the location

`bag_wtp_fill_rows` parks it there and everything else reads it back:

| on the winning location | is |
| --- | --- |
| `bag_wtp_best` | the bonus, in percent |
| `bag_wtp_bt` | the building that won |
| `bag_wtp_pm` | the method that won |
| `bag_wtp_goods` | the raw materials the province supplies to it |
| `bag_wtp_goods_all` | how many it could supply, which is why the two differ |

The window reads those off its own row scope. The fifty CMM rows copy them into
globals of their own (`bag_wtp_row_N`, `_bt_N`, `_pm_N`, `_bonus_N`), because a
localization key has no scope to read from.

## Still wanted, not built

Fifty provinces is the CMM table's ceiling, not the window's; dropping the table
lifts it. No sorting or filtering inside the window either.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

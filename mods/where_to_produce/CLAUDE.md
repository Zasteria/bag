# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method **available to you now** and ranks the locations by what that method would
earn from the raw materials the province supplies.

**State: five loads in.** The fifth put the three tabs, the goods filter and the
per-province table on screen and they work. What it showed is that the *row* was
the limit: one line of text can name a location and a building and nothing else,
and the owner needed the province, the method, and what the number is made of.

## What the sixth run has to answer

The answer now has a window of its own, `bag_wtp_result_window.gui`, and the
CMM table stands beside it as a fifty-row summary. None of this has been loaded.

1. **The window opens** — «Считать» opens it, «Открыть» reopens it, and the
   close button empties it.
2. **A row is a province**: name, area, the bonus, the building **and which of
   its methods won**, then an icon per raw material the province supplies to that
   method. That last one is «из чего» — the numerator of the bonus, item by item.
3. **A row expands** into the province's locations, each with what it works now
   and the same «Добавить» / «Убрать» buttons the selection window has.
4. **The table under the button** now names the province and the method too, and
   its rows have a tooltip.
5. **`error.log`** — the window is 380 lines of new GUI, and GUI failures do name
   their file and line.

Still open from the fifth build: the region lists, the age filter, `error.log`.

## Two CMM caps, neither written near the call that cares

- **A list is good to 50 rows** (`CMM_MarkListPosition_*` and the item chain are
  both unrolled to fifty). The window has no such cap; it is bounded by the
  ranking pass instead.
- **A dropdown is clickable only to its twentieth option**
  (`CMM_MarkDropdownSelection_0` … `_19`). Every picker here is a list.
- **A button and a list may not share a setting id** — same `<mod>__<id>_name`
  collision as a tab and a setting. The window's button is `show`, not `result`.

## Settled, and not to be re-litigated

- **The map picker closes after each pick.** That is the generic action's
  lifecycle; `fire_generic_action` executes with a supplied target rather than
  reopening the panel. Area granularity is the answer.
- **A window's datamodel is what costs.** A scripted widget never comes down, so
  only the list it repeats over decides how many rows are alive. The selection
  window lists just the provinces something is picked in; the results window
  keeps `bag_wtp_ranked` and fills `bag_wtp_results` from it on opening, emptying
  it again on closing.
- **The selection is recorded twice** — a variable on the location for the map
  and the interface, a global list for the ranking — and only `bag_wtp_pick` /
  `bag_wtp_drop` may write it.
- **No marked zone.** A location's continent and region are plain triggers, so
  nothing is written onto a continent's locations in advance.
- **The bonus is province-level**, which is why a row is a province. What would
  separate two locations of one province is building slots, and the game exposes
  no slot count to script or to the interface — `--find slot` has nothing.

## The answer lives on the location

`bag_wtp_fill_rows` parks it there and everything else reads it back:

| on the winning location | is |
| --- | --- |
| `bag_wtp_best` | the bonus, in percent |
| `bag_wtp_bt` | the building that won |
| `bag_wtp_pm` | the method that won |
| `bag_wtp_goods` | the raw materials the province supplies to it |

The window reads those off its own row scope. The fifty CMM rows copy them into
globals of their own (`bag_wtp_row_N`, `_bt_N`, `_pm_N`, `_bonus_N`), because a
localization key has no scope to read from.

## Still wanted, not built

- The window is capped at fifty provinces only because the CMM table beside it
  is. Dropping the table lifts it.
- Sorting or filtering inside the window; it shows the ranking and nothing else.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method **available to you now** and ranks the locations by what that method would
earn from the raw materials the province supplies.

**State: six loads in, and the results window works** — rows, the method after
the colon, expansion into locations, «в целом вроде ок». Two things came out of
that run and are not tested: a province is not what the game calls a province,
and the window drew outside its own frame.

## What the seventh run has to answer

1. **One row per province definition.** The game splits a province by ownership
   and names the halves «Молдавская провинция Бессарабия»; ranking those answers
   for half the ground and moves the answer on the day they join. Rows are
   definitions now, scored over every location in them, and a location's owner
   shows under the row.
2. **«Из чего» prints «supplied/total» and that many icons.** The column looked
   empty in the sixth screenshot and the count is there to say whether the list
   is empty or the icons will not draw.
3. **Both windows stay inside their frames** after the description was bounded
   and `widgetanchor = center` added.
4. **One hover settles the open question:** in a province currently split by a
   border, does the game's own RGO tooltip credit a good only the other half
   produces? That says whether this mod's number is today's or after-conquest.
5. Still open from the fifth build: the region lists, the age filter,
   `error.log`.

## Three CMM caps, none written near the call that cares

A list is good to **50 rows**, a dropdown clickable to its **twentieth option**
(so every picker here is a list), and a button and a list **may not share a
setting id** — same `<mod>__<id>_name` collision as a tab and a setting, which is
why the window's button is `show`. The window itself has no cap; the ranking pass
bounds it.

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
- **The bonus is province-level**, which is why a row is a province rather than
  a location. What would separate two locations of one province is building
  slots, and the game exposes no slot count to script or to the interface.
- **And the province is the `province_definition`**, not the `province`: the
  latter is one owner's piece of it. A planning tool answers for the ground as it
  will be, not for the border as it stands.

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

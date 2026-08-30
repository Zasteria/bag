# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method **available to you now** and ranks the locations by what that method would
earn from the raw materials the province supplies.

**State: eleven loads in, and the eleventh found the window ignoring the
borders.** Picking areas inside the ticked region moved the count and nothing
else, and the rows arrived in map order rather than in rank order. Both are
fixed and neither is confirmed: **the twelfth run is what says so.**

## What the twelfth run has to answer

Both of the eleventh's failures were the silent kind, and both are fixed blind
— write-ups in `docs/TESTLOG.md` and `docs/PITFALLS.md`:

- **a generic action's `effect` is not in the country's scope**, so the pickers'
  `bag_wtp_recompute_live` did nothing while the scope-agnostic count beside it
  went on moving. Wrapped in `scope:actor` — **the one guess in this build**, and
  `error.log` names it if it is wrong for an `owncountry` action.
- **`every_in_global_list` undid the ranking** on the way into the window's
  datamodel. That copy is `ordered_in_global_list` on `bag_wtp_rank_order` now.

Two things in the window exist to be read rather than used. The **«№» column**:
out of order down the window = the copy; in order with the bonus jumping about =
`order_by` in `bag_wtp_fill_rows`. And **«обошёл · нашёл · пересчётов»** in the
header: the third not moving on a pick = the scope again, moving while the rows
do not = the datamodel.

Never judged, twice deferred: the two-line rows, villages not at the top of a
weapons search, the goods icons beside their count, and the age filter.

**Two things are settled and not to be attempted again.** Clicking the map with
a window open is impossible — the game's panels are view objects and no
on_action carries a map click (`docs/research/interface.md`). And a geography
tree of our own came up empty twice and is deleted: the game's target panel is
how ground gets chosen here.

Only the goods and ground lists are still CMM's; the caps that shape them are in
`docs/research/cmf.md`.

## Settled, and not to be re-litigated

- **The map picker closes after each pick** — the generic action's lifecycle,
  not a fault, and the only map-click channel a mod has at all.
- **A window's datamodel is what costs.** A scripted widget never comes down, so
  only the list it repeats over decides how many rows are alive; `bag_wtp_results`
  is filled on opening and emptied on closing.
- **The selection is recorded twice** — a variable on the location, a global list
  for the ranking — and only `bag_wtp_pick` / `bag_wtp_drop` may write it.
- **The bonus is province-level**, which is why a row is a province: what would
  separate two of its locations is building slots, and the game exposes none.
- **And the province is the `province_definition`** — the `province` is one
  owner's piece of it, and this answers for the ground, not for today's border.
- **The owner's flag under an expanded row stays** — seventh run.

## The answer lives on the location

`bag_wtp_fill_rows` parks it there and everything else reads it back:

| on the winning location | is |
| --- | --- |
| `bag_wtp_best` | the effective output, `out * (1 + bonus/100)`, which is what the ranking sorts on |
| `bag_wtp_rank` | the place it came in, 1 first — what the «№» column prints and what the copy into the window sorts on |
| `bag_wtp_bt` | the building that won |
| `bag_wtp_pm` | the method that won |
| `bag_wtp_out` | what it produces a level, which is what `_best` is made of |
| `bag_wtp_bonus` | the RGO bonus, which is what the row prints |
| `bag_wtp_goods` / `_all` | the raw materials the province supplies, and how many it could |

Each of those has a `_rural` twin: villages are scored on their own side, and a
row shows both answers.

Each row reads those off its own scope: no globals per row, and no fifty-row
ceiling but `RESULT_ROWS` in the generator. Not built: sorting or filtering
inside the window, and any measure of a building's cost or its slot.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

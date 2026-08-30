# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method **available to you now** and ranks the locations by what that method would
earn from the raw materials the province supplies.

**State: ten loads in, and the mod is one window.** The tenth run found the
result rows collapsed into each other and the selection tree still empty; the
tree and its whole window are deleted, and the map-picker buttons moved into the
results window, where **every pick re-ranks** while it is open.

## What the eleventh run has to answer

1. **The rows read** — one province, two lines where a built-up building and a
   village were both found. They overlapped because a `widget` does not size
   itself to its child; every height is a number now.
2. **The three «Выбрать…» buttons** sit in the results window with the running
   count and «Очистить выбор».
3. **The answer follows the borders**: after a pick, no «Считать» needed.
4. **Villages are not at the top** of a weapons search — ranking is by effective
   output, `output * (1 + bonus/100)` — and the goods icons sit beside their
   count.
5. Never yet reported: the age filter.

**Two things are settled and not to be attempted again.** Clicking the map with
a window open is impossible (`docs/research/interface.md`: the game's own
panels are view objects, no on_action carries a map click). And a geography tree
of our own was tried twice, came up empty both times, and was deleted — the
game's target panel, which closes after each pick, is how ground is chosen here.

## CMM caps, none written near the call that cares

A list is good to **50 rows** and a dropdown clickable to its **twentieth
option**, so every picker here is a list. A button and a list **may not share a
setting id** — same `<mod>__<id>_name` collision as a tab and a setting. The
answer is out of CMM entirely now; only the pickers and the three buttons are
left on the tab.

## Settled, and not to be re-litigated

- **The map picker closes after each pick** — the generic action's lifecycle,
  not a fault, and the only map-click channel a mod has at all.
- **A window's datamodel is what costs.** A scripted widget never comes down, so
  only the list it repeats over decides how many rows are alive. The window
  fills `bag_wtp_results` on opening and empties it on closing.
- **The selection is recorded twice** — a variable on the location, a global list
  for the ranking — and only `bag_wtp_pick` / `bag_wtp_drop` may write it.
- **The bonus is province-level**, which is why a row is a province rather than a
  location: what would separate two of its locations is building slots, and the
  game exposes no slot count at all.
- **And the province is the `province_definition`**, not the `province`: the
  latter is one owner's piece of it. A planning tool answers for the ground as it
  will be, not for the border as it stands.
- **The owner's flag under an expanded row stays** — asked and answered, seventh
  run.

## The answer lives on the location

`bag_wtp_fill_rows` parks it there and everything else reads it back:

| on the winning location | is |
| --- | --- |
| `bag_wtp_best` | the bonus, in percent |
| `bag_wtp_bt` | the building that won |
| `bag_wtp_pm` | the method that won |
| `bag_wtp_out` | what it produces a level, which is what `_best` is made of |
| `bag_wtp_bonus` | the RGO bonus, which is what the row prints |
| `bag_wtp_goods` | the raw materials the province supplies to it |
| `bag_wtp_goods_all` | how many it could supply, which is why the two differ |

Each of those has a `_rural` twin: villages are scored on their own side, and a
row shows both answers.

The window reads those off its own row scope, which is why there are no globals
per row any more and no fifty-row ceiling.

## Still wanted, not built

Fifty provinces is now only `RESULT_ROWS` in the generator. No sorting or
filtering inside the window, and no measure of a building's cost or its slot --
`×` output is the whole of what "better method" means here.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

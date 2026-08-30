# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method **available to you now** and ranks the locations by what that method would
earn from the raw materials the province supplies.

**State: nine loads in.** The answer half is confirmed; the ninth run found the
tree empty, the icons still spread, and the ranking answering the wrong question.
All three are rebuilt and untested.

## What the tenth run has to answer

1. **The tree fills.** Its four columns were written out; a `block` nested inside
   a `blockoverride` never reached the instance, which is why headers drew and
   rows did not.
2. **A result row is two lines** — the best built-up building and the best
   village, each with its own bonus, method, `×` output and goods.
3. **Villages no longer top a weapons search.** Ranking is by effective output,
   `output * (1 + bonus/100)`, not by the bonus alone.
4. **The Mod Menu table is gone**; the window is the only place the answer is.
5. **The goods icons sit beside their count** — text icons now, not `icon`
   widgets, which take a share of an hbox rather than their glyph.

**Clicking the map with a window open is not possible** and is not to be
attempted again — see `docs/research/interface.md`. The game's own panels are
view objects, and no on_action carries a map click.

**The region lists are how the owner frames every search** (Карпаты, then the map
picker for the provinces beside it). Confirmed in use, ninth run.

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
  only the list it repeats over decides how many rows are alive. Both windows
  fill their lists on opening and empty them on closing.
- **The selection is recorded twice** — a variable on the location, a global list
  for the ranking — and only `bag_wtp_pick` / `bag_wtp_drop` may write it.
- **No marked zone.** A location's continent and region are plain triggers.
- **The bonus is province-level**, which is why a row is a province rather than a
  location: what would separate two of its locations is building slots, and the
  game exposes no slot count at all.
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

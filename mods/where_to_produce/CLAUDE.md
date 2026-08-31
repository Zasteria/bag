# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province supplies — **in two ages: what you can build now, and
what the ground gives once every advance is in.**

**State: eighteen loads in, and the second column is confirmed on screen.** A
good or a whole urban right, a window each; the ranking sorts, a pick re-ranks
live, the pickers stay folded, «Открыть» reopens the last result, and every row
carries both ages — `bag_wtp__rank_by_end` picks which the ranking obeys, with
the near column breaking its ties.

## Where it stands

**A method the province feeds nothing of is not an answer** — since the
eighteenth run, where fine cloth came back as silk at 0.00% in a wool country.
Where nothing is fed there is no row.

**Eight buildings run two methods at once and the mod models one** — fine
cloth, jewelry, cannons and firearms carry a second
`unique_production_methods` block, and the building runs one from each. It
understates their output and their inputs. The fix fits the existing shape and
waits on one tooltip:
[`../../docs/investigations/production_ladder.md`](../../docs/investigations/production_ladder.md).

**Never reported**, both from the seventeenth run: no province at 0.00% on every
good of a bundle, and «Уникальные права» empty for all but Byzantines and
Scandinavians. **And the rights window has one age** to the goods window's two.

**Urban rights** are two lists on the Goods tab and a window of their own: a
bundle of two or three goods is a different question in a different unit. The
numbers and the deferred level rights:
[`../../docs/investigations/town_rights.md`](../../docs/investigations/town_rights.md).
One button, not two: «Считать» answers whichever is ticked, and both cannot be.

**`cmf_on_mod_registration` fires every time the mod page is opened**, so
`bag_wtp_register` destroys nothing.

**Not to be attempted again:** clicking the map with a window open
(`docs/research/interface.md`), and a geography tree of our own — empty twice,
deleted. The pickers' CMM caps: `docs/research/cmf.md`.

## Settled, and not to be re-litigated

- **A window's datamodel is what costs.** A scripted widget never comes down, so
  only the list it repeats over decides how many rows live; a window's list is
  filled on opening and emptied on closing.
- **The selection is recorded twice** — a variable on the location, a global
  list for the ranking — and only `bag_wtp_pick` / `_drop` may write it.
- **The bonus is province-level** — which is why a row is a province, and the
  `province_definition` at that: the whole ground, not one owner's piece. What
  would separate two of its locations is building slots, which the game hides.
- **The buildable tick is about the location, not the owner** — the row for it
  is in `docs/SETTLED.md`.
- **The owner's flag under an expanded row stays** — seventh run.

## The answer lives on the location

`bag_wtp_fill_rows` parks it there; everything else reads it back:

| on the winning location | is |
| --- | --- |
| `bag_wtp_best` | `out * (1 + bonus/100) * RANK_SCALE` — what the ranking sorts on, never printed |
| `bag_wtp_rank` | the place it came in, 1 first — the «№» column, and what the copy sorts on |
| `bag_wtp_bt` / `_pm` | the building and the method that won |
| `bag_wtp_out` | what it makes a level, unscaled — the row's `×` |
| `bag_wtp_bonus` | the RGO bonus, the row's percentage |
| `bag_wtp_goods` / `_all` | the raw materials the province supplies, and how many it could |

Each has a `bag_wtp_end_*` twin: the same six for the last age.

For an urban right the same six are `bag_wtp_r_*_<k>` for slot `k` of the
bundle, `bag_wtp_r_good_<k>` naming the good and `bag_wtp_r_total` the sum the
ranking sorts on. Three slots: script has no list of tuples.

All have a `_rural` twin too, and a row reads them off its own scope: no globals
per row, no ceiling but `RESULT_ROWS`. Not built: sorting inside a window, and
what a building costs to put up.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

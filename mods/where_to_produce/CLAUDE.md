# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method **available to you now** and ranks the locations by what that method would
earn from the raw materials the province supplies.

**State: fourteen loads in and doing its job for a single good.** The ranking
sorts, a pick re-ranks while the window is open, and the two-line row reads —
the village under the guild rather than above it.

## Where it stands

Unjudged: the tail of «0.00% … 0/2» provinces being out of the table; the
**pickers folding shut** on first sight of the mod page and staying where the
player leaves them after (`bag_wtp_fold_pickers` writes CMM's own
`cmm_group_collapsed` map, which no macro covers — a contract with a comment in
`cmm_settings_pane.gui`); and the **age filter**, never once reported.

**Urban rights are built and have never been loaded.** A third list on the Goods
tab, exclusive with the two goods lists, and a **second window** — a bundle of
two or three goods is a different question in a different unit, so it is not a
third line on the first window. A right's own percentage re-ranks nothing (it is
the same everywhere); what ranks is the bundle, added through the goods' market
prices. Level rights — Flemish cloth, the marketplace charters — are deliberately
out. All of it, with the numbers:
[`../../docs/investigations/town_rights.md`](../../docs/investigations/town_rights.md).

**Two things are settled and not to be attempted again.** Clicking the map with
a window open is impossible (`docs/research/interface.md`), and a geography tree
of our own came up empty twice and is deleted.

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
| `bag_wtp_best` | `out * (1 + bonus/100) * RANK_SCALE` — what the ranking sorts on, never printed |
| `bag_wtp_rank` | the place it came in, 1 first — the «№» column, and what the copy sorts on |
| `bag_wtp_bt` / `_pm` | the building and the method that won |
| `bag_wtp_out` | what it produces a level, unscaled — the row's `×` |
| `bag_wtp_bonus` | the RGO bonus, which is the row's percentage |
| `bag_wtp_goods` / `_all` | the raw materials the province supplies, and how many it could |

For an urban right the same six are `bag_wtp_r_*_<k>` for slot `k` of the
bundle, with `bag_wtp_r_good_<k>` naming the good and `bag_wtp_r_total` the sum
the ranking sorts on. Three slots, because three is the widest bundle and script
has no list of tuples.

Each has a `_rural` twin — villages are scored on their own side and a row shows
both answers — and each row reads them off its own scope: no globals per row,
and no ceiling but `RESULT_ROWS`. Not built: sorting or filtering inside the
window, and any measure of a building's cost or its slot.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

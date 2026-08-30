# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method **available to you now** and ranks the locations by what that method would
earn from the raw materials the province supplies.

**State: twelve loads in.** The twelfth confirmed the map pickers now reach the
pass and killed two more faults it exposed. Nothing since is confirmed: **the
thirteenth run is what says so.**

## What the twelfth run cost, and what the thirteenth has to answer

The eleventh's scope fix worked — a pick re-ranks — and immediately showed two
things behind it, both fixed blind:

- **`root` was still assumed to be the country in 218 places.** The rule reached
  the row pass and not the scoring pass beside it, so a pick reached the pass and
  the pass found no method available anywhere: «обошёл 44 · нашёл 0», and a table
  that emptied on every pick. The country is `save_scope_as` at the top of
  `bag_wtp_score_candidates` now, and no `root` is left outside
  `bag_wtp_generated_picker.txt`, which only CMM callbacks reach.
- **`order_by` will not sort a fraction.** A scriptorium scores 0.3000 to 0.3129
  across Europe and the rows came back in map order. `bag_wtp_m<n>` is the
  output × `RANK_SCALE` (1000) now — 300.00 to 312.88 — and nothing prints it:
  the row's `×` is the method's own output, written out unscaled.

So the thirteenth wants the best bonus at «№» 1 and falling down the window,
«нашёл» staying non-zero after a pick, and the counts agreeing with what was
clicked. If the order is still wrong, the «№» tooltip carries the number the
sort saw: two numbers in the right order under two rows in the wrong one means
`order_by` is not the tool for this at all.

Never judged, three times deferred: the two-line rows, villages not at the top
of a weapons search, the goods icons beside their count, and the age filter.

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

Each has a `_rural` twin — villages are scored on their own side and a row shows
both answers — and each row reads them off its own scope: no globals per row,
and no ceiling but `RESULT_ROWS`. Not built: sorting or filtering inside the
window, and any measure of a building's cost or its slot.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

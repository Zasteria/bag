# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method **available to you now** and ranks the locations by what that method would
earn from the raw materials the province supplies.

**State: seventeen loads in, and confirmed in game end to end.** It answers for
a single good and for a whole urban right, in a window each; the ranking sorts,
a pick re-ranks live, the pickers stay folded, the age filter moves the answer
as ages pass, and «Открыть» reopens the last result.

## Where it stands

Two things go into the next load and neither is structural: **no province at
0.00% on every good of a bundle** — the trigger that filters them was called and
never written until the seventeenth run — and **the two rights lists**, of which
«Уникальные права» should be empty for anyone but a Byzantine or a Scandinavian.

**Urban rights: two lists on the Goods tab** — nine general and the
country-specific ones, split on `unlock_town_rights` rather than on opinion —
and a **second window**, because a bundle of two or three goods is a different
question in a different unit. A unique right is offered only where the game's
own `potential` or unlocking advance says it could be held. The numbers:
[`../../docs/investigations/town_rights.md`](../../docs/investigations/town_rights.md).

One button, not two: «Считать» answers whichever of a good and a right is
ticked, and they cannot both be ticked.

**`cmf_on_mod_registration` fires every time the mod page is opened**, so
`bag_wtp_register` must destroy nothing.

**Two things are settled and not to be attempted again.** Clicking the map with
a window open is impossible (`docs/research/interface.md`), and a geography tree
of our own came up empty twice and is deleted. Only the pickers are still CMM's;
their caps are in `docs/research/cmf.md`.

## Settled, and not to be re-litigated

- **The map picker closes after each pick** — the action's lifecycle, not a
  fault, and the only map-click channel a mod has.
- **A window's datamodel is what costs.** A scripted widget never comes down, so
  only the list it repeats over decides how many rows are alive; each window's
  list is filled on opening and emptied on closing.
- **The selection is recorded twice** — a variable on the location, a global list
  for the ranking — and only `bag_wtp_pick` / `bag_wtp_drop` may write it.
- **The bonus is province-level**, which is why a row is a province: what would
  separate two of its locations is building slots, and the game exposes none.
- **The buildable tick is about the location, not the owner.** `can_build_building`
  is asked in the location's scope: rank, terrain, what the building needs. A
  province with no town drops out; one across a border does not.
- **And the province is the `province_definition`** — the `province` is one
  owner's piece of it, and this answers for the ground, not today's border.
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

Each has a `_rural` twin, and each row reads them off its own scope: no globals
per row, no ceiling but `RESULT_ROWS`. Not built: sorting inside a window, and
any measure of a building's cost.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

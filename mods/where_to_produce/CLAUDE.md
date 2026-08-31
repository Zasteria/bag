# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province works.

**State: twenty-five loads in, and a row answers in three ages** — «Сейчас»,
«По пути» (the best this ground ever feeds, and the last age it can be built),
«В конце». **Two «Считать» buttons, not three sort headers:** one orders by
today, the other by the end and breaks its ties on «По пути», the only column
with anything to say where a ladder ends early.

## Where it stands

**A recipe the province mostly cannot feed is not an answer**, and where none
clears the bar there is no row. The bar is half the bonus the recipe could ever
earn — `generate.fed_floor`, one literal per method — because "fed anything at
all" offered a silk weaver where there are dyes and no silk. Every column keeps a
fed answer for the ranking and an unfed one for printing, so a cell says 0.00%
where a blank would lie: wool fine cloth stops at the workshop.

**A building runs one method out of each of its slots** — eight have two, and
each slot earns its own bonus over its own output (settled from the game's
panel), so a `Method` is the pair: `eu5data.Method.shares`, and why in
[`../../docs/investigations/production_ladder.md`](../../docs/investigations/production_ladder.md).

**Urban rights** are two lists on the Goods tab and a window of their own, on the
same two buttons and fallbacks but with no «По пути» column, only the tiebreak. A
right's country gate is its own `potential` or its advance's, never
`has_advance`, so most countries see none of the three. Numbers and the deferred
level rights:
[`../../docs/investigations/town_rights.md`](../../docs/investigations/town_rights.md).

**`cmf_on_mod_registration` fires every time the mod page is opened**, so
`bag_wtp_register` destroys nothing. **Not to be attempted again:** a geography
tree of our own, empty twice. Picker caps: `docs/research/cmf.md`.

## Settled, and not to be re-litigated

- **A window's datamodel is what costs**: a scripted widget never comes down, so
  only the list it repeats over decides how many rows live. Filled on opening,
  emptied on closing.
- **The selection is recorded twice** — a location variable and a global list —
  and only `bag_wtp_pick` / `_drop` writes it.
- **Every column in both windows is a fixed width and none expands**; one that
  hugs its content is a `widget` with an anchored child, never a sized hbox.
  Three ways to lose a column to that, in `docs/pitfalls/interface.md`.
- **The bonus is province-level** — which is why a row is a `province_definition`:
  the whole ground, not one owner's piece. What would separate two of its
  locations is building slots, which the game hides.
- **The buildable tick is about the location, not the owner** (`docs/SETTLED.md`)
  and is the one setting that re-ranks the open window: it decides which
  locations are candidates at all.

## The answer lives on the location

`bag_wtp_fill_rows` parks it there; everything else reads it back:

| on the winning location | is |
| --- | --- |
| `bag_wtp_best` | `out * (1 + bonus/100) * RANK_SCALE` — what the ranking sorts on, never printed |
| `bag_wtp_rank` | the place it came in, 1 first — the «№» column |
| `bag_wtp_bt` / `_pm` | the building and the method that won |
| `bag_wtp_out` / `_bonus` | what it makes a level unscaled — the row's `×` — and the RGO bonus, its percentage |
| `bag_wtp_goods` / `_all` | the raw materials the province supplies, and how many it could |

`bag_wtp_mid_*` and `bag_wtp_end_*` are the same for the other two columns, plus
`bag_wtp_mid_age`; `_any_best*` is each column's unfed fallback, printed only,
and `bag_wtp_row_end` is which column the row prints. An urban right's are
`bag_wtp_r_*_<k>` for slot `k` of three (script has no list of tuples),
`_r_good_<k>` the good and `_r_total` what the ranking sorts on. All have a
`_rural` twin, all are read off the row's own scope: no globals per row, no
ceiling but `RESULT_ROWS`. Not built: what a building costs.

**Built by** `generate.py`, from `tools/refresh.py`. Depth:
[`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

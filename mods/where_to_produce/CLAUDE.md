# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province supplies.

**State: twenty-four loads in, and a row answers in three ages** — «Сейчас»,
«По пути» (the best this ground ever feeds, and the last age it can be built),
«В конце». **Two «Считать» buttons, not three sort headers:** one orders by
today, the other by the end and breaks its ties on «По пути», which is the only
column with anything to say where a ladder ends early.

## Where it stands

**A method the province feeds nothing of is not an answer**, and where nothing is
fed there is no row. Every column keeps a fed answer for the ranking and an unfed
one for printing, so a cell says 0.00% where a blank would lie — a ladder can end
early: wool fine cloth stops at the workshop.

**A building runs one method out of each of its slots**, and eight have two —
fine cloth, jewelry, cannons, firearms. **Each slot earns its own bonus over its
own output** (settled from the game's panel), so a `Method` is the pair, summed
output and blended bonus: `eu5data.Method.shares`, and why in
[`../../docs/investigations/production_ladder.md`](../../docs/investigations/production_ladder.md).

**The rights window obeys the same two buttons**, on the same fallbacks; it has
no «По пути» column, only the tiebreak. A right's country gate is its own
`potential` or its advance's — never `has_advance`.

**Urban rights** are two lists on the Goods tab and a window of their own: a
bundle is a different question in a different unit, and «Считать» answers
whichever of a good and a right is ticked. The numbers and the deferred level
rights:
[`../../docs/investigations/town_rights.md`](../../docs/investigations/town_rights.md).

**`cmf_on_mod_registration` fires every time the mod page is opened**, so
`bag_wtp_register` destroys nothing. **Not to be attempted again:** a geography
tree of our own — empty twice, deleted. Picker caps: `docs/research/cmf.md`.

## Settled, and not to be re-litigated

- **A window's datamodel is what costs.** A scripted widget never comes down, so
  only the list it repeats over decides how many rows live; a window's list is
  filled on opening and emptied on closing.
- **The selection is recorded twice** — a location variable and a global list —
  and only `bag_wtp_pick` / `_drop` writes it.
- **Every column in both windows is a fixed width; none expands.** Two ways to
  lose a row to that, both in `docs/PITFALLS.md`.
- **The bonus is province-level** — which is why a row is a province, and the
  `province_definition` at that: the whole ground, not one owner's piece. What
  would separate two of its locations is building slots, which the game hides.
- **The buildable tick is about the location, not the owner** — the row for it
  is in `docs/SETTLED.md`.

## The answer lives on the location

`bag_wtp_fill_rows` parks it there; everything else reads it back:

| on the winning location | is |
| --- | --- |
| `bag_wtp_best` | `out * (1 + bonus/100) * RANK_SCALE` — what the ranking sorts on, never printed |
| `bag_wtp_rank` | the place it came in, 1 first — the «№» column |
| `bag_wtp_bt` / `_pm` | the building and the method that won |
| `bag_wtp_out` | what it makes a level, unscaled — the row's `×` |
| `bag_wtp_bonus` | the RGO bonus, the row's percentage |
| `bag_wtp_goods` / `_all` | the raw materials the province supplies, and how many it could |

`bag_wtp_mid_*` and `bag_wtp_end_*` are the same for the other two columns, plus
`bag_wtp_mid_age`; `_any_best*` is each column's unfed fallback, printed only,
and `bag_wtp_row_end` is which column the row prints.

For an urban right the same six are `bag_wtp_r_*_<k>` for slot `k` of the
bundle, `bag_wtp_r_good_<k>` naming the good and `bag_wtp_r_total` the sum the
ranking sorts on. Three slots: script has no list of tuples.

All have a `_rural` twin and are read off the row's own scope: no globals per
row, no ceiling but `RESULT_ROWS`. Not built: what a building costs.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

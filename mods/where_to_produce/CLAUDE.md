# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province works.

**State: twenty-seven loads in, and a row answers in three ages** — «Сейчас»,
«По пути» (the best this ground ever feeds, and the last age it can be built),
«В конце». **Two «Считать» buttons, not three sort headers:** one orders by
today, the other by the end and breaks ties on «По пути», the only column with
anything to say where a ladder ends early.

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
right's gate is its own `potential` or its advance's, never `has_advance`, so
most countries see none of the three. Numbers and the deferred level rights:
[`../../docs/investigations/town_rights.md`](../../docs/investigations/town_rights.md).

**Four pickers, and the market one names its own candidates**: only what
`interaction_source_list` holds is clickable, so `bag_wtp_select_market` fills it
from `every_market_in_world` (`docs/SETTLED.md`).

**The whole-map plan is built and has never been loaded.** Every good at once,
one building at a time, under a cap per location: three numeric settings, a
window of rows by load, a map mode painting the same. It reuses
`bag_wtp_score_<g>` and **normalizes each good by its own best here**, without
which the biggest recipe takes every contested province. **The expensive
button** — 241 recipes a location against a ranking's five — and that cost is
what a first run measures. All of it in
[`../../docs/investigations/whole_map_plan.md`](../../docs/investigations/whole_map_plan.md).

**`cmf_on_mod_registration` fires every time the mod page is opened**, so
`bag_wtp_register` destroys nothing. **Not to be attempted again:** a geography
tree of our own, empty twice. Picker caps: `docs/research/cmf.md`.

## Settled, and not to be re-litigated

- **A window's datamodel is what costs**: a scripted widget never comes down, so
  only the list it repeats over decides how many rows live. Filled on opening,
  emptied on closing.
- **The selection is recorded twice**, a location variable and a global list, and
  only `bag_wtp_pick` / `_drop` writes it.
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

`bag_wtp_fill_rows` parks it there and everything else reads it back — every
variable named, and the `_rural`, `mid_`, `end_` and urban-right twins, in
[`README.md`](README.md#the-answer-lives-on-the-location). No globals per row,
no ceiling but `RESULT_ROWS`. Not built: what a building costs.

**Built by** `generate.py`, from `tools/refresh.py`. Depth:
[`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

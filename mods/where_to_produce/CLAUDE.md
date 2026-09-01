# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province works.

**State: twenty-nine loads in.** A row answers in three ages — «Сейчас», «По
пути» (the best this ground ever feeds, and the last age it can be built), «В
конце» — on two «Считать» buttons rather than sort headers.

## Where it stands

**A recipe the province mostly cannot feed is not an answer** — the bar is half
the bonus the recipe could ever earn (`generate.fed_floor`), because "fed
anything at all" offered a silk weaver where there are dyes and no silk. Every
column keeps a fed answer for the ranking and an unfed one for printing, so a
cell says 0.00% where a blank would lie.

**A building runs one method out of each of its slots** — eight have two, each
earning its own bonus over its own output, so a `Method` is the pair
(`eu5data.Method.shares`):
[`../../docs/investigations/production_ladder.md`](../../docs/investigations/production_ladder.md).

**Urban rights** are two lists on the Goods tab and a window of their own, with
no «По пути» column. A right's gate is its own `potential`, never `has_advance`.
Numbers and the deferred level rights:
[`../../docs/investigations/town_rights.md`](../../docs/investigations/town_rights.md).

**Four pickers, and the market one names its own candidates**: only what
`interaction_source_list` holds is clickable, so `bag_wtp_select_market` fills it
from `every_market_in_world` (`docs/SETTLED.md`).

**The whole-map plan is chosen per province and spent per location.** Two short
lists a province, towns and villages, each as long as that side's cap; every
location builds its side's list. Sweeps until the ground is full. **A list entry
is a building, not a good** — one building of a type a location, one method a
building. **Every building is one `can_build_building` allows in that location**
(terrain, rank, `location_potential`, never an advance — so it is safe for
unowned ground and for the endgame plan). **The two sides are the building's own
rank gates**, not `village_category`. **A right is all or nothing**: a province
that cannot take its whole bundle is not offered it.
Urban rights take a town list whole, chosen per province. Every condition is a
location variable — **a `province_definition` holds none** (`docs/PITFALLS.md`).
**The expensive button** — 241 recipes a location. All of it in
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

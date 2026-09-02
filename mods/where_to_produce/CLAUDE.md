# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province works.

**State: the plan works and he has seen it** — «города получают права и домики из
прав», 2026-09-02. Four fifths of placed buildings earn a bonus where they stand.
**Three fixes on top of it, none of them run**: the round guard at 50, the tier
ladder in the last band only (twelve passes), and a paged plan window.

**The tick is the rank, for the whole calculation** — `bag_wtp_stands_<building>`
takes the rank from the tick, the `location_potential` still from the game — and
**a tick outlives a save**, so «Сбросить пометки» clears all five continents at
once. Both are rows in `docs/SETTLED.md`. «Диагностика» + `mods.bat → 8` reads
the plan back and draws the conclusions.

A row answers in three ages — «Сейчас», «По пути» (the best this ground ever
feeds, and the last age it can be built) and «В конце» — on two «Считать»
buttons.

## Where it stands

**A recipe the province mostly cannot feed is no answer to the ranking** — the
bar is half the bonus it could ever earn (`generate.fed_floor`) — but **the plan
must never use it as a gate**. Nor is a recipe whose building cannot stand there:
`can_build_building`, in all three ages.

**A building runs one method out of each of its slots** — eight have two, each
earning its own bonus over its own output:
[`production_ladder.md`](../../docs/investigations/production_ladder.md).

**Urban rights** are two lists on the Goods tab and a window of their own, with
no «По пути» column. A right's gate is its own `potential`, never `has_advance`;
in the plan every town gets one and its whole bundle goes up. Numbers and the
deferred level rights: [`town_rights.md`](../../docs/investigations/town_rights.md).

**The plan is an optimisation with a covering constraint** — maximise the bonus
captured, subject to every good the ground can produce being produced. **Read
[`plan_formula.md`](../../docs/investigations/plan_formula.md) before changing
any of it.** Two things to carry: the currency is **`gain =
bonus ÷ that recipe's own ceiling`**, since a raw bonus does not compare across
goods; and the ground is **dealt in descending bands of gain across every good
at once**. **An entry is a building and a location holds one of each.** **The
sides are the building's own rank gates**, not `village_category`. Every
condition is a location variable — **a `province_definition` holds none**
(`docs/PITFALLS.md`). How it is put together:
[`whole_map_plan.md`](../../docs/investigations/whole_map_plan.md).

`bag_wtp_register` destroys nothing, because registration reruns
(`docs/PITFALLS.md`). **Not to be attempted again:** a geography tree of our own,
empty twice.

## Settled, and not to be re-litigated

- **A window's datamodel is what costs**: a scripted widget never comes down, so
  only the list it repeats over decides the row count — hence `PLAN_ROWS` is one
  page of the plan and `PLAN_RANKED` the answer, each location told its page.
- **The selection is recorded twice**, a location variable and a global list;
  only `bag_wtp_pick` / `_drop` writes it.
- **Every column in both windows is a fixed width and none expands**; one that
  hugs its content is a `widget` with an anchored child, never a sized hbox
  (`docs/pitfalls/interface.md`).
- **The bonus is province-level** — which is why a row is a `province_definition`:
  the whole ground, not one owner's piece. What would separate its locations is
  building slots, which the game hides.
- **The buildable tick is about the location, not the owner**
  (`docs/SETTLED.md`), and it re-ranks the open window.

## The answer lives on the location

`bag_wtp_fill_rows` parks it there and everything else reads it back — every
variable named, and the `_rural`, `mid_`, `end_` and urban-right twins, in
[`README.md`](README.md#the-answer-lives-on-the-location). No globals per row.
Not built: what a building costs.

**Built by** `generate.py`, from `tools/refresh.py`. Depth:
[`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

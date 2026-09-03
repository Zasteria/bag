# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province works.

**Read before touching any `_plan_*`:
[`plan_gaps.md`](../../docs/investigations/plan_gaps.md)** — eight faults, all
closed, all but one confirmed by a run. The press still owed is about **a large
ground**: 48 locations cannot tell the ladders apart.

**State: the plan works and he has seen it** — «города получают права и домики из
прав». Numbers live in `docs/TESTLOG.md`, never here.

**The tick is the rank, for the whole calculation** — `bag_wtp_stands_<building>`
takes the rank from the tick, the `location_potential` still from the game — and
**a tick outlives a save**, so «Сбросить пометки» clears all five continents at
once (`docs/SETTLED.md`). «Диагностика» + `mods.bat → 8` reads the plan back.

## Where it stands

**A recipe the province mostly cannot feed is no answer to the ranking** — the bar
is `generate.fed_floor` — but **the plan must never use it as a gate**. Nor is a
recipe whose building cannot stand there: `can_build_building`, all three ages.
**The bonus counts RGOs only** (`docs/research/engine.md`).

**A building runs one method out of each of its slots** — eight have two, each
earning its own bonus over its own output:
[`production_ladder.md`](../../docs/investigations/production_ladder.md). A row
answers in three ages — «Сейчас», «По пути», «В конце» — on two «Считать» buttons.

**Urban rights** are two lists on the Goods tab and a window of their own; in the
plan every town gets one and its whole bundle goes up. **A right's gate is its own
`potential` and never `has_advance`, in the plan as in the window** — the advance
is reported, not enforced. And **the game's exclusion between two rights is a
town's rule, not a country's**.
Numbers: [`town_rights.md`](../../docs/investigations/town_rights.md).

**The plan is an optimisation with a covering constraint** — maximise the bonus
captured, subject to every good the ground can produce being produced. **Read
[`plan_formula.md`](../../docs/investigations/plan_formula.md) before changing any
of it.** The currency is **`gain = bonus ÷ the best ceiling any recipe of that
*good* reaches in the game`**; the ground is **dealt in descending bands of gain
across every good at once**, four ladders of five bands — coverage, the scarce,
everything, the leftovers — and **the order between them is the design**.

**An entry is a building and a location holds one of each**, **the sides are the
building's own rank gates** and not `village_category`, and every condition is a
location variable — **a `province_definition` holds none** (`docs/PITFALLS.md`).
[`whole_map_plan.md`](../../docs/investigations/whole_map_plan.md).

**Not to be attempted again:** a geography tree of our own (empty twice), a
relative band ladder (`plan_gaps.md` D), gating charters on their advance (H), and
reopening why a scarce good has one building — **it is the RGO discount, measured
twice** (B). `bag_wtp_register` destroys nothing (`docs/PITFALLS.md`).

## Settled, and not to be re-litigated

- **A window's datamodel is what costs**: a scripted widget never comes down, so
  only the list it repeats over decides the row count — `PLAN_ROWS` is one page
  and `PLAN_RANKED` the answer.
- **The bonus is province-level** — hence a row is a `province_definition`: the
  whole ground, not one owner's piece; what would separate its locations is
  building slots, which the game hides.
- **The selection is recorded twice** and only `bag_wtp_pick` / `_drop` writes it;
  **every column is a fixed width** (`docs/pitfalls/interface.md`); **the
  buildable tick is the location's, not the owner's** (`docs/SETTLED.md`).

**The answer lives on the location.** `bag_wtp_fill_rows` parks it there and
everything else reads it back, never a global per row; every variable is named in
[`README.md`](README.md#the-answer-lives-on-the-location).

**Built by** `generate.py`, from `tools/refresh.py`. Depth:
[`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

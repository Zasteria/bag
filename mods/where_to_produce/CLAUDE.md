# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province works.

**State: rolled back 2026-09-02 to the build of the thirty-eighth load** — the
four tests the owner called «большой рывок». Everything built above it is out;
what is open here, and what those runs settled, is the last section of
`plan_formula.md` below.

**The one job is a run, not a cause.** «Диагностика» on the «Расчёт» tab writes
everything the mod knows into `debug.log`, and `mods.bat → 8` puts it in the
clipboard; the protocol and every branch of the answer are in `docs/TESTLOG.md`,
written down before the run. Four theories were wrong on four runs
(`docs/pitfalls/diagnosis.md`): read the report first.

A row answers in three ages — «Сейчас», «По пути» (the best this ground ever
feeds, and the last age it can be built) and «В конце» — on two «Считать»
buttons.

## Where it stands

**A recipe the province mostly cannot feed is no answer to the ranking** — the
bar is half the bonus it could ever earn (`generate.fed_floor`) — but **the plan
must never use it as a gate**: every good the ground can produce has to be
produced, fed or not. Nor is a recipe whose building cannot stand there:
`can_build_building`, in all three ages.

**A building runs one method out of each of its slots** — eight have two, each
earning its own bonus over its own output:
[`../../docs/investigations/production_ladder.md`](../../docs/investigations/production_ladder.md).

**Urban rights** are two lists on the Goods tab and a window of their own, with
no «По пути» column. A right's gate is its own `potential`, never `has_advance`;
in the plan every town gets one and its whole bundle goes up. Numbers and the deferred level rights:
[`../../docs/investigations/town_rights.md`](../../docs/investigations/town_rights.md).

**The plan is an optimisation with a covering constraint** — maximise the bonus
captured, subject to every good the ground can produce being produced. **Read
[`../../docs/investigations/plan_formula.md`](../../docs/investigations/plan_formula.md)
before changing any of it.** Two things to carry: the currency is **`gain =
bonus ÷ that recipe's own ceiling`**, since a raw bonus does not compare across
goods; and the ground is **dealt in descending bands of gain across every good
at once**. **An entry is a building and a location holds one of each.** **The
sides are the building's own rank gates**, not `village_category`. Every
condition is a location variable — **a `province_definition` holds none**
(`docs/PITFALLS.md`). How it is put together:
[`../../docs/investigations/whole_map_plan.md`](../../docs/investigations/whole_map_plan.md).

**`cmf_on_mod_registration` fires every time the mod page is opened**, so
`bag_wtp_register` destroys nothing. **Not to be attempted again:** a geography
tree of our own, empty twice. Picker caps: `docs/research/cmf.md`.

## Settled, and not to be re-litigated

- **A window's datamodel is what costs**: a scripted widget never comes down, so
  only the list it repeats over decides the row count.
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

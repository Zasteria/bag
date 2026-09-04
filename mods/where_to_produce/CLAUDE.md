# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province works.

**Read before touching any `_plan_*`:
[`plan_gaps.md`](../../docs/investigations/plan_gaps.md)** — the checklist at its
end is what the next press has to show.

**State: the plan works and he has seen it.** Numbers live in `docs/TESTLOG.md`.
**The tick is the rank** and **outlives a save** (`docs/SETTLED.md`).

## Where it stands

**A recipe the province mostly cannot feed is no answer to the ranking** — the bar
is `generate.fed_floor` — but **the plan must never use it as a gate**. **The bonus
counts RGOs only**; **one method per slot**:
[`production_ladder.md`](../../docs/investigations/production_ladder.md).

**Urban rights** are two lists on the Goods tab and a window of their own; every
town gets one and its whole bundle goes up — **108 rooms of 192 on a small
ground, which is where most of its shape comes from**. **The charter ladder
raises its ceiling one town at a time and runs every band at each height**; a
ceiling alone spreads nothing. That lands **84% of the best placement with those
counts**. **A right's gate is its own `potential`, never `has_advance`**, and
**an exclusion between two rights is a town's rule, not a country's**.
[`town_rights.md`](../../docs/investigations/town_rights.md).

**The plan is an optimisation with a covering constraint** — maximise the bonus
captured, subject to every good the ground can produce being produced. **Read
[`plan_formula.md`](../../docs/investigations/plan_formula.md) before changing any
of it.** The currency is **`gain = bonus ÷ the best ceiling any recipe of that
*good* reaches in the game`**; the ground is dealt in **four ladders of five
descending bands** — coverage, the scarce, everything, the leftovers — and **the
order between them is the design**. **The last ladder's band is each good's own
best**: the share goes on gain, the leftovers on fit.

**A good's share is the whole ground divided by the goods, less one per RGO, and
a charter's buildings are spent out of it.**

**An entry is a building and a location holds one of each**, and every condition is
a location variable — **a `province_definition` holds none**
([`whole_map_plan.md`](../../docs/investigations/whole_map_plan.md)). **A row draws
`_row_goods`, not `_plan_goods`**, so its order never moves.

**A preference is an edit, not a term in the objective.** `bag_wtp_edit_*` moves
one building a press, where it costs least. **Two rules: a good keeps its last
building, and a charter's go whole or not at all** («забирать целиком всю связку
право+его домики» — that edit is owed). Nothing is evicted while a room is free,
nor left evicted if the placement refuses, and **`_edit_place_*` asks the cap
itself**: a placement that cannot say no corrupts the plan. **Three `WTP EDIT`
lines in the report** — a press is otherwise invisible to it.

**The editor is a window and never the settings page.** Three save slots, then
every good as a cell of «−1, icon with its count, +1». **A window exists only if
`in_game/gui/scripted_widgets/` names it**; **a control behind a first click is one
he will not find**; and **the picker is 47 written-out cells**, because a
datamodel row carries a goods scope and a scope reaches no numbered `_pn<n>`
([`pitfalls/interface.md`](../../docs/pitfalls/interface.md)).
`check_script.py` resolves every name a window says.

**Not to be attempted again**, all built or measured and rejected: a geography tree
of our own, gating charters on their advance, spreading them inside a province,
answering a preference with a re-plan, the editor on the settings page, granting
charters charter-first, finer bands, a wrapping widget in the picker.
[`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md).

**The answer lives on the location**, and **four things are settled and not to be
re-litigated**: [`README.md`](README.md).

**Built by** `generate.py`, from `tools/refresh.py`. Depth:
[`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province works.

**Read before touching any `_plan_*`:
[`plan_gaps.md`](../../docs/investigations/plan_gaps.md)** — eight faults closed,
and the checklist at its end is what the next press has to show.

**State: the plan works and he has seen it.** Numbers live in `docs/TESTLOG.md`,
never here. **The tick is the rank, for the whole calculation**, and **a tick
outlives a save** (`docs/SETTLED.md`).

## Where it stands

**A recipe the province mostly cannot feed is no answer to the ranking** — the bar
is `generate.fed_floor` — but **the plan must never use it as a gate**. **The bonus
counts RGOs only** (`docs/research/engine.md`), and **a building runs one method
per slot**: [`production_ladder.md`](../../docs/investigations/production_ladder.md).

**Urban rights** are two lists on the Goods tab and a window of their own; in the
plan every town gets one and its whole bundle goes up — **108 rooms of 192 on a
small ground, which is where most of its shape comes from**. **The charter ladder
raises its ceiling one town at a time and runs every band at each height**; a
ceiling alone spreads nothing. That lands **84% of the best placement with those
counts, and charter-first and finer bands both measure worse**. **A right's gate
is its own `potential`, never `has_advance`**, and **the exclusion between two
rights is a town's rule, not a country's**.
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
a charter's buildings are spent out of it.** It used to be the rooms the charters
*left*, with a good's own charters added back — 2 on Westphalia, so wine walked in
at 8 and iron at 1, and he did that arithmetic himself.

**An entry is a building and a location holds one of each**, and every condition is
a location variable — **a `province_definition` holds none**
([`whole_map_plan.md`](../../docs/investigations/whole_map_plan.md)).

**A preference is an edit, not a term in the objective.** `bag_wtp_edit_*` changes
a finished plan in place: one building a press, into the location where it costs
least, and nothing else moves. **A good's last building and a charter bundle's
buildings are never the victim.** A weight fed into a re-plan was built first and
moved 42 locations of 48 — that is the thing not to build again.

**The editor is a window and never the settings page.** `bag_wtp_edit_window.gui`:
three save slots, the ground's goods as icons, «−1» / «+1» beside each one picked;
`bag_wtp_changes_window.gui` is «показать изменения». **The first build of it never
drew at all and the cause is still unnamed** — no base widget type is in
`reference/`, so nothing here can check a `.gui` statically; `error.log` is the
only thing that can say why.

**Not to be attempted again**, all built or measured and rejected: a geography tree
of our own, gating charters on their advance, spreading charters inside a province,
answering a preference with a re-plan, the editor on the settings page, granting
charters charter-first, and finer bands.
[`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md).

**The answer lives on the location**, and **four things are settled and not to be
re-litigated**: [`README.md`](README.md).

**Built by** `generate.py`, from `tools/refresh.py`. Depth:
[`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

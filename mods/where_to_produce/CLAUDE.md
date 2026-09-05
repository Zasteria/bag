# `where_to_produce` — brief

Name a good and the ground; the mod finds each location its best production
method and ranks the locations by what that method would earn from the raw
materials the province works.

**Read before touching any `_plan_*`:
[`plan_gaps.md`](../../docs/investigations/plan_gaps.md).** Numbers live in
`docs/TESTLOG.md`. **The tick is the rank** and **outlives a save**
(`docs/SETTLED.md`).

## Where it stands

**A recipe the province mostly cannot feed is no answer to the ranking** —
`generate.fed_floor` — but **never gate the plan on it**. **The bonus counts
RGOs only**; **one method per slot**:
[`production_ladder.md`](../../docs/investigations/production_ladder.md).

**Urban rights** are two lists on the Goods tab and a window of their own; every
town gets one and its whole bundle goes up — **108 rooms of 192 on a small
ground**. **The charter ladder raises its ceiling one town at a time, running
every band at each height**; a ceiling alone spreads nothing. **A right's gate is its own `potential`, never `has_advance`**, and
**an exclusion between two rights is a town's rule, not a country's**.
[`town_rights.md`](../../docs/investigations/town_rights.md).

**The plan is an optimisation with a covering constraint** — maximise the bonus
captured, subject to every good the ground can produce being produced. **Read
[`plan_formula.md`](../../docs/investigations/plan_formula.md) before changing any
of it.** The currency, the **four ladders of five descending bands** and the order
between them are the design; the last band is each good's own best.

**A good's share is the ground divided by the goods, less one per RGO; a
charter's buildings are spent out of it.**

**An entry is a building and a location holds one of each**, and every condition
is a location variable — **a `province_definition` holds none**
([`whole_map_plan.md`](../../docs/investigations/whole_map_plan.md)). **A row draws `_row_goods`, not
`_plan_goods`**, so its order never moves.

**A preference is an edit, not a term in the objective.** `bag_wtp_edit_*` moves
one building a press, where it costs least; a good keeps its last building and a
charter's go whole or not at all. Nothing is evicted while a room is free, nor left
evicted if the placement refuses, and **`_edit_place_*` asks the cap itself**. **Three `WTP EDIT` lines in the
report**; **the round trip is no undo** (`docs/TESTLOG.md`).

**A press pins its good** — `_lock<n>` — and a freed room goes to the good
**furthest below its share**; without the pin that rule undoes his presses.
**A pin is yellow in the cell and released by its own button**: state he cannot
see or clear is the mod's fault, twice paid for. **`_skip<n>` («не нужен») outlives a plan**
and **the plan reads it too** — `_pq<n>` held at 1, the open ladder skipping it.
**Both are existence flags, and a slot stores and restores both**: his rule,
2026-09-05, that loading a plan must not carry what came after saving it.
**`_edit_locked_<n>` is the charter's bundle, not the player's pin.**

**The editor is a window, never the settings page.** Three slots, then every
good as a cell of «−1, count, +1, не нужен». **Its header prints a build stamp** — ask
for it before believing a fix failed.
**The editor has no re-plan button**: «План»/«На конец» are on the mod's page,
«Пересчитать» in the results window. **A window exists only if
`in_game/gui/scripted_widgets/` names it**; **a glyph the game never uses may not be in
the font** — take a texture, and colour with `#Y …#!`, never `§`; **a control behind a first click is one
he will not find**; and **the picker is 47 cells in fixed columns**, because a
datamodel row carries a goods scope and a scope reaches no numbered `_pn<n>`
([`pitfalls/interface.md`](../../docs/pitfalls/interface.md)).
`check_script.py` resolves every name a window says **except a widget type**, and
**measures the box against its widest row**.

**Not to be attempted again**: eight, built or measured and rejected —
[`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md). **The answer
lives on the location**, and **four things are settled**: [`README.md`](README.md).

**Built by** `generate.py`, from `tools/refresh.py`. Anything else:
`python3 tools/kb.py <words>`.

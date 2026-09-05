# `where_to_produce` — brief

## Four functions. Never mix them up.

His words, 2026-09-06, after the fourth time: «ты постоянно смешиваешь функции
плана и редактирования». **Read this list before touching anything.**

| # | what | where | files |
| --- | --- | --- | --- |
| 1 | **Choose the ground** for everything below | mod page | `_zone_*`, `_region_*` |
| 2 | **One good or one town right → the top locations for it**, ranked by what local RGOs pay | mod page + results window | `_score_*`, `_rank_*` |
| 3 | **A whole plan for that ground** — every production seeded where it pays | «План» / «На конец» on the mod page; «Пересчитать» in the results window | `_plan_*` |
| 4 | **Editing that plan afterwards**, one building at a time | the editor window, and only there | `_edit_*` |

**3 and 4 are separate, and the traffic between them runs one way.** The editor
reads the plan on the map and changes it. **Nothing the editor holds — a pin, a
«не нужен» flag, its share, the star in a cell — is ever read by 3.** Pressing
«План» gives a fresh plan, full stop.

Crossed on 2026-09-05: `_plan_set_quota`, inside `_plan_run`, held `_pq<n>` at 1
for a flagged good, so an editor click steered the next plan. Reverted.
**The test: «не нужен», then «План» — the new plan must be ordinary.**

**Read before touching any `_plan_*`:
[`plan_gaps.md`](../../docs/investigations/plan_gaps.md).** **The tick is the
rank** and **outlives a save** (`docs/SETTLED.md`).

## Where it stands

**Never gate the plan on `generate.fed_floor`**; **the bonus counts RGOs only**;
**one method per slot**:
[`production_ladder.md`](../../docs/investigations/production_ladder.md).

**Urban rights** shape most of a small ground — 108 rooms of 192. **A right's
gate is its own `potential`, never `has_advance`.** Detail:
[`README.md`](README.md#права), [`town_rights.md`](../../docs/investigations/town_rights.md).

**The plan is an optimisation with a covering constraint** — maximise the bonus
captured, subject to every good the ground can produce being produced. **Read
[`plan_formula.md`](../../docs/investigations/plan_formula.md) before changing any
of it.**

**An entry is a building and a location holds one of each**; **a
`province_definition` holds no variables**
([`whole_map_plan.md`](../../docs/investigations/whole_map_plan.md)).

**A preference is an edit, not a term in the objective.** `bag_wtp_edit_*` moves
one building a press, where it costs least; a good keeps its last building and a
charter's go whole or not at all. **`_edit_place_*` asks the cap itself.** **Three `WTP EDIT` lines in the
report**; **the round trip is no undo** (`docs/TESTLOG.md`).

**A press pins its good** — `_lock<n>` — and a freed room goes to the good
**furthest below its share**; without the pin that rule undoes his presses. **A
pin is a star after the count, released by its own button. He asks for symbols,
not colours.** `_lock<n>` and `_skip<n>` are existence
flags a slot stores and restores.
**`_edit_locked_<n>` is the charter's bundle, not the player's pin.**

**The editor is a window, never the settings page.** Three slots, then every
good as a cell of «−1, count, +1, не нужен». **Its header prints a build stamp** — ask
for it before believing a fix failed. **A window exists only if
`in_game/gui/scripted_widgets/` names it**; **a glyph the game never uses may not be in
the font** — take a texture, and colour with `#Y …#!`, never `§`; **a control behind a first click is one
he will not find**; and **the picker is 47 cells in fixed columns**, because a
datamodel row carries a goods scope and a scope reaches no numbered `_pn<n>`
([`pitfalls/interface.md`](../../docs/pitfalls/interface.md)).
`check_script.py` resolves every name a window says **except a widget type**, and
**measures the box against its widest row**.

**Not to be attempted again**: eight, rejected —
[`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md). **The answer
lives on the location**: [`README.md`](README.md).

**Built by** `generate.py`, from `tools/refresh.py`. Anything else:
`python3 tools/kb.py <words>`.

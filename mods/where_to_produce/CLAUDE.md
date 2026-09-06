# `where_to_produce` — brief

## Four functions. Never mix them up.

«Ты постоянно смешиваешь функции плана и редактирования» — его слова.

**The mod page is three tabs — Земля, Расчёты, Техническая — and four buttons
that only open windows**, every setting inside the window of its function. **Two rules of his, above any layout
idea**: **no descriptions in a window header** — that is the control's tooltip —
and **anything technical belongs on «Техническая»**
([`wtp_menu_rebuild.md`](../../docs/investigations/wtp_menu_rebuild.md)).

| # | what | where | files |
| --- | --- | --- | --- |
| 1 | **Choose the ground** | «Земля» on the mod page, or the map buttons in any window | `_zone_*`, `_region_*` |
| 2 | **One good or right → the best locations for it**, by what local RGOs pay | the ranking window: circles pick it, «Искать локации» runs it | `_score_*`, `_rank_*`, `_pick_*` |
| 3 | **A whole plan for that ground** — every production where it pays | the plan window: the caps and both switches there, «Пересчитать» runs it | `_plan_*` |
| 4 | **Editing that plan afterwards**, one building at a time | the editor window, and only there | `_edit_*` |

**3 and 4 are separate, and the traffic runs one way.** The editor reads the plan
and changes it; **nothing it holds — a pin, a «не нужен» flag, the star in a cell
— is ever read by 3**. Crossed once and reverted. **The test: «не нужен», then a
fresh plan — it must be ordinary.**

**Before touching any `_plan_*`:
[`plan_gaps.md`](../../docs/investigations/plan_gaps.md).** **The tick is the rank
and outlives a save.**

## Where it stands

**Never gate the plan on `generate.fed_floor`**; **the bonus counts RGOs only**;
**one method per slot**
([`production_ladder.md`](../../docs/investigations/production_ladder.md)).
**A right's gate is its own
`potential`, never `has_advance`**
([`town_rights.md`](../../docs/investigations/town_rights.md)). **The plan is an
optimisation with a covering constraint** — maximise the bonus captured, subject
to every good the ground can produce being produced
([`plan_formula.md`](../../docs/investigations/plan_formula.md)). **An entry is a
building and a location holds one of each**
([`whole_map_plan.md`](../../docs/investigations/whole_map_plan.md)).

**A preference is an edit, not a term in the objective**: `bag_wtp_edit_*` moves
one building a press, where it costs least, and **the round trip is no undo**.
**The editor's share subtracts the RGOs** — `_eq<n>`. **A press pins its good**
(`_lock<n>`); a freed room goes to the good furthest below its share, «+1» takes
one from the good furthest above, and what a fill placed then trades locations
between itself (`_fillg`, `_edit_reshuffle`). **A pin is a star, not a colour.** **The changes window is a diff, not a
chronology** (`_chg_seq` orders it); the journal is `WTP PRESS` in `debug.log`.
**A charter is not a building**: every town holds exactly one, so «+1»/«−1»
*moves* it, bundle and all, and no town ends without one (`_edit_right_swap`,
`_rquota`). `_lock<n>` and `_skip<n>` are existence
flags a slot stores and restores; **`_edit_locked_<n>` is the charter's bundle,
not the player's pin.** **«Расширить» доливает новую землю**: новое = выбранное
минус `_plan_touched`, старое заморожено, замок спадает, когда простая доля его
переросла. **Оно сужает `_candidates`, а не пишет второй план. Прогона не
было.**
[`wtp_editor_design.md`](../../docs/investigations/wtp_editor_design.md).

**The build stamp is on «Техническая»**, before believing a fix failed. **Before
touching any `.gui`, the checklist is
[`pitfalls/windows.md`](../../docs/pitfalls/windows.md)** — the window's own
shape, the frame line, the row's usable width, what `check_script.py` resolves
and what it cannot. Every rule in it this mod paid for, most of them twice.

**Not to be attempted again**: eight, rejected
([`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md)). **The answer
lives on the location**. **Built by** `generate.py` from `tools/refresh.py`.

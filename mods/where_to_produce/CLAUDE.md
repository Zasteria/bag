# `where_to_produce` — brief

## Four functions. Never mix them up.

His words, 2026-09-06, after the fourth time: «ты постоянно смешиваешь функции
плана и редактирования».

**Since 2026-09-06 the mod page is three tabs — Земля, Расчёты, Техническая —
and four buttons that only open windows**, every setting inside the window of
its function. A circle writes `bag_wtp_good_index` itself; `_right_ok<n>` says
whether a country may be shown a right, because a `visible` cannot ask a
trigger. **Built 2026-09-06, never run**:
[`wtp_menu_rebuild.md`](../../docs/investigations/wtp_menu_rebuild.md).

| # | what | where | files |
| --- | --- | --- | --- |
| 1 | **Choose the ground** for everything below | «Земля» on the mod page, or the map buttons in either window | `_zone_*`, `_region_*` |
| 2 | **One good or one town right → the top locations for it**, ranked by what local RGOs pay | the ranking window: circles pick it, «Искать локации» runs it | `_score_*`, `_rank_*`, `_pick_*` |
| 3 | **A whole plan for that ground** — every production seeded where it pays | the plan window: the caps and both switches there, «Пересчитать» runs it | `_plan_*` |
| 4 | **Editing that plan afterwards**, one building at a time | the editor window, and only there | `_edit_*` |

**3 and 4 are separate, and the traffic runs one way.** The editor reads the
plan on the map and changes it. **Nothing the editor holds — a pin, a «не нужен»
flag, its share, the star in a cell — is ever read by 3.** «Пересчитать» gives a
fresh plan, full stop.

Crossed once, 2026-09-05, and reverted: `_plan_set_quota` held `_pq<n>` at 1 for
a flagged good. **The test: «не нужен», then a fresh plan — it must be
ordinary.**

**Read before touching any `_plan_*`:
[`plan_gaps.md`](../../docs/investigations/plan_gaps.md).** **The tick is the
rank** and **outlives a save** (`docs/SETTLED.md`).

## Where it stands

**Never gate the plan on `generate.fed_floor`**; **the bonus counts RGOs only**;
**one method per slot**:
[`production_ladder.md`](../../docs/investigations/production_ladder.md).
**Urban rights** shape most of a small ground — 108 rooms of 192, and **a
right's gate is its own `potential`, never `has_advance`**:
[`README.md`](README.md#права), [`town_rights.md`](../../docs/investigations/town_rights.md).

**The plan is an optimisation with a covering constraint** — maximise the bonus
captured, subject to every good the ground can produce being produced; **read
[`plan_formula.md`](../../docs/investigations/plan_formula.md) before changing
any of it**. **An entry is a building and a location holds one of each**; **a
`province_definition` holds no variables**
([`whole_map_plan.md`](../../docs/investigations/whole_map_plan.md)).

**A preference is an edit, not a term in the objective**: `bag_wtp_edit_*` moves
one building a press, where it costs least, and **the round trip is no undo**
(`docs/TESTLOG.md`). **A press pins its good** — `_lock<n>` — and a freed room
goes to the good furthest below its share; **a pin is a star after the count,
because he asks for symbols, not colours**. `_lock<n>` and `_skip<n>` are
existence flags a slot stores and restores, and **`_edit_locked_<n>` is the
charter's bundle, not the player's pin**. Every rule of the editor, and what
each was paid for:
[`wtp_editor_design.md`](../../docs/investigations/wtp_editor_design.md).

**The editor and both ranking windows print a build stamp** — ask for it before
believing a fix failed. **Five silent window faults, and every rule they left,
are in [`pitfalls/interface.md`](../../docs/pitfalls/interface.md)**: a window
exists only if `scripted_widgets/` names it, a glyph the game never uses may not
be in the font, and a control behind a first click is one he will not find.
`check_script.py` resolves every name a window says **except a widget type**,
and **measures the box against its widest row**.

**Not to be attempted again**: eight, rejected —
[`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md). **The answer
lives on the location**: [`README.md`](README.md). **Built by** `generate.py`,
from `tools/refresh.py`; anything else, `python3 tools/kb.py <words>`.

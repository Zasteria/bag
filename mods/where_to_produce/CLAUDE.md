# `where_to_produce` — brief

## Four functions. Never mix them up.

«Ты постоянно смешиваешь функции плана и редактирования» — его слова.

**The mod page is three tabs and four buttons that only open windows**, every
setting inside the window of its function. **Two rules of his**: **no
descriptions in a window header** — that is the control's tooltip — and
**anything technical belongs on «Техническая»**
([`wtp_menu_rebuild.md`](../../docs/investigations/wtp_menu_rebuild.md)).

| # | what | where | files |
| --- | --- | --- | --- |
| 1 | **Choose the ground** | «Земля» on the mod page, or the map buttons in any window | `_zone_*`, `_region_*` |
| 2 | **One good or right → the best locations for it**, by what local RGOs pay | the ranking window: circles pick it, «Искать локации» runs it | `_score_*`, `_rank_*`, `_pick_*` |
| 3 | **A whole plan for that ground** — every production where it pays | the plan window: the caps and both switches there, «Пересчитать» runs it | `_plan_*` |
| 4 | **Editing that plan afterwards**, one building at a time | the editor window, and only there | `_edit_*` |

**3 and 4 are separate and the traffic runs one way**: nothing the editor holds
is ever read by 3. Crossed once and reverted. **The test: «не нужен», then a
fresh plan — it must be ordinary.**

**Before touching any `_plan_*`:
[`plan_gaps.md`](../../docs/investigations/plan_gaps.md).** **The tick is the
rank and outlives a save.**

## Where it stands

**Never gate the plan on `generate.fed_floor`**; **the bonus counts RGOs only**;
**one method per slot**
([`production_ladder.md`](../../docs/investigations/production_ladder.md)).
**A right's gate is its own `potential`, never `has_advance`**
([`town_rights.md`](../../docs/investigations/town_rights.md)). **An entry is a
building and a location holds one of each**
([`whole_map_plan.md`](../../docs/investigations/whole_map_plan.md)).

**Равномерность держит уровень, а не квота**: круг поднимает `_plan_lvl` на
единицу, товар берёт не больше одного домика за круг, и **полоса выгоды решает
«где», а не «сколько»**; покрытие — это круг 1, открытая лестница — сухой круг
([`plan_as_reservation.md`](../../docs/investigations/plan_as_reservation.md)).
**Локация держит по одной деревне каждого вида** — четыре `is_village = yes`
рядом законны, а две одинаковых нет, и это тот же запрет на повтор здания, что
был всегда ([`plan_gaps.md`](../../docs/investigations/plan_gaps.md)).
**Весов город/село нет и не будет**, и **выхлоп сторону не различает**
([`plan_share_sides.md`](../../docs/investigations/plan_share_sides.md)).
**Правила редактора, доливки и рядов, «Специализация» и сводка по товарам —
все выписаны**:
[`archive/wtp_brief_rules.md`](../../docs/archive/wtp_brief_rules.md). Устройство
редактора — [`wtp_editor_design.md`](../../docs/investigations/wtp_editor_design.md).

**Резервация по стеснённости построена 2026-09-07, в игре не была**: локация
принадлежит самому стеснённому товару своей стороны и на ступенчатых кругах
предлагается только ему, `owt`/`owr` в «Диагностике» — скольким она хозяин
([`plan_reservation.md`](../../docs/investigations/plan_reservation.md)).
**Дальше, порядок его**: её прогон, перетасовка внутри провинции, шаги 7–8.

**The build stamp is on «Техническая»**, before believing a fix failed. **Before
touching any `.gui`, the checklist is
[`pitfalls/windows.md`](../../docs/pitfalls/windows.md)** — every rule in it this
mod paid for, most of them twice.

**Not to be attempted again**: eight, rejected
([`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md)). **The answer
lives on the location.** **Built by** `generate.py`.

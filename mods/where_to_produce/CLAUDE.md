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


**Равномерность держит уровень, а не квота**: круг поднимает `_plan_lvl` на
единицу, товар берёт не больше одного домика за круг, и **полоса выгоды решает
«где», а не «сколько»**; покрытие — это круг 1, открытая лестница — сухой круг
([`plan_as_reservation.md`](../../docs/investigations/plan_as_reservation.md)).
**Весов город/село нет и не будет**, и **выхлоп сторону не различает**
([`plan_share_sides.md`](../../docs/investigations/plan_share_sides.md)).
**Правила редактора, доливки и рядов, «Специализация» и сводка по товарам —
все выписаны**:
[`archive/wtp_brief_rules.md`](../../docs/archive/wtp_brief_rules.md). Устройство
редактора — [`wtp_editor_design.md`](../../docs/investigations/wtp_editor_design.md).

**План ровен, измерено 2026-09-07 — общую раздачу не переделывать**: товар
останавливает **своя квота**, и мера равномерности — `n + rgo` против неё, а не
занятые комнаты; разбор печатает `tools/diag.py`. Снятая по этой мерке
резервация — [`archive/plan_reservation.md`](../../docs/archive/plan_reservation.md).

**Деревня — одно здание на несколько товаров**, и локация держит по одному
каждого вида: отсюда весь ответ про рыбу
([`plan_gaps.md`](../../docs/investigations/plan_gaps.md)). **У такого здания свой
потолок**, равный общей доле и растущий вместе с ней; однотоварные здания его не
имеют — их держит квота товара, и фермерская деревня среди них. Пять таких
зданий, три из них деревни. **Построено 2026-09-07, в игре не было**
([`plan_villages.md`](../../docs/investigations/plan_villages.md)).

**Дальше**: прогон потолка, потом города со своим котлом, перетасовка и шаги 7–8.

**The build stamp is on «Техническая»**, before believing a fix failed. **Before
touching any `.gui`, the checklist is
[`pitfalls/windows.md`](../../docs/pitfalls/windows.md)** — every rule in it this
mod paid for, most of them twice.

**Not to be attempted again**: eight, rejected
([`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md)). **The answer
lives on the location.** **Built by** `generate.py`.

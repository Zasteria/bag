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


**Равномерность держит уровень**: круг поднимает `_plan_lvl` на единицу, товар
берёт один домик за круг **на каждой своей стороне**, полоса решает «где»
([`plan_as_reservation.md`](../../docs/investigations/plan_as_reservation.md)).
**Правила редактора, доливки, рядов, «Специализации» и сводки**:
[`archive/wtp_brief_rules.md`](../../docs/archive/wtp_brief_rules.md),
[`wtp_editor_design.md`](../../docs/investigations/wtp_editor_design.md).
**Мера равномерности — `n + rgo`**, её печатает `tools/diag.py`.

**Деревня — одно здание на несколько товаров**, локация держит по одному каждого
вида, и такое здание идёт по кругу как однотоварное
([`plan_villages.md`](../../docs/investigations/plan_villages.md)).

**Два котла, и всё в них по своей стороне** — уровень, рост доли, комнаты.
«Деревня = товар»: у кого в селе одна деревня, сельской доли нет, в сводке
прочерк. Доля стороны решается вместе со скидкой за РГО, а долю, которую земля
принять не может, **переливает** на другую. Три равенства:
`доля = город + село`, `доля − РГО = потолок города + потолок села`,
`домиков + РГО = доля`
([`plan_rural_pool.md`](../../docs/investigations/plan_rural_pool.md)).

**Раздача принята 2026-09-08** — земля 1380 из 1380, обе стороны полные.
**Перетасовки нет и не будет**: зонд `_diag_shuffle` намерил её потолок в 2.1 %,
из которых 86 % заперты в грамотах
([`plan_gaps.md`](../../docs/investigations/plan_gaps.md)). **Дальше**: шаги 7–8.

**Условие внутри значения ключа локализации ломает клетку.** «19-1» в сводке
делает диспетчер `customizable_localization`, как «почему остановился»;
`SelectLocalization` с вложенным сравнением убил столбец целиком, 2026-09-09.

**The build stamp is on «Техническая»**, before believing a fix failed. **Before
touching any `.gui`, the checklist is
[`pitfalls/windows.md`](../../docs/pitfalls/windows.md)** — every rule in it this
mod paid for, most of them twice.

**Not to be attempted again**: eight, rejected
([`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md)). **The answer
lives on the location.** **Built by** `generate.py`.

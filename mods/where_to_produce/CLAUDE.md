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
| 3 | **A whole plan for that ground** — every production where it pays | the plan window: the caps and **three** switches there, «Пересчитать» runs it | `_plan_*` |
| 4 | **Editing that plan afterwards**, one building at a time | the editor window, and only there | `_edit_*` |

**3 and 4 are separate and the traffic runs one way**: nothing the editor holds
is ever read by 3. Crossed once and reverted. **The test: «не нужен», then a
fresh plan — it must be ordinary.**

**Before touching any `_plan_*`:
[`plan_gaps.md`](../../docs/investigations/plan_gaps.md).** **The tick is the
rank and outlives a save.**

## Where it stands

**Его список после партии — [`wtp_backlog.md`](../../docs/investigations/wtp_backlog.md),
и он открыт.** 1, 2, 3, 5, 8 построены 2026-09-12 и прогона не видели; 4, 6, 7,
9 — нет. **CM и Glorp UI сняты с плейсета**: житница это переживает, **отмашка
автостроя — нет**, ванильная замена ей живёт только в интерфейсе
(`ToggleAutoExpandBuilding`). **«Специализация» — галочка в окне плана**;
**девять провинций и больше — одна грамота на провинцию** (`_plan_grant_step`);
две карты CM перенесены файлом (`bag_wtp_food.txt`).


**Раздача — уровень, два котла, деревня-товар, три равенства** —
[`archive/wtp_brief_plan_rules.md`](../../docs/archive/wtp_brief_plan_rules.md),
закрыто прогоном 2026-09-08. **Редактор, доливка, ряды, «Специализация», сводка**:
[`archive/wtp_brief_rules.md`](../../docs/archive/wtp_brief_rules.md),
[`wtp_editor_design.md`](../../docs/investigations/wtp_editor_design.md).

**Выгода от земли — свойство ПРОВИНЦИИ, а не локации** (`_g<n>` спрашивает
`any_location_in_province_definition`), значит внутри провинции менять нечего;
«Перетасовать» — ручной переезд **между** ними
([`plan_gaps.md`](../../docs/investigations/plan_gaps.md)).

**Всё, что мод делает в чужих окнах** — галочки плана в списке зданий локации,
отмашка на автострой CM, кнопки житницы и «снести лишнее», и чтение зданий чужих
модов генератором — [`wtp_integration.md`](../../docs/investigations/wtp_integration.md).
Три правила оттуда, которые дороже прочих: **`root` в фильтре — не сам объект**;
**`_stands_<здание>` слушается тумблера ранга, поэтому не годится ни для чего,
что делает игра**; **мод ничего не делает периодически** — это его требование.

**The build stamp is on «Техническая»**, before believing a fix failed. **Before
touching any `.gui`, the checklist is
[`pitfalls/windows.md`](../../docs/pitfalls/windows.md)** — every rule in it this
mod paid for, most of them twice.

**Not to be attempted again**: eight, rejected
([`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md)). **The answer
lives on the location.** **Built by** `generate.py`.

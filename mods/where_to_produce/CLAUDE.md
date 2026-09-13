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

**Деревня — сущность, а не товар, и это правило обязано стоять в обоих местах**:
ворота плана выбрасывали её из товара, ворота редактора — нет, и «+1» на дичь
втыкал лесную деревню (2026-09-12). У редактора свой `own_groups`, а три
универсальные деревни стоят своей строкой «+1/−1» под номерами `len(order) + k`.

**3 and 4 are separate and the traffic runs one way**: nothing the editor holds
is ever read by 3. Crossed once and reverted. **The test: «не нужен», then a
fresh plan — it must be ordinary.**

**Before touching any `_plan_*`:
[`plan_gaps.md`](../../docs/investigations/plan_gaps.md).** **The tick is the
rank and outlives a save.**

## Where it stands

**Его список после партии — [`wtp_backlog.md`](../../docs/investigations/wtp_backlog.md),
и он открыт.** 1, 2, 3, 4, 5, 8 построены; 6, 7, 9 — нет, как и **ванильная
отмашка автостроя** (CM снят с плейсета, замена ей живёт только в интерфейсе:
`ToggleAutoExpandBuilding`). **«Специализация» — галочка в окне плана**;
**девять провинций и больше — одна грамота на провинцию** (`_plan_grant_step`);
**житница сама заполняется** тем, что растит еду или РГО, и её кнопка в
редакторе меняет локацию сразу; сводка — две страницы, вторая по грамотам.


**Раздача — уровень, два котла, деревня-товар, три равенства** —
[`archive/wtp_brief_plan_rules.md`](../../docs/archive/wtp_brief_plan_rules.md).
**Редактор, доливка, ряды, «Специализация», сводка** —
[`archive/wtp_brief_rules.md`](../../docs/archive/wtp_brief_rules.md),
[`wtp_editor_design.md`](../../docs/investigations/wtp_editor_design.md).

**Выгода от земли — свойство ПРОВИНЦИИ, а не локации** (`_g<n>`), значит внутри
провинции менять нечего ([`plan_gaps.md`](../../docs/investigations/plan_gaps.md)).

**Всё, что мод делает в чужих окнах** —
[`wtp_integration.md`](../../docs/investigations/wtp_integration.md). Три правила
оттуда дороже прочих: **`root` в фильтре — не сам объект**; **`_stands_<здание>`
слушается тумблера ранга, поэтому не годится ни для чего, что делает игра**;
**мод ничего не делает периодически**.

**The build stamp is on «Техническая»**, before believing a fix failed. **Before
any `.gui`: [`pitfalls/windows.md`](../../docs/pitfalls/windows.md)** — every
rule in it this mod paid for, most twice.

**Not to be attempted again**: eight
([`archive/wtp_not_again.md`](../../docs/archive/wtp_not_again.md)). **The answer
lives on the location.** **Built by** `generate.py`.

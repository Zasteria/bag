# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## The job: `where_to_produce`, побережье ждёт его решения

**`_plan_*` — это
[`investigations/plan_gaps.md`](investigations/plan_gaps.md); порядок шагов и их
цена — [`wtp_practice_plan.md`](investigations/wtp_practice_plan.md); правила
редактора — [`wtp_editor_design.md`](investigations/wtp_editor_design.md).
Больше ничего.**

### Шаги 0–6 закрыты и видены в игре

**Три правила их переживают:** состояние редактора — редакторово, и свежий план
его не читает; работа с `.gui` начинается с
[`pitfalls/windows.md`](pitfalls/windows.md); окно изменений отложено.

### Раздача уровнями, сводка и специализация — построены и приняты

**Круг поднимает уровень на единицу, товар берёт не больше одного домика за
круг**, а внутри круга лестница прежняя: ступени дефицита, пять полос в каждой,
потом всё остальное. Полоса решает «где» и «кто раньше», а не «сколько».
Покрытие стало кругом 1, открытая лестница — сухим кругом, порог на товар исчез;
`_px<side><n>` снимает с обходов товар, которому некуда, `_plan_top` не даёт
сухому кругу убить «Расширить».
[`investigations/plan_as_reservation.md`](investigations/plan_as_reservation.md).

**Сводка** — иконка в окне плана: строка на товар и причина остановки.
**Специализация** — кнопка на странице мода, провинция отдаёт лучшую грамоту всем
городам, ячейка достаётся тому, кто платит больше всех
([`investigations/plan_specialisation.md`](investigations/plan_specialisation.md)).

**Все три прогнаны 2026-09-07 и приняты.** Северная Германия, 416 локаций:
`placed=1384 rooms=1384`, `laps=87` при пределе 150; сумма `nt` = 544 и `nr` =
840 — счёт закрывается до единицы. **Полосы выгоды больше не решают «сколько»**:
`iron` с лучшей выгодой **0** взял 41 место из 43, а все пятнадцать только
городских товаров легли в 16…19 независимо от выгоды. Провинция в специализации
раздаёт грамоту всем своим городам, и средняя по ней считается по-настоящему.

**Побережье оказалось не проблемой.** Рыбу в селе делает только рыбацкая
деревня, и её же делает `naval_supplies`: 42 прибрежных локации, 38 рыбацких
деревень (17 + 21), занято на 90 %. Резервация по стеснённости чинила диагноз,
которого не было; владелец её просил — решать после следующего прогона.

**Закрыто его ответом:** локация держит по одной деревне каждого из четырёх
видов, две одинаковых — нет. Правило мода было верным изначально; выключатель,
построенный на полдня, снят.

**Построено и ждёт прогона:** ступень дефицита считает места **своей стороны**
(`_ngt`/`_ngr`), а не обе разом — `naval_supplies` умеет 178 локаций всего и
потому проходил как массовый товар, имея в сёлах те же 42 места, что рыба. И
сводка: столбец РГО, ровность по сторонам порознь, «мест нет» разделено на «стоит
во всех своих местах» и «его места заняли другие».

**Специализация закрыта как есть.** Добавлять в неё редкость он отказался сам:
«по сути она просто пойдёт догонять условия общего плана» —
[`investigations/plan_specialisation.md`](investigations/plan_specialisation.md).

### The share, and the tiers, as they stand

A good builds while under the **level**, its **total quota** and the **cap of the
side it builds on**; the scarce tiers are a **share of the ground** (2…32 %) with
1/2/4/8/16 as floors, counted **per side** since 2026-09-07. Side quotas alone and
output weights were rejected on numbers
([`investigations/plan_share_sides.md`](investigations/plan_share_sides.md)).

### Then 7 and 8, in that order, and not before

**His order, 2026-09-04: «доработать все начатые функции мода и потом уже
пытаться интегрировать его в функционал CM и glorp».** 7 is the plan shown in
the location panel, inside Glorp UI's own interface. 8 stamps the plan onto
Construction Manager, gated on CM being present — and the space the goods icons
used to hold in the plan rows is the space he is keeping for CM's links.
**A session taking either one re-reads those mods' files** — `python3
tools/refs.py` for the version, grep for the name. He also offered `cheatmenu` and
Advanced Auto Build's interface for `reference/`
([`CONVENTIONS.md`](CONVENTIONS.md)).

**Instrument before the third theory** and **do not spend his run on a guess** —
[`pitfalls/diagnosis.md`](pitfalls/diagnosis.md).

## The job: `mods.bat`, and one run to confirm it

**Both halves are repaired and neither has been run on his machine** — a failed
steamcmd run looked exactly like a successful one
([`archive/mods_bat_repair.md`](archive/mods_bat_repair.md)). **Ask for:**
`mods.bat → 1`, `→ 4`, `mods.bat check`, and the output of all three. Logs go
through `python3 tools/which_build.py <logs folder>` first, as always.

## Then `glorpui_hints` goes out

Nothing outstanding; publishing is five steps in
[`WORKSHOP.md`](WORKSHOP.md#putting-glorpui_hints-out-in-order), the lists are in
[`archive/next_glorpui_publish.md`](archive/next_glorpui_publish.md).

## Also waiting on the owner, all of it cheap

- **`mods.bat → 2` on his machine.** The 2026-08-28 files of Advanced Auto Build
  and Glorp UI are still not in this tree; both generators were fixed against
  rewritten copies. Entry 2 does **not** re-extract the game.
- **The panel-open bisect and the hover run** — protocols written out in
  [`investigations/panel_hitch.md`](investigations/panel_hitch.md) and
  [`investigations/widget_leak.md`](investigations/widget_leak.md), every branch
  with its next step. **Do not design a different test until they have run.**

## Before asking him for anything

Read [`SETTLED.md`](SETTLED.md). And walk the protocol as the person who has to
do it: *"sit on the map and open nothing"* is impossible while events fire, which
is why everything is paused now. He cannot be asked to run a thing twice.

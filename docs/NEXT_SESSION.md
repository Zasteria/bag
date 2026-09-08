# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## Работа: `where_to_produce` — арифметика доли, нужен прогон

**Построено 2026-09-08, в игре не было.** Десятый прогон дал землю 1380 из
1380, а владелец назвал четыре расхождения в числах: «арифметика любит красоту».
Все четыре настоящие и все четыре починены.

1. **Последняя прибавка сухого круга отменяется** — она никому не досталась, а
   доля из-за неё стояла на единицу выше достижимой.
2. **Сухой круг поднимает долю только той стороны, где остались комнаты**
   (`_plan_pt`/`_plan_pr`, в отчёте `filled=`). Городу хватало 19, селу нужно
   было 55; поднимали обе, и городской потолок уходил на 21 при доходе 18.
3. **Проход стеснённых держит квоту**, а «стеснённой стороны» как особого
   случая больше нет: камень ставил `_pq` на каждой стороне — 73 домика при
   квоте 62 и 88 «с РГО» против 75 у всех.
4. **Перелив доли между сторонами**: доля стороны, которую своя земля принять
   не может, уходит на другую (соль: 13 из сельских 55 годятся только в город).
   **И уровень считается по своей стороне** — иначе 42 сельских домика,
   поставленных проходом стеснённых, выбивали соль из городского круга.

Плюс доля берётся на единицу ниже найденной, а сухой круг доводит её до той, на
которой земля заполнилась.

**Просить у него**: «Пересчитать» на северной Германии и «Диагностика».
Ждём: доля город **19**, село **55**, «Доля» три числа 19/55/74; земля 1380 из
1380; `доля город + доля село = доля −РГО` в каждой строке, где земли хватает;
камень 6+53=59 (+15 РГО = 74), соль 13+42=55 (+19 = 74), железо 43 «не хватило
земли». Остаток ±1 у городских товаров — это 528 комнат на 35 товаров нацело
не делятся.

**Что читать про `_plan_*`:**
[`investigations/plan_gaps.md`](investigations/plan_gaps.md) — открытое и
закрытое; [`plan_as_reservation.md`](investigations/plan_as_reservation.md) —
как устроена раздача уровнями; [`wtp_practice_plan.md`](investigations/wtp_practice_plan.md)
— порядок шагов; [`wtp_editor_design.md`](investigations/wtp_editor_design.md) —
правила редактора. Больше ничего.

### Что стоит и работает — шаги 0–6

Земля, ранжирование, план, редактор, слоты, «Расширить», сводка и специализация
— всё видено в игре, 416 локаций и 1380 зданий на 1380 мест; числа в
[`TESTLOG.md`](TESTLOG.md).

**Товар строит, пока он ниже уровня своей стороны, своей общей квоты и потолка
своей стороны**; редкие ступени — доля земли (2…32 %) с полами 1/2/4/8/16.
Отвергнутое — [`plan_share_sides.md`](investigations/plan_share_sides.md).

**Три правила, которые переживают всё:** состояние редактора — редакторово, и
свежий план его не читает; работа с `.gui` начинается с
[`pitfalls/windows.md`](pitfalls/windows.md); локация держит по одной деревне
каждого из четырёх видов, а две одинаковых — нет.

### Порядок работ: 1 — потолок здания, 2 — города, 3 — перетасовка, 4 — шаги 7 и 8

Второй не начинать раньше первого. Один прогон на пункт: «Пересчитать» на
северной Германии и «Диагностика» — этого хватает, чтобы сказать, работает
правка или снимается. **И читать «коротко» целиком**: разбор «кого остановила
квота, кого потолок города, а кому не хватило земли» `tools/diag.py` считает сам,
и он же поймал, что резервацию проверять было незачем.

### Шаги 7 и 8 — чужие моды, и они последние

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

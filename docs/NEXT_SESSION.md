# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## Работа: `where_to_produce` — обособленная сельская раздача, нужен прогон

**Его решение, 2026-09-07: города и сёла считаются отдельно, а в селе деревня
становится единицей сама по себе.** Первая половина построена в тот же день и
**в игре не была**: первый слот каждой сельской локации — деревня, цепочкой
рыбацкая → лесная → фермерская → торговая, до лестницы и зеркалом прохода
грамот; три из четырёх вышли из равного круга, торговая осталась. Правило,
находки из файлов игры и предсказание —
**[`investigations/plan_villages.md`](investigations/plan_villages.md)**.

**Просить у него**: «Пересчитать» на северной Германии и «Диагностика», сравнение
с отчётом того же дня. Ждём: **все 284 сельские локации с деревней в первом
слоте** (новая строка `VILL` печатает разбивку и `none`), **побережье занято
целиком** — 42 вместо 39, **скот упирается в долю**, а не в число хлебных
локаций, обычные сельские домики просядут с 519 до ~450–500.

**Вторая половина — города со своим котлом — не построена и ждёт этого прогона.**
Осторожно: две независимые квоты по сторонам он отменял 2026-09-07 утром
(«товары с дублем будут иметь повышенные лимиты»), и лекарство от этого —
приоритет только-городским товарам — в буквальном виде выносит пиво, сукно и
стекло из городов совсем
([`plan_share_sides.md`](investigations/plan_share_sides.md)).

**Что читать про `_plan_*`:**
[`investigations/plan_gaps.md`](investigations/plan_gaps.md) — открытое и
закрытое; [`plan_as_reservation.md`](investigations/plan_as_reservation.md) —
как устроена раздача уровнями; [`wtp_practice_plan.md`](investigations/wtp_practice_plan.md)
— порядок шагов; [`wtp_editor_design.md`](investigations/wtp_editor_design.md) —
правила редактора. Больше ничего.

### Что стоит и работает — шаги 0–6

Земля, ранжирование, план, редактор, слоты, «Расширить», сводка и специализация
— всё видено в игре. **Раздача уровнями**: круг поднимает уровень на единицу,
товар берёт не больше одного домика за круг, полоса выгоды решает «где», а не
«сколько».

**Три прогона на северной Германии приняли всё это** — 416 локаций, 1380 зданий
на 1380 мест; числа в [`TESTLOG.md`](TESTLOG.md).

**Три правила, которые переживают всё:** состояние редактора — редакторово, и
свежий план его не читает; работа с `.gui` начинается с
[`pitfalls/windows.md`](pitfalls/windows.md); локация держит по одной деревне
каждого из четырёх видов, а две одинаковых — нет.

### Доля и ступени, как они стоят

Товар строит, пока он ниже **уровня**, своей **общей квоты** и **потолка своей
стороны**; редкие ступени — доля земли (2…32 %) с полами 1/2/4/8/16, по сторонам.
Отвергнутое — [`plan_share_sides.md`](investigations/plan_share_sides.md).

### Порядок работ: 1 — деревни, 2 — города, 3 — перетасовка, 4 — шаги 7 и 8

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

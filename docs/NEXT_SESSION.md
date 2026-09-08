# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## Работа: `where_to_produce` — один прогон, и это последнее

**Раздача закрыта прогоном 2026-09-08**, разбор —
[`archive/wtp_brief_plan_rules.md`](archive/wtp_brief_plan_rules.md).
**«Расширить» больше не стирает плановую квоту**: незамороженный товар идёт по
квоте `_plan_set_quota` для всей земли.

**Перетасовка — кнопка в окне редактора, два прохода, переезд между
провинциями** (выгода — свойство провинции, внутри неё менять нечего). Первый
проход — сами грамоты, его порядок: «сначала проработать городские права…, потом
всё остальное и не трогать домики городских прав». Прогон 2026-09-09 напечатал
`rights rounds=3 swaps=3 | button rounds=3 swaps=19`, но в числа он не смотрел —
это лог, а не приёмка. Разбор —
[`investigations/plan_gaps.md`](investigations/plan_gaps.md).

**Шаги 7 и 8 построены и не прогнаны** — галочки плана в списке зданий локации
и автострой через Construction Manager. Устройство обоих, и два правила, которые
дороже прочих (`root` в фильтре — не сам объект; `_stands_<здание>` слушается
тумблера ранга и потому не годится ни для чего, что делает игра), —
[`investigations/wtp_integration.md`](investigations/wtp_integration.md).

**Одно место, где шаг 8 может молча не сработать, и оно измеряется.** Диспетчер
CM висит на том же месячном пульсе и начинает с очистки очередей; порядок листьев
между модами не определён ничем. Встали раньше него — поставленное стирается в
тот же тик, и это неотличимо от «строить нечего». Поэтому строка
`CM ran/armed/staged` в диагностике. `ran=1`, `armed>0`, `staged=0` при том, что
строить есть что, — лист надо переносить.

**Просить один прогон, и он закрывает всё разом:**

1. «Пересчитать» → «Перетасовать» → «Диагностика», и отдельно «Расширить».
   Ждём: домиков ровно столько же, `по сторонам` ровно 528/852, ни один домик
   грамоты не тронут.
2. **Автострой.** Нажать иконку автостроя на одной локации, на одной провинции
   и в шапке; проверить, что иконка загорается и гаснет со второго нажатия.
   Прожать месяц-два и снять диагностику: строка «Автострой CM» должна
   показать `помечено N`, `взято N` и `поставлено в очередь` не ноль, а окно
   очереди CM — предложить именно плановые домики.

**Что читать про `_plan_*`, и больше ничего:**
[`plan_gaps.md`](investigations/plan_gaps.md) — открытое и закрытое;
[`plan_as_reservation.md`](investigations/plan_as_reservation.md) — раздача
уровнями; [`wtp_editor_design.md`](investigations/wtp_editor_design.md) —
правила редактора.

### Что стоит и работает — шаги 0–6

Земля, ранжирование, план, редактор, слоты, «Расширить», сводка и специализация
— всё видено в игре; числа в [`TESTLOG.md`](TESTLOG.md). **Три правила, которые
переживают всё:** состояние редактора — редакторово, и
свежий план его не читает; работа с `.gui` начинается с
[`pitfalls/windows.md`](pitfalls/windows.md); локация держит по одной деревне
каждого из четырёх видов, а две одинаковых — нет.

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

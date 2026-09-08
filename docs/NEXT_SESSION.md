# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## Работа: `where_to_produce` — шаги 7 и 8, и это последнее

**Раздача закрыта прогоном 2026-09-08**: земля 1380 из 1380, обе стороны полные,
доли 19/55/74. Остаток «−1» у восемнадцати городских — остаток от деления 528
комнат на 35 товаров.

**Перетасовка**: кнопка в **окне редактора**, переезд между провинциями. Выгода —
свойство провинции (`any_location_in_province_definition`), внутри неё менять
нечего. Деревня — партнёр обмена, но её выгоду обмен намеренно не спрашивает.
Домики грамот не трогаются вовсе. Разбор —
[`investigations/plan_gaps.md`](investigations/plan_gaps.md).

**«Расширить» больше не стирает плановую квоту**: незамороженный товар идёт по
квоте `_plan_set_quota` для всей земли Z = X + Y.

**Просить один прогон:** «Пересчитать» → «Перетасовать» → «Диагностика», и
отдельно «Расширить». Ждём: домиков ровно столько же, `по сторонам` ровно
528/852, `button swaps` не ноль, обмены с деревнями есть, ни один домик грамоты
не тронут.

**Две работы, которые он назвал и которые не построены:**

1. **Перетасовка грамот, первым проходом.** «Перетасовка должна сначала
   проработать городские права, перетасовать именно их, потом всё остальное».
   Машина переезда грамоты есть (`_edit_right_out` / `_edit_right_need`,
   «+1»/«−1» на грамоте), автоматического прохода нет.
2. **Фильтр в окне строительства Glorp UI** — шаг 7. Окно
   `glorpUI_build_location_lateralview.gui`, 2876 строк, ряд стоит на
   `BuildInLocationLateralView.GetBuildingType`. Фильтр = `visible` на ряде от
   `IsShown` со скоупами локации и типа здания. **Решение, которое надо принять
   первым: перекрывать их файл целиком (ломается на каждом их обновлении) или
   класть своё маленькое окно рядом.**

**Деревни в обмене есть, но грубо, и это его решение**: сельский домик меняется
с деревней по **своей** выгоде, деревня едет туда, где освободилось, и что земля
платит ей самой, не спрашивается. Зонд печатает их выгоду числом `villages=` —
это цена компромисса.

**Что осталось: шаги 7 и 8**, они ниже. Всё остальное видено в игре и принято.

**Ещё одно, не спрошенное:** грамота потолка не спрашивает, и два товара стоят
на единицу выше своего (`dyes`, `wine` — 15 при потолке 14). Он это видел и не
возражал.

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

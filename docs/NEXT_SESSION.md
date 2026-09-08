# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## Работа: `where_to_produce` — один прогон, потом шаг 8, и это последнее

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

**Шаг 7 — галочки в панели зданий локации, чужого окна не потребовалось.**
`gui/filters/bag_wtp_filters.txt`: «Планируемые» (статический список типов) и
«Из плана — сюда» (`_plan_builds` этой локации). Локацию приносит **общая с
`rgo_bonus_filter`** проба `bag_view_location` — иначе последний загруженный мод
унёс бы пробу другого; обе копии побайтово одинаковы, `check_script.py` следит.

**Обе галочки видены в игре 2026-09-09** — вторым прогоном, после того как
первый показал, что **`root` в фильтре не есть отфильтровываемый объект** (та же
ошибка держала неработающей панельную фишку `rgo_bonus_filter`; обе теперь
спрашивают `this = building_type:X` **до** смены скоупа). Разбор —
[`research/interface.md`](research/interface.md#filter-scopes-what-a-trigger-actually-gets).

**Ступень по зубам, а не по плану.** План «на конец» ставит верх лестницы, а
панель недоступное не показывает — строка товара пропадала. Лестницу называет
игра (`obsolete`), «доступна ли ступень» — `can_build_building` в скоупе страны,
и у фильтра страны нет: ответ лежит готовым в `_ba_<здание>`, который считают
«Пересчитать» и `cmf_on_mod_registration`. Фишка пропускает самую высокую
доступную ступень той же лестницы. **Взял продвижение и не пересчитал план —
покажет ступень ниже, чем мог бы; это вся цена.**

**Просить один прогон, и он закрывает всё разом:**

1. «Пересчитать» → «Перетасовать» → «Диагностика», и отдельно «Расширить».
   Ждём: домиков ровно столько же, `по сторонам` ровно 528/852, ни один домик
   грамоты не тронут.
3. Панель производства локации, где план поставил **деревню** и где план «на
   конец» поставил ступень выше доступной: под «Из плана — сюда» должны стоять
   деревня и та ступень лестницы, которую он может построить сейчас.

**Что осталось: шаг 8**, он ниже. Всё остальное построено и ждёт прогона.

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

### Шаг 8 — Construction Manager, и он последний

**His order, 2026-09-04: «доработать все начатые функции мода и потом уже
пытаться интегрировать его в функционал CM и glorp».** 7 is done and waiting on a
run. 8 stamps the plan onto Construction Manager, gated on CM being present — and
the space the goods icons used to hold in the plan rows is the space he is
keeping for CM's links. **A session taking it re-reads CM's files** — `python3
tools/refs.py` for the version, grep for the name.

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

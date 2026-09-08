# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## Работа: `where_to_produce` — один прогон, потом шаг 8, и это последнее

**Раздача закрыта прогоном 2026-09-08**, разбор —
[`archive/wtp_brief_plan_rules.md`](archive/wtp_brief_plan_rules.md).
**«Расширить» больше не стирает плановую квоту**: незамороженный товар идёт по
квоте `_plan_set_quota` для всей земли Z = X + Y.

**Перетасовка — кнопка в окне редактора, и она идёт двумя проходами.** Переезд
**между** провинциями: выгода — свойство провинции
(`any_location_in_province_definition`), внутри неё менять нечего. Первый проход
— сами грамоты, его порядок, 2026-09-09: «сначала проработать городские права,
перетасовать именно их, потом всё остальное и не трогать домики городских прав».
Пара городов меняется грамотами целиком (`_plan_move_right_<k>` →
`_edit_right_swap` с обеих сторон), ни одна не появляется и не исчезает, условие
то же — паре вместе должно стать лучше; числа свои, `_ps_rrounds` /
`_ps_rswaps`. Деревня — партнёр второго прохода, но её выгоду обмен намеренно не
спрашивает, и это его решение. Разбор —
[`investigations/plan_gaps.md`](investigations/plan_gaps.md).

**Шаг 7 построен, и чужого окна не потребовалось.** Панель зданий локации
набирает галочки через `WithFilterTags('building')`, значит хватило
`in_game/gui/filters/bag_wtp_filters.txt`: «Планируемые» (статический список
типов) и «Из плана — сюда» (`_plan_builds` этой локации). Локацию приносит
**общая с `rgo_bonus_filter`** проба `bag_view_location`: оба мода перекрывали бы
одну панель, и последний загруженный унёс бы пробу другого, поэтому проба одна и
обе копии возятся побайтово одинаковыми (`check_script.py` следит). Разбор —
[`research/interface.md`](research/interface.md#list-filters).

**Две галочки, а не одна, нарочно.** «Планируемые» не может не сработать — она
статический список. Видна она и не видна вторая — причина названа без второго
прогона: проба не записала локацию. То же говорит строка `FILTER view_location=`.

**Просить один прогон, и он закрывает всё разом:**

1. «Пересчитать» → «Перетасовать» → «Диагностика». Ждём: домиков ровно столько
   же, `по сторонам` ровно 528/852, в сводке `Кнопка «Перетасовать»` — грамот и
   домиков не ноль, обмены с деревнями есть, ни один домик грамоты не тронут.
2. Отдельно «Расширить».
3. Открыть панель производства любой локации, где план что-то поставил, и
   найти в ряду фильтров две галочки: «Планируемые» и «Из плана — сюда». Вторая
   должна оставить ровно те здания, что план держит в этой локации.

**Что осталось: шаг 8**, он ниже. Всё остальное построено и ждёт прогона.

**Что читать про `_plan_*`, и больше ничего:**
[`plan_gaps.md`](investigations/plan_gaps.md) — открытое и закрытое;
[`plan_as_reservation.md`](investigations/plan_as_reservation.md) — раздача
уровнями; [`wtp_editor_design.md`](investigations/wtp_editor_design.md) —
правила редактора.

### Что стоит и работает — шаги 0–6

Земля, ранжирование, план, редактор, слоты, «Расширить», сводка и специализация
— всё видено в игре; числа в [`TESTLOG.md`](TESTLOG.md). **Товар строит, пока он
ниже уровня своей стороны, своей общей квоты и потолка своей стороны**;
отвергнутое — [`plan_share_sides.md`](investigations/plan_share_sides.md).

**Три правила, которые переживают всё:** состояние редактора — редакторово, и
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

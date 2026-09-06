# Test log

What has actually been in the game, and what it showed.

Only the player can run EU5, so a run is the scarcest thing this repository
consumes. Everything else here — the reference tree, the generators, the
checkers — exists to spend fewer of them. This file is where a run's result
stops being a remark in a chat and becomes something a later session can rely
on.

**A session writes the entry, not the player.** The player says what happened,
in as few words as they like; the session turns it into a row and commits it. If
a run is not written down, `STATUS.md` will keep calling something "untested"
long after it was tested, which is the same cost as not having run it.

## How to fill this in

One entry per run. What matters is the last two columns: what was expected, and
what actually appeared.

- **Date and mod** — and the base mod's version if the run was about a
  translation, from `python3 tools/refs.py`.
- **What was loaded** — the playset order matters for a localization mod, since
  the mod loaded later wins the key.
- **Expected / observed** — the whole point. "Nothing happened" is a result and
  belongs here.
- **`error.log`** — quote the line if there was one. It names the file and the
  line for GUI failures and script errors. An effect that never runs logs
  nothing at all, so "log clean" is itself worth recording: it says the failure
  is the silent kind and the next step is a `cmf_log`, not another guess.

**Do not ask for logs by default.** The owner said so on 2026-08-31 — a zip is
his time and the session's tokens both — and three loads running the answer was
"clean". Ask when something *did nothing* and the reason has to be either a GUI
error or a silent effect, when a crash or a load failure is in play, or when a
`cmf_log` was added for this run. A layout question, a number that looks wrong,
a filter that filters: the screenshot already says it.

## Runs

**2026-09-06, прогон `a69370f2` — три ответа из одной диагностики, и он сам
передал проверку туда.** Его слова: «Смотри сам как что ведёт себя в диагностике.
Я не могу проверить визуально по окну изменений… там нет хронологии изменений…
Так что сам проверяй всё в диагностике.»

**Что диагностика доказала.**

- **Шаг 3 работает.** `EDIT scan fitn=23 cands=9 strict=1` — «+1» выбрал жертву
  строгим проходом, то есть среди тех, кто выше своей доли, а не из всех подряд.
- **Доля редактора считает РГО.** `G2 coal … rgo=3 eq=2` при `quota=5`, и
  `G36 leather … rgo=0 eq=5`. Ровно та арифметика, что и у плана.
- **Перестановка прошла впустую:** `EDIT shuffle rounds=18 swaps=0 gain=0`.
  Против первого прогона (`rounds=68 swaps=19 gain=1971`) это ноль обменов при
  живом проходе. **Причину назвать нечем — значит, не называю.**

**Три правки по этому чтению** (сборка `4b095f`, ни одна не прогнана):

- **Жертву «+1» выбирает превышение, а не цена домика.** Было: из кандидатов
  берётся самый дешёвый домик. Стало: сначала тот товар, что дальше всех выше
  своей доли, цена домика — только при равенстве. Старая форма выселяла один и
  тот же товар подряд, потому что «дешевле всех» не меняется от того, что его
  стало меньше.
- **Четыре счётчика в перестановку**, чтобы `swaps=0` перестал быть немым:
  `pairs` — сколько пар вообще рассмотрено, `same` — в обеих комнатах один товар,
  `nofit` — локация не держит чужой товар, `worse` — обмен ничего не даёт.
  Печатаются строкой `EDIT shuffle … | pairs= same= nofit= worse=`.
- **Журнал нажатий, потому что окно изменений хронологии не держит.** Оно
  сравнивает план с сохранённым: два нажатия по одной локации в нём одна строка.
  Мод теперь пишет `WTP PRESS n= op= good= hit= | done= fail= norefill= |
  esg= evicted=` в `debug.log` **в момент нажатия** — лог хронологичен по
  устройству, помнить ничего не надо. `tools/diag.py` собирает эти строки в
  «Журнал нажатий» перед отчётом, с именем локации и именами товаров.

**Гипотеза про `swaps=0`, и она именно гипотеза:** все локации одной провинции
дают товару одну и ту же оценку, так что пары внутри провинции обменивать
бессмысленно. `same` и `worse` следующего прогона скажут, так ли это.

**2026-09-06 — он нашёл расхождение между планом и редактором, и оно
подтверждается кодом без всякого прогона.** Его слова: «заливке плевать на
сочетание имеющихся домиков и их аналогов в виде РГО… видит, что угля и
прядильных культур 3, а остальных 6, и заливает им по очереди, пока их тоже не
будет по 6, не учитывая, что аналогичных РГО там уже по 3, и счёт для них по
сути 9, а всего остального 6».

**Он прав, и это две строки в двух файлах.** План: `_pq<n> = max(1, доля −
_nrgo<n>)` — РГО вычитается на каждый товар. Редактор: `_esh<n> = _edit_quota −
_pn<n>` — плоская доля на всех, `_nrgo` не упомянут вовсе. То есть план считал
РГО, а заливка редактора — нет, и на его земле разница ровно та, что он описал:
`coal rgo=3`, `fiber_crops rgo=3`.

**Исправлено:** у редактора теперь своя доля на товар, `_eq<n> = max(1,
_edit_quota − _nrgo<n>)`, ровно по арифметике плана и с тем же полом в единицу.
Её читают и недобор заливки, и признак «выше доли» шага 3. `_nrgo<n>` пишется
`_plan_prepare`, то есть до первого плана его нет — чтение защищено
`has_global_variable`.

**И зонд в диагностике: `eq=` в строке `G<n>`**, рядом с `q=` плана и `rgo=`.
Одним взглядом видно, сходятся ли две доли.

**Едва не уехало молча:** `eq` встал семнадцатым числом строки, а scratch-значений
для печати было шестнадцать — `bag_wtp_dg17` не существовало, и строка напечатала
бы пустоту вместо числа, нигде об этом не сказав. Поймано перед сборкой, число
поднято. **Теперь это ловит проверка:** `check_script.py` разрешает каждый
`ScriptValue('...')` в локализации, окнах и `debug_log` против объявленных
значений мода; проверено на подломленном имени.

**2026-09-06, сборка `ae1ed0` — шаг 2а подтверждён числами.** Строка диагностики:
`EDIT shuffle rounds=68 swaps=19 gain=1971` при `GAIN gain_total=101167`. Проход
запускался (68 раундов на ~30 нажатий «−1»), сделал 19 обменов и добавил около
2% общей выгоды, ничего не сломав: 61 нажатие, план по-прежнему 192 здания на
192 места.

**И его наблюдение объясняется конструкцией, а не ошибкой:** «убрал 1 товар с 6
до 1 — 0 изменений… убрал около 4 товаров до 1, и только потом появились
перестановки».

- **После первого «−1» меняться не с чем.** В наборе одна локация, пары нет.
- **Дальше заливка часто кладёт в освободившиеся места один и тот же товар** —
  самый голодный остаётся самым голодным несколько нажатий подряд, и это видно
  в первом отчёте: пять локаций, во всех убран jewelry, а встали coal и
  fiber_crops. Обмен двух локаций с **одинаковым** товаром не меняет ничего, и
  строгое улучшение его правильно не берёт.
- **А там, где недоборы совпали, заливка уже выбрала по выгоде** — это её
  вторая половина правила. Менять остаётся только то, что развела разница
  недоборов, и такие пары появляются, когда набор подрос и товары в нём разные.

**Значит «0 перестановок» на первых нажатиях — правильный ответ, а не молчание.**
Отличить его от «проход не запускался» можно только по `rounds`, ради чего это
число и печатается: 68, а не 0.

**Мелочь, замеченная в том же отчёте и не связанная с шагом:** последнее нажатие
— «−1» по `fruit`, у которого один домик, и обход честно сказал «подходящих 1, с
местом или жертвой 0». Последний домик товара не забирается никогда — так и
задумано.

**2026-09-06, сборки `be43d2` и `0b854a` — меню перестроено, интерфейс принят,
шаг 2 и шаг 2в закрыты.** Три прогона, всё принято его словами: «столбцы встали
как надо», «права встали как надо», «пикер товаров стал более читаемым», «сетка
редактора встала просто отлично». Правило, которое объяснило все три перекоса
сразу, — коробка с запасом места делит его между детьми — в
[`pitfalls/interface.md`](pitfalls/interface.md). Записи целиком:
[`archive/testlog_wtp_menu.md`](archive/testlog_wtp_menu.md).


## Waiting on a run

The next session should start here rather than designing anything new. All of
these are prepared, all are cheap, and the owner has agreed to the hover one.

**`where_to_produce`, twenty-eighth load.** Four small things and one question,
all of it one glance with the results window open. Not worth a run of its own.

1. **Any market can be taken now**, the neighbour's included — the list is every
   market in the world, framed by the ticked continents. Hover a market you hold
   nothing in and it should outline and click like the rest.
2. **The four picker buttons look like «Очистить выбор»** — solid, not
   transparent. Same in the rights window.
3. **The corner above the +/- buttons has a «+» in it** and «№» has not moved.
4. **«Восточная Мунтения» does not touch «Валахия»**, «Трансильвания» does not
   touch its percentage, and the row is four pixels narrower than it was.
5. **The one question: «Из чего».** The header and the row are identical column
   for column in the file, so if the icons still sit right of the heading, the
   cause is a constant inset the rows carry and the header does not. **What
   settles it in one look:** does «Сейчас» sit exactly over its percentages? If
   yes, the drift starts somewhere in the middle and I have the wrong model of
   it; if «Сейчас» is *also* slightly left of its numbers, every heading is, and
   `margin_left` is the one number to move.

**The panel-open bisect — five minutes, no log to read.** Reported 2026-08-25:
any tab opens instantly in vanilla and with a hitch, sometimes a freeze, under
the playset — *on a save loaded a minute ago*, so it is not the widget leak.
Counted from the files already; the candidates and the numbers are in
[`investigations/panel_hitch.md`](investigations/panel_hitch.md).
The playset is 22 workshop mods, 17 of them touching `in_game`
(`python3 tools/playset.py <logs>` reads it out of `debug.log`), so this is a
bisect: same save, same three panels (country, diplomacy, a location's build
panel), halving the `in_game` mods until the hitch is cornered — four or five
loads of a minute each. Worth trying **Construction Manager** and
`rgo_bonus_filter` first, in case they save the bisect. No log, no timing — the
owner's own sense of the hitch is the measurement, because the difference he
describes is one anybody can feel.

Advanced Auto Build was the first version's headline and it was wrong: the owner
does not run it. Its `3781437488` is mounted in the 2026-08-24 log, so if it
turns out to be enabled and merely unused, that still costs — a scripted widget
is instantiated whether it is opened or not.

**The hover test, and the tooltip settings with it.** One session, one save,
paused throughout. Two minutes sweeping the mouse over the map and top bar with
**no clicks**; then Settings → Tooltip Settings with `Map Tooltips` set to
Disabled and both delays at maximum; then the same two minutes again. Send
`performance_degradation.log`. What each outcome means is in
[`investigations/widget_leak.md`](investigations/widget_leak.md) — read it
before asking for anything else, because the losing branch has its own next test
already written and it is not this one repeated.

~~**`ru_loc_fix` round two — eleven keys and four expansions, never in game.**~~
**Confirmed 2026-08-27** from the logs drop above: none of the six keys appears
in `error.log` any more.

**And one thing only eyes can check.** Whether the repaired Russian *reads*
correctly. The log says those keys no longer fail; it does not say the sentences
are right. Quickest look: a religion tooltip (harmony, purity, honor), the goods
filter chips in a location's buildings panel, and the price line in the build
panel.

## Never run

Kept here so it is one list rather than scattered through prose:

- whether anything in `goods_target` runs on a monthly pulse. Its lists,
  readings and ticks are confirmed on screen; nothing periodic is.
- `rgo_bonus_filter`'s build-panel chip.
- ~~**`where_to_produce`'s «В конце» plan.**~~ **Run 2026-09-03**, three times.
  What is still never run is **the whole plan on a large ground since the
  ladders were rebuilt**: Westphalia is 48 locations and its answer came back
  identical to the old build's, so nothing there tests the change. The press
  that would is the one of the earlier report — northern Germany, 233 locations,
  where the open pass used to place 271 buildings of 770.
- Everything `nd_ru` has translated apart from Westphalia — 3 600 keys that have
  never been on screen.

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

**2026-09-06, сборка `52c7f7` — окна закрыты его словами: «Всё, окна починили».**
Пять окон, у каждого своя рамка, содержимое внутри неё. Отдельного разбора он не
давал и не должен: тема тянулась шесть сборок и закончилась одной строкой.
**Что закрылось вместе с ней** — шапка редактора (та самая, «которая не
растягивается»), рамки окна плана, поиска и изменений, и **иконки товаров ушли
из-под иконок домиков** в окне плана и редактора: «Всё хорошо». Место под ними
он держит под ссылки на автостроительство CM — это шаг 8, не мусор.

**Чего этот прогон не проверял:** свёрнутый вид по умолчанию (виден только на
новой игре) и строку нажатий — «я вообще никогда не обращал внимания на подобные
тексто-цифровые строки».

**Правило, ради которого стоило шесть сборок:**
[`pitfalls/windows.md`](pitfalls/windows.md) — один чек-лист, и `CLAUDE.md`
теперь отправляет туда до любой правки `.gui`. Его слова: «меня заебало решать
проблему окон чуть ли не через одну сессию».

**2026-09-06, прогон на `429a60` — рамка редактора встала, и я стёр её из трёх
других окон.** Его слова: «ты сделал рамку в одном окне, а из других трёх
буквально удалил её вообще».

**Причина, и она целиком моя.** Скрипт, переносивший `using =
bg_window_default_alt` на само окно, брал **первую строку `size = {` в файле**.
В окне редактора типы объявлены в отдельном файле, и первой оказалась строка
самого окна — там всё вышло правильно. В четырёх остальных типы лежат выше
`window`, и строка попала внутрь типа: `bag_wtp_chg_goods_entry`,
`bag_wtp_select_footer`, `bag_wtp_right_slot_1`. Окна остались без фона, а
товарная ячейка получила оконную рамку. В окне плана строка попала в
`bag_wtp_plan_goods_entry` — тот самый тип, который я в той же сборке удалил, так
что там рамки не осталось вовсе.

**Правило, которое это ловит, теперь в `check_script.py`:**
`frameless_windows` — каждое `window` обязано нести
`using = bg_window_default_alt`, и **ничто, кроме `window`, не смеет её нести**.
Проверено на живой поломке: убрал строку из окна плана — поймал; вернул — чисто.

**Ещё одна ловушка внутри самой проверки:** делить тело окна «до первого
ребёнка» нельзя, `size = { 1320 900 }` выглядит ровно как открытие блока.
Проверка сначала дала три ложных срабатывания и была переписана на поиск строки
по её собственному отступу.

**2026-09-06, прогон на `5bcea8` — грамоты встали, и он наконец описал шапку так,
что её стало видно.**

**Его слова, и это первое верное описание за шесть попыток:** «рамка всего окна
вместе с шапкой не увеличивается, а содержимое и "лист" внутри окна выходит за
пределы рамки в правую сторону». Он специально снял скриншот шире окна: рамка
идёт по низу и обрывается справа, уходя за лист вверх к краю шапки.

**Измерено, и он прав:** окно редактора объявляет **1500**, а самый широкий ряд в
нём — **1544**. Это строка слотов, которой я в прошлой сборке добавил две кнопки.
Слоты сужены 330 → 300 (подпись 160 → 130), ряд стал 1454.

**И проверка, которая должна была это поймать, была повёрнута не в ту сторону.**
`overflowing_windows` разрешал ряду быть **шире** коробки на 60 «под поля» —
поэтому 1544 при 1500 прошли молча. Поля и полоса прокрутки отнимают ширину у
ряда, а не добавляют: теперь ряду разрешено `ширина − 40`. Проверено: до правки
ловит, после — чисто, и остальные четыре окна тоже в пределах.

**Иконки в строках плана двоились**, и он попросил убрать товарные, оставив
домики: «по домику и так ясно, что это за товар». Две строки по 20 в ячейке 42 не
пересекались по числам, а `autoresize = yes` внутри них — пересекались на экране.
Убраны из окна плана и редактора (строка у них одна), поиск по одному товару не
тронут. Освободившееся место он просил под ссылки на автостроительство CM — шаг 8.

**Грамоты по местам приняты:** «встали хорошо».

**2026-09-06, прогоны `dba516` и `00e5a2` — шаг 4 собран и принят: «выглядит
очень хорошо».** Провинции сворачиваются в обоих окнах плана, сортируются внутри
своих областей (обход внутри обхода, не упаковка ключей), свёрнутый вид включён
по умолчанию. Там же нашлись два молчаливых дубля script value и родилась
проверка на них. Записи целиком:
[`archive/testlog_wtp_provinces.md`](archive/testlog_wtp_provinces.md).

**2026-09-06, сборка `e00483` — шаг 5 закрыт, окно изменений отложено им самим.**
Прогона диагностики он не присылал и сказал, что она не нужна: «связка приезжает
целиком — всё хорошо», «строка нажатия — всё хорошо». Грамота из одного домика,
уступающая место связке из двух-трёх, была тем самым случаем, который терял домик
молча, и он больше не теряет.

**«Окно изменений задвигаем в дальний ящик»** — его слова: правок оно требует
много, а функциональности несёт мало. Грамоты в нём показываются, огрехи
остались, и **браться за них незачем, пока он не попросит**.

**2026-09-06, прогоны `6f094f0a` и `e170d103` — грамоты в редакторе, от «не
работает ни одна кнопка» до рабочего переезда.** Две ошибки, обе от чужой машины
плана: `_plan_right_fits_<k>` требует свободную комнату (ложно в готовом плане
всегда), и `_edit_place_town_<n>` отказывает на полном городе, так что связка
больше уходящей теряла домик молча. Оба правила — в
[`PITFALLS.md`](PITFALLS.md). Записи целиком:
[`archive/testlog_wtp_charters.md`](archive/testlog_wtp_charters.md).

**2026-09-06, прогоны `83ea98a6` и `23a56b9e` — журнал нажатий доехал, шаги 2а и
3 закрыты счётчиками.** Десять «+1» по одному товару выселили десять разных, а
`swaps=0` перестановки оказался ответом, а не поломкой: `pairs=23270 same=685
nofit=8844 worse=13730`. Оттуда же правило **разница — не журнал, хронологию
держит только лог** ([`pitfalls/diagnosis.md`](pitfalls/diagnosis.md)). Записи
целиком: [`archive/testlog_wtp_journal.md`](archive/testlog_wtp_journal.md).

**2026-09-06, прогоны `a69370f2` и сборка `ae1ed0` — доля редактора научилась
считать РГО, шаг 2а подтверждён числами.** Его находка: план вычитал РГО из доли
товара, а заливка редактора — нет. Починено (`_eq<n>`), зонд `eq=` в строке
`G<n>`, и `check_script.py` с тех пор разрешает каждый `ScriptValue`. Записи
целиком: [`archive/testlog_wtp_rgo.md`](archive/testlog_wtp_rgo.md).


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

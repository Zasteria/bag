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

**2026-09-08, третья сборка дня — я сломал раздачу, и прогон это поймал.**
Земля заполнена на **79 %** (1087 домиков из 1380, 373 локации из 416) вместо
ста, кругов 73, ни один товар не добрал своей квоты: глина 37 при квоте 39,
уголь 48 при 49.

**Причина названа числом, а не догадкой.** `_plan_set_caps`, вынесенный ради
пересчёта потолков, пересчитывал вместе с ними и **сами три растущих числа** —
`_qcapt` и `_qcapr` из «комнаты ÷ товары». Сухой круг прибавлял им единицу, а
следующий же вызов её стирал: потолки сторон замерли на **15 и 37** при квоте
**55**, и товар с квотой 49 упирался в 9+37. `qt=`/`qr=`, добавленные накануне,
показали это с первой строки — уголь `q=49 nt=10 qt=9 nr=38 qr=37`.
**Пересчёт, сбрасывающий то, ради чего его зовут.** Исправлено тем же днём: три
числа считает `_plan_set_quota`, растит сухой круг, а `_plan_set_caps` их только
читает.

**Что осталось непроверенным из-за этого:** железо (13+26=39 при своих 43
локациях) и признак стеснённости — их `qt=qr=44`, то есть правило отработало, но
судить о нём на вставшей раздаче нельзя.

**И один настоящий ответ, который прогон всё же дал.** Красители стоят на 15 при
потолке 10 — это **грамоты**: `royal_book_rights` выдана 15 городам и несёт
(books, dyes, paper), а грамота ставится до лестницы и потолком не гасится
(«Оно БУДЕТ выдано ОБЯЗАТЕЛЬНО», 2026-09-01). Скидка за РГО у товара, попавшего
в грамоту, не действует вовсе.

**2026-09-08, сборка со скидкой «сначала город» — правило работает, и оно же
сломало железо.** Северная Германия, 1380 из 1380, кругов больше, доля выросла
до **71**.

**Что сработало ровно как задумано:** глина 11 городов → **3**, волокно → 3
(и те три — грамоты, их потолок стал нулём), `medicaments` 17 → **13**, то есть
20 всего вместо 24 и вровень с `dyes` 20. Городские товары легли в **19…20**.

**И вторая поломка, которую нашёл его вопрос «с какого перепуга прядильные
остались на 3, а не на 0».** Ни с какого: **сухой круг прибавлял единицу каждому
потолку по отдельности, и скидка за РГО в этих прибавках растворялась.** У
прядильных 21 своё РГО, городской потолок на старте `15 − 21 = 0` — а к концу,
после 35 сухих кругов, **35**. Ноль держал их ровно до первого сухого круга.
Грамоты тут ни при чём: прядильных нет ни в одной из тринадцати. Теперь сухой
круг поднимает **три числа** — общую долю и две доли сторон — и выводит потолки
заново, так что скидка держит всю раздачу.

**Что сломалось: железо.** Городская доля 20, своих РГО 11 → потолок 9, и оно
взяло **8 городов из 15** при 26 сёлах из 28. Итог **34+11=45** вместо
возможных 43+11=54. Скидка съела ровно те места, которых у железа мало, а
добрать негде: вся его земля — 43 локации при доле 60.

**Правило по итогам:** у товара, чья земля меньше его доли (`_ngt + _ngr <= _pq`),
потолков сторон нет вовсе — делить ему нечего. Для `medicaments` признак ложен
(132 городских локации против доли 64) и скидка там работает; для железа, рыбы и
соли — истинен. Построено в тот же день.

**И его же наблюдение, которое стоило этого прогона:** «проблема реально в том,
что я не вижу потолка». Потолок растёт с каждым сухим кругом, единого числа на
всех нет — теперь `qt=`/`qr=` печатаются в строке каждого товара, а «коротко»
даёт их разброс.

**2026-09-08, сборка `bc9c39` — потолок общего здания сработал, и новые поля
назвали причину потери скидки за РГО.** Северная Германия, те же 416 локаций и
1380 зданий на 1380 мест, кругов 109 против 87.

**Деревень 215 вместо 333.** `market_village` 71 при потолке 73,
`forest_village` 70, `fishing_village` 39 — первые две упёрлись, третью держит
побережье. Освободившиеся комнаты ушли обычным домикам, и уровень поднялся с
60–65 до **71–72**: `beer` 72, `clay` 55+16=71, `coal` 65+6=71. `stone` 52+15=67
(было 60), `salt` 37+19=56 (было 53), `livestock` 35+40=75.

**`rgot`/`rgor` подтвердили гипотезу до последней цифры.** `medicaments`:
`rgot=1 rgor=6` — из семи её РГО в городе стоит одно, а строить она умеет
только в городе, так что шесть скидок срезали сельский потолок, которым она не
пользуется. Отсюда 17+7=24 против 17+0=17 у `incense` при одинаковых 132
городских локациях. `dyes` с `rgot=3` встала на 15 — ровно на три ниже. **Дыра
была ровно там, где сказано, и делением по стороне.**

**Его правило по итогам, 2026-09-08**: скидка за РГО срезает **сначала городской
потолок**, остаток — сельский. «В городах мне не будет тыкаться глина, пока РГО
хватает для этого перевеса»: у глины `rgot=6 rgor=10`, 16 РГО и 11 городов из 70
при 150 сельских местах. Построено в тот же день.

**2026-09-07, сборка `aff13a` — резервация по стеснённости сработала на полную и
не дала ничего.** 12 товаров держали 458 локаций, `stone` владел всеми 53
своими сёлами — и не сдвинулось ничего, `salt` потерял два. Правило снято тем же
днём. Прогон вместо этого закрыл сам вопрос: девятнадцать товаров кончают
вплотную к своей квоте и стоят, считая РГО, на 60–65, то есть **план уже был
ровен**, а посылка резервации считала неиспользованные комнаты вместо
достигнутого уровня. Ниже уровня только `salt` 53, `iron` 51, `fish` 39 и
`naval_supplies` 38 — всем четверым не хватает земли. Разбор целиком:
[`archive/plan_reservation.md`](archive/plan_reservation.md).

**Срез «дефицитные получают всё?»:** `iron` берёт все 28 своих сельских локаций —
ступени работают; недобирают `stone` (34 из 53) и `salt` (29 из 42), у обоих
стартовая квота урезана своими же РГО.

**2026-09-06 и 09-07, шесть прогонов до потолка здания** — иконки, две земли,
«Расширить» с нулём сдвига на старой земле, первый замер выхлопа, специализация
на Вестфалии и трёхклассовая доля. Записи целиком в
[`archive/testlog_wtp_editor.md`](archive/testlog_wtp_editor.md).

**2026-09-07, два прогона на северной Германии — раздача уровнями принята.**
416 локаций, 1380–1384 здания на столько же мест, кругов 87 и 89. Полосы выгоды
перестали решать «сколько» (`iron` с выгодой 0 взял 41 место из 43); ступень по
сторонам стоила нуля и дала ноль. Записи целиком в
[`archive/testlog_wtp_northern_germany.md`](archive/testlog_wtp_northern_germany.md).

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

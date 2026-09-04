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

**2026-09-05 (вечер) — `where_to_produce`, шаг 2: доля работает, флажок — нет.**
192 нажатия, диагностика, скриншот.

- **Доля живая, и зонд назвал её с первого раза.** `EDIT share quota=3 free=19
  pool_rooms=66 | rooms=192 plan_quota=5`: 16 товаров из 35 закреплены и держат
  126 мест, остальные 19 делят 66 по 3. Виноделие он поднял до 36, инструменты
  до 17, спиртные до 10 — доля остальных упала с 5 до 3 ровно на это. Правило
  «закреплённый съедает комнаты у прочих» подтверждено числами.
- **Заливка по недобору тоже работает.** `walk hit=1 esg=10 esw=0` при «−1»
  инструментов: место занял товар с **выгодой 0**, то есть выигравший по
  недобору, а не по выгоде. Строка нажатия: «−1 Инструменты ← Гэзстенторп —
  место занял Железо».
- **Замок подтверждён его же тестом.** Опустил травы до 1, затем суд. материалы
  до 1 — травы в комнаты материалов не полезли. Его чтение верное: закреплённый
  товар в лотерее не участвует.

**Три находки, все настоящие.**

1. **Галочка «не нужен» рисовалась пустым квадратом.** `✔` в шрифте игры нет —
   и **в её собственной локализации нет ни одного такого символа**, так что
   подобрать другой значило бы снова угадывать. Заменено на `checkbutton_round_alt`,
   собственный чекбокс игры: оба состояния из текстуры, состояние из `down`.
2. **«Флажок ничего не менял на деле», и он прав дважды.** План его не читал
   вовсе — следующий же пересчёт возвращал товару полную долю, то есть ровно
   «кликать их в минус при каждом добавлении земли», против чего флажок и
   заведён. И «+1» по помеченному товару спокойно растил его дальше.
3. **Секция товаров нечитаема:** «липнут друг к другу», «на каждой строке разное
   количество», «должны быть ровненькими по столбикам». Причина —
   `ignoreinvisible = yes`: 35 товаров из 47 давали пять рваных строк разной
   длины по центру.

**И один тест был поставлен мной неверно.** Пункт 3 просил смотреть, кому уйдёт
место при «+1» — а «+1» отдаёт место тому товару, на котором нажали; по недобору
раздаётся только место, освобождённое «−1». Его «я не понимаю» было правильной
реакцией на неправильную формулировку.


**2026-09-05 — `where_to_produce`, шаг 1 подтверждён целиком: строка нажатия и
ширина окон.** Три нажатия по протоколу плюс то, чего не просили.

- **Ожидалось:** «+1» в свободное место, «+1» с вытеснением и «−1» дают три
  разные строки, каждая называет товар, локацию и того, кто ушёл или встал.
- **Наблюдалось:** все три. Его слова: «читабельно что ушло, что появилось»,
  «мод сказал, что места нет, всё верно», «показал что встало вместо нужного
  товара». **И окно изменений сходится со строкой** — два независимых читателя
  одного плана согласны, чего до сих пор никто не проверял.
- **Окна:** «выглядят аккуратно и верхняя плашка всегда нужной длины». Замер
  оказался верным: 1640 / 1260 / 1240 против строк 1524 / 1144 / 1124, и
  `allow_outside` правильно было оставить.
- Логи не запрашивались: всё сделало видимое.

**И одно наблюдение сверх протокола — тест шага 2, поставленный им досрочно.**
Он опустил «−1» несколько товаров до одного домика подряд, и **ни один из них не
занял освободившиеся места других**. Это тот самый случай, который правило доли
из шага 2 должно чинить, и здесь он прошёл сам.

**И это не «шаг 2 не нужен» — это его исходная точка, которую шаг 2 обязан не
сломать.** Заливка сейчас идёт **по выгоде**: у товара, только что опущенного до
1, никакого особого права на освободившуюся комнату нет, поэтому он и не
полез — ровно то, что он увидел. Шаг 2 меняет заливку **на недобор**, и под
одним этим правилом опущенный до 1 товар становится самым голодным и **полезет
первым** — это в точности та регрессия, которую он сам нашёл раньше
(`wtp_editor_design.md`: суд. материалы с 7 до 1, потом травы с 8 до 1, и
материалы залезли обратно в комнаты трав). `_lock<n>` существует именно против
неё.

**Отсюда приёмка шага 2:** повторить этот же его тест после сборки. Если
опущенные руками товары начали занимать чужие освободившиеся комнаты — замок не
читается, и это регрессия против прогона 2026-09-05, а не новое поведение.

**2026-09-04 (вечер) — `where_to_produce`, «+1»/«−1» РАБОТАЮТ.** Его слова:
«механизм добавления/удаления лимита товарных домиков… я проверил и он
работает». Это закрывает единственное, ради чего редактор существовал и что не
было подтверждено ни разу.

- **Ожидалось:** нажатие меняет план — строка с `ушло:` и `встало:`.
- **Наблюдалось:** меняет. Правка доходит до плана.
- **И одно наблюдение сверх ожидаемого, его же:** «+1» товару X вытесняет
  товар Y, но «−1» тому же X отдаёт место товару Z, а не Y. **Это не сбой, это
  прямое следствие двух правил** (разбор — ниже, в этом же файле не повторяется;
  см. `investigations/plan_gaps.md`): «+1» выбирает локацию по разнице
  «X минус жертва», «−1» — по абсолютной слабости X, поэтому это разные
  локации; и жертва выбиралась как **минимум среди стоящих**, а заливка берёт
  **максимум среди подходящих**, то есть противоположный вопрос.
  **Следствие, которое важнее самого вопроса: «+1» и «−1» — не отмена друг
  друга.** Круг «+1 X, затем −1 X» оставляет X при своих, Y на один меньше,
  Z на один больше. Отмены у редактора нет — только загрузка слота.
- Логи не запрашивались: нажатие сделало видимое, это не тихий отказ.

**2026-09-04 — `where_to_produce`, отчёт назвал причину с первой попытки.**
40 нажатий, диагностика.

- **Строки `WTP EDIT` окупились сразу.** `evicted=1 room=1 | placed_before=191
  placed_after=192` при `done=0 fail=1`: выселение прошло, место было, поставить
  не удалось, жертву вернули. Всё это без единой догадки.
- **Причина: `_edit_good` был переменной страны, а читался в области локации.**
  `bag_wtp_edit_add` читает его дважды — сверху, где область это страна (и там
  всё работало: `fitn=42 cands=42`), и внутри `ordered_in_global_list`, где
  область это **локация**. `var:` там спрашивает у локации переменную, которой у
  неё нет, поэтому `add_dispatch` не совпадал никогда. То же самое в
  `drop_dispatch` и в исключении товара из заливки — **все три внутри обхода**.
  Отсюда: «+1» выселяет и возвращает, «−1» говорит «сделано» и не делает ничего.
  Одна ошибка на три сборки.
- **Исправлено: `_edit_good` — глобальная.** Число, которое редактор несёт через
  области, глобальное, без исключений.
- **`check_script.py` теперь ловит этот класс**: имя, которое пишут только
  `set_global_variable`, а читают голым `var:` (и наоборот). Проверено поломкой
  нарочно.
- **Отдельно из этого же отчёта, на его вопрос про 64%:** земля кормит 123 здания
  из 192. Это не алгоритм — это Вестфалия. РГО тут есть только у 11 товаров
  (`livestock 6, wool 6, coal/fiber_crops/salt/stone 3, clay/iron/lumber/sand 2,
  fish 1`), а план обязан поставить 35 товаров. У 24 из них `rgo=0`, и на этой
  земле их рецепты не может накормить ничто. 80–95% были у поиска **одного**
  товара, где верхние строки списка по определению накормлены.

**The three runs that found the editor's silent faults** — buildings placed
over the cap with nothing evicted, the presses that arrived and named two bugs,
and the window that opened with no controls in it — are in
[`archive/testlog_wtp_editor.md`](archive/testlog_wtp_editor.md). All five
faults are fixed and confirmed; the numbers under
[`pitfalls/interface.md`](pitfalls/interface.md)'s table are there.

**Older `where_to_produce` runs — the window that first opened, the first
levelling press, the relative ladder,
the large ground, the gain fix, the charter worth 90, the specialised provinces,
the thirteen-zero probe, the level rights and the roll-back to the thirty-eighth
load — are in
[`archive/testlog_wtp_plan.md`](archive/testlog_wtp_plan.md).** Superseded by the
runs above; kept because what they measured about the game stands.

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

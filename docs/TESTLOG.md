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

**2026-09-04 — `where_to_produce`, правка ставит домики сверх лимита и ничего не
убирает.** 49 нажатий, диагностика и два скриншота.

- **Сверх лимита.** 219 зданий вместо 192, Фризойте — 18 при `cap_urban=4`.
  В списке изменений четыре локации, у всех «ушло: пусто» и длинный «встало».
  **Ни одного выселения за 49 нажатий.**
- **Причину назвать нечем.** Обход выселяет при `_esg > 0` и полной локации, а
  ставит только при `_edit_room = 1`, то есть `load < cap`. Оба условия читают те
  же переменные, что и план, который сам ровно 192 и не переполняет. Прочитано
  всё: `_edit_worst`, `_edit_scan`, `_edit_place`, `_plan_is_town`, `_plan_can`.
  Расхождения в тексте нет.
- **Поэтому — измерение, и он попросил его сам**: «Добавляй скан информации для
  себя в диагностике на функцию редактора». В отчёте три строки `WTP EDIT`:
  что нажали, что нашёл скан, и что обход увидел там, где встал — `hit`, `town`,
  `load`, `esg`, `esw`, `evicted`, `room`, `placed` до и после, оба лимита.
  Числа локации паркуются в глобальные прямо в обходе: `debug_log` не достаёт до
  элемента, на котором стоит walk. `tools/diag.py` печатает их в «коротко».
- **И предохранитель: `_edit_place_*` снова спрашивает лимит.** Причина не в
  том, что я знаю ответ, а в том, что **постановка, которая не умеет сказать
  «нет», портит план**. Теперь она откажет, а отчёт скажет, кто из двух ошибся.
- **Замок грамот вернулся, по его второму слову.** «Я бы предпочёл не забирать
  домики по частям у городских прав. Я бы скорее предпочёл забирать у города
  целиком всю связку право+его домики.» Целая связка — то, что надо строить;
  до тех пор домики грамоты не трогаются.

**2026-09-04 — `where_to_produce`, нажатия дошли, и это назвало два бага.**
Вестфалия, план сохранён в слот 1.

- **Счётчик и подписи сработали как задумано.** Железо → «стоит уже везде, где
  эта земля умеет» (верно: `ng=4 n=4`). Текстиль → **«поставить не удалось, и всё
  осталось как было»** — то есть нажатие дошло, место освободилось, постановка
  отказала. Это та самая ветка, ради которой она делалась.
- **Баг 1: скан и постановка спрашивали разное.** Скан выбирал локацию по
  `_edit_fits_*` (без комнаты), а ставил `_plan_try_*` через `_plan_can_*`,
  который комнату требует. Два предиката вместо одного — и в день, когда они
  разошлись, окно не могло сказать почему. **Теперь предикат один**:
  `_edit_place_*` — то же самое размещение под `_edit_fits_*`, а комнату
  освобождает и проверяет сам обход.
- **Баг 2: «−1» отдавала место обратно тому же товару.** Он в заливке подходит по
  построению — только что там стоял — и почти всегда лучший. Отсюда «нажатие
  сделано» и ноль изменений. Заливка теперь его исключает.
- **Замок грамот снят, по его слову.** «В том числе городские права и их домики —
  не должны быть жёстко зарезервированы в этот момент.» Это была моя выдумка, и
  она стоила дорого: грамота есть у каждого города и запирала 2–3 из 4 домиков,
  так что у «+1» была одна-две законные жертвы на город. **У редактора осталось
  ровно одно своё правило** — последний домик товара на земле не забирается.
- **Не сделано и названо: «+1»/«−1» для городских прав.** Грамота сажает свою
  связку через ту же машину размещения, которая до этой сборки отказывала, — её
  надо увидеть работающей раньше.

**2026-09-03 — `where_to_produce`, окно открылось и оказалось без органов
управления; выкачка файлов ничего не изменила, и это был верный ответ.**

- **В редакторе не было кнопок, потому что они появлялись только после клика по
  иконке.** Владелец: «там только их иконки и ничего больше… никаких кнопочек +1
  или -1». Второй список убран целиком: «−1» и «+1» теперь стоят у каждого товара
  в самом списке. Плюс на экране появилась третья ветка «последнего нажатия» —
  «товар не дошёл до эффекта», чтобы сломанная кнопка больше никогда не читалась
  как отказ правила.
- **Порядок домиков в строке снова не тот, но в другую сторону.** Канонический
  порядок по номеру товара разбил привычную группировку: связка грамоты стояла
  первой, теперь перемешана. «Красота опять попортилась, но уже в другом месте.»
  Теперь первыми идут товары связки той грамоты, что выдана этому городу, потом
  остальные по номеру.
- **`git ls-files reference/game/in_game/gui` = 408, и выкачка скопировала ровно
  408.** GitHub Desktop сказал «нет изменений» и был прав: `in_game/gui` лежал в
  репозитории целиком с самого начала. **Моя прошлая фраза «его не просил
  манифест» была неверной** — папка была, просто попала туда не через манифест. И
  `gui/scripted_widgets/` там нет и быть не могло: у ванили такой папки нет
  вообще, это механизм только для модов.
- **Инструмент теперь считает не скопированное, а изменённое.** «1098 файлов»
  ничего не говорило; теперь «1085 файлов, 0 из них новых или изменённых» и
  прямая строка о том, что коммитить нечего и это ответ, а не сбой. Проверено
  двумя прогонами подряд.

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

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

**2026-09-04 — `where_to_produce`, сборка без карт вовсе уронила игру на загрузке.
Откачено.** Его слова: «даже не загружается сохранение и так же не начинается
новая игра». Логи присланы.

- **Это четвёртый краш подряд, и он хуже трёх прошлых**: те убивали игру при
  открытии редактора, этот — раньше, до того как в игру вообще можно войти.
- **Что говорят логи: ничего.** `error.log` и `gui.log` доходят до `09:53:03` и
  показывают отрисовку игрового интерфейса (шапка страны, левая панель) — то
  есть игра дошла до карты и умерла там. Ни одной строки про `bag_wtp` кроме
  давно известного шума. `gui.log` про окно мода не пишет вообще — файл разобран
  без ошибок. `debug.log` обрывается на `ClearAndRecalculateCachedData`.
- **Проверено оффлайн, всё сходится**: 102 вызванных scripted GUI существуют,
  165 ключей локализации есть в обоих языках, 84 script value определены, скобки
  сбалансированы, `check_script`, `check_cmm`, `check_docs` чисты. Ни одного
  висячего имени. Причину назвать нечем.
- **Что это на самом деле закрыло: карта переменных была не при чём.** Четыре
  сборки, четыре разных механизма доставки числа в окно, четыре краша. Общее у
  них одно — **число товара, попадающее в интерфейс**. Значит следующий заход не
  «ещё один мостик», а окно **без числа вообще**.
- **Откачено до `a55e14b`** — последней сборки, которая и грузится, и открывает
  редактор. Сама сборка со счётчиком цела в истории: `92a8af4`.

**2026-09-04 — `where_to_produce`, сборка на флагах тоже уронила игру. Откачено.**
Его слова: «Не важно. Вылетает и с галочкой и без галочки.»

- **Предохранитель не спасает.** Тумблер выключен — краш тот же. Причина:
  **`And(...)` в выражении интерфейса вычисляется целиком**, не по короткой
  схеме, так что `visible` не защищает то, что оно проверяет.
- **Логи снова пусты** — ни `error.log`, ни `gui.log` ничего не пишут.
- **Причину назвать нечем, и третьего захода не будет.** Карты переменных из
  мода убраны совсем.

**2026-09-04 — `where_to_produce`, у каждого товара в редакторе появилось его
число.** Не прогон, а следствие прошлого: владелец согласился, что железу
действительно некуда встать, и попросил видеть это **до** нажатия — «я должен
видеть текущее число лимита домиков… цвет красным/зелёным… при наведении на
красное — по каким конкретно причинам».

- **Число берётся из карты, потому что строка датамодели несёт scope, а счётчики
  плана пронумерованы.** `_pn<n>` не индексируется товаром; глобальная карта
  `add_to_global_variable_map = { name key value }` — мост между ними, и это
  механизм CMF, который она сама читает как
  `GetVariableFromGlobalVariableMap(name, Scope).GetValue`.
- **Причина считается точно, а не приблизительно.** `_edit_worst` — свойство
  локации, а не добавляемого товара, так что весь ответ стоит один проход по
  локациям плюс по одному `any` на товар: столько же, сколько одно «+1».
  0 — можно; 1 — товар уже стоит везде, где земля умеет его делать; 2 — места
  есть, но все заняты тем, что нельзя трогать.
- **Не проверено в игре:** цвет. `§G…§!` в этом моде работает в подсказках, а в
  обычном `text_single` вне кнопки — ни разу не рисовался. Если вместо цвета
  появится `§G4§!` буквами, красить надо иначе; само число при этом будет верным.

**2026-09-04 — `where_to_produce`, список товаров нарисовался, и отказ «+1»
оказался землёй, а не правилом.**

- **Список заполнился — «35 шт.» на экране**, и число сразу сняло вопрос: было бы
  «0», чинили бы наполнение. Строил его `scrollbox` + `vbox`, по строке на товар с
  названием справа — **и это заняло полокна**. Владелец: «Иконки достаточно…
  На 1 строку поместится таких наборов штук 5-10.» Переделано в `flowcontainer`
  с `wrap_count = 10`: ячейка `−1 [иконка] +1` шириной 104, 35 товаров в четыре
  строки вместо тридцати пяти.
- **«+1» на железе не сработало, и правила тут ни при чём.** `ng=4` — железо
  умеют делать **четыре** локации Вестфалии, и `n=4` — во всех четырёх оно уже
  стоит. `_edit_fits_town_10` требует, чтобы товара в локации ещё не было, так
  что кандидатов ноль. Пятому домику негде встать.
- **Проверено, что редактор не тащит правила плана.** В
  `bag_wtp_generated_editor.txt` нет ни одной ссылки на `_pq<n>` — квота плана в
  редактор не заходит вовсе. Ограничений ровно два, оба согласованные: последний
  домик товара и домик из связки грамоты.
- **Сообщение было виновато, а не механизм.** «Не дало правило, либо товару негде
  встать» — это два разных ответа в одной строке, и владелец прочитал первый.
  Теперь их шесть, каждый называет причину: некуда; есть куда, но подвинуть
  некого; последний домик; все домики из грамот; кнопка не донесла товар;
  сделано.

**2026-09-04 — `where_to_produce`, доля выровняла план, а список товаров в
редакторе пропал.** Вестфалия / Мюнстер, с логами.

- **Доля работает.** `quota=5`, и в «коротко» **на товар от 3 до 6 зданий,
  посередине 6** — вместо 1..9. Железо 4, вина больше не девять. Это ровно то,
  чего он добивался.
- **Владелец прислал старую `diagnostics.txt`** (`quota=2`, `mods.bat -> 8`) —
  забыл собрать новую. Настоящий отчёт нашёлся в `debug.log` из архива логов, и
  он же назвал версию сборки: строка `mods.bat -> «Забрать диагностику из игры»`
  бывает только в новой.
- **Иконок товаров в редакторе нет, и причина не названа.** В логах про
  `bag_wtp_edit_window.gui` нет ни одной ошибки — ни разбора, ни типов, ни в
  `gui.log`. Между сборкой, где иконки были, и этой изменились две вещи сразу:
  контейнер (два `hbox` → `scrollbox` + `vbox`) и тип строки (`widget` → `hbox`).
  **Обе формы по отдельности рисуются в других окнах этого мода каждый кадр**,
  так что ни одна из них не объясняет пустоту.
- **Теория «`layoutpolicy` рядом с размером» проверена и отвергнута.** Такая пара
  есть в трёх местах в `bag_wtp_result_window.gui` и `bag_wtp_right_window.gui` —
  окнах, которые работают. И у скроллбокса ширина была `-1`, то есть не задана
  вовсе. Строить на этом фикс значило бы потратить прогон на догадку.
- **Вместо догадки — число на экране.** В заголовке списка теперь печатается,
  сколькими товарами он заполнен. Пусто и «0 шт.» — не заполнился; пусто и
  «35 шт.» — заполнился и не рисуется. Это две разные починки, и следующий
  прогон скажет, какая.

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

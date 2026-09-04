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

**2026-09-04 — `where_to_produce`, выборка встала ровно, но ни одно нажатие не
сработало.** Скриншот и диагностика. «Щёлкал и на +1 и на −1, ничего вообще не
менялось.»

- **Раскладка принята.** Пять `hbox` с datamodel — иконки и кнопки на местах.
- **Шесть нажатий «показать изменения» подряд: ноль изменённых локаций.** План
  192/192, `moved=0`. Ни одно нажатие не тронуло план.
- **А окно при этом писало «сделано».** `_edit_done` — глобальная переменная,
  она переживает сохранение, и **`_edit_add` обнуляет её первой строкой**. Раз
  она осталась в единице — **эффект не выполнялся ни разу**. Кнопка не доносит
  нажатие. (Ветка «сделано» стоит в подписи раньше ветки «кнопка не донесла
  товар», поэтому старое значение маскировало правду.)
- **Что до этого было проверено в моде, а что нет.** Строку товаров через
  `hbox` + `datamodel` этот мод рисует с первой сборки — но её ячейка
  (`bag_wtp_result_goods_entry`) это `text_single`, **не кнопка**. Кликабельная
  ячейка внутри `hbox`-datamodel здесь не была проверена ни разу.
- **Земля при этом забита целиком**, и это отдельный факт для «+1»:
  `ROOM towns_with_room=0`, 192 здания на 192 места, у каждого города грамота,
  которая запирает 2–3 из его 4 домиков. Свободных под выселение — один-два на
  город.
- **Собрано в ответ:** выборка из 47 написанных ячеек (не datamodel), у каждой
  своя пара `bag_wtp_pick_plus_<n>` без всякого scope, **число домиков рядом с
  иконкой** — то, что он просил трижды, — и **счётчик нажатий в заголовке**.
  Счётчик и есть измерение: не двигается — не работает кнопка, двигается —
  работает, а отказало правило.

**2026-09-04 — `where_to_produce`, редактор открылся. Три находки, две из них
баги правки.** Скриншоты окна и «показать изменения», логи присланы.

- **`flowcontainer` был причиной всех четырёх крашей.** Подтверждено: окно
  открывается. Это закрыто.
- **`fixedgridbox` не крашит, но раскладывает неправильно.** Часть ячеек ушла за
  правый край окна, часть встала под другими. Заменён на пять `hbox` с
  datamodel — ровно та форма, которой этот мод рисует товары в каждой строке
  плана с первой сборки. Ряды режутся в скрипте, окно не переносит ничего.
- **Нажатий было около 15, изменений — два, и оба в минус.** Логи: одна локация,
  `-incense`, `-medicaments`, ни одного `+`. В шапке 190 зданий вместо 192,
  Хорстмар с двумя домиками из четырёх.
- **Причина названа и это две ошибки, а не догадка.**
  1. **Выселение было безусловным.** `_edit_worst` назначает жертву на *каждой*
     локации-кандидате — так нужно `_edit_state` — а обход сносил её всегда,
     включая локации со свободным местом. Скан оценивает свободное место в «не
     стоит ничего», а обход брал за него домик.
  2. **Постановка не проверялась.** Снёс жертву, попробовал поставить, и если
     постановка отказала — домик просто исчезал, а окно писало «сделано».
- **Исправлено:** выселение только когда мест нет; счётчик зданий снимается
  после выселения, и если план не вырос — жертва возвращается на место, а окно
  говорит «поставить не удалось, всё осталось как было». **Потерять домик
  теперь нельзя ни при какой причине отказа.**
- **Чего всё ещё не знаю:** *почему* постановка отказывала. Скан и
  `_plan_can_*` в чём-то расходятся. Новая строка окна назовёт этот случай, если
  он повторится, — тогда причина будет измерена, а не угадана.

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

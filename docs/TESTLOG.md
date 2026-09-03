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

**2026-09-03 — `where_to_produce`, окно редактора открылось, и слоты работают.**
Вестфалия / Мюнстер, скриншот окна.

- **Регистрация в `scripted_widgets` была всей причиной.** Окно открывается,
  слоты видны («Слот 1 · 192 дом. в 48 лок.», «Слот 2 · пусто»), загрузка слота 1
  прошла. Товары земли — иконками двумя строками, сырьё и произведённое.
- **«Последнее нажатие: ничего не изменилось»** — так и должно читаться, пока
  товар не выбран: `_edit_done` стоит нулём с загрузки.
- **Порядок домиков в строке менялся после загрузки слота.** Было «пиво, вино,
  спирт», стало «спирт, вино, пиво» — план тот же, а читается как другой.
  Владелец: «Одно и то же, но визуально сбивает с толку.» Причина: `_plan_goods`
  пишется в порядке расстановки, а восстановление слота — в порядке нумерации
  товаров. Строки теперь читают `_row_goods` / `_row_builds`, которые
  пересобираются в одном фиксированном порядке после каждого плана, загрузки и
  правки.
- **`mods.bat → «Забрать из игры файлы или логи»` нашёл 0 файлов.** Корнем
  выбралась `…/Europa Universalis V/game` — там есть `in_game/`, но ни одной
  папки из манифеста, и вывод не сказал, что там есть на самом деле. Плюс BOM в
  первой строке манифеста делал его собственный заголовок «пропущенной записью».
  Оба чинены; при неудаче инструмент теперь печатает настоящее дерево установки.
  **Что там на самом деле — всё ещё неизвестно**, и ответит следующий запуск.

**2026-09-03 — `where_to_produce`, доля сработала, а окно не открывалось потому,
что его никто не регистрировал.** Вестфалия / Мюнстер, и на этот раз с логами.

- **Доля дала ровно то, что обещала.** Железо поднялось с 1 до **3** = 5 − 2 РГО.
  Владелец: «Железа стало 3, как ты и говорил. И мне мало три, но на расчёт
  верный.» Три ему мало — за этим и нужен редактор.
- **Сортировка строк по грамоте принята**: «стала более гармонична».
- **Окно редактора: причина найдена в логе и она не в `.gui`.** `error.log`
  показал строку зонда из `bag_wtp_open_edit_window_effect` три раза — эффект
  отрабатывал. При этом **ни одной ошибки** про `bag_wtp_edit_window.gui`: ни
  разбора, ни типов, ни в `gui.log`. Окно не создавалось вовсе, потому что его
  не было в `in_game/gui/scripted_widgets/bag_wtp_scripted_widgets.txt` — файле
  на три строки, где перечислены ровно те три окна, которые работали.
  `docs/pitfalls/interface.md`, и теперь это ловит `check_script.py`.
- **Две сессии ушли не на тот вопрос** — на то, доступен ли какой-то виджет, —
  потому что в `reference/` нет ни одного базового типа. Настоящая нехватка была
  другая: в дереве нет `gui/scripted_widgets/`. Добавлено в
  `tools/game_files_manifest.txt`.

**2026-09-03 — `where_to_produce`, грамоты легли ровно, редактор не открылся
вовсе, и владелец поймал арифметику доли.** Вестфалия / Мюнстер, 48 локаций, 192
места из 192.

- **Лестница уровней сработала.** `rquota=5 rlevels=6`, и грамоты вышли **5 или
  6 у каждой из девяти** — было 6·7 и по 3 у оружейной и ювелирной. Ровно как
  предсказано.
- **Цена ровности измерена: 141 → 128 «кормящихся» зданий из 192** (73% → 67%),
  средняя выгода 56.8% → 52.4%. Ровные грамоты стоят земле примерно шестую часть
  бонуса, и это не догадка, а две строки `GAIN` подряд.
- **Расстановка грамот — 84.3% от лучшей возможной при тех же количествах.**
  Посчитано точно, венгерским методом по числам `RQ` из самого прогона
  (`_rq<k>` — статическая величина, она не меняется по ходу прохода, так что
  задача о назначениях решается по этим же числам): план дал **21246**, лучшее
  при счёте 5–6 — **25189**.
- **Две очевидные альтернативы измерены и обе хуже.** Проход по грамотам вместо
  прохода по городам: **18526**. Более мелкие полосы (10, 20, 50, 100 вместо 5),
  усреднённые по 40 случайным порядкам обхода: 5 полос дают 22969, 20 полос —
  21370. Мельче — хуже. Строить не стал ни то, ни другое.
- **Что дало бы 97.8%: проход обменов после лестницы.** Пара городов меняется
  грамотами, если сумма от этого растёт. На этих числах +8% за ~12 обменов, и
  количества сохраняются по построению. Не построено: в этот прогон уже уходят
  три неоткрытых окна и новая доля, и ещё одна перестройка распределителя сделала
  бы прогон нечитаемым.
- **Редактор не открылся ни из настроек, ни из окна плана.** Слоты при этом
  работают — подписи на кнопках меняются, — значит мост «кнопка → scripted gui →
  эффект» жив, а `bag_wtp_edit_window.gui` не рисуется. **Причина не названа.**
  Статически её не достать: ни один базовый тип (`widget`, `hbox`,
  `button_regular`, `flowcontainer`) в `reference/` не определён — они в той
  части `gui/`, которой в дереве нет, — так что проверить наследование типов
  нечем. Нужен `error.log`.
- **Кнопка «Редактор» стояла в группе `what`**, то есть в разделе расчёта по
  одному товару. Владелец: «почему отдельная кнопка "правка плана" находится в
  секции расчёта по 1 товару или праву».
- **Доля товара считалась от мест, оставшихся после грамот, и это была ошибка.**
  Владелец: «как будто бы 1 домик + 2 РГО не равняются 9, а равняются 3. Так
  почему? Почему РГО внезапно стал весить 4 вместо 1?» Он прав. `quota=2` в
  `PASS` — это 84 места (192 минус 108, потраченных грамотами) на 35 товаров.
  Дальше каждому товару прибавлялись его собственные грамотные домики и
  вычитались РГО: вино 2 + 6 = **8**, железо 2 − 2 = 0 → **1**. Девять вина и
  один металл — это вычитание, а не земля.

**Older `where_to_produce` runs — the first levelling press, the relative ladder,
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

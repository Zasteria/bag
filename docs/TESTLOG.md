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

**2026-09-06 (без пересборки) — шаг 2 закрыт, и одна правка оказалась ошибочной
по существу.** Он прогнал оставшееся на той же сборке.

- **«Снять закрепления»** снимает звёздочку и **не снимает кружок «не нужен»** —
  это правильно и так задумано: два разных утверждения, у каждого своя кнопка.
- **Слот возвращает пометки и закрепления** — да, сохраняются и загружаются.
  Обе стороны проверены.
- **Флажок «не нужен» не должен трогать общий план, и я это сломал.** Его слова:
  «нажав "План" на странице мода я получу лишь план на выбранную землю… слава
  богу я получаю просто новый план, а не план в котором какой-то домик закреплён
  на лимите 1». **Откачено:** `_pq<n>` больше не держится на 1 у помеченного
  товара, открытая лестница снова поднимает всем поровну, в `_plan_*` ноль
  ссылок на `_skip`.

**Ошибка была не в коде, а в диагнозе.** «Флажок ничего не меняет на деле» я
прочитал как «план его не читает», хотя область флажка — **только окно
редактирования**.

**Что именно откачено, потому что он спросил прямо:** в `bag_wtp_plan_set_quota`
стояло 47 блоков `if = { limit = { has_global_variable = bag_wtp_skip<n> }
set_global_variable = { name = bag_wtp_pq<n> value = 1 } }`, и открытая лестница
пропускала помеченные товары. `_plan_set_quota` вызывается на 15-й строке внутри
`bag_wtp_plan_run` — то есть кнопкой «План». **Флажок доставал до общего плана с
коммита `4422eb3` и до `a733654`.** Он считал, что не доставал, — но эту связку
(«не нужен», затем «План») ни разу не прогоняли, поэтому увидеть было негде.

**И главное следствие:** четыре функции мода выписаны таблицей **первым разделом
брифа** — выбор земли, поиск по одному товару, общий план, редактирование. «Ты
постоянно смешиваешь функции плана и редактирования», 2026-09-06, и это четвёртый
раз. Там же граница: **редактор читает план, план не читает редактор.**

**Шаг 2 закрыт.**


**2026-09-06 — `where_to_produce`, интерфейс пикера принят.** Его отчёт по трём
пунктам, все прошли.

- **Строки встали ровно**, включая последнюю: добивка пустыми ячейками до полной
  ширины сработала.
- **Зазор есть** — промежуток 14 читается как зазор, а не как «через миллиметр».
- **Звёздочка появляется** при «+1». Метка символом вместо цвета — то, о чём он
  просил дважды.
- **Дыры в сетке он снял с повестки сам:** «в целом похер, что там дырки, когда
  товаров нет, разберёмся с этим в другой раз». Шаг 2б остаётся записанным, но
  не срочным.

**Шаг 2 при этом не закрыт, и это надо назвать прямо.** Из пяти его проверок
подтверждены две с половиной: доля и замок — числами, «+1» снимает флажок,
загрузка слота, сохранённого до флажка, флажок снимает, звёздочка видна.
**Не прогонялось ни разу:**

1. **«Снять закрепления»** — уходят ли звёздочки и остаются ли домики на местах.
2. **Слот в положительную сторону** — сохранить *с* флажками и закреплениями,
   загрузить, и должны вернуться они же. Проверялась только обратная сторона.
3. **«Не нужен» + «План» на странице мода** — остаётся ли у помеченного товара
   один домик. **Это и есть весь смысл флажка**: до правки план его не читал,
   и следующий же пересчёт возвращал товару полную долю. Ровно это и не
   проверено.


**2026-09-05 (ночью, по скриншоту) — `where_to_produce`, три правки интерфейса.**
Прогона не было, всё по его отчёту с картинки.

- **Четвёртая строка съезжала, и причина арифметическая:** 47 товаров на пять
  строк оставляют последней семь ячеек, а короткий `hbox` в центрирующем
  родителе стоит в другом месте. Все строки добиты пустыми ячейками до полной
  ширины — теперь каждая ровно 1396.
- **Товары стояли вплотную**: «я не хочу, чтобы инструмент 1 товара был
  буквально через миллиметр от другого». Промежуток 6 → 14, окно 1440 → 1500.
- **Цвет заменён символом, как он и просил дважды:** «добавлять какой-то символ
  к цифре и всё». Закреплённый товар — звёздочка после числа. `*` это ASCII, то
  есть в отличие от `✔` вопроса о шрифте нет вовсе.

**И его вопрос, который я трижды закрывал отговоркой, имеет ответ «да».**
«Почему мод не может сам вычислить, каких товаров не окажется, и просто не
добавлять их в список» — может. Мешал не принцип, а то, что строке datamodel
негде было взять счётчик `_pn<n>`. `every_goods` есть, `Goods.MakeScope` есть,
`Scope.GetVariable` этот мод уже использует — значит счётчик кладётся на сам
товар и читается из строки. Разбор и порядок проверок —
`research/interface.md`; это шаг 2б и начинается он с одной дешёвой проверки.

**Чит-меню до сессии не доехало.** `reference/` ходит через git, последний
коммит по нему старый, в дереве его нет. Его надо закоммитить и запушить, иначе
для сессии его не существует.


**2026-09-05 (поздний вечер) — `where_to_produce`, столбики встали, но цена
видна.** Скриншот, прогона по пунктам не было.

- **Ячейка-`widget` сработала.** На картинке товары стоят столбиками, а не
  рваной лентой по центру: `hbox` со скрытыми органами больше не схлопывается.
- **И цена этого решения теперь на виду.** Земля умеет 35 товаров из 47, и
  двенадцать пустых мест раскиданы по сетке. Его вердикт: **«если их грамотно
  упорядочить — места они станут занимать раза в 2 меньше»**. Выравнивание и
  упаковка в нынешней конструкции взаимоисключающи: ячейки расписаны по товару и
  стоят на своих местах, поэтому недоступный товар оставляет дыру.
- **Цветные пометки ему не нужны.** «Мне в целом пофиг и не нужны всякие там
  жёлтые, красные буквы цифры.» Жёлтое число закрепления остаётся единственным
  видимым признаком замка, и **это противоречие следующей сессии надо снять с
  ним**, а не решить за него: замок должен быть виден, но не цветом.
- Логи не запрашивались.


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

**The five runs that built the editor and found its silent faults** — buildings placed
over the cap with nothing evicted, the presses that arrived and named two bugs,
the window that opened with no controls in it, and the report that named a scope fault first time — are in
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

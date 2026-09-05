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

**2026-09-06, сборка `ea49f6` — второй прогон правок: три из четырёх приняты,
одна причина найдена в коде, одна не найдена до сих пор.**

- **Заголовки пикера на одной строке** — да.
- **«Выбрать мою землю» работает как надо.**
- **Штамп на «Технической» пишется правильно.**
- **Окно плана** — «в целом более-менее, можно оставить так».
- **Права упаковались, но вторая колонка съехала на строку вниз.** Его слова:
  «во втором столбце прав пропуск в 1 строке, вместо например 2 пропусков в
  конце». Причина та же, что была у заголовков: `hbox` центрует детей друг
  относительно друга, колонка из трёх прав встала посередине колонки из шести.
  Обе колонки теперь в `widget` фиксированной высоты с якорем наверх.

**«Из чего» и счётчики — одна причина найдена, вторая нет.**

**Найденная, и это третий раз, когда одно и то же правило стоит прогона:**
столбец «Здание и метод» в окне по одному товару был `hbox` с написанным на нём
`size = { 394 28 }`, а **объявленный размер `hbox` не держит** — правило стоит в
`pitfalls/interface.md` с 05.09 и в комментарии в том же файле. С
`ignoreinvisible = yes` и одним видимым методом из четырёх этот hbox мерился в
262 вместо 394, и **всё, что правее — «Из чего» и «Подходит», — уезжало на 132
пикселя влево от своих заголовков**. Теперь колонку держит `widget`, а `hbox`
внутри только раскладывает два текста.

**Ненайденная:** в окне по городскому праву столбец «Здание и метод» — обычный
`text_single` в 470, и в шапке он тоже 470; суммы ширин шапки и строки совпадают
до пикселя, а на экране содержимое всё равно левее заголовка примерно на два
десятка. **Причина не найдена в исходнике, и гадать про неё я не стал.** Шаблон
`scrollbox` в `reference/` отсутствует, так что его собственный отступ измерить
не из чего. **Что это значит для следующего прогона:** если после исправления
выше окно по одному товару встало, а окно по праву нет — остаток изолирован и
меряется одним скриншотом.

**Верх редактора — «как был страшным набором столбиков, так и остался».** Две
конструкции подряд оказались неверными: сначала ячейки стояли по своим местам и
недоступный товар оставлял дыру посреди блока, потом строки паковались влево и
выходили рядами по три рядом с рядами по девять. **Третья: рисуются все 47
товаров, и каждая ячейка одинакова** — ровно то, что он просил дважды («точно
такое же удобное расположение как в поиске по 1 товару/праву»). Товар, которого
эта земля не делает, ничего на экране не обещает ложно: «+1» по нему обходит
землю, не находит места и говорит это строкой нажатия (`_edit_last_nowhere`).

**2026-09-06, сборка `b54e47` — перестроенное меню прогнано целиком, и оно
работает.** Его слова о результате: «в целом — очень круто, почти идеально».
Три вкладки, четыре кнопки, пикер в окне расчёта, лимиты и переключатели в окне
плана — **всё это подтверждено на экране**, вместе с землёй Мюнстера, 48 локаций
в 31 провинции, и правом на книгопечатание.

**Что подтверждено работающим:**

- страница мода: Земля / Расчёты / Техническая, три кнопки на «Расчётах»;
- выбор товара и права кружком, «Искать локации», обе таблицы;
- окно плана: «−»/«+» лимитов, галка прав, переключатель «на конец»,
  «Пересчитать» — «все кнопочки вроде как исправно выполняют свои назначения»;
- иконки товаров в пикере: «очень хорошо и аккуратно встали… в конце пару
  пустых ячеек и это выглядит гармонично».

**Что не работает и убрано совсем: «Только там, где здание вообще может
стоять».** Он сообщил три вещи разом — название не описывает поведение, галка
**не фильтрует ничего**, и она не нужна. Причину не искали: функция удалена
вместе с триггерами `bag_wtp_can_build_something` и `bag_wtp_can_build_<n>`.
**Это второй раз, когда эта галка оказывается мёртвой** — 31.08.2026 она не
работала из-за `if`/`else_if` в триггере. Вместо неё он заказал **«Выбрать мою
землю»** — пятую кнопку выбора земли рядом с областью, провинцией, локацией и
рынком.

**Что встало криво, и обе причины найдены в исходнике:**

- **иконки в столбце «Что ставит план»** сидели примерно на 70 пикселей правее
  своего заголовка: ячейка была `widget` 260 шириной, а внутри `vbox`, который
  забирает всю ширину и **центрует свои строки**. Комментарий над ней утверждал
  обратное. Две `hbox` с якорем на левый край вместо `vbox`;
- **«Из чего» и счётчики** — та же семья: `parentanchor = left|vcenter` без
  `widgetanchor`, то есть якорь виджета взят по умолчанию, а **умолчание отсюда
  не проверяемо**. Сказано вслух в тринадцати местах.
- **заголовки «Товар» и «…или городское право» на разной высоте** — `hbox`
  центрует детей друг относительно друга, а блоки разной высоты. Оба блока
  теперь в `widget` фиксированной высоты с якорем наверх.

**И правило, которое он сформулировал сам:** переключатель «на конец игры» **не
должен пересчитывать сам** — «снимаю галочку — жму пересчитать — получаю
результат… я считаю так и должно быть». В окне расчёта он пересчитывал сразу;
убрано, теперь оба переключателя ведут себя одинаково.

**И два общих требования к интерфейсу, из того же сообщения:**

1. **Техническое и наблюдательное — на «Техническую» вкладку**, а не в окна
   функций: «где и так не то чтобы много места». Штамп сборки уехал туда,
   в заголовок группы «Отладка».
2. **Никаких эссе в шапках окон.** «Длинные тексты там становятся настолько
   мелкими, что я ни разу даже не пытался их читать… я стремлюсь к интуитивно
   понятному интерфейсу». Четыре абзаца-описания удалены из окон результата,
   прав, плана и редактора; всё это уже есть в подсказках кнопок.

**Что осталось из его списка не сделанным:** редактирование городских прав в
окне правки (`+1`/`−1` по грамотам) — это шаг 5 практического плана, отдельная
машина выселения связки целиком, и в эту сборку не входило.

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

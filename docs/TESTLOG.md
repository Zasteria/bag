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

**2026-09-03 — `where_to_produce`, полосы выровняли грамоты до шести, а две
остались на трёх.** Вестфалия / Мюнстер, 48 локаций, «на конец», 192 места из
192, два одинаковых отчёта в одном файле.

- **Полоса 0 с квотой сработала, и это был правильный диагноз.** Было «10 000
  текстильных и по одной оружейной»; стало **шесть** у семи грамот из девяти.
  Владелец: «Фикс как бы сработал, но только на половину. Сейчас там примерно по
  6 прав у всего».
- **Ювелирные и оружейные — по три, и потолок тут ни при чём.** Квота была
  `48 ÷ 9 = 5.33`, то есть шесть; семь грамот в неё упёрлись, а эти две до неё
  не дошли. **Обход шёл по городам**: каждый город берёт лучшую грамоту, у
  которой ещё есть место, а оружейные стоят по земле **62..187** против
  **200..624** у соперниц — они не бывают лучшими ни в одном городе, пока у
  соперницы остаётся хоть одно место. Три города им достались только там, где всё
  прочее уже выбрано: Эссен, Реклингхаузен, Дипхольц.
- **Это и есть причина, а не догадка.** Она читается прямо из `RQ` каждого
  города: у Эссена «фламандское сукно 441 | каменные 321 | инструментальные 200 |
  ремесленные 94 | **оружейные 62 ← выдано**» — грамота взята последней в списке,
  то есть всё, что выше, уже было потрачено.
- **Ювелирные стоят 0 во всех 48 городах** (у Вестфалии нет драгоценных
  металлов), и владелец сказал, что для них тройка его, возможно, устроит. Для
  оружейных — нет: «им есть чё взять и я бы даже сказал есть у кого отобрать».
- **Открытая лестница снова не проверена.** `P36..P40` поставили ноль: земля
  кончилась на `P35`. Ничего нового про большую землю этот прогон не сказал.
- Против прошлого плана изменилось локаций **0** — товары легли ровно как
  прежде, изменились только грамоты.

**2026-09-03 — `where_to_produce`, прогон с относительной открытой лестницей:
на Вестфалии не изменилось ничего, кроме того, что план сдвинулся весь.**
Вестфалия / Мюнстер, 48 локаций, «на конец», 192 места. Отчёт оборвался — в логе
нет строки `END`, последняя локация напечаталась наполовину.

- **Относительная лестница на этой земле не работает, и не должна была.**
  `P36..P40` поставили **ноль**: земля кончилась на `P35 band0/tierall`. Открытая
  лестница вступает только там, где после квот остаются места, то есть на большой
  земле. Проверять её надо было тем же нажатием по северной Германии, а прогон
  пришёл по маленькой.
- **`изменилось локаций: 42 из 48`** — и это приговор тому, что было сделано
  вместо редактора. Вес, поданный в полный пересчёт, двигает почти всю землю;
  владелец просил ровно обратного и был прав.
- **Права по-прежнему перекошены**, и вот причина, найденная в коде, а не
  угаданная: банда 0 у грамот шла **без квоты**. Полосы 800..200 квоту держат, но
  оружейная грамота стоит на этой земле 62–163, а ювелирная 0 — они не проходят
  ни в одну полосу выше нуля, и единственное, что им доставалось, — один город из
  ковровой лестницы. Дальше открытый проход снимал квоту и раздавал остатки
  тому, кто дороже: фламандское сукно 10 городов из 48 при квоте 6, оружейная 1,
  ювелирная 1. **Исправлено:** полоса 0 теперь идёт с квотой, до открытого
  прохода.
- **Заурэлэнд и Ольденбург читаются в отчёте целиком** и подтверждают то же:
  корабельная грамота в 5 городах Заурэлэнда, фламандская в 7 городах
  Ольденбурга. Обе внутри квоты 6; перекос дают не они, а те две, что не получили
  ничего.
- **Что построено после этого прогона и в игре не было:** равномерные грамоты,
  редактор плана целиком (свой выбор товара тремя выпадающими списками, «+1»,
  «−1», сохранение, возврат, «показать изменения»), и снятый вес.

**Older `where_to_produce` runs — the large ground, the gain fix, the charter
worth 90, the specialised provinces, the thirteen-zero probe, the level rights and the
roll-back to the thirty-eighth load — are in
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

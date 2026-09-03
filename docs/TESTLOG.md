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

**2026-09-03 — `where_to_produce`, большая земля: полосы оказались единственным
распределителем, и «10000000 сукна и 1 пушка» — это формула, а не вкус
владельца.** Два нажатия, оба «на конец»: Вестфалия (48 локаций, 192 места) и
северная Германия (416 локаций, 1351 место, 74 провинции).

- **Открытая лестница с полосами работает и на большой земле стоит дорого.**
  `open800` поставил 335 зданий, `open600` — 107. Прошлая сборка ставила всё это
  одним проходом на полосе 0. `fed` вырос до **1174 из 1351 (87%)** против 605 из
  770 (79%), средний выигрыш 78.6%.
- **И два прохода упёрлись в лимит кругов**: `P36 open800` и `P37 open600` —
  `sweeps=50/50`. То, что они не успели поставить на высокой полосе, свалилось на
  низкую, то есть ровно то, ради чего лестницу и делали полосатой. Лимит поднят
  до 150.
- **Квота на большой земле не держит ничего.** 29 на товар, и её не достиг ни
  один: у `cannons` квота **160**, мест **103**, поставлено **2**. Значит
  распределяет только полоса — и она абсолютная.
- **Измерено, и это ответ на его жалобу:** товары, у которых лучшая точка на
  земле даёт ≥800, получили в среднем **42** здания; те, у кого ниже — **12**.
  Ровный дележ был бы 36. Обрыв резкий: `books 738 → 16`, `firearms 444 → 2`,
  `cannons 362 → 2`, а всё с 1000 — от 12 до 108.
- **Значит пункт D закрыт в прошлой сессии неверно.** На 48 локациях квота 2
  держала всё, дележ выходил ровным, и относительная лестница выглядела лишней. На
  416 локациях квота не держит ничего. **Одна земля не может закрыть вопрос про
  масштаб** — это и есть цена того, что D закрыли по маленькой.
- **На Вестфалии план не изменился ничем** — 192 здания, `fed=143`,
  `gain_total=112304`, те же строки проходов, что и у прошлой сборки. Ярусные
  проходы снова 3 из 69: их держит квота 1 у семи сырьевых товаров, и это
  подтверждено второй раз.
- **Заурэлэнд, его пример:** 7 локаций, 28 зданий — tar 6, naval 5, dyes 4,
  paper 4, books 2, furniture 2, остальное по одному. Всё это поставил **круг
  грамот**, а не распределитель: корабельная грамота в 5 городах из 7 (её оценка
  там 1000, инструментальная 799, оружейная 163). Он ждал 2-2-2-1. Это не ошибка
  формулы, а другая цель — и это тот случай, для которого сделан ручной
  регулятор.
- **Грамоты после отката гейта:** 9 разных из 9 возможных, и новая строка отчёта
  говорит, что восемь из них ещё не открыты. Работает.
- **Проверено на файле, не в игре:** относительная открытая лестница, ручной
  регулятор, снимок прошлого плана и строка «изменено: убрано X добавлено Y».

**Older `where_to_produce` runs — the gain fix, the charter worth 90, the
specialised provinces, the thirteen-zero probe, the level rights and the
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

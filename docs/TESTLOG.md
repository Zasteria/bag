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

**2026-09-03 — `where_to_produce`, два нажатия по чек-листу: три починки
подтверждены, одна оказалась регрессией, а ярусы редкости держит не лестница, а
квота.** Вестфалия / Мюнстер, 48 локаций все городами, 192 места из 192, 8
провинций. Нажатие 1 — «сейчас», нажатие 2 — «на конец».

- **Подтверждено:** `ordered_provs=8` вместо вечного нуля; каждая строка `WTP L`
  названа **одним** именем; `RQ legend` на месте, перед блоком локаций;
  `grantable=` различает «не досталось» и «не для этой державы» — на «в конце» 9
  единиц и 4 нуля, ровно те четыре (Византия, текстильные, две скандинавских).
- **Цена лестницы приемлема.** Кругов 73 («сейчас») и 61 («на конец») против 57;
  ни один проход не упёрся в лимит.
- **Полосатая открытая лестница работает.** На «сейчас» `P36 open800` поставил
  11 зданий и `P37 open600` ещё 2 — тринадцать мест, которые прошлая сборка
  раздавала одним проходом на полосе 0, то есть по порядку списка.
- **Регрессия, и она моя.** Возрастной гейт грамот на «сейчас» оставил Мюнстеру
  **одну** грамоту из тринадцати: у него есть `flemish_cloth_making` и нет
  `town_rights_enable`. Правило «каждый город обязательно получит право» отдало
  эту одну грамоту **всем 48 городам**: сукно встало в 48 локациях из 192, а
  товаров план поставил 30 вместо 35. **Откачено** — план снова считает по
  `potential`, как и список в окне, а открытие печатается в отчёте отдельным
  полем `unlocked=`.
- **Ярусы редкости снова поставили 3 здания из 69 — и порядок проходов тут ни
  при чём.** `P26..P30` (полоса 0, ярусы) при 66 свободных местах поставили
  **ноль**. Держит квота: у семи сырьевых товаров она равна 1, потому что
  область уже добывает это сырьё сама, и ковровая лестница этот единственный
  домик уже израсходовала. `clay` 2 РГО, `coal` 3, `fiber_crops` 3, `iron` 2,
  `salt` 3, `sand` 2, `stone` 3 — при базовой квоте 2.4. **Это правило
  владельца, работающее ровно как он его сформулировал** («там уже есть 2 рго
  глины — тебе нужно всего 3 домика»), а не поломка. Вопрос B закрыт окончательно
  и в третий раз переоткрывать его не надо.
- **План «на конец» вышел числом в число такой же, как у прошлой сборки**:
  192 здания, `fed=143`, `gain_total=112304`, те же строки проходов. То есть
  перестановка лестниц на этой земле не изменила ничего — её проверять надо на
  большой области, где открытый проход раньше ставил 271 здание из 770.
- **Модель квоты сверена на всех товарах обоих отчётов и сходится точно:**
  `q = max(1, PASS quota + что поставили грамоты этому товару − rgo) +
  число кругов открытой лестницы`. Последнее слагаемое теперь печатается как
  `open_sweeps`, а `diag.py` вычитает его сам и называет товары, которых мало
  из-за собственного РГО.

**2026-09-03 — `where_to_produce`, the gain fix held and the quota was caught
handing out a charter worth 90.** «Тонкое сукно ушло из Гослара.» 992 of 1309
buildings now earn something, up from 966.

- **Goslar is arithmetic, not a fault, and his reading of it is right.** «Сейчас»:
  tooling **925** against jewelry **909** — a genuine near-tie, copper feeding
  `copper_tools_guild_maintenance` whole. «На конец»: tooling **0** and jewelry
  909, so the jewelry charter takes it. His own words for why, and the numbers
  agree: «в конце инструментам в целом нахер не нужна медь». The end-game tools
  recipe is the iron mill, which wants iron and coal and has no copper option.
- **The book charter fell from 984 to 710**, which is the paper inflation gone.
  Predicted and confirmed.
- **But Vorpommern is a plain fault and he found it.** Both its towns took the
  **jewelry** charter, which their ground pays **90** for, while the artisan
  charter at **316** stood beside it. Amber is all that province has and amber is
  a trim, not a base — so the score was right and the grant was not.
- **The cause is the quota in the last band.** The passes were 800, 600, 400,
  200, 0 with the quota on, then band 0 with it lifted. **A pass that admits
  anything at all while the quota is still on** is what granted jewelry at 90:
  artisan, masonry, tooling and flemish were each already at the quota of
  61 towns ÷ 9 grantable rights ≈ 6, and jewelry was not. Brewing ended on 14, so
  the quota did not even buy evenness — it only misallocated at the bottom.
- **Fixed by dropping that pass**: the bands above 0 spread the charters, and the
  open pass lets the ground decide alone. A town whose best charter is worth
  under 200 waits for it and takes its real best. Not run.

**2026-09-03 — `where_to_produce`, the provinces specialised, and the probe named
the last fault.** «Провинции действительно сильно специализировались… мне
нравится куда стремится мод.» One province alone gave five towns five different
rights and every building из прав matched them.

- **Goslar, at last, with numbers.** `WTP RQ` on the «на конец» plan: **books
  984, jewelry 909**, tooling 925 on «сейчас». So the mod *does* see the silver —
  jewelry scoring 909 is near its best anywhere — and it lost honestly, by 75 and
  by 16 out of 1000. No bug in the rights themselves.
- **But the numbers it lost to were inflated, and that is a real fault.** `gain`
  was `bonus ÷ the chosen recipe's own ceiling`. A `fine_cloth_guild` running the
  plain base with a fur trim has one raw input and a ceiling of **2.86%**, so a
  province with fur and nothing else fed it whole and it scored **1000** — the
  same as a perfect wool province — for 2.86% on an output of 0.7. That is why
  fine cloth stood in Goslar: «там ничего для него нет, только мех для
  улучшения».
- **117 of 241 methods were inflated this way, across 21 of the 47 goods**, and
  `paper` is among the worst: `paper_guild_cloth_maintenance` is 1.66% of paper's
  10% and was scoring 1000. Paper is one third of the book charter, and the book
  charter is what took Goslar.
- **The divisor is the good's best ceiling in the game now**, not the recipe's
  own. The fur recipe reads 286 and a wool province 833, which is his order. The
  reason to normalize at all is untouched: a good whose *best* recipe tops out at
  5% still competes with one that reaches 10%.
- **His scarcity point is not built and deliberately so.** Jewelry can be *made*
  in all 416 locations (`ng=416`), so the tier ladder — which counts where a good
  can stand — treats it as common; what is scarce is where the ground *pays* for
  it. That wants a band-relative count and it is a second change; the gain fix
  moves all three of Goslar's rivals, so it goes first and alone.

**Older `where_to_produce` runs — the thirteen-zero probe, the level rights, and
the roll-back to the thirty-eighth load — are in
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

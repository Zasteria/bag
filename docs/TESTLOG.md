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

**2026-09-03 — `where_to_produce`, пять нажатий, и в них видно, что ковровый
проход не ставил ничего.** Вестфалия / Мюнстер, 48 локаций все городами, «на
конец» (нажатия 1, 3, 5), «сейчас» (2), и одно нажатие по большой области — 233
локации, 41 провинция, квота 16 (4). Разбор целиком в
[`investigations/plan_gaps.md`](investigations/plan_gaps.md).

- **`P31 cover` поставил 0 и `P32 open` поставил 0**, потому что `P30
  band0/tierall` уже добил землю до 192 из 192. Гарантия «все товары
  производятся» не выполнялась: `stone` кончил план с `ng=6 w=6 n=0` — ноль
  зданий там, где шесть локаций его могут сделать.
- **Ни одной печки болотного железа.** `iron ng=4 o=0 q=2 n=1`: выигрыш ноль
  везде (у добывающего здания нет входов-товаров), поэтому железо входит только
  на полосе 0, а к ней его четыре локации заняты.
- **Оружейная грамота одна на всю область и в пустом месте.** В шести городах
  Зауэрлэнда корабельная платит **1000**, оружейная **163**; корабельная взяла
  все шесть в полосе 800, и ковровая лестница грамот, идущая после полос, отдала
  оружейную Эльсфлету, где та стоит **0**. Ювелирная — то же самое, 1 штука.
- **Ярусы редкости не работают:** все ярусные проходы вместе поставили **5
  зданий из 84**, остальные 79 сделали пять проходов `tierall`. Полоса стоит
  снаружи яруса, у редких товаров выигрыш низкий, и до полосы 0 они не ходят.
- **Оценка выданных прав, измеренная:** Зауэрлэнд — корабельная 1000, смоляная
  1000, книжная 896, инструментальная 799, фламандская 454, оружейная 163,
  ювелирная 0. Грамот доступно 9, городов 48, `_rquota = 48 ÷ 9 = 5.33` → по 6
  на грамоту; фламандская взяла 10 (6 + 4 в открытом проходе).
- **Квота грамот теперь честная**, фикс двойного счёта виден: `cloth q=13 n=13`,
  `dyes q=9 n=9` — квота 2 плюс то, что дали грамоты.
- **`diag.py` всё это время отдавал сырой лог.** `render_rq` печатает строку без
  метки `WTP`, предохранитель считал её потерей и срабатывал на каждом отчёте, а
  «коротко» складывалось по всем пяти нажатиям сразу («выдано 263»). Исправлено
  и проверено на этом же файле.
- **Сделано по итогам, ни одно не проверено в игре:** ковровая лестница у товаров
  и у грамот перенесена в начало, до полос.

**2026-09-03 — `where_to_produce`, the covering ladder placed the weaponry charter
and could not place jewelry, and the quota collapsed to 2.** Westphalia, all 48
locations ticked to towns, «на конец».

- **Weaponry went from 0 to 1**, so the covering ladder works. **Jewelry stayed at
  0**, and the cause is one comparison: the winner is taken with `rtry > rbest`
  and `rbest` started at **0**, so a charter the ground pays exactly nothing for
  could never win even when it was the only one left. Westphalia has no precious
  metal, jewelry scored 0 in all 48 towns. `rbest` starts at -1 now.
- **Flemish took 11 against everyone else's 6, and it is not double counted.**
  `fine_cloth` scores 0 on this ground, cloth 908, so flemish is `(908+0)/2 = 454`
  and royal textile `(908+0+0)/3 = 303`. The same cloth, divided by a smaller
  bundle. That is «все права равны», working as he asked for it.
- **The bonus is counted once a province, not once a location.** He asked
  directly; `_b<n>` reads `any_location_in_province_definition`, which is a
  boolean. Five coal locations pay exactly what one pays.
- **The weaponry charter landed in Dortmund at 62 and not in Sauerland at 163**
  because by the covering ladder's last band the Sauerland towns were already
  full — they had taken the naval charter, which scores 1000 there.
- **And the quota fell to 2 — but the fault was not the quota, it was double
  counting.** 48 towns all took a charter and the charters ate 109 of the 192
  rooms, so `(rooms − rights) ÷ 35 goods` came out at **2**. That subtraction is
  correct and every good pays it once. What was wrong is that `_pn<n>` — the
  good's own counter, which the allocator reads against that cap — **was never
  cleared of what the charters had put down**, so the same 109 buildings were
  charged a second time, good by good. `tools` entered the allocator at `_pn = 6`
  (all six from the six tooling charters, which landed in the Ruhr at 200 because
  Sauerland's towns had taken the naval charter at 1000) against a cap of 2, and
  could not take a single free room in Sauerland at **799**. It finished the plan
  with the charters' six and none of its own. **Fixed:** `_plan_set_quota` adds
  `_pn<n>` back into `_pq<n>`, so the cap is the good's share of the *free* rooms
  on top of what its charters already built. Not run.

**2026-09-03 — not a run: the owner asked where a copper tools recipe came from,
and three faults came out of the answer.** «У моей нации был только 1 рецепт, тот
что с оловом… этого метода не должно было быть как кандидата в принципе.»

- **He is right about the recipe, and right about the numbers.** `copper_tools_guild_maintenance`
  is unlocked by `copperworking`, whose `potential` is `is_capital_mesoamerica`.
  What the plan actually chose in Goslar was `bronze_tools_guild_maintenance` —
  copper **and tin**, tin missing, 9.26% of 10 → **926**, which is the 925 in the
  report. My «copper feeds it whole» was wrong; his reading was right.
- **Fault one: a paired method escapes its advance.** A pair's key is
  `base+improvement` and `copperworking` says `unlock_production_method =
  copper_base`, so the lookup missed all four `copper_base+*` jewelry recipes.
  Münster was being offered a Mesoamerican recipe **in the «сейчас» plan**.
- **Fault two: «на конец» assumed every advance is eventually in.** 45 of the 181
  advances that unlock a building or a method are locked to a tag, a culture
  group or a region, and 13 of the mod's 241 methods sit behind one. That is how
  **five porcelain guilds landed in northern Germany** — the kiln wants an
  east-Asian capital. `_reach_<n>` asks the advance's own `potential` now.
- **Fault three, mine, from 2026-09-02.** `hand_cannon_guild` went into
  `ALWAYS_AVAILABLE` as «the first firearms building»; its advance wants an
  east-Asian capital, so that handed a Chinese building to everyone. It is
  `gun_smith` — age 2, no `potential` — and **his original «огнестрел во второй
  эпохе» was right all along.**
- **And the enhancement question, closed by him.** Base is 9.09 of the 10 points
  and the trim is 0.91, so the coincidence he wanted to chase is worth under one
  per cent: «нет смысла рвать задницу ради ~1%». The 10% split is the game's own
  arithmetic and the mod keeps matching it.

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
- **`where_to_produce`'s «В конце» plan.** Every run so far has been «сейчас»,
  and on Münster nine goods scored 0 for want of an advance — which is exactly
  the case the second button exists for.
- Everything `nd_ru` has translated apart from Westphalia — 3 600 keys that have
  never been on screen.

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

**2026-09-01 — `where_to_produce`, thirty-seventh load. Every town took the same
charter and none of them got glass; the glass half is the game's answer, the
charter is ours.** Three screenshots, Westphalia with every location forced to a
town. «Всё ещё довольно плохая раскидка даже на глаз.»

- **«Локаций 48 (городских 48) · провинций 8 · мест 144 · товаров 28 · норма 3 ·
  прав выдано 48 · зданий 138 в 48 локациях · лимиты 3/3 · кругов 23».** The
  ground is 96% full and every town has a right, which is what the last two runs
  were for. **Bog iron went to the wetland locations and got room**, which is the
  scarcity tiers doing their job on the case he named.
- **Glass cannot be built anywhere in Westphalia at the start, and the game is
  what says so.** Traced through the data rather than guessed: glass has five
  town recipes, and the ages that unlock their buildings are guild 0, workshop 4,
  glassworks 5, mill 6. So the only unlocked one is `glass_guild` — and it
  carries `location_potential = { is_produced_in_location_market = goods:sand }`,
  which no Westphalian market answers. `bag_wtp_avail_<n>` is
  `can_build_building` in **country** scope, which does check the advance
  (`docs/research/engine.md`), so the later three are out too. «В конце» would
  place it; «Сейчас» cannot, and should not.
- **The fault is that the charter was granted anyway, forty-eight times.**
  `mason` is age 0 and stands in every town, so `royal_masonry_rights` scored
  around a thousand everywhere while its rival bundles scored what their own
  goods could reach — and the grant divisor added on the previous run was
  dividing a thousand against near-zero rivals, so it never turned the outcome
  over. **Six other charters are wholly age-0 buildable** — artisan, brewing,
  naval, textile, tooling, jewelry — and any of them would have filled the town.
- **Fixed: a right is scored by how much of it the town could actually finish.**
  Each bundle good the town can build adds a flat 2000 plus its own score;
  one it cannot adds nothing; the total is divided by the bundle's size. So the
  number is "what fraction of this charter would really go up here" first and
  "how good would it be" second, and a bundle a town can finish outranks a bigger
  one it cannot whatever the scores inside them. The grant divisor stays on top.
- **The empty slots follow from the same thing.** Дюльмен at 1 of 3 and three
  towns at 2 of 3 had all been given the masonry charter and could place only
  its masonry half.

**2026-09-01 — `where_to_produce`, thirty-sixth load. The plan works and reads
right; three faults in the allocation, all named by the screenshots.** Two
screenshots, Westphalia whole and Münsterland alone. «Вау, оно кажется даже
адекватно работает… вся визуальная часть теперь работает как надо.»

- **Westphalia: «Локаций 48 (городских 7) · провинций 8 · мест 144 · товаров 27
  · норма 4 · прав выдано 7 · зданий 140 в 48 локациях · лимиты 3/3 · кругов
  40».** Rights on seven towns against one before, the quota reads 4, and the
  window and its rows are what he wanted.
- **Münsterland alone, five towns, one province: «мест 15 · товаров 13 · норма 1
  · прав выдано 5 · зданий 10 в 5 локациях».** Ten buildings in fifteen rooms,
  and the same goods standing in three of the five.
- **Fault one: «товаров» counts goods that cannot stand on this ground.**
  `_ordmax` is the better of the two sides, so a good whose only buildings are
  rural counts as makeable where every candidate is a town. Münsterland reported
  13 where at most 8 could ever be placed — **and the quota divides by that
  number**, so every good's share came out too small. `_ng<n>` and
  `_plan_scored` are counted on the side the location actually is now.
- **Fault two: the open pass lifted the quota instead of raising it**, so the
  first good down the list took every free room at once. That is the repetition
  in three of five towns. It raises every quota by one a round now, and the
  leftover ground fills in even layers.
- **Fault three: identical towns all take the same right.** Every location of a
  province scores the same, so four of five Münsterland towns took the masonry
  and glass charter and then held the same buildings. A right's score is divided
  by how often it has been granted now — the same shape as a good's province
  divisor. A better right still wins; a tie spreads.
- **Not a fault, and worth writing down: a right whose bundle the ground cannot
  make is granted anyway and comes out short.** Липпштадт took «Права на
  каменные и стекольные» and the plan put masonry, horses and spinning. Glass is
  the reason: every glass recipe wants sand, the province has none, so glass
  falls under `generate.fed_floor` and `glass_guild` also gates on
  `is_produced_in_location_market = goods:sand`. The mandatory-rights rule is
  doing what it was told; the ground refused the second half.

**2026-09-01 — `where_to_produce`, thirty-fifth load. Both plan buttons opened
nothing, and it was a rename in the same session that did it.** Logs supplied;
`which_build.py` confirms the tree.

- **«Кнопка "план" и одна и вторая теперь просто не работают и не открывают окно
  расчётов (с гор правами и без них). По отдельным товарам — всё работает.»**
- **`error.log`: «Variable 'bag_wtp_plan_open' is used but is never set.»** That
  is the whole fault. Adding the quota phase introduced a global flag and it was
  renamed `_plan_free` to keep it away from the window's own `plan_open`; the
  rename matched on `plan_open value = 1` and caught
  `bag_wtp_open_plan_window_effect` too — the **only** thing that sets the flag
  the window's `visible` reads. Both plan buttons go through that one effect,
  which is why both died and the per-good windows did not.
- **Nothing else of this mod's is in the log.** No script-value error from the
  province divisor, the quota, the RGO count or the mandatory rights, so the
  pass itself is untried rather than broken — the window never opened to show it.
- **Also in the log all along and now explained:** «Variable
  'bag_wtp_pm2_rural' is used but is never set», and its `mid_`/`end_` twins.
  Not a fault: **no two-part method may stand in a rural settlement** — all
  eight two-slot buildings are town and above — so the second-method half of a
  village row is always hidden, which is what it should be. The widgets are left
  alone and marked.
- **A checker now catches this class**, and was proven against this exact bug: a
  variable the mod reads that nothing in it, and not CMF, ever writes.
  `remove_variable` deliberately does not count as a write — read, removed, and
  never set is the shape of the fault.
- **The plan is still unloaded.** The thirty-fourth run's four changes have not
  been seen once.

**2026-09-01 — `where_to_produce`, thirty-fourth load. The per-tier sweep budget
works; the plan is full and wrong in a way that named its own fault.** One
screenshot of the plan window, Westphalia, caps 3/3, rights on. «Довольно плохо,
объяснять пока не хочу, посмотри сам.»

- **«Локаций 48 (городских 6) · провинций 8 · мест 144 · товаров 27 · прав
  выдано 1 · зданий 140 в 48 локациях · лимиты 3/3 · кругов 41».** The
  thirty-third load's fault is closed: 140 of 144 places filled against 28
  before, every location used. The per-tier budget was the whole of it.
- **Six villages of Paderborner Plateau, rows 3 to 8, each given the same three
  buildings.** This is the fault the formula work then explained: every location
  of a province scores identically for a good — the bonus is the province's — so
  with nothing to stop it a good takes its best province whole and that
  province's locations come out clones of each other. The fix is the province
  divisor, unloaded.
- **One right across six towns.** All-or-nothing needed a bundle of three to fit
  a cap of three exactly. The owner settled it the same day: a right is granted
  to every town regardless. Unloaded.
- **27 goods of 47 placed**, which is the ground and not a fault: twenty goods
  have no candidate location in Westphalia at all.
- **No log asked for and none needed** — the header line carried the diagnosis,
  which is what it was added for.

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
- **The whole-map plan in `where_to_produce`** — the tab, the two caps, the
  pass, the window and the map mode. Built 2026-09-01 and never loaded; what a
  first run has to answer is in
  [`investigations/whole_map_plan.md`](investigations/whole_map_plan.md).
- Everything `nd_ru` has translated apart from Westphalia — 3 600 keys that have
  never been on screen.

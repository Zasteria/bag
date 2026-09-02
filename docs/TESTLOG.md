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

**2026-09-02 — `where_to_produce`, Münster and all of northern Germany. The three
fixes work, and the number the mod exists for is 95%.** «Вроде как всё
заполняется хорошо… как будто бы основные функции мод теперь выполняет как надо.»
416 locations, 74 provinces, 61 towns, no ticks set anywhere.

- **All three fixes confirmed in one press.** 1309 buildings in 1309 rooms —
  100%, against 970 of 1312 on the same ground before. **No pass came near the
  guard**: the worst was 31 of 50, and the twelve passes are the ones the
  generator lists. The page bar and the removed province ceiling were on screen
  and neither drew a remark.
- **Selection quality, and it is the answer to «идеально ли он работает».**
  `GAIN fed=968 of placed=1309 gain_total=918033`. 74% of placed buildings earn
  a bonus where they stand — but **the ones that do capture 948 of 1000 of their
  own recipe's ceiling** (918033÷968). The 26% that earn nothing are the price of
  the covering constraint and of filling the ground, both of which he asked for.
  The overall 70.1% is those two numbers mixed, and is the less useful of them.
- **The distribution is the ground's arithmetic, not the formula's.** 355 of 416
  locations are villages and only 23 goods have a village side at all, so the ten
  goods makeable in all 355 take ~66 each and half the ground between them, while
  town-only goods share 244 slots of which the rights claim ~135. Town slots came
  out exactly 244 = 61×4 and village 1065 = 355×3, so nothing was left on the
  table anywhere.
- **Rights: 61 grants over 61 towns, 9 distinct, the largest 8.** No charter
  spam. `constantinopolitan_silk` (no silk here) and both Scandinavian ones went
  to 0, correctly.
- **Two faults this run makes visible, neither of them new.**
  `royal_weaponry_rights` was granted twice on a ground where cannons and
  firearms have no advance, so those towns carry a charter that delivers one good
  of three and the location-wide penalty for all of it — the rescored bundle
  (2000 a makeable good, −1000 a gap) is the fix and is one of the things still
  out of the tree. And **the mod page still says a right is all-or-nothing**,
  which stopped being true on 2026-09-01 at his own word: `plan_right_fits_<k>`
  is an `OR`.
- **Nine goods scored 0 for want of an advance** — lumber, silk, silver, sugar,
  tobacco, cotton, incense, ivory, wild game — so «сейчас» covers 32 of 47. That
  is the age and not the plan; «В конце» is the button that answers for them.

**2026-09-02 — `where_to_produce`, three presses in one log, and the tick never
reverted.** He ran the two-press test written the same day and it answered on the
first reading. «Тумблеры не переключились никуда… потом я нажал пересчитать — и
тогда они переключились снова на города.»

- **The ticks he cleared stayed cleared.** Presses one and two walked the same 44
  locations of Wallachia — `ticks now set: town=0 village=0` both times, and
  `towns=3` live where the plan before them had counted 17. The clicks land and
  they hold; closing the window and changing the map area do nothing to them.
- **The third press walked 127 locations, and the fourteen ticks in it are not
  the ones he cleared.** They are Марошвашархей, Кездивашархей, Ковасна,
  Секейкерестур, Дьердьосентмиклош, Гёргеньсентимре, Секейудвархей,
  Шепшисентдьёрдь, Чиксереда, Бырлад, Аджуд, Кудалби, Фокшаны, Галац — every one
  of them outside the 44 he had on screen, ticked earlier in the session and
  never cleared. Widening the ground brought them into the plan for the first
  time; four slots each put them at the top of the window; and that is
  indistinguishable from a revert. **Wallachia's own rows all read
  `forced_town=0` in the same report.**
- **So it is not a fault, and the window is what should have said so.** A tick is
  a location variable and it outlives a save, so «clear the rows I can see» was
  never «clear them». A button was added the same day: «Сбросить пометки
  город/село», all five continents in one press, printing how many it cleared.
- **And the number he asked for, at last.** `GAIN` in all three presses: **79%,
  76% and 82% of placed buildings earn a bonus where they stand**, and the
  average building captures **73%, 74% and 78% of the ceiling its own recipe
  could ever reach.** The largest ground, the one with the ticks in it, is the
  best of the three on both counts — the rank simulation costs nothing in
  quality.
- **The ticks also make more of the ground**: 44 locations gave 149 rooms with
  them and 135 without, 17 towns against 3, 17 rights against 3.

**2026-09-02 — `where_to_produce`, the rank simulation, and it works.** «Открыл
план — на первый взгляд работает как надо. Города получают права и домики из
прав.» Transylvania and Wallachia together: 127 locations, 22 towns of which 8
are of town rank and 14 ticked, 19 provinces, 403 buildings in 403 rooms.

- **Both predictions from the previous entry came back right.** Glass `T … w`
  went from 3 of 17 to **22 of 22**; every made good now wins a town method in
  every town. And the charter spam is gone: 22 rights over **nine different
  ones**, the largest holding 3 towns where masonry held 9 of 17 before.
- **No pass came near the sweep guard** — the worst was 11 of 12, on the open
  pass. `RIGHT`, `ROOM` and the location rows all read cleanly with the round
  brackets.
- **The distribution, which he asked to have read for him.** 36 goods of the 38
  the ground can make got something, from 1 building to 20. **Nine goods take 20
  each and that is 45% of the ground**: coal, sand, beer, cloth, glass, jewelry,
  leather, masonry, pottery — every one of them makeable in all 127 locations, so
  every one reaches the quota. Twenty goods took 7 or fewer, all of them
  town-only, competing for 88 town slots the rights have first call on. **That is
  the formula working as written**; `plan_max`, his own per-good ceiling, is the
  lever and it is 0.
- **How much of it earns anything, and why the answer is not in this report.**
  `o=0` on a side means every placement there earns nothing, and those alone are
  38 buildings of 403 — a floor, not the figure, because `o` is a maximum. Two
  counters were added for it the same day (`GAIN fed=… gain_total=…`), one `if`
  a placement.
- **One bug he found and it is not diagnosed.** Toggles cleared to auto, replan,
  «всё вроде бы было окей» — then he left the window or changed the map area and
  **the ticks were back on the towns**. Nothing in the mod writes
  `bag_wtp_force_town` except the button on the row, so this is not guessable
  from the source. The `ROOM` line now counts both ticks over every walked
  location and reads them live, so one press of «Диагностика» — with no plan —
  separates «the variable came back» from «the window is drawing a stale state».
- **`Important assertion failed: (Getting player in synchronous state, likely to
  cause a desync)`** appears once, at the first `[…GetPlayer…]` the dump reads.
  It is how the dump reads every number, and it matters in multiplayer rather
  than here — recorded so the next session does not chase it.

**2026-09-02 — `where_to_produce`, the diagnosis, first press. It named the cause
and found two faults in itself.** «Нажал "диагностика"… вроде появился такой
файлик» — the file was **0 bytes**; with the reader fixed the same press gave the
whole report.

- **The mod's half worked on the first load.** Button, CMF registration, callback,
  `bag_wtp_diag` and `debug_log` — none of them had ever run. `SELFTEST 1` came
  back `12345`, so every number below it is trustworthy.
- **The empty file was the reader's fault**, and it is a rule now: `diag.py` cut
  the game's line prefix with a regex written against a *guessed* shape, matched
  nothing, and the fold dropped every line it did not recognise
  (`pitfalls/diagnosis.md`).
- **The ground: 44 locations, 17 on the town side, 27 villages, 6 provinces, and
  it filled completely** — `placed=149 rooms=149`, no pass anywhere near the
  12-sweep guard (the worst was 7).
- **The cause of «no glass in towns», and it is one number.** A town-side method
  won on **3 of the 17 town-side locations** — for glass, and for cloth, tools,
  pottery, jewelry, beer, leather, paper, weaponry and eleven more. For the
  RGO-side goods it won on all 17: sand 17, masonry 17, fiber_crops 17, horses 16,
  tar 12. **Fourteen of those «towns» refuse manufacturing and accept only
  RGO buildings** — which is exactly «в городах я вижу много селитры, глины и
  прочего что можно добывать в сельских местностях».
- **Why they refuse it:** `glass_guild` is `town = yes, city = yes,
  megalopolis = yes` and `rural_glassmaker` is `rural_settlement = yes,
  town = no`. The game has four ranks and `bag_wtp_plan_is_town` admits a
  location either because the player ticked it or because its rank is not
  `rural_settlement` — and any non-rural rank takes a guild. So those fourteen
  are ticked villages. **The tick moves a location to the plan's town side and
  cannot move its rank in the game.**
- **The market gate is dead for good.** Both glass buildings carry the *identical*
  `is_produced_in_location_market = goods:sand`, and the rural one stood in all 27
  villages — so sand is in those markets. Twenty goods with no market condition at
  all were stopped in the same fourteen places.
- **The charter spam is the same fault one level up.** 17 rights for 17 towns:
  `royal_masonry_rights` in **9**, `royal_naval_rights` in **5**. In a ticked town
  masonry and tar can stand and glass and naval supplies cannot, so the bundle
  comes out half-made every time — and the `L` lines show it: «Район Арджеш …
  right=6 | clay, sand, masonry, tar».
- **And glass would lose anyway in the three real towns**: its best ordering there
  was `o=108` out of 1000, so it qualifies only in the last band, by which time
  those three have spent their four slots each on their own granted right.
- **Two faults in the dump, both fixed.** `[glass, masonry]` in a `debug_log`
  string is data-function syntax — the engine looked for a function called
  `glass`, failed, and cut `given=` onto a line of its own; round brackets now.
  And `error_log` writes into `debug.log` as well, so every headline arrived
  twice; one pointer in `error.log` now and the detail once.
- **Both remaining self-tests answered, and two retired.** A localization key as a
  `debug_log` message comes out as the key; `ROOT.GetName` and `SCOPE.GetName` do
  not exist. `debug_log_scopes = no` names the scope and is what every row uses.
  All of it in `research/engine.md`.
- **The one thing inferred rather than measured** — that those fourteen are ticked
  rather than some rank the mod does not know about — the next press prints
  outright: `ROOM` now carries how many of the town side are of town rank and how
  many the tick moved, and every `L` line carries `town_rank` and `forced_town`.

**2026-09-02 — not a run: `where_to_produce` was rolled back to the build of the
thirty-eighth load**, and the owner stopped the line. He picked that build by its
own message — the four tests, «большой рывок» — «именно в этом коммите я
почувствовал, что мод выглядит так, как я его задумывал… именно в этом коммите я
хочу начать постройку диагностического инструмента». **The two runs directly
below tested builds that no longer exist**, and so does the funnel probe branch
`claude/glass-sand-cycle-diagnosis-0qhgzw`, which was never merged. What they
measured about the *game* stands — the identical `location_potential` of
`glass_guild` and `rural_glassmaker` above all; what they say about our code no
longer describes the tree. What the thirty-eighth load left open came back with
it, deliberately, and is listed in `investigations/plan_formula.md`, last section.

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

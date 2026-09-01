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

**2026-09-01 — `where_to_produce`, thirtieth load. The plan runs, and the owner
found the model's real mistake in one province.** Two screenshots, 127 locations
in 26 provinces, caps 3/4, rights on.

- **«Локаций 127 (городских 8) · провинций 19 · мест 389 · товаров 30 · записей
  в списках 75 · зданий 322 в 120 локациях · кругов 8».** The province model
  works end to end: rows grouped by province, its towns first, and its locations
  carrying the same list. The `province_definition` fix held.
- **And the list is wrong, because its unit is wrong.** Székely Land's villages
  each got tools, jewelry and beer — «по сути все три этих товара даёт одно и то
  же здание „торговая деревня"». He is right: `market_village` makes all three,
  **a location holds one building of a type and a building runs one method**, so
  those three entries are one building's worth of answer and two wasted slots.
  The plan's list is a list of **buildings** now, not of goods, and a good whose
  winning building is already on the province's list is not an answer.
- **The worse half of the same mistake, found by following it up.** The plan's
  «village» side was `village_category` — four buildings in the whole game. But
  **thirty production buildings declare `rural_settlement = yes`**, and the other
  twenty-six are exactly what he said should have been there: stone quarries,
  clay pits, lumber mills, masons, salt collectors, sand pits. The two sides are
  split on the building's own rank gates now (`eu5data.Method.rural` / `.urban`),
  which takes a rural location's choice from 4 buildings to 30 and from a
  handful of goods to 31.
- **19 provinces against 26 «выбрано»** is not yet explained. The picker counts
  provinces its own way and the plan counts the ones it prepared; they should
  agree, and one of them is wrong.
- **What he could not read:** the town/village override. It was two glyphs drawn
  over the corner of the rank icon — «просто на значке появились какие-то
  символы». It is a labelled button in a column of its own now, saying
  «авто / город / село» in words.
- **Asked for besides:** «Пересчитать» inside the window, so a run happens when
  he says so and not after every click; the urban right named on the row, not
  merely implied by its goods; and the plan on two buttons like the ranking,
  now and at the end of the game.
- No logs asked for and none needed.

**2026-09-01 — `where_to_produce`, twenty-ninth load. The province model placed
nothing at all, and `error.log` carried not one line about it.** One screenshot,
Wallachia and more, with logs.

- **«Рассмотрено локаций: 127 · мест: 381 · товаров тут можно делать: 30 ·
  зданий: 0 в 0 локациях · лимиты 3/3 · кругов: 1».** So the ground was
  collected, the capacity counted, thirty goods scored and normalized — and then
  every one of the 47 picks failed its `limit` in silence. The rights switch made
  no difference and neither did the per-good ceiling, which places the fault
  before either of them.
- **The logs are clean.** Not one script error, trigger error or missing-variable
  line from the pass. This is the failure `CLAUDE.md` names: an effect that
  merely does nothing logs nothing.
- **The cause, on the evidence: a `province_definition` will not hold a
  variable.** The province's lists and their counters were kept on the
  definition, and `var:bag_wtp_plan_town_n < …` was then read back in every
  pick's `limit`. A definition is static map data; **nothing in vanilla and
  nothing in any mod in `reference/` writes a variable to one**, and the mod's
  own proven idiom has always been `every_location_in_province_definition`
  instead. Everything the pass reads was moved onto the locations, mirrored
  across the province.
- **Not proven, and that is why the summary line grew.** It now reads locations,
  towns among them, provinces, room, goods, list entries, buildings — left to
  right, so the first zero names the step that failed without another zip.
- **The other thing the log gave up:** «Value of wrong type in
  `bag_wtp_show_found:0`», once a frame with the page open, because the
  *ranking's* `bag_wtp_found` was never initialised on a fresh save. Fixed in
  `bag_wtp_init_counters`.
- **Asked for besides:** a hand switch to plan a location as a town, because the
  game's rank is only what is true today; the map pickers in the plan window,
  since choosing ground meant opening the other window and coming back; and a
  better name for «не больше стольких провинций на товар», which read as «не
  больше сельских».

**2026-09-01 — `where_to_produce`, twenty-eighth load. The whole-map plan runs,
and the owner's verdict is «получилось даже более менее сносно, я ожидал большой
лажи».** Three screenshots, Wallachia, caps 3/3.

- **The pass survives a button press and nothing was reported slow.** 44
  locations, 132 rooms, **30 of the 47 goods makeable on that ground**, 90
  buildings in 31 locations at 3 per good. The window drew, the counters read,
  the map mode painted. Everything built on 2026-09-01 is now loaded except the
  «Открыть» button and the caps at anything but 3.
- **The per-good number was the binding constraint, not the caps.** Raising the
  urban cap 3 → 5 changed nothing; raising «зданий на товар» to 10 filled the
  ground exactly — **132 buildings in all 44 locations**. So the caps were never
  reached and the ceiling the plan actually ran into was its own rounds.
- **Locations were left empty at 3 per good**, 13 of the 44, and the owner's
  ruling is that **no location in the plan's ground should ever be left empty**:
  what a displaced building leaves behind is exactly what should cascade into the
  poorer ground.
- **And the one-good-per-province rule was the wrong rule.** It was built to
  spread a good across provinces; the owner plays the opposite way — «вся
  сельская местность в одной провинции в большинстве случаев получит линейку
  домиков одинаковую», a province specialises and its locations repeat it. He
  read the scatter on the screenshot as a fault before realising the rows were
  grouped: what he expected under Западная Мунтения was «ряд почти одинаковых
  товаров». The rule is inverted rather than tuned — see
  [`investigations/whole_map_plan.md`](investigations/whole_map_plan.md).
- **Asked for besides:** urban rights in the plan, with first pick of the ground
  and a switch to leave them out.
- No logs asked for and none needed: nothing did nothing.

**2026-08-31 — `where_to_produce`, twenty-seventh load. The market picker works,
and it is drawn on the map after all.** One screenshot, fine cloth, «На конец».

- **A market *is* a map region to the picker.** Hovering outlines the market's own
  borders and a click takes it — no list needed, the same feel as an area. The
  file said the opposite for one commit; a market not being drawn on the map was
  a guess from vanilla's one usage and it was wrong.
- **But only the markets `interaction_source_list` names are clickable**, and it
  named `every_market_present_in_country`, so the neighbour's market could not be
  taken — which is exactly the market somebody planning a conquest wants to lay
  out. It is `every_market_in_world` now, framed by the ticked continents the way
  the other three pickers are.
- **The picking works and the owner is happy with it**: «В остальном всё чётко,
  удобно, классно.» Selection, re-rank and the counters all followed.
- **The four picker buttons were transparent and dreary** — an `action_button`
  with `bg_button_flavor_1`, copied from Advanced Auto Build, which is a flavour
  background over a bare button. They are `action_button_regular` now, which is
  the game's own type using `button_regular_texture`: the same solid look as
  «Очистить выбор» beside them.
- **The corner above the +/- buttons was empty** and read as a column out of
  line. It has a «+» heading now; `margin_left` went 48 → 10 and the new 38-wide
  cell makes the difference back, so «№» has not moved.
- **And the goods row was four pixels wider than the scrollbox it sits in** —
  1104 against 1100 — which nothing had noticed. The trailing spacer pays it
  back.
- **Still open: «Из чего» reads as sitting right of its heading.** Measured out
  of the file, the header and the row are identical column for column, so this is
  not a width. What is left is a constant inset the rows have and the header does
  not, and `margin_left` is the one number that moves it.

**2026-08-31 — `where_to_produce`, twenty-sixth load. All four fixes hold.**
Three screenshots, fine cloth, and the owner's verdict: «если не придираться к
этим злосчастным столбикам и выравниваниям, сейчас меня устраивает функционал».

- **No silk weaver where there is no silk.** Западная Мунтения now reads
  «Гильдия портных: Мериносовая шерсть ×0.70 + Красители с квасцами», **9.43%**,
  «2/3» — and the two icons say why the old answer was wrong in a way nobody had
  spotted: **the province works wool *and* dyes**. Silk never had anything to do
  with it. 7.14 (wool) + 2.29 (dyes) = 9.43, the recipe fed on both halves; the
  silk one won before only because 0.90 a level unfed beat 0.70 a level at 7.14%.
  «В конце» is «Фабрики тонкого сукна ×4.00», 0.63%, «1/1». The wool provinces
  behind it are untouched at 7.14% «1/3», and the count went 13 → 12.
- **The buildable tick re-ranks the open window** — third screenshot, «Обошёл 8 ·
  нашёл 5 · пересчётов 4», five provinces left standing with the window never
  closed.
- **`error.log` is clean**: not one `bag_wtp` line beyond the `Flag … never used`
  and `Variable … used but never set` noise. The two `PostValidate` lines are
  `qol_vassal_test_events`, another mod's.
- **Two columns I narrowed were narrowed too far.** «Восточная Мунтения» abuts
  «Валахия» and «Трансильвания» abuts its percentage: `elide` fills a column to
  the last pixel and then touches the next one, so width alone can never fix it.
  Both got their width back and a spacer of their own, paid for out of the method
  column, and the row still adds up to what the header does.
- **Not settled: whether «Из чего» is now under its heading.** The middle columns
  read as aligned in the screenshots and that one may still sit a dozen pixels
  right, which is too fine to call at this resolution. One glance on the next run
  answers it.

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

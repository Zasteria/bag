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

**2026-09-01 — `where_to_produce`, thirty-third load. The sweep guard ate the
plan, and the owner called a halt to iterating.** Three screenshots, Westphalia,
caps 3/3, rights on; and the ranking checked separately on stone.

- **«Локаций 48 (городских 7) · провинций 8 · мест 144 · товаров 27 · прав
  выдано 1 · зданий 28 в 20 локациях · лимиты 3/3 · кругов 12».** Twenty-eight
  buildings out of a hundred and forty-four places, most locations holding one
  thing, whole provinces cut short.
- **«Кругов 12» is the diagnosis and it is in the line.** `PLAN_ROUNDS` is 12 and
  the sweep counter was **one counter shared by all six scarcity tiers**, so the
  scarce tiers spent the budget and the last tier — the one that fills the ground
  — never ran. Each tier has its own budget now.
- **The ranking's buildability gate works and is visibly right.** Stone in
  Westphalia: the wholly flat province is gone, and Sauerland stayed with 3.72%.
  **But Sauerland has seven locations and one of them is flat**, and the row said
  nothing about that: «мне должно предлагаться конкретнее место». A row prints
  `n/m` now — how many of the province's locations can hold the winning building
  — counted for free off the winners the scoring pass already wrote.
- **«Обошёл 48 · нашёл 1»** for stone across the whole of Westphalia. One
  province. That is the gate being strict, and it is worth knowing whether it is
  too strict before anything else is built on top of it.
- **Only one urban right granted** (tools, in Münster). All-or-nothing plus
  buildability is a hard filter and Westphalia is a poor ground for bundles, but
  whether that is right or too strict is not settled.
- **The picker says «48 лок. в 31 пров.» and the plan says «провинций 8».** They
  count different things — the picker counts `province`, the owner-split piece,
  and the plan counts `province_definition` — and neither label says so.
- **The plan's icons ran together.** 26-wide cells at 2 spacing; 32 at 6 now.
- **And the owner's instruction:** «Мне кажется нам нужно сначала вывести точную и
  доходчивую формулу приоритетов и выгоды постройки производства, нежели вот так
  вот долбить всё туда-сюда.» No more counters, no more rounds of guessing —
  agree the formula first. It is written out in
  [`investigations/plan_formula.md`](investigations/plan_formula.md) and that
  document is the next session's first move.

**2026-09-01 — `where_to_produce`, thirty-second load. The buildability gate
holds, and the owner took the model apart one level further.** Two screenshots,
Westphalia, 48 locations, caps 3/3.

- **«Локаций 48 (городских 6) · провинций 8 · мест 144 · товаров 27 · записей 37
  · зданий 140 в 48 локациях · кругов 4».** Goods fell 32 → 27 and buildings 148
  → 140 with the gate in, and **no iron anywhere** — which is the gate working,
  though he knows of a wetland province and wants to see it offered there.
- **The building icons drew nothing.** `BuildingType.GetIcon` returns a `CString`
  — a texticon, the same as `Goods.GetIcon` — so it belongs in `raw_text` and not
  in an `icon`'s `texture`. Vanilla writes it that way in `alertmanager.gui`.
- **`§Yгород§!` printed literally** in the override button, and its rank icon of
  course never changed, being the game's. One word, no markup, and the game's
  own rank icon moved out beside the location name.
- **No urban right anywhere, all dashes.** Truthful under all-or-nothing —
  Westphalia can make no whole bundle — but indistinguishable from a broken
  feature, so the summary counts rights granted now.
- **And the ranking beside the plan was cheating the same way.** «Каменоломню мне
  выдало что отлично можно построить в провинции где полностью равнина, но там
  есть дерево». `can_build_building` now gates every one of the ranking's
  answers too, in all three ages.
- **Two rules of the model were wrong, and he found both.**
  **One:** uniqueness is per *location*, not per province — a market village
  makes tools, jewelry, beer and pottery, so four villages of a province may take
  one each rather than all taking pottery. The province lists are gone; the plan
  decides per location and a province looks coherent only where it deserves to.
  **Two:** a good only one place can hold must take that place before a common
  good takes its second — «жёстко зарезервировать». The sweeps run in scarcity
  tiers now (1, 2, 4, 8, 16, then everything), ordered by how many candidate
  locations can host each good.
- **He asked for the algorithm in plain words**, and it is on the «План» button's
  own tooltip now, six steps.
- No logs asked for and none needed.

**2026-09-01 — `where_to_produce`, thirty-first load. The plan was planning
things that cannot be built.** Three screenshots, Westphalia, 48 locations in 31
provinces, caps 3/4, once without rights and once with.

- **«Локаций 48 (городских 6) · провинций 8 · мест 150 · товаров 32 · записей в
  списках 43 · зданий 148 в 48 локациях · кругов 4».** The building rule and the
  rank-gate sides both hold — village lists are different buildings now.
- **And the plan offered iron in East Westphalia, where iron has exactly one
  building: `bog_iron_smelter`, whose `location_potential` is
  `is_adjacent_to_lake` or `topography = wetlands`.** There are no wetlands
  there. Plantations were on offer in Westphalia too, and `sugar_plantation`
  wants the location to already grow sugar *and* be overseas or colonial.
  **The plan never asked whether a building may stand where it is put** — the
  ranking has that tick and the plan did not inherit it.
- **The fix is one condition and the engine's own words justify it.**
  `can_build_building` documents itself as "location only checks local
  requirements, country checks the country scope requirements", so asked in the
  location's scope it is terrain, rank and `location_potential` and never the
  country's advances — which is exactly what a plan wants, and it is safe on the
  end-of-game side too.
- **A right was granted where its bundle does not fit.** Brewing rights (beer,
  liquor, wine) landed on a province with no wine, and the ordinary sweeps filled
  the third slot with horses and salt. His rule: **a right obliges every good of
  its bundle to be made where it is granted**, so all or nothing. No two goods of
  any bundle in the game share a town building, so the test is an exact AND of
  the per-good conditions.
- **The right was printed on village rows as well**, where a right never applies.
- **The window's toolbar was 1272 wide inside 1130** — four 164-pixel picker
  buttons, a 260 summary and two 150 buttons — which is the frame «уехала» he
  saw at the top right, twice now.
- **And the doubt underneath all of it:** «я начинаю сомневаться, что мод вообще
  хоть как-то ранжирует». It does — `bag_wtp_m<n>` (output × RGO bonus) →
  `_pnowbest_*` → `_p<g>` → `order_by` — and the fed floor is applied. It was
  ranking correctly over a set of methods that included ones the ground cannot
  hold, which reads exactly like not ranking at all.
- No logs asked for and none needed.

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

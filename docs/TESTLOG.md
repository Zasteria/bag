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

**2026-09-01 — `where_to_produce`, Wallachia again. The charter spam survived the
scoring fix, and the owner struck out the rule underneath it.** «Убери вообще
любое упоминание этого правила.»

- **His rule, now the sharpest line in `investigations/plan_formula.md`:**
  «Отсутствие сырья не должно влиять на то будет ли домик существовать вообще или
  будет ли он как-то смещён в очереди из-за этого. Отсутствие сырья может влиять
  только на ВЫБОР метода производства в конкретном домике.»
- **Two rules removed under it.** The unfed divisor, which halved a recipe the
  ground feeds nothing on top of a gain already zero — the same fact counted
  twice. And the input substitution entirely, score *and* placement: where a
  granted right's good could not stand, the slot had been going to the market
  input that would unblock it. `generate.market_inputs` is gone with it.
- **His stone quarry question, checked: it does earn a bonus.** Lumber is an RGO
  and `crude_quarry_maintenance` tops out at 10%. **But seven recipes in the game
  can never earn one at all** — `lumber_mill`, `slave_market`, `shoen` quarries
  among them — and the divisor was punishing them for it twice over.
- **What no rule of ours can change, and it must not be confused with the
  above:** `can_build_building` is the *game* refusing a building. A glass guild
  may not stand until sand is in the market. That is not the ground failing to
  feed a recipe, and the plan cannot plan a building the game forbids — which is
  why a right is scored on the bundle a town can actually finish.
- **Unverified.** Whether the spam ends needs a run.

**2026-09-01 — `where_to_produce`, thirty-eighth load. Four tests of the derived
formula. «Как будто бы выглядит всё довольно хорошо и ты сделал большой рывок».**
Nothing that follows was re-run after being fixed.

- **Westphalia, 6 towns, caps 3/3: it holds up.** «Он ставит нужные домики к гор.
  правам и заполняет свободные ячейки… всем 5 выданы разные права.» All 144 rooms
  filled, 64 sweeps. The rights spread — the grant divisor works. At caps 3/4 it
  filled 153 of 153 and gave 9 rights.
- **One province alone, 5 locations: «все товары разные на каждую маленькую
  локацию, это выглядит правильно».** The band ordering doing what it is for.
- **Every location forced to a town in the first province, villages below:
  glass lands in the villages and never in the towns, while saltpetre and clay —
  which a village could dig — take the town slots.** Not a fault in itself: an
  RGO building declares `town = yes` as well, so the plan may put one there.
  **But it is a loss the formula can name.** A right carries a blanket
  `local_production_efficiency` penalty over the whole town, so a building that
  is not in the bundle takes the penalty and none of the bonus — the same
  building is strictly better in a town with no right. `_ord<n>` halves a
  right-holding town's spare slots now. Halved rather than forbidden: the
  penalty's value is a define `reference/` does not hold.
- **All of northern Germany, 416 locations and 1312 rooms: 970 buildings in 354
  locations, and «мод не справился досчитать всё как надо».** He is right, and
  the cause is the round guard. A sweep places at most one building per good per
  side, so 970 buildings over 32 goods needs thirty sweeps at the very least, and
  `PLAN_ROUNDS` was 12 — every pass was being cut off with work left.
  **Fixed twice over**: the guard is 50, and the tier ladder now runs in the last
  band only, which is twelve passes where there were thirty-three. The guard is
  free where a pass has no work, since the `while` leaves the moment a sweep adds
  nothing.
- **«Показано всего 150 локаций» is the window's row cap, not the count.**
  `PLAN_ROWS` is 150 and the datamodel is what costs, so the cap stays; the
  header line says «показано N» now, beside the 354 it really used.
- **A one-off spike and a short hitch on «Пересчитать» over that ground**,
  reported without complaint. Worth keeping in mind against the pass count.
- **The province ceiling is gone.** «Я не представляю ситуацию, когда бы я мог
  захотеть сменить значение этой строки с 0.» Under the formula the quota does
  that job and is derived rather than typed, so the setting, its alias, its
  default and both localizations are removed.
- **Known and deliberately left:** faults in the single-good side of the mod,
  which he named and set aside for a later session.

**Wallachia, the same day, and it answered the question the Westphalia test left
open.** «В 90% случаев мне спамятся права стекла или судостроительства. При этом
везде он отказывается ставить и стекло и судостроительный завод.» 44 locations,
26 of them towns, 26 rights — and nearly all of them the same two charters.

- **His guess at the mechanism was right, and the cause was a fix from the same
  day.** The substitution — where a granted right's good cannot stand, plant the
  input that would let it — was also being counted in the right's *score*. And
  `sand_pit` asks only that the location is not already a sand RGO, so it stands
  nearly everywhere. That made `royal_masonry_rights` the one charter in the game
  that is complete in every town, and a sand pit went in wherever the glass
  should have.
- **Two things fixed in the score.** A right is now scored on the goods the town
  can really make — planting an input is a consolation for a right already
  granted, never a reason to grant it. And a bundle is no longer averaged over
  its size: each good the town can make is worth 2000 plus its gain, each it
  cannot takes 1000 off. Averaging had made a one-good charter tie with a whole
  three-good one, and every two-good bundle beat a three-good one with a single
  gap — which is the other half of why the same two kept winning.
- **Unverified.** Neither fix has been in the game.

**2026-09-01 — `where_to_produce`, no run. The owner stated the objective, and
the formula was derived from it rather than assembled from rules.** Nothing here
has been in the game.

- **«Все товары которые можно произвести на выбранной земле — должны
  производиться, все. И не важно есть для них сырьё на этой земле или нет.»**
  Coverage is a hard constraint. The RGO bonus only ever decides *which* recipe a
  building runs, never whether it is built.
- **«Максимально возможная часть получит свои плюшки… но при этом товары будут
  все.»** That is maximise-subject-to-cover, and it has one answer;
  [`investigations/plan_formula.md`](investigations/plan_formula.md) is the
  derivation.
- **The currency changed, and this is the substance of it.** Measured: a recipe's
  ceiling runs from 2.00% to 10.00% and five goods are capped under 5%, so a raw
  bonus cannot compare across goods — and the old `worth ÷ the good's own best on
  this ground` compares worse, squeezing everything into 0.909–1.000. What
  compares is **`gain = bonus ÷ that recipe's ceiling`**, 0 to 1: how much of what
  this good could ever get here, it gets.
- **The ground is now dealt in descending bands of gain, across every good at
  once.** By the time a good that would gain a fifth reaches a location, the good
  that would have gained four fifths has taken it — the opportunity cost paid by
  the ordering rather than by asking every other good. That is «дальше не жиреть»
  and «выделить у менее вкусных провинций место под всё остальное», and it
  replaces the per-good round-robin that produced the chaos.
- **A covering pass was added and it is his first requirement**: after the bands,
  any good still at zero takes a free slot anywhere, at any gain.
- **`town_right_efficiency_penalty` is understood structurally at last.** A right
  is a `location_modifier` carrying `local_<good>_output_modifier` per bundle good
  *and* a blanket `local_production_efficiency` penalty on the whole town. So the
  owner was right — «права дают слишком жирный бонус и дебафят всё остальное» —
  and a town holding a right should hold its bundle and as little else. **The
  number is a define and is in no file `reference/` holds**: one `grep` on his
  install, and until then the discount is a direction without a size.
- **Cost:** the normalisation pass is gone with the old currency, which is 47
  ordered walks saved a run; the bands cost 32 tier passes where there were 7.
- **Not in the formula, and named by him:** a rural location per province set
  aside for food. «До этого мы пока ещё не дошли.»

**2026-09-01 — `where_to_produce`, thirty-seventh load. Every town took the same
charter and none of them got glass; the glass half is the game's answer, the
charter is ours.** Three screenshots, Westphalia with every location forced to a
town. «Всё ещё довольно плохая раскидка даже на глаз.»

- **«Локаций 48 (городских 48) · провинций 8 · мест 144 · товаров 28 · норма 3 ·
  прав выдано 48 · зданий 138 в 48 локациях · лимиты 3/3 · кругов 23».** The
  ground is 96% full and every town has a right, which is what the last two runs
  were for. **Bog iron went to the wetland locations and got room**, which is the
  scarcity tiers doing their job on the case he named.
- **A session said glass was unbuildable there. It was wrong, and the owner's
  screenshots settled it the same day** — the game offers a glass guild in
  Münster and a rural glassmaker in Dülmen, both age 0. The gate was read
  correctly (`is_produced_in_location_market = goods:sand`); what was never
  checked is whether the ground satisfies it, and nothing here can check that.
  Filed in `PITFALLS.md`. **So glass is placeable, in the few towns whose market
  has sand — and on this run a charter had already filled those.**
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
- **Tried and reverted the same day: running the scarcest tiers before the
  charters.** It was built as the owner's own exception to a mandatory right, and
  it was the wrong reading of both the exception and the fault. Glass is *inside*
  `royal_masonry_rights`; it never needed to pre-empt the right, and letting
  every scarce good jump the queue contradicts what he had said several times —
  a right's buildings are mandatory. Rights are first again, whole bundle.
- **Built instead, and it is what he actually asked for:** where a granted
  right's good cannot stand, **the slot goes to the input that would make it
  possible**. Glass wants sand in the market and `sand_pit` stands at any rank
  asking only that the location is not already a sand RGO — so a town given
  `royal_masonry_rights` with no sand gets the pit, and the glass follows on the
  next plan. Derived rather than named: `generate.market_inputs` scans every
  `location_potential` in the game and finds exactly one usable pair,
  glass ← sand. The right's own score counts the good as reachable either way,
  so the substitution does not push the right down the list that needs it.

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

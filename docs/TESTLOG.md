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

## Runs

**2026-08-31 — `where_to_produce`, eighteenth load. The second column works,
and it brought back three things the first column had been hiding.** Five
screenshots, Wallachia, 1369, 127 locations in 26 provinces.

- **Both columns render and both ticks work.** «Прибавка» and «В конце» side by
  side, «Ранжировать по последней эпохе» visibly reorders and the re-rank
  counter moves with it. Paper: `2.49% -> 10.00%` on lumber-only provinces,
  `10.00% -> 10.00%` on Северная Олтения, which supplies both fiber and lumber.
  The ladder arithmetic is right on screen.
- **Ranking by the last age had no tiebreak**, so the 10.00 -> 10.00 province
  sat below a 2.49 -> 10.00 one. Owner: «конечный в приоритете, а начальный
  бонус — вторичным в счёте». Fixed with a thousandth of the near score added
  to the far one: the smallest step a raw material makes in the endgame set is
  1.9, so it can only order ties.
- **Cannons and firearms were not in the goods list at all** — hidden because
  no building for them is unlocked in the second age. That hiding is gone: every
  good some building makes is offered now, whatever the age, which also means a
  good another mod adds a building for.
- **Fine cloth answered with silk weavers at 0.00% in a wool country**, one row
  in the whole Carpathians. Not a bug in the arithmetic — 0.70 a level unfed
  beats 0.50 at the full ten percent — but the wrong answer: the game would run
  the recipe the market can feed, and the market is fed by the ground. **A
  method whose raw materials the province supplies none of is no longer an
  answer**; the wool provinces come back with wool weavers at 10%.
- **`fine_cloth_guild` runs two methods at once, not one.** The owner said cloth
  and jewelry have «улучшения» and cannons and firearms have ammunition; the
  files agree — eight buildings carry two `unique_production_methods` blocks,
  and a building runs one method from each. The mod treats them as alternatives
  and so understates both the output and the inputs of exactly those eight.
  Unbuilt, and the one thing here that needs a measurement before it can be:
  [`investigations/production_ladder.md`](investigations/production_ladder.md).
- **The rights window still answers for today only**, and its bundle showed
  weaponry alone until «Считать методы, до которых не дошла эпоха» was ticked —
  firearms and cannons have no unlocked building in the second age. It has no
  second column yet; that tick is what stands in for one.

**2026-08-31 — `where_to_produce`, seventeenth load. The registration fix holds,
two things are confirmed after weeks of «never reported», and the filter that
was meant to be fixed was never written.** Owner: «Список теперь сохраняется
после закрытия и открытия окна мода… Думаю основной пул задач для этой сессии
был выполнен.»

- **The counters are honest.** «Обошёл 127 · нашёл 19 · пересчётов 3», «в 26
  пров.», «№» running 16…19 down the visible part. Opening the mod page no
  longer throws the answer away, and «Открыть» reopens the last result — which
  is the whole of what that button is for.
- **Confirmed, both long outstanding:** the pickers stay folded («свёрнутые
  списки давно проверены — они сохраняются свёрнутыми»), and **the age filter
  works** — «метода производств и домики действительно меняются на более крутые
  и расчёт идёт уже от них». Seventeen loads to get that one reported.
- **Южная Олтения at 0.00% on all three goods is still there**, and the reason
  is not the filter's logic. `bag_wtp_right_row_is_worth_it` is *called* by the
  generated pass and **nothing defines it**: the patch that was to have written
  the trigger died half way through and only the call survived. An undefined
  name in a `limit` does not stop anything — the limit passes, and the symptom
  is a filter that filters nothing, exactly as the `trigger_if` fault looked.
  Written now, and `tools/check_script.py` refuses an unresolved call: every
  `<name> = yes` in a mod's own `common/` must resolve to the mod, to a mod in
  `reference/`, or to the engine's dumps.
- **And the buildable tick does not mean what it said.** «При её включении —
  показывается всё равно не только моя земля, но и чужая. Основное что она
  фильтрует — наличие городов в провинции.» He is right and the label was wrong:
  `can_build_building` is asked in the *location's* scope and answers about the
  location — its rank, its terrain, what the building needs — not about who owns
  it. It reads «Только там, где здание вообще может стоять» now, and says so.

**2026-08-31 — `where_to_produce`, sixteenth load. The rights window works, and
one screenshot carried three faults at once.** «Вроде как работает… выглядит
наглядно и понятно.» The bundle rows read: three goods, each with its own
method, bonus and materials, «Ценность» ranking them.

- **«Обошёл 127 · нашёл 0 · пересчётов 3», «в 0 пров.», and «№» reading 0 on
  every row — with rows on screen.** All one cause: `bag_wtp_register` ended
  with `bag_wtp_drop_browse` and `bag_wtp_clear_rows`, and **CMF's registration
  hook fires again every time the mod page is opened**. Opening the menu wiped
  the answer, zeroed the counters and took the rank off every location. The
  owner had already described the symptom without connecting it: «если закрыть
  окно cmm и открыть мод заново — расчёт сбросится». Registration touches
  nothing now.
- **The rows survived that wipe because `bag_wtp_clear_rows` did not know about
  `bag_wtp_right_results`** — a second window's list added and not added to the
  one effect that empties them. Hence a table of rows whose rank had just been
  removed.
- **A province at 0.00% on all three goods, «0/2» three times.** The good pass
  has filtered those since the fourteenth run; the rights pass had no equivalent
  and `var:bag_wtp_r_total > 0` is true of any province where the bundle can be
  made at all. `bag_wtp_right_row_is_worth_it` now asks the bundle's bonuses.
- **And the rights list wanted splitting.** «Мне за валахию не особо то надо
  видеть монополию константинополя.» Two lists now, and the split is the game's
  data rather than an opinion: a right `town_rights_enable` unlocks is general
  (nine of them), anything else is unique. A unique right is offered only where
  the game's own condition passes — the silk monopoly carries
  `potential = { OR = { has_or_had_tag = BYZ has_or_had_tag = ROM } }` and the
  Scandinavian privileges carry an advance nobody else takes.

Everything before 2026-08-29, and `where_to_produce`'s first fifteen loads — the
map mode, the twenty-option dropdown, the missing `is_ordered`, the run that
turned the mod from asking for a method into finding one, and the four that
confirmed the scoring, the tabs, the results window and whole provinces — is in
[`archive/testlog_2026-08.md`](archive/testlog_2026-08.md), moved rather than
trimmed. Search both with `python3 tools/kb.py`.

## Waiting on a run

The next session should start here rather than designing anything new. All of
these are prepared, all are cheap, and the owner has agreed to the hover one.

**`where_to_produce`, nineteenth load.** The eighteenth answered the second
column; what it left open, plus what this session changed on the back of it.

1. **Fine cloth in the Carpathians again.** It should now list wool provinces
   with «Гильдия портных: Ткачи шерсти ×0.50» at 10.00%, where the eighteenth
   run got one silk row at 0.00%. If it is still silk, the fed-first rule is not
   reaching the pass.
2. **Cannons and firearms are in the goods list** in the second age, and rank
   with an empty «Прибавка» and a filled «В конце».
3. **Ranking by the last age puts 10.00 -> 10.00 above 2.49 -> 10.00.**
4. **No province at 0.00% on every good** at the bottom of a rights table, and
   **«Уникальные права» empty** for Wallachia — both were the seventeenth run's
   and neither has been reported since.
5. **One tooltip, and it settles the eight two-slot buildings.** Open the build
   panel on a fine cloth guild, or a cannon maker, in a province that supplies
   one of its raw materials, and read the game's own production-efficiency
   figure. Whether it counts the inputs of both slots together or only one is
   the whole question, and nothing in `reference/` answers it —
   [`investigations/production_ladder.md`](investigations/production_ladder.md)
   has what each outcome means.

What is left after that is not a run but a decision: whether an ownership half
belongs in the buildable tick (`can_build_building` cannot ask it from a
location scope), and whether level rights get a table of their own —
[`investigations/town_rights.md`](investigations/town_rights.md).

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
- Everything `nd_ru` has translated apart from Westphalia — 3 600 keys that have
  never been on screen.

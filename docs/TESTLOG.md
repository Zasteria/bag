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

**2026-08-31 — `where_to_produce`, twenty-second load. The pairs are right and
the rights window was answering the wrong question.** Three screenshots, fine
cloth and cannons, and a weaponry right.

- **The pairs read correctly.** «Гильдия портных: Гильдия ткачей шёлка ×0.90 +
  Красители с квасцами», «Здание пушкарей: Железные стволы ×1.16 + Железные
  снаряды», with both slots' raw materials counted.
- **«Считать» looked like it was sorting by the endgame** — 1.78% above 7.14%.
  It was not: the ranking is by effective output and always has been, so ×0.90
  at 1.78% (0.916) outranks ×0.70 at 7.14% (0.750). Settled at the eighth run,
  when a forest village at 10% topped a weapons search; the owner reached the
  same reading himself from the cannons table.
- **«На конец» did nothing at all in the rights window.** The bundle pass read
  `bag_wtp_best_method` and nothing else, so both buttons gave the same table in
  the same order, showing first-age buildings. It reads the column the button
  names now, falls back the same way, and breaks its ties on «По пути» — with
  the row filter widened, or the table would empty itself exactly where a ladder
  ends early.
- **«Права: считать методы будущих эпох» is deleted.** Owner: «нафига вообще
  нужна?» — right twice over: since the twentieth load it reached no method at
  all, and a right should obey the same two buttons a good does. A unique right
  is still gated on `potential` — a tag is a fact about the country — but never
  on the advance that unlocks it.
- **«Из чего» sat far right of its header** in the rights window: the block was
  sized by its own icons and started wherever the expanding method column
  stopped. It is 190 wide in both windows now, like the header.

**2026-08-31 — `where_to_produce`, twenty-first load. The two-slot question is
answered, from the game's own panel.** Three screenshots.

- **Confirmed:** «По пути» prints `10.00% до 5` on the wool provinces and
  `0.81% до 6` where there are dyes; sorting by «В конце» orders them; a bundle
  keeps every good, at 0% where the ground feeds it nothing; alignment is better.
- **Each production slot earns its own bonus, over its own output.** A tailors'
  guild in Dordrecht: the tooltip is headed «Производственная эффективность
  метода "Красители с квасцами"» and lists «Добыча ресурса "Красители"…
  +10.01%» under it. Not the building's efficiency — the method's. So the eight
  two-slot buildings are now one method of the summed output at the
  output-weighted blend of the two bonuses, and the owner's own reading of the
  screenshot said the same thing before the arithmetic did.
- **Which explains what he noticed first:** Западная Мунтения showed «1/1» and
  the wool icon while the province also supplies dyes. The dyes feed the
  *improvement* slot, which the mod was not modelling. That row is a pair now.
- **The «×» is per building level.** The panel showed 0.76 against the method's
  0.2: four levels, an age multiplier, and efficiency multiplying output but not
  inputs. Nothing there separates provinces, so the mod keeps the per-level
  figure.
- **Three sort buttons in a header were one control too many.** Owner: «Я хочу
  иметь ровно две кнопки расчитать» — one for what you can build now, one aimed
  at the end of the game, both filling the same three columns. The headers are
  plain labels again and the second «Считать» is on the mod page.
- **The rights window's header lined up with nothing.** Same 10px scrollbox
  margin as the goods window, now fixed, and its columns read left too.

**2026-08-31 — `where_to_produce`, twentieth load. Everything asked for works,
and the middle age is missing.** Four screenshots, fine cloth and a weaponry
right.

- **Confirmed:** the far column prints 0.00% on every row; the sort buttons
  work and the mark follows them; two ticks on the page instead of three; no
  province at 0.00% in a rights table; «Уникальные права» empty for Wallachia.
- **Sorting appeared to do nothing with «Считать методы…» on**, and it was not a
  fault: with that tick the near column already held the best method of any age,
  which is the same ordering the far column gives. Two states saying one thing.
  The tick no longer touches the goods pass at all — the third column replaces
  it — and it is named for the rights window, which is all it still does.
- **Every column header sat ten pixels left of its column.** The rows are inside
  a scrollbox whose content carries a 10px margin and the header is not;
  `margin_left` is 48 now, and the three sort buttons have gaps between them.
- **A good of a bundle vanished when the ground fed it nothing** — Северная
  Мунтения showed мебель and керамика but not кожа. Owner: it should stay, at
  0%, and only a row where *every* good is fed nothing should go. A slot now
  falls back to the best available method whether it is fed or not; its value to
  the ranking stays zero.
- **And the ask this run is really about.** «В конце» is 0.00% for every wool
  province, so it cannot order them, and what the owner wants ordered is
  precisely that: where to build so that nothing is rebuilt, taking the best the
  ground gives *along the way*. There is now a third column, «По пути»: the best
  recipe this ground ever feeds in any age, and the last age it can be built —
  `10.00% до 5` for wool fine cloth, because the manufactory that obsoletes the
  wool workshop unlocks in the fifth. Sorting by «В конце» breaks its ties on
  it, so the top row is the province that ends best and, among equals, is best
  on the road there.

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

**`where_to_produce`, twenty-third load.** All of it new, none loaded.

1. **The rights window obeys both buttons.** «Считать» and «На конец» must give
   different tables — the second showing the buildings that survive to the last
   age, ordered by them, and by «По пути» where they are all zero.
2. **One tick left on the mod page**, «Только там, где здание вообще может
   стоять». The rights one is gone.
3. **«Уникальные права» still empty for Wallachia** — the list gates on
   `potential` alone now, so this is the check that dropping the advance gate
   did not open the floodgates.
4. **«Из чего» sits under its header** in both windows.
5. **Nothing in `error.log`** naming `bag_wtp`.

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

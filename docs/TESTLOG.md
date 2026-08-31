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

**2026-08-31 — `where_to_produce`, twenty-fifth load, with logs.** Two
screenshots of fine cloth, «Считать» and «На конец».

- **The row names its building again and every column sits under its header** —
  both asked for and both confirmed. `error.log` carries no `PostValidate` with
  `bag_wtp` in it; the only `bag_wtp` lines are `Flag … never used` and five
  `Variable … used but never set` for `_mid_goods*` and `_pm2_rural`, which are
  a generated `clear_variable_list` and a village that never runs a pair. Noise.
- **«Из чего» is still not under its header, and worse on the second
  screenshot.** Not a drift this time: the icons are *centred* in their column.
  The container is an hbox with a width, `ignoreinvisible` leaves it exactly one
  visible child, and an hbox with a width spreads its children across it — so
  the offset is half the slack, which is why «0/1» alone sat further right than
  «1/3» with an icon. Both windows' goods columns are plain `widget`s now with a
  `parentanchor = left|vcenter` inside.
- **A silk weaver was offered where there is no silk.** Западная Мунтения
  supplies dyes and nothing else the recipe wants, and it came first at 1.78% on
  «Гильдия ткачей шёлка + Красители с квасцами» — one input of three. Owner:
  the market will not have silk either, so it is not an answer at all. The floor
  a method has to clear is **half the bonus its raw materials could ever add**
  now, not one point above nothing; `generate.fed_floor`, and the same fed/unfed
  fallback as before behind it.
- **The buildable tick drops provinces, but only after the window is closed and
  opened again.** It never re-ranked — it wrote the setting and refreshed the
  lists, which is right for every other tick on that page and wrong for the one
  that changes which provinces are candidates. It calls
  `bag_wtp_recompute_live` now, the same guard the map pickers go through.
- **Wallachia sees no unique rights, which is the right answer.** The mod offers
  three of them — two Scandinavian, gated on a culture group, and the Byzantine
  silk monopoly on a tag. The other five grant building levels rather than an
  output ratio and are deliberately not in the list. The Scandinavian half of
  the question is still unrun and the owner has said he would rather not.

**2026-08-31 — `where_to_produce`, twenty-fourth load. The fixed-width columns
ate the building's name.** Two screenshots, fine cloth and textile.

- **A row printed «± Красители с квасцами» and nothing else** — no building, no
  method, no «×». The cause is one line: the method cell was given a size of its
  own, and a child carrying `layoutpolicy_horizontal = expanding` inside a sized
  hbox gets **no width at all**, so the text elided to nothing. The improvement
  beside it survived because it was `autoresize = yes`. Every column in both
  windows carries an explicit width now and none of them expands; the slack goes
  to a spacer at the far right, and the row's widths add up to the header's to
  the pixel (762 after the area column in the goods window, 700 per slot in the
  rights one).
- **Two spacers where the header had one.** «В конце» was followed by 10px in a
  row and 6 in the header, and a second 6 had crept in before «По пути»: four
  and six pixels, and every column after them out of line. That is the whole of
  the «Из чего» drift.
- **Fifty pixels moved from «Из чего» to «Здание и метод»**, which is where the
  long names are: a building, a method and an improvement in one cell.
- **Urban rights work on both buttons**, owner's words, and the unique list is
  empty again — which for Wallachia is the right answer, since the two
  Scandinavian privileges gate on a culture group and the Byzantine one on a tag.

**2026-08-31 — `where_to_produce`, twenty-third load, with logs.** Owner: rights
work and the two tables differ; unique rights arrived in Wallachia; the goods
table ranked for the last age still named first-age buildings; «Из чего» still
sits away from its header.

- **`error.log` carries one real line and no more:** `PostValidate of trigger
  'trigger_else_if' returned false at bag_wtp_generated_triggers.txt:107` — the
  last link of the `bag_wtp_can_build_something` chain, which ended on an
  `else_if` with no `trigger_else` after it. Everything else naming the mod is
  `Flag 'bag_wtp_good_*' is set but is never used`, which is CMM's list flags and
  is cosmetic. The chain ends `trigger_else = { always = no }` now.
- **Dropping the advance gate let the Scandinavian privileges into a Wallachian
  list.** Those two rights carry no `potential` of their own; what keeps them out
  is `culture = { has_culture_group = culture_group:scandinavian_group }` on the
  *advance* that unlocks them. A right inherits its advance's `potential` now —
  a country gate that is a fact rather than a thing you have not got round to.
- **Ranked for the last age, the row still named the building you can build
  today.** The order followed the button and the printing did not: the method
  column reads the near column whenever it is set, and it always is. `row_end` is
  written on the row now and the window reads the column the button asked for,
  goods icons included.
- **«Из чего» drifts because the method column expands.** An expanding column is
  as wide as what is left, and a row inside a scrollbox has less left than the
  header — by the scrollbar and the content margin. Both windows give the method
  column a fixed width and put the slack in a spacer at the far right.

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

Everything before 2026-08-29, and `where_to_produce`'s first twenty loads — the
map mode, the twenty-option dropdown, the missing `is_ordered`, the run that
turned the mod from asking for a method into finding one, and the four that
confirmed the scoring, the tabs, the results window and whole provinces — is in
[`archive/testlog_2026-08.md`](archive/testlog_2026-08.md), moved rather than
trimmed. Search both with `python3 tools/kb.py`.

## Waiting on a run

The next session should start here rather than designing anything new. All of
these are prepared, all are cheap, and the owner has agreed to the hover one.

**`where_to_produce`, twenty-seventh load.** A new picker and two layout
questions. One session with the mod page open answers all of it.

1. **«Выбрать рынок» is there and works.** Fourth button in the row, in the goods
   window and the rights window both. It opens a *list only* — a market is not
   drawn on the map, so there is no map click and no highlight, and that is the
   engine's shape, not a fault. Picking one should put every land location of
   that market into the plan and re-rank on the spot; picking it again should
   take them out. «Выбрано: N лок. в M пров.» is the number to watch.
   - If the list is empty and says «Ваша страна не входит ни в один рынок», the
     source list is wrong and that is the thing to report.
   - If the panel opens but the plan does not change, the effect never reached
     the country's scope — the «пересчётов» counter will not have moved.
2. **The four buttons still read.** They lost 46 pixels each to make room:
   «Выбрать провинцию» is the longest and the one to check for a truncation.
3. **«Восточная Мунтения» no longer touches «Валахия»**, and «Трансильвания» no
   longer touches its percentage.
4. **«Из чего»: is it under its heading, or still a dozen pixels right of it?**
   Cannot be called from a screenshot at the size sent. If still off, say so and
   nothing else — the header and the rows add up to the same numbers, so the
   cause is inside the scrollbox and it is one number to move.

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

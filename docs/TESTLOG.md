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

**2026-08-31 — `where_to_produce`, fourteenth load. The filter works and the
offer to defeat it was the litter.** Owner: «Хвосты ушли… Хотя я абсолютно не
понимаю нахера вообще есть возможность смотреть на эти пустые хвосты — выглядит
как просто мусорная часть мода.» The tick is gone; the one case it protected —
a method that wants no raw material and so can earn no bonus anywhere — is a
branch in `bag_wtp_row_is_worth_it` and needs no setting.

**`mods.bat → 2` does not re-extract the game.** «Ничего нового там не было,
только копирование модов в плейсет и референс.» Adding a folder to
`tools/game_files_manifest.txt` is therefore not enough to get it into
`reference/`, and the owner copied `common/town_rights` in by hand instead.
Which menu entry runs `extract_game_files` — and whether one exists — is the
open question; the manifest entries for `goods`, `production_methods`,
`building_types` and `town_rights` are right either way, since without them the
next real extraction would have deleted three folders `where_to_produce`
compiles from.

**2026-08-30 — `where_to_produce`, thirteenth load. It works.** Owner: «В целом
вроде как всё починилось, что мне нужно было. Я выбирал области — всё
обновлялось сразу же.» Two screenshots.

- **The ranking sorts and the pick re-ranks.** «Обошёл 127 · нашёл 19 ·
  пересчётов 3» and again at 10, the areas following each pick, and the «№»
  column running 1…19 with the bonus falling down it. Both of the twelfth run's
  faults are closed: `order_by` sorts once the values are in the thousands, and
  the pass reaches the country from a generic action.
- **The two-line row reads**, first time it has been judged: «Гильдия
  ружейников: Кузнецы-клиночники ×1.00» at 2.37% over «Лесная деревня: Сельский
  оружейник ×0.20» at 10.00%, with the goods icons beside their `1/2` and `1/1`.
  Which also settles the ninth run's question: **the village is no longer at the
  top of a weapons search** — 0.22 effective against the guild's 1.0237 — and it
  is on the row where it belongs rather than above it.
- **The tail of 0.00% rows is noise.** Nineteen provinces found, and the ones
  after about ten were all «0.00% … ×0.30 … 0/2» — the same building at the same
  output as the rows above, supplying none of its raw materials. Filtered now,
  with a tick on the Answer tab to bring them back, and shown regardless when
  the winning method wants no raw material at all.
- **The mod page is a page to scroll.** Seven region lists and two goods lists,
  all unfolded. They are folded once now, the first time a player sees the page,
  and his own folding is his after that.

Everything before 2026-08-29, and `where_to_produce`'s first twelve loads — the
map mode, the twenty-option dropdown, the missing `is_ordered`, the run that
turned the mod from asking for a method into finding one, and the four that
confirmed the scoring, the tabs, the results window and whole provinces — is in
[`archive/testlog_2026-08.md`](archive/testlog_2026-08.md), moved rather than
trimmed. Search both with `python3 tools/kb.py`.

### 2026-08-29 — `mods.bat`, an update run on the owner's own machine

Not a game run — the mod menu, on the box that has Steam, reported by the owner
in full. It is here because only he can run it and because two of the three
things it found were invisible from a session.

**Loaded:** `mods.bat → 2 → 3` (reference and playset both), against a Steam
workshop folder that had Advanced Auto Build's 2026-08-28 build and Glorp UI's
2026-08-28 build in it.
**Expected:** the copies in `reference/` replaced, the generators rebuilt, and a
report of what moved.
**Observed:** the copies were replaced; **two generators failed and stopped the
run**, and the run then ended by telling him the two mods it had just copied in
were still behind.

- `auto_build_ru` — `28 key(s) the base mod does not define`. The new Advanced
  Auto Build deleted 28 keys, the ranking-mode block among them, and no key was
  added or renamed. A deletion, and it stopped everything.
- `glorpui_hints` — `Glorp UI writes a hint this mod cannot translate:
  GLORP_UI_SVH_CENTRALIZATION_PV_PETTY_BUREAUCRACY: @hint! Grant
  [ShowEstatePrivilegeName('petty_bureaucracy')]`. Glorp UI moved its hint
  references to the engine's own data function.
- `svx_unlock_gate.txt` changed in the same run, which is the quiet half: the
  advance gates are found by a second regex that only knew the old shape, so it
  matched nothing and wrote the file empty. Nothing errored.
- `workshop.py record` then stamped both freshly copied mods `behind`, because
  it dates a copy by `git log` and the copy was not committed yet.

**Verdict:** all four are fixed and the exact run was replayed against files
rewritten into the new shapes — refresh comes out green, with one note naming
the nine dropped keys. Still his to confirm: that the real 2026-08-28 files
behave the way the rewritten ones did, which is one `mods.bat → 2` away.

**He also said the tool never actually updated a mod in Steam for him** — he
still had to unsubscribe and resubscribe. It compared install dates, and Steam
stamps a mod updated when it *notices* the update rather than when it downloads
it. It compares build ids now (`manifest` against `hcontent_file`), and will
re-fetch a mod on demand whatever the check says. Untested against a real
`appworkshop_3450310.acf`; see [`STATUS.md`](STATUS.md).

### 2026-08-30 — `glorpui_hints` against Glorp UI's 2026-08-28 build, in game

**Loaded:** the owner's playset, Glorp UI 2026-08-28 with `glorpui_hints` after it.
**Observed, reported by the owner:** with Glorp UI's new «показать недоступные»
switch **on**, the two mods conflict and something on Glorp UI's side breaks;
with it **off**, everything is fine. He also reports their version of the
feature has gaps and does not show everything worth using, and that with their
filter off it is «совсем плохо».

**Cause, found in the files and not guessed:** their update added one
`TooltipScrolledStringPairList` per side that prints vanilla's own C++ hint blob
(`[SocietalValue.GetLeftHint(Player.Self)]`) when the country variable
`showUnavailableSocietalValueSuggestions` is set, and added
`NOT = { has_variable = showUnavailableSocietalValueSuggestions }` to every one
of their `glorpui_svh_visible_*` script values. So their switch is an either/or:
their filtered lists off, vanilla's blob on. This mod replaces that whole
`blockoverride`, and rebuilt their half from the entries its regex recognised —
which the blob entry is not. Switch on: their lists gone (their own script
values say so), their blob gone (this mod dropped it). Half the tooltip empty,
nothing in `error.log`. «Совсем плохо» is vanilla's raw blob, which is what
their switch shows.

**Fixed:** their block is now spliced in byte for byte and the check compares
text rather than parsed entries. Replaying the old behaviour against the new
files reproduces the fault and the check now names it.

**Verdict:** unrun. The fix has never been in game — the next load with their
switch **on** is the test, and what should appear is vanilla's blob plus this
mod's own lists, with Glorp UI's per-axis lists hidden by their own design.


### 2026-08-30 — the same switch, and `gui.log` named the build that answered

**Reported by the owner**, two screenshots and the whole `logs/` folder. Playing
Wallachia, both mods on, the *Наступление ↔ Оборона* tooltip. Switch **off**:
«Дальше продвинуться в сторону обороны» with its one takeable line, and this
mod's «Также влияет на смещение» under it — "the same as before the update, and
it suited me". Switch **on**: the «Дальше продвинуться» block disappears
outright; only this mod's block is left.

**That is the pre-fix bug, exactly, and the run did not test the fix.**
`gui.log` gives the line of every template that overrides another:

```
Template 'SocietalValueCountryLeft_tooltip'  at gui/svx_extra_societal_value_hints.gui:6
Template 'SocietalValueCountryRight_tooltip' at gui/svx_extra_societal_value_hints.gui:964
```

The file in this tree puts them at **9** and **984**. Lines 6 and 964 are commit
`012317f`, 2026-08-25 — the build with no blob block at all. The deploy in
`Documents/.../mod/glorpui_hints/` was never refreshed after 2026-08-29. The same
log fingerprints `glorpUI_generated_societal_value_hints.gui` at 3 and 261, which
is the 2026-08-28 build in `reference/` byte for byte, so their half is the half
we think it is.

**Confirmed anyway,** because the 25 Aug build is a real build:

| | |
| --- | --- |
| **the override chain** | `svx_… > glorpUI_… > shared/government_tooltips.gui`, both sides, no error. Load order is right and this mod does win the templates. |
| **`error.log`, 356 lines** | not one names a `svx_` file, `svx_unlock_`, `country_religion`, `GLORP_UI_SVH_*` or `SVX_*`. The advance gate and the aspect gate log nothing; the one `jomini_trigger` line is another mod's event. |
| **`ru_loc_fix` round two** | still 0, on a fourth run. `MARKET_SURPLYS_INFO` was 82 in the 07:44 logs of the same day and 0 in this one. |

**Not confirmed:** the splice, the five advance-locked privileges as *shown*
(Wallachia offers none of them either way), and `Inconsistent trigger scopes` —
its repair is newer than the gui file, so the deployed build's provenance for
`svx_extra_hint_loc.txt` is not pinned, and the Confucian Academy gate is on an
axis Wallachia does not have.

**Written down as a tool, not as a warning.** `python3 tools/which_build.py
<logs folder>` fingerprints every gui file in a log against this tree and against
`git log`, and says which commit ran. This is the second run lost this way.


### 2026-08-30 — the splice, in game, and it works

**Loaded:** the 2026-08-29 build, installed by hand from the repository because
`mods.bat` did not do it (see below). Wallachia, *Наступление ↔ Оборона*, Glorp
UI's «показать недоступные» **on**.

**Observed:** «Дальше продвинуться в сторону обороны» is back and now carries
vanilla's own unfiltered blob — five lines where the filtered list had one:
«Добавить государственный принцип "Система гарнизонов"» +0.05, «…"Тактика
асимметричной войны"» +0.10, «Установить политику "Оборонительная позиция"»
+0.10, «Содержание крепостей» and «Влияние совета», both (масштабируется).
This mod's «Также влияет на смещение» sits under it with its four. Glorp UI's
per-axis list is gone, which is their design.

**Verdict: the splice is confirmed.** Vanilla's blob, this mod's lists, their
lists hidden — exactly what was predicted, and the last thing this mod was
waiting on. The owner: «вроде всё работает ок», and «наш мод более показателен и
ясен визуально».

**Known and deliberately not fixed:** a few rows appear in both blocks —
«Содержание крепостей» is in vanilla's blob and in this mod's list. The owner
was asked nothing and said to leave it: the blob is theirs to decide and
de-duplicating across it would mean parsing it, which is the thing that broke
this feature the first time.


## Waiting on a run

The next session should start here rather than designing anything new. All of
these are prepared, all are cheap, and the owner has agreed to the hover one.

**`where_to_produce`, fifteenth load — the urban rights, first sight.** Tick a
right on the Goods tab instead of a good; it is a third list there and it drops
whatever good was ticked.

1. **The list draws at all.** Twelve rows, each iconed by the first good of its
   bundle and named by the game. The one guess in the build is
   `town_rights_type:<key>` as a value a CMM list item can hold — if it cannot,
   this is where `error.log` says so and the list is empty or absent.
2. **«Считать» opens the other window**, «Где производить — городские права»,
   and not the first one. Only one of the two is ever open.
3. **A row is the bundle**: one line per good — good, bonus, building and
   method, and the raw materials — and «Ценность» on the left, which is what the
   rows are ranked on. Rights with one good draw one line and rights with three
   draw three, nothing overlapping.
4. **A pick still re-ranks** and «№» still runs 1, 2, 3 down the window.
5. Carried over, still never judged: the pickers folding shut on first sight of
   the mod page, and the age filter.

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

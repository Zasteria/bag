# Test log

What has actually been in the game, and what it showed.

Only the player can run EU5, so a run is the scarcest thing this repository
consumes. Everything else here — the reference tree, the generators, the
checkers — exists to spend fewer of them. This file is where a run's result
stops being a remark in a chat and becomes something a later session can rely
on.

**A session writes the entry, not the player.** The player says what happened,
in as few words as they like; the session turns it into a row and commits it. If
a run is not written down, `HANDOFF.md` will keep calling something "untested"
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

### 2026-08 — `nd_ru`, overriding a base mod's localization

**Loaded:** National Destinies, then `nd_ru` below it in the playset.
**Expected:** the Russian keys of `nd_ru` to replace National Destinies' own,
which are English text under an `l_russian:` header.
**Observed:** they did. Westphalia reads in Russian end to end.
**Verdict:** the whole approach of the mod rests on this and it holds. Load order
decides; `nd_ru` must sit after the base mod.

### 2026-08 — `goods_target`, every good and a target each, with logs

**Loaded:** game 1.3.11, the player's normal playset. Logs supplied.
**Expected:** monthly checks counted in the settings tooltip, a target per row,
readings updating monthly.
**Observed, in four parts:**

1. **Monthly checks: 0.** The pulse leaves no trace at all. The display path is
   not the suspect — Construction Manager reads `var:` inside script values the
   same way this does.
2. **The Target column shows a raw key**, `bgt__construction__t…`.
3. **The readings do not change from month to month.**
4. **The game visibly loses ticks while the Mod Menu is open** — obvious with
   the game unpaused, opening and closing the menu.

**The logs say nothing about this mod.** Zero lines in `error.log`, its five
rotations, `gui.log` or `game.log`; `debug.log` shows only that it mounted and
that its `1.3.*` matched game 1.3.11. So none of the four is an error the engine
noticed — all four are the silent kind.

**Diagnosed from the logs and the reference tree, not guessed:**

- The raw key is the **format keys**. `cmm_set_list_field_conditional_format`
  makes the widget read `<mod>__<setting>__<field>_prefix` and `_postfix`, and
  the `_high` / `_low` pair for the sign. CMF detects their existence by
  comparing `Localize(key)` against the key itself, so a missing one renders as
  its own name and logs nothing. `cm__auto_build_list__min_discount_*` is the
  worked example.
- The performance and the frozen readings are the same cause: each of the 74
  row labels calls `ScriptValue('bgt_impact_<good>')`, and each of those does
  four market and default price lookups. That is evaluated for every drawn row,
  every frame. The version before this one had no reading in its rows and cost
  nothing noticeable; the tooltip with five of them was also fine.

**Not resolved:** why the monthly pulse never runs. `monthly_country_pulse`
exists in the game's own dump, CMF chains it through `_cmf_on_monthly` into
`cmf_monthly_human_country_pulse`, and this mod's *registration* leaf on
`cmf_on_mod_registration` demonstrably works — so on_action merging from this
mod's file works at least once.

### 2026-08 — `goods_target`, the goods list

**Expected:** a 28-row list with two ticks per row, and a monthly log line
naming what is ticked.
**Observed:** the list draws, the rows name their goods, a row can be selected
and the game's own goods tooltip comes up on hover. Ticks can be set. **The log
shows nothing new** — no monthly entries at all.
**Verdict:** the list half works, including the `_on_changed` callback without
which nothing would draw. Whether a tick reaches script is still unknown,
because the only thing that would have said so was the log.
**Two suspects, both removed rather than diagnosed:** the monthly effect was
gated on `variable_map(cmm|flag:bgt__log_readings)`, and asking a variable map
for a key it does not hold is an error rather than false — a setting left at its
registered default may never have been written to the map. And the count was
logged with `cmf_log_value = { value = var:... }`, a CMF macro taking `var:` in
an argument, which is the shape that kills a CMM list on `item = var:x`.
**Learnt:** the mod now counts into country variables that a script value reads
back into the tooltip, so the next answer does not depend on the log at all.
**Also asked for:** every good rather than the 28 construction ones (cannons
were missing), and a target per good rather than one for all.

### 2026-08 — `goods_target`, first load: do the readings match

**Loaded:** the player's normal playset with `goods_target` added.
**Expected:** a Mod Menu tab with two settings, and readings that agree with the
game's own construction cost tooltip.
**Observed:** both. The tab renders in Russian, and the tooltip of "Писать замеры
в журнал" showed lumber -14.7%, masonry +22.1%, glass -33.0%, sand -18.7%,
stone +1.1%. The player confirms the discount matched the game at the start of
the run.
**Verdict:** the measurement the whole mod rests on is right. Registration, the
`capital.market.market_price` reading, the per-good script values and
`GuiScope...ScriptValue` in a CMM tooltip all work.
**Learnt:** the readings move every month, so a yearly log line is the wrong
cadence — the probe moved to CMF's monthly pulse, which is also where
Construction Manager's own dispatcher runs.

### 2026-08 — logs from a live playset, checked for our own mods

**Loaded:** the player's normal playset — CMF, Construction Manager, Glorp UI,
National Destinies, our mods — while dumping `script_docs`.
**Observed:** `error.log` carries no line mentioning `bag_rgo`, `eu5ab`, `nd_`
or any `_ru_generated_` file. Its 164 repeated script errors come from another
Russian localization mod (`common/customizable_localization/ru_EUN_custom_loc.txt`,
"Event target link 'location_rank' returned an invalid object"), and `gui.log`
only notes CMF and Glorp overriding vanilla types, which is what they are for.
**Verdict:** nothing of ours errors at load or in play.

### 2026-08 — `auto_build_ru`, does the game pick the file up

**Loaded:** Advanced Auto Build with `auto_build_ru`.
**Expected:** the mod's Mod Menu tab in Russian instead of raw keys.
**Observed:** works as intended — reported by the player.
**Verdict:** the mod is done. Adding keys for a language a base mod does not ship
needs no dependency on it and no load-order care.
**Since:** the base mod moved to 0.9.2 Beta, bringing 40 new keys. Those are
translated but have not been on screen.

### 2026-08 — `rgo_bonus_filter`, buildings panel chip

**Expected:** a filter chip in the funnel menu of a location's buildings panel,
leaving only buildings that gain efficiency from raw materials in the province.
**Observed:** works. Lightly tested — not walked across many provinces.
**Still unrun:** the second chip, in the build panel
(`BuildInLocationLateralView`).

### 2026-08 — `where_to_produce`, the good-first build

**Expected:** for a chosen good, a ranked list of provinces.
**Observed:** correct on screen — `Рудные горы / Оружейные заводы / 1.88% /
4.075` read true against the game's own tooltip.
**Note:** this build was then replaced by a province-first one that was never
run, and the mod was removed. See
[`HANDOFF.md`](HANDOFF.md#why-where_to_produce-failed).

### 2026-08-24 — logs from a live game, EU5 1.3.11

The player sent a full `logs/` after a short session: main menu at 22:02, game
from 22:05:17 to 22:08:32, Sweden, the playset below. Nothing was being tested;
the question was where the errors come from and why the game slows down the
longer it runs. Both were answered from the files, so this is the most useful
run in this log so far.

**Loaded:** Community Mod Framework, Autonomous Diplomats, Construction Manager,
Goods Target, Glorp UI + two local `glorpui_*` addons, Quality of Life by Buddy,
Integration Hotfix, Please Buy My Terrible Art, National Destinies + Nation
Destinies Rus + `nd_ru`, OGAS Optimized, `auto_build_ru`, `rgo_bonus_filter`,
`sheep_farm_food`. Game in Russian.

**Observed — errors.** 39 289 lines across `error.log` and its five rotations.

| source | lines |
| --- | --- |
| the game's own Russian localization | 34 700 (88%) |
| `ForeignCountryView` with no context, vanilla GUI | 1 497 |
| `location_rank` in `common/customizable_localization/ru_EU5_custom_loc.txt` | 484 |
| everything else | ~2 600 |

**31 350 of those were written in the single second 22:05:49**, all from five
search-filter strings, and they rotated `error.log` five times over. Every error
the game produced before that second is gone. That alone is a reason to fix
them: the log is unusable for anything else while they are there.

`game.log` carries 804 more the error log never sees — `Object of type
'country' is not valid for 'longname_ru_GEN'` (576), `'CL_tt'` (152), `'CL_ACC'`
(76) — all from the same custom localization file.

**Observed — the slowdown.** `performance_degradation.log` samples every 3 600
rendered frames, and the two in-game intervals are unambiguous:

| | frames | GUI widgets | memory |
| --- | --- | --- | --- |
| after load | — | 37 768 | 12 675 MB |
| +1 sample | 3 601 | 64 318 (+26 550) | 12 977 MB (+301) |
| +1 sample | 3 601 | 98 195 (+33 877) | 13 214 MB (+237) |

Seven to nine GUI widgets and roughly 280 MB per minute, steadily, while the
frame time itself stays flat at 14–15 ms. So the degradation the player
describes is not the renderer giving up: it is the process growing until the
machine runs out of memory. It starts at 12.4 GB and gains ~280 MB a minute, and
the machine had 20.5 GB free at launch — about an hour and a quarter to
swapping. Reloading the save frees it, which is exactly what the player reports.

**Verdict:** the errors are the game's, not the mods'; `ru_loc_fix` is the
answer to 88% of them. The leak is a separate fault, is real, is measurable
with the game's own counter, and is **not** attributed to anything yet — see
[HANDOFF](HANDOFF.md#the-memory-leak) for the next step, which is two short
runs and one number.

### 2026-08-24 (evening) — `ru_loc_fix` in game, an hour of play

**The first thing this repository has fixed that the log can confirm.**

**Loaded:** the same playset as the morning run, with `ru_loc_fix` added at the
top. No time-acceleration mod this time; the player notes the game degrades
without it too, and that the mod exists to paper over exactly this.

**Expected:** no `FetchData failed for 'AddTextIf(EqualTo_string(` from the five
search-filter strings, and no burst at load.
**Observed:** zero. Not one `CUSTOM_SEARCH_FILTER` line anywhere in
`error.log`, `gui.log` or `game.log`. The 31 350-lines-in-one-second burst is
gone and `error.log` no longer rotates itself out of existence at startup.
**Rate:** 39 289 errors in three minutes became 35 455 in an hour — about twenty
times fewer per minute.

**And the log became readable, which was the other half of the point.** Three
keys nobody could see before now stand at the top, all with the same fault the
filters had: `RGO_BUILD_GOODS_PRICE_IMPACT_ON_COST` 13 950 lines,
`FILTER_BY_GOODS` 3 866, `MARKET_SURPLYS_INFO` 1 650. So the fault was never
about filter strings; it is about reaching a Russian case through
`$GOODS_..._RU_*$` from a panel where the reference loses the scope. Round two
fixes those and eight more.

**One thing the run settled that no amount of reading could.** `gui.log` still
lists seventeen `Failed parsing localized text` lines for keys this mod repairs
— and they are all stamped 23:12:33, sixteen seconds *before* the mod's
localization is merged at 23:12:49. They are the frontend pass parsing vanilla's
value. None of the seventeen appears again anywhere in the run. So a
`Failed parsing localized text` at frontend load is not evidence of anything
being broken in game.

**Verdict:** the approach works and the tooling around it works. What it cannot
do is tell in advance *which* of the ninety-odd keys that reference a declension
helper will fail; only a run says that, which is what `fixes/observed.txt` is for.

**Still not checked by eye:** whether the repaired sentences read correctly on
screen. The log says they no longer fail; it does not say the Russian is right.
The quickest look is a religion tooltip (harmony, purity, honor) and the goods
filter chips in a location's buildings panel.

## Never run

Kept here so it is one list rather than scattered through prose:

- whether anything in `goods_target` runs on a monthly pulse. Its lists,
  readings and ticks are confirmed on screen; nothing periodic is.
- `rgo_bonus_filter`'s build-panel chip.
- Everything `nd_ru` has translated apart from Westphalia — 3 600 keys that have
  never been on screen.

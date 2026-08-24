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

## Never run

Kept here so it is one list rather than scattered through prose:

- whether a tick in `goods_target` reaches script, and why its monthly log line
  never appeared. The list and its readings are confirmed; the pulse is not.
- `rgo_bonus_filter`'s build-panel chip.
- Everything `nd_ru` has translated apart from Westphalia — 3 600 keys that have
  never been on screen.

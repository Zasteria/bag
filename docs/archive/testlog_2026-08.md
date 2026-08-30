# Test log — runs before 2026-08-27

Archived out of [`../TESTLOG.md`](../TESTLOG.md) so the live log stays the size
of a thing a session can afford to read. Nothing here is superseded; it is
simply finished. What these runs settled is in
[`../SETTLED.md`](../SETTLED.md), and this is the evidence behind it.

Ask for a run by name rather than reading the file:
`python3 tools/kb.py <words>`.

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
[`HANDOFF.md`](../HANDOFF.md#why-where_to_produce-failed).

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
[HANDOFF](../HANDOFF.md#the-memory-leak) for the next step, which is two short
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

### 2026-08-25 — the widget experiment, five blocks on one save

The protocol from [`HANDOFF.md`](../HANDOFF.md#the-slowdown), run by the player on a
loaded 1362 save: paused throughout except the last block, two minutes per
activity, a short unpaused skip between blocks so the in-game date separates
them in the log. One sampler row is 3 601 frames, about fifty seconds here.

Only intervals *inside* one block are counted; a row whose date differs from the
row before it spans the skip as well and is thrown out.

| block | what was done | widgets | per frame |
| --- | --- | --- | --- |
| 1 | paused, hands off | **+0, +0, +0** | **0.00** |
| 2 | clicking countries, opening diplomacy | +20 099 | +1.86 |
| 3 | clicking locations, opening the build panel | +3 178 | +0.29 |
| 4 | cycling map modes | +32 254 | +1.49 |
| 5 | speed 7, panning the map, dismissing events | +27 566 in one row | — |

**Three findings, and the first two are settled.**

**Idle costs nothing at all.** Not "little" — three consecutive rows of exactly
+0 across 10 800 frames. Every widget this game accumulates is created by
something the player did. (The first row of block 1 adds 9 624; that is the
interface finishing its build after the save loaded, not idling.)

**Widgets *are* released — but only on teardown.** Quitting the 1337 game at the
start of the run took the count from 38 281 to 2 618 to 367 in two rows. Nothing
comparable happens during play: the largest fall inside the session is −557.

**It is not one window.** That was the hypothesis and it is wrong. Diplomacy
panels and map modes leak at comparable rates — 1.86 and 1.49 widgets a frame,
ten to seventeen thousand per fifty seconds of clicking — and the location panel
leaks too, six times slower but never zero. Whatever is failing to release is
shared by most of the interface, so bisecting panels further is a dead end.

**A caveat about frame time, and it matters.** This run stayed at 14 ms
throughout, at 175 000 widgets, where the hour-long run was at 17–21 ms with the
same count. The difference is that this run was paused for all but the last
block, and a paused game does no simulation. So this run says nothing about the
frame-time cost of widgets; it was designed to measure accumulation and that is
all it measured.

**What it rules out for this repository:** `rgo_bonus_filter` adds to the
location panel, and the location panel is the *lightest* of the three. Nothing
of ours is implicated.

**Next:** the remaining axis is mods against vanilla, and one run settles it —
see [`HANDOFF.md`](../HANDOFF.md#the-slowdown).

### 2026-08-25 — vanilla against the full playset, and the case closes

The run before this one left one question: is the widget leak the mod set or the
base game. This run answers it, and the answer is the base game.

**What the file shows happened.** One process, two games. The first is the full
playset — 37 768 widgets at 1337_04_01, 449 Gfx units, 843 trade wagons, the same
three numbers to the unit as every modded run in this log. Then a return to the
main menu, the playset changed, and a second new game: 36 977 widgets, 448 Gfx
units, **713** trade wagons. A genuinely different and lighter data set, so the
mods really did come off. (EU5 reloads a playset in place; the process never
restarted.)

**The same activity, both sides:**

| | idle, paused | clicking countries and opening diplomacy |
| --- | --- | --- |
| full playset (1362 save) | +0 | +20 099 over 10 803 frames = **+1.86/frame** |
| mods off (1337 start) | +0 | +21 472 over 10 803 frames = **+1.99/frame** |

**Vanilla leaks at the same rate — slightly faster, if anything.** The two sides
are not perfectly matched (a 1362 save knows more countries than a 1337 start),
but the magnitudes are identical and the idle baseline is exactly zero in both.
Nothing in the playset causes this, and nothing in this repository can fix it.

**Confirmed again, twice in one file: the main menu releases everything.**
Leaving a game took widgets from 37 768 to 2 618 to 364 — the same 364 the
process starts with — and memory from 12 952 MB to 9 951 MB, which is what it
was before any game was loaded. So quitting to the main menu and loading the save
again is worth exactly as much as restarting the executable, and costs a
fraction of the time.

**Verdict:** a base-game defect, measured and quantified. The measurement is
finished — but the investigation is *not*, and the owner said so plainly when
this entry first ended with "so file a bug report". They already knew it was
vanilla. What is wanted is a lever from the mod side, or evidence that there is
none. The lead and the next run are in
[`HANDOFF.md`](../HANDOFF.md#the-slowdown--it-is-the-base-game-and-the-hunt-is-for-a-lever).

### 2026-08-25 — `glorpui_hints`, the merge, and a key on screen

**Loaded:** the merged `glorpui_hints` in place of `glorpui_ru_svh_fix` and
`glorpui_svh_extra`.
**Expected:** the societal value tooltip to read in Russian and to carry the
added block.
**Observed:** it does. Screenshot of *Оборона*: Glorp UI's own list in Russian
("Принять реформу правления Система гарнизонов +0.05"), and under it «Также
влияет на смещение» with the four parliament issues about building forts and
«Обороняющаяся сторона в войне +0.10», scrolled. The owner's words: "в целом всё
работает как и раньше".
**Verdict:** **the merge is confirmed.** Two mods in one folder under one id load
and behave as the two did. Nothing in `glorpui_hints` is outstanding.

**And the screenshot showed something else — three raw keys, none of them ours.**
The tooltip read «Дальше продвинуться в сторону
*SOCIEALVALUE_RIGHTITEM_WNTT_GEN*:», «При своём максимальном значении
*SOCIEALVALUE_NAME_GEN* будет оказывать…» and «Поддержать *SOCIEALVALUE_VALUE_ACC*
с помощью действий совета». That is the game's own Russian localization: it
defines seven declension helpers spelled `SOCIETALVALUE_*` and references all
seven as `SOCIEALVALUE_*` — a missing T — in twenty four keys. No overlap, so
every reference resolves to nothing.

`$NAME$` naming nothing neither errors nor logs: the engine prints the name in
capitals and carries on. So this class was invisible to every rule
`ru_loc_fix` had, and it took a screenshot to find one. It has a rule now
(`missing_ref`), and finding it turned up **49 keys in thirteen references**,
which `ru_loc_fix` repairs 45 of. Unfixed and reported: four culture tooltips
whose nearest defined key belongs to a different people.

**Riding on the same rule: `locscan.py` could not see 18 012 keys** — 3.4% of
the tree — because its key regex rejected a line with a comment after the
closing quote. `hre_tt: "0" #True` read as undefined, so every reference to it
looked broken. Fixed; every other rule's count is unchanged, which is how we
know the fix did not disturb them.

**Untested:** all 45 repairs. Any run checks them — the three keys above are on
the societal value tooltip, which is one hover away.

### 2026-08-25 — `ru_loc_fix` round three, and the game files arrived

**Loaded:** the playset with `ru_loc_fix` at 207 keys.
**Expected:** the three raw keys on the societal value tooltip to become words.
**Observed:** they did. The owner: "проверил, что ценности теперь отображаются
правильно".
**Verdict:** **round three confirmed.** `$SOCIEALVALUE_*$` was the fault and the
rewrite to `$SOCIETALVALUE_*$` is the repair, on screen. That also settles the
class: a `$NAME$` naming no key really does print the name, and repairing the
reference really does fix it — which is what makes the other 21 repairs
(`protestant_union.tt`, `catholic_league.tt`, `pirate_events.2.a`) worth
believing without seeing each one.

**And the game files came in**, by `tools/extract_game_files.ps1` on the owner's
Windows box — 597 files, `in_game/common/` up from seven directories to
thirty one. The PowerShell script had never been run when it was written; it
works.

**What the extraction missed, and it matters:** `static_modifiers` — 298 of the
1405 societal value pushes, and the whole "scaling" half of `glorpui_hints`
(fort maintenance, army size, at war, defender in war). The scan of what did
arrive finds **1128 pushes across 22 source types**; the missing 298 are all
that folder. It is not under `in_game/` at all, and the first sweep only looked
there. Both scripts now search the whole install for a manifest directory that
is not where it says, and sweep every `.txt` in the install rather than one
mount — so re-running brings it. `modifier_type_definitions` is missing for the
same reason.

**Still untested:** nothing about `glorpui_hints` changed in this round, so its
extra hint lists are still the ones built before any of this. Rebuilding them
against the arrived files is the next thing, and it needs `static_modifiers`
first.

### 2026-08-25 — culture tooltips, and a theory that did not survive them

**Loaded:** the playset, after the game files went into `reference/`.
**Expected:** to find out whether the Russian culture tooltips resolve, since
every `*_culture_tt` key in the game's Russian custom localization holds a bare
number equal to its own line number minus two — 1755 of them, no exceptions.
**Observed:** they resolve, completely. Screenshot of a location's culture list:
*Вестфальск* opens a full culture tooltip (traditions 179.00, cultural influence
71.63, language, culture groups, the eight countries it is primary for),
*Германск* opens the culture group, *Нижнефранконск* the same. The owner: "вроде
они работают как надо и раньше работали так же".
**Verdict:** **the theory was wrong and this is closed.** The key on screen is
`westphalian_cadj`, which is literally
`#TOOLTIP:CULTURE,$westphalian_tt$, #L Вестфальск#!#!`, and `westphalian_tt`
holds `"1052"` on line 1054 — so the number is exactly what the engine wants
there, or it ignores the argument. Repairing 1755 keys would have fixed nothing
and broken whatever it touched. `PITFALLS.md` carries the lesson: a pattern in
the data explains a fault, it does not establish one.

**And the rest of the game files arrived**, `static_modifiers` among them — not
under `in_game/` but under `main_menu/common/`, found by the by-name search the
last round added. The manifest now names the real paths. The source scan is
complete for the first time: **1426 pushes across 23 source types**, up from
1128.

**So `glorpui_hints` was rebuilt from real game files** — the first time that
has been possible in this repository rather than on the owner's machine. 243
hint lines became **264**, 107 gated became **138**, and nothing was lost. The
twelve new ones are five Italian and foreign leagues the game has added since
the lists were last built, plus two placements of *Обороняющаяся сторона в войне*
and *Парламент в столице*. Defensive goes from 9 lines to 15.

**Untested:** the rebuilt lists. The visible change is the defensive axis
growing by six lines and new international organizations appearing; one hover
over a societal value shows it.

### 2026-08-25 — the rebuilt hint lists

**Loaded:** `glorpui_hints` with the lists rebuilt from the game files now in
`reference/`.
**Expected:** more lines per direction, and no raw keys from the 21 new gated
entries.
**Observed:** "всякого в списках действительно больше. Каких-то глючных ключей и
т.п. не вижу. Всё работает ок."
**Verdict:** **the rebuild is confirmed.** 264 hint lines and 138 gates render
correctly, which also confirms the pipeline end to end for the first time inside
this repository: game files in `reference/` → scan → generator → mod → screen.

**English is out of scope by the owner's decision**, unless the mod is ever
published: "английским языком заниматься не планирую, по крайней мере пока не
появится желание выложить этот мод в общий доступ." The gap stays recorded in
the mod's README; it is not work.

### 2026-08-25 — the availability gates, first round

**Loaded:** `glorpui_hints` with the four new gate kinds, on the owner's own
save (a Catholic German county).
**Expected:** organizations he cannot join and missions in a missions-off game
to disappear; religious aspect lines to start appearing.
**Observed:** "итальянские лиги пропали, миссии тоже". Both confirmed.
**Verdict:** `can_join_international_organization` and
`game_has_missions_enabled` both work as gates in a country scoped
customizable localization. That is the mechanism proven, not just these two
categories.

**Religious aspects: still unknown, and not his fault.** He plays Catholic,
where aspects are set by the Papacy rather than chosen, so the repaired
`religion = religion:X` gate has nothing to show him either way. It needs a run
as a religion that picks its own aspects — Lutheran was his example. Until then
the `country_religion` repair is reasoned, not seen.

**Two things still not filtered, both reported from the screen:**

- **Cabinet actions.** *Дикастерия по евангелизации* and *Влияние Строгановых*
  were on screen for a Catholic German county. They are `office_of_new_converts`
  (`potential` wants a modifier on Kazan) and `stroganov_influences` (`potential`
  wants the Stroganov variable) — national, and both carry a `potential` block
  this mod was not reading. All eight cabinet actions that push have one.
- **Parliament issues.** All four *Поддержка строительства …* lines showed at
  once when only one can ever be valid: `promote_castle_building` requires
  `has_advance = castle_advance` and forbids the better advances, and the other
  three do the same one rung up. The gate was `has_parliament = yes` and nothing
  else.

Both are fixed in the same session: cabinet actions take `potential` + `allow`
verbatim, parliament issues take `has_parliament = yes` plus the estate that
raises the issue plus `potential` + `allow`. Gated lines 167 → **175**.

**A bonus the verbatim copy brings:** two parliament issues carry
`potential = { always = no }` with a comment saying they are event-driven.
Copying `potential` drops them, which is right.

**Untested:** the cabinet action and parliament issue gates. What to look for —
*Дикастерия по евангелизации* and *Влияние Строгановых* gone, and exactly one
*Поддержка строительства …* line instead of four.

**The mod menu switch and the scaling hovers, both unrun.** Two mechanisms
landed together and they fail differently, which is how to tell them apart:

- **The switch.** `Подсказки общественных ценностей → Списки → Фильтрация →
  Показывать всё без фильтра`, in CMF's mod menu. If the row is not there at
  all, registration did not run. If the row is there and the tooltip does not
  change, the `.gui` condition is wrong. Nothing else in the mod moves either
  way.
- **The hovers.** «(масштабируется)» and «(условие)» on the 41 scaled and
  conditional lines. These are game concepts this mod defines. If they work, the
  hover says what the modifier scales with and at what value it is at full size
  — 100 army tradition, 200% of the fort limit, `army_size_percentage > 1.0` for
  the expected-army one. If a text-only concept is not a thing, those 41 words
  render bare or as `ERROR:` and nothing else is affected.

### 2026-08-25 — the switch works, the two clever bits did not

**Loaded:** `glorpui_hints` with the mod menu switch and the scaling hovers.
**Expected:** a switch that restores the unfiltered pool, and a hover on
«(масштабируется)» saying what the modifier scales with.
**Observed:** **the switch works** — "переключатель есть и свою функцию он
выполняет". The hovers do not, and they took text with them: on
*Децентрализация* the *Парламент вне столицы* line rendered as a bare `+0.20`
with no words at all, and on *Традиционализм* the *Доля крестьян в населении*
line as a bare `до +0.10`. In the same list *Банкрот* and *Сословие Племена*
rendered correctly.
**Verdict:** two separate faults, both in the same commit, both silent.

1. **A label that is nothing but a `$reference$` has no floor.** The labels had
   been changed to the game's own `$STATIC_MODIFIER_NAME_x$` so a rename would
   be followed for free. All three keys exist in the game's Russian files;
   `is_bankrupt` rendered and `parliament_outside_capital` and
   `peasants_percentage_in_country` rendered as nothing. What separates them is
   **still unknown** — and the fix does not depend on knowing, because a label
   made only of a reference loses the whole line when the reference fails.
2. **A mod-defined game concept with no `texture` renders as nothing.** The
   hovers were `[Concept('svx_scale_x','(масштабируется)')|e]` with the concepts
   declared in the mod's own `game_concepts/`. The whole data block produced
   empty output — visible on *Банкрот*, which kept its label and its value and
   lost the word between them. Glorp UI's own concepts all carry a `texture`.

**Both are backed out.** Labels are this mod's own strings again, and the
explanation is inline in the same line, which cannot fail:
«Превышен лимит крепостей *(масштабируется: максимум при
used_fort_limit_percentage = 200%)*: +0.10» and «Армия больше ожидаемой *(при
army_size_percentage > 1.0)*: +0.10». Where the game's files say nothing — every
`static_modifier`, *Средняя грамотность* among them — it reads
*(масштабируется, показан максимум)* and claims nothing more. A trigger that
only repeats its own label gets no bracket at all.

**And the checker that would have caught the first one is in.** Every hint label
must carry literal text of its own; a label made only of markup and references
fails the run. Its first version silently passed the very line it was written
for — a non-greedy match started at an earlier `@hint!` and swallowed the whole
entry before it — so it is verified in both directions now: clean on the real
file, and failing on a planted reference-only label.

**Untested:** the inline notes. Everything they replace was rendering before the
change, so the risk is the wording rather than the mechanism.

### 2026-08-25 — the inline scaling notes, rejected on sight

**Loaded:** `glorpui_hints` with the explanation inline in each hint line.
**Observed:** it does not fit. The screenshots show the *labels* truncated —
*Традиции армии* as «Традиции армии ( …», *Во время войны* as «Во вр …», *Доля
крестьян в населении* as «Доля …» — with the bracket spilling across the value
column. And where a modifier declares nothing, "(масштабируется, показан
максимум)" says what «до +0.10» already said. The owner: "чёт супер гига пупер
фу… просто пара бесполезных слов".
**Verdict:** **reverted.** The hint text is byte-identical to the 2026-08-25
version he approved; only the switch's keys are new on top of it. The left half
of a `TooltipScrolledStringPairList` row is narrow and truncates rather than
wraps — in [`PITFALLS.md`](../PITFALLS.md#interface) now.

The arithmetic behind the notes was correct and is kept in
[`research/engine.md`](../research/engine.md): `auto_modifiers` declare
`scales_with` and `potential_trigger`, `static_modifiers` declare neither. It is
recorded rather than used, so a later session does not derive it a third time.

**One correction from the owner, not acted on at his request.** He believes
"expected army" is set by the estates — what they expect the country to field.
The file says only `army_size_percentage > 1.0`, which is a ratio against
something the modifier does not name, so both can be true and the file does not
settle it. Nothing in the mod depends on this any more.

### 2026-08-27 — a logs drop, and the error nobody would have seen

**Not a designed run.** The player was asked to look at the eleven-language
rebuild, said it "looks the same as before", and sent the whole `logs/` folder
instead. It answered three things anyway, one of them a real bug.

**What was loaded.** The 2026-08-25 build of `glorpui_hints`, out of
`Documents/.../mod/glorpui_hints` — **not** the 2026-08-27 rebuild, which had
not been installed. So "looks the same as before" is not evidence about the
rewrite, and the axis he was looking at (*Миролюбие*) could not have shown a
difference in any case: its extra block is two conditional lines,
«В мирное время» and «Крепостей меньше половины лимита», and those words are
identical in both builds. The catalogue lines are the ones that changed.

Also loaded: `3784988919` (`Glorp UI small fix`), the rival addon, alongside
ours. The screenshot shows **our** phrasing — «Даровать привилегию Религиозные
дипломаты», «Принять реформу правления Дипломатические традиции» — where his
says «Предоставить …» and «Добавить … ([government_reform|e])». So on this
playset ours wins the shared keys. Worth knowing and worth not relying on: the
mount lines interleave the two across several passes and the order is not
obviously ours to control.

| | |
| --- | --- |
| **`Missing loc key 'GLORP_UI_SVH_*'`** | **0.** Was 725 per load before this mod existed. The translation half does its whole job. |
| **`ru_loc_fix` round two** | **confirmed.** All six keys it was to repair — `RGO_BUILD_GOODS_PRICE_IMPACT_ON_COST`, `FILTER_BY_GOODS`, `MARKET_SURPLYS_INFO`, `ALERT_HAS_UNMARRIED_CHILDREN`, `THIRD_DESTROY_BUILDING_EFFECT`, `DESTROY_BUILDING_EFFECT` — appear **0 times** in `error.log`. Round one was already confirmed; round two now is. |
| **`glorpui_hints` gates** | **one broken gate, found only because the logs came.** |

**The bug.** One line, once, in `error.log`:

```
[jomini_trigger.cpp:803]: is_core_of: Inconsistent trigger scopes (country vs.
location) at common/customizable_localization/svx_extra_hint_loc.txt:3073
```

`svx_n_sinicized_004` is the Confucian Academy, and its gate is that building's
own `allow` block copied verbatim. **A building's `allow` is evaluated on the
location being built in**, not on the country — `is_core_of = owner`,
`owner = { ... }`, `region`, `market`, `has_building`, `dominant_culture` — and
all 179 of them were being pasted into a `type = country` customizable
localization. `is_core_of` is simply the one strict enough to say so.

On screen this shows as nothing at all: the gate does not answer, so the hint
either never appears or always does, and no player would ever connect the two.

**The repair is the exact question rather than a workaround.** Every building
push here is a `capital_country_modifier` — the building has to be *in the
capital* — so the block belongs in the capital's scope:
`exists = capital capital = { ... }`. `capital` is a country → location event
target (`python3 tools/api.py capital`) and the game writes `exists = capital`
in front of it 76 times in its own `common/`.

**And the rule went into the checker.** `check_gate_scopes` in
`mods/glorpui_hints/tools/generate.py` reads **Supported Scopes** out of the
engine's own trigger dump (`reference/game/docs/triggers.log`) and reports
any trigger called in country scope
that the engine does not allow there. It follows only the outer scope — a nested
`capital = { ... }` is a different scope and is left alone, which is precisely
what the repair is. Checked both ways: it catches the old line and passes the
new one.

**Still unrun, and unchanged by this:** everything the 2026-08-27 rebuild added.
The cheapest single check is now known — turn the mod menu switch
«Показывать всё без фильтра» on and hover **Децентрализация**: the subject type
lines should read «**Тип ленника** …» where the old build said «Тип вассала».

### 2026-08-27 — the concept tokens render, and in two languages

**The change with the widest blast radius is confirmed.** Screenshots of the
*Decentralization* tooltip with the mod menu switch «Показывать всё без фильтра»
on, in Russian and then in English — the player switches language from the
console on the fly, which turns out to make testing the other ten languages
almost free.

| expected | observed |
| --- | --- |
| the catalogue lines open with the game's own word for the category, from `[religious_aspect\|e]` and friends | **yes.** «**Религиозная особенность** Двенадцать представителей», «**Тип ленника** Феод / Пронии / Удж-бей / Вассал» — where the 2026-08-25 build said «Аспект веры» and «Тип вассала» |
| the concept renders as an encyclopedia link, not plain text | **yes** — the category word is coloured and hoverable, the object name beside it is not |
| English exists at all | **yes.** "Religious Aspect The Twelve Emissaries", "Subject Type Fiefdom". The old build shipped no English `SVX_*` keys, so this block would have been raw keys |
| the English openers are Glorp UI's own | **yes** — "Enact the Traditional Distribution Policy" |
| the unfiltered block replaces the two filtered ones | **yes**, and the block titles translate: «Влияет на смещение (без фильтра)» / "Pushes towards this (unfiltered)" |

So `catalog` in `languages.py` stays a concept token, and the seven Russian
terms it corrected are the game's own words on screen. **That was the one change
that could have gone badly, and it did not.**

**One thing the hot language switch does not do:** the vanilla block title
«Дальше продвинуться в сторону децентрализации:» stayed Russian in the English
screenshot while everything this mod owns switched. Not our key and not our bug
— but it means a language switched from the console is not a clean test of
*vanilla* strings, only of ours. A real check of another language wants a
restart.

**Still unconfirmed:** the five advance-gated privileges, the building `allow`
repair from earlier today, and nine of the eleven languages.

### 2026-08-27 — the upload button exists, and it is hidden

Two screenshots, an hour apart, and the second corrected the first.

**First read, wrong:** the launcher's «Модификации и дополнения» shows playsets,
order and checkboxes and nothing about publishing, so EU5 was written up as
having no first-party upload.

**It has one.** The player found it: the same screen, the row **«Выбранные
модификации: N/M»**, a small **sandbox icon** in that row next to the gear. It
opens **Mod Tools**, with tabs *Create mod* and *Uploaded mods*, the whole of
`metadata.json` as a form — Name, ID, Path, Version, Supported game version,
Description, and the tag list as checkboxes — and a button reading **Upload New
Mod**.

It is documented, in one sentence, in the middle of a dev diary about writing
events and situations:
[Tinto Talks 85, Modding](https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-85-22nd-of-october-modding.1864004/)
— *"navigate into the Mods & DLCs Menu in the top right corner and then open the
Mod Tools view by clicking on the sandbox icon next to Selected Mods"*. That
diary is otherwise entirely about authoring; publishing is that clause and the
button in a screenshot. The wiki does not mention it at all, which is why it
documents the third-party uploader instead — and why an hour went on finding a
button that was on screen the whole time.

**So the route is the game's own**, and the tag checkboxes in that form are the
authoritative tag vocabulary — the same one four mods here were outside of.
[PDX Workshop Manager](https://github.com/kaiser-chris/pdx-workshop-manager)
stays as the fallback; `mods.bat → 5 → «к»` still writes its config.

Also confirmed from the same screenshot: the load order the player actually
runs puts `Glorp UI` at 3 and `Glorp UI - Societal Value Hints` at 4, directly
after it, which is what the declared dependency is for.

## `where_to_produce`, the first seven loads

Moved out of the live log when it outgrew its budget; the fourth and fifth
runs are still there.

**2026-08-30 — `where_to_produce`, third load. The map mode works; the design of
the picker did not.** Five screenshots.

- **The map mode paints**, and it is the thing the owner wanted: Wallachia green
  as chosen, the ticked Carpathians dark as the zone. Its name showed as
  `mapmode_bag_wtp_selection_name` — a map mode's name key is
  `mapmode_<key>_name`, not `<key>`.
- **The target picker opens and works, and closes after each pick.** That is the
  generic action's lifecycle; `fire_generic_action` fires with a supplied target
  rather than reopening the panel, so there is no script-side way to keep it up.
  Area granularity is the mitigation.
- **Asking the player for the production method was wrong.** Owner's words: the
  mod is meant to find the best method for his ground, and asking him to guess it
  first "полностью ломает конечную суть мода". Rebuilt: the good is the only
  question, every method for it is scored per location, and the row names the
  building that won.
- **Six region groups were a bad frame.** Replaced by five continents, which also
  removed the zone walk entirely — a location's continent is a plain trigger.
- **The window listed nothing when no region was ticked**, so nothing could be
  trimmed. It now lists the provinces something is picked in, which is its actual
  job and what bounds it.

**2026-08-30 — `where_to_produce`, second load. The data half works; the picker
is capped at twenty.** Five screenshots.

- **The result table reads.** "Бельцы — 9.25% (2/2)", fifty rows, descending.
  That is a location name out of a global variable and two script values printed
  from a localization key — the mechanism nothing in this repository had ever
  done, and the reason the first `where_to_produce` was worth attempting again.
- **The region lists render** with the game's own names ("Балканы", "Карпаты",
  "Польша"), so a list row's label set to `flag:<game key>` works and arrives
  translated. The ticks reach script: the zone came out at 260 locations in 53
  provinces.
- **A CMM dropdown is clickable only to its twentieth option.** Reported as
  "некоторые здания просто не выбираются". Found in CMF: an option click runs
  `CMM_MarkDropdownSelection_<index>` and CMF defines `_0` to `_19`. The
  218-option method picker was replaced by two lists — 47 goods, then at most 20
  ways to make the chosen one.
- **The selection window's rows collapsed to zero height**, all but the one
  expanded province, which piled them at the left edge. The item was wrapped in
  a `widget`, which does not size itself to its child; Advanced Auto Build puts
  the row type directly in `item`.
- **The window was the wrong shape for the job anyway.** The owner wanted what
  Advanced Auto Build actually does: the game's own target picker, which is a
  `select_trigger` block inside a `generic_action` — search box, sortable list,
  map highlight, and a map click picking the same thing a row does. AAB's
  restriction to owned land is its own `interaction_source_list`, not the
  engine's; vanilla's actions mostly give no source and filter with `visible`,
  which runs in the candidate's scope.

**2026-08-30 — `where_to_produce`, first load. The tab renders; no list on it
does.** Screenshot: the Mod Menu tab "Где производить" shows the group "Здание и
метод" with its three settings (the method dropdown, the tick, the button) and
nothing else — no region groups, no result table. Diagnosed from the files, not
guessed: `cmm_register_settings_list` declares `is_ordered` and the generated
call omitted it, so all six region lists and the result list died at
registration. Fixed; `tools/check_cmm.py` grew the missing-argument check that
would have caught it.

Two things the same screenshot settled without being asked:

- **The method dropdown is unusable at 218 options**, and the label was the
  reason. The control is about 165 pixels and elides the tail, so "good, icon,
  building, method" showed the good — which repeats for twenty rows — and cut off
  the method entirely. Relabelled to icon, building, method, and sorted by
  building so one building's methods sit together. Better, and still not a
  substitute for a real picker.
- **Registration itself works.** The dropdown, the tick and the button all
  rendered with their names and descriptions, so `cmf_on_mod_registration`, the
  mod id, the tab and the group keys are all right.

**2026-08-30 — `where_to_produce`, fifth load. The tabs and the table are on
screen; the row says too little.** One screenshot of the «Расчёт» tab, cloth
guild ranked.

- **The three tabs render** — «Товар», «Земля», «Расчёт» — and the button and
  the table are under the right one. The tab/setting key collision is behind us.
- **The table fills**, one row per province: twelve different names down the
  screen where the fourth run repeated one. The building prints
  («Гильдия прядильщиков»).
- **Every row reads 10.00%.** Not a bug: that method's only raw input is
  `fiber_crops`, so any province with fibre crops is at the ceiling. It is,
  though, the reason the ranking looks like it is not ranking — the row does not
  say what the number is made of.
- **What the owner asked for, off this screen:** the row names a location and he
  reads it as a province («показывается только 1 какая-то локация»); he wants
  the province, with its locations under it; which of the building's methods
  won; and the goods the bonus is made of («должно показывать прядильные
  культуры»).
- Regions, the age filter and `error.log` were not reported and stay open.

**2026-08-30 — `where_to_produce`, fourth load. Everything asked for worked.**
Owner: the goods tick moves; the ranking "работает, подбирает"; the map picker
"выбирается всё как надо"; nothing worth pulling out of `error.log`. That closes
the mod's whole mechanism — the scoring, the picker, the window, the map mode.

Four things the run asked for, all built and none of them loaded yet:

- **Tabs.** Five groups on one scroll. A CMM tab is just a `tab_id`, but a tab
  key and a setting key are both `<mod>__<id>_name` — so a tab and a list may not
  share a name, and the zone list had to become `continent`.
- **Regions back beside the continents.** A ticked continent paints the whole
  screen; the good case was one region ticked with its neighbours addable.
- **Methods the age has not reached were being recommended.** The unlock data is
  in the tree now: `1_building_unlocks.txt` gates 119 buildings by age and
  `3_production_method_unlocks.txt` gates ten methods directly, so
  `can_build_building` in country scope plus `has_advance` answers "available to
  me now". This is what `docs/archive/where_to_produce.md` recorded as
  unanswerable; `common/advances/` was not in the tree then.
- **The table ran out of rows before it ran out of answers.** Every location of a
  province scores the same, so it now holds one row per province.

**2026-08-30 — `where_to_produce`, sixth load. The results window works; the
province is not what the game says it is.** One screenshot, everything selected.
Owner: «в целом вроде ок».

- **The window renders and does its job.** Rows, the area, 10.00%, the building
  **and the method after the colon** — and the methods differ between rows,
  «Гильдия прядильщиков льна» against «…шерсти», which is the scoring choosing
  per province in plain sight. The plus expands a row into its locations, each
  with its raw material and «Добавить».
- **A province is not a province.** Two rows, «Измаил» and «Молдавская провинция
  Бессарабия», are two halves of one province split by ownership — the game
  splits a `province` by owner and names the pieces that way. Ranking the halves
  answers for half the ground, and the answer would move on the day they join,
  which is the day the mod plans for. Now one row per `province_definition`,
  scored over every location in it, with each location's owner shown under the
  row. **Which of the two the engine's own bonus counts is still unknown** —
  `docs/research/engine.md` has the one-hover test that would settle it.
- **The window drew outside itself** — frame ending where it should, header and
  rows carrying on past it over the game's top bar. One description line:
  `autoresize` with no `maximumsize` does not wrap, it grows, and
  `allow_outside = yes` let it drag every expanding row with it. Bounded now, in
  both of this mod's windows, and `widgetanchor = center` added to match vanilla.
  Advanced Auto Build has the same defect, which is where the shape came from.
- **Unclear from the screenshot: the «Из чего» column looks empty.** The goods
  icons in the *location* rows draw fine, so `GetGoodsIcon` works; if the column
  is genuinely empty the fault is the `bag_wtp_goods` variable list. The row now
  prints «supplied/total» beside the icons, which tells an empty list from an
  icon that will not draw without another round trip.

**2026-08-30 — `where_to_produce`, seventh load. Whole provinces and the frame
hold; the goods icons do not.** Two screenshots, «в целом вроде ок».

- **The window is inside its frame** and **a row is one whole province** —
  «Бессарабия» as a single row, its locations under it with the owner's flag
  beside each. The owner's flag: «нахер не нужно, но и не мешает, пусть
  останется».
- **The goods icons never drew, and the count off the same list did.** «1/2» and
  «2/2» print correctly beside an empty space — so `bag_wtp_goods` holds the
  right items and `GetDataModelSize` reads them. What was missing is the
  `datacontext` on the datamodel item: the province rows work because they carry
  one, and this one addressed `Scope.GetGoods` from inside the type instead.
  Vanilla's own scope lists set `datacontext = "[Scope.Get<Type>]"` on the item
  and then use the type name, `GetGoodsIcon(Goods.Self)`.
- **Lakes and sea zones were in the expanded rows**, a screenful of «Ничья земля»
  under every coastal province. `ProvinceDefinition.GetLocations` hands out
  everything. Hidden now on `Location.IsPossibleToOwn`, and the whole mod's
  notion of ground moved from `is_land` to `is_ownable` — "not sea, lake or an
  impassable" — so nothing unbuildable enters the plan through the map picker
  either.
- **The count drifted with the number of icons**, «1/2» sitting a few pixels
  right of «2/2». An hbox sizes itself to its children, so one icon fewer moved
  everything after it. Placed in a plain `widget` now.
- **The method in the row is enough on its own** — the owner reads the recipe off
  its tooltip. The icons stay because a method with several inputs still needs
  them, and the count says what the icons cannot when they fail to draw.

### 2026-08-30 — `where_to_produce`, eighth load, with logs. Everything asked for
is on screen; the map picker is the one thing left.** Owner: «в остальном —
круто».

- **The goods icons draw**, the lakes are gone from the expanded rows, the count
  sits still. The `datacontext` on the datamodel item was the whole of the icon
  fault.
- **The whole-province rule is confirmed by eye**: Bessarabia is split by a
  border and the horses in the far half count towards its number, which is what
  the mod means by planning for the ground rather than the border. The engine's
  own tooltip was not the thing compared, so *that* question stays open — it is
  just no longer urgent.
- **`error.log` carries nothing of this mod's**, first time it has been read for
  it. 1706 of its 2742 lines are `jomini_custom_text.h` on vanilla Russian,
  341 are a null promote in a loc string, and the four `Widget cannot have a
  position in a layout` are Glorp UI's.
- **`gui.log` had 124 lines that were ours**: `bag_wtp_select_window.gui:177`,
  `Widget cannot have a position in a layout` — a `parentanchor` on a button that
  is a direct child of an hbox. Anchors belong inside a plain widget; an hbox is
  a layout and places its own children.
- **The icons sat a column apart.** An hbox given more width than its children
  spreads them across it. Left to hug its content now.
- **And the ask, for the fourth time: the game's own map selection.** Both
  screenshots are the same mechanism — `military_objective_group.gui`, driven by
  `MilitaryObjectiveGroupView` with `GeographyGlue` rows. **Engine objects: a mod
  cannot instantiate either**, and there is no on_action for a map click, so a
  window of one's own cannot be told what the player clicked. What *is* reusable
  is `PdxGuiWidget.SetHighlight{Region,Area,Province,ProvinceDefinition,Location}`
  — the game's own map highlight, callable from any `.gui`.

### 2026-08-30 — `where_to_produce`, ninth load. The tree came up empty, and the
ranking was ranking the wrong thing.** Three screenshots.

- **All four columns of the tree were empty, headers and all four frames drawn.**
  That pairing is the diagnosis: the header's `blockoverride` reached the
  instance and the rows' did not, because the rows' `block` was nested inside the
  `blockoverride` of the scrollbox. A block inside a blockoverride never
  resolves. The four columns are written out now, no column type at all.
- **The goods icons still sat a column apart** after being given no width: the
  spreading was the `icon` widget inside an hbox, not the hbox's size. They are
  text icons now — `[Goods.GetIcon]`, which is what vanilla writes in its own
  strings — and a text hugs its glyph.
- **The ranking put forest villages at the top of a weapons search.** Not a bug
  in the scoring; the scoring was answering the wrong question. A village wants
  one raw material, so it reaches the full 10% anywhere, and it produces 0.2
  weaponry a level against a weapon guild's 1.0 and a factory's 4.0. Ranking is
  by **effective output** now — `output * (1 + bonus/100)`, the bonus being an
  efficiency percentage and therefore a multiplier — and villages are scored on
  their own side, so a row shows two answers: the best built-up building and the
  best village.
- **The Mod Menu table is gone.** It said the same thing as the window one line
  at a time, and it was the only thing holding the answer to fifty rows.
- **The owner uses the region lists and nothing else** to frame a search:
  Карпаты in Europe, then the map picker for Валахия, Молдова, Трансильвания.
  That answers what six runs of "the region lists are untested" was asking.

### 2026-08-30 — `where_to_produce`, tenth load. The rows collapsed into each
other, the tree was still empty, and the selection window was the wrong idea.**
Two screenshots.

- **The province rows overlapped.** The card holding a row is a `widget`, and a
  widget does not size itself to its child: it was given
  `layoutpolicy_vertical = preferred` and no height when the row grew a second
  line. Fixed heights all the way down now — 60 for the card, 28 per answer.
- **The tree columns were still empty** after being written out, so the block
  nesting was not the fault either. Whatever it is, it is not worth another
  round trip: the whole selection window is deleted.
- **And the owner said what to do instead**: «нахрена для этого всего вообще
  целое отдельное окно? Просто засунь кнопки „выбрать…“ в окно результатов.
  Чтобы я прямо там выбирал и он мне прямо сразу показывал результаты после
  каждого изменения границ.» So the three map-picker buttons, the running count
  and «Очистить выбор» are in the results window, and **every pick re-ranks
  while that window is open** — the answer follows the borders as they are
  drawn.
- The scoring, the two-line row and the goods icons from the ninth build could
  not be judged under rows that overlapped; they come back for the eleventh.

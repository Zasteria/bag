# Handoff

Where the three mods stand, and what a fresh session needs to carry on. Read this
first, then [`RESEARCH.md`](RESEARCH.md) for how EU5 modding actually works —
most of that was learnt the hard way and will save a repeat.

## Settled — do not measure any of this again

Five runs of the game went into the answers below, most of them an evening's work
for the owner. The numbers are in [`TESTLOG.md`](TESTLOG.md). Asking for any of
this a second time spends the one resource this repository cannot generate for
itself, so read the table before designing a test.

| question | answer | where |
| --- | --- | --- |
| Whose fault are the localization errors? | The base game's Russian files. 88% of 39 289 lines. | TESTLOG 2026-08-24 |
| Did the filter fix work? | Yes. Zero `CUSTOM_SEARCH_FILTER` lines in an hour; the error rate fell about twentyfold a minute. | TESTLOG 2026-08-24 evening |
| Are the 17 `Failed parsing localized text` in `gui.log` real? | No. They are stamped sixteen seconds before the mod's localization is merged — the frontend reading vanilla on the way past. | TESTLOG 2026-08-24 evening |
| Is the slowdown memory running out? | No. The working set peaks and then falls; what grows without limit is the widget count. | TESTLOG 2026-08-24 evening |
| Do map icons / units / game time cause the widget growth? | No. It scales with neither game days nor unit count. | [the slowdown](#the-slowdown--it-is-the-base-game-and-the-hunt-is-for-a-lever) |
| Does idling cost anything? | No — exactly +0, twice, across 10 800 frames each. | TESTLOG 2026-08-25 |
| Is it one bad window? | No. Diplomacy +1.86/frame, map modes +1.49, locations +0.29; none zero. | TESTLOG 2026-08-25 |
| Is it the mod set? | No. Vanilla leaks +1.99/frame against the playset's +1.86. | TESTLOG 2026-08-25 vanilla |
| Is it anything in this repository? | No. `rgo_bonus_filter` lives in the lightest panel of the three. | same |
| Does the merged `glorpui_hints` load and work? | Yes. Both blocks render, in Russian, on the same save. | TESTLOG 2026-08-25 |
| Can a mod free widgets? | No. `dump_data_types` has no `Destroy`/`Clear`/`Free`/`Collect`/`Prune` on any GUI type. | research/engine.md |
| Is there a widget limit or pool size to raise? | No. `NGUI` in `00_defines.txt` is twenty lines of name lengths, queue sizes and alert thresholds. Nothing about pools, caches or arenas. | research/engine.md |
| Why keep `nd_ru` when `nation_destinies_rus` translates 93% of the mod? | **Because that one is Google's machine translation and behind on versions.** The owner loads `nd_ru` *after* it on purpose: where ours has a key, his good translation wins; everywhere else the machine one fills in. This was decided before this repository existed, and has now been asked twice. | [below](#somebody-else-has-translated-national-destinies-nearly-all-of-it) |

**And one thing the owner has already rejected as an answer:** "report it to
Paradox". They know it is a base-game defect and know other players have it. The
job is to find something that helps from the mod side, or to establish with
evidence that nothing can.

## State

**The mod menu's update loop broke on somebody else's update, and is fixed.**
2026-08-29: the owner ran `mods.bat → 2` against the 2026-08-28 builds of
Advanced Auto Build and Glorp UI and both translation generators stopped the
run. The whole run, and what each of the four faults was, is in
[`TESTLOG.md`](TESTLOG.md#2026-08-29--modsbat-an-update-run-on-the-owners-own-machine);
the rules that came out of them are in
[`PITFALLS.md`](PITFALLS.md#the-reference-tree-changes-under-you). What matters
here is what is now true and what is not:

- **verified by replay** — the run was repeated against copies of both mods
  rewritten into the new shapes. `tools/refresh.py` comes out green, with a note
  naming the nine keys Advanced Auto Build deleted, and `glorpui_hints` rebuilds
  all eleven languages and still finds all five advance-locked privileges;
- **not verified** — the *real* 2026-08-28 files. They are not in this tree yet;
  bringing them in is `mods.bat → 2` on his machine, and it is the next thing
  that run should show;
- **not verified at all** — the Steam side, below.

**Updating a mod in Steam: rewritten, never run.** The owner's own report is
that the menu never actually updated a workshop mod for him and he still
unsubscribed and resubscribed. It compared *dates* — Steam's installed-at
against the workshop's updated-at — and Steam stamps an item as updated when it
notices the update, whether or not the files followed. It now compares **build
ids**: `manifest` out of `appworkshop_3450310.acf` against `hcontent_file` out
of `GetPublishedFileDetails`. Two that differ are two different sets of files and
nothing about it is a guess; anything Steam has no build id for still falls back
to dates, and the report says which of the two answered. With it:

- any mod can be re-fetched on demand, whether or not the check thinks it is
  behind — "ничего не отстаёт" was exactly the answer that used to be wrong;
- what steamcmd actually brought back is compared against what the workshop
  serves, and said out loud when they differ — that is the one case where
  unsubscribing and resubscribing is still the answer;
- copying into `reference/` stops first when the Steam folder itself is behind,
  because that path copies out of the Steam folder and would otherwise bring in
  the old version and rebuild every generator against it without a word.

**None of that has run against a real `appworkshop_3450310.acf`.** It was
exercised against a synthetic one — manifests read correctly, and a mod whose
dates match but whose build id differs is correctly called outdated — and the
field names are Steam's own. The first real run is the test. If Steam's record
turns out to hold no `manifest` for these items, every mod falls back to dates
and the menu says so on the line above the table; that is the failure to look
for.

**The reference tree moved, and nothing broke.** Construction Manager 2.2.12 and
Community Mod Framework 2.4.1 came in, the second a real reorganisation of the
CMM list code. `tools/refresh.py` rebuilds everything from them and reports
clean: no generated file changed, and `tools/check_cmm.py` — the check that every
CMM macro is called with arguments CMF declares — still passes. What 2.4.1 added
is in [`research/cmf.md`](research/cmf.md#what-cmf-241-added).

**`ru_loc_fix/` — working, round one confirmed in game, rounds two and three unrun.**
Repairs the markup in the game's own Russian localization. It came out of the
player's question about why their `error.log` is full: the answer is that 88% of
it was the base game's Russian files, not any mod. **207 keys** now, in seven
shapes — unclosed brackets, accessors `dump_data_types` does not have, `Custom()`
applied to a string, roots that are nothing, keys reaching a Russian case through
a helper reference, wrong scopes the game named in its own log, and `$NAME$`
references to keys that do not exist. Nothing is
retranslated; only the markup changes.

The mod is generated. `mods/ru_loc_fix/tools/locscan.py` is the rule set, split
into hard rules (cannot fire on a healthy key) and advisory ones (compare against
English, need a person). `generate.py` refuses to write a key that no longer
exists, a key that is no longer broken, or a repair that still trips a rule; 185
of the 207 are search-and-replace against whatever the game ships that day, so a
patch that rewrites the sentence keeps the repair. It runs from
`tools/refresh.py` with everything else.

**Confirmed in game, 2026-08-24.** An hour of play with the mod loaded: not one
`CUSTOM_SEARCH_FILTER` line in the log, and the burst that used to rotate
`error.log` five times inside one second is gone. The rate fell from 39 289
errors in three minutes to 35 455 in an hour — about twenty times fewer per
minute — and the log is legible for the first time.

What that legibility bought was round two. The same fault turned out not to be
confined to filter strings: `RGO_BUILD_GOODS_PRICE_IMPACT_ON_COST` (13 950
lines), `FILTER_BY_GOODS` (3 866) and `MARKET_SURPLYS_INFO` (1 650) took their
place, each reaching a Russian case through `$GOODS_..._RU_*$`. Eleven more keys
went in for that round.

**Round three came from a screenshot, 2026-08-25, and it is a class the log
cannot report.** A `$NAME$` reference to a key that does not exist neither errors
nor logs — the engine prints the name, in capitals, inside the sentence. The
societal value tooltip read «Дальше продвинуться в сторону
*SOCIEALVALUE_RIGHTITEM_WNTT_GEN*:» because the game defines seven declension
helpers as `SOCIETALVALUE_*` and references all seven as `SOCIEALVALUE_*`. The
new hard rule `missing_ref` finds **49 keys in thirteen references**; 46 are
repaired and 3 are deliberately not.

**Confirmed on screen 2026-08-25** — the owner reports the tooltip reads
correctly now. That settles the class and not just the key: a `$NAME$` naming no
key does print the name, and repairing the reference does fix it.

**The culture list arrived and settled the last four.** `common/cultures/`
defines 1751 cultures. `inca_culture` is not one of them and `inka_culture` is —
a c for a k — so `country_history_CSU`, which is Cusco's country history and does
render, is repaired. The other three are declensions for `even_culture`,
`halkomelemt_culture` and `lalagyr_culture`, none of which the game has: nothing
can ask for the declension of a culture that does not exist, so those keys are
unreachable and stay as they are. Pointing them at the neighbour would be worse
than leaving them — Even and Evenk are two different peoples. The reasoning sits
in `fixes/observed.txt` so it is not derived a second time.

**A thing the culture list exposed, checked, and closed.** All 1755
`*_culture_tt` keys in `EU5_customizable_localization_ru_culrel_l_russian.yml`
hold a bare number equal to their own line number minus two — for all 1755, with
no exceptions, and the 624 keys of the `X_tt` family alongside them are numeric
too. They are used as `#TOOLTIP:CULTURE,$X_tt$,`, where a culture key looks like
it belongs, so this was written up here as "every culture tooltip in the Russian
localization is handed a line number".

**That conclusion was wrong, and a run said so.** The owner hovered the culture
list in a location panel on 2026-08-25: the tooltips are complete and correct —
traditions, language, culture groups, the countries the culture is primary for.
The text he hovered is `westphalian_cadj`, which is literally
`#TOOLTIP:CULTURE,$westphalian_tt$, #L Вестфальск#!#!`, and `westphalian_tt`
holds `"1052"` on line 1054. So the number *is* what the engine wants there, or
the engine ignores the argument; either way nothing is broken.

**Do not repair this.** The line-number correlation is a real and verifiable
fact about the file and it means nothing for behaviour. Changing 1755 working
keys on the strength of it would have been the most expensive mistake in this
repository. What the episode is actually worth is in
[`PITFALLS.md`](PITFALLS.md#localization).

**And the rule found a hole in the checker.** `locscan.py`'s key regex required a
line to end at the closing quote, so a key with a trailing comment —
`hre_tt: "0" #True` — was not a key to any rule in the file. **18 012 keys, 3.4%
of the tree**, invisible. Fixed; every other rule's count came back identical,
which is how we know nothing else moved.

**Round two keeps the grammar.** The first fix replaced declined forms with
nominatives. This one does not have to: the same strings hold the promote both
ways — `RGO_BUILD` has `[GOODS.GetDefaultMarketPrice]` inline, which works, next
to `$GOODS_GetName_RU_GEN_lower$`, which does not — so the scope is present and
it is the *reference* that loses it. `fixes/expand.txt` writes the helper out
inside the key, seventy five `AddTextIf` tests and all.

**What still errors, and what each would need.** After round two lands, roughly
12 000 lines an hour should remain, and almost none of it is localization:

| | lines/hour | what it would take |
| --- | --- | --- |
| `ForeignCountryView` evaluated with no view context | 5 118 | vanilla's own `foreign_country_lateralview.gui`, which Glorp UI copies verbatim — the bug is Paradox's, and fixing it means carrying a copy of a large `.gui` |
| `ActionGroup.GetActions` at `gui/shared/cards.gui:2363` | 2 476 | the same: a vanilla `.gui` |
| `longname_ru_GEN` finding no entry for a country, in `game.log` | 4 108 | **nothing.** The file is in the tree now and the fault is not in it: `country_ru_flavor` ends in a `fallback = yes` entry and every one of its 218 suffixed keys exists, so the object being passed is an invalid country and that is the caller's doing |
| character nicknames: `Select_CString(Character.IsFemale, …)` given a `Container` | ~1 300 | unknown. The same 180 keys work everywhere else, so it is one caller and nothing in the log says which |
| `Custom()` handed a location where it wants a country, in `debug.log` | ~390 | unattributed. New in the second run, but the shape (`predlog_vvo`, `CL_tt`, `CL_tt`, `CL_PREP` in that order, 98 times over) matches no key this mod touches |
| other mods' scripts, `D008_pronoia`, an audio arena, an input stack | ~50 | their authors', not ours |

The `location_rank` errors of the first run — 484 lines — did not recur. If they
come back: `LR_GEN` and its four siblings in
`in_game/common/customizable_localization/ru_EU5_custom_loc.txt` test
`location_rank = location_rank:x` with no fallback, so a location that has no
rank at all falls through. That file is 49 653 lines and overriding it wholesale
to add one fallback is not worth it.

**`goods_target/` — paused, half working, four faults known.** An addon to
Construction Manager: build the producers of goods you tick until they are as
cheap as you asked, subsidising them on the way.

On screen and right: registration, both goods lists (74 rows, every good in the
game), the ticks, and the price readings, which matched the game's own
construction tooltip.

Not right, and none of it logs anything: **nothing runs on the monthly pulse**
(the counter stays at zero), the readings never change and the game loses ticks
while the menu is open (both because 74 row labels each evaluate a live script
value every frame), and the Target column printed a key (missing format keys —
diagnosed, fixed, unverified).

The mod's README has each fault, what is proven about it, and the cheapest next
step for the one that matters: Construction Manager runs on the same pulse, so
whether *its* automation still works in the same save says whose fault it is,
and costs nothing to check.

Still nothing builds and nothing is subsidised.

**`rgo_bonus_filter/` — working, in use.** Two filter chips, one per building
list. Nothing outstanding.

### Somebody else published a Glorp UI hint addon too — and it is not the same mod

`Glorp UI small fix` (workshop 3784988919, in `reference/` for comparison,
version 0.1) appeared in late August 2026 and looks at first glance like our
mod. It is not. Measured, not skimmed:

| | `glorpui_hints` (ours) | `Glorp UI small fix` |
| --- | --- | --- |
| keys per language | 1128 | 768 |
| of them Glorp UI's own hint keys | 759 | 763 |
| **new hint content** | **364 keys** | 5 |
| languages | **11** (2026-08-27; was Russian) | 10 (no English) |
| gating | 253 lines by country trigger, plus 5 by `has_advance` | 3 privileges by `has_advance` |
| CMM setting | yes | no |

**The overlap is the translation half only.** Both give Glorp UI's ~760
`GLORP_UI_SVH_*` keys a Russian text, and on those keys whichever mod mounts
later wins. The styles differ: he keeps Glorp UI's `[government_reform|e]`
concept link and puts it in brackets after the name; ours replaces it with the
Russian phrase and drops the link.

**What our mod does that his does not exist to do at all:** the 364 keys of hint
content from the twenty source kinds Glorp UI's generator never reads. His mod
translates Glorp UI's list; ours also *extends* it. That half is untouched by
him.

**What he had that we did not — both taken on 2026-08-27, neither by copying
his text:**

- **Ten languages.** ~~The one place his mod was ahead.~~ Ours ships eleven
  now, English included. What was actually worth taking from his files is a
  *shape*: he puts the verb after the object in German, Turkish, Japanese and
  Korean, which is why our openers are written with a `{ref}` placeholder rather
  than as a prefix. A prefix-substitution design cannot express those four
  languages at all. The words are ours, and fourteen of the category nouns are
  neither his nor ours — they are game concepts, which is a route he did not
  take and which is both free and more accurate. See
  [`research/translation.md`](research/translation.md#shipping-in-all-eleven-languages).
- **A gate for privileges locked behind an advance.** Glorp UI's
  `glorpui_svh_privilege_takeable` filter reads a privilege's `potential`/`allow`
  and nothing else, so a privilege whose only lock is an advance's
  `unlock_estate_privilege` is recommended to a country that cannot take it. His
  census is exact and reproduces here: **10 vanilla privileges are locked that
  way**, four of them appear in Glorp UI's hints, and `ayans_privilege` is
  already filtered by `has_or_had_tag = TUR` in its own potential — so **three
  leak**: `peasants_yeomanry`, `jaysh_armies`, `ghazi_privilege`. **Done, from
  the data**: `generate.py` scans `common/advances` for `unlock_estate_privilege`
  rather than listing the three, so a patch that locks an eleventh is picked up
  by a rebuild, and it gates `ayans_privilege` too — the tag check in its
  potential is not the advance, and both have to hold. Five hint keys in all.
  **The mechanism is his and it is the real prize**: a `customizable_localization`
  *cannot be overridden*, first definition wins, later duplicates dropped with
  `gamedatabase.h: Duplicated key ... will not be created from file` — his file
  carries that log line. So the base mod's rule is untouchable and the way round
  is to take over the localization key it prints. Now in
  [`PITFALLS.md`](PITFALLS.md#localization).
- **Four Glorp UI keys whose Russian is broken grammar** — `GLORP_UI_AVG_CONTROL`
  ("Средняя значение"), `GLORP_UI_AVG_PROXIMITY`, `SWAP_TO_AVG_CONTROL`,
  `REFRESH_AVG_PROX` ("Обновить Средняя расстояние"). Note his file's header
  claims they are *absent* from Glorp UI's Russian; they are not, they are
  present and wrong. Same practical effect, different reason. **Done**, in
  Russian only — the other nine translations of those four keys were checked and
  are grammatical, so Glorp UI keeps ownership of its own text there.

**`TO_MOVE_FURTHER_TO_LEFT/RIGHT` we already fix**, in `ru_loc_fix`: vanilla's
Russian references `$SOCIEALVALUE_..._GEN$` — a typo for `SOCIETALVALUE` — and
we repair the reference. He repoints the key at
`[SocietalValue.GetLeftLabelWithNoTooltip]` instead, for ten languages. Two
routes to the same repair; ours does not need Glorp UI installed.

**If both mods are loaded**, the later one wins every shared key, which means
his three gated privileges silently ungate if ours mounts after him. Running
both is not useful: pick one for the translation half, and ours for the content.

**`glorpui_hints/` — eleven languages as of 2026-08-27, and none of that has
been in game.** Version 1.1.0. What changed, all of it unrun:

- **eleven languages** — every folder the game has, English included. A language
  is about fifty short strings in
  [`mods/glorpui_hints/tools/languages.py`](../mods/glorpui_hints/tools/languages.py), because a
  hint line is an opener, a reference the game resolves itself, and a number;
- **the fourteen category nouns became game concepts** rather than translated
  words, which is free in every language and fixed **seven Russian terms** that
  were synonyms — an advance is «Улучшение», not «Достижение».
  **Confirmed on screen 2026-08-27**, in Russian and English, rendering as
  encyclopedia links: [TESTLOG](TESTLOG.md). This was the risk of the rewrite
  and it is closed;
- **five hints now wait for the advance that unlocks the privilege**, scanned
  out of `common/advances`;
- **four keys of Glorp UI's own interface repaired**, Russian only;
- **the workshop tags were wrong** — `Localization` is not an EU5 tag — and are
  fixed in every mod here, with `tools/publish.py` to keep them that way.

The mod is otherwise as it was, and that part is confirmed. It came in
from the `EU5-filters` repository, where it lived as `glorpui_ru_svh_fix` (the
missing Russian for Glorp UI's societal value hints) and `glorpui_svh_extra`
(the hint sources Glorp UI's generator never reads). Both worked in game as
separate mods; the owner asked for one, and this is it, at id
`bag.glorpui_hints`. **The merge loaded and worked on 2026-08-25** — both blocks
render in Russian, screenshot in [`TESTLOG.md`](TESTLOG.md). The old two are out
of the playset; leaving either alongside would mean two mods defining the same
keys and overriding the same templates.

Nothing in the contents changed. Both halves were re-checked against Glorp UI as
it is in `reference/` now, and both are still current: the 759 hint keys
regenerate byte-identical, and Glorp UI's 34 tooltip lists per side are still
exactly what this mod re-emits inside its own override. So the Glorp UI update
broke neither half.

What the merge added is `mods/glorpui_hints/tools/generate.py`, in
`tools/refresh.py` with everything else. It regenerates the Russian hint text
from Glorp UI's English file every run, and — the part that matters — it
compares this mod's re-emission of Glorp UI's list against Glorp UI's own file
as an ordered sequence and fails naming the difference. That failure has no
symptom in game: the templates parse, the mod loads, and the player silently
gets a stale copy of Glorp UI's list. It is in
[`PITFALLS.md`](PITFALLS.md#loading) now.

**It can be rebuilt here now, and it has been.** The extra hint lists compile
out of the game's own `common/` tree, none of which was in `reference/`. The
owner ran `tools/extract_game_files.ps1` on 2026-08-25 and all of it is here:
the source scan reports **1426 pushes across 23 source types**, complete. Two of
the directories are not under `in_game/` at all — `static_modifiers` and
`modifier_type_definitions` live under `main_menu/common/` — which is why the
manifest carries a real path per entry.

Rebuilt against them, the lists went from 243 hint lines to **264** and from 107
gated to **138**, with nothing lost: five Italian and foreign leagues the game
has added, and two more placements of existing lines. Defensive goes from 9
lines to 15. `python3 mods/glorpui_hints/tools/generate.py --game-files
reference/game` is the command; it is not part of `tools/refresh.py` because the
scan takes a minute and the game files move far less often than Glorp UI does.

**Filtering by availability, 2026-08-25 — the owner's ask, and it is done.** He
wants the lists to stop offering what his country can never take: Italian
leagues he cannot join, parliaments a monarchy cannot have, missions in a game
with missions switched off. All three were the ungated categories, and all three
turned out to have an answer in the game's own vocabulary rather than needing
one invented — `can_join_international_organization` from the engine dump,
`game_has_missions_enabled` from the game's own scripted triggers, and
`potential`/`allow` copied verbatim for parliament types. Confirmed on screen the
same evening: the leagues and the missions are gone.

**A second round followed from the same run.** Cabinet actions and parliament
issues came back still unfiltered, and both were the same oversight — the object
carries its own `potential` and the mod was not reading it. `office_of_new_converts`
wants a location modifier on Kazan; `promote_castle_building` requires the castle
advance and forbids the better ones, which is why all four fort-support issues
showed at once. Both take `potential` + `allow` verbatim now, and a parliament
issue also takes the estate that raises it. Gated lines went 138 → 167 → **175**.
The mod's README has the table.

**One gate is still unseen.** The religious aspect repair cannot be checked by
this owner: he plays Catholic, where aspects are set by the Papacy rather than
chosen, so there is nothing for the gate to show either way. It needs a run as a
religion that picks its own aspects.

**That work found a live bug that had been shipping.** 492 religious aspect
lines were gated on `country_religion`, a trigger that does not exist anywhere —
so those lines never appeared, indistinguishably from a country not qualifying.
It is `religion = religion:X` now, and a new check in
`mods/glorpui_hints/tools/generate.py` compares every trigger name in the gates
against the engine dump, the game's scripted triggers, and every name the game
itself writes in that position. See [`PITFALLS.md`](PITFALLS.md#script).

**The switch is built, and it is the mod's first script.** `Списки → Фильтрация
→ Показывать всё без фильтра` in CMF's mod menu turns the two filtered blocks
off and an unfiltered one on. It is a `.gui` condition only —
`CMMSettingIsRegistered` and `CMMValueEqualsOne` are GUI functions — so the
unfiltered body is a plain string that cannot fail. The registration effect on
`cmf_on_mod_registration` is the mod's only hand written script, and the mod now
declares a dependency on CMF. Tooltip lists go 102 → 136; the extra 34 are
hidden unless the switch is on.

**Saying more than «масштабируется» was tried twice and dropped.** The owner
wanted to know how much literacy or how much fleet reaches the maximum. Part of
that is exact — `auto_modifiers` declare `scales_with`, so the threshold is
arithmetic — and part has no answer at all, because `static_modifiers` declare
nothing and the engine scales them. The first attempt put it in a hover and the
hover rendered empty; the second put it inline and it truncated the labels it
shared a row with. Both are in [`PITFALLS.md`](PITFALLS.md); the arithmetic is
kept in [`research/engine.md`](research/engine.md) so it is not derived a third
time. The line reads label, «(масштабируется)», number — as it did before any of
this.

**Known gap, not yet work: English.** The added lines are Russian only. An
English game finds no `SVX_*` keys and renders the two new blocks as raw keys —
the same fault this mod fixes for Glorp UI, pointing the other way. It is a
change to the generator (fourteen category nouns and two block titles), not to
the files.

**`auto_build_ru/` — done, confirmed working in game.** Russian for Advanced Auto
Build, which ships English and Chinese only and so rendered as raw keys in a
Russian game. The player reports the Mod Menu tab reading correctly.

The base mod updated to 0.9.2 Beta mid-session and the generator refused to
write, naming 40 keys it had never seen — the template buttons, the priority
step tooltips, a whole R.G.O. diagnostics panel and a throughput warning. That
is what it is for. All 40 were translated then. Note the base mod's id is
`eu5ab_regional_development` and its folder now carries a workshop number; both
are resolved by `tools/refs.py` and neither is written down anywhere.

**0.9.3 Beta came in on 2026-08-25 and brought a second ranking strategy** — the
mod can now order ordinary buildings by the profit the game itself predicts,
instead of by its own supply-and-demand score. 28 new keys, all translated: the
strategy block in the window, the two candidate limits, the CMM setting and its
two options, and four new throughput warnings. 1269 keys now.

**Two keys had gone stale without anything saying so.** The throughput warning's
`action_name` and `action_desc` were rewritten by the base mod — they used to be
about presets and additions, they are now about the new Planning Candidates
limit — under a Russian translation that stayed put and went on reporting itself
complete. `nd_ru` catches that with fingerprints and this generator had none. It
does now: `mods/auto_build_ru/english_generated_fingerprints.txt`, same shape,
same `--accept`. Both keys are retranslated. **None of the 0.9.3 work has been
in game.**

**`nd_ru/` — в работе, играбелен за Вестфалию и Швабию.** Русский для National
Destinies. Базовый мод везёт одиннадцать языков, и файлы всех одиннадцати
побайтово равны английским, так что в русской игре он читается по-английски.
Объём — 40 790 ключей, **690 376 слов** прозы, 220 файлов. Версию не записывать:
её печатает `python3 tools/refs.py`.

**Перекрытие проверено в игре и работает.** Отдельный мод, загруженный после
базового, переопределяет уже определённые тем ключи. Это был главный риск, и он
снят. В лаунчере `nd_ru` должен стоять **после** National Destinies.

**Совместим с машинным переводом из мастерской.** Имена наших файлов
(`*_ru_generated_l_russian.yml`) не совпадают с именами того мода (как у
базового), значит подмены файла целиком не будет. Ставить: машинный ниже, наш
выше — получится наш текст там, где он есть, машинный везде остальном.
Английского от нас не добавится: генератор не пишет непереведённые ключи.

Сделано — **4 174 ключа** (10,2% ключей, 6,4% слов):

- все 5 правил игры;
- названия и описания 45 образуемых стран, какие мод называет сам; остальные 93
  из его 125 формируемых стран берут имя из игры и русскими были всегда, так что
  **названия стран закрыты полностью**;
- три большие системы целиком: Дунайская монархия (`nd_dnm`, 685 ключей),
  Дунайский вопрос (`nd_danube`, 443), Австрия (`nd_hab`, 150);
- **три страны целиком**: Вестфалия (`nd_wes`, 208 ключей с учётом лежащих в
  общих файлах), Швабия (`nd_swa`, 192) и объединённая Европа (`nd_eur`, 275);
- названия Ломбардии;
- общие файлы `nd_event_guards` (144) и `nd_bureaucracy_impact_modifier_types`
  (1770 из трёх шаблонов) — чинят свои строки сразу у всех стран.

Ничего из этого, кроме Вестфалии и перекрытия, в игре не проверялось.

**Обновление базового мода до 1.3.7 разобрано.** Оно тронуло ровно ту часть,
что уже была переведена: 67 новых ключей в `nd_dnm` (целая система «Вопрос о
Рейхе» — остаться в Империи или порвать с ней, утверждение Санкции рейхстагом,
два новых дипломатических действия) и два переписанных значения, `DNM_f_desc`
и `nd_dnm.21.a_tt`. Всё это переведено, `nd_dnm` снова закрыт целиком. Ещё
четыре новых ключа в `nd_event_entries` — чистые `$...$`-ссылки на заголовки
событий, переводить их не нужно.

**Устаревание перевода теперь ловится само.** Из этого обновления генератор
поймал только `nd_dnm.21.a_tt`, и только потому, что там изменилась разметка;
переписанный `DNM_f_desc` нашёлся руками, через `git diff` по `reference/`.
Поэтому `generate_ru.py` снимает отпечаток английского значения каждого
переведённого ключа в `english_generated_fingerprints.txt` и на следующем
запуске называет те, где английский сдвинулся. Поправить перевод, затем
`generate_ru.py --accept`. До этого запуск возвращает ошибку, то есть хук
начала сессии покажет `FAIL nd_ru` — ровно тогда, когда это нужно.

**Как продолжать — в [`../mods/nd_ru/README.md`](../mods/nd_ru/README.md).** Там
три команды, которыми ведётся работа, что именно проверяет генератор и порядок
работы над страной. Термины — в
[`../mods/nd_ru/GLOSSARY.md`](../mods/nd_ru/GLOSSARY.md), сверяться с ним
обязательно: расхождение в терминах на двухстах файлах читается как небрежность.
Порядок стран — в `mods/nd_ru/priority.txt`, остаток — `mods/nd_ru/tools/scope.py --plan`.

**Сколько это стоит.** Одна сессия ровной работы сдвинула около 25 000 слов
вместе с оснасткой и ошибками. Отсюда: остаток рабочего набора по Европе —
5 832 ключа, 25 тыс. слов, примерно одна такая сессия. Полная проза той же
Европы — ещё 6 693 ключа и 214 тыс. слов сверх того. Весь мод целиком —
34 618 ключей, 646 тыс. слов, около двадцати шести сессий.
На подписке Pro весь мод не окупается; объём режется по приоритету. Самый
выгодный приём — искать файлы, где одна формулировка повторяется сотнями ключей,
и переводить их шаблоном: так 1 914 ключей обошлись в два десятка строк.

**Про модель.** Смена модели не сокращает число токенов — английский всё равно
читается, русский пишется. Экономит только цена токена и понижение усилий
рассуждения: перевод не рассуждательная задача, и `high` на нём почти не
окупается. Сам перевод абзаца модель послабее сделает сопоставимо; хуже она
сделает другое — удержание единого термина на двухстах файлах и поиск дыр вроде
ключей страны в чужом файле. Отсюда разумное деление: названия — модели подешевле
и с меньшими усилиями, длинная проза и структурные разборы — сильной.

**`where_to_produce/` — removed, August 2026.** A Mod Menu tab that ranked what
was worth building in a province you picked. It never worked in game and the
owner stopped wanting it; the reason it did not work was never established,
because it was never tested. What it is worth knowing about it is in
[Why it failed](#why-where_to_produce-failed), below.

## The slowdown — it is the base game, and the hunt is for a lever

Measured across five runs. The measurement is finished; what is open is whether a
mod or a setting can do anything about it. Numbers and method in
[`TESTLOG.md`](TESTLOG.md); this is the state of it.

**What it is.** The game accumulates GUI widgets and never releases them while a
session is running. 364 at the main menu, ~37 000 once a game is loaded, 294 013
after an hour of ordinary play. Frame time follows: 14 ms early, 21 ms after an
hour.

**How big that is.** Every `.gui` file the game ships declares, in total, about
**27 800 widgets** — the whole interface, every window, counted statically
(`in_game/gui/`, widget declarations, minus properties that share the shape). So
after an hour the process is holding **more than ten copies of the entire
interface**. This is not a heavy panel; it is instances piling up.

**What causes it.** Interface interaction, and nothing else:

| | widgets per frame |
| --- | --- |
| paused, hands off | **0.00** — exactly zero, across 10 800 frames, twice |
| clicking countries, opening diplomacy | +1.86 |
| cycling map modes | +1.49 |
| clicking locations, opening the build panel | +0.29 |

**What it is not.** Ruled out, each with data rather than argument:

- *map markers, unit icons, the passage of time* — growth does not scale with
  game days (103 days added 138 widgets, 125 days added 10 936) and does not
  scale with the unit count, which swings 276 to 708 with no relation to it;
- *one bad window* — every kind of interaction leaks, at different rates and none
  of them zero;
- *the mod set* — with every mod off the same activity leaks **+1.99** widgets a
  frame against **+1.86** with the full playset. Vanilla is marginally worse;
- *anything in this repository* — `rgo_bonus_filter` adds to the location panel,
  the lightest of the three by a factor of six.

### The lead worth following

**Growth decays inside a block of unchanging activity.** Four blocks, four times
the same shape:

```
diplomacy, full playset   +24814   +8809  +11150    +140
locations, full playset    +3783   +1338   +1504    +336
map modes, full playset   +17532   +5191   +3278   +5123   +1130   +0
diplomacy, no mods        +14560   +3487   +3425    -418    +258
```

He was doing the same thing throughout each row, so a per-*action* leak would be
flat. A decaying one says the cost is per *distinct thing looked at*: the first
pass over a set of countries or map modes is expensive and the second is nearly
free. Over an hour of real play you keep meeting new things, which is why it
never plateaus.

**The engine offers nothing to release them.** `dump_data_types` has no widget
`Destroy`, `Clear`, `Free`, `Collect` or `Prune` — the only such names belong to
buildings, editors and variable systems. `PdxGuiWidget` can be hidden, found,
counted and animated, and that is all. So there is no mod-side call that undoes
this; a fix has to be something that stops the widgets being made.

### The candidate, and the lever that goes with it

Hover. It fits everything: idle costs nothing because an unmoving mouse shows no
tooltips; clicking through diplomacy sweeps the pointer over dozens of new flags,
names and numbers; map modes sweep it over a new legend each time; and the decay
within a block is what a per-subject tooltip cache would look like.

**And the defines say tooltips are built with no delay at all.**
`game/loading_screen/common/defines/jomini/00_tooltips.txt`, in full:

```
NTooltip = {
    OPEN_DELAYED_TIME = 0.0f;
    CLOSE_TIME = 0.2f;
    TENDENCY_BUFFER = 15;
    MIDDLE_MOUSE_LOCK_TIME = 0.25;
    MOUSE_MOVE_DISTANCE_TO_UPDATE_TOOLTIP_POSITION = 10.0f;
    MOUSE_MOVE_DURATION_TO_UPDATE_TOOLTIP_POSITION = 0.2;
}
```

Zero delay means every brush of the cursor over anything builds a tooltip
immediately. Sweeping across the map builds them by the dozen a second.

That file's own first line is `# This file overrides
cw/jomini/modules/tooltip_manager/data/common/defines/jomini/00_tooltips.txt`, so
overriding a defines file is the ordinary mechanism and **a mod can do the same
thing**. If hover is the source, a one-file mod setting `OPEN_DELAYED_TIME` to
something like `0.35f` cuts the creation rate by whatever fraction of hovers are
incidental — which is most of them.

Better still, the game's own **Settings → Tooltip Settings → Show Delay** almost
certainly drives the same value. So the setting tests the mod before the mod is
written.

### The run that decides it

One session, one save, paused throughout:

1. **A** — move the mouse over the map and the top bar for two minutes, sweeping
   across countries and buttons, **without a single click**.
2. Settings → Tooltip Settings: `Show Delay` to **maximum**, `Map Tooltips` to
   **Disabled**, `Map tooltips delay` to **maximum**.
3. **B** — exactly the same two minutes of sweeping.

Then `performance_degradation.log`.

- **A leaks and B does not** → the mechanism is tooltips. Write the defines mod,
  and then look at what else can be trimmed from the heaviest tooltip files
  (`shared/location_tooltips.gui` 438 widgets, `shared/combat_tooltips.gui` 428,
  `cooltip.gui` 627).
- **A leaks and B leaks the same** → the delay is not the knob, but hover still
  is. Then the tooltip `.gui` files are the place to look.
- **A does not leak at all** → hover is out entirely and the leak needs clicks.
  The next test is then the same panel opened thirty times against thirty
  different panels opened once, which separates a per-open leak (a mod can make
  panels cheaper) from a per-object cache (only Paradox can).

### The other route, if the run does not settle it

`debug_mode` in the console opens a toolbox. The buttons, as of 1.3.11:

```
TOOLBOX     Language  Environment  Map menu  Inspect  Explorer  Unit Viewer  Errors
2D Tools    UI Editor  Animator  UI Bounds  UI Library  Workbench  Reload GFX
3D Editors  E. Designer  Animation Edit  Particle Edit
```

There is **no Tweaker**, so the runtime-variable idea is out. But `UI Editor` is
the live widget tree, and that is the direct way to name what accumulates: play
until the count is high, open it, and see which container holds a quarter of a
million children. `UI Bounds` draws widget outlines and would show a stack of
invisible ones. `Inspect` reports whatever is under the cursor.

**The mitigation that is already established.** Leaving to the main menu releases
all of it — widgets back to the 364 the process starts with, memory back to what
it was before any game was loaded. So **main menu, then load the save** is worth
exactly as much as restarting the game and costs a fraction of the time.

## The second slowdown — panels open slower with mods, from the first minute

Reported 2026-08-25: *"открыть любую вкладку в ваниле происходит мгновенно, а вот
с модами с микрозадержкой или даже фризом даже при только-только запущенном
сохранении."* This is **not** the widget leak and must not be filed with it. The
leak grows over hours and reloading clears it; this is present on a save loaded a
minute ago, so it is a fixed per-frame or per-open cost that the playset adds.

**First, the size of what can be said.** The owner runs **22 workshop mods**, and
`reference/` holds five of them. `tools/playset.py` reads the mount table out of
his own `debug.log` — the engine writes one line per mod folder it mounts, in
load order — and reports that **17 of the 22 mount `in_game`**, which is the only
mount that can add a widget, a filter chip or a scripted widget to the running
game. Of those 17, at most 14 have never been looked at. So the census below is
honest about a quarter of the surface and silent about the rest; do not write
"the playset does X" on the strength of it.

**And the owner does not run Advanced Auto Build**, which the first version of
this section led with. His `debug.log` of 2026-08-24 does mount workshop id
`3781437488` — that is Auto Build, `in_game` and `main_menu` both — so either it
was turned off since, or it is enabled and unused, which costs the same because
a scripted widget is instantiated whether the player opens it or not. Its numbers
are kept below because they are the clearest example of the pattern, not because
they explain his hitch.

`tools/guicost.py` counts the rest from the files:

```
                          files  widgets GetScriptedGui   live  loops
vanilla                     387    58354              9      0      0
cmf                          44     7486             70     12      0
construction_manager         20     4545            344      3      0
glorp_ui                     49    13782             67      1      0
national_destinies            3      251              0      0      0
auto_build                    7    14125           4719      7     19
mods/rgo_bonus_filter         2      207              4      0      0
```

**The number that does not belong.** `GetScriptedGui('x')` in a `.gui` file
runs a script trigger from the interface — the expensive kind of expression,
because it enters the script engine. Vanilla uses it **nine times** in 387 files.
Advanced Auto Build uses it **4 719 times** in seven, 2 166× vanilla's density
per widget; Construction Manager **344 times**, 491×. With Auto Build out of the
playset, **Construction Manager is the heaviest thing anybody here has looked
at** — and thirteen mods nobody has looked at are still in the room.

**And all seven of Auto Build's windows are in `scripted_widgets/`,** so the
engine instantiates them at load and never takes them down: **14 125 widgets
live for the whole session** whether or not the player opens the mod. Vanilla's
entire interface, statically, is about 27 800. CMF's twelve always-live windows
come to 104 widgets and Construction Manager's three to 96 — those are probes,
which is what a scripted widget is for. This is a different order of thing.

**`eu5ab_engine_queue_window` is a background worker.** It is deliberately kept
"visible" (`visible = "[EqualTo_CFixedPoint('(CFixedPoint)0', '(CFixedPoint)0')]"`
— always true) and parked at `position = { -10000 1 }` so it keeps ticking
offscreen. Inside are **eight phases**, each a self-restarting animation state at
**0.15 s**, each walking a `datamodel` of the player's candidate locations × their
candidate building types and running per pair:

```
GetBuildOrExpandBuildingCost           GetBuildingTypeIncomeToOwnerInLocation
GetBuildingTypeProfitInLocation        CanBuildOrExpandBuilding
```

Each phase's gate is itself a `GetScriptedGui(...).IsShown(...)` evaluated every
frame. That is a plausible cause of a hitch on any panel open, for the ordinary
reason: the frame budget is already spent before the panel asks for anything.

**Static widget counts understate a `datamodel` window, and Construction
Manager is the case in point.** `cm_hidden_window` declares twenty-three widgets
— and binds `datamodel = "[GetGlobalList('cm_building_types_to_process')]"`, so
what actually lives is that subtree **once per building type**, and the game has
465 of them. Nested inside each row are two more datamodels, over the type's
construction demand entries and over its production methods. The file's own
comments say what it is for: *"Always-present hidden window that classifies every
building type once per lobby"*, kept alive with
`visible = "[EqualTo_CFixedPoint('(CFixedPoint)0', '(CFixedPoint)0')]"` — always
true — at `position = { -10000 1 }`, and *"Keeps descendant visibility gates
re-evaluating each frame."* That is a few thousand live widgets whose `visible`
expressions (`BuildingType.HasConstructionGoodsDemand`, `BuildingType.IsProducing`,
`ProductionMethod.IsProducing`) are re-asked every frame, by design.

`cm_construct_queue_window` is the same shape with sixteen datamodels over
locations × building types, and it too is always live.

None of this is a bug: it is how CM gets at engine bindings that read only in
GUI. It is simply not free, and it is paid whether or not a panel is open.
`python3 tools/guicost.py --drivers` names the list every always-live window
iterates, because the multiplier is the number that matters and no static count
can know it.

**Filter chips are the second cost, and this repository is in it.** Every chip
whose `tag` matches a list is a trigger run once per item, every time the list
draws. `python3 tools/guicost.py --filters`:

| tag | vanilla | mods add |
| --- | --- | --- |
| building | 36 | +15 (+42%) |
| town_rights | 21 | +7 (+33%) |
| raw_goods | 15 | +4 (+27%) |
| ruler | 27 | +5 (+19%) |
| province | 8 | +1 (+12%) |

Four of the fifteen added to `building` are ours. They are not cheap ones:
`bag_rgo_has_local_bonus` walks `any_location_in_province` and evaluates a
40-branch `OR` per location, per building type in the list. On a five-location
province with a hundred buildable types that is thousands of trigger evaluations
per open of the build panel.

**Two hypotheses already dead, so nobody re-checks them:**

- *Glorp draws heavier panels.* No. On the sixteen vanilla files it replaces,
  Glorp's versions hold **3 850 widgets against vanilla's 4 956** — 0.78×. It
  adds 33 files of its own (2 399 widgets) but replaces nothing with something
  bigger.
- *A mod's Russian localization is throwing parse errors on open.* No. The hard
  rules of `mods/ru_loc_fix/tools/locscan.py` run over every mod's Russian files
  find **zero** faults: CMF 94 keys, Construction Manager 451, Glorp 139,
  National Destinies 40 719, Auto Build 1 241, and our own five mods. The broken
  markup is the base game's alone.

**The test.** Seventeen mods can be halved in four or five loads, and each load
is a minute. The same save and the same three panels every time — the country
panel, diplomacy, and a location's build panel — because the owner's own sense
of the hitch is a good enough measurement for a difference he describes as
obvious:

1. Everything on. Confirm the hitch is there.
2. Half the `in_game` mods off. Instant or not?
3. Keep halving whichever half still hitches.

Two named suspects are worth trying first, in case they save the bisect
entirely: **Construction Manager**, for the reasons above, and our own
`rgo_bonus_filter`. If it is CM, the choice is the owner's — the mod or the
responsiveness; nothing here can make another author's hidden window cheaper. If
it is ours it is fixable: those four chips can be made to cost a variable lookup
instead of a province walk.

If the bisect lands on a mod nobody has looked at, copy its folder from
`steamapps/workshop/content/3450310/<id>/` into `reference/mods/` and run
`guicost.py` again — that is what the id list from `playset.py` is for. If it
lands on nothing in particular, the cost is spread and the next instrument is
`ScriptProfilerEntry`, which the engine dumps expose with
`GetAverageTimeExclusive`, `GetCallCount` and `GetFileAndLine`.

## Where to check things

Everything a session needs is in `reference/` — the game's `gui` and the parts
of `common` that matter, plus Community Mod Framework, Construction Manager,
Glorp UI and the two mods being translated. Grep it rather than asking for
uploads, and run `python3 tools/refs.py` rather than believing a version written
in prose.

The one thing that still has to come from the player is `logs/` after a test
run, because only they can run the game. After any refresh of `reference/`:

```
python3 tools/refresh.py
```

**Whether a refresh is owed** is answered without asking him: `python3
tools/workshop.py` compares the tracked workshop items against what the last
sync wrote down, needs nothing but the network, and runs daily on GitHub as
well. The workshop itself will never hand the files to GitHub: an anonymous
steamcmd download of an item for this game is refused, so the files only move
from a machine that owns it.

**The menu has been run end to end, on 2026-08-25, and it works.** Advanced Auto
Build 0.9.3 was found, fetched with steamcmd under his account, copied into
`steamapps/workshop/content/3450310/` — the folder the game reads mods from —
and then into `reference/`, rebuilt, committed and pushed, all from the menu.
The playset came in the same evening: **17 mods, 18 MB of text**, which is the
first time anything here could see more than five of the twenty-two.

**He brings them over from a menu — `mods.bat` in the repository root, which is
there so the command never has to be looked up again — and that menu is not
only about this repository.** It reads his whole subscription out of Steam's own
`appworkshop_3450310.acf`, says which mods the workshop has moved on since Steam
downloaded them, fetches those with steamcmd into the game's workshop folder so
the next launch loads them, and only then offers the copies here, the rebuild,
and the push. A mod moves between `reference/mods/` (whole, watched daily) and
`reference/playset/` (text only) from the same menu, which rewrites
`tools/workshop_mods.txt` itself.

**It also installs what we build.** Menu item 4 copies the mods in `mods/` into
`Documents/Paradox Interactive/Europa Universalis V/mod/`, which is the folder
he used to keep in step by hand — pull the branch, delete the old folder, paste
the new one, six times. It offers a `git pull` first, says of each mod whether
the game's copy is the same, different or absent, and can take one back out
again.

**Only the game's half of a mod folder goes.** `.metadata/` and the mount
directories (`in_game`, `main_menu`, `loading_screen`, …); never `tools/`,
`translations/`, `fixes/` or the READMEs, which are this repository's business.
A top-level directory that is in neither list is **reported and not copied** —
so a mount nobody has heard of cannot be dropped in silence, and a new source
folder cannot end up inside a live mod.

That shape is deliberate and was asked for in those words: **nothing about
updating his mods may require a session of ours.** `sync_workshop.ps1` is still
there for the unattended path, and `workshop.py` is still the machinery under
both.

**The first real sync ran on 2026-08-25**, and brought both mods this repository
translates up to date in one command. It also showed what the loop is worth:
Advanced Auto Build had gained 28 keys and quietly rewritten two, and National
Destinies had added a formable to a sentence. All of it is translated now, and
both generators are clean.

**A sync from a box without Python rebuilds nothing.** That is what the first
run did: the reference copies were committed and pushed, `refresh.py` never ran,
and so nothing said the translations had drifted. The update check survives it —
`workshop.py status` works out from git that a folder committed after the
workshop's last update cannot be behind, so it does not need `record` to have
run — but the generators do not run themselves. After a sync, make sure someone
ran `python3 tools/refresh.py` and read its report.

Advanced Auto Build used to arrive in `reference/` without its `.metadata/`,
which is why `auto_build_ru` declares only CMF as a dependency. The workshop copy
the sync brings carries it, so `refs.py` now reads that mod's id and version out
of the tree like every other; the dependency line is the only thing left over
from when it could not.


## What the playset turned out to hold

Counted on 2026-08-25, the first time `tools/guicost.py` could see more than the
five mods in `reference/mods/`. Seventeen more, and the answer is mostly a
narrowing one — which is worth as much as a suspect:

- **not one playset mod adds a filter chip.** The `building` tag is still
  vanilla's 36 plus Construction Manager's 11 and our 4, so the +42% this
  repository has been reasoning about is the whole of it. That closes a
  direction rather than opening one;
- **three of them keep an always-live window**, and all three are small:
  `faster.universalis` has eight 24-widget `fum_speed_watcher_*` windows whose
  `visible` is `IsGameSpeedEqualOrGreaterThan` — cheap engine calls, no script —
  and `autonomous_diplomats` (8 widgets) and `calidad_de_vida_eu5` (4) have one
  each. Against Construction Manager's 344 `GetScriptedGui` calls that is
  nothing;
- **no playset mod overrides a file our mods ship.** Checked by relative path
  across every `.txt`, `.yml` and `.gui` in `mods/`.

So the interface census now covers the playset and still names the same two
heavy things: Construction Manager at 491x vanilla's script-call density, and
Advanced Auto Build at 2161x — **which he does not run**. The remaining
unexamined surface is behaviour, not declarations: what those mods do on tick.

## Somebody else has translated National Destinies, nearly all of it

`nation_destinies_rus` is in his playset — a **full** Russian translation of the
mod `nd_ru` translates. Measured against the base mod's English, on the same day:

| | keys | markup faults | left in English |
| --- | --- | --- | --- |
| the base mod (English) | 40 795 | — | — |
| `mods/nd_ru` | 4 174 (10%) | 0 | 53 |
| `nation_destinies_rus` | 37 949 (93%) | 33 | 120 |

**3 787 of our 4 174 keys are keys it also translates**, and 32 of its 33 markup
faults are inside that overlap — so on those keys ours is the sound one, and
whichever of the two mounts *later* wins them.

**The decision was made long ago and is not open.** That mod is machine
translation — Google's — and it lags the base mod's versions; the owner runs it
*under* `nd_ru` deliberately, so that a key we have translated properly shows
our text and everything else falls back to the machine one rather than to
English. `nd_ru` is therefore not competing with it and does not need to reach
93% to be worth having: every key it covers is a key upgraded from machine to
human, and the 32 broken-markup keys in the overlap are repaired by the same
mechanism.

**Do not ask him about this again, and do not propose dropping `nd_ru`.** It
has come up twice; the numbers above exist to make the arrangement legible, not
to reopen it. What matters practically: **`nd_ru` must mount after
`nation_destinies_rus`** — if a load order ever puts it first, our translation
becomes invisible and the symptom is machine-Russian on keys we know we
translated.

Our 53 English leftovers are deliberate and correct: they are `_CATEGORY` keys
pointing at vanilla category names and proper nouns that stay as they are
(`Erbverbrüderung`, `Studia Generalia`).

## Hard-won facts that are easy to lose

- The RGO bonus formula, verified to the digit against three tooltips, is in
  [`research/engine.md`](research/engine.md#the-formula-behind-the-number) and in code in
  `tools/eu5data.py`. Every input counts in the divisor, produced goods included.
- A `building_type` filter receives `root` and nothing else — not `scope:target`,
  whatever vanilla's comment says. Reading it logs an error every pass.
- A CMF action bar element is drawn from localization: `_icon` takes a texticon
  like `@good!`, and `_color` must name one of CMF's palette entries or the
  button is invisible in the bottom bars.
- Square brackets in a localization value are data function syntax, so a plain
  `[debug]` in a label renders as `ERROR:`. The same syntax is what lets a row
  label read a global variable back.
- A CMM macro called with an argument name CMF does not declare fails silently
  and takes the rest of its effect with it. One `step` instead of `step_value`
  cost a full round. `python3 tools/check_cmm.py mods/<mod>/in_game/common`
  checks a whole mod for it.

## Why `where_to_produce` failed

It was removed in August 2026, unfinished, at the owner's word: "нерабочая
помойка, я ей не пользуюсь". Written down because the next attempt at the same
question should not repeat the shape of it.

**What it was.** A tab in CMF's Mod Menu. Four CMM list settings — region, area,
province, then the answer — where picking a row in one filled the next, and the
last ranked every building by what that province's raw materials were worth to
its best production method, in percent and in volume.

**What was verified, and what was not.** The data layer was checked against the
game and was right: the bonus formula matches three tooltips to the digit, and
an earlier build of the same data answered the *opposite* question ("for this
good, which province") correctly on screen — `Рудные горы / Оружейные заводы /
1.88% / 4.075` read true. Then the front end was rebuilt around province-first
picking, and **that rebuild was never run in game even once**. Nothing about the
new front is known to be broken; nothing about it is known to work either.

**Why the cause was never found.** The failure mode this repository hits most:
an effect that never runs logs nothing at all. Six things were suspect at once —
`region = { }` and `area = { }` as scope blocks, comparing `region =
global_var:x`, reading a variable map inside a script value, re-registering a
list at a new height, `GetRegion` / `GetArea` on a global variable, and whether
`can_build_building` was stricter than it looked. Diagnosing that needs one
`cmf_log` per suspect and one game run each, and the mod was not wanted enough
to pay for them.

**The lesson worth carrying.** The mod was built to completion before anything
of it was loaded once. A `cmf_log` on the first picker, run in game, would have
cost one round trip and told us which half of six unknowns was even in play. In
a repository where only the player can run the game, the size of the untested
increment *is* the risk — and the interface half, not the data half, is where
everything here has gone wrong.

**Where its parts went.** The formula and the CMM list mechanics are in
[`RESEARCH.md`](RESEARCH.md); the game-data reader is `tools/eu5data.py`,
untouched and still correct; the CMM macro check is `tools/check_cmm.py`, which
now runs against any mod. The mod itself is in git history — `git log --
mods/where_to_produce` — if a future approach wants to read how something was  <!-- check-docs: ignore -->
done.

**If the question gets picked up again**, two things are known to be possible and
were never done: a button injected into the location panel through
`scripted_widgets`, so the province on screen is the one answered for instead of
walking three pickers; and building straight from a row, since
`construct_building = { building_type owner payer }` in a location scope queues a
real construction and Construction Manager uses exactly that. The open question
there was never the effect — it was *which* location of the province to build in.

One thing the game files in `reference/` still cannot answer: a *method* locked
behind an advance. `ProductionMethod.IsAvailable` exists as a GUI data function,
so the game knows, but there is no script-side counterpart and neither
`building_types/` nor `production_methods/` records the unlock. Answering it
needs `common/advances/` and the technology folder beside it, which are not in
the tree.

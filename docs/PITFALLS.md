# Pitfalls

Mistakes already made in this repository, each with the symptom that gave it
away. Every one of them cost at least one round trip through the game, because
none of them raise an error you would notice.

Scan this whenever something silently does nothing.

## Script

**A CMM macro called with an argument CMF does not declare fails silently and
takes the rest of its effect with it.** `step` where CMF declares `step_value`
meant the setting never entered CMM's maps; syncing its alias then errored, and
everything after it in the same effect was skipped — including four other
settings. Symptom: an interface that renders perfectly and does nothing.
`python3 tools/check_cmm.py mods/<mod>/in_game/common` checks a whole mod against
whichever CMF is in `reference/`.

**Dropdown options are numbered from one.** Registering with `default_index = 0`
put the stored value out of range, so nothing the player picked matched any
branch. Symptom: menu looks correctly filled in, nothing downstream reacts.

**A comment saying a trigger was confirmed is not a confirmation.**
`gates.py` gated 492 religious aspect hints on `country_religion = religion:X`,
under a comment reading "confirmed in common/religious_aspects". It is not there
and never was: `country_religion` appears nowhere in the game's script and is
not in the engine's trigger dump. What those files carry is
`religion = calvinist` — the aspect declaring its own religion, a different
thing in a different scope. The country trigger is `religion = religion:X`, 598
uses in the game's own `common/`.

Nothing caught it for months because a wrong trigger name in a
`customizable_localization` gate does not stop the mod loading; the gate simply
never passes and the lines never appear, which looks exactly like a country not
qualifying for them. It was found the day a checker started comparing every
trigger name in the file against what exists. **Put the confirmation in a
checker, not in a comment** — a comment records what someone believed once, and
a checker re-establishes it on every run.

**A `building_type` filter receives `root` and nothing else.** Not
`scope:target`, whatever the comment at the top of vanilla's
`58_building_type.txt` says. Reading it logs an error on every pass of the list.
`building` and `location` scoped filters do get it.

**Numeric-looking keys are not all goods.** `debug_max_profit = -1` on the
plantations was being counted as an input, turning four recipes' total input
weight negative. Match keys against the goods catalogue rather than against
"is it a number".

**A method with no `produced` outputs nothing.** A monastery burns clay for
upkeep, so it has no production efficiency for local clay to improve — which is
why the game gates its own shovel badge on `IsProducing`. Counting upkeep
methods put castles and monasteries in a list of things to build for their raw
materials.

**A live script value in a list row costs a frame, every frame.** 74 rows each
labelled with `ScriptValue('bgt_impact_<good>')`, each of those reading a market
price and a default price, made the game visibly lose ticks whenever the Mod
Menu was open — and the figures still looked frozen, because what a row shows is
recomputed constantly rather than when the thing it describes changes. Compute
on a pulse into a variable and let the row read the variable; the same five
values inside one tooltip cost nothing, so it is the number of rows drawing them
that matters, not the values themselves.

**A formatted list field needs its format keys or it prints their names.**
`cmm_set_list_field_format` and `cmm_set_list_field_conditional_format` make the
widget read `<mod>__<setting>__<field>_prefix` and `_postfix`, and for the
conditional one also `_prefix_high` / `_postfix_high` / `_prefix_low` /
`_postfix_low`. CMF decides whether a key exists by comparing `Localize(key)`
against the key itself, so a missing one is not an error — it renders as its own
name, in the column, where a number should be. `cm__auto_build_list__min_discount_*`
shows the full set.

**A CMM list silently loses every row past the fiftieth.** CMF initialises list
items through an unrolled chain ending at item 50, so a list registered at 74
shows 50 rows and says nothing about the rest. Split into several lists — and
give each its own output, since `cmm_build_list_bool_list` clears the list it
builds into and a shared one would keep only the last.

**Asking a variable map for a key it does not hold is an error, not false.** A
CMM setting sitting at its registered default may never have been written to the
`cmm` map, so `"variable_map(cmm|flag:<mod>__<setting>)" >= 1` as a plain gate
can take the whole effect down on a new game. Guard it with
`is_key_in_variable_map` and decide what the absence means.

**`item = var:x` inside a CMM list macro dies at load** with "More than one
colon in event target link" — the macro pastes it verbatim. Ordinals into
`cmm_set_list_data_value` and friends have to be literals; generate a switch that
turns a counter into one.

## Interface

**View objects only resolve inside their own panel.** Reading
`LocationProductionView.GetSelectedLocation` from a scripted widget returns null
and logs once per frame. Vanilla never reads a `*View` outside its own file;
elsewhere it only calls `Show<X>View(...)` to open one. If a probe has to watch a
panel, it has to live in that panel.

**Skins go on the widget, not in a `background` block.** `background = { using =
bg_paper_card }` does nothing at all; vanilla writes `using = bg_paper_card` on
the widget itself. Symptom: a window drawing its text straight onto the map.

**Copying a vanilla `.gui` brings its `types` block with it.** Construction
Manager and Glorp UI both restyle panels by redefining `types` from files of
their own, so a copy carrying vanilla's versions of those same types clobbers
them, load order deciding who loses. Copy the *window* and leave the types alone.

**Hidden rows still occupy their cell.** The list bodies are `fixedgridbox`es
with fixed row heights and no `ignoreinvisible`, so hiding a row from the
interface leaves a hole. Filter the data instead, or resize the list.

## Localization

**A `customizable_localization` cannot be overridden.** Localization keys do —
a mod loading later wins, and `glorpui_hints` rewrites 759 of Glorp UI's every
build. A `customizable_localization` does the opposite: **the first definition
read wins, and the later duplicate is dropped**, saying so in the log and
nowhere else.

```
gamedatabase.h:408  Duplicated key glorpui_svh_free_subjects_pv_peasants_yeomanry
                    will not be created from file: ...
```

So an addon cannot tighten a base mod's rule by redeclaring it, however late it
loads — the redeclaration is simply thrown away and the base mod's rule keeps
running. What it *can* do is take over the localization key that rule prints and
point it at a rule of its own. That is what
`in_game/common/customizable_localization/svx_unlock_gate.txt` does. The line
came out of `Glorp UI small fix`, whose author had already hit it and written the
log line down.

**A category noun probably does not need translating at all.** The game defines
`game_concept_<name>` in all eleven of its localization folders, so
`[religious_aspect|e]` renders "Religious Aspect", «Религиозная особенность»,
"Glaubensaspekt" — for free, in the player's language, with the encyclopedia link
attached. `python3 tools/api.py` does not list these; grep
`reference/game/main_menu/localization/*/game_concepts_l_*.yml` for
`game_concept_`.

Beyond the ten languages it saves, it is the only way to be *sure* the term
matches the game's own. Fourteen category nouns in `glorpui_hints` were hand
written Russian and **seven of them were synonyms** rather than the game's word:
an advance is «Улучшение», not «Достижение»; a subject type «Тип ленника», not
«Тип вассала». Nobody would have noticed either without comparing.

The cost is that a concept the game renames becomes a raw token on screen in
every language at once and nothing errors — so check the ids against the game's
own localization in the generator, the way
`mods/glorpui_hints/tools/generate.py` does.

**Square brackets are data function syntax.** A label reading `[debug] location
known` renders as `ERROR:`. Keep brackets out of plain text.

**A `$NAME$` that names a key which does exist can still come out blank.**
`glorpui_hints` replaced its hand written modifier labels with references to the
game's own — `$STATIC_MODIFIER_NAME_parliament_outside_capital$` instead of
"Парламент вне столицы" — so that a patch renaming a modifier would be followed
for free. On screen some of them rendered and some rendered as nothing:
`is_bankrupt` was fine, `parliament_outside_capital` and
`peasants_percentage_in_country` were bare values with no text. All three keys
exist in the game's Russian files. Nothing was logged.

What separates them is still unknown, and that is the point: **a label that is
nothing but a reference has no floor.** If the reference resolves the line reads
correctly, and if it does not the line loses everything, silently. The rule now
in `mods/glorpui_hints/tools/generate.py` is not "no references" — the catalogue
lines have referenced `$building_type$` since the beginning and always worked —
but "every label carries literal text of its own", so a reference can lose part
of a line and never all of it.

**The left half of a `TooltipScrolledStringPairList` row is narrow, and it
truncates rather than wraps.** A hint line is `@hint! <label>: <value>`, and the
label has about as much room as a short noun phrase. Adding a parenthetical to
it — "(масштабируется: максимум при used_fort_limit_percentage = 200%)" — did
not make the row taller: it cut the *label* off at «Традиции армии ( …» and
«Во вр …» and spilled the rest across the value column. Nothing errors, and it
only shows on a screenshot. Whatever a hint line has to say has to fit in a few
words, or belong somewhere that is not that row.

**A mod-defined game concept with no texture renders as nothing.** The same
change made «(масштабируется)» a game concept so the explanation could be a
hover: `[Concept('svx_scale_army_tradition','(масштабируется)')|e]`, with the
concept declared in the mod's own `in_game/common/game_concepts/`. Glorp UI
proves a mod can define concepts — but every one of its own carries a `texture`,
and these carried only `shown_in_encyclopedia = no`. On screen the whole
`[Concept(...)]` produced empty output: the line kept its label and its value and
lost the word between them. No error, no log line. If a text-only concept is
wanted, prove it with one before generating forty.

**A `$NAME$` that names no key prints the name.** No error, no log line, no
blank: the engine puts `SOCIEALVALUE_RIGHTITEM_WNTT_GEN` in capitals in the
middle of the Russian sentence and carries on. The game's own Russian defines
seven societal value declension helpers as `SOCIETALVALUE_*` and references all
seven as `SOCIEALVALUE_*`, so twenty four keys print a name instead of a word —
and it took a screenshot to notice, because nothing else could. `missing_ref` in
`locscan.py` is the rule now. It is hard on the fault and careful about the
repair: the *nearest* defined key is not always the intended one, and four of
the thirteen references it finds are cultures whose neighbour is a different
people (Even and Evenk, Halkomelem and Halkomelemt, Lalagir and Lalagyr).

**A pattern in the data is not a fault until something fails.** All 1755
`*_culture_tt` keys in the game's Russian
`EU5_customizable_localization_ru_culrel_l_russian.yml` hold a bare number that
is exactly the key's own line number minus two — every one of them, plus 624
more in a sibling family. They are used as `#TOOLTIP:CULTURE,$X_tt$,`, where a
culture key looks like it belongs. That is a striking, verifiable pattern and it
reads exactly like a generator that wrote line numbers into tooltip targets, so
this document briefly said every culture tooltip in the Russian localization was
broken.

It is not. A hover settled it: the tooltips are complete and correct, and the
key on screen (`westphalian_cadj` → `#TOOLTIP:CULTURE,$westphalian_tt$,` →
`"1052"`, on line 1054) is one of the numeric ones. The number is what the engine
wants there, or the engine ignores it.

The cost of getting this wrong would have been 1755 keys rewritten to fix
nothing. **A pattern explains a fault; it does not establish one.** Before
repairing on the strength of a shape in the data, find the thing that visibly
fails — and if nothing visibly fails, that is the answer.

**A "broken" key can be a key nothing can call.** Three of the culture
references `missing_ref` found are declensions for `even_culture`,
`halkomelemt_culture` and `lalagyr_culture` — cultures the game does not have,
though `evenk_`, `halkomelem_` and `lalagir_` all exist. Unreachable, harmless,
and repairing them by pointing at the near neighbour would have put the Evenk
tooltip on the Even culture. Before repairing a dangling reference, check
whether the thing it belongs to exists at all: `reference/game/in_game/common/`
answers it, and a dead key is cheaper left alone than fixed wrong.

**A checker that silently reads less than it thinks is worse than no checker.**
`locscan.py`'s key regex required the line to end at the closing quote, so
`hre_tt: "0" #True` — a key with a comment after it — was not a key as far as
every rule was concerned. **18 012 keys, 3.4% of the tree**, invisible. The
symptom only appeared when a new rule started asking "is this reference
defined?" and answered no 1 418 times. Nothing was wrong with the rule. When a
checker's finding count looks too big to be true, suspect what the checker can
see before suspecting the game.

**The game loads the selected language's folder and nothing else — there is no
fallback to English.** Glorp UI generates 759 `GLORP_UI_SVH_*` keys into
`main_menu/localization/english/` and no other language, so on a Russian client
every one of them is missing, the societal value hint list renders empty, and
the tooltip says «Нет.» while `debug.log` takes 725 `Missing loc key` lines per
load. Nothing about that reads as a localization problem on screen: the widget
draws correctly and is simply blank. It hits all ten non-English languages, not
just Russian. When a mod's feature works in English and does nothing in Russian,
check which language folders it actually ships before looking anywhere else.

**A CMF action bar element is drawn entirely from localization**, keyed on the
element name: `_icon` takes a texticon such as `@good!`, `_name` and `_tooltip`
fill the tooltip, and **`_color` must name one of CMF's palette entries** or the
button is invisible in both bottom bars. The top position is a tab and skips
that gate, which makes a missing `_color` look like "only works in one position".

**A list setting is its own group**, so CMM keys its header through the tab:
`<mod>__<tab>__<setting>_name`. Getting this wrong prints the key on screen,
which at least tells you the right one.

**A model writing hundreds of Russian lines drops foreign characters into
them.** Three CJK ideographs landed mid-word in the first large batch
(`сохранив自 свою`), a fourth in a later one, and an English `though` survived in
a Russian sentence. None of it is visible while writing and none of it errors:
it simply renders on screen. On any batch past a few dozen lines, put the check
in the generator rather than trusting the eye — `mods/nd_ru/tools/generate_ru.py`
refuses a value carrying a character outside Cyrillic and the Latin proper names
need, or an English function word the source value does not itself contain.

**A Latin word given a Russian ending reads past every check that was in
place.** `territoryов` survived the CJK rule (Latin is allowed, for the mod's
proper names) and the English-function-word rule (`territory` is not a function
word), and would have reached the screen. The rule that catches it is narrower
and exact: a Latin letter glued to a Cyrillic one *inside one word* is never a
proper name and always a slip. It is in `generate_ru.py` now, and it fires on
nothing in the 4 000 keys already translated.

**A base-mod update can leave a translation stale in complete silence.** When
National Destinies went to 1.3.7 it rewrote `DNM_f_desc` and `nd_dnm.21.a_tt`.
Only the second was caught, and only because its *markup* changed; the first was
found by diffing the reference tree by hand. A rewritten sentence with the same
brackets looks identical to every check. `generate_ru.py` now fingerprints the
English behind every translated key in `english_generated_fingerprints.txt` and
names the ones that moved; `--accept` records the new English once the
translation has been brought up to date. Symptom without it: the Russian
confidently describes a mechanic the mod no longer has.

**Not everything with letters in it is prose.** `dip_..._CATEGORY:
"CATEGORY_HOSTILE_ACTIONS"` names one of the game's own interaction categories.
It has no markup to protect it, so it read as ordinary text and sat in
`scope.py`'s to-do list as two keys that would never go away. Translating it
would file the interaction under a category that does not exist. `scope.py`
excludes it now.

**Checking one file is not checking the country.** Westphalia looked finished at
88 keys; ten more sat in a shared modifier file, and the shared file for event
guards held one more. Grep every localization file for the tag before calling a
country done. Symptom: a panel that is Russian everywhere except one tooltip.

**A per-file completeness rule blocks a layered pass.** The generator first
demanded that a source file cover its base file entirely, which is right for a
small mod and wrong for a names-first pass over a large one. An untranslated key
simply stays with the base mod; count it and report it, do not refuse it.

**The mod's own `\"` is legal and the quote check must allow it.** A value like
`\"Let others wage war\"` parses fine; a naive "no double quotes" rule rejects
the whole file. Match an unescaped quote only.

**Generate localization for every language, not just English.** The player plays
in Russian; an English-only key shows as the raw key.

**The engine does not fall back to English.** A mod shipping only
`english` and `simp_chinese` renders every one of its keys as the raw key name
in a Russian game — the whole interface, not a stray label. That is what
Advanced Auto Build's Mod Menu tab looked like, and it is diagnosed by the
company it keeps: if other mods in the same list read correctly, the language
is fine and that mod's `.yml` for it is simply absent.

**A shipped language can be the English text under a different header.**
National Destinies ships eleven languages whose 220 files are byte identical to
the English ones apart from the `l_<language>:` line, so the mod reads in English
inside a Russian game while `localization/russian/` plainly exists. It is the
opposite symptom to a missing `.yml`, which shows raw keys — here everything
renders, just in the wrong language. Diff the files against `english/` before
concluding a language is present. It also changes the job: those keys are
defined, so a translation has to **override** them rather than add to them, and
the overriding mod has to load later.

**A `_format` key does nothing for a CMM setting.** Only list *fields* take a
format, and only through `cmm_set_list_field_format`. A row's text comes from
`_name`, `_desc` and `_text`. `search_filter_<key>_format` is the unrelated
filter convention that makes this look plausible.

**The base game's own Russian localization is broken, and it is the largest
single source of errors in a Russian game.** For a long time the answer to "the
log is full of localization errors" here was "some mod's". It is not: 88% of the
39 289 errors in the run of 2026-08-24 came out of
`reference/game/main_menu/localization/russian/`. Six shapes, all found by
`mods/ru_loc_fix/tools/locscan.py`: unclosed brackets (55 keys), accessors that
`dump_data_types` does not list (36 — `GetAdjectvive`, `GetGovernnment`,
`GerHerHis`), `Custom()` applied to the result of `GetName` (27), roots that are
nothing at all (10 — including `XXX` left in by a translator), a filter string
quoting another key (6), and wrong scopes the game named itself (14). Before
blaming a mod for a localization error, run that scanner.

**A `$OTHER_KEY$` reference inside a search-filter string loses the object.** A
filter's name and description are built once per object the filter selects, and
in that context a data function written inline resolves and the same data
function reached through a quoted key does not.
`CUSTOM_SEARCH_FILTER_LOCATION_RAW_GOODS_NAME` and `..._RAW_GOODS_DESC` sit four
lines apart, do the same thing two ways, and only the second one fails — every
time, 75 failed lookups per evaluation.

**Thirty thousand errors in one second destroys the log.** `error.log` rotates
at 1 MB and keeps five. Five filter strings produced 31 350 lines inside the
second the game started, which rotated it five times over: everything the game
had said before that second was gone before the player quit. When a log looks
suspiciously empty of everything except one repeated error, check the
timestamps at the head of each rotation — if they are all the same second, the
log is not telling you what happened, it is telling you what happened last.

**`Custom()` cannot be asked of a name.** `Country.GetName.Custom('CL_GEN')` is
27 keys' worth of the same mistake in the shipped Russian files: `GetName` has
already produced text and text cannot be promoted. The whole key fails to parse,
so the player sees nothing at all rather than an undeclined name.

**A GUI type can be real and appear nowhere in the English localization.** The
first version of the unknown-root rule compared against English strings alone
and accused twenty-five healthy keys, all using `UnitTypeLateralView`, which is
a perfectly ordinary type that no English string happens to mention. Check the
engine's `dump_data_types` before calling a name invented — the same rule that
applies to effects and triggers.

**`performance_degradation.log` has columns that identify a playset.** `GUI
widgets` at the first in-game sample, `Total number of Gfx units` and
`Total number of Trade wagons` are deterministic for a given bookmark and data
set — 37 768 / 449 / 843 for this playset at 1337_04_01, every single run. When a
run arrived that was supposed to be vanilla, those three columns said so without
anyone having to be asked: 36 977 / 448 / 713. Use them to confirm a run was
configured the way the report says it was.

**`performance_degradation.log` records the in-game date, which turns it into a
controlled experiment for free.** A row whose date equals the row before it was
taken while the game was paused. Splitting an hour that way said more than any
guess: paused and idle adds zero widgets, growth does not scale with game days
(103 days added 138 widgets, 125 days added 10 936), and it does not scale with
the unit count on the map. That ruled out map icons, unit markers and the tick
itself without asking the player to run anything.

**Three samples of a performance log cannot tell a leak from a warm-up.** The
first reading of `performance_degradation.log` had memory climbing 280 MB a
minute and concluded the game was heading for swap. An hour of the same log says
otherwise: the working set peaks at 14.7 GB and then falls under 7 GB. What
actually grows without limit is the GUI widget count and the frame time. Read the
whole run before naming a cause; the file is a few kilobytes and there is no
excuse.

**`Failed parsing localized text` in `gui.log` at frontend load says nothing
about the game.** Seventeen of them, all at one timestamp, sixteen seconds before
the mod's localization is merged — the frontend parses vanilla's value on the way
past. Check the timestamp against the `pdx_localize.cpp:257` lines that mark the
merge before believing that list.

**Fixing the loudest error is how you find the second loudest.** Five keys were
34 225 of 39 289 lines and hid everything else, including three keys with exactly
the same fault that had never once appeared in a log. There is no way to reach
those by reading files: nothing separates the ninety keys that reference a
declension helper from the ten that fail. Expect a fix of this kind to take more
than one round, and treat the second log as the point of the first fix.

**Closing a bracket turns a parse error into a scope error.** `lieutenancy_tt`
never rendered because of an unbalanced bracket; with the bracket closed it
renders, and now the two `Custom()` calls inside it can be seen failing on a
scope that is not a country. The fix was still right — but a key that starts
working starts reporting, and a rise in a different error is not automatically a
regression.

**A test the player physically cannot perform is a wasted round trip.** "Sit on
the map for five minutes without opening anything" is impossible in a running
game — events fire and demand a click. The owner said so, and he was right. Pause
removes events, the tick and map churn in one move, and every block after that is
attributable. Before asking for a protocol, walk through it as the person who has
to do it.

**"Report it to the developers" is not a deliverable.** This session established
that the widget leak is vanilla's, wrote the numbers up as a bug report, and
handed it over as the answer. The owner's reply was that he had known it was
vanilla the whole time and was asking for a fix, not a diagnosis. He was right
about that too: the diagnosis had ruled things out, but nothing had yet been
asked of the engine dumps about what a mod *could* do. Establishing whose fault
something is is the beginning of the work here, not the end of it.

**When a measurement is finished, say which questions it closed.** Five rounds of
tests produced ten settled facts, and the risk at the end of every session is
that the next one re-derives them and spends the owner's evenings doing it. The
table at the top of [`HANDOFF.md`](HANDOFF.md#settled--do-not-measure-any-of-this-again)
exists for that; add to it rather than writing a new narrative each time.

## Publishing

**The workshop's tag list is fixed, and a tag outside it is dropped rather than
refused.** Four mods here were filed under `Localization`, which EU5 does not
have; the tag it does have is `Translation`, and `Economy` is really
`Trade and Economics`. The upload says nothing, the mod simply ends up in no
category on a hub where people browse by category. The list read off the hub's
own filter sidebar is `WORKSHOP_TAGS` in
[`../tools/publish.py`](../tools/publish.py), and `python3 tools/publish.py`
checks every mod against it along with the version format, the thumbnail and the
BOM.

**The Steam app id for EU5 is `3450310`.** The wiki's PDX Workshop Manager page
says `529340`, which is Imperator: Rome. `3450310` is the one `steamcmd` in
`tools/workshop.py` actually downloads with.

## The reference tree changes under you

**An addon answers to its base mod's name.** `3784988919_glorp_ui_small_fix`
matches every hint that finds `3601047146_glorp_ui` — both folders contain
`glorp` and `ui` — and the day it arrived, `refs.mod("glorp.ui")` stopped being
able to answer at all and `glorpui_hints` failed to build. Folder names were
never enough on their own; the fix is that a candidate declaring exactly the
`id` asked for wins over one that merely reads like it. Expect more of this: an
addon is usually named after what it is an addon to.

**A folder name in `reference/mods/` is not a fact.** The owner refreshes these
by hand, and the name arrives however the upload produced it: the same mod is
`community_mod_framework` one time and `3692202776_community_mod_framework` the
next. Anything hardcoding the name breaks silently — a missing base mod reads as
"nothing to translate", not as an error. Ask `tools/refs.py`, which matches on
the `id` inside `metadata.json` (`trin.national_destinies`); the number in the
Steam path is not that id.

**Another mod's localization file is not written the way ours are.** A strict
parser — key, colon, quoted value, end of line — is right for this repository's
own files and wrong for everybody else's. `nation_destinies_rus` ends every
line with a `#NT!` marker *after* the closing quote, and a parser that insisted
on the quote being last read **8 keys out of 37 949** and produced a confident,
completely wrong conclusion about how much that mod translates. Allow a trailing
comment before drawing any conclusion from somebody else's file, and sanity-check
the count against the file size before believing it.

**A translated key can go stale while every check still passes.** When a base mod
*rewrites* an English value, the Russian under it is still present, still
markup-clean and still counted as covered — and now says something else.
Advanced Auto Build 0.9.3 did that to two keys, and nothing reported it, because
that generator kept no fingerprint of the English it had translated from. Both
translation generators keep one now (`english_generated_fingerprints.txt`,
signed off with `--accept`). Coverage is not currency.

**A workshop sync that pushed is not a refresh that ran.** `sync_workshop.ps1`
rebuilds the generated files only if it finds Python on that machine; without
one, the reference copies are committed and pushed and nothing else happens,
which reads exactly like a clean run. The first sync did this — **on a machine
with Python installed**, because the search was `Get-Command python/python3/py`
and an install made without ticking "Add python.exe to PATH" answers none of the
three. It reads the registry first now
(`Software\Python\<company>\<tag>\InstallPath`, which every python.org and
Store install writes whether or not PATH knows), and
`.\tools\sync_workshop.ps1 -CheckPython` reports what it would use and every
candidate it rejected. `workshop.py status` works the currency out from git
regardless, but the generators still have to run somewhere — `python3
tools/refresh.py` after any sync, and read the report.

**PowerShell hands a native command's output through a pipe, not a console.**
Python then encodes stdout with the machine's ANSI code page instead of UTF-8,
and the first Cyrillic line — `nd_ru`'s generator prints its report in Russian —
raises `UnicodeEncodeError` and takes the rest of the run with it. The sync
script sets `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` before calling Python
for exactly this.

**A base mod that *deletes* a key stopped the whole update loop.** Advanced Auto
Build's 2026-08-28 build dropped 28 keys, the ranking-mode block among them.
`generate_ru.py` treated "a key here the base mod does not define" as the same
class of fault as "a key the base mod defines and nobody translated" and refused
to write anything — and because the mod menu runs every generator in one pass,
one deleted feature in somebody else's mod stopped the owner's update. The
generated file is written from the base mod's own key list, so a translation of
a deleted key is never emitted and nothing renders wrong: it is dead weight, not
a fault. It is now reported by name, the run goes on, and `--prune` takes the
lines out of `ru.yml`. A *rename* still stops the run, because that half shows up
as a missing key — which is the case that actually needs a human.

**A regex that reads somebody else's file in one shape goes quiet when they
change shape.** Glorp UI wrote its hint references as
`#TOOLTIP:ESTATE_PRIVILEGE,petty_bureaucracy #L $petty_bureaucracy$#!#!` and now
writes `[ShowEstatePrivilegeName('petty_bureaucracy')]` — the engine's own data
function, which does the same job. Two things in `glorpui_hints` read that shape,
and they failed differently: the hint parser raised, loudly, naming the line;
`PRIVILEGE_HINT_RE`, which finds the privileges an advance locks, would simply
have matched nothing, written an empty `svx_unlock_gate.txt`, and shipped a mod
recommending privileges the country cannot take, with nothing in any log. **A
loud failure is the lucky one.** Both shapes are accepted now, and
`check_gates_found_something` compares the two readings against each other, so a
third shape stops the run instead of emptying a file.

**Re-emitting somebody else's block drops whatever your parse cannot see.**
`glorpui_hints` replaces Glorp UI's `blockoverride` on the societal value
tooltip wholesale, and it used to rebuild their half from the entries its regex
recognised — a `ScriptValue(...)` gate, a title, a `Localize(...)` body. Glorp
UI's 2026-08-28 build added one entry per side with **none of the three**:
vanilla's own C++ hint blob, `[SocietalValue.GetLeftHint(Player.Self)]`, behind
their new `showUnavailableSocietalValueSuggestions` setting. The parse could not
see it, the check that compares the two lists compared parsed entries and passed,
and the entry was silently dropped — so their new switch did nothing for anyone
running both mods, and because the same setting also switches *their* per-axis
lists off (`NOT = { has_variable = ... }` in every `glorpui_svh_visible_*`),
turning it on made half the tooltip vanish. Nothing in `error.log`.

The fix is not a better regex. **Copy the bytes**: the block is spliced in
verbatim and the check compares text, so a shape nobody has thought of survives
by default. This is the second time in two days that a parse of somebody else's
file went quiet when they changed shape — the entry above it is the first. When
this repository holds a copy of another mod's *structure* rather than its data,
copy it, do not re-derive it.

**A copy synced and not yet committed reads as `behind`.** `record` dated a
reference copy by `git log` — which still knows only the old commit — so the
sync stamped two mods it had just brought in as out of date, and the run ended
by telling the owner to run the sync he had just run. Nothing under `reference/`
is ever hand-edited, so an uncommitted change there means exactly one thing: it
was just copied in. That is now its own verdict (`uncommitted`), and it says
"commit it" rather than "you are behind".

**A version written in prose goes stale the moment the owner updates a mod.**
That is not the owner's mistake to fix by annotating uploads; it is the
document's mistake. Versions come from `python3 tools/refs.py`, and a mod
arriving newer than a document remembers is the normal state of this repository
rather than something to report as a problem.

## Loading

**Later file wins for a duplicate database key, and files sort by name.** A mod
redeclaring `sheep_farms` in `00_sheep_farm_food_buildings.txt` loses to
vanilla's `rural_buildings.txt`, because `00_` sorts first. The `00_` prefix is
for files that must load *early*; to override, sort late. Symptom: mod loads,
changes nothing, logs nothing.

**`metadata.json` needs `"game_id": "eu5"`.** Every working mod has it. Without
it the launcher does not treat the folder as an EU5 mod.

**Overriding another mod's *generated* override goes stale in complete
silence.** `mods/glorpui_hints/` overrides Glorp UI's override of the societal
value tooltip templates, and to keep Glorp UI's own hint lists it re-emits them
inside its own file. When Glorp UI regenerates those templates — which it does
on every game patch — nothing errors: the templates still parse, the mod still
loads, and the player quietly gets a months-old copy of Glorp UI's list with
whatever Glorp UI added missing from it. `error.log` says nothing, because
nothing failed. The only defence is a checker that compares the two files, so
`mods/glorpui_hints/tools/generate.py` reduces both to an ordered sequence of
(gating script value, title, body key) and fails naming the difference. Any mod
that copies another mod's generated file needs the same check written the same
day the copy is made.

## Deciding what exists

**"No mod here uses it" is not "the engine lacks it".** Subsidies were declared
GUI-only after grepping vanilla's `common/`, CMF, Construction Manager and Glorp
UI and finding only `ToggleSubsidizeBuildings` in a `.gui`. The engine has
`set_subsidized` and `is_subsidized`, both in the building scope, and a feature
had already been redesigned around their absence. The game prints its whole API
— `python3 tools/api.py <name>` answers in a second, and
`reference/game/docs/` is where those dumps live. Ask it before concluding
anything is impossible.

## Diagnosing without a signal

**Two suspects and one round trip is a wasted round trip.** A monthly log line
that never appeared could have meant the pulse never fired, the setting read
errored, or CMF's log would not render what it was handed. Fixing all three
blind answered nothing: the next run still showed one number, and it was still
ambiguous. What works is a probe whose failure modes are *separable* — a counter
that only the pulse can increment, shown through a path already proven to work,
so the reading distinguishes "never ran" from "ran and could not be displayed".

**Ask for the logs before theorising.** `error.log` being empty of your mod is
itself a finding: it rules out every failure the engine notices and leaves only
the silent classes — a missing localization key, an effect never called, a value
never read. Two of the four faults in `goods_target` were identified from the
logs plus `reference/` in one pass, without a further run.

## Working blind

**Building a whole mod before loading it once is the expensive mistake, and it
has been made here.** `where_to_produce` was finished — four CMM lists, pickers,
scoring, tooltips — and then abandoned without ever running, leaving six
independent suspects and no way to tell which was in play, because an effect
that never runs logs nothing. One `cmf_log` on the first list, one round trip,
would have cut that to one. Only the player can run the game, so the size of an
untested increment is the whole risk: the smallest thing that produces a visible
signal beats the complete feature every time.

## Diagnosis

**`error.log` is the fastest tool here** and names the file and line. Every bug
found in this repo was found in it, usually in one pass. It also carries a
callstack for script errors, which is what points at the effect that swallowed
the rest of its body.

**An effect that never runs logs nothing at all.** That is the failure mode this
repo hits most. When the symptom is "nothing happened and the log is clean", do
not guess twice — put a `cmf_log` on the path in question and have the player
look at CMF's log panel.

**`game.log` carries load-time macro expansion errors** that `error.log` does
not.

**`reference/` is not the playset, and mistaking it for one produces a confident
wrong answer.** A session counted what every mod in `reference/` costs the
interface, found one mod far outside the range, and led with it. The owner's
reply was that he does not run that mod. `reference/` holds the five mods
somebody thought to upload; his `debug.log` of the same week mounts **22**, of
which 17 touch `in_game`. The mount table is right there in the log —
`virtualfilesystem_physfs.cpp: Mounted Data: .../workshop/content/3450310/<id>/<part>`,
one line per folder, in load order — and `python3 tools/playset.py <logs>` reads
it. Run that before any sentence beginning "the playset".

**A static widget count says nothing about a window built on `datamodel`.** The
same session reported `cm_hidden_window` as 23 widgets. It declares 23 and binds
a datamodel over every building type in the game, so what lives is that subtree
465 times over, with two more datamodels nested per row. Whenever a count is
about cost rather than about files, check what the window repeats over first —
`guicost.py --drivers` prints it.

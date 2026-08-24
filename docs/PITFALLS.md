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

**Square brackets are data function syntax.** A label reading `[debug] location
known` renders as `ERROR:`. Keep brackets out of plain text.

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

## The reference tree changes under you

**A folder name in `reference/mods/` is not a fact.** The owner refreshes these
by hand, and the name arrives however the upload produced it: the same mod is
`community_mod_framework` one time and `3692202776_community_mod_framework` the
next. Anything hardcoding the name breaks silently — a missing base mod reads as
"nothing to translate", not as an error. Ask `tools/refs.py`, which matches on
the `id` inside `metadata.json` (`trin.national_destinies`); the number in the
Steam path is not that id.

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

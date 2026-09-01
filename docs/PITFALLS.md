# Pitfalls

Mistakes already made in this repository, each with the symptom that gave it
away. Every one of them cost at least one round trip through the game, because
none of them raise an error you would notice.

Scan this whenever something silently does nothing.

Two subjects outgrew this file and have their own, which `tools/kb.py`
searches like everything else:

- [`pitfalls/localization.md`](pitfalls/localization.md) — declensions,
  `customizable_localization`, `$NAME$` references, markup that renders as
  `ERROR:`, and the theory about culture tooltips that did not survive a run.
- [`pitfalls/reference_tree.md`](pitfalls/reference_tree.md) — what breaks when
  somebody else's mod updates under a generator.
- [`pitfalls/interface.md`](pitfalls/interface.md) — windows that draw outside
  themselves, skins that do nothing, view objects that resolve nowhere.
- [`pitfalls/diagnosis.md`](pitfalls/diagnosis.md) — how to find a fault that
  logs nothing, and how to spend a run on it rather than a guess.
- [`pitfalls/shipping.md`](pitfalls/shipping.md) — putting a mod out and getting
  it loaded: workshop tags, the app id, load order, `metadata.json`, and
  overriding somebody else's override.

## Script

**A `province_definition` does not keep a variable.** It is static map data, not
a runtime entity — the runtime one is `province` — and a `set_variable` inside
`province_definition = { … }` writes nothing, silently. `where_to_produce`'s plan
kept each province's two lists and their counters there and placed *zero*
buildings out of 381 places: every `limit` that read one of the counters failed,
`error.log` carried not one line, and the pass counted its own 127 locations and
30 goods correctly on the way past. **Nothing in vanilla or in any mod in
`reference/` writes a variable to a definition** — the way to hold a province's
state is `every_location_in_province_definition` and a variable on each location,
which is what `bag_wtp_store_row` has always done. A definition is still a
perfectly good *scope* to read through, and to iterate from.

**A `trigger_if` chain must end in a `trigger_else`.** Ending on a
`trigger_else_if` logs `PostValidate of trigger 'trigger_else_if' returned false`
against the last link and voids the whole trigger — `where_to_produce`'s
«only where the building can stand» filtered nothing for two loads, and the line
sat in `error.log` unread because it names a generated file and a line number
rather than the setting it broke. `trigger_else = { always = no }` closes it.

**A CMM macro called *without* an argument CMF declares fails exactly like one
called with an argument it does not.** The known half of this rule was `step`
where CMF wanted `step_value`; the other half cost `where_to_produce` a whole
load. `cmm_register_settings_list` declares `is_ordered`, the call omitted it,
`$is_ordered$` stayed in the pasted text, and every list registration died where
it stood — taking the row labels and the field registration after it in the same
effect. The symptom was a Mod Menu tab holding only the settings that happened to
be registered by a *different* effect, with no error anywhere. `check_cmm.py`
now reports both directions.

**`cmf_on_mod_registration` fires every time the mod page is opened.** Not on a
new game, a save load and a country transfer only, whatever it reads like:
`where_to_produce`'s registration ended with a `clear_rows`, and the result the
player had just computed was gone by the time he reached the button that
reopens it — the counters beside it zeroed, the rank taken off every row, and
the rows themselves left on screen because the newer of the two windows' lists
had been forgotten in that same `clear_rows`. Registration is for making things
exist. Anything it destroys, it destroys on a schedule nobody chose.

**A call to a name nothing defines is not reported where you would look.** The
patch that was to write `bag_wtp_right_row_is_worth_it` died half way; the
`limit = { bag_wtp_right_row_is_worth_it = yes }` that called it survived,
passed for every province, and the filter filtered nothing — the same symptom as
the `trigger_if` fault below and a run of its own to find. `check_script.py`
resolves every `<name> = yes` in a mod's own `common/` against the mod, the mods
in `reference/`, and the engine's own effect and trigger dumps.

**A trigger's conditional is `trigger_if`, and nothing else is.** `if` is an
*effect* in the engine's own dump and `else_if` is not in it at all. Written
inside `common/scripted_triggers/` they log `Unknown trigger type: else_if` once
per line and leave a scripted trigger that comes back **true no matter what** —
the worst failure a filter can have, because it filters nothing and looks
correct. `where_to_produce`'s "only where it can be built today" was that from
the day it was written, through fifteen loads, and the tick was on the list of
things "never reported" the whole time. The forms are `trigger_if`,
`trigger_else_if`, `trigger_else`; `tools/check_script.py` refuses the others.

**A file carries one byte order mark, at byte zero.** A second one is a
character in the text and the interface parser answers `'﻿' is not a valid
widget/type/property`, then abandons the file — every type in it missing, the
window never found, and the only symptom in game a button that does nothing.
Writing a string that already begins with a BOM through `encoding='utf-8-sig'`
is how it happens, and nothing about the file looks wrong afterwards.
`tools/check_script.py` counts them.

**A ranking on fractions does not sort.** `where_to_produce` ranked provinces on
a method's effective output, which for the one book method a 1369 country has
unlocked runs 0.3000 to 0.3129 across the whole of Europe. The rows came back in
alphabetical order of the province key — the unordered walk — and `order_by` had
plainly done nothing. The tell is in the tree: **not one `order_by` anywhere
sorts on a fraction.** Vanilla ranks on `military_strength`, `country_tax_base`,
`population`; Advanced Auto Build on a score built out of `add = 12000`. Scale
until the differences are whole numbers, and keep the scaled value out of
anything that prints.

**A scope rule applied to half a mod is not applied.** The `root`s the rule
below condemns were taken out of `where_to_produce`'s row pass and left in all
218 places in the scoring pass beside it, which cost the next run too: the
pickers reached the pass and the pass found no method available anywhere,
because each availability check was a country trigger asked through `root` from
inside a walk over locations. Grep the whole mod for the construct in the
session the rule turns up.

**A generic action's `effect` does not run in the actor's scope.** The three map
pickers in `where_to_produce` ended with two scripted effects written for a
country and no wrapper. The first was scope-agnostic line by line and ran
anyway — the count it maintains went on moving, which is what made the whole
thing look like it was working. The second opened with `has_variable` on a
country variable, got no, and did nothing. Symptom: a selection that is visibly
registered and an answer that never changes. Vanilla writes `scope:actor = { … }`
around every one of its five actions' effects and Advanced Auto Build's forty
touch nothing but `scope:target_location`; **not one existing action anywhere
relies on the bare scope**, which is the tell. Wrap it, and prefer `scope:` and
`this` over `root` in anything an action can reach.

**An unordered iterator will undo a ranking, and nothing says so.**
`where_to_produce` sorted into one global list and copied that into the window's
datamodel with `every_in_global_list`. `every_*` promises nothing about order,
and a window draws its rows in the order its list holds them, so every hop
between lists has to be `ordered_*`. Cheapest guard: write the rank onto the row
and print it, so a shuffle is visible rather than looking like a ranking nobody
understands.

**`max` on an ordered iterator counts what it visits, not what you keep.**
`where_to_produce` ranks locations and keeps one row per province, since every
location of a province scores the same. With `max = 50` on
`ordered_in_global_list` it filled about a dozen of its fifty rows and looked
like a ranking that had run out of answers — the walk was spending its fifty on
the other locations of the same provinces. Any pass that filters inside the loop
has to ask for enough iterations to reach the rows it wants, and say in a comment
what the ratio is.

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

## Never invent a name for something the game already names

**2026-09-01.** A session called `royal_masonry_rights` «масонская хартия». The
owner plays in Russian, saw a name that exists in no game of his, and reasonably
asked why an invented right was displacing his glass. Nothing had been invented;
the name had. His game calls it «Права на каменные и стекольные работы», and the
key and its localization are each one grep away.

**Name a rule, building, good or right by its key or by the string the game
shows.** Never by a translation of the key, and never by a phrase invented to
read more smoothly: the owner cannot check the code, so a name he cannot find
costs him confidence in the whole report.

## Reading a `location_potential` is not checking the ground

**2026-09-01, and it cost the owner a round trip.** `where_to_produce`'s plan
never placed glass, and a session concluded from `glass_guild`'s
`location_potential = { is_produced_in_location_market = goods:sand }` — plus the
ages of the other three glass buildings — that glass simply could not be built in
Westphalia, wrote that into `SETTLED.md`, and told the owner so. He replied with
two screenshots of the game offering him a glass guild in Münster and a rural
glassmaker in Dülmen.

The gate was read right; **what was never checked is whether the ground satisfies
it**, and nothing in this repository can check that — market contents are save
state. The reference tree says what a condition *is*, never whether it *holds*.

So: a `location_potential` explains why a good *might* be missing. Only a run
says whether it is. Say which of the two you have.


## Deciding what exists

**"No mod here uses it" is not "the engine lacks it".** Subsidies were declared
GUI-only after grepping vanilla's `common/`, CMF, Construction Manager and Glorp
UI and finding only `ToggleSubsidizeBuildings` in a `.gui`. The engine has
`set_subsidized` and `is_subsidized`, both in the building scope, and a feature
had already been redesigned around their absence. The game prints its whole API
— `python3 tools/api.py <name>` answers in a second, and
`reference/game/docs/` is where those dumps live. Ask it before concluding
anything is impossible.

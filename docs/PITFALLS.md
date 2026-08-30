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

## Script

**A CMM macro called *without* an argument CMF declares fails exactly like one
called with an argument it does not.** The known half of this rule was `step`
where CMF wanted `step_value`; the other half cost `where_to_produce` a whole
load. `cmm_register_settings_list` declares `is_ordered`, the call omitted it,
`$is_ordered$` stayed in the pasted text, and every list registration died where
it stood — taking the row labels and the field registration after it in the same
effect. The symptom was a Mod Menu tab holding only the settings that happened to
be registered by a *different* effect, with no error anywhere. `check_cmm.py`
now reports both directions.

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

**Check which build answered before believing what a run showed.** Twice a
report has been read as a fault in a mod whose files on disk were already right:
the folder the game loads,
`Documents/Paradox Interactive/Europa Universalis V/mod/<mod>/`, held an older
build, so the run reproduced the bug the fix had removed. Nothing says so — a
stale build is not an error, it is a different mod, and `error.log` is clean
because the old mod was valid. `gui.log` gives it away by accident: it prints the
file *and line* of every template that overrides another, and line numbers are a
fingerprint. `python3 tools/which_build.py <logs folder>` matches them against
this tree and every revision `git log` has, and names the commit that ran. Do
that first, before reading anything else into a run.

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

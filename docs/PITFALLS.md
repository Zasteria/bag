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
`mods/where_to_produce/tools/generate.py` checks this when pointed at CMF's
`scripted_effects`.

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

## Loading

**Later file wins for a duplicate database key, and files sort by name.** A mod
redeclaring `sheep_farms` in `00_sheep_farm_food_buildings.txt` loses to
vanilla's `rural_buildings.txt`, because `00_` sorts first. The `00_` prefix is
for files that must load *early*; to override, sort late. Symptom: mod loads,
changes nothing, logs nothing.

**`metadata.json` needs `"game_id": "eu5"`.** Every working mod has it. Without
it the launcher does not treat the folder as an EU5 mod.

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

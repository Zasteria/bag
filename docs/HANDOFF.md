# Handoff

Where the two mods stand, and what a fresh session needs to carry on. Read this
first, then [`RESEARCH.md`](RESEARCH.md) for how EU5 modding actually works —
most of that was learnt the hard way and will save a repeat.

## State

**`rgo_bonus_filter/` — working, in use.** Two filter chips, one per building
list. Nothing outstanding.

**`where_to_produce/` — rewritten around the opposite question; untested.**
Everything up to the last round answered "for this good, which province" and
worked: the lists populated, the volume columns and sort order were right, and
`Рудные горы / Оружейные заводы / 1.88% / 4.075` read exactly true. The player
then said that is not the mod they want. What they want — and what the community
"Province Breakdown" spreadsheet does — is the inverse: **pick a province, see
what is worth building in it.**

So the front was rebuilt: region → area → province pickers, then one ranked list
of buildings. The whole verified data layer survived unchanged — the bonus
formula, the volumes, the availability filter, the list machinery. What went was
the good picker, the recipe list and the province shortlist.

## What the spreadsheet asked for, and what it got

| Spreadsheet column | Here |
| --- | --- |
| Province / Area / Region | the three picker lists, built from land you hold |
| Top Burgher Buildings | the answer with **Show = Town** |
| Top Laborer Buildings | the answer with **Show = Rural** — `pop_type` gives the split |
| Raw Goods | not shown; it is what the percentages are computed from |
| Ideal City Locations | not done. It is a made-up topography score, and picking a location is the same problem the build button would need |

The percentages will read lower than the sheet's: it tops out at 12.5% on
single-input buildings from patch 1.0.6, and 1.3.10 tops out at 10%, verified
against three tooltips.

## Not done, and asked for

- **The game's own look.** The answer is a CMM table: a `text_single` and numeric
  cells. The player wants the plate the game draws for a building — icon, name,
  input icons, arrow, output — clickable, with a tooltip. That cannot be done
  inside a CMM list, and the way to it is our own window. Everything it needs is
  reachable: `GetGlobalList` as a datamodel (vanilla does it), `BuildingType.GetIcon`
  and `.GetName` if the pool holds `building_type:` scopes rather than flags,
  `Player.MakeScope.GetVariableFromVariableMap(name, key).GetValue` for the
  numbers — that is how CMF reads its own maps from GUI — and
  `BuildingType.GetPossibleProductionMethods` for the recipe. The old custom
  window failed because it read `LocationProductionView`, which only resolves
  inside its own panel; a window reading only our own globals does not.

- **A button in the location panel** to jump to the province on screen instead of
  walking three pickers. `scripted_widgets` makes it possible; it was left out
  because injecting into a vanilla panel is where the old custom window already
  failed once, and the table wanted to be right first.
- **Building from the row.** `construct_building = { building_type owner payer }`
  in a location scope queues a real construction and Construction Manager uses
  exactly that. The open question is *which* location of the province — the same
  problem the spreadsheet's "Ideal City Locations" column exists to answer.

## Untested, in order of doubt

Nothing of the new front has been in game. In rough order of how likely each is
to be the thing that breaks:

1. **`region = { }` and `area = { }` as scope blocks from an owned location.**
   Both appear in vanilla (`area = { any_ownable_location_in_area = ... }`), and
   `.region` is used dotted, but this is the first thing here to rely on them.
   If the region list comes up empty, that is where to look.
2. **`region = global_var:wtp_sel_region` as a filter on `every_owned_location`.**
   Vanilla only ever compares against a literal `region:x`. If the area list
   ignores which region was picked, this comparison is why.
3. **`can_build_building` and `building_type_is_obsolete` on the country.**
   Both are engine triggers vanilla uses country-side — `country_can_build_in_location`
   splits exactly this way, and Construction Manager leans on both. They are what
   the **Only what I have now** toggle is; if it turns out stricter than it looks
   and empties the answer, that toggle is the thing to turn off and the rest of
   the filtering carries on. That is why it is its own setting rather than folded
   into the availability filter.
4. **Reading a variable map inside a script value** — `wtp_candidate_rank` does
   `"variable_map(wtp_bonus_of|scope:wtp_cand)"`. CMF uses that expression in
   triggers and effects, not in a script value. If every row scores the same, the
   selection sort is reading nothing.
5. **Re-registering a list at a new height.** Clearing `cmm_list_items_<setting>`
   and removing `cmm_list_initialized_<setting>` sends registration back through
   its first-time branch, which is how it is meant to work — but CMF has no
   caller that does this. Four lists now depend on it.
6. **`GetRegion` / `GetArea` on a global variable.** `GetProvince` is confirmed
   working from the screenshots; these two follow the same pattern and
   `Area.GetNameWithNoTooltip` exists, but they have not been seen.

`error.log` names the file and line for GUI failures. A script effect that
merely does nothing logs nothing at all, which is what made every bug in this
mod so far invisible — check `game.log` too, that is where the load-time macro
expansion errors turn up.

## Files a new session must be given

None of this is in the repository, and nothing can be verified without it:

| What | Why |
| --- | --- |
| `<EU5>/game/in_game/gui/` | filters, panels, widget types |
| `<EU5>/game/in_game/common/` — `building_types`, `production_methods`, `goods` | everything the generators read |
| `<EU5>/game/in_game/common/` — `scripted_effects`, `scripted_triggers`, `on_action` | the only reference for what script can do |
| Community Mod Framework (workshop 3692202776) | the CMM API being used |
| Construction Manager (workshop 3736668860) | the only working example of CMM lists |
| Glorp UI (workshop 3601047146) | interface patterns; also what the filter mod must not collide with |
| `Documents/Paradox Interactive/Europa Universalis V/logs/` | how every bug so far was actually found |

Regenerate after any patch, and point the generator at CMF so it checks macro
argument names:

```
python3 rgo_bonus_filter/tools/generate_rgo_filter.py "<EU5>/game/in_game/common"
python3 where_to_produce/tools/generate.py "<EU5>/game/in_game/common" "<CMF>/in_game/common/scripted_effects"
```

## Decisions already made, worth not relitigating

- **Provinces, not locations.** The bonus is province wide; ten locations of one
  province would score identically.
- **Volume is what compares two recipes.** The bonus is production efficiency,
  so it multiplies output: a jeweller's guild at 10% turns out 1.10, a village
  carver at the same 10% turns out 0.11. Ranking on the percentage alone put
  them level, which is what "I want to see the volume too" was about.
- **A building is worth what its best method is worth here.** Scoring walks a
  building's methods and keeps the best by whatever is being ranked on, and
  reports *that* method's figures and recipe. Taking the best percentage and the
  best volume independently would have been two different methods on one row.
- **A method that gains nothing here is passed over.** Its volume is the plain
  output, which every other province matches, so it says nothing about the place.
- **A building type's key is its own localization key**, so the flag standing for
  a candidate labels its row directly. A region, an area and a province have no
  such key, so those rows park theirs in a global and a fixed key per ordinal
  reads it back.
- **Tooltips are generated without words.** They are `$key$` references to the
  game's own method and goods names plus three captions written per language by
  hand, so one generated file serves every localization.
- **Town and rural are `pop_type`.** Burghers are the town half, labourers,
  peasants, slaves and clergy the rural one — which is the split the spreadsheet
  uses, and it matters because the two go in different kinds of location.
- **Only recipes that output something count.** A monastery burns clay for
  upkeep and produces nothing, so it has no efficiency to gain — which is why
  the game gates its own shovel badge on `IsProducing`.
- **The interface lives in the Mod Menu.** A custom window was built and thrown
  away: view objects only resolve inside their own panel, and CMM gives the
  framework's look for free.

## The one thing the game files here cannot answer

*Building* unlocks are solved: `can_build_building` in the country scope is the
engine's own answer and moves with advances and ages by itself.

What is left is one *method* of an unlocked building being locked behind an
advance. `ProductionMethod.IsAvailable` exists as a GUI data function, so the
game plainly knows, but there is no script-side counterpart and nothing in
`building_types/` or `production_methods/` records the unlock. A pre-Columbian
variant of a guild you do have still counts towards that guild's figure.

It is a small error now — the ages gate buildings, not methods within them — and
fixing it would need whatever holds the unlocks, `common/advances/` and the
technology folder beside it.

## Loose ends, none blocking

- The picker lists cap at twenty rows and the answer at twelve. A realm holding
  land in more than twenty regions, or twenty areas of one region, silently sees
  only the first twenty. Raising it means changing `LISTS` in the generator,
  which emits both switches, and adding the matching localization keys.
- The generator deletes what it no longer emits, so a generated file that
  disappears after a run was left over from an earlier design rather than lost.

## Hard-won facts that are easy to lose

- The RGO bonus formula, verified to the digit against three tooltips, is in
  [`../where_to_produce/README.md`](../where_to_produce/README.md). Every input
  counts in the divisor, produced goods included.
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
  cost a full round. `generate.py` checks for this across both
  `scripted_effects/` and `scripted_guis/` when given CMF's path.

# Glorp UI — Societal Value Hints (RU)

One mod that does both halves of the societal value tooltip: it gives Glorp UI's
own hint list a Russian text, and then adds the sources Glorp UI's generator
never looks at.

Requires **Glorp UI** (`glorp.ui`) and must load **after** it — the mod overrides
Glorp UI's own override of the tooltip templates. `.metadata/metadata.json`
declares the dependency, so the launcher orders it.

> **Confirmed in game, 2026-08-25.** Both blocks render in Russian on the
> societal value tooltip. What is still unrun is in
> [what is untested](#what-is-untested).

## What it fixes

Hover a societal value and the tooltip offers **«Дальше продвинуться в сторону
X:»**. In a Russian game that block said **«Нет.»** for every axis, and in an
English game it was thin — a handful of national reforms and nothing else.

**The empty list** is a localization fault. Glorp UI removes the game's built-in
C++ hint block and replaces it with its own lists, whose text lives in 759
`GLORP_UI_SVH_*` keys — shipped in `english/` and in no other language. Paradox
games load the localization folder of the selected language only, with no
fallback to English, so on a Russian client every one of those keys is missing,
the list renders empty, and `debug.log` collects 725 lines like this on every
single load:

```
[jomini_custom_text.cpp:220]: Missing loc key 'GLORP_UI_SVH_CENTRALIZATION_PV_PETTY_BUREAUCRACY'
    for custom localization 'glorpui_svh_centralization_pv_petty_bureaucracy' (or variant),
    at 'common/customizable_localization/glorpui_generated_societal_value_hint_loc.txt:3'
```

The bug is not Russian-specific: it hits all ten non-English languages. The
right fix upstream is for Glorp UI to emit its generated file for every
language, even with English text in it, so the feature does not switch itself
off for everyone who plays in something else.

**The thin list** is a scope fault, and it is Glorp UI's generator being honest
about what it read: government reforms, laws/policies, estate privileges and
advances. The game pushes a societal value from far more than that. Every push
in the game is a `monthly_towards_<direction>` modifier — 34 of them, one per
direction, all flagged `is_societal_value_change = yes` in
`common/modifier_type_definitions`. Scanning every game file for them finds
**1405 pushes across 23 kinds of object**:

```
laws                442      static_modifiers   298      government_reforms 235
estate_privileges   150      auto_modifiers      87      religious_aspects   60
traits               24      parliament_issues   24      building_types      23
employment_systems    9      chivalric_orders     8      subject_types        6
international_orgs    5      estates              5      cabinet_actions      5
regencies             5      religious_schools    4      missions             4
disasters             3      advances             2      parliament_types     1
```

Glorp UI covers three of the twenty-three. That is why *defensive* was empty for
an ordinary country: of its thirteen candidates almost all are national —
`luc_libertas` (Ragusa), `katepanata`, `partitio_reform`, `margraviate` — and a
normal country qualifies for none.

## What it adds

A second block, **«Также влияет на смещение»**, under Glorp UI's own, and a
third, **«Станет доступно при условиях»**, for what is out of reach today but
not out of reach forever. A fourth, **«Влияет на смещение (без фильтра)»**,
replaces both when the mod menu switch is on. 264 hint lines across all 34 directions, of two kinds:

- **catalogue lines** — something to pick or to build: employment system,
  buildings, religious aspects, religious schools, parliament issues, chivalric
  orders, subject types, estates, cabinet actions, international organizations,
  advances, missions;
- **system lines, marked «масштабируется»** — always in force and growing with
  the state of the country: fort/army/navy maintenance, army size and
  experience, average control, average development, literacy, estate shares of
  the population, war and peace, attacker and defender, fort limit, legitimacy.
  Plus "point the cabinet at this value", for each of the 34 directions.

For *defensive* that is 0 → 15 lines, including `fort_maintenance_mod` and the
four parliament issues about building forts. The employment example lands too:
«Способ найма рабочих: Равенство +0.10».

### Filtering by availability

138 of the lines are wrapped in `customizable_localization` with a trigger and
disappear when the country cannot have the thing, and 78 more are listed under
«Станет доступно при условиях» instead. By category: religious aspects 120,
parliament issues 24, international organizations 24, buildings and religious
schools and subject types and chivalric orders and cabinet actions 65 between
them, employment systems 9, estates 5, missions 4, parliament types 2.

| Category | Gate |
| --- | --- |
| Religious aspects | `OR = { religion = religion:X ... }` + `NOT = { has_religious_aspect = ... }` |
| Religious schools | the object's own `enabled_for_country` block, copied verbatim |
| Estates | `country_has_estate = estate_type:X` |
| Parliament issues | `has_parliament = yes` + the estate that raises it + the issue's own `potential` and `allow` |
| Cabinet actions | the action's own `potential` and `allow` blocks, verbatim |
| Subject types | `is_subject_type = X` |
| Chivalric orders | `has_chivalric_order = yes` |
| Buildings | the object's own `country_potential` and `allow` blocks, verbatim |
| Employment systems | `NOT = { has_employment_system = employment_system:X }`, for itself and for every stronger option |
| International organizations | `exists = international_organization:X` + `can_join_international_organization = international_organization:X` |
| Status in an organization | membership of, or joinability of, the organization that grants it |
| Missions | the mission's own `visible` block, verbatim — which opens with `game_has_missions_enabled = yes` |
| Parliament types | the object's own `potential` and `allow` blocks, verbatim |

Argument forms come from `reference/game/docs/triggers.log`, the output of the
console's `script_docs`, where each trigger states its **Supported Scopes** and
**Supported Targets**. `has_employment_system` declares
`Supported Targets: employment_system`, which is where the `employment_system:`
prefix comes from. Nothing is guessed: a trigger form that does not appear
verbatim in the shipped files leaves the line ungated instead, because a
mistyped trigger is a load error and an ungated hint is only noise.

Employment systems are mutually exclusive, so an option is hidden not only when
it is already chosen but when any other option is chosen that pushes the same
axis at least as hard. With *Equality* (+0.10) active, every
`capitalism_prioritising_*` (+0.05) and *Equality* itself drop out.

**The organizations, missions and parliament types were the ungated ones**, and
they are the four the owner asked for on 2026-08-25: the Italian leagues showing
up for a country that can never join one, parliaments a monarchy cannot have,
and missions listed in a game where missions are switched off. Each is gated by
the game's own answer rather than by a guess:

- **`can_join_international_organization`** is an engine trigger, country scope,
  organization target — it is in the engine dump `reference/game/docs/triggers.log` and this mod simply asks
  it. The organization's own `can_join_trigger` cannot be copied instead: it is
  written against `scope:recipient`, which *is* the organization, and a country
  scoped customizable localization has no such scope. `exists` comes first
  because most of these are situational — the Italian leagues exist only while
  the Italian Wars run — and it is the guard the game puts in front of its own
  organization checks.
- **Missions** take the mission's own `visible` block verbatim, which every one
  of them opens with `game_has_missions_enabled = yes` — the game's own scripted
  trigger for the Missions game rule, `NOT = { has_game_rule = mission_packs_disabled }`.
  So a game with missions switched off loses those lines outright. `enabled` is
  deliberately not copied: it answers "can this be finished now", which changes
  month to month, where a hint only needs "is this a thing this country can be
  offered".
- **Parliament types** take `potential` and `allow` verbatim, the same shape as
  buildings. The ones belonging to an international organization gate on
  `international_organization_type`, which is asked of an organization and not
  of a country, so those are left ungated rather than copied into the wrong
  scope.

**Cabinet actions and parliament issues came back from the first run still
unfiltered**, and both were the same oversight: the object carries its own
`potential`, and the mod was not reading it.

- *Дикастерия по евангелизации* and *Влияние Строгановых* were on screen for a
  Catholic German county. They are `office_of_new_converts`, whose `potential`
  wants a location modifier on Kazan, and `stroganov_influences`, whose
  `potential` wants the Stroganov variable. All eight cabinet actions that push
  a societal value carry a `potential`.
- All four *Поддержка строительства …* parliament issues showed at once, when
  only one can ever be valid: `promote_castle_building` requires
  `has_advance = castle_advance` and forbids bastions, star forts and
  fortresses; the other three say the same thing one rung up. `has_parliament =
  yes` could not know that. The issue's `estate` goes in too, because an issue
  is raised by an estate and a country without that estate never sees it.

Copying `potential` verbatim also drops the two issues that carry
`potential = { always = no }` under a comment saying they are driven by events —
which is right, they are not something a country can be offered.

Nothing is left ungated now except what a trigger cannot reach.

Left out entirely: `traits`, `regencies`, `disasters` (situational, not the
player's choice) and the Byzantine `auto_modifiers` branch (hellenization and
latinization, ~50 objects, BYZ only).

### The switch, and what it is for

Filtering is the point, but a filtered list cannot be checked against itself.
`Списки → Фильтрация → Показывать всё без фильтра` in CMF's mod menu turns the
two filtered blocks off and one unfiltered block on: every line the direction
has, with no trigger in front of any of it. For the rare game where the plan is
to fight your way into a region you start nowhere near, and for answering "is
this filtered out, or is it simply not there".

It is a `.gui` condition and nothing more —
`CMMSettingIsRegistered('svx__show_all')` and `CMMValueEqualsOne(...)`, both GUI
functions — so no script runs and the unfiltered body is a plain string that
cannot fail. The registration is the mod's only hand written script:
`in_game/common/scripted_effects/svx_cmm_registration.txt` on CMF's
`cmf_on_mod_registration`. `python3 tools/check_cmm.py
mods/glorpui_hints/in_game/common` checks the call against whichever CMF is in
`reference/`, and checks that every localization key CMM derives is defined.

The switch is per country rather than global: it is a reading preference of the
person looking at the tooltip, and CMF's global variants store one value for the
whole session, which is for rules rather than for what a player wants to see.

### What «масштабируется» actually means

Every scaled and conditional line carries a hover. «(масштабируется)» and
«(условие)» are game concepts this mod defines — the same mechanism Glorp UI
uses for its banner — and their text is compiled out of the modifier's own file:

- an **`auto_modifier`** declares `scales_with`, an ordinary script value block,
  so both the quantity and the value at which the modifier reaches full size are
  computable. `army_tradition multiply = 0.01` is full at **100**;
  `used_fort_limit_percentage subtract = 1.0` at **200%**;
  `value = 0.5 subtract = used_fort_limit_percentage multiply = 2` at **0%**,
  which is what "below half the fort limit" never said out loud. It may declare
  only `potential_trigger`, and then the answer is the condition rather than a
  number: *Армия больше ожидаемой* is `army_size_percentage > 1.0`, which is the
  whole of what "expected army" means.
- a **`static_modifier`** declares neither. The engine scales those when it
  attaches them and neither the shipped files nor the defines say by how much,
  so the hover says exactly that rather than inventing a figure. *Средняя
  грамотность* is one of these: the +0.10 is the maximum and nothing in the
  files says what literacy reaches it.

41 explanations, 13 of them with a computed threshold. The arithmetic declines
anything whose shape it does not cover — two quantities subtracted from each
other, a conditional block — rather than guessing, because a wrong threshold is
worse than none.

The line's label comes from the game's own `$STATIC_MODIFIER_NAME_x$` /
`$AUTO_MODIFIER_NAME_x$` where the game has one, so a patch that renames a
modifier is followed for free and the concept links inside those names come
along. The hand written label is only the fallback.

### Scaling versus conditional

Sources from `static_modifiers` / `auto_modifiers` split in two, and the value is
written differently for each:

- **scaling** — the magnitude grows with the state of the country (fort
  maintenance, army size and experience, average control, estate shares). Marked
  «масштабируется», value written as «до +X», which is the maximum;
- **conditional** — switched on whole when a condition holds (bankruptcy, war,
  over the fort limit, a ruler who is a general). No marking, the condition is
  named in the line itself, and the value is exact.

## What is in the folder

```
.metadata/metadata.json                                     id bag.glorpui_hints, depends on glorp.ui
.metadata/thumbnail.png                                     512x512, carried over from the two mods this replaces
main_menu/localization/russian/
  glorpui_generated_societal_value_hints_l_russian.yml      759 keys — the missing half of Glorp UI
  svx_extra_hints_l_russian.yml                             the added lines, 68 body keys + 216 gated ones
in_game/gui/svx_extra_societal_value_hints.gui              the two tooltip templates, overridden
in_game/common/customizable_localization/svx_extra_hint_loc.txt   216 availability gates
in_game/common/script_values/svx_extra_hint_script_values.txt     51 visibility values
```

Everything under `main_menu/` and `in_game/` is generated. `svx_` is this mod's
prefix for the names it puts into the game's namespace.

## Rebuilding

```
python3 mods/glorpui_hints/tools/generate.py
```

That is what `tools/refresh.py` runs, and it does two different jobs.

**The Russian hint text is regenerated every time**, out of Glorp UI's own
English file. The hints come from three templates, and everything language
specific in them is the leading verb phrase — the reform, policy and privilege
names arrive through `$key$` references the game resolves in the active
language. So the Russian file is the English file with three phrases replaced:

| English | Русский |
|---|---|
| `Grant <privilege>` | `Даровать привилегию <привилегия>` |
| `Add the <reform> [government_reform\|e]` | `Принять реформу правления <реформа>` |
| `Enact the <policy> [policy]` | `Ввести политику <политика>` |

The trailing concept tokens are dropped: they only read in English word order,
and in Russian the verb phrase has already named the object type. A Glorp UI
update that adds hints is picked up with nobody noticing; one that writes a
fourth shape fails the run and names the key.

**The added lines are not**, because they are compiled out of the game's own
`common/` tree, which is large and only partly needed. It is all in `reference/`
now — see [where the game files come from](#where-the-game-files-come-from) — so
the rebuild is one flag away, and the files are committed rather than rebuilt on
every run because the scan takes a minute:

```
python3 mods/glorpui_hints/tools/generate.py --game-files reference/game
```

### What the run checks even when it rebuilds nothing

The mod's real hazard is not a load error. It overrides Glorp UI's override and
**re-emits Glorp UI's own list inside it**, so if Glorp UI restructures those
templates nothing fails at load: the player quietly gets this mod's older copy
of Glorp UI's list and never sees what Glorp UI added. Nothing in `error.log`
would say so.

So every run compares the two files as an ordered sequence of tooltip lists —
which script value gates each one, which title it carries, which body key it
prints — and fails naming the difference:

```
Glorp UI now lists GLORP_UI_SVH_BODY_NEWTHING (glorpui_svh_visible_hellenization)
in SocietalValueCountryRight_tooltip and this mod does not — rebuild with --game-files
```

It also checks that every name the `.gui` reaches for resolves: each script value
is defined here or by Glorp UI, each `[Localize(...)]` key exists, each
`[Player.Custom(...)]` has a rule behind it, and each rule is actually printed by
something. A `.gui` asking for a name nothing defines does not fail to load — it
prints zero, or the raw key, which is the exact fault this mod exists to repair.

**And every trigger the gates call is a name that exists.** A mistyped trigger is
a load error — but in the *player's* game, a round trip away. Three sources
answer it together: the engine's dump, the game's `scripted_triggers/`, and
every name the game itself writes in the same position anywhere in `common/`.
The third is not optional: `religion = religion:catholic` and
`culture = culture:low_frankish` are scope comparisons, appear in the dump
nowhere, and the game writes them 598 and 1 418 times.

The check earned itself on the first run. `country_religion = religion:X` gated
**492** religious aspect lines and `country_religion` does not exist — not in the
dump, not anywhere in the game's script. The comment in `gates.py` claimed it
was confirmed in `common/religious_aspects`; what those files carry is
`religion = calvinist`, the aspect declaring its own religion, which is a
different thing in a different scope. It is `religion = religion:X` now.

## What it costs the interface

`python3 tools/guicost.py` prices it at **136 widgets in one file, no
`GetScriptedGui`, no always-live window, no loop** — the cheapest thing in the
tree. What it does spend is script calls while a societal value tooltip is up:
136 `visible` expressions, one per tooltip list, each running a script value.
Thirty-three of every thirty-four fail on their first line
(`scope:glorpui_sv = societal_value_type:X`) and cost nothing more. The axis that
matches then evaluates its body, which is up to 21 `Player.Custom` gates on the
worst direction. Glorp UI's own version already ran 34 of those `visible` calls;
this mod takes it to 136, of which 34 are the unfiltered block that is hidden
unless the switch is on.

That is worth keeping in mind against the open
[panel-hitch question](../../docs/HANDOFF.md), whose live hypothesis is hover:
this is a hover-built tooltip that runs script. It has never been measured.

## Where the game files come from

Rebuilding the added lines needs the directories named in
`tools/game_files_manifest.txt`. **They are all in `reference/` as of
2026-08-25**, and the scan they feed reports 1426 societal value pushes across
23 kinds of object — complete. The list, and where each one actually lives:

Twenty three directories under `in_game/common/` — laws, government reforms,
estate privileges, religious aspects and schools, estates, subject types,
chivalric orders, parliament issues and types, employment systems, cabinet
actions, international organizations, missions, advances and the rest — plus two
that are **not under `in_game/` at all**: `main_menu/common/static_modifiers`
(298 pushes, the whole scaling half) and
`main_menu/common/modifier_type_definitions`. That second pair is why the
manifest carries a real path per entry rather than assuming a mount.

`tools/extract_game_files.ps1` copies the list out of an EU5 install straight
into `reference/game/` — run it on the machine that has the game, then commit
what appears. `tools/extract_game_files.py` is the same thing where Python is
easier to reach. Both read `tools/game_files_manifest.txt`, so the list cannot
drift between them; both give a directory that is not where the manifest says
one search by name across the whole install before calling it missing; and both
sweep every `.txt` in the install for `monthly_towards_`, so a directory Paradox
renames comes along regardless.

## What is untested

- **Whether the thumbnail is load-bearing.** Both mods this replaces shipped a
  512x512 `.metadata/thumbnail.png` on the belief that the launcher skips a mod
  without one, and both were listed. Every other mod in this repository ships
  none and is listed too. So one of the two is wrong and nobody has isolated
  which; the file is carried over because it costs 1.8 KB to keep.
- **The mod menu switch.** CMM registration is the most silent-failing thing in
  this repository: a mod that never registers shows no row and logs nothing.
  Look for `Подсказки общественных ценностей → Списки → Фильтрация` in CMF's mod
  menu. If the row is absent, registration did not run; if the row is there and
  the tooltip does not change, the `.gui` condition is wrong. The two fail
  differently, which is why they are worth telling apart.
- **The hover on «(масштабируется)» and «(условие)».** These are game concepts
  this mod defines. Glorp UI proves a mod *can* define one, but its examples all
  carry a `texture` and these carry only `shown_in_encyclopedia = no` — a
  text-only concept is unproven here, and vanilla's own `game_concepts/` is not
  in `reference/` to check against. If it does not work the symptom is on those
  41 lines only: the word renders without a hover, or renders as `ERROR:`.
  Reverting is one line in the generator.
- **The cabinet action and parliament issue gates.** What to look for:
  *Дикастерия по евангелизации* and *Влияние Строгановых* gone, and exactly one
  *Поддержка строительства …* line instead of four.
- **The religious aspect gate.** The organizations and missions gates are
  confirmed on screen; this one is not, because the owner plays Catholic, where
  aspects are set by the Papacy rather than chosen. It needs a run as a religion
  that picks its own — Lutheran, for instance. Until then the `country_religion`
  repair is reasoned, not seen.
- **English.** Out of scope by the owner's decision unless the mod is ever
  published. The added lines are Russian only, so an English game finds no
  `SVX_*` keys and renders the new blocks as raw keys. Fixing it is a change to
  the generator — English for fourteen category nouns and two block titles — not
  to the files.


# Glorp UI — Societal Value Hints (RU)

One mod that does both halves of the societal value tooltip: it gives Glorp UI's
own hint list a Russian text, and then adds the sources Glorp UI's generator
never looks at.

Requires **Glorp UI** (`glorp.ui`) and must load **after** it — the mod overrides
Glorp UI's own override of the tooltip templates. `.metadata/metadata.json`
declares the dependency, so the launcher orders it.

> Both halves ran in game as two separate mods and worked. This folder is those
> two merged, with the same generated files; the merge itself has not been
> loaded. See [what is untested](#what-is-untested).

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
not out of reach forever. 243 hint lines across all 34 directions, of two kinds:

- **catalogue lines** — something to pick or to build: employment system,
  buildings, religious aspects, religious schools, parliament issues, chivalric
  orders, subject types, estates, cabinet actions, international organizations,
  advances, missions;
- **system lines, marked «масштабируется»** — always in force and growing with
  the state of the country: fort/army/navy maintenance, army size and
  experience, average control, average development, literacy, estate shares of
  the population, war and peace, attacker and defender, fort limit, legitimacy.
  Plus "point the cabinet at this value", for each of the 34 directions.

For *defensive* that is 0 → 9 lines, including `fort_maintenance_mod` and the
four parliament issues about building forts. The employment example lands too:
«Способ найма рабочих: Равенство +0.10».

### Filtering by availability

216 of the lines are wrapped in `customizable_localization` with a trigger and
disappear when the country cannot have the thing:

| Category | Gate |
| --- | --- |
| Religious aspects | `OR = { country_religion = religion:X ... }` + `NOT = { has_religious_aspect = ... }` |
| Religious schools | the object's own `enabled_for_country` block, copied verbatim |
| Estates | `country_has_estate = estate_type:X` |
| Parliament issues | `has_parliament = yes` |
| Subject types | `is_subject_type = X` |
| Chivalric orders | `has_chivalric_order = yes` |
| Buildings | the object's own `country_potential` and `allow` blocks, verbatim |
| Employment systems | `NOT = { has_employment_system = employment_system:X }`, for itself and for every stronger option |

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

Left ungated: missions, international organizations and parliament types — the
roster has no "the country has this object" trigger for them.

Left out entirely: `traits`, `regencies`, `disasters` (situational, not the
player's choice) and the Byzantine `auto_modifiers` branch (hellenization and
latinization, ~50 objects, BYZ only).

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
`common/` tree and almost none of that is in `reference/` — see
[what this needs](#what-this-needs-that-reference-does-not-have). They are
committed as generated files and rebuilt only when the game files are handed
over:

```
python3 mods/glorpui_hints/tools/generate.py --game-files <unpacked game files>
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

## What it costs the interface

`python3 tools/guicost.py` prices it at **102 widgets in one file, no
`GetScriptedGui`, no always-live window, no loop** — the cheapest thing in the
tree. What it does spend is script calls while a societal value tooltip is up:
102 `visible` expressions, one per tooltip list, each running a script value.
Thirty-three of every thirty-four fail on their first line
(`scope:glorpui_sv = societal_value_type:X`) and cost nothing more. The axis that
matches then evaluates its body, which is up to 21 `Player.Custom` gates on the
worst direction. Glorp UI's own version already ran 34 of those `visible` calls;
this mod takes it to 102.

That is worth keeping in mind against the open
[panel-hitch question](../../docs/HANDOFF.md), whose live hypothesis is hover:
this is a hover-built tooltip that runs script. It has never been measured.

## What this needs that `reference/` does not have

Rebuilding the added lines needs the game's `in_game/common/` tree, and
`reference/game/in_game/common/` carries seven directories of it. Missing, and
needed:

```
societal_values/              the 34 axis pairs — without this nothing can be built
modifier_type_definitions/    which modifiers are societal value changes
laws/  government_reforms/  estate_privileges/  advances/
static_modifiers/  auto_modifiers/
religious_aspects/  religious_schools/  estates/  subject_types/
chivalric_orders/  parliament_issues/  parliament_types/
employment_systems/  cabinet_actions/  international_organizations/  missions/
script_values/                for `societal_value_monthly_move` and its siblings
```

Until those arrive the generated files are frozen at whatever game version they
were built against, and a patch that adds or renames a source is invisible here.

## What is untested

- **Whether the thumbnail is load-bearing.** Both mods this replaces shipped a
  512x512 `.metadata/thumbnail.png` on the belief that the launcher skips a mod
  without one, and both were listed. Every other mod in this repository ships
  none and is listed too. So one of the two is wrong and nobody has isolated
  which; the file is carried over because it costs 1.8 KB to keep.
- **The merge itself.** Two mods became one folder with one id
  (`bag.glorpui_hints`). Nothing about the contents changed apart from the
  generator names in the header comments, but no run has loaded it.
- **Removing the old two.** `glorpui_ru_svh_fix` and `glorpui_svh_extra` must
  come out of the playset; leaving either alongside this one means two mods
  defining the same keys and overriding the same templates.
- **The added lines against the current game version.** They were compiled from
  the game files as they were, and nothing here can re-read them.
- **English.** The added lines are Russian only. In an English game the `SVX_*`
  keys are missing and the new blocks render as raw keys — the same fault this
  mod fixes for Glorp UI, in the other direction. Fixing it means English labels
  for the fourteen category nouns and the two block titles, which is a change to
  the generator, not to the files.

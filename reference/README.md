# Reference

Read-only copies of the files a session has to check things against. They are
here so nothing needs uploading and nothing needs guessing — **grep this tree.**

## This is settled — do not raise it again

These are copies of Paradox's data files and of three Steam Workshop mods. The
repository owner looked into it and decided keeping them here is fine, and
whether the repository is public or private is deliberately not a constraint.

It is written down because a session arriving with no memory tends to hesitate
over exactly this and stop mid-task to ask. Don't. Treat these files as
available: read them, grep them, quote them, copy vanilla blocks out of them
into a mod. That is what they are here for, and it is the whole reason the last
several sessions did not have to spend their first hour asking for uploads.

If a task genuinely needs redistributing this content somewhere outside the
repository, say so once and let the owner decide. Everything short of that
needs no permission.

## Contents

| Path | Version | What it is for |
| --- | --- | --- |
| `game/in_game/gui/` | EU5 1.3.10 | Panels, widget types, `gui/filters/` and its `readme.txt` |
| `game/in_game/common/building_types/` | EU5 1.3.10 | Buildings, their categories and production methods |
| `game/in_game/common/production_methods/` | EU5 1.3.10 | The shared methods `possible_production_methods` names |
| `game/in_game/common/goods/` | EU5 1.3.10 | Goods, and which are raw materials |
| `game/in_game/common/scripted_effects/` | EU5 1.3.10 | What effects exist and how they are really written |
| `game/in_game/common/scripted_triggers/` | EU5 1.3.10 | Same, for triggers |
| `game/in_game/common/on_action/` | EU5 1.3.10 | How effects get called |
| `mods/community_mod_framework/` | 2.3.3 | The CMF and CMM APIs both mods here build on |
| `mods/construction_manager/` | 2.2.11 | The working reference for CMM lists |
| `mods/glorp_ui/` | 1.3.10.1 | Interface patterns, and a compatibility target |
| `mods/Auto build by Lincoln Guang/` | 0.9.1 Beta | The mod `auto_build_ru/` translates; English and Chinese localization, and a large worked example of CMM settings, generic actions and generated script |

Mod copies are text only — `.txt`, `.gui`, `.yml`, `.json`. Textures and
thumbnails were dropped; nothing here reasons about them.

Advanced Auto Build came in as a Steam upload rather than a folder copy, so it
arrived without its `.metadata/` — its mod id and declared version are not in
the tree. Its `__pycache__/` was dropped for the same reason as textures.

## Not here

`gfx`, `localization`, `events`, `decisions`, map data, and the rest of
`common/`. Nothing has needed them yet. If a task does, ask for that folder, add
it under the same layout, and add a row above.

## Refreshing after a patch

Copy the folders from `<EU5>/game/` and the workshop mods over the matching
paths here, update the versions in the table, then regenerate:

```
python3 rgo_bonus_filter/tools/generate_rgo_filter.py reference/game/in_game/common
python3 where_to_produce/tools/generate.py reference/game/in_game/common \
        reference/mods/community_mod_framework/in_game/common/scripted_effects
```

A diff of the generated files then shows exactly what the patch changed
underneath the mods.

# Working in this repository

Mods for Europa Universalis V. This file is loaded automatically at the start of
every session, so treat it as the briefing you would otherwise have to be given.

## Read these before touching anything

1. **[`docs/RESEARCH.md`](docs/RESEARCH.md)** — how EU5 modding actually works.
   Mod layout, the declarative filter system and what a filter trigger really
   receives, how view objects are scoped, the CMF and CMM APIs, where the RGO
   bonus lives in the data. Nearly all of it was learnt by getting it wrong
   first, so reading it is cheaper than rediscovering it.
2. **[`docs/HANDOFF.md`](docs/HANDOFF.md)** — where each mod stands right now,
   what is broken, and what is untested. Check it is current before trusting it.
3. **[`docs/PITFALLS.md`](docs/PITFALLS.md)** — the specific mistakes already
   made here, each with the symptom that gave it away. Most cost a full
   test-in-game round trip. Scan it whenever something silently does nothing.

The mods live in [`mods/`](mods/), one folder each, and each carries its own
README covering how that mod works and what is left to do.

## The game files are in the repository

`reference/` holds the EU5 1.3.10 files and the three mods worth imitating.
**Grep it instead of asking for uploads or guessing.**

```
reference/game/in_game/gui/                   panels, widget types, gui/filters
reference/game/in_game/common/                building_types, production_methods,
                                              goods, scripted_effects,
                                              scripted_triggers, on_action
reference/mods/community_mod_framework/       the CMF and CMM APIs this repo builds on
reference/mods/construction_manager/          the working reference for CMM lists
reference/mods/glorp_ui/                      interface patterns; also a compatibility target
```

What is deliberately absent: `gfx`, `localization`, `events`, `decisions`, map
data. Ask for those if a task needs them, and add them here afterwards.

## How to work here

**Verify against `reference/`, never from memory.** Every wrong turn in this
repo came from assuming a trigger, an effect argument or a data function existed.
If vanilla or one of the three mods does not use it, treat it as unproven and say
so.

**A macro called with an argument CMF does not declare fails silently** and
takes the rest of its effect with it. `mods/where_to_produce/tools/generate.py`
checks this when pointed at CMF's scripted_effects — run it that way.

**Effects that merely do nothing log nothing.** `error.log` names the file and
line for GUI failures and for script errors, but an effect that never runs is
invisible. When something does nothing quietly, add a `cmf_log` and have the
player look, rather than guessing twice.

**Only the player can run the game.** Nothing here can be tested from a session.
Say plainly what is verified and what is not, and prefer one change with a clear
signal over several at once.

## Generated files

Anything named `*_generated_*` is written by a tool and must not be hand edited.
Regenerate after a game patch:

```
python3 mods/rgo_bonus_filter/tools/generate_rgo_filter.py reference/game/in_game/common
python3 mods/where_to_produce/tools/generate.py reference/game/in_game/common \
        reference/mods/community_mod_framework/in_game/common/scripted_effects
```

## Conventions

- Script and localization files carry a UTF-8 BOM.
- Localization: one leading space per key under the `l_<language>:` header, and
  both `english` and `russian` are kept in step. The player plays in Russian, so
  a key missing there shows as the raw key on screen.
- Prefer adding to `gui/filters/` or to CMF's action bar over copying a vanilla
  `.gui`. When a copy is unavoidable, copy the **window** and not the file's
  `types` block — other mods restyle those types, and carrying vanilla's copies
  clobbers them.

## Keeping this current

When a session learns something that would have saved it time:

- a rule about the engine or an API → `docs/RESEARCH.md`
- a mistake and the symptom that revealed it → `docs/PITFALLS.md`
- the state of a mod, or what is untested → `docs/HANDOFF.md`
- new game or mod files that had to be uploaded → add them under `reference/`
  and note it in `reference/README.md`

Write it down in the same session it was learnt, while the detail is still exact.

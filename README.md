# EU5 Modding Workspace

A workbench for building mods for **Europa Universalis V**, and the accumulated
knowledge of how to do that without rediscovering the same things every time.

The game ships no modding documentation. Everything here was worked out by
reading the game's own files, imitating mods that already work, and reading
`error.log` after each attempt. That process is expensive, so its results are
written down rather than kept in anyone's head.

## What is here

| | |
| --- | --- |
| **[`mods/`](mods/)** | The mods themselves, one folder each |
| **[`docs/`](docs/)** | How EU5 modding works, what has already gone wrong, where each mod stands |
| **[`reference/`](reference/)** | The game's own files and three mods worth imitating, to check against |
| **[`CLAUDE.md`](CLAUDE.md)** | Loaded automatically by Claude Code; the briefing a fresh session starts from |

## Mods

| Mod | What it does | State |
| --- | --- | --- |
| [`mods/rgo_bonus_filter/`](mods/rgo_bonus_filter/) | Filter chips that cut both building lists down to what gains production efficiency from raw materials in the province | Working |
| [`mods/where_to_produce/`](mods/where_to_produce/) | Pick a province, get a ranked list of what is worth building there | In progress |

Each folder is a complete mod: copy the folder itself into
`Documents/Paradox Interactive/Europa Universalis V/mod/`. Both depend on the
Community Mod Framework for their settings.

## Docs

- **[`docs/RESEARCH.md`](docs/RESEARCH.md)** — how EU5 modding actually works.
  Mod layout, the declarative filter system and what a filter trigger really
  receives, how view objects are scoped, the CMF and CMM APIs, where the RGO
  bonus lives in the data.
- **[`docs/PITFALLS.md`](docs/PITFALLS.md)** — mistakes already made, each with
  the symptom that gave it away. None of them raise an error you would notice,
  which is exactly why they are written down.
- **[`docs/HANDOFF.md`](docs/HANDOFF.md)** — where each mod stands, what is
  broken, what has never been run.
- **[`docs/SESSION_START.md`](docs/SESSION_START.md)** — the prompt to open a
  new session with.

## Reference

`reference/` holds EU5 1.3.10's `gui` and the parts of `common` that matter,
plus Community Mod Framework, Construction Manager and Glorp UI. It is there so
a session can grep for an answer instead of guessing or asking for uploads —
which is where most of the wasted effort in this repository has gone.

## How the work goes

Nothing here can be tested from a session: only the player can run the game. So
the loop is one change with a clear signal, then a screenshot and `error.log`.
That log names the file and the line, and has found every bug in this repository
so far — usually in one pass. The failure that costs a round trip is the silent
one, where an effect never runs and nothing is logged at all.

Anything named `*_generated_*` is written by a tool from the game's own data and
must not be hand edited. Regenerate after a patch:

```
python3 mods/rgo_bonus_filter/tools/generate_rgo_filter.py reference/game/in_game/common
python3 mods/where_to_produce/tools/generate.py reference/game/in_game/common \
        reference/mods/community_mod_framework/in_game/common/scripted_effects
```

A diff of the generated files then shows exactly what the patch changed
underneath the mods.

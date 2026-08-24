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
| [`mods/goods_target/`](mods/goods_target/) | Build for a construction discount: keep building the producers of chosen goods until building everything else is cheap. An addon to Construction Manager | First step, untested |
| [`mods/auto_build_ru/`](mods/auto_build_ru/) | Russian localization for Advanced Auto Build, which ships English and Chinese only | Working |
| [`mods/nd_ru/`](mods/nd_ru/) | Russian localization for National Destinies, which ships eleven languages all carrying the English text | In progress |

Each folder is a complete mod: copy the folder itself into
`Documents/Paradox Interactive/Europa Universalis V/mod/`.

One mod was removed: `where_to_produce`, a province-first "what is worth building
here" table, which was built to completion without ever being loaded in game and
then abandoned. What it taught, and where its working parts went, is in
[`docs/HANDOFF.md`](docs/HANDOFF.md#why-where_to_produce-failed).

## Docs

- **[`docs/TESTLOG.md`](docs/TESTLOG.md)** — what has actually been in the game
  and what it showed. Only the player can run EU5, so a run is the scarcest
  thing here; each one gets written down.
- **[`docs/RESEARCH.md`](docs/RESEARCH.md)** — how EU5 modding actually works.
  Mod layout, the declarative filter system and what a filter trigger really
  receives, how view objects are scoped, the CMF and CMM APIs, where the RGO
  bonus lives in the data, and how to translate somebody else's mod.
- **[`docs/PITFALLS.md`](docs/PITFALLS.md)** — mistakes already made, each with
  the symptom that gave it away. None of them raise an error you would notice,
  which is exactly why they are written down.
- **[`docs/HANDOFF.md`](docs/HANDOFF.md)** — where each mod stands, what is
  broken, what has never been run.
- **[`docs/SESSION_START.md`](docs/SESSION_START.md)** — the prompt to open a
  new session with.

## Reference

`reference/` holds EU5's `gui` and the parts of `common` that matter, plus
Community Mod Framework, Construction Manager, Glorp UI and the two mods being
translated. It is there so a session can grep for an answer instead of guessing
or asking for uploads — which is where most of the wasted effort in this
repository has gone.

The owner refreshes it by hand whenever something updates, so what is in it and
at which version is a question for the tree, not for a document:

```
python3 tools/refs.py
```

## How the work goes

Nothing here can be tested from a session: only the player can run the game. So
the loop is one change with a clear signal, then a screenshot and `error.log`.
That log names the file and the line, and has found every bug in this repository
so far — usually in one pass. The failure that costs a round trip is the silent
one, where an effect never runs and nothing is logged at all.

Anything named `*_generated_*` is written by a tool from the game's own data and
must not be hand edited. After a patch, or after any refresh of `reference/`:

```
python3 tools/refresh.py
```

It rebuilds every generated file and then names the ones that changed — which is
exactly what the patch changed underneath the mods.

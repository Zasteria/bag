# Working in this repository

Mods for Europa Universalis V. This file is loaded automatically at the start of
every session, so treat it as the briefing you would otherwise have to be given.

## What this session is for

**[`docs/NEXT_SESSION.md`](docs/NEXT_SESSION.md) — read it before anything else.**
It names the one job in progress, what five evenings of the owner's testing have
already settled, and what not to ask him to do again. The rest of this file is how
to work here; that file is what to work on.

## Read these before touching anything

1. **[`docs/RESEARCH.md`](docs/RESEARCH.md)** — the index to how EU5 modding
   actually works, split by subject: [`research/engine.md`](docs/research/engine.md)
   for what the engine gives a mod, [`research/cmf.md`](docs/research/cmf.md) for
   the framework and Construction Manager's automation,
   [`research/translation.md`](docs/research/translation.md) for translating
   somebody else's mod. Read the one the task needs, not all three. Nearly all of
   it was learnt by getting it wrong first, so reading it is cheaper than
   rediscovering it.
2. **[`docs/HANDOFF.md`](docs/HANDOFF.md)** — where each mod stands right now,
   what is broken, and what is untested. It opens with a table of questions the
   owner's test runs have already answered; **never ask for a measurement listed
   there.** Check the rest is current before trusting it.
3. **[`docs/PITFALLS.md`](docs/PITFALLS.md)** — the specific mistakes already
   made here, each with the symptom that gave it away. Most cost a full
   test-in-game round trip. Scan it whenever something silently does nothing.

The mods live in [`mods/`](mods/), one folder each, and each carries its own
README covering how that mod works and what is left to do.

## The game files are in the repository

`reference/` holds the EU5 files and the mods worth imitating.
**Grep it instead of asking for uploads or guessing.**

```
reference/game/in_game/gui/                   panels, widget types, gui/filters
reference/game/in_game/common/                building_types, production_methods,
                                              goods, scripted_effects,
                                              scripted_triggers, on_action
reference/game/main_menu/localization/        what the game calls its own concepts
reference/game/docs/                          the engine's own API dump — ask it with tools/api.py
reference/mods/                               CMF, Construction Manager, Glorp UI,
                                              and the two mods being translated
```

**Do not hardcode a mod's folder name, and do not trust a version written in
prose.** The owner refreshes these by hand whenever a mod updates, and the
folder name arrives however the upload produced it — `community_mod_framework`
one time, `3692202776_community_mod_framework` the next. Ask the tree instead:

```
python3 tools/refs.py                                  what is there, with versions
python3 tools/refs.py --path community_mod_framework   where it is right now
```

In a tool, `import refs` and call `refs.known("cmf")`, which resolves the mod by
the `id` inside its `metadata.json`. `reference/INVENTORY.md` is the same list,
written by that tool.

These files are here to be used — read, grepped, quoted, and copied from into a
mod. The owner has settled that question; see `reference/README.md`. Do not stop
mid-task to ask about it, and do not treat a mod arriving at a newer version as
a problem to report — it is the normal state of this tree.

What is deliberately absent: `gfx`, `events`, `decisions`, map data, and most of
`common/`. Ask for those if a task needs them, and add them here afterwards.

## How to work here

**Ask the game whether something exists.** It prints its own API, and the dumps
are in `reference/game/docs/`:

```
python3 tools/api.py set_subsidized      an effect, trigger, target or GUI function by name
python3 tools/api.py --find subsid       substring, across every dump
```

Never conclude from "no mod here uses it" that the engine lacks it — that
mistake cost a redesign. What the dumps do not answer is *how* something
behaves; for that, verify against vanilla and the reference mods, never from
memory, and say plainly when something is unproven.

**A macro called with an argument CMF does not declare fails silently** and
takes the rest of its effect with it. `python3 tools/check_cmm.py
mods/<mod>/in_game/common` checks a whole mod for it — run it after touching any
CMM call.

**Effects that merely do nothing log nothing.** `error.log` names the file and
line for GUI failures and for script errors, but an effect that never runs is
invisible. When something does nothing quietly, add a `cmf_log` and have the
player look, rather than guessing twice.

**Only the player can run the game.** Nothing here can be tested from a session.
Say plainly what is verified and what is not, and prefer one change with a clear
signal over several at once. Build the smallest thing that would show a signal
and ask for a run — a whole feature finished before its first load is how
`where_to_produce` ended up with six suspects and no way to choose between them.

**When the player reports a run, write it into [`docs/TESTLOG.md`](docs/TESTLOG.md)
in the same session.** They report it once, in passing; if a session does not
record it, the next one goes on calling the thing untested.

## The tools are part of the repository

Every generator and checker lives in `mods/*/tools/` and is committed. **Nothing
about them is carried in a session's head** — a fresh session gets them by
reading the repository, and a rule they enforce today they will enforce next
year. When a session learns a rule the hard way, the cheapest place to put it is
inside the checker that would have caught it, not only in prose.

At the top level, `tools/` is what every mod's tooling shares:

| | |
| --- | --- |
| `refs.py` | where the reference tree is, resolved by mod id rather than folder name |
| `refresh.py` | the one command to run after the owner refreshes `reference/` |
| `api.py` | what the engine actually has: effects, triggers, on_actions, GUI functions |
| `check_cmm.py` | every CMM call in a mod: CMF's declared arguments, and every localization key CMM will look for |
| `check_docs.py` | the documents still describe files that exist |
| `eu5data.py` | the game's goods, methods and building types, and the RGO formula |
| `guicost.py` | what the interface costs before anybody clicks: always-live windows, script calls from `.gui`, filter chips per tag |
| `playset.py` | which mods the player actually runs, read out of the mount table in his own `debug.log` |

`.claude/hooks/session-start.sh` runs the first two checkers at the start of
every session and hands the result back as context, so a session begins knowing
the state of the tree rather than what a document last remembered.

`mods/nd_ru/tools/` is the fullest example:

| | |
| --- | --- |
| `generate_ru.py` | собирает игровые файлы из `translations/` и отказывается писать сломанное |
| `scope.py` | что осталось перевести, по файлам и по приоритету |
| `term.py` | как игра сама называет своё понятие (advances — «Улучшения») |

`generate_ru.py` уже дважды остановил ошибку, которую не заметил глаз: китайский
иероглиф посреди русского слова и забытое английское слово в русской фразе. Обе
проверки появились после того, как ошибка случилась, — это и есть способ здесь
работать.

## Generated files

Anything named `*_generated_*` is written by a tool and must not be hand edited.
After anything under `reference/` changes — a game patch, a mod update, an
upload the owner did without saying so — one command rebuilds all of it and
reports what moved:

```
python3 tools/refresh.py
```

Nothing else needs doing about a refresh, and nothing anywhere records a version
by hand. Run it at the start of a session too: it is cheaper than believing a
document. `--check` reports and then reverts, for when you only want to know.

Each generator still runs on its own and takes an explicit path when you want a
different copy of the files. The two translation generators are the ones run
after the *mod each translates* updates rather than after a game patch, and they
fail naming the keys when that mod's English file has moved.

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

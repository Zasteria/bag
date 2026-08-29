# Working in this repository

Mods for Europa Universalis V. Six of them, in [`mods/`](mods/), plus the game's
own files to grep and the tooling that rebuilds everything.

## Do not read this repository. Ask it.

The documents here are worth about ninety thousand tokens. Reading them is how a
session spends its whole budget before writing a line — and pays for them again
on every turn afterwards, because the context is resent each time. So:

    python3 tools/kb.py <words>            which section answers this, and what it costs
    python3 tools/kb.py --show FILE:LINE   read exactly that section
    python3 tools/kb.py --map              every document, every section, with sizes

**Open a whole document only when `kb.py` says the answer fills it.** Grep is
the same instinct: `grep -rn` over `reference/` beats reading a game file.

## Start of a task

1. **The task names a mod** → read `mods/<mod>/CLAUDE.md`, that one only. It
   holds the state, the commands, and what fails silently in that mod.
   [`docs/STATUS.md`](docs/STATUS.md) is the one-line-each index if you need to
   pick.
2. **The task names no mod** → [`docs/NEXT_SESSION.md`](docs/NEXT_SESSION.md) is
   the job in progress.
3. **Before designing any test** → [`docs/SETTLED.md`](docs/SETTLED.md). It is
   short, every row cost the owner an evening, and asking for one of those
   measurements again is the one thing this repository cannot afford.

Everything else is on demand: [`docs/PITFALLS.md`](docs/PITFALLS.md) when
something silently does nothing, [`docs/RESEARCH.md`](docs/RESEARCH.md) for how
the engine and CMF actually work, [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md)
for the reference tree and the rebuild loop,
[`docs/WORKSHOP.md`](docs/WORKSHOP.md) when putting a mod out.

## Rules that exist because breaking them is silent

- **Only the player can run the game.** Nothing here can be tested from a
  session. Say plainly what is verified and what is not. Build the smallest
  thing that would show a signal and ask for one run — a whole feature finished
  before its first load is how `where_to_produce` ended up with six suspects and
  no way to choose between them.
- **A run the player reports goes into [`docs/TESTLOG.md`](docs/TESTLOG.md) in
  the same session.** They report it once, in passing. A session that does not
  write it down leaves the next one calling the thing untested.
- **A CMM macro called with an argument CMF does not declare fails silently**
  and takes the rest of its effect with it. One `step` instead of `step_value`
  cost a full round trip. `python3 tools/check_cmm.py mods/<mod>/in_game/common`
  after touching any CMM call.
- **Effects that merely do nothing log nothing.** `error.log` names the file and
  line for GUI and script failures; an effect that never runs is invisible. Add
  a `cmf_log` and have the player look, rather than guessing twice.
- **A `building_type` filter receives `root` and nothing else** — not
  `scope:target`, whatever vanilla's comment says. Reading it logs an error every
  pass.
- **A `customizable_localization` cannot be overridden.** First definition wins;
  later ones are dropped with `gamedatabase.h: Duplicated key`. The way round
  another mod's rule is to take over the localization key it prints.
- **Square brackets in a localization value are data function syntax**, so a
  plain `[debug]` in a label renders as `ERROR:`. The same syntax is what lets a
  row label read a global variable back.
- **A CMF action bar element is drawn from localization**: `_icon` takes a
  texticon like `@good!`, and `_color` must name one of CMF's palette entries or
  the button is invisible in the bottom bars.
- **Script and localization files carry a UTF-8 BOM**, and localization keys
  take one leading space. The player plays in Russian: a key missing there shows
  as the raw key on screen.

## Ask the game whether something exists

    python3 tools/api.py set_subsidized      an effect, trigger, target or GUI function
    python3 tools/api.py --find subsid       substring, across every dump

**Never conclude from "no mod here uses it" that the engine lacks it** — that
mistake cost a redesign. The dumps say what exists, not how it behaves; for
behaviour verify against `reference/`, never from memory, and say plainly when
something is unproven.

Do not hardcode a reference folder's name and do not trust a version written in
prose: `python3 tools/refs.py`, or `refs.known("cmf")` in a tool.

## Rebuilding

    python3 tools/refresh.py           rebuild every generated file, report what moved

Run it at the start of a session; it is cheaper than believing a document. The
owner does this and the rest of his mod loop from `mods.bat`, a menu rather than
a command to remember. **Do not tell him to run the pieces by hand when the menu
covers it**, and do not build a step only a session can perform.

## Keeping this current

Write it down in the same session it was learnt, in the smallest place that
holds it — and keep that place small:

| what | where |
| --- | --- |
| a rule about the engine or an API | `docs/RESEARCH.md` and the file it indexes |
| a mistake and the symptom that revealed it | `docs/PITFALLS.md` |
| a mod's state, or what is untested | `mods/<mod>/CLAUDE.md`, one line in `docs/STATUS.md` |
| a measurement a run settled | `docs/TESTLOG.md`, and `docs/SETTLED.md` if it closes a question |
| a rule a checker could enforce instead | the checker |

**Everything under `docs/` has a size budget and `tools/check_docs.py` enforces
it.** A document that has outgrown its budget is not trimmed by deleting what it
knows — it is split, and the finished half moves to `docs/archive/`, which
`kb.py` still searches. The budget exists because this repository already grew
past the point where a session could afford to read it once.

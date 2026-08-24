# EU5 modding notes

How EU5 modding actually works, learnt mostly by getting it wrong first. The
game ships no modding documentation, so everything here came from the game's own
files, from mods that already work, and from `error.log` after each attempt.

Split by subject, because a session rarely needs more than one of them: a
translation does not care how a CMM list is registered, and an interface mod
does not care what a `$vanilla_key$` passthrough is.

| | |
| --- | --- |
| **[`research/engine.md`](research/engine.md)** | What the engine gives a mod: how to ask it what exists, mod layout, list filters and what a trigger really receives, view object scoping, scripted widgets, why localization is code and the ways it fails to compile, and where the RGO bonus and the goods data live |
| **[`research/cmf.md`](research/cmf.md)** | Community Mod Framework: its hooks, Mod Menu settings, the list machinery that fails silently, and how Construction Manager's automation is put together for an addon to reach |
| **[`research/translation.md`](research/translation.md)** | Translating somebody else's mod: what the job is, what it costs, and how a localization breaks without a word |

Two things are worth knowing before opening any of them.

**The game prints its own API.** `-debug_mode`, then `script_docs` and
`dump_data_types` in the console; the dumps are in `reference/game/docs/`. Ask
them rather than inferring from what mods happen to use:

```
python3 tools/api.py set_subsidized       exact name, across every dump
python3 tools/api.py --find subsid        substring, anywhere
python3 tools/api.py --scope building     everything taking that scope
python3 tools/api.py --gui IsAvailable    GUI data functions only
```

That distinction cost real work once: subsidies were written off as
interface-only because nothing in `common/` used `set_subsidized`, and the
engine had it all along. What the dumps do *not* say is how something behaves,
or whether it does anything useful in a given scope. That still comes from
vanilla, from the reference mods, and in the end from a run.

**Versions are not written down here.** The owner refreshes `reference/`
whenever a mod updates; `python3 tools/refs.py` says what is in the tree. What
these notes describe was true of CMF 2.3.x and re-checked against 2.4.1, and
says so where a version matters.

The companion documents are [`PITFALLS.md`](PITFALLS.md) — the same knowledge
from the other end, as mistakes and the symptom each one showed — and
[`TESTLOG.md`](TESTLOG.md), which is what has actually been in the game.

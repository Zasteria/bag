# `glorpui_hints` — brief

The societal value tooltip, with the sources Glorp UI's own generator never
looks at. Glorp UI reads laws, government reforms and estate privileges — 827 of
the game's 1 426 pushes across 23 source types; this mod adds **264 lines from
fourteen more** and gates them by whether the country can actually take them.

**This is the mod the current job is about.** What that job is:
[`../../docs/NEXT_SESSION.md`](../../docs/NEXT_SESSION.md).

## State

**Glorp UI took the translation half upstream.** Their 2026-08-28 build ships
the hints in all eleven languages, with this mod's verb-after-object opener
design. Settled 2026-08-30: **Russian stays here, the other ten go back to
them** — `SHIP_GLORP_HINTS` in `tools/generate.py` is `["russian"]`. The owner
prefers this mod's Russian and does not mind about the rest.

**Unrun, and the next load is the test.** Their new «показать недоступные»
switch shows vanilla's own hint blob; this mod was dropping that blob entry, so
the switch emptied half the tooltip. Their block is spliced in byte for byte
now. **Turn their switch on**: vanilla's blob and this mod's lists should both
appear, and Glorp UI's per-axis lists should be gone — that last part is their
design, not a fault.

**What is only here, and stays here:** the 264 extra lines; the availability
gates (252 lines gated by a country trigger, 175 gated objects); `SVX_REACHABLE`;
holding back the five advance-locked privileges; four repaired Russian keys of
Glorp UI's own interface.

**One gate has never been seen and cannot be by this owner.** The religious
aspect gate — he plays Catholic, where aspects are set by the Papacy, so there
is nothing for it to show either way. It needs a run as a religion that picks
its own aspects.

**Known gap, not yet work:** the added lines are Russian only. An English game
renders the two new blocks as raw keys.

## The open piece of work

**89 of the 429 (axis, policy) pairs the game pushes are in nobody's list** —
21%, including the strongest tier, and they are not scattered: **six law files
are missing whole**, because they are laws belonging to an international
organization or a religion rather than to a country's own law list, which is
what Glorp UI's generator reads. Nothing has been built for them. This is the
biggest thing neither mod shows.

## How it is built

    python3 mods/glorpui_hints/tools/generate.py              the mod (in tools/refresh.py)
    python3 mods/glorpui_hints/tools/generate.py --conflicts  what overlaps Glorp UI
    python3 mods/glorpui_hints/tools/generate.py --game-files reference/game
    python3 mods/glorpui_hints/tools/scan_sources.py reference/game

The last two rebuild the hint lists from the game's `common/` tree. They are
**not** in `tools/refresh.py`: the scan takes a minute and the game files move
far less often than Glorp UI does.

## Three things that fail silently here

- **A `customizable_localization` cannot be overridden** — first definition
  wins, later ones are dropped with `gamedatabase.h: Duplicated key`. So Glorp
  UI's own filter rule is untouchable and the way round it is to take over the
  localization key it prints. That mechanism is the reason the advance gate
  works at all.
- **This mod re-emits Glorp UI's tooltip lists inside its own override.** If
  their list moves and ours does not, the templates still parse, the mod still
  loads, and the player silently gets a stale copy. `generate.py` compares the
  two as an ordered sequence and fails naming the difference — that check is the
  only symptom there will ever be.
- **A gate on a trigger that does not exist never fires and never logs.** 492
  religious aspect lines were gated on `country_religion`, which is nothing
  anywhere; they simply never appeared. `generate.py` now checks every trigger
  name in the gates against the engine dump and the game's scripted triggers.

Depth: [`README.md`](README.md). The other addon that looks like this one, and
why it is not: [`../../docs/archive/glorpui_small_fix.md`](../../docs/archive/glorpui_small_fix.md).

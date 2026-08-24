# Next session: read this first

This repository holds five mods, four documents and a pile of history. Almost
none of it is what the next session is for. This file says what is.

## The one job

**Make Europa Universalis V stay playable for longer than an hour.**

The owner's own description: the first hour is comfortable, the next two get
quietly worse, and by the third or fourth the game is a slideshow — slow ticks,
freezes, the lot. Reloading fixes it. He wants that first hour to last four.

Everything below serves that. If a task does not, it is not this session's.

## What is already known — do not measure it again

The full table is at the top of [`HANDOFF.md`](HANDOFF.md#settled--do-not-measure-any-of-this-again).
The short version:

- the game leaks GUI widgets and never frees them while a session runs — 364 at
  the main menu, ~37 000 in game, **294 013 after an hour**, which is more than
  ten copies of the entire interface;
- **idling costs exactly zero.** Every widget comes from something the player did;
- it is **not** map icons, unit markers, or the passage of time;
- it is **not** one bad window — diplomacy, map modes and location panels all
  leak, at 1.86, 1.49 and 0.29 widgets a frame;
- it is **not** the mod set. Vanilla leaks slightly faster;
- **no mod can free a widget** — the engine exposes no such call;
- **there is no widget limit to raise** — `NGUI` in the defines has no pool, cache
  or arena.

Five evenings of the owner's time went into those. Asking for any of it again is
the worst thing this session can do.

## The live hypothesis

**Hover.** Every brush of the cursor builds a tooltip, and the defines say it is
built with **zero delay** (`NTooltip.OPEN_DELAYED_TIME = 0.0f` in
`reference/game/loading_screen/common/defines/jomini/00_tooltips.txt`). That fits
every observation, including the zero when idle.

If it holds, the fix is a one-file mod overriding that define — and the game's
own **Settings → Tooltip Settings → Show Delay** probably drives the same value,
so the setting tests the mod before it is written.

## What to do, in order

1. **Ask whether the run happened.** The protocol is written out in
   [`HANDOFF.md`](HANDOFF.md#the-run-that-decides-it): paused, two minutes of
   mouse-sweeping with no clicks, tooltip settings changed, the same two minutes
   again, then `performance_degradation.log`. Every branch of the result already
   has its next step written down there. **Do not design a different test until
   that one has been run.**
2. **Read the numbers the same way as before.** One sampler row is 3 601 frames.
   Only compare intervals whose in-game date matches the row before them — those
   were recorded paused, and are the clean ones.
3. **If hover is confirmed**, write the defines mod. It is small: one file at
   `common/defines/jomini/00_tooltips.txt` inside a mod, with the whole `NTooltip`
   block copied and `OPEN_DELAYED_TIME` raised. Then measure again.
4. **If it is not**, the fallback route is `UI Editor` in `debug_mode` — the live
   widget tree, and the only tool that can name what accumulates. The toolbox
   contents are in [`research/engine.md`](research/engine.md#the-debug-toolbox).

## Riding along, no extra work

`ru_loc_fix` round two — eleven keys and four expansions — has never been in
game. It needs no protocol: any run tests it. After any log arrives, check that
`error.log` no longer carries `RGO_BUILD_GOODS_PRICE_IMPACT_ON_COST`,
`FILTER_BY_GOODS`, `MARKET_SURPLYS_INFO`, `ALERT_HAS_UNMARRIED_CHILDREN`,
`THIRD_DESTROY_BUILDING_EFFECT` or `DESTROY_BUILDING_EFFECT`, and write the
result into [`TESTLOG.md`](TESTLOG.md).

## How to work here

- The owner cannot be asked to run the same thing twice. Before requesting a run,
  walk the protocol as the person who has to do it — *"sit on the map and open
  nothing"* is impossible while events fire, which is why everything is paused now.
- "It is a base-game defect, report it to Paradox" is **not** an acceptable
  answer. He knew that before the first test. The job is a lever from the mod
  side, or evidence with numbers that none exists.
- Everything else about working in this repository is in
  [`../CLAUDE.md`](../CLAUDE.md) and [`RESEARCH.md`](RESEARCH.md). The mods other
  than `ru_loc_fix` are not this session's business unless the owner says so.

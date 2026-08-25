# Next session: read this first

This repository holds six mods, six documents and a pile of history. Almost
none of it is what the next session is for. This file says what is.

## This session: get `glorpui_hints` into the workshop

The mod is **finished as a piece of software** and unfinished as a *published*
one. On 2026-08-27 it went from Russian to **eleven languages**, took the two
things worth taking from the rival addon, and grew the tooling to publish it.
None of that has been in game. So this session is two things and they are in
this order:

### 1. What the 2026-08-27 screenshots already settled

Do not ask for these again — they are in [`TESTLOG.md`](TESTLOG.md):

- **the category as a game concept renders**, in Russian and English, as an
  encyclopedia link. That was the whole risk of the rewrite and it is closed;
- **English works** — the block titles, the openers, all of it;
- **the launcher has no upload button**, so the route is PDX Workshop Manager;
- **a building's `allow` was being copied into country scope** and the engine
  said so in one line of `error.log`. Fixed, and `check_gate_scopes` now catches
  the whole class;
- **`ru_loc_fix` round two is confirmed** from the same logs.

**The player switches language from the console on the fly.** That makes
checking another language nearly free — but a hot switch does not re-resolve
*vanilla* strings, only the mod's, so a real check of one wants a restart.

### 2. What is still unrun on `glorpui_hints`

Cheap, and none of it needs a protocol:

- **the five advance-gated privileges.** Playing anyone but England, Morocco or
  the Ottomans, `Yeomanry` / `Jaysh Armies` / `Ghazi` / `Ayans` must not be
  offered. `error.log` must not carry `svx_unlock_`;
- **the building `allow` repair** — `error.log` must not carry
  `Inconsistent trigger scopes` any more;
- **nine of the eleven languages**, which is a console switch each;
- **the four repaired Glorp UI keys.** The player could not find those map
  modes and does not care about them; if they are still not visible next time,
  **offer to drop them** — they are another mod's interface and the only thing
  in here outside this mod's stated scope.

### 3. Publish it

Everything is ready and `python3 tools/publish.py glorpui_hints` says `ok`.

1. merge the branch, then `mods.bat → 4` with the `git pull`;
2. load once and check §2 above;
3. `mods.bat → 5 → «к» + номер` writes `manager-config.json` beside the game's
   mod folder — app id, thumbnail path and mod directory already right;
4. run [PDX Workshop Manager](https://github.com/kaiser-chris/pdx-workshop-manager)
   (GUI build, Steam running and logged in), point it at that config;
5. on the workshop page, by hand: **Glorp UI** and **Community Mod Framework**
   as Required Items, and **hidden first**.

The whole thing, with what is verified and what is not, is
[`WORKSHOP.md`](WORKSHOP.md).

### What was done on 2026-08-27, so it is not re-derived

- **Eleven languages for about fifty strings each.** Everything a player reads
  is in `mods/glorpui_hints/tools/languages.py`; the generators hold no words.
  The reasoning is in
  [`research/translation.md`](research/translation.md#shipping-in-all-eleven-languages)
  and the mod's own [README](../mods/glorpui_hints/README.md).
- **Category nouns are game concepts, not translations.** Free in ten extra
  languages and more accurate than the Russian it replaced.
- **A `customizable_localization` cannot be overridden** — first definition
  wins, later duplicates dropped. In [`PITFALLS.md`](PITFALLS.md#localization);
  it is what the advance gates are built on.
- **The workshop tag vocabulary is fixed and four of our mods were outside it.**
  Also in [`PITFALLS.md`](PITFALLS.md#publishing).

### What is deliberately not done

- **A thumbnail for the other five mods.** Only `glorpui_hints` has one, and it
  is the workshop page's picture as well as the launcher's icon.
  `mods/glorpui_hints/tools/make_thumbnail.py` draws one when a second mod is
  ready to go out.
- **Reviewing the ten new translations with somebody who speaks them.** They are
  written against the game's own terminology where a concept exists and are
  otherwise a careful translation of the Russian. Nobody has read them. A
  correction goes in `languages.py`, never in a generated `.yml`.

## Where everything else stands, 2026-08-26

- **The mod loop is finished** — see the section further down, and do not
  rebuild it.
- **`reference/playset/` holds the other 17 mods** he runs, text only, and
  `tools/guicost.py` counts them. What that census found is in
  [HANDOFF](HANDOFF.md#what-the-playset-turned-out-to-hold).
- **Every generator is green** against the current reference tree; the
  translations were brought up to Advanced Auto Build 0.9.3 and National
  Destinies 1.3.8 on 2026-08-25.
- **`nd_ru` covering a tenth of National Destinies is deliberate** — the settled
  table in [HANDOFF](HANDOFF.md#settled--do-not-measure-any-of-this-again) says
  why. Do not raise it.
- The performance hunt below is the owner's standing job and has not moved; it
  waits on a run he has not been asked for yet.

## The standing job: make the game playable for longer than an hour

This is the owner's big one, and it outlives any single session. It is *not*
what he asked for next — the section at the top of this file is — but it is what
everything below serves, and it is where the next run he agrees to should go.

**Make Europa Universalis V stay playable for longer than an hour.**

The owner's own description: the first hour is comfortable, the next two get
quietly worse, and by the third or fourth the game is a slideshow — slow ticks,
freezes, the lot. Reloading fixes it. He wants that first hour to last four.

Everything in the rest of this file serves that.

There are **two faults under that one complaint**, and they are not the same
fault. The first grows over hours and a reload clears it — that is the widget
leak, and it is the base game's. The second is there in the first minute, on a
freshly loaded save, and it is the playset's. Keep them apart: a measurement of
one says nothing about the other.

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

## The second job, added 2026-08-25

**Panels open with a hitch under the playset and instantly in vanilla — on a save
loaded a minute ago.** That is a *different* fault from the one above: this one
does not grow, does not need three hours, and reloading does not clear it. Do not
merge the two in your head.

It has been counted from the files, with no run spent — the section is
[The second slowdown](HANDOFF.md#the-second-slowdown--panels-open-slower-with-mods-from-the-first-minute)
and the tools are `python3 tools/guicost.py` and `python3 tools/playset.py`.

**Know the size of what you can say.** The owner runs **22 workshop mods**;
`reference/` has five. `playset.py` reads the mount table out of his `debug.log`
and reports that **17 of the 22 mount `in_game`** — the only mount that can add a
widget — and that at most 14 of those have never been looked at. Any sentence of
the form "the playset does X" is a sentence about a quarter of the surface.
**He does not run Advanced Auto Build**, whatever the 2026-08-24 log's mount of
`3781437488` says; the first version of this section led with it and was wrong.

What is actually established:

- `GetScriptedGui('x')` in a `.gui` is a script trigger run from the interface.
  Vanilla uses it **nine times** in 387 files. Of what is in `reference/` and
  still in the playset, **Construction Manager is the heaviest at 344** — 491×
  vanilla's density per widget;
- **static widget counts lie about `datamodel` windows.** `cm_hidden_window`
  declares 23 widgets and binds a datamodel over **every building type**, 465 of
  them, with two more datamodels nested per row — permanently live, at
  `position = { -10000 1 }`, with a comment saying it "keeps descendant
  visibility gates re-evaluating each frame";
- mods add **+42%** filter chips to the `building` tag, four of them ours, and
  ours walk a province per building type;
- **dead already:** Glorp's panels are lighter than vanilla's (0.78×), and no
  mod's Russian localization has a single hard markup fault.

**Ask for the bisect before anything else.** Seventeen mods halve in four or five
loads of a minute each; same save, same three panels (country, diplomacy, a
location's build panel). Try Construction Manager and `rgo_bonus_filter` first in
case they save the bisect. If it lands on nothing, the instrument is
`ScriptProfilerEntry`.

**The whole playset is now in `reference/playset/` and has been counted** — that
step of the old plan is done, and what it found is in
[`HANDOFF.md`](HANDOFF.md#what-the-playset-turned-out-to-hold). Short version:
no playset mod adds a filter chip, three keep small always-live windows, and
the heavy script density is still Construction Manager's. So the declarations
have been read; what has not been read is what those mods *do on tick*, and the
bisect is still the cheapest way to find out which one matters.

## The live hypothesis

**Hover.** Every brush of the cursor builds a tooltip, and the defines say it is
built with **zero delay** (`NTooltip.OPEN_DELAYED_TIME = 0.0f` in
`reference/game/loading_screen/common/defines/jomini/00_tooltips.txt`). That fits
every observation, including the zero when idle.

If it holds, the fix is a one-file mod overriding that define — and the game's
own **Settings → Tooltip Settings → Show Delay** probably drives the same value,
so the setting tests the mod before it is written.

## What to do, in order

0. **Ask for the five-minute bisect** in the section above. It costs almost
   nothing and it can close the second job outright.
1. **Ask whether the hover run happened.** The protocol is written out in
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

## The mod loop is finished — do not rebuild it

`mods.bat` in the repository root (over `tools/mods.ps1`, over `tools/mods.py`)
is the owner's tool for everything about a mod updating:
his whole subscription against the workshop, steamcmd into the game's own
workshop folder, the copies here, **our own mods into
`Documents/Paradox Interactive/Europa Universalis V/mod/`**, moving a mod
between `reference/mods/` and `reference/playset/`, the commit and the push. It was built because he said in
so many words that **nothing about updating his mods may require one of our
sessions** — so do not add a step only a session can do, and do not tell him to
run the pieces by hand when the menu covers it. `tools/workshop.py` is the same
machinery without the menu, and the GitHub check runs daily on its own.

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

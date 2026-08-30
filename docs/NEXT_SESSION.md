# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## The job: `mods.bat` does not install anything

**`glorpui_hints` is finished and confirmed** — the splice passed in game on
2026-08-30 (`TESTLOG.md`). What is left is getting it out, and that is blocked on
the tool, not on the mod.

**What the owner reports, twice over.** `mods.bat` says `ok` and installs
nothing. Two separate failures, both silent:

1. **Workshop mods are never refreshed.** The `workshop/` folder keeps the old
   versions, so the game keeps loading them.
2. **Our own mods are never copied into the game.** He installed
   `glorpui_hints` through the menu twice, was told it worked, and both runs
   loaded a build from days earlier. He has now copied it by hand, which is the
   only reason 2026-08-30 tested the right files.

**What he wants it to be**, in his words: a replacement for updating through
Steam. He picks a mod in a menu; it pulls that mod from `main` and **replaces**
the copy in `Documents/Paradox Interactive/Europa Universalis V/mod/` outright,
old files gone rather than written over. Same for pulling workshop updates down.

`tools/mods.ps1` is the menu and `tools/workshop.py` is the half without one.
Start by finding out what the install step actually does when it prints `ok` —
that it reports success while copying nothing is the first thing to fix, because
it is what cost the two runs. `python3 tools/which_build.py <logs folder>` on the
next logs drop is how the fix gets confirmed.

## Then `glorpui_hints` goes out

Nothing about the mod is outstanding. Riding along on whatever load comes next,
none of it needing a protocol:

- the five advance-gated privileges. Playing anyone but England, Morocco or the
  Ottomans, `Yeomanry` / `Jaysh Armies` / `Ghazi` / `Ayans` must not be offered,
  and `error.log` must not carry `svx_unlock_`;
- `error.log` must no longer carry `Inconsistent trigger scopes` — a building's
  `allow` was being copied into country scope. Clean on 2026-08-30, but on an
  axis Wallachia does not have, so it is still open;
- nine of the eleven languages, which is a console switch each. **A hot switch
  does not re-resolve vanilla strings**, only the mod's, so a real check of one
  wants a restart;
- the four repaired Glorp UI interface keys. The player could not find those map
  modes and does not care about them. **If they are still not visible next time,
  offer to drop them** — they are another mod's interface and the only thing here
  outside this mod's stated scope.

### Then publish

`python3 tools/publish.py glorpui_hints` says `ok` and everything is ready.

1. merge the branch, then `mods.bat → 4` with the `git pull`;
2. load once and check the list above;
3. in game: mods screen → «Выбранные модификации» row → **sandbox icon** → Mod
   Tools → *Create mod*, filled from `metadata.json` (the table is in
   [`WORKSHOP.md`](WORKSHOP.md)) → **Upload New Mod**;
4. check the page is not empty and that `relationships` survived in
   `.metadata/metadata.json` — both are known ways this tool has misbehaved. The
   fallback is [PDX Workshop Manager](https://github.com/kaiser-chris/pdx-workshop-manager),
   and `mods.bat → 5 → «к»` writes its config;
5. on the workshop page, by hand: **Glorp UI** and **Community Mod Framework**
   as Required Items, and **hidden first**.

### Deliberately not done

- **A thumbnail for the other five mods.** Only `glorpui_hints` has one.
  `mods/glorpui_hints/tools/make_thumbnail.py` draws one when a second mod is
  ready to go out.
- **Reviewing the ten new translations with somebody who speaks them.** Nobody
  has read them. A correction goes in `languages.py`, never in a generated
  `.yml`.

## Also waiting on the owner, all of it cheap

- **`mods.bat → 2` on his machine.** The 2026-08-28 files of Advanced Auto Build
  and Glorp UI are still not in this tree; both generators were fixed against
  rewritten copies and the real run is what confirms it. The same run is the
  first real test of the Steam-side rewrite — build ids instead of dates. The
  whole story is [`TESTLOG.md`](TESTLOG.md#2026-08-29--modsbat-an-update-run-on-the-owners-own-machine).
- **The panel-open bisect — five minutes, no log to read.**
  [`investigations/panel_hitch.md`](investigations/panel_hitch.md) has the
  protocol. It can close that job outright.
- **The hover run.** [`investigations/widget_leak.md`](investigations/widget_leak.md)
  has it written out, and every branch of the result already has its next step.
  **Do not design a different test until that one has been run.**

## Before asking him for anything

Read [`SETTLED.md`](SETTLED.md). And walk the protocol as the person who has to
do it: *"sit on the map and open nothing"* is impossible while events fire, which
is why everything is paused now. He cannot be asked to run the same thing twice.

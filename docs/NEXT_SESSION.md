# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## The job: `glorpui_hints` — one load, then the workshop

The mod is finished as software and unfinished as a *published* one. Its brief
is [`../mods/glorpui_hints/CLAUDE.md`](../mods/glorpui_hints/CLAUDE.md).

**Deploy first. The 2026-08-30 run tested the 2026-08-25 build** — the folder
`Documents/.../mod/glorpui_hints/` had never been refreshed, and `gui.log` proved
it (`TESTLOG.md`). So the ask is `mods.bat → 4` **and then** the load, and the
next logs get `python3 tools/which_build.py <logs folder>` before anything else
is read into them.

**The load itself is one thing.** Glorp UI's 2026-08-28 build has a «показать
недоступные» switch that shows vanilla's own hint blob. This mod was dropping
that blob entry, so the switch emptied half the tooltip; their block is spliced
in byte for byte now, and none of it has been in game. **Turn their switch on.**
Expected: vanilla's blob and this mod's own lists both present, Glorp UI's
per-axis lists gone — that last part is their design, not a fault. What he saw
on 2026-08-30 with the switch on — the whole «Дальше продвинуться» block gone —
is precisely the old bug, so it is the symptom to watch disappear.

**Riding along on the same load, none of it needing a protocol:**

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

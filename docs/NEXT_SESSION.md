# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## The job: `mods.bat`, and one run to confirm it

**`glorpui_hints` is finished and confirmed** — the splice passed in game on
2026-08-30 (`TESTLOG.md`). It only passed because the owner installed the build
by hand: `mods.bat` printed `ok` twice and the game went on loading a five-day
-old copy, and workshop mods were never refreshed either.

**Both halves are repaired, and neither has been run on his machine.** That is
the whole of the next job: one pass through the menu, and read what it says.

**Пункт 1, the workshop.** A failed steamcmd run looked exactly like a
successful one — it asked only whether the item's folder existed in steamcmd's
own directory, and it existed from the previous attempt, so an unfinished login
still copied last week's files over the workshop folder. The folder is
fingerprinted before and after now, the exit code is read, the cached copy is
offered for deletion first, and **only a mod whose copy actually changed is
copied onward**; anything else is named on screen.

**Пункт 4, our own mods.** The copy loop was sound; nothing checked that it
landed. The install is **read back off disk** now, a mismatch says so with the
path, and the screen names the branch and commit installed. A `game_mods` path
set once with a typo — the one way this could have installed into a folder the
game never reads — is refused rather than created.

**And `mods.bat check` answers it without the menu**, printing each of our mods
against the game's folder and the repository's branch and commit — the line to
paste before anybody theorises about a mod again.

**What to ask him for:** `mods.bat → 1`, then `→ 4`, then `mods.bat check`, and
the output of all three. If a mod still reads «отличается» after installing, the
message names the folder and that is the next thing to look at. The logs from
whatever run follows go through `python3 tools/which_build.py <logs folder>`
first, as always now.

## `where_to_produce`: urban rights are built, not loaded

The owner copied `common/town_rights` into `reference/` by hand on 2026-08-31,
because `mods.bat → 2` turned out to copy mods and not to re-extract the game.
So the data is here and the arithmetic is settled:
[`investigations/town_rights.md`](investigations/town_rights.md) is the whole
of it, and it is short.

The three findings that decide the build: a right's percentage is the same in
every location and so **re-ranks nothing** — only the bundle of two or three
goods does; adding a bundle's goods needs `default_market_price` from
`common/goods`, or it is books-plus-masonry and the ninth run's mistake again;
and a `+5 levels` right is a quantity where the others are ratios, so it gets
its own number and never a shared one.

**Built 2026-08-31 and never loaded**: the output half — a third list on the
Goods tab and a window of its own. Level rights are deferred by the owner. The
fifteenth-load protocol is in [`TESTLOG.md`](TESTLOG.md#waiting-on-a-run), and
one `grep` for `town_right_efficiency_penalty` is still outstanding: eleven
rights reference it and nothing `reference/` holds defines it.

**And a smaller thing worth fixing while there:** which `mods.bat` entry runs
`tools/extract_game_files.py`. Пункт 2 does not, and the manifest is only worth
something if something runs it — the four folders added for `where_to_produce`
(`goods`, `production_methods`, `building_types`, `town_rights`) are three that
the mod has compiled from since its first commit and that no entry covered.

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
  rewritten copies and the run confirms it. It now also carries the
  four folders added to the manifest for `where_to_produce`, `town_rights` among
  them, and nothing of the urban-rights job can start before it. The same run is the
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

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

## `where_to_produce` wants one extraction run, and only then the town rights

The owner asked for urban rights — the **Городские права** a location can be
granted, which trade a small penalty on all production for a large bonus to one
bundle of goods, and so want a mode that ranks ground for the *bundle* rather
than for one good. Nine general production rights, each naming its bundle in
localization — tools; jewelry; weaponry+firearms+cannons; paper+books+dyes;
leather+pottery+furniture; liquor+beer+wine; cloth+fine cloth; naval
supplies+tar; masonry+glass — plus country-unique ones, of which Flemish Cloth
Industry gives no efficiency at all, only `+5` to a building limit, which is a
different kind of answer and may not belong in the same table.

**The numbers are not in `reference/`.** The engine's side is all there —
`has_town_rights`, `every_town_rights_in_location`, `grant_town_rights`, a
`town_rights_type` target — but `common/town_rights` was never extracted, so
what each right modifies, by how much, and what gates it are unknown here.
Reading the bundles out of localization prose is the mistake this repository has
a rule against.

`town_rights` is in `tools/game_files_manifest.txt` now, so **the `mods.bat → 2`
already waiting below brings it in** — along with `goods`, `production_methods`
and `building_types`, which `where_to_produce` has read all along and which no
manifest entry covered, so an extraction run would have dropped them. After that
the bundles and their percentages generate like everything else; the design
question worth settling first is whether a bundle is a third goods list or a
mode over the two that exist.

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

# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## The job: `where_to_produce`, the plan formula

**Read [`investigations/plan_gaps.md`](investigations/plan_gaps.md) first and
nothing else.** Nine faults, all closed, five runs behind them. Three results to
carry before touching anything:

- **The formula has two regimes.** On 48 locations the quota binds and the bands
  barely matter; on 416 the quota binds nothing and the band is the whole
  allocator. Fault D was closed on the small ground and had to be reopened on the
  large one — **a measurement answers the ground it was taken on**
  (`pitfalls/diagnosis.md`).
- **A scarce good with one building is the RGO discount and not a fault** — his
  own rule, now re-derived three times.
- **Charters use `potential` and never the advance.** The other way was built,
  run, and cost the plan a quarter of its ground.

**Three presses are owed and none has been in the game.** On Westphalia: the
charter ladder now climbs its ceiling one town at a time and runs every band at
each height, so the nine charters should come back **five or six each** instead of
6·7 + 3 + 3. That is the thing he said the plan is worthless without, and the two
runs behind it are the newest in [`TESTLOG.md`](TESTLOG.md). On a large ground:
the relative open ladder, which does not engage at all on 48 locations because
the quota fills them first. And the editor's windows, below.

**The editor is a window of its own now, and none of it has been loaded.** He
refused the first build outright — it was nine settings on the mod's page and
«окно настроек мода - стало засраным и неудобным… я не хочу делать подобные вещи
там». So: `bag_wtp_edit_window.gui`, three save slots, the goods this ground can
make as icons, «−1» and «+1» flanking each one he picks, and
`bag_wtp_changes_window.gui` for «показать изменения». The save buttons are in the
plan window as well, where he asked for them.

**Three GUI files have never been drawn.** That is the whole risk in this build:
script failures name their file and line in `error.log`, and a `.gui` that does
not parse takes its window with it silently. The first load should be «Открыть
план → Редактор», and if the window does not appear the log will say why.

**The mistake the editor replaces is worth carrying**: a hand weight fed back into
a full re-plan, which measured at 42 locations of 48 moved by a knob meant to move
one. A preference is an edit, not a term in the objective. The checklist is the
last section of `plan_gaps.md`.

**Do not spend his run on a guess.** Every fault in that file was found by
counting in his log, not by theorising, and the four-theories rule
(`pitfalls/diagnosis.md`) is what this mod cost him already.

## The job: `mods.bat`, and one run to confirm it

**`glorpui_hints` is finished and confirmed** — the splice passed in game on
2026-08-30 (`TESTLOG.md`). It only passed because the owner installed the build
by hand: `mods.bat` printed `ok` twice and the game went on loading a five-day
-old copy, and workshop mods were never refreshed either.

**Both halves are repaired, and neither has been run on his machine.** That is
the whole of the next job: one pass through the menu, and read what it says.

**Пункт 1, the workshop.** A failed steamcmd run looked exactly like a
successful one — it asked only whether the item's folder existed — so an
unfinished login copied last week's files over the workshop folder. The folder is
fingerprinted before and after now, the exit code read, and **only a mod whose
copy actually changed is copied onward**.

**Пункт 4, our own mods.** The copy loop was sound; nothing checked that it
landed. The install is **read back off disk** now, and the screen names the
branch and commit installed.

**And `mods.bat check` answers it without the menu**, printing each of our mods
against the game's folder and the repository's commit.

**What to ask him for:** `mods.bat → 1`, then `→ 4`, then `mods.bat check`, and
the output of all three. If a mod still reads «отличается» after installing,
the message names the folder. The logs from whatever run follows go
through `python3 tools/which_build.py <logs folder>` first, as always now. No
menu entry runs `tools/extract_game_files.py` yet, and which should is open.

**What is settled about `where_to_produce` and not in `plan_gaps.md`** — the
single-good side's known faults, the scarce-pass optimisation measured and left
unbuilt, and where the diagnosis lives — is in
[`archive/wtp_settled_asides.md`](archive/wtp_settled_asides.md).

## Then `glorpui_hints` goes out

Nothing about the mod is outstanding. Riding along on whatever load comes next,
none of it needing a protocol:

- the five advance-gated privileges. Playing anyone but England, Morocco or the
  Ottomans, `Yeomanry` / `Jaysh Armies` / `Ghazi` / `Ayans` must not be offered,
  and `error.log` must not carry `svx_unlock_`;
- `error.log` must no longer carry `Inconsistent trigger scopes` — a building's
  `allow` was being copied into country scope. Clean on 2026-08-30, but on an
  axis Wallachia does not have, so it is still open;
- nine of the eleven languages, a console switch each. **A hot switch does not
  re-resolve vanilla strings**, only the mod's, so a real check wants a restart;
- the four repaired Glorp UI interface keys. The player could not find those map
  modes and does not care. **If still not visible next time, offer to drop
  them** — another mod's interface, and outside this mod's stated scope.

### Then publish

`python3 tools/publish.py glorpui_hints` says `ok`; everything is ready, and the
five steps — merge, load, Mod Tools, check the page, Required Items by hand —
are in [`WORKSHOP.md`](WORKSHOP.md#putting-glorpui_hints-out-in-order).

### Deliberately not done

A thumbnail for the other five mods — `make_thumbnail.py` draws one when a second
goes out — and reviewing the ten new translations with somebody who speaks them,
where a correction goes in `languages.py` and never in a generated `.yml`.

## Also waiting on the owner, all of it cheap

- **`mods.bat → 2` on his machine.** The 2026-08-28 files of Advanced Auto Build
  and Glorp UI are still not in this tree; both generators were fixed against
  rewritten copies. Entry 2 does **not** re-extract the game.
- **The panel-open bisect — five minutes, no log to read**, protocol in
  [`investigations/panel_hitch.md`](investigations/panel_hitch.md). It can close
  that job outright.
- **The hover run**, written out in
  [`investigations/widget_leak.md`](investigations/widget_leak.md), every branch
  of the result with its next step already. **Do not design a different test
  until it has been run.**

## Before asking him for anything

Read [`SETTLED.md`](SETTLED.md). And walk the protocol as the person who has to
do it: *"sit on the map and open nothing"* is impossible while events fire, which
is why everything is paused now. He cannot be asked to run a thing twice.

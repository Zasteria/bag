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

## `where_to_produce`: it works, and what is left is his to choose

**The plan does what it was meant to, and he has seen it** — «на первый взгляд
работает как надо, города получают права и домики из прав», 2026-09-02. The
symptom that cost four runs is measured, named and fixed: the tick is the rank
now (`SETTLED.md`), the charter spam is gone, and **four fifths of placed
buildings earn a bonus where they stand, capturing 78% of their own recipe's
ceiling on average**. All of it is on `main`.

**Read `TESTLOG.md` before anything.** Four runs of 2026-09-02 are in it and they
carry every number this section summarises.

**Three things he named on 2026-09-02 are built and none has been in the game.
One big ground tests all three at once**, and northern Germany — 416 locations,
1312 rooms — is the one that failed before:

- **The round guard is 50 and the pass count is twelve.** 127 locations already
  put the open pass at 11 of 12, and 970 buildings over 32 goods cannot be done
  in fewer than thirty sweeps. What to read on the run: `WTP P<n> sweeps=x/50` in
  the report — a pass at 50 is still being cut off — and whether the rooms come
  out full. **What to watch against it is the hitch** he reported without
  complaint on that ground: twelve passes are fewer than thirty-three, but each
  may now run four times as long.
- **The plan window pages.** `PLAN_ROWS` is still 150 because the datamodel is
  what costs; `PLAN_RANKED` (1500) is how many rows the pass keeps, and «Назад» /
  «Вперёд» under the summary walk them. The summary says «в строках N» beside the location
  count, so the two numbers can be told apart at a glance. If the ground is bigger
  than 1500 used locations the bar says so by the two disagreeing.
- **The province ceiling is gone** — setting, alias, default, both localizations
  and its gate in the allocator.

**What is open, and none of it is a bug:**

- **Nine goods take 45% of the ground.** Coal, sand, beer, cloth, glass, jewelry,
  leather, masonry, pottery — makeable in every location, so each reaches the
  quota and stops at 20. Sixteen town-only goods got 7 or fewer, competing for
  22 towns × 4 slots that the rights have first call on. **The formula working as
  written.** The lever he had for it was `plan_max`, and it went with the province
  ceiling at his word; if he wants one back it should be derived, not typed.
- **The single-good side** has faults he has seen and set aside without naming.

**The diagnosis comes out when the work does.** It is `bag_wtp_diag*`, the `_f*`
counters, the two `_pass*` counters and two buttons; `pitfalls/diagnosis.md` has
what it prints and how to read it, and `tools/diag.py` draws the conclusions so
he does not have to.

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

# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## The job: `where_to_produce`, the plan formula

**2026-09-03, the owner's own framing:** «Основная задача будет полностью
проанализировать весь мод и решить, насколько он точен и оптимизирован, почему он
работает одновременно и так хорошо и одновременно из него выпадают очевидные
вещи, которые делают так плохо. У меня столько планов на этот мод, а я всё вожусь
с этой формулой который день.»

**He then handed the whole thing over, 2026-09-03:** «Я даю тебе полную свободу
действий… перебери весь мод и сделай как должно быть на твой взгляд, а не мои
субъективные запросы.» That session is done and the answer is in the tree.

**Read [`investigations/plan_gaps.md`](investigations/plan_gaps.md) first and
nothing else.** Eight faults, all closed, four runs behind them. Three results to
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

**One press is owed, on a large ground.** Nothing built after the second run of
2026-09-03 has been in the game: the relative open ladder, the round guard at 150,
the hand regulator, and the plan's own «изменено: убрано X добавлено Y». The
checklist is the last section of `plan_gaps.md`.

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

## `where_to_produce`: what is settled and not in `plan_gaps.md`

**The plan does what it was meant to and he has seen it** — «города получают
права и домики из прав». The tick is the rank (`SETTLED.md`), the window pages,
and the province ceiling and `plan_max` are gone at his word.
**The single-good side** has faults he has seen and set aside without naming.

**Two optimisations are measured and deliberately not built.** The 25 scarce
passes cost 25 sweeps of 61 and place three buildings — a pass no good qualifies
for could be skipped by 47 comparisons rather than a whole sweep. And the plan's
own diff walk is 47 list reads a location. Neither has a complaint against it, so
both are numbers written down rather than changes.

**The diagnosis comes out when the work does.** `pitfalls/diagnosis.md` has what
it prints; `tools/diag.py` draws the conclusions so he does not have to.

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

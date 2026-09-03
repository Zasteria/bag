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
nothing else.** Eight faults now, all closed: A, E and F confirmed by his runs; C
answered by the game's own tooltip and D by a measurement the report was already
printing, neither needing a run; B, G and H fixed and **never once in the game**.

**One run is owed and it closes those three at once.** Вестфалия / Мюнстер, all
48 locations ticked to towns — once «на конец» and once «сейчас», because the
charter age gate is what «сейчас» now behaves differently under. What each press
has to show is the last section of `plan_gaps.md`. **Nothing else is worth asking
him for until that comes back**: every remaining question about the plan is a
question about numbers this run produces.

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

**The plan does what it was meant to and he has seen it** — «на первый взгляд
работает как надо, города получают права и домики из прав», 2026-09-02. The tick
is the rank (`SETTLED.md`), the charter spam is gone, the window pages, and the
province ceiling and `plan_max` are removed at his word. The 2026-09-02 detail is
in [`archive/testlog_wtp_plan.md`](archive/testlog_wtp_plan.md).

**The single-good side** has faults he has seen and set aside without naming.

**And the dead weight is out**: `_pp<n>` (a province walk on every placement, for
a divisor removed a day earlier), 47 `_ordmax<n>` values and 228 `_reach_<n>`
triggers reading `always = yes`. If the plan is measurably faster on the next run,
that is where it came from.

**The diagnosis comes out when the work does.** `bag_wtp_diag*`, the `_f*` and
`_pass*` counters, two buttons; `pitfalls/diagnosis.md` has what it prints, and
`tools/diag.py` draws the conclusions so he does not have to.

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

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

## `where_to_produce`: rolled back, and the probe is the whole of the job

**The tree is back at the build of the thirty-eighth load** — the four tests he
called «большой рывок», where the spread of goods over a whole ground first
looked to him as he had meant it. He named it himself on 2026-09-02: «именно в
этом коммите я хочу начать постройку диагностического инструмента». Everything
above it is out, and the branch
`claude/glass-sand-cycle-diagnosis-0qhgzw`, which carried the funnel probe, was
never merged and is not to be. **What is open at this build and what those later
runs settled are both in the last section of**
[`investigations/plan_formula.md`](investigations/plan_formula.md) — read it
before touching the plan.

**The instrument is built; the job is one run and reading it.** «Диагностика» on
the «Расчёт» tab writes everything the mod knows into `debug.log` in one press,
and `mods.bat → 8` puts it in his clipboard. **The protocol, and what every
branch of the answer means, are in `TESTLOG.md`, written down before the run** —
read them there rather than theorising again: four of his runs went on four
theories and none on a measurement
([`pitfalls/diagnosis.md`](pitfalls/diagnosis.md) has the episode and what the
dump prints).

**The symptom it is aimed at:** the plan will not put glass in a town and puts it
in villages freely, and both recipes carry the identical `location_potential`, so
the market gate is not what stops it. The `G` line for glass answers it — `r = 0`
is a full ground, `g = 0` the one-per-type rule, `p = 0` with `g > 0` ours.

**Do not propose a cause before that report is read**, and add no second
counter: he asked for none until the mod works, and this one comes out with the
fault it finds.

**Three things he measured himself are open again**, because the fixes for them
sat above the rollback and went out with it: a big ground does not finish (the
round guard at 12 against the thirty sweeps the arithmetic needs), the province
ceiling setting he asked to have removed, and «показано 150 локаций», which is
the window's row cap and not the count. **They can be ported back on their own
the moment he asks** — none of them is a theory about the symptom.

**Live besides:** the single-good side has faults he has already seen and set
aside — he did not name them, so ask before guessing; and the hand weight, the
food location and the caps at 3/4/5 are all his, in `plan_formula.md`'s own
closing list.

**What is left besides is decisions, not runs**, and they are written up in
[`investigations/town_rights.md`](investigations/town_rights.md):

- **Level rights**, deferred 2026-08-31: a quantity where the output rights are
  a ratio, so they want their own number and table.
- **Whether the buildable tick should ask about ownership** — that means asking
  the country from a trigger that has none.
- **`town_right_efficiency_penalty`**, in eleven rights and in no file
  `reference/` holds: one `grep` on the owner's install.


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

- **A thumbnail for the other five mods.**
  `mods/glorpui_hints/tools/make_thumbnail.py` draws one when a second goes out.
- **Reviewing the ten new translations with somebody who speaks them.** A
  correction goes in `languages.py`, never in a generated `.yml`.

## Also waiting on the owner, all of it cheap

- **`mods.bat → 2` on his machine.** The 2026-08-28 files of Advanced Auto Build
  and Glorp UI are still not in this tree; both generators were fixed against
  rewritten copies and the run confirms it. Entry 2 does **not** re-extract the
  game.
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

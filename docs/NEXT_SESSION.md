# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## The job: `where_to_produce`, the plan editor

**Read [`investigations/plan_gaps.md`](investigations/plan_gaps.md) first and
nothing else.** The plan itself is finished and confirmed in game; the editor is
what is live.

### Where it stands, 2026-09-04

**The plan works and he has seen it.** 192 buildings in 192 rooms on Westphalia,
charters 5–6 each, goods 3–6 each. Nothing about the plan is owed except the
relative open ladder, which does not engage on 48 locations and wants a large
ground.

**The editor works, end to end, confirmed 2026-09-04.** A press changes the
plan. That was the one thing it existed for and it took five silent faults to
get there.

**What the same report opened: «+1» and «−1» are not each other's undo.** «+1» X
displaces Y; «−1» X gives the room to Z. Both steps are correct on their own —
the walks ask opposite questions and pick different locations — but the round
trip leaves Y one down and Z one up, invisibly. **The editor has no undo at all;
loading a slot is the only one.** The reasoning is in `TESTLOG.md`; what to do
about it is the open design question.

### Five silent faults, and all five are written down

Nothing in any log for any of them, and **the table that names them is
[`pitfalls/interface.md`](pitfalls/interface.md)** — it is not repeated here.
The lesson that outlives them: **instrument before the third theory**
(`pitfalls/diagnosis.md`). The last fault was named by the first report that
carried the editor's numbers, not by the fourth guess.

### What was agreed about the editor, and what is still open

**[`investigations/wtp_editor_design.md`](investigations/wtp_editor_design.md),
2026-09-04.** The whole of it is there and is not restated here. In one line
each: the refill after «−1» goes by shortfall against the fair share rather
than by gain; «+1» and «−1» are independent tools and no undo is wanted; a
target count per good is rejected; the press must say what it did; the editor's
window widens and its frame stops sliding; provinces fold; charters get their
bundle edit; and new ground is fitted to a finished plan without disturbing it.

**Three questions are open in that file and none of them is a session's to
settle alone** — the location panel against `construct_building`, the order
within a shortfall, and whether «+1» should prefer a victim above its share.

### Answered elsewhere, not here

**Why «выгода от места» fell from 80–95% to 64%** is a row in
[`SETTLED.md`](SETTLED.md) — a bigger ground raising it is a prediction, and one
northern-Germany run settles it. **Why a preference is an edit and never a term
in the objective** is [`investigations/plan_formula.md`](investigations/plan_formula.md).

**Do not spend his run on a guess.** Every fault above was found by counting in
his log or his report, and the four-theories rule (`pitfalls/diagnosis.md`) is
what this mod has already cost him.

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

Nothing about the mod is outstanding; four things ride along on whatever load
comes next, and publishing is five steps in
[`WORKSHOP.md`](WORKSHOP.md#putting-glorpui_hints-out-in-order). Both lists, and
what is deliberately not done, are in
[`archive/next_glorpui_publish.md`](archive/next_glorpui_publish.md).

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

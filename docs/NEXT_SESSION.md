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

Nothing in any log for any of them. **The table is in
[`pitfalls/interface.md`](pitfalls/interface.md)** — a `flowcontainer` with a
`datamodel` (four crashes), a `fixedgridbox` that overlapped its cells, a build
nobody ran treated as a baseline, a global surviving a save and lying about the
present, and `_edit_good` read on the wrong scope. Two are checkers now.

**The last was named by the first report that carried the editor's numbers**, not
by the fourth guess, and that is worth more than the fix: **instrument before the
third theory** (`pitfalls/diagnosis.md`).

### What the next press has to show

One press of «+1» on any good with room, then «Показать изменения». **A row with
both `ушло:` and `встало:`.** If it misses, «Диагностика» → the `EDIT` lines say
which stage failed, and no theorising is needed or wanted.

### What he asked for and is owed, in his order

1. **«+1»/«−1» for urban rights, and eviction of a whole bundle.** «Я бы
   предпочёл не забирать домики по частям у городских прав. Я бы скорее предпочёл
   забирать у города целиком всю связку право+его домики.» The charter lock is
   back meanwhile, so a town keeps the buildings its charter is for.
2. **The two plan windows should fold by province.** 48 locations in a flat list
   is noise; the single-good search already folds and is the model to copy.
3. **A good may take a charter's slot, last of all** — his idea, unevaluated:
   only where the charter's own good earns nothing from that ground, and the
   claimant earns more than the 5% a broken bundle costs.
4. **The editor should share nothing with the plan but load and save.** Largely
   done — it places through `_edit_place_*` and asks `_edit_fits_*` — but the
   scan, the walk and the counters still live in `bag_wtp_generated_editor.txt`
   beside the plan's, and `_plan_rank`/`_plan_show` are called after every press.

### Answered but not measured

**Why «выгода от места» fell from 80–95% to 64%**: different questions. The old
number ranked locations for **one** good, where the top rows are fed by
definition; the plan places **35**, and Westphalia has RGOs for eleven, so 24
goods have `rgo=0` and nothing here feeds their recipes. **A bigger ground should
raise it — a prediction, not a measurement**, and one northern-Germany run
settles it.

**And the mistake the editor replaces**: a hand weight fed into a re-plan moved
42 locations of 48 with a knob meant to move one. **A preference is an edit, not
a term in the objective.**

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

# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## The job: `where_to_produce`, the plan editor

**Read [`investigations/plan_gaps.md`](investigations/plan_gaps.md) first and
nothing else.** The plan itself is finished and confirmed in game; the editor is
what is live.

### Where it stands, 2026-09-06

**The plan works and he has seen it.** 192 buildings in 192 rooms on Westphalia,
charters 5–6 each, goods 3–6 each. Nothing about the plan is owed except the
relative open ladder, which does not engage on 48 locations and wants a large
ground.

**The editor works, end to end, confirmed 2026-09-04.** A press changes the
plan, which is the one thing it existed for.

**And «+1» and «−1» are not each other's undo** — «+1» X displaces Y, «−1» X
gives the room to Z, both correct alone and the round trip leaves two other
goods moved. **The editor has no undo but loading a slot.** Reasoning in
`TESTLOG.md`; what to do about it is the open design question.

### The plan for the practical sessions

**[`investigations/wtp_practice_plan.md`](investigations/wtp_practice_plan.md)
is the order, the files and what to ask him for.** Do not re-derive it. The
rules each step implements are
[`investigations/wtp_editor_design.md`](investigations/wtp_editor_design.md).

0. **`tools/code.py`** — done 2026-09-04, no run needed.
1. **The editor's window: the press line, the width, the frame** — **done and
   confirmed 2026-09-05.**
2. **Share, `_lock<n>`, and the «не нужен» flag** — **done and confirmed
   2026-09-06**, with one change reverted: **pins, flags, the share and the star
   belong to the editor window alone, and a fresh plan reads none of them.**
2а. **Reshuffle the buildings a fill placed** — **confirmed 2026-09-06**:
   `shuffle rounds=68 swaps=19 gain=1971`, then `rounds=18 swaps=0 gain=0` on the
   next run. The pass is alive and traded nothing, and **no cause is named** —
   four counters were added instead (`pairs`, `same`, `nofit`, `worse`) so one
   run says which. One fix fell out of it: a removal did not ask town or village
   and charged the wrong side's gain.
2в. **Rebuild the mod's menu** — **closed 2026-09-06**, three rounds and all
   three confirmed on screen. **What it taught outlives the menu**: a box given
   more room than its children need divides the difference between them, an
   `hbox` will not hold a written width, and two different things must not share
   one column — [`pitfalls/interface.md`](pitfalls/interface.md); the move
   itself, [`investigations/wtp_menu_rebuild.md`](investigations/wtp_menu_rebuild.md).
2д. **The editor's share counts the RGOs now** — his catch, 2026-09-06, and the
   code agreed at once: the plan subtracts `_nrgo<n>` from every good's share and
   the editor's fill compared them all against one flat number. `_eq<n> = max(1,
   _edit_quota − _nrgo<n>)`, read by the fill and by step 3 alike; **confirmed in
   the diagnosis**, `G2 coal … rgo=3 eq=2` against `quota=5`.
3. **Even eviction on «+1»** — **confirmed 2026-09-06**: `EDIT scan fitn=23
   cands=9 strict=1`, so the share chose the victim. **One change on top, never
   run:** the victim is now the good furthest *above* its share, with the
   cheapest building only breaking ties — «cheapest» does not change as a good
   shrinks, so the same good was evicted press after press.
3а. **The press journal, because a diff cannot hold chronology.** His blocker,
   2026-09-06: the changes window merges two presses on one location and loses
   the order. The mod writes `WTP PRESS …` into `debug.log` at press time and
   `tools/diag.py` renders «Журнал нажатий»; why that shape, in
   [`pitfalls/diagnosis.md`](pitfalls/diagnosis.md).
4. **Provinces fold in the two plan windows.**
5. **Charters: «+1»/«−1» and whole-bundle eviction.**
6. **New ground fitted to a finished plan.**
7. **The plan shown in the location panel**, inside Glorp UI's interface.
8. **The plan stamped onto Construction Manager**, gated on CM being present.

### Waiting on him, cheap

**Two mods for `reference/`, which he offered**: `cheatmenu` (a catalogue of
effects *in use*, and a large interface with live `fixedgridbox` datamodels) and
Advanced Auto Build's interface. Why, in [`CONVENTIONS.md`](CONVENTIONS.md).

### Two lessons that outlive the faults

**Instrument before the third theory**, and **state the player cannot see or
clear is the mod's fault** — both in [`pitfalls/diagnosis.md`](pitfalls/diagnosis.md).
The five silent GUI faults are named in
[`pitfalls/interface.md`](pitfalls/interface.md).

### Answered elsewhere, not here

**Why «выгода от места» fell from 80–95% to 64%** is a row in
[`SETTLED.md`](SETTLED.md) — a bigger ground raising it is a prediction, and one
northern-Germany run settles it. **Why a preference is an edit and never a term
in the objective** is [`investigations/plan_formula.md`](investigations/plan_formula.md).

**Do not spend his run on a guess.** Every fault above was found by counting in
his log or his report, and the four-theories rule (`pitfalls/diagnosis.md`) is
what this mod has already cost him.

## The job: `mods.bat`, and one run to confirm it

**Both halves are repaired and neither has been run on his machine.** A failed
steamcmd run looked exactly like a successful one, and our own install was never
read back off disk; both are fixed, fingerprinted and reported now. The whole
diagnosis is in
[`archive/mods_bat_repair.md`](archive/mods_bat_repair.md).

**What to ask him for:** `mods.bat → 1`, then `→ 4`, then `mods.bat check`, and
the output of all three. Logs from whatever run follows go through
`python3 tools/which_build.py <logs folder>` first, as always now.

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

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
1, 2, 2а, 2в, 2д. **The window, the share, the reshuffle, the menu and the
   RGOs** — **all closed and confirmed in game, 2026-09-05 and 2026-09-06.**
   What survives them in the code: **pins, flags, the share and the star belong
   to the editor window alone, and a fresh plan reads none of them**; the
   editor's share subtracts the RGOs exactly as the plan's does; the buildings a
   fill placed trade locations between themselves while a trade is worth
   anything. **What the menu taught outlives the menu**: a box given more room
   than its children need divides the difference between them, an `hbox` will not
   hold a written width, and two different things must not share one column —
   [`pitfalls/interface.md`](pitfalls/interface.md).
3. **Even eviction on «+1»** — **closed 2026-09-06**: ten «+1» on one good
   evicted ten *different* goods, each the most bloated. The victim is the good
   furthest above its share, cheapest building only breaking ties.
3а. **The press journal** — **confirmed 2026-09-06.** A diff cannot hold
   chronology, so the mod writes `WTP PRESS …` into `debug.log` at press time and
   `tools/diag.py` renders «Журнал нажатий».
4. **Provinces fold in the two plan windows** — **confirmed 2026-09-06**, with
   three fixes after it: provinces sort inside their areas (a walk inside a walk,
   never a packed `order_by`), the fold is on by default, and
   the extra `widget` between `window` and `vbox` came out of all five windows —
   the header had never stretched, he had said so three times, and the shape is
   copied from `ai_settings_menu.gui` rather than guessed at. **Charter cells are
   written per *place*, not per charter** (`_rslot<p>`), so an unavailable charter
   leaves no hole.
5. **Charters in the editor** — **closed 2026-09-06.** A charter is not a
   building: every town holds exactly one, so a press is a *move*, bundle and
   all, and a town never ends without one. **Two faults found by his runs, both
   from reusing the plan's own machinery**: the candidate test wanted a free room,
   so nothing moved at all; and `_edit_place_town_<n>` refuses on a full town, so
   a bigger bundle lost a building silently. Room is made *before* the bundle is
   planted now ([`PITFALLS.md`](PITFALLS.md)). **The changes window is shelved at
   his own word**; do not touch it until he asks.
6. **New ground fitted to a finished plan.**
7. **The plan shown in the location panel**, inside Glorp UI's interface.
8. **The plan stamped onto Construction Manager**, gated on CM being present.

### Two things he asked for and has not seen

**A frame that fits, and rows that fit in it.** The «header» complaint was the
content overflowing the frame all along — measured at last on 2026-09-06, 1544 in
a 1500 box — and the check that should have caught it was subtracting the margin
the wrong way. Both fixed, neither run.

**The plan rows carry building icons only** now, and the space the goods icons
held is what he wants for the Construction Manager links of step 8.

### Waiting on him, cheap

**Two mods for `reference/`, which he offered**: `cheatmenu` and Advanced Auto
Build's interface. Why, in [`CONVENTIONS.md`](CONVENTIONS.md).

### Two lessons that outlive the faults

**Instrument before the third theory**, and **state the player cannot see or
clear is the mod's fault** — [`pitfalls/diagnosis.md`](pitfalls/diagnosis.md).

### Answered elsewhere, not here

**Why «выгода от места» fell to 64%** is a row in [`SETTLED.md`](SETTLED.md).
**Why a preference is an edit and never a term in the objective** is
[`investigations/plan_formula.md`](investigations/plan_formula.md).

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

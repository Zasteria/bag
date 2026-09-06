# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## The job: `where_to_produce`, step 6 is built and owes one run

**Read [`investigations/wtp_practice_plan.md`](investigations/wtp_practice_plan.md)
for the order and what each step cost, and
[`investigations/wtp_editor_design.md`](investigations/wtp_editor_design.md) for
the rules it implements. `_plan_*` itself is
[`investigations/plan_gaps.md`](investigations/plan_gaps.md). Nothing else.**

### Steps 0–5 are closed, and every one of them was seen in the game

The window, the share, the reshuffle, the menu, the RGOs, even eviction on «+1»,
the press journal, provinces folded inside their areas, and charters that move
rather than multiply — all confirmed by his runs of 2026-09-05 and 2026-09-06.
**Three things outlive them:**

- **The editor's state is the editor's.** A pin, a «не нужен», the share and the
  star are read by `_edit_*` alone, and a fresh plan reads none of them.
- **Windows have their own checklist** —
  [`pitfalls/windows.md`](pitfalls/windows.md), read **before** touching any
  `.gui`. Six builds went into one frame; `check_script.py` now enforces three
  of its rules.
- **The changes window is shelved at his own word** — «правок требует много,
  функциональности несёт мало». Do not touch it until he asks.

### Step 6 — «Расширить» — is closed, confirmed twice in the game

Two runs, `сдвинулось на старой земле = 0` both times and corroborated by a
second counter; a pin lifted when the share outgrew it. Written up in
[`TESTLOG.md`](TESTLOG.md); how it is wired is one table in the practice plan.

**Still never run:** the fold-by-default (only a **new game** shows it) and any
large ground since the ladders were rebuilt — northern Germany's 233 locations;
Westphalia's 48 does not test it, and the extension re-scores and re-ranks, so it
carries the same open question.

### The live question: what is being made even — buildings or output

**Measured now, not estimated.** The `out=` probe ran: buildings 1…24, output
3.5…99.5, a town building worth 10–13.7 against a village building's 0.84–3.7.
Masonry with 20 buildings makes 27.5; cannon with 6 makes 80. **His instinct was
right and the answer to «как находить это число» is that it is never chosen** —
the share is a turn-taking rule, not a goal, and the ladder already discovers the
level where the ground runs out. Change the currency, not the machine:
**evenness decides who picks next (by output), the RGO gain decides where** —
which is the split the allocator already has. Full derivation and the measured
cost in [`investigations/plan_share_sides.md`](investigations/plan_share_sides.md).

**Not built, and deliberately.** Evening by output buys evenness with bonus, and
by how much is unknown — so it belongs behind a switch, two presses of
«Пересчитать» on one ground and both `GAIN` lines side by side. **Ask him before
building it.**

### Then 7 and 8, in that order, and not before

**His order, 2026-09-04: «доработать все начатые функции мода и потом уже
пытаться интегрировать его в функционал CM и glorp».** 7 is the plan shown in
the location panel, inside Glorp UI's own interface. 8 stamps the plan onto
Construction Manager, gated on CM being present — and the space the goods icons
used to hold in the plan rows is the space he is keeping for CM's links.
**A session taking either one re-reads those mods' files**: what is recorded here
came off Glorp UI 10.08.26 and CM 2.2.12, and he updates `reference/` without
saying so. `python3 tools/refs.py` for the version, grep for the name.

### Waiting on him, cheap

**Two mods for `reference/`, which he offered**: `cheatmenu` and Advanced Auto
Build's interface. Why, in [`CONVENTIONS.md`](CONVENTIONS.md).

### Two lessons that outlive the faults

**Instrument before the third theory**, and **state the player cannot see or
clear is the mod's fault** — [`pitfalls/diagnosis.md`](pitfalls/diagnosis.md).
**Why «выгода от места» fell to 64%** is a row in [`SETTLED.md`](SETTLED.md);
**why a preference is an edit and never a term in the objective** is
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

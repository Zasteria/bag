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

### Step 6 — «Расширить» — is built and has never been loaded

**He chose the form on 2026-09-06: one button, in the editor, with the ground
buttons beside it.** New ground is whatever is picked now minus `_plan_touched`;
the old ground is frozen, the new rooms fill to the new share, and a pin the new
share outgrew lifts by itself. How it is wired, in one table, is in the
practice plan — the whole of it is four one-condition edits inside `_plan_*` and
narrowing `_candidates`.

**Nothing about it is verified. It cannot be from here.** The run that closes it
is written out at the end of that section, and the number that decides is
**«на старой земле сдвинулось», which must be 0** — on the window under the
button, and as `WTP EXT` in the diagnosis.

**Two other things nobody has run and neither is owed a build:** the
fold-by-default (a save carries its own value, so only a **new game** shows it),
and the whole plan on a large ground since the ladders were rebuilt — northern
Germany, 233 locations; Westphalia's 48 does not test it. **The extension has
the same open question**: it re-scores the ground it adds and re-ranks
everything, so a large second ground is its own measurement.

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

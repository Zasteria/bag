# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## The job: `where_to_produce`, three new things owe one run

**Read [`investigations/wtp_practice_plan.md`](investigations/wtp_practice_plan.md)
for the order and what each step cost, and
[`investigations/wtp_editor_design.md`](investigations/wtp_editor_design.md) for
the rules it implements. `_plan_*` itself is
[`investigations/plan_gaps.md`](investigations/plan_gaps.md). Nothing else.**

### Steps 0–5 and step 6 are closed and were seen in the game

All confirmed by his runs of 2026-09-05…07 and written up in the practice plan.
**Three rules outlive them:** the editor's state is the editor's and a fresh plan
reads none of it; `.gui` work starts at
[`pitfalls/windows.md`](pitfalls/windows.md); the changes window is shelved.

### Three things built 2026-09-07, none of them ever loaded

**1. Раздача уровнями.** The band no longer decides *how many*. A lap raises
`_plan_lvl` by one and every good may add at most one building in it; inside the
lap the ladder is what it was — scarce tiers, five bands in each, then everything
— so gain still says **which** location and scarcity **who picks first**.
Coverage is lap 1 (at level 1 the gate *is* `_pn = 0`) and the open ladder is a
dry lap (a lap that places nothing raises every quota); both phases are gone as
code. Two new counters make it work: `_px<side><n>` drops a good with no free
place from the walk, `_plan_top` stops a dry lap killing «Расширить».
[`investigations/plan_as_reservation.md`](investigations/plan_as_reservation.md).

**What it must fix:** eight goods with six places each finished with **one**
while cloth with forty-eight finished with **fifteen**. **What it may cost:**
total gain — `GAIN fed=` and the average percent of ceiling, against 2026-09-06.

**2. Окно сводки**, on a `@production_panel!` icon in the plan window: a row a
good — count, town/village split, places this ground offers it, its share, what
the ground pays its best building — and **why it stopped**, one of nine reasons.
Header: least, most, goods with nothing, goods that took every place they could.
Computed on opening, over `_plan_touched`.

**3. «Специализация»**, a button on the mod page: the same pipeline with two
different middles — a province gives its best charter to all its towns, and every
free room goes to whoever pays most in it. No shares, caps or tiers.
[`investigations/plan_specialisation.md`](investigations/plan_specialisation.md).

**What a run has to answer, in this order:**

1. `WTP L1 placed=` should be very nearly «every good this ground can make». If
   it is not, coverage broke when it became lap 1.
2. The lap profile should fall off gently. A cliff after L2–L3 means the level
   gate is not binding.
3. The summary's «меньше всех / больше всех» against the same numbers of
   2026-09-06 — that gap is the whole point of change 1.
4. `laps=150` in `PASS` is the guard cutting the draft off with work still to do.
5. «Специализация» on the same ground: does every town of one province hold the
   same charter? **The one form with no precedent in this mod** is
   `change_global_variable = { add = bag_wtp_rq<k> }` reading a *location* script
   value inside a walk over locations; if it silently yields 0, every province
   picks charter 1 and that is what the screen will show.

### The share, and the tiers, as they stand

A good builds while under its **total quota** *and* under the **cap of the side it
builds on** — and, since 2026-09-07, while under the level. Side quotas alone and
output weights were both rejected on numbers, and output cannot classify a
building as town or village
([`investigations/plan_share_sides.md`](investigations/plan_share_sides.md)).
The scarce tiers are a **share of the ground** (2…32 %) with the old 1/2/4/8/16 as
floors, so 48 candidates behave exactly as before and 1000 give 20…320.
**Neither has been run since.**

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

**Instrument before the third theory** and **do not spend his run on a guess** —
[`pitfalls/diagnosis.md`](pitfalls/diagnosis.md). **Why a preference is an edit
and never a term in the objective** is
[`investigations/plan_formula.md`](investigations/plan_formula.md).

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

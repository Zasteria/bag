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

### The plan for the practical sessions

**[`investigations/wtp_practice_plan.md`](investigations/wtp_practice_plan.md)
is the order, the files and what to ask him for.** Do not re-derive it. The
rules each step implements are
[`investigations/wtp_editor_design.md`](investigations/wtp_editor_design.md).

0. **`tools/code.py`** — done 2026-09-04, no run needed.
1. **The editor's window: the press line, the width, the frame** — **done and
   confirmed in game 2026-09-05.** All three lines read back; the windows are as
   wide as their content. `allow_outside` **stays**: the close button hangs
   outside on purpose, exactly as vanilla's does.
2. **Share, `_lock<n>`, and the «не нужен» flag** — **done and confirmed
   2026-09-06.** One change was reverted with it: the flag had been taught to
   hold `_pq<n>` at 1 in the global plan, and that crosses a line —
   **pins, flags, the share and the star belong to the editor window alone, and
   «План» gives a fresh plan reading none of them.**
2а. **Reshuffle the buildings a fill placed** — the fill chooses *which* good by
   shortfall but *where* by the accident of press order. Scope is strictly the
   buildings it placed and their own locations, so no count changes. Not built.
2в. **Rebuild the mod's menu** — his ask, 2026-09-06, and he called it urgent.
   Three tabs (Земля, Расчёты, Техническая), **one «open» button per function on
   the mod page** and every setting moved inside its own window; the editor gets
   its own button beside the plan's rather than sitting inside it. Full spec:
   [`investigations/wtp_menu_rebuild.md`](investigations/wtp_menu_rebuild.md).
   **Starts with one question to CMF**: can a `cmm_*` setting be read and written
   from our own window, or does its value move into a global of ours?
2б. **A packed picker** — **he took it off the table himself**: «в целом похер,
   что там дырки». The way out is that a good is its own scope (`every_goods`,
   `Goods.MakeScope`), so the count can sit on it and the picker becomes a
   datamodel — `research/interface.md` has the order of checks.
3. **Even eviction on «+1»** — two passes, never a packed number. `_esh<n>`,
   the per-good shortfall step 2 built, is the marker it needs; it is computed
   already and nothing on the «+1» side reads it yet.
4. **Provinces fold in the two plan windows.**
5. **Charters: «+1»/«−1» and whole-bundle eviction.**
6. **New ground fitted to a finished plan.**
7. **The plan shown in the location panel**, inside Glorp UI's interface.
8. **The plan stamped onto Construction Manager**, gated on CM being present.

### Waiting on him, cheap

**Two mods for `reference/`, which he offered and which are worth taking**:
`cheatmenu` (a catalogue of effects *in use*, and a large interface with live
`fixedgridbox` datamodels — exactly what step 2б needs) and a proper look at
Advanced Auto Build's interface. Why, in
[`CONVENTIONS.md`](CONVENTIONS.md).

**And one thing to settle with him, not for him:** he does not want coloured
markers — «не нужны всякие там жёлтые, красные буквы цифры» — while the yellow
count is the only thing that shows a pin, and an invisible pin is a fault
already paid for. The pin must stay visible; the form is his call.

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

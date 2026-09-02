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

**The tree is back at the build the thirty-sixth run praised**, the first where
the plan's formula ran and read right. The owner asked for it on
2026-09-02: «верни мод в состояние, когда только-только была введена удачная
формула… лучше мы решим уже на том моменте основную мучающую проблему, чем будем
делать это после того как накрутили сверху множество других неработающих
правок». Everything of 2026-09-01 above that commit is out — the new currency,
the unfed divisor, the input substitution, the round guard, the rescored rights —
and `claude/glass-sand-cycle-diagnosis-0qhgzw`, which carried the funnel probe,
was never merged and is not to be. **What those runs settled is kept**, with the
symptom itself, in the last section of
[`investigations/plan_formula.md`](investigations/plan_formula.md).

**Build the probe. Do not propose a cause.** Four of his runs went on four
theories about one symptom and fixed none of it;
[`pitfalls/diagnosis.md`](pitfalls/diagnosis.md) has the episode. **The plan will
not put glass in a town and puts it in villages freely** — and the town recipe
and the village one carry the identical `location_potential`, so the market gate
is not what stops it.

**The probe: a funnel counter per stage, for one good the player picks** —
`_avail_` said yes, then `can_build_building` in the location's scope, then a
method won (`_pm<n>` not 0), then `_plan_can_town_<n>`, then placed. Whichever
number collapses is the answer, and one run reads it.
`cmm_register_list_data_field` is a per-good column if the window is the wrong
place (`research/cmf.md`). **Read the abandoned branch once before building it
again** — it wrote that funnel, and the owner's word on it is the brief: the tool
was itself buggy and dear to walk around. He asked for no more counters until the
mod works; the probe does not break that — it comes out after.

**The three faults the thirty-sixth run named came back with the rollback**
(`TESTLOG.md`): the side-blind goods count, the open pass lifting the quota
instead of raising it, identical towns all taking the same right. **They wait.**

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

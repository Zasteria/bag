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
successful one — it asked only whether the item's folder existed, and it did from
the previous attempt — so an unfinished login copied last week's files over the
workshop folder. The folder is fingerprinted before and after now, the exit code
read, and **only a mod whose copy actually changed is copied onward**.

**Пункт 4, our own mods.** The copy loop was sound; nothing checked that it
landed. The install is **read back off disk** now, a mismatch says so with the
path, and the screen names the branch and commit installed.

**And `mods.bat check` answers it without the menu**, printing each of our mods
against the game's folder and the repository's branch and commit.

**What to ask him for:** `mods.bat → 1`, then `→ 4`, then `mods.bat check`, and
the output of all three. If a mod still reads «отличается» after installing, the
message names the folder to look at. The logs from whatever run follows go
through `python3 tools/which_build.py <logs folder>` first, as always now.

## `where_to_produce`: the whole-map plan

**Everything before the plan is done and the owner is content with it** — the
three ages on a row, the two «Считать» buttons, the four pickers including a
whole market. The state is [`../mods/where_to_produce/CLAUDE.md`](../mods/where_to_produce/CLAUDE.md);
one alignment question is open in `TESTLOG.md` and nothing else is.

**Do not ask him for logs unless something did nothing** — the rule and its
exceptions are at the top of `TESTLOG.md`.

**The whole-map plan is the job, and the next session's first move is
[`investigations/plan_formula.md`](investigations/plan_formula.md) — not code.**
The owner stopped the iterating himself on 2026-09-01, after six loads: «нам
нужно сначала вывести точную и доходчивую формулу приоритетов и выгоды
постройки производства, нежели вот так вот долбить всё туда-сюда». That file is
the specification — what one building in one location is worth, what the ground
can hold, and who claims it first — with four questions at the end that are his
alone. **Put those four to him and settle them before touching the allocation.**
[`investigations/whole_map_plan.md`](investigations/whole_map_plan.md) is how the
thing is built; the formula is what it is for.

**And he asked for no more counters until it works.**

**Six loads in, and the thirty-third found the guard eating the plan**: one sweep
counter shared by all six scarcity tiers, so the last tier — the one that fills
the ground — never ran, and twenty-eight buildings landed in a hundred and
forty-four places. Fixed, unloaded, and worth one press before any design work:
it is the difference between «план почти пуст» and a plan.

Also unloaded: the `n/m` on a ranking row — how many of a province's locations
can hold the winning building, his Sauerland question — and the plan's icons
given room to breathe.

Not built on purpose: **the demand knob** — «я выбираю товар и щёлкаю +1» — which
under the province model is a floor in provinces, one CMF numeric field and one
round before the sweeps, held back only so the next screenshot stays readable;
the RGO discount; regret ordering within a sweep; and choosing which goods to
plan rather than all of them.

**Also open, and cheap:** one layout question, in `TESTLOG.md`. Everything else
about `where_to_produce` is confirmed.

**What is left besides is decisions, not runs**, and they are written up in
[`investigations/town_rights.md`](investigations/town_rights.md):

- **Level rights**, deferred 2026-08-31: a quantity where the output rights are
  a ratio, so they want their own number and table.
- **Whether the buildable tick should ask about ownership** — that means asking
  the country from a trigger that has none.
- **`town_right_efficiency_penalty`**, in eleven rights and in no file
  `reference/` holds: one `grep` on the owner's install.

Which menu entry should run `tools/extract_game_files.py` is still open — no
entry does today.

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

- **A thumbnail for the other five mods.** Only `glorpui_hints` has one;
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

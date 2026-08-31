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
successful one: it asked only whether the item's folder existed in steamcmd's own
directory, and it did from the previous attempt, so an unfinished login still
copied last week's files over the workshop folder. The folder is fingerprinted
before and after now, the exit code read, the cached copy offered for deletion
first, and **only a mod whose copy actually changed is copied onward**.

**Пункт 4, our own mods.** The copy loop was sound; nothing checked that it
landed. The install is **read back off disk** now, a mismatch says so with the
path, and the screen names the branch and commit installed. A `game_mods` path
typo'd once — the one way this could install into a folder the game never reads —
is refused rather than created.

**And `mods.bat check` answers it without the menu**, printing each of our mods
against the game's folder and the repository's branch and commit — the line to
paste before anybody theorises about a mod again.

**What to ask him for:** `mods.bat → 1`, then `→ 4`, then `mods.bat check`, and
the output of all three. If a mod still reads «отличается» after installing, the
message names the folder to look at. The logs from whatever run follows go
through `python3 tools/which_build.py <logs folder>` first, as always now.

## `where_to_produce`: three ages on a row, and the pairs are in

Twenty-four loads. A row answers in three ages — «Сейчас», «По пути» (the best
this ground ever feeds, and the last age it can be built), «В конце» — because
the end alone cannot order a table where every wool province ends at 0.00%. Two
«Считать» buttons choose the order and which age the row names.

**The two-slot question is settled** from the game's own build panel — each slot
earns its own bonus over its own output:
[`investigations/production_ladder.md`](investigations/production_ladder.md).

**The twenty-sixth load passed on everything and the owner is satisfied with the
functionality.** The twenty-fifth's three complaints were a silk weaver offered
where there is no silk (the fed floor is half the recipe's possible bonus now,
`generate.fed_floor`), «Из чего» centred rather than left in its column (a sized
hbox spreads its children; it is a `widget` with an anchored child now), and the
buildable tick not re-ranking the open window. All three hold. Two name columns
narrowed to pay for the method column had to be given their width back and a
spacer; one alignment question is open in `TESTLOG.md`.

**Do not ask him for logs unless something did nothing** — the rule and its
exceptions are at the top of `TESTLOG.md`.

**So the next thing is the goal itself, not another fix.** Ask him before
designing any of it — the shape below is his sentence, not a spec.

**Where this is going**, in the owner's words: take a stretch of land, work out
every province's limits and lay out *all* its production — best goods first, then
the rest — capped at three or four buildings a province, with a rule for the ones
everything wants. None of it is built; it is why the per-province answer has to
be right first.

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
  modes and does not care. **If they are still not visible next time, offer to
  drop them** — another mod's interface, and the only thing here outside this
  mod's stated scope.

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
  rewritten copies and the run confirms it, as it does the Steam-side rewrite
  ([`archive/testlog_2026-08.md`](archive/testlog_2026-08.md)). Entry 2 does
  **not** re-extract the game.
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

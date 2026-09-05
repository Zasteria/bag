# `mods.bat` — что было сломано и как починено

Вынесено из [`../NEXT_SESSION.md`](../NEXT_SESSION.md) 2026-09-05, когда тот
перерос бюджет. **Работа сделана, ждёт одного прогона** — что именно просить,
осталось в `NEXT_SESSION.md` одной строкой. Здесь разбор обеих поломок.

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

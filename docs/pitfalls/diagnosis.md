# Pitfalls — finding a fault that logs nothing

Split out of [`../PITFALLS.md`](../PITFALLS.md), which stays the list of
mistakes; this is the method for the ones the engine does not report. Only the
player can run the game, so every entry here is about spending one run instead
of three.

## Diagnosing without a signal

**Two suspects and one round trip is a wasted round trip.** A monthly log line
that never appeared could have meant the pulse never fired, the setting read
errored, or CMF's log would not render what it was handed. Fixing all three
blind answered nothing: the next run still showed one number, and it was still
ambiguous. What works is a probe whose failure modes are *separable* — a counter
that only the pulse can increment, shown through a path already proven to work,
so the reading distinguishes "never ran" from "ran and could not be displayed".

**Check which build answered before believing what a run showed.** Twice a
report has been read as a fault in a mod whose files on disk were already right:
the folder the game loads,
`Documents/Paradox Interactive/Europa Universalis V/mod/<mod>/`, held an older
build, so the run reproduced the bug the fix had removed. Nothing says so — a
stale build is not an error, it is a different mod, and `error.log` is clean
because the old mod was valid. `gui.log` gives it away by accident: it prints the
file *and line* of every template that overrides another, and line numbers are a
fingerprint. `python3 tools/which_build.py <logs folder>` matches them against
this tree and every revision `git log` has, and names the commit that ran. Do
that first, before reading anything else into a run.

**Ask for the logs before theorising.** `error.log` being empty of your mod is
itself a finding: it rules out every failure the engine notices and leaves only
the silent classes — a missing localization key, an effect never called, a value
never read. Two of the four faults in `goods_target` were identified from the
logs plus `reference/` in one pass, without a further run.

## Four theories, three fixes, and the cause still unknown

**2026-09-01, and it is why `CLAUDE.md` now forbids guessing.** One symptom —
`where_to_produce`'s plan would not put glass in a town — drew four explanations
out of a session in a row, each stated with more confidence than it had earned:

1. *the ground has no sand* → wrong; the owner's screenshots showed the game
   offering him a glass guild;
2. *`can_build_building` refuses it, so glass is impossible in Westphalia* →
   wrong, and it went into `SETTLED.md` before he disproved it;
3. *the charter is granted where the bundle cannot be finished* → real, but not
   the cause; fixing it changed nothing;
4. *sand is in the market but not **produced** there* → unfalsifiable from here,
   and the same run refuted it: **`glass_guild` and `rural_glassmaker` carry the
   identical gate, and glass appears in the villages while never appearing in the
   towns.** One condition cannot be true and false in one market.

Each theory cost a fix and a run. **The run is the scarce thing** — only the
owner can make one — and none of the four spent one on finding out.

**And the shape of the mistake is the same every time: a condition was read out
of `reference/` and then treated as a fact about the ground.** The tree says what
a condition *is*, never whether it *holds* — market contents, RGOs and buildings
are save state, and nothing here can see them. A `location_potential` explains why
a good *might* be missing; only a run says whether it is. Say which of the two
you have.

What should have been built after the first miss is a probe: a counter per stage
of the funnel, for one good, reported on the window. Availability, then
buildability, then a method won, then the placement gate, then placed. One run
reads it and the cause has nowhere left to hide.

## The funnel probe, and the protocol for it

**Not built. This is what to build first when the plan does something and nobody
can say why**, and it is written out here so the next session delivers it in a
shape the owner can actually read — he asked, before the 2026-09-01 session
closed, where he was supposed to look.

**Where it lives: on the plan window's header line, nowhere else.** Not
`error.log`, not a file, not the mod action log. He plays the game; the answer has
to be on the screen he already has open, in one line he can screenshot. That is
also why it must come out again once the fault is found — «он просил не добавлять
больше счётчиков, пока не заработает».

**What it counts.** One good, the one already selected on the Goods tab, over the
candidates the plan is working: five numbers, each a subset of the one before.

| # | the stage | what a zero here means |
| --- | --- | --- |
| 1 | the country has the building unlocked (`bag_wtp_avail_<m>`) | no advance for it yet — «Сейчас» cannot offer it and «В конце» can |
| 2 | `can_build_building` says yes in the location's scope | terrain, rank or `location_potential` refuses it |
| 3 | a method won — `bag_wtp_pm<n>` / `_prm<n>` is not 0 | the scoring pass dropped it after 1 and 2 both passed, which is ours |
| 4 | `bag_wtp_plan_can_town_<n>` / `_can_rural_<n>` says yes | the cap, the one-building-per-type rule, or the good is already there |
| 5 | placed | the bands, the quota or the tiers never gave it a turn |

**Read left to right and stop at the first collapse.** 1 and 2 are the game's
answer and nothing here can argue with them; 3, 4 and 5 are ours and each has a
different owner in `generate.py`.

**The protocol, walked as the person who has to do it:**

1. install, load the save;
2. pick the ground — an area is enough, and «городских» in the header should not
   be zero if the question is about a town;
3. tick the one good in question on the Goods tab;
4. press «План»;
5. screenshot the header line.

That is one run and one screenshot, and it answers a question four theories could
not.

## Working blind

**Building a whole mod before loading it once is the expensive mistake, and it
has been made here.** `where_to_produce` was finished — four CMM lists, pickers,
scoring, tooltips — and then abandoned without ever running, leaving six
independent suspects and no way to tell which was in play, because an effect
that never runs logs nothing. One `cmf_log` on the first list, one round trip,
would have cut that to one. Only the player can run the game, so the size of an
untested increment is the whole risk: the smallest thing that produces a visible
signal beats the complete feature every time.

## Diagnosis

**`error.log` is the fastest tool here** and names the file and line. Every bug
found in this repo was found in it, usually in one pass. It also carries a
callstack for script errors, which is what points at the effect that swallowed
the rest of its body.

**An effect that never runs logs nothing at all.** That is the failure mode this
repo hits most. When the symptom is "nothing happened and the log is clean", do
not guess twice — put a `cmf_log` on the path in question and have the player
look at CMF's log panel.

**`game.log` carries load-time macro expansion errors** that `error.log` does
not.

**`reference/` is not the playset, and mistaking it for one produces a confident
wrong answer.** A session counted what every mod in `reference/` costs the
interface, found one mod far outside the range, and led with it. The owner's
reply was that he does not run that mod. `reference/` holds the five mods
somebody thought to upload; his `debug.log` of the same week mounts **22**, of
which 17 touch `in_game`. The mount table is right there in the log —
`virtualfilesystem_physfs.cpp: Mounted Data: .../workshop/content/3450310/<id>/<part>`,
one line per folder, in load order — and `python3 tools/playset.py <logs>` reads
it. Run that before any sentence beginning "the playset".

**A static widget count says nothing about a window built on `datamodel`.** The
same session reported `cm_hidden_window` as 23 widgets. It declares 23 and binds
a datamodel over every building type in the game, so what lives is that subtree
465 times over, with two more datamodels nested per row. Whenever a count is
about cost rather than about files, check what the window repeats over first —
`guicost.py --drivers` prints it.

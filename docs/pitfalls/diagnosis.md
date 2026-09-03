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

**The episode this whole instrument came out of**, and the rule it produced is in
the root `CLAUDE.md`: *a cause you cannot name is not a cause — do not guess it,
measure it.* Four of the owner's runs went on four theories about one symptom and
none on a measurement. The narrative, and what each theory cost, is in
[`../archive/diagnosis_four_theories.md`](../archive/diagnosis_four_theories.md).

## «Диагностика»: one press, everything, as text

**Built 2026-09-02.** The owner asked for it in as many words — «сделай какой-то
нормальный инструмент в моде, который будет отслеживать всё что можно
отслеживать… чтобы я мог его тебе показать или скопировать от него какой-то лог —
и ты сразу всё понимал "ОТ" и "ДО"» — after four runs went on four theories and
none on a measurement.

**A log and not a window, and that was measured rather than assumed.** The first
try was four columns beside the goods list; they came back saying glass stopped
at the placement stage in towns and could not say *in how many* towns, because a
column has one cell and the ladder had eaten the count. A screenshot has the same
problem one layer up. **Text has no width**, so every counter prints uncompressed
and no reading is ambiguous twice.

**And at the scale of the thing measured.** The first funnel asked the owner to
tick one good; his answer settles it for anything built here later: «эта проблема
— в плане расчётов по земле, где раскидываются ВСЕ товары, а не выбирается
конкретный». A per-good instrument cannot diagnose an all-goods pass, and the
symptom *is* the interaction between goods.

**Where it is:** the «Диагностика» button, Mod Menu → «Расчёт», beside «Показать
план». **It costs the plan nothing**: every counter except the per-pass pair is
read back afterwards off what the plan parked on the locations, so the expensive
button stays exactly as expensive as it was. **It reads state and writes none**,
so it is safe at any moment — pressed before a plan it prints zeros throughout,
which is itself the answer to «did the pass run at all».

**What it prints**, between `WTP ==== BEGIN` and `WTP ==== END`:

| block | what is in it |
| --- | --- |
| `BUILD` | the generator's own constants — methods, goods, rights, rounds, bands, tiers, and the 32 passes in order |
| `SELFTEST` | four lines that prove the dump itself, below |
| `PICK` / `SET` / `PASS` | everything chosen, both caps, which question was asked, and the totals the header line shows |
| `G<n>` | **one line per good, town and village apart**: `m` methods, `a` unlocked, `w` a method won, `r` of those with room left, `g` the gate would still open, `p` placed, `o` the best ordering it ever had — plus `ng`, the quota, the placements and the RGOs |
| `ROOM` | how many towns and villages still had room when the plan stopped |
| `P<n>` | what each of the 32 allocation passes did: sweeps used out of the guard, and the running total after it |
| `RIGHT <k>` | how many towns each urban right was granted in, and what it grants |
| `L` | one line per location, best first, with what was put in it — a good to a line, folded back into one line by `tools/diag.py` |
| `R` | the single-good ranking's own rows, for the case where the plan is right and the table it is read against is not |

**Reading a `G` line: the first zero left to right is the stage**, and the number
before it is how many locations got that far — the thing a column could not
carry. Three readings have different owners:

- `w > 0`, `r = 0` — **the ground filled up**. Not a fault in itself.
- `w > 0`, `r > 0`, `g = 0` — the good, or its building, **is already in every
  place that still has room**. That is the one-per-type rule, and whether it is
  right is a design question.
- `g > 0`, `p = 0` — **the allocator never gave it a turn.** Ours, and the three
  suspects are named on the same line: `q` the quota, `ng` against the tier the
  pass admits, and `o` against the band — a good whose `o` never reaches 200 has
  only the last band, by which time the towns are taken.

**Both caps print what they left out**, so a cap is never silently the answer.

**How the text gets out of the game:** `mods.bat → 8`, or
`python3 tools/diag.py`. It finds the game's `logs`, takes the last report,
strips the log prefixes, folds each location's goods back onto its own line and
copies the result to the clipboard. `--raw` keeps the log's own shape; `--all`
takes every report in the file rather than the last.

**It comes out with the fault it finds.** The whole of it is `bag_wtp_diag*`,
`bag_wtp_dv*`/`_dg*`, the `_f*` counters, the two `_pass*` counters in
`_plan_allocate`, and one button.

## And it worked: what one press answered

**2026-09-02, the first press.** Four theories over four runs had not named the
cause; one press of the finished instrument did, and the report is what settled
it rather than any reasoning in this file.

**The number that did it: a town-side method won on 3 of 17 town-side
locations** — for glass, and for cloth, tools, pottery, jewelry, beer, leather,
paper, weaponry and eleven more; while sand, masonry and fiber_crops won on all
17. Fourteen of those «towns» take RGO buildings and refuse manufacturing, because
they are villages the player ticked into towns and a guild is `town = yes`. **The
tick moves a location to the plan's side of the ledger; it cannot move its rank in
the game.** `SETTLED.md` has the row.

**Twenty goods at once is why it is settled and one good was not.** The funnel's
first shape asked about one good and could not have distinguished the market
condition from the rank: only a line for *every* good shows sixteen goods with no
market condition stopped in exactly the same fourteen places.

**And the dump found two faults in itself**, which is the third time this file
records the probe finding the fault in the probe: `[glass, masonry]` in a
`debug_log` string is data-function syntax, and `error_log` writes into
`debug.log` too, so every headline arrived twice. Both in `research/engine.md`.

## A reader that guesses a format loses the run it was built for

**2026-09-02, the first press.** The mod's half worked on the first load — button,
callback, effect and `debug_log` all — and the owner got a file of **zero bytes**,
because `tools/diag.py` cut the game's log prefix with a regex written against a
*guessed* shape. Nothing matched, so no line came out starting with `WTP`, and the
fold dropped every line it did not recognise.

Three rules came out of it, and they are about any reader of anybody else's
output:

- **Cut at what you wrote, not at what they wrote.** `WTP` is in every line of
  ours and in nothing else, so `line.find("WTP ")` is an answer where a regex
  over the prefix is a prediction.
- **Never drop what you do not recognise.** An unknown line goes through with a
  mark on it. A reader that silently discards is indistinguishable from a mod
  that never ran — which is exactly the confusion the whole instrument exists to
  remove.
- **Refuse to hand back nothing.** If the fold keeps less than half of what the
  log held, the raw block is written instead and the tool says so. An empty file
  is worse than no file: it looks like an answer.

**And a press has to be visible where it was pressed.** He expected a window; the
report is too long to read on screen and is not for him. The button's own
description now prints what the last collect saw, the same way «Считать» prints
its three numbers — so the press is never indistinguishable from a dead button.

### Three more, found in the same reader on 2026-09-03

All three had been in every report the owner sent, and none of them logged
anything. They are the second half of the rules above, stated as failures.

**A prefix is not a key.** `line.startswith("WTP RQ ")` was meant for a town's
charter scores and also matched `WTP RQ legend`, the one line that explains the
numbers. The legend arrives after the last location, when no row is open, so the
fold threw it away in silence: it is in **none** of the three reports of
2026-09-03, and nobody noticed because a legend's absence looks like a legend that
was never written. Had it arrived one line earlier it would have overwritten the
last town's scores instead. `re.match(r"WTP RQ \d", line)` now, and the legend is
printed *before* the rows rather than under two hundred of them.

**A row took every name it had been handed, and the mod handed it two.**
`debug_log_scopes` writes one line naming the current scope; the location block
called it before its `L` line **and again** before its `RQ` line, so the log held
each location's name twice and the fold gave every row from the second onwards
the previous location's name as well as its own — «WTP L Район Липпштадт (980)
Район Зост (981) rank=2». The owner, looking for one town in it: «Понятия не имею
где конкретно искать строку Гослара.» The second call is gone; the reader takes
the *nearest* name and marks the rest rather than joining them.

**A number can be labelled with another number's name.** `ranked_provs` in the
`PASS` line printed `_found`, which is the single-good ranking's province count,
and read `0` on every plan ever dumped. Nothing about a zero says it is the wrong
variable. **A field that is always zero deserves the same suspicion as a
safeguard that always fires**: check what it is reading before believing what it
says.

**And the one number that is honest and still misleads.** `q` in the goods line
is read back after the plan, so it carries the layer the open ladder added — one
per sweep — on top of the quota. `PASS quota=2` beside `clay q=2 rgo=2` reads as
the RGO discount doing nothing, and is the discount working and the open ladder
adding one back. An hour went into re-deriving that from three reports before the
line was made to say it. **A report that is read against itself has to say which
of its numbers were taken when.**

### A fix that follows from consistency is still a guess

**2026-09-03, and it cost a quarter of a plan.** The «Сейчас» plan refused a
building whose advance the country had not taken and, in the same answer, handed
out charters from an age it had not reached. That is a genuine inconsistency, it
was named in an investigation, and closing it needed no measurement to justify —
which is exactly why it went in without one.

The run: Münster holds one of the thirteen charters' advances, so the gate left
it one grantable charter, and «every town gets one» gave that charter to all
forty-eight towns. Cloth in 48 locations of 192; goods produced down from 35 to
30. Reverted the same day.

**The rule this repository already had was «a cause you cannot name is not a
cause — measure it».** This is its other half: **an argument about the shape of
the code is not a measurement about the answer**. The gate was consistent,
defensible, passed every checker, and made the output worse — because the rule it
collided with («каждый город обязательно получит право») was written when nine
charters were available and degenerates at one.

**What it does not mean is «change nothing without a run».** The same session
also removed dead work, corrected a scope misreading and rebuilt the pass order,
and all of those held. The distinction is what the change is *for*: repairing
something measured, versus tidying something that merely reads wrong. The second
kind is where a run is owed **before** the change ships, or where the change
should be a report field instead — which is what the advance became.

### A measurement answers the ground it was taken on

**2026-09-03, and it cost the same fault being closed twice.** The plan's bands
were measured on Westphalia — 48 locations, a quota of 2 a good — and the reading
was unambiguous: every good got roughly its share, the bands barely mattered, and
the relative-band idea was written up as unnecessary with the numbers to prove it.
The same build on northern Germany, 416 locations, quota 29:

```
cannons   candidate locations 103   quota 160   placed 2
goods reaching 1000 somewhere:  30, averaging 42 buildings
goods that never do:             8, averaging 12
an even share would be          36
```

Nothing about the formula changed between the two. **The quota binds on a small
ground and binds nothing on a large one**, and which of the two mechanisms is
doing the allocating flips completely between them. A measurement taken where the
quota binds says nothing at all about ground where it does not.

**So: before closing a question with a number, say what the number is a
measurement *of*.** «The bands are not the problem» was true of Westphalia and
false of the realm. The habit that catches it is cheap — name the regime in the
same sentence as the finding, and the next reader can see whether their ground is
the same one.

**And a corollary about asking for runs.** The press that overturned this was
asked for in the previous session and arrived in the same file as the small one,
which is the only reason the error lasted hours instead of days. **Where a
quantity in the formula scales with the ground — a quota, a room count, a
candidate count — one press is not evidence and two of different sizes are.**

## The report is not for the player, so the tool has to read it

**2026-09-02, his second press.** «Проверить насколько всё идеально и выгодно
распределено я не могу из-за того что это сложно для меня как человека… Ты мог
бы сам посмотреть.» He is right, and it is not a complaint about the format: 47
counters and 127 location rows are a session's input, not a person's.

So `tools/diag.py` **draws the conclusion and prints it first** — how full the
ground came out, how many buildings earn anything where they stand, how the goods
divide, which right holds how many towns, which passes ran out of sweeps. A dozen
lines of Russian at the top of the same file, and the same dozen in the console.
The detail stays underneath for the session.

**And one guard about guards.** The rule that a reader must refuse to hand back
nothing was written the day before, and its first version counted lines: fewer
out than in meant something was lost. On the first real report the fold honestly
turned 427 lines into 178 — four of every five are a good on a location's own row
— and the guard threw the folded version away and shipped the raw one. **Count
what must survive, not how much came out**: every `WTP` line except the `WTP LG`
rows that folding is for.

## What a `debug_log` string can and cannot reach

**Measured 2026-09-02, by a dump failing.** Three presses produced 632 `WTP`
lines in `debug.log` and 306 in `error.log`, every number in them zero. All four
of these shape the file that is built now.

- **`debug_log` writes on a normal build.** Construction Manager guards its own
  behind `debug_only`; that is their choice, not a requirement. `error_log`
  lands too, which is why the headline goes to both sinks and the detail to one.
- **A global is reachable**:
  `[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('<sv>')|0]` resolves inside
  a `debug_log` string exactly as it does in a localization.
- **The item a walk is standing on is not reachable at all.** `THIS.MakeScope`
  gives «Failed to convert statement for argument '0' for call 'SetRoot'», once
  per reader per row, and the bracket is echoed literally into the log. **Park a
  per-row number in a scratch global and print that**; `debug_log_scopes = no`
  logs the current scope, which is what names the row.
- **And one script-value form reads zero in silence.** `value = 0` with
  `if = { limit = { has_global_variable = x } add = global_var:x }` returned 0
  for every reader, with nothing in any log — on a plan that had just placed 417
  buildings. **`value = global_var:x` is the form that prints real numbers**, and
  a guard belongs in the effect, where `if` demonstrably works.

**There is no clipboard.** The whole copy surface the engine exposes is
`LobbyView.CopyServerID` and `ChildItem.CopyDnaToClipboard`, neither taking a
string — checked against the game's own `data_types_gui.txt`. Text leaves the
game through the log, which is why `tools/diag.py` exists.

**The lesson under all of it is the one this file already carries**: the probe
found the fault in the probe. A dump that had only been reasoned about would have
been believed.

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

**A budget subtracted from the pool and again from each share charges twice.**
2026-09-03. `where_to_produce`'s plan spends the ground in two phases: the town
charters go in first, then the goods fill what is left. `_plan_quota` is
`(rooms − what the charters spent) ÷ goods`, which is right — every good pays for
the charters once, together. But `_pn<n>`, the good's own counter that the
allocator reads against that share, is incremented by the very effect the charter
round calls to place a building, and nothing cleared it. So a good the charters
favoured arrived at the allocator already over its share and was frozen out of the
ground it is best at — `tools` at `_pn = 6` against a cap of **2**, unable to take
a free room paying it 799 out of 1000. **The symptom is a good that has exactly as
many buildings as some other phase gave it and none of its own**, and it looks
like a scoring fault, which is where three theories went first. When two phases
share a counter, say in one place which of them the budget is for.

**A safety net that fires on every report is a broken tool, not a careful one.**
2026-09-03. `tools/diag.py` folds the log and then checks that no `WTP` line was
lost, falling back to the raw log if any was. The rights line added that day is
rendered as «права: …» — **without the tag** — so every report with one counted 48
lines as lost, the net fired every time, and the owner got the raw log for days
without either of us noticing. Worse: the fallback then ran the summary over
**all five presses at once**, so «Права: выдано 263» was 48+48+48+71+48 across
five different runs, and any conclusion drawn from that header was nonsense. The
tell is that the tool's own warning line becomes routine — read the warning it
prints, and if it prints on every honest input, the check is the thing to fix.

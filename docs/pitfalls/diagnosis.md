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

## Instrument before the third theory

**2026-09-04, the plan editor.** Four sessions and eleven of his runs went on a
part of the mod the report could not see. Every press was invisible: «ничего не
изменилось» covered a button that never fired, a rule that refused, a placement
that silently failed and a walk that evicted and restored. Each session picked a
theory, built a fix, and spent a run on it.

**He ended it himself**: «Добавляй скан информации для себя в диагностике на
функцию редактора, чтобы ты видел чё там происходит.» Three lines went into the
report — what was asked, what the scan found, what the walk saw where it stood —
and **the very next press named the cause**, which no amount of reading the code
had:

    EDIT asked  presses=40 op=1 good=… reached=1 | outcome done=0 fail=1
    EDIT scan   fitn=42 cands=42 | walk hit=1 town=1 load=4 esg=9 esw=0
    EDIT walk   evicted=1 room=1 | placed_before=191 placed_after=192

Evicted, room found, placement refused, victim restored — `_edit_good` was a
country variable being read in a location's scope. **The rule: the second time a
part of the mod cannot be seen from the report, stop fixing and instrument it.**
Not the fourth.

**Three things make an instrumented press readable.** A counter that separates
«the button never fired» from «a rule refused». State reset when the window
opens, or a global from an hour ago reads as this press's result. And a `hit`
flag, because 0 and «no walk happened» must not look alike.

**A `debug_log` string cannot reach the item a walk stands on** — park the
location's numbers into globals inside the walk, and print those.

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
| `EDIT` | **the last press of the editor, in three lines** — what was asked (presses, op, good, reached, done/fail/norefill), what the scan found (fitn, cands), and what the walk saw where it stood (hit, town, load, esg, esw, evicted, room, placed before and after, load after, both caps). The location's numbers are parked into globals inside the walk, because a `debug_log` cannot reach the item a walk is on |
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

**How the text gets out of the game:** `mods.bat → «Забрать диагностику из игры»`, or
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

**Closed, and the whole episode is in**
[`../archive/diagnosis_reader.md`](../archive/diagnosis_reader.md): `tools/diag.py`
guessed at the report's shape, five presses were summed into one «коротко», and
the run it was built for was spent reading a summary of the wrong thing. The rule
it produced: **the reader and the writer are generated from one description, or
the reader is a second guess about the first.**

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
- **And a scope parks in a global just as a number does**, which is what lets a
  label say «+1 сукно → Мюнстер» instead of «сделано». `set_global_variable =
  { name = x value = scope:y }` after a `save_scope_as` inside the walk, then
  `[GetGlobalVariable('x').GetLocation.GetName]` in the localization —
  `GetGlobalVariable` is a global promote returning a `Scope`, so the same cast
  chain works on it that `mods/where_to_produce` already uses one scope down
  (`[Location.MakeScope.GetVariable('bag_wtp_r_good_1').GetGoods.GetName]`), and
  that CMF's own log uses for `cmf_log_loc`. **A number has no name**: an index
  in a global can only be turned into words by a `customizable_localization`
  with a branch per value, so park the scope where the name is wanted and the
  number where the report is. Built 2026-09-04, not yet seen in game.
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

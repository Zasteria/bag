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

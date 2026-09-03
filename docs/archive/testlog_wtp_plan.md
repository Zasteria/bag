# `where_to_produce` — the runs the plan was built on

Split out of [`../TESTLOG.md`](../TESTLOG.md) on 2026-09-03, at its budget. These
are superseded: what they say about the **game** stands, what they say about our
code was rewritten by the runs that followed. `tools/kb.py` still searches them.

**2026-09-03 — `where_to_produce`, the probe came back thirteen zeroes, and the
level rights work.** Goslar took tooling on «сейчас» and books on «на конец»,
again. «Понятия не имею где конкретно искать строку Гослара.»

- **`WTP RQ` printed `1=0 2=0 … 13=0` on every town, and that is the probe's own
  fault.** `_rqf<k>` asked `_plan_can_town_<n>`, which is a **placement** gate: it
  also asks whether the town still has room and whether the good is already
  standing there. At grant time the town is empty and the gate reduces to «a town
  method for this good won here»; the dump runs after the plan, when every town
  is full, so every clause was false. The twin asks `var:_pm<n> > 0` now — the
  scoring fact, which survives the plan.
- **And the line is rendered rather than printed raw.** `1=0 2=0 3=0` is material
  for an answer, not an answer: `tools/diag.py` now folds it into «права:
  ювелирные 2909 | книгопечатные 2856 ← выдано | …», names from the report's own
  legend, sorted, with the granted one marked.
- **The level rights work and his culture reading was right.** Münster is
  Westphalian, which is in the Netherlandish group, so `flemish_cloth_industries_right`
  is offered — and it took **9 grants against `royal_textile_rights`' 1**. His
  «two towns of one province, one textile one flemish» is the province divisor
  spreading them, which is what it is for. **But the 9:1 is not the level
  arithmetic**: the mod scores both purely on which goods they favour, so flemish
  (cloth, fine cloth) beats textile (cloth, dyes, fine cloth) only because dyes
  drags the average down. Nothing in the code knows five levels beat +20%.
- **Numbers for the next press to be read against**: `jewelry T o=909`,
  `paper 1000`, `dyes 952`, `books 615`, `tools 399`. If Harz has silver, jewelry
  in Goslar should read near 2900 and the RQ line will say whether it did.
- **His design point, and it is a real gap.** «Мод должен проверить есть ли 5
  городов в провинциях с драг металлами, прежде чем забивать эти города какими-то
  другими правами.» Rights are assigned town by town in walk order, each taking
  its best; nothing lets a right only two towns on the map can serve claim those
  two first. The goods have that machinery — `PLAN_TIERS` — and **it was weakened
  on 2026-09-02 to pay for the round guard**: the ladder now runs in the last band
  only, so in bands 800–200 a common good takes a scarce one's ground with no
  contest. Both are open.

**2026-09-02 — not a run: `where_to_produce` was rolled back to the build of the
thirty-eighth load**, and the owner stopped the line. He picked that build by its
own message — the four tests, «большой рывок» — «именно в этом коммите я
почувствовал, что мод выглядит так, как я его задумывал… именно в этом коммите я
хочу начать постройку диагностического инструмента». **The two runs directly
below tested builds that no longer exist**, and so does the funnel probe branch
`claude/glass-sand-cycle-diagnosis-0qhgzw`, which was never merged. What they
measured about the *game* stands — the identical `location_potential` of
`glass_guild` and `rural_glassmaker` above all; what they say about our code no
longer describes the tree. What the thirty-eighth load left open came back with
it, deliberately, and is listed in `investigations/plan_formula.md`, last section.

**2026-09-03 — `where_to_produce`, the locked advances held, and the rights turned
out to have no covering rule.** Westphalia, all 48 locations ticked to towns.

- **The locked-advance gate works, and the two survivors are correct.** Porcelain
  and lacquerware are gone from «сейчас» and stay in «на конец» — he checked and
  both unlock in age 5 for Münster, so that is right, not a leak. Goslar keeps
  tooling on «сейчас» and takes jewelry on «на конец», as predicted.
- **No town got the weaponry charter, on either plan**, and none got jewelry.
  «Какое-то количество оружейных прав должно было выделиться каким-то городам
  обязательно.»
- **The score is right and the rule is missing.** Over those 48 towns the bundle
  reads cannons 136, firearms 166, weaponry 187 — averaged over three, the
  charter is **163** everywhere, against 200–624 for every rival. Westphalia has
  almost no iron (2 buildings of it), so all three are poor; the charter loses
  fairly and **nothing then forces it in**. The goods have had that rule since
  2026-09-01; the rights never did.
- **A covering ladder for the rights**, the goods' `cover` pass in the same
  shape: after the banded passes, the bands run again admitting only charters
  with nothing anywhere, so each takes the town its ground suits best rather than
  whichever town the walk reaches first. Then the open pass as before. Not run.

## `NEXT_SESSION`'s `where_to_produce` section, as it stood 2026-09-02

Superseded by [`../investigations/plan_gaps.md`](../investigations/plan_gaps.md);
its numbers describe builds that no longer exist.

## `where_to_produce`: it works, and what is left is his to choose

**The plan does what it was meant to, and he has seen it** — «на первый взгляд
работает как надо, города получают права и домики из прав», 2026-09-02. The
symptom that cost four runs is measured, named and fixed: the tick is the rank
now (`SETTLED.md`), the charter spam is gone, and **four fifths of placed
buildings earn a bonus where they stand, capturing 78% of their own recipe's
ceiling on average**. All of it is on `main`.

**Read `TESTLOG.md` before anything.** Four runs of 2026-09-02 are in it and they
carry every number this section summarises.

**Three things he named on 2026-09-02 are built and none has been in the game.
One big ground tests all three at once**, and northern Germany — 416 locations,
1312 rooms — is the one that failed before:

- **The round guard is 50 and the pass count is twelve.** 127 locations already
  put the open pass at 11 of 12, and 970 buildings over 32 goods cannot be done
  in fewer than thirty sweeps. What to read on the run: `WTP P<n> sweeps=x/50` in
  the report — a pass at 50 is still being cut off — and whether the rooms come
  out full. **What to watch against it is the hitch** he reported without
  complaint on that ground: twelve passes are fewer than thirty-three, but each
  may now run four times as long.
- **The plan window pages.** `PLAN_ROWS` is still 150 because the datamodel is
  what costs; `PLAN_RANKED` (1500) is how many rows the pass keeps, and «Назад» /
  «Вперёд» under the summary walk them. The summary says «в строках N» beside the location
  count, so the two numbers can be told apart at a glance. If the ground is bigger
  than 1500 used locations the bar says so by the two disagreeing.
- **The province ceiling is gone** — setting, alias, default, both localizations
  and its gate in the allocator.

**What is open, and none of it is a bug:**

- **Nine goods take 45% of the ground.** Coal, sand, beer, cloth, glass, jewelry,
  leather, masonry, pottery — makeable in every location, so each reaches the
  quota and stops at 20. Sixteen town-only goods got 7 or fewer, competing for
  22 towns × 4 slots that the rights have first call on. **The formula working as
  written.** The lever he had for it was `plan_max`, and it went with the province
  ceiling at his word; if he wants one back it should be derived, not typed.
- **The single-good side** has faults he has seen and set aside without naming.

**The diagnosis comes out when the work does.** It is `bag_wtp_diag*`, the `_f*`
counters, the two `_pass*` counters and two buttons; `pitfalls/diagnosis.md` has
what it prints and how to read it, and `tools/diag.py` draws the conclusions so
he does not have to.

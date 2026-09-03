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

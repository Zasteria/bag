# `where_to_produce` — what has been tried and must not be tried again

**A global variable map keyed by a database object, 2026-09-04.** Built to get a
per-good number into a picker row — `add_to_global_variable_map = { key =
goods:clay }` and `GetVariableFromGlobalVariableMap(…, Goods.MakeScope)` — and it
crashed the game on opening the window, twice, with nothing in any log. CMF keys
every map it keeps by a flag and never by a database object; `Goods.GetKey` makes
one from the row, and that route is untried. Reverted whole: the build had three
new mechanisms in it and a crash leaves nothing to bisect with.

Split out of [`../../mods/where_to_produce/CLAUDE.md`](../../mods/where_to_produce/CLAUDE.md)
on 2026-09-03, at its budget. Every line here is a thing that was built, run and
reverted; the brief keeps the one-line pointer and this keeps the reasons.
`tools/kb.py` searches it.

---

**Not to be attempted again:** a geography tree of our own (empty twice), gating
charters on their advance (`plan_gaps.md` H), spreading charters inside a province
(it emptied a province of the charter its ground was made for), answering a
preference with a re-plan, and reopening why a scarce good has one building —
**it is the RGO discount, measured twice** (B). `bag_wtp_register` destroys
nothing (`docs/PITFALLS.md`).


Where each is argued out: `docs/investigations/plan_gaps.md` for the charter age
gate (H) and the RGO discount (B), `plan_formula.md` for the editor against a
re-plan, `whole_map_plan.md` for the geography tree, `docs/PITFALLS.md` for
`bag_wtp_register`.

# `where_to_produce` — what has been tried and must not be tried again

**A number per good in the editor's picker, 2026-09-04, four builds, four
crashes.** Keyed by `goods:clay` (crash on opening, twice); keyed by a flag from
`Goods.GetKey` with `.IsSet` guards and a CMM switch (crash on opening, with the
switch on and off, because `And(...)` in a GUI expression is eager); and with no
map at all — 47 cells written into the `.gui`, each holding
`ScriptValue('bag_wtp_show_pn<n>')` in its own localization key — **which crashed
on loading**, before the game could be entered. Not one of the four left a line
in any log. Everything resolves offline: names, keys, script values, braces,
every checker.

**Do not build a fifth bridge.** What the four share is the number reaching the
interface, not the mechanism carrying it, so the next attempt is a picker with
**no number and no data function in it at all** — «+» / «✖» as a plain
localization value, the count read from the plan's own rows. The 47-cell build is
kept whole at `92a8af4` if it is ever worth bisecting. `../pitfalls/interface.md`.

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

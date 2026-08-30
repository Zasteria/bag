# `where_to_produce` — brief

A planning tool in the Mod Menu. Tick the regions you are planning inside, pick
a building and the production method you mean to run it on, and get the
locations inside those borders ranked by the production efficiency that method
would gain from raw materials.

**State: written, never loaded once. Nothing here is confirmed in game.** This
is the second attempt at the question; the first was
[`../../docs/archive/where_to_produce.md`](../../docs/archive/where_to_produce.md),
and it died because a whole feature was finished before its first load. Do not
extend this before the run below has happened.

**What the first run has to answer**, in the order the pass runs, and the button
description on screen prints the first three as numbers:

1. Do the region rows carry names, or the raw keys? They are labelled by handing
   CMM the game's own region key as a flag — documented, never done here.
2. Does ticking a region reach script? "Отмечено регионов" above zero says yes.
3. Does the walk find locations? "Рассмотрено локаций".
4. Does the ranking fill rows? "Заполнено строк".
5. Do the result rows read back a location name and two numbers out of global
   variables? That is the one mechanism nothing in this repository has proved.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, run from
`tools/refresh.py` with everything else. It writes the 218-option method picker,
the six region lists, the per-method weights, the bonus script value, the fifty
result rows and both localizations, all from the game's own files.

## What is known to be unproven, beyond the run

- **Seven of the seventy-seven region keys** are named by the game's
  localization but scoped into by nothing in `reference/`:
  `central_africa_region`, `central_india_region`, `macaronesia_region`,
  `micronesia_region`, `poland`, `polynesia_region`,
  `southern_africa_islands_region`. `region:<key>` on a key the map does not
  define fails at load, in `error.log`. The generator prints the list on every
  rebuild.
- **`can_build_building = global_var:bag_wtp_building`** — a global variable as
  a trigger's target. Only reachable with the "только там, где уже можно
  строить" tick on, so a failure there does not touch the default path.
- **`ordered_in_global_list`** over a global variable list. The ordering itself
  is not in doubt: the game's own script proves `order_by` sorts highest first
  by writing `multiply = -1` where it wants the weakest.

## Two things that are settled and should not be re-litigated

- **The fifty-row ceiling is CMM's, and only the result table pays it.** It is
  an unrolled chain of `if`s ending at item 50, in two CMF files of about 3200
  lines. Dropdowns have no cap at all — that is why the method picker is one
  control with 218 options. Raising the table's ceiling means leaving CMM, not
  editing a number: the owner knows and asked for the capped version first.
- **The bonus is province-level.** The game credits a raw material worked
  anywhere in the province, so every location of one province reads the same.
  `rgo_bonus_filter` already matches that on screen.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

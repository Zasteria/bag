# The whole plan: every building, placed once, over one stretch of ground

**This is what the mod was built for**, in the owner's words on 2026-08-31, and
everything before it — the per-province answer, the three ages, the two «Считать»
buttons, the market picker — exists so that this can be right rather than
plausible. Nothing of it is built. This file is the statement of the job, kept
whole so that nobody has to reconstruct it from a chat again.

## What he asked for

> Добавить возможность отмечать несколько нужных товаров/прав или вообще все
> сразу и видеть, какие провинции становятся «магнитами» для слишком большого
> числа зданий. Показывать нагрузку на провинцию и предлагать альтернативы менее
> загруженным местам.

Out of which: **a map of the full production cycle**, every building distributed
over the chosen ground the most profitable way, with four things the
one-good-at-a-time table cannot do.

1. **Many goods at once**, or all of them. Today a run answers for one good or
   one urban right.
2. **Slots are finite and contested.** A province that wins three goods cannot
   host three buildings; a cap of three or four is the owner's own figure, and
   what happens to the losers is the whole problem. «Магнит» is his word for the
   province every good wants.
3. **The RGOs already on the ground count.** Ten spinning-crop RGOs in the zone
   and the plan should not answer with ten more spinning-crop workshops. Balance,
   not a ranking repeated per good.
4. **It is re-runnable under a constraint.** «Этому товару нужно больше места» —
   the whole map shifts and settles again.

## How it is meant to be played

> Я создаю изначальную карту со всеми запланированными зданиями сразу. Далее
> смотрю какой товар в дефиците — иду смотрю именно на этой карте где лучше
> воткнуть этот товар, чтобы не помешать другим зданиям в будущем, но при этом
> получить максимальные бонусы местного производства.

So the map is not a report, it is a **standing plan** the player consults when
the game asks a question. The shortage is read off the game's own market panel
(«Local balance», see [`market_truth.md`](market_truth.md)); the plan says where
that good goes without spoiling the rest.

## What is already in hand

- **The per-province answer, and it is trusted.** Twenty-seven loads, and the
  owner's verdict on the twenty-sixth was that the functionality is right. That
  is the scoring this stands on.
- **A method's worth per province, in three ages**, and the rule that a recipe
  the ground mostly cannot feed is not an answer (`generate.fed_floor`).
- **Four ways to frame the ground**, a whole market among them.
- **The engine facts that bound it**: the bonus is province-level, a row is a
  `province_definition`, and building slots — the one thing that would separate
  two locations of a province — are hidden from script.

## What has to be decided before anything is written

None of these is a research question; they are the owner's, and asking them is
the first move, not the second.

- **How many buildings a province.** Three or four was said in passing. Is it a
  constant, or does it come from the province?
- **What "balance" means when two goods want the same ground.** Highest score
  wins and the loser takes its next-best province? Or a global assignment that
  maximises the total, which can move a good off its own best province to free it
  for one that has nowhere else to go?
- **What counts as demand.** Every good equally, or weighted — by price, by what
  the market is short of, by what the player ticked?
- **What the RGOs on the ground do to it.** Do they merely inform, or does a
  province already working a good lose priority for a building that makes it?
- **What the answer looks like.** A table per province of what to build there, a
  map mode, or both.

## The trap this must not walk into

**A whole feature finished before its first load is how `where_to_produce`
ended up with six suspects and no way to choose between them** — the rule at the
top of `CLAUDE.md`, earned here. Whatever the design turns out to be, the first
thing built is the smallest piece that shows a signal: two goods, one province
cap, and a table that says which good lost and where it went instead.

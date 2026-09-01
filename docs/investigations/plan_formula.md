# The plan's formula: what a building is worth, and who gets the ground first

**Written because the owner called a halt to iterating**, on 2026-09-01, after
six loads of the whole-map plan: «мне кажется нам нужно сначала вывести точную и
доходчивую формулу приоритетов и выгоды постройки производства, нежели вот так
вот долбить всё туда-сюда». So this is the specification, in one place, to be
agreed *before* the next line of the allocation is written. Where the code
already does a thing, it says so; where the formula is a proposal, it says that
too.

## Part one: what one building in one location is worth

**A. The engine's number, and it is settled.**

```
RGO bonus % = 10 × (input amounts the province supplies) ÷ (all input amounts)
```

Verified to the digit against three tooltips (`docs/research/engine.md`). Every
input counts towards the denominator, produced goods included, which is why a
weapon smith tops out at 5.24% rather than 10%. It is counted over the whole
`province_definition`, both halves of any border cutting it.

**B. What that is worth is what it produces, not the percentage.**

```
worth = output_per_level × (1 + bonus/100)
```

A forest village at a full 10% makes 0.2 a level; a weapon guild at 2.86% makes
1.0. Ranking on the percentage puts the village first, which is wrong, and cost
the eighth load. `bag_wtp_m<n>` is this number × 1000.

**C. A recipe the ground mostly cannot feed is not an answer.**

The bar is half the bonus that recipe could ever earn — `generate.fed_floor`,
one literal per method. Below it the method is not offered at all. This is what
stops a silk weaver being proposed where there are dyes and no silk.

**D. A building the ground cannot hold is not an answer either.**

`can_build_building` in the *location's* scope: the rank, the terrain and the
building's `location_potential`, and never an advance. Asked of every method, in
the plan and in the ranking alike.

**E. Comparing two different goods needs one more step.**

`worth` is in units of the good — 1.0 of lumber against 0.2 of wine — so it
compares two *locations for one good* and nothing else. For the plan, each good
is divided by its own best over the chosen ground:

```
fit(good, location) = worth(good, location) ÷ best worth of that good anywhere here
```

1.00 where the good most belongs, and every good peaks at 1.00. **This is the
one step with no evidence behind it** — it is a choice, not a measurement, and
the alternative worth arguing about is in the open questions below.

## Part two: what the ground can hold

Hard rules, none of them negotiable, all of them the game's:

1. **One building of a type per location.** A building runs one method, so two
   goods off one `market_village` cannot both be made in one village — but the
   next village along may take that building on another method.
2. **A location's rank decides which buildings may stand there.** Thirty
   production buildings declare `rural_settlement`; only four are villages.
3. **`can_build_building`**, per D above.
4. **The player's cap** — buildings per rural location, per town — which is a
   house rule, because the game exposes no slot count at all.
5. **An urban right is a town's whole answer**, two or three goods at once, and
   its bonus obliges all of them to be made there. All or nothing.

## Part three: who gets the ground first

This is the half that is a proposal. In order:

| tier | who claims | why |
| --- | --- | --- |
| 0 | **what the player asked for by hand** | «этому товару нужно больше места» — not built |
| 1 | **urban rights**, in towns, whole bundles only | the largest bonus in the game, and it decides a town's whole list |
| 2 | **goods that almost nowhere can hold** | iron without an RGO is one building wanting wetlands; where it can go at all, it must |
| 3 | **everything else, by fit, round by round** | every good takes one location a round, best fit first |

Tier 2 is graded rather than binary: the sweeps run at 1, 2, 4, 8, 16 candidate
locations and then everything, so scarcity is a slope and not a cliff. Rounds
inside a tier continue until one adds nothing, so nothing the ground can feed is
left empty.

**Within a tier the order is still the goods list's**, which is arbitrary. The
fix is regret — `fit(best) − fit(second best)`, the good with the worst
alternative picking first — and it is unbuilt and unmeasured.

## What only the owner can settle

- **Is `fit` the right cross-good measure?** It says "this location is as good
  for wine as that one is for lumber, relative to each good's own best". The
  alternative is a *market* measure — output × price — which would rank a
  province by money and let expensive goods outbid cheap ones. He ruled the
  market out for demand; this is a different use of it and may be the honest one.
- **Is all-or-nothing right for a right?** Westphalia produced exactly one right
  under it. The alternative is to grant a right where most of the bundle fits and
  leave the gap to ordinary goods, which is what the thirty-first load did and he
  rejected.
- **How much is an RGO already on the ground worth against a building?** It is
  supply that already exists, and the plan does not count it at all yet.
- **What does "равномерно" mean when the ground is small?** «Я не должен забить
  всё девятью видами товаров» — but nine is what three provinces at three
  buildings a location comes to. The tension is real and the answer decides
  whether the cap or the spread gives way.

## What is already true of the code

Everything in parts one and two. Part three is built as tiers 1–3; tier 0 is not.
The state, the effects and the window are described in
[`whole_map_plan.md`](whole_map_plan.md).

# The whole plan: every building, placed once, over one stretch of ground

**This is what the mod was built for**, in the owner's words on 2026-08-31, and
everything before it — the per-province answer, the three ages, the two «Считать»
buttons, the market picker — exists so that this can be right rather than
plausible.

## What he asked for

> Добавить возможность отмечать несколько нужных товаров/прав или вообще все
> сразу и видеть, какие провинции становятся «магнитами» для слишком большого
> числа зданий.

And how it is meant to be played:

> Я создаю изначальную карту со всеми запланированными зданиями сразу. Далее
> смотрю какой товар в дефиците — иду смотрю именно на этой карте где лучше
> воткнуть этот товар, чтобы не помешать другим зданиям в будущем.

So the plan is not a report, it is a **standing plan** the player consults when
the game asks a question. The shortage is read off the game's own market panel
(«Local balance», [`market_truth.md`](market_truth.md)); the plan says where that
good goes without spoiling the rest.

## The five answers, 2026-09-01

The design questions this file used to end in are answered. Verbatim where the
wording decides something.

1. **The cap is per location, not per province, and there are two of them** —
   one for rural locations, one for urban, because «количество вмещаемых линеек
   домиков в сельских и городских местах может сильно отличаться». Both are set
   in the game: «я поставил для одних 3, для других 4 — сделали расчёт».
2. **Best percentage first, and a filled province drops out for everyone else**,
   with urban rights placed before ordinary goods — *his* first guess, offered
   as a thing to test rather than a decision: «это надо тестировать… Предлагай ты
   свои варианты».
3. **No market, no price, no shortage.** «Изначально задача стоит распределить
   равномерно все товары, чтобы производилось всё в достаточном количестве.» The
   only weighting is his own, by hand, afterwards.
4. **RGOs already on the ground are supply, and they buy the plan out of
   building that good** — «если на нашей территории нет этого сырья в РГО» the
   quarries are needed, and if there is, «их нужно урезать». With the exception
   that is the reason the manual weight exists at all: wood, glass, masonry and
   stone are wanted in quantity whatever the ground already gives.
5. **A table and a map.** The table is understood; the map he left open —
   «какие у тебя есть там возможности в плане карты, так что потом разберёмся».

## What the engine allows, checked today

- **There is no building-slot cap in the game to read.** `max_levels` on a
  building is that one building's own ladder (`rural_building_cap = 1 +
  development×0.1 + max_rgo_workers×0.5 + river`, `common/script_values/`);
  nothing anywhere counts *buildings* in a location. So the cap is a house rule,
  it cannot be derived, and the mod's job is to make its consequence visible
  rather than to guess the number — see the capacity line below.
- **The map half is nearly free, because this mod already does it.**
  `bag_wtp_selection.txt` paints the picked ground from a location variable, so a
  second mode painting the plan's load is one more file of the same shape —
  `docs/research/interface.md` for what a mode can and cannot carry.
  Per-location *icons* are not among them: every map marker is a widget the
  engine instantiates against a data context of its own, so a mod may hide and
  show them but never add one. Colour, tooltip and the game's own RGO icons are
  the whole of what the map will draw.
- **CMF has the two settings this needs**: `cmm_register_numeric_setting` for
  the caps, `cmm_register_list_numeric_field` for a number per row of the goods
  list, and `cmm_build_list_field_map` reads the whole column back as a variable
  map keyed by `goods:<good>`. The goods lists are already bool-field lists —
  multi-tick is what they natively are, and this mod suppresses it.
- **`ordered_in_global_list` takes a `limit`**, and vanilla uses it for exactly
  the shape the allocation needs (`situation_effects.txt`: strongest, then
  second-strongest excluding the first). So "this good's best free location" is
  one engine-side sort, not a walk.

## The design that follows

Marked where it is a proposal of ours rather than his answer.

**The score is normalized per good, and that is the one thing that must not be
skipped.** `out × (1 + bonus/100)` is not comparable between two goods — it is
1.0 lumber against 0.2 wine, a units difference — and a plan that ranks
(good, province) pairs on it hands every contested province to whatever good has
the biggest output. Each good is divided by its own best in the chosen ground
instead: `fit = score(province) / score(this good's best province here)`, 1.00 at
its best, self-calibrating, no constant to keep. **Ours.**

**Round-robin, not one sweep.** Every good takes one location, then every good
takes another, and so on until the caps are full. Even distribution then needs no
quota — it is what the rounds do. **Ours.**

**Who wins a province two goods want: the one with the most to lose.**
`regret = fit(its best free) − fit(its second-best free)`; highest regret picks
first in the round. A good with an equally good alternative steps aside by
itself; a good with nowhere else to go keeps the ground. This is the middle of
the two answers his question offered — the loser goes to its next province, but
which one is the loser is decided by what the *pair* costs, not by the bigger
number. **Ours, and the part most worth testing against plain best-percent
first.**

**Urban rights go in a round zero**, before ordinary goods: his answer, and a
right needs a town or city location anyway.

**One building of a good per province, full stop**, so a good's second building
lands in a different province while any is left. Otherwise the best province
takes the same good twice and the plan is a heap again. A good that really wants
two in one province is what the weight is for. **Ours.**

**The manual weight is picks per round.** A number on each row of the goods list,
default 1; stone at 3 takes three locations a round. That is «запросить
увеличение места под конкретный товар», and it is the same number that overrides
the RGO discount.

**RGOs are subtracted from what a good is owed, not from the province's score.**
A good with *n* RGO locations in the ground sits out its first *n* rounds. It is
deliberately not a penalty on the province: the ground that grows salt is often
exactly where a salt works belongs — what the RGO changes is *how many* are
wanted, which is what he said.

**The answer needs no new window.** The plan writes the same location variables
the results window already reads — `bag_wtp_bt`, `_pm`, `_out`, `_bonus`,
`_goods` — so a plan is the existing table, differently chosen, plus the good's
own name on the row and what it displaced. The map mode is a second reader of
the same variables.

**And the plan tab prints its own capacity**: rural locations × rural cap + urban
× urban cap, against the number of goods asked for. That is how the cap gets
chosen — by seeing what it buys — rather than by us inventing an average he can
already estimate better than we can. **Ours, and it is the honest answer to «ты
способен вычислить оптимальное среднее количество линеек».**

## What is built, 2026-09-01, and never loaded

The first slice, and it is deliberately not all of the design above.

- **A «4. Общий план» group** on the same tab as the two «Считать» buttons:
  «Зданий на сельскую локацию» (3), «Зданий на город» (4), «Зданий на товар» (3),
  and two buttons — «План» and «Открыть».
- **The pass**, `bag_wtp_generated_plan.txt`: one `bag_wtp_score_<g>` per good
  over the picked ground, harvested into `_p<g>`, each good divided by its own
  best here, then rounds of `ordered_in_global_list ... max = 1` — one location
  per good per round, never twice in a province, never past a location's cap.
- **A window of rows by load**, busiest first, each naming the location, its
  province, what it already digs up and the goods the plan gives it.
- **A map mode**, «Где производить — план», in the Economy category: green at
  one building, red at four, pale where the plan passed over.
- **Five numbers on the button and in the window**, counted by the pass itself,
  because an effect that does nothing logs nothing: locations considered, room
  in them, goods this ground can make, buildings placed, locations used.

**Not built, and named here so nobody looks for it:** the per-good weight, the
RGO discount, regret ordering, and choosing which goods to plan — the plan
always plans all 47. Each of those changes what a good is *owed*, and none of
them can be judged before the base distribution has been seen once.

**What the first run has to answer, in order.** Whether the button returns at
all, and how long a small ground takes — start with one area, then a region,
because the pass reads 241 recipes on every location against a ranking's five.
Then whether «мест» against «товаров» makes the caps choosable. Then whether the
spread looks like a plan or like a heap.

**And the one thing known to be arbitrary**: within a round the goods are served
in a fixed order. After normalization every good's first choice is worth exactly
the same, so round one is a genuine tie and any order is as good as another —
but from round two on, fixed order quietly favours the goods that come first.
That is what regret ordering is for, and it is the next thing to build.

## Still open

- Whether the RGO count is over the planned ground only or the country too.
  Default proposed: both, since «наша территория» was his phrase.
- Whether regret ordering beats plain best-percent-first. One run with each,
  same ground, is the test.
- The map mode's colouring: by planned good (47 colours, unreadable) or by load —
  how many buildings a location took against its cap, which is «магнит» drawn
  directly. The second, first.

## The trap this must not walk into

**A whole feature finished before its first load is how `where_to_produce` ended
up with six suspects and no way to choose between them** — the rule at the top of
`CLAUDE.md`, earned here. So the first thing built is the smallest piece that
shows a signal, and the signal wanted first is the cost: scoring every good over
the picked ground is 218 method readings a location where one good is about five,
and whether that survives a button press is not knowable from here.

# The plan's formula: what a building is worth, and who gets the ground first

**The owner answered the four open questions on 2026-09-01** and sent the plan's
own screenshot with them: «довольно плохо». His answers and that screenshot point
at the same thing, so this file is no longer a proposal — it is the formula,
derived, with the three measurements that force its shape.

## The three measurements everything follows from

**1. The RGO bonus is a ten per cent band, and nothing more.**

```
worth = output_per_level × (1 + bonus/100),   bonus ∈ [0 … 10]
```

So two locations that can run the *same* method differ by at most 10%, and
because `generate.fed_floor` refuses anything under half a recipe's ceiling, in
practice by about 5%. Measured over all 47 goods: a completely unfed building
scores **0.909 to 0.980** of a fully fed one.

**This is the fact the old formula got wrong.** `fit` divided each good by its
own best on the chosen ground, which squeezes every good into 0.909–1.000 and
leaves the outcome to be decided by the goods list's arbitrary order. The
screenshot is that: six villages of Paderborner Plateau, one after another, each
handed the same three buildings.

So **the bonus is a tie-break, not a ranking.** Any decision the plan makes on a
margin wider than ten per cent has to come from somewhere else, and the rest of
this file is where.

**2. An urban right is worth two to five times the bonus.**

Ten rights grant output, and the grants run `+0.2` to `+0.5` — twenty to fifty
per cent, on two or three goods at once, where the whole RGO ceiling is ten. That
is not a preference, it is the arithmetic: **a right outranks every other
consideration in a town.** It also settles the owner's answer 2 objectively.

**3. Buildability is binary, huge, and lands almost entirely on the raw goods.**

Of the 110 production buildings the mod uses, **25 carry a `location_potential`,
and they are nearly all the RGO-side ones** — pits, quarries, farms, villages,
plantations. The manufacturing ladder (guild → workshop → manufactory → mill)
gates on the location's *rank* and on nothing else.

Two consequences. Scarcity is a real constraint for raw goods and essentially
none for made goods, which is what the tiers are for. And **the game already
refuses to duplicate an RGO**: `clay_pit` carries `NOT = { raw_material =
goods:clay }`, `stone_quarry`, `sand_pit`, `fiber_crops_farm` and
`bog_iron_smelter` the same. Part of the owner's answer 3 is therefore enforced
by the engine before the plan is asked.

## The formula

For a good `g` in a candidate location `L`, in the province `P` that holds `L`:

```
admissible(g, L)  =  can_build_building(best method's building, L)
                  ∧  bonus ≥ fed_floor(method)
                  ∧  L does not already hold that building type
                  ∧  load(L) < cap(L)

worth(g, L)       =  output × (1 + bonus/100)                      ≤ +10%

priority(g, L)    =  worth(g, L) ÷ (1 + already(g, P))

need(g)           =  max(1, round(quota × weight(g)) − rgo(g))
quota             =  capacity_left_after_rights ÷ (goods with any admissible L)
```

`already(g, P)` is how many of that good the plan has already put in this
province; `rgo(g)` is how many locations of the ground already yield it as an
RGO; `weight(g)` is the owner's own knob, 1 by default.

**The divisor is the whole of the fix for the screenshot.** Every location of a
province is worth exactly the same to a good — the bonus is a
`province_definition`'s property — so with no decay a good takes *all* of its
best province before touching its second best, and every location of that
province comes out identical. Halving, thirding and quartering makes the second
building look elsewhere unless this province is twice as good, and nothing here
is ever twice as good (measurement 1). It is one divide and one counter per good
per province.

**The quota is what «равномерно» means, at both scales.** Small ground — three
provinces, twenty-seven rooms, forty goods — gives a quota under one, so every
good takes exactly one place and the ground comes out mixed rather than
specialised. Large ground gives a quota of twenty-five, so each good takes its
twenty-five best places, which are the ones its raw materials are under, and
stops; the free rooms left over are what the goods with no bonus anywhere fill.
That is his answer 4 in one line, and it needs no separate rule for either case.

## Who claims the ground, in order

| tier | who claims | why |
| --- | --- | --- |
| 0 | **what the owner weighted by hand** | his `weight(g)`, and the only place a preference enters |
| 1 | **urban rights — every town, mandatory, whole bundle** | +20…50% against a +10% ceiling |
| 2 | **goods few locations can host**, sweeps at 1, 2, 4, 8, 16 candidates | bog iron has one building and it wants wetlands |
| 3 | **everyone else, round by round, to `need(g)`** | the quota above |
| 4 | **the rooms still empty, quotas lifted** | nothing the ground can feed is left out |

**A right is granted whether or not its bundle fits.** That is the owner's
answer 2 and it reverses what the code does today: «каждому городу будет выдано
наиболее подходящее ему право. Оно БУДЕТ выдано ОБЯЗАТЕЛЬНО. И каждый такой
город обязательно получит все здания из его бонуса.» Which right is still asked
of the town — the bundle's own scores added up, among the rights the country's
`potential` allows — but the answer is now always granted, and its buildings are
placed before anything else in that town. Today's `_plan_right_fits_<k>` gate is
why the screenshot granted **one** right across six towns.

**And a right's building can be evicted, in exactly one case:** one that earns no
bonus at all, displaced by a tier-2 good with nowhere else to go or by a
hand-weighted one. His words: «какое-то здание из городских прав, которое не
получает бонусов от рго — может быть вытеснено».

## The four answers, as given

1. **No money.** «Считать в деньгах не нужно. Дешёвые товары зачастую не менее
   важны чем дорогие.» Price never enters the plan. `worth` stays in units of the
   good and goods are made comparable by the quota, not by a price.
2. **Rights are mandatory and whole**, as above. He wants the caps tried at 3, 4
   and 5, because he does not know whether an ordinary town holds more than three
   full ladders once the third and fourth ages grow them.
3. **One RGO counts as one building.** «Рго это по сути та же линейка здания… 1
   рго ты можешь рассматривать как один домик локации. Допустим ты хочешь
   добывать глину 5 домиками на области. Смотришь что там уже есть 2 рго глины —
   соответственно тебе нужно уже всего 3 домика.» So the discount is in *count*,
   not in units: `need(g)` less `rgo(g)`. His earlier exception stands — wood,
   glass, masonry and stone are wanted in quantity regardless, which is what
   `weight(g)` is for.
4. **«Равномерно» is the quota**, and it is scale-free, as derived above.

## What is not settled

- **`town_right_efficiency_penalty`** sits in eight of the ten output rights and
  in no file `reference/` holds. If it penalises the goods *outside* the granted
  bundle, then "a right decides a town's whole list" is mechanical rather than
  advisory, and the eviction rule above is wrong. One `grep` on the owner's
  install — it is already on the list in `NEXT_SESSION.md`.
- **Ordering inside one tier** is still the goods list's. The decay divisor takes
  most of the sting out of it, since a good that has just placed drops behind the
  ones that have not; whether regret ordering adds anything on top is a question
  for after the first run with the decay in.
- **The cap is a house rule.** The game exposes no building-slot count at all
  (`whole_map_plan.md`), so 3/4/5 is his to try and the plan's job is to make the
  consequence legible.

## The rollback of 2026-09-02, and what survives it

**The tree is back at the build the thirty-sixth run praised** — «Вау, оно кажется
даже адекватно работает». Everything built above it that day was undone at the
owner's word: «лучше мы решим уже на том моменте основную мучающую проблему, чем
будем делать это после того как накрутили сверху множество других неработающих
правок». So everything above in this file is the code again, exactly.

**What the undone day still knows, and no run should buy twice:**

- **The owner's rule about raw materials.** It is a decision, not a build, so it
  outlives the code that carried it:
  > Отсутствие сырья не должно влиять на то будет ли домик существовать вообще
  > или будет ли он как-то смещён в очереди из-за этого. Отсутствие сырья может
  > влиять только на ВЫБОР метода производства в конкретном домике.

  **The formula above breaks it in one named place**: `fed_floor` sits inside
  `admissible`, so a recipe this ground feeds nothing is refused outright rather
  than merely valued at nothing. That is left standing on purpose — it is a
  suspect for the symptom below, and a suspect is not fixed before a probe names
  it.
- **The symptom that outlived every fix, and is the whole of the job now.** The
  plan will not put glass in a *town*; it puts it in villages freely.
  `glass_guild` and `rural_glassmaker` carry the **identical**
  `location_potential = { is_produced_in_location_market = goods:sand }`, so the
  market gate cannot be what stops it — one condition is not true and false in
  one market. Four theories about it were wrong on four of the owner's runs:
  [`../pitfalls/diagnosis.md`](../pitfalls/diagnosis.md).
- **What was built on top and is not in the tree now**, so that none of it is
  re-derived and none of it re-applied before a run asks for it: the currency
  changed to `gain = bonus ÷ that recipe's own ceiling`; the unfed divisor, added
  with it and struck out again; the input substitution, which planted sand where a
  granted charter wanted glass and spammed a realm with charters; a right scored
  on the bundle its town can actually finish; the round guard. The rollback also
  puts back the three faults the thirty-sixth run named — the side-blind goods
  count, the open pass lifting a quota instead of raising it, and identical towns
  all taking the same right — each written out under that run in `TESTLOG.md`.

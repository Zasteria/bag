# The plan's formula: what is being maximised, and how the ground is dealt

**Rewritten 2026-09-01, when the owner stated the objective outright.** Before
this the file was a pile of rules; it is now a derivation, because he said what
the plan is *for* and everything follows from that.

> Товары будут добываться все которые только можно добыть, но распределение их
> должно быть такое, где максимально возможная часть получит свои «плюшки», а
> другие получат чуть меньше или вообще не получат.

That is an optimisation problem with a covering constraint, and it has one
answer.

## The problem, exactly

Over the chosen ground, choose a building for every slot so as to

**maximise** the total bonus captured,

**subject to**, and none of these are negotiable:

1. **every good the ground can produce gets at least one building.** «Все товары
   которые можно произвести на выбранной земле — должны производиться, все. И не
   важно есть для них сырьё на этой земле или нет.» Coverage is a hard
   constraint, not a preference;
2. one building of a type per location, and `can_build_building` must allow it;
3. `load(L) ≤ cap(L)`, the owner's house rule — the game exposes no slot count;
4. every town takes its best urban right and its whole bundle is placed there.

## The currency, and why it is not what the file used to say

**A raw bonus does not compare across goods.** Measured over all 47: the ceiling
a good's best recipe could ever reach runs from 2.00% to 10.00%, and five goods
are capped under 5%. A good that can never earn more than 2% will lose every
comparison against one that can earn 10%, and that is not a reason to build it
somewhere worse.

**A normalised `worth` does not compare either, and that was the older mistake.**
Dividing each good by its own best *on this ground* squeezes everything into
0.909–1.000 — because the bonus is only a ten per cent band — and then the
outcome is decided by the goods list's arbitrary order. That is what produced six
identical villages on the thirty-fourth run.

What compares is **how much of what this good could ever get here, it gets**:

```
gain(g, L)  =  bonus(g, L) ÷ ceiling(g)          ∈ [0, 1]
```

1.00 means "the ground feeds this recipe completely". 0.00 means "it feeds it
nothing", which is still a building the plan must place. **The objective is
Σ gain over every building placed**, and no price, no output size and no
per-good divisor enters it. It is the honest reading of «свои плюшки».

## The one insight that makes the deal optimal

The failure mode is greed, and the owner named it: «дальше не жиреть». If every
good takes its own best location in turn, the good that would gain 0.9 there and
the good that would gain 0.1 there compete on equal terms, and whichever the list
reaches first wins. Total gain is thrown away for nothing.

The fix is opportunity cost — place a good where what it gains most exceeds what
it displaces — and the cheap way to get it is **not** to compute it per location.
It is to deal the ground in descending order of gain, across all goods at once:

```
for band in 1.0, 0.9, 0.8, … 0.1, 0.0:
    for each good, scarcest first:
        if it is still under its quota:
            take its best free location whose gain ≥ band
```

By the time a good with gain 0.2 reaches a location, every good that would have
gained 0.9 there has already taken it. **The ordering is the opportunity cost**,
and it costs one comparison on a walk that already happens.

Three things the owner asked for fall out of it without a rule of their own:

- **the best bonuses are taken first**, whichever good they belong to;
- **a good that gains nothing anywhere places only in the last band** — that is,
  in the ground nothing else wanted. «Выделить у менее вкусных провинций место
  под всё остальное»;
- **nothing is left to the goods list's arbitrary order** except among placements
  of genuinely equal gain.

## The rest of the deal, in order

| # | pass | why |
| --- | --- | --- |
| 0 | **what the owner weighted by hand** | his knob; not built |
| 1 | **urban rights**, every town, whole bundle | the largest number in the game — see below |
| 2 | **the bands**, 1.0 down to 0.0, scarcest good first inside each | the objective |
| 3 | **coverage**, any good still at zero takes any free slot | constraint 1, guaranteed |
| 4 | **surplus**, quotas raised a layer a round until nothing is added | fills the ground evenly |

**Pass 3 is the guarantee and it is not optional.** A good that lost every band —
because rights took the towns, or because it gains nothing and the ground filled
— still gets one building. Until this exists the plan does not meet his first
requirement.

Two dampers keep a pass from stacking:

```
priority(g, L)  =  gain(g, L) ÷ (1 + already(g, province of L))
quota(g)        =  max(1, capacity ÷ |goods| − rgo(g))
```

The divisor is because **every location of a province is worth the same to a
good** — the bonus is the province's — so undivided, a good takes its best
province whole. The quota is «равномерно» and is scale-free: three provinces give
a quota under one, so everything is covered once and mixed; a large realm gives a
quota of twenty-odd, so each good takes its best twenty-odd places and stops.

## Urban rights, and why they are their own pass

A right is a `location_modifier` on the town:

```
royal_masonry_rights = {
    location_modifier = {
        local_masonry_output_modifier = 0.25
        local_glass_output_modifier   = 0.25
        local_production_efficiency   = town_right_efficiency_penalty
    }
}
```

So it is **two things at once**, and the owner had it right: «права дают слишком
жирный бонус и дебафят всё остальное». The bundle's goods get +20% to +50% output
where the whole RGO ceiling is 10%; and *everything else in that town*, bundle
included, takes a blanket production-efficiency penalty.

Two consequences, and the first is a hard one:

- **a town holding a right should hold its bundle and as little else as
  possible.** A non-bundle building there earns the penalty and none of the
  bonus, so the same building is strictly better in a town without a right. The
  bands must therefore discount a right-holding town's leftover slots;
- **rights are worth more than anything the bands can find**, by a factor of two
  to five, which is why they are dealt first rather than competing.

**`town_right_efficiency_penalty` is a define and it is not in `reference/`** —
only its eleven uses are. The structure above is certain; the number is not, and
it is one `grep` on the owner's install. Until then the discount above is a
direction without a size.

## What the owner's own play says, and where it differs

He described it himself, and marked it as his habit rather than as correct:
province by province, the top three buildings by local bonus in the town, then
the same in the countryside, then a rural location set aside to feed the
province; iron and its like displace a top-three building where nowhere else will
hold them; and when a right arrives, its bundle replaces the three.

**The problem he cannot solve by hand is the one the formula exists for.** Doing
it province by province maximises each province in isolation, and the goods that
gain nothing anywhere are left with nowhere at the end — «а вдруг у меня вообще
нет каких-то РГО, например того же песка?». Dealing in bands over the whole
ground is the same greed, ordered globally instead of locally, and that is
precisely the difference between his hand play and an optimum.

**Not yet in the formula and named by him:** a rural location per province set
aside for food. He said «до этого мы пока ещё не дошли».

## What only a run can settle

- the value of `town_right_efficiency_penalty`, and therefore how hard the bands
  should discount a right-holding town's spare slots;
- whether a cap of 3 is right, which is why he asked for 3, 4 and 5;
- whether the bands want ten steps or four — a band costs a sweep.

## The rollback of 2026-09-02, and what survives it

**The tree is back at the build of the thirty-eighth load** — the four tests the
owner called «большой рывок», and the first time the spread of goods over a whole
ground looked to him the way he had meant it: «именно в этом коммите я
почувствовал, что мод выглядит так, как я его задумывал». Everything built above
it was undone at his word — «лучше мы решим уже на том моменте основную мучающую
проблему, чем будем делать это после того как накрутили сверху множество других
неработающих правок» — so everything above in this file is the code again,
exactly. The run itself is in [`../archive/testlog_2026-08.md`](../archive/testlog_2026-08.md).

**Open at this point, and he named all of it himself:**

- **a big ground does not finish.** All of northern Germany: 970 buildings in 354
  of 416 locations, «мод не справился досчитать всё как надо». The cause was
  measured afterwards and the arithmetic is not in doubt — a sweep places at most
  one building per good per side, so 970 buildings over 32 goods needs thirty
  sweeps at the least, and `PLAN_ROUNDS` is 12 here;
- **«показано всего 150 локаций»** is `PLAN_ROWS`, the window's row cap, not the
  count of what the plan used. Nothing is lost, only undrawn, and the header does
  not say so at this point;
- **the province ceiling setting is still here**, and he asked for it to go: «я не
  представляю ситуацию, когда бы я мог захотеть сменить значение этой строки с
  0». Under this formula the quota does that job and is derived rather than typed;
- **a one-off spike and a short hitch on «Пересчитать»** over that ground,
  reported without complaint: thirty-three passes and ninety-eight sweeps a plan;
- **the symptom that is the whole of the job.** Force a province to towns and
  glass lands in the villages below and never in those towns, while saltpetre and
  clay — which a village could dig — take the town slots. And the glass-and-
  masonry charter is handed out over and over.

**What the undone runs still know, and no run should buy twice:**

- **The owner's rule about raw materials**, 2026-09-01. A decision, not a build,
  so it outlives the code that carried it:
  > Отсутствие сырья не должно влиять на то будет ли домик существовать вообще
  > или будет ли он как-то смещён в очереди из-за этого. Отсутствие сырья может
  > влиять только на ВЫБОР метода производства в конкретном домике.

  **`UNFED_PENALTY` above breaks it** — a recipe the ground feeds nothing is
  divided by two on top of a `gain` already zero, the same fact counted twice, and
  it moves that building in the queue. It is left standing on purpose: it is a
  named suspect for the symptom, and this repository does not fix a suspect
  before a probe points at one. (`fed_floor` is *not* a gate in the plan here —
  the plan keeps an unfloored twin of every side, so that part of the rule already
  holds.)
- **The observation that killed the market theory**, thirty-ninth load. It is
  about the game, so it stands whatever our code does: `glass_guild` and
  `rural_glassmaker` carry the **identical** `location_potential = {
  is_produced_in_location_market = goods:sand }`, and glass appears in the
  villages while never appearing in the towns. One condition is not true and false
  in the same market, so the market gate is not what stops town glass — and four
  sessions' worth of explanation went with it
  ([`../pitfalls/diagnosis.md`](../pitfalls/diagnosis.md)).
- **What was built above the rollback and is not in the tree.** Three of these
  answer measurements he made himself and can be ported back on their own the
  moment he asks: the round guard at 50 with the tier ladder in the last band only
  (twelve passes rather than thirty-three), the province ceiling removed, and the
  header saying «показано N» beside the number the plan really used. The rest were
  aimed at a cause nobody had named: a right-holding town's spare slots halved,
  the input substitution (sand planted where a charter wanted glass, which spammed
  a realm with charters), the rescored rights, and `UNFED_PENALTY`'s own removal.

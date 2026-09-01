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

## The design, as the twenty-eighth run left it

Marked where it is a proposal of ours rather than his answer.

**The plan is chosen per province and spent per location.** The first build chose
a location at a time, and that was the wrong unit: he plays a province as a
specialisation — «вся сельская местность в одной провинции в большинстве случаев
получит линейку домиков одинаковую» — while a rule of one building per good per
province produced the exact opposite. So a province takes two short lists, one
for its towns and one for its villages, each as long as that side's cap, and
every location of it then builds its side's list entire. A province reads as one
answer, its villages repeat each other, and what differs is the ground.

**A list entry is a building, not a good.** A location holds one building of a
type and a building runs one production method, so tools, jewelry and beer —
`market_village` all three — are one answer and not three. That was the
thirtieth load's finding, his: «по сути все три этих товара даёт одно и то же
здание». The province's list carries the building beside the good, and a good
whose winning building is already there is not an answer. **His.**

**And the two sides are "where may this stand", not "is it a village".** The
ranking's village side is `village_category` — four buildings in the game. Thirty
production buildings declare `rural_settlement = yes`, and the other twenty-six
are the stone quarries, clay pits, lumber mills and masons he expected to see in
the empty slots. The plan splits on the building's own rank gates instead, which
takes a rural location from 4 buildings to 30. **Ours, and it is the reason the
plan's scoring has accumulators of its own rather than reusing the ranking's.**

**And the province's state lives on its locations, mirrored.** The
twenty-ninth load placed nothing out of 381 places and logged not one line: the
lists were kept on the `province_definition`, which is static map data and holds
no variable (`PITFALLS.md`). Every condition the allocation asks is a plain read
off the candidate in hand now, which is also cheaper than the province hop it
replaced.

**Which locations count as towns is the player's to override.** The game's rank
is only what is true today, and the mod cannot guess which village he means to
raise; a button on the plan's own rows cycles town → village → the game's answer,
and no plan run clears it. **His, and the reason it is a button and not a
guess.**

**The score is normalized per good, and that is the one thing that must not be
skipped.** `out × (1 + bonus/100)` is not comparable between two goods — it is
1.0 lumber against 0.2 wine, a units difference — and a plan that ranks
(good, province) pairs on it hands every contested province to whatever good has
the biggest output. Each good is divided by its own best in the chosen ground
instead: 1.00 at its best, self-calibrating, no constant to keep. **One divisor
for both sides**, so a good worth five times as much in a town as in a village
still says so. **Ours.**

**Round-robin, and it runs until the ground is full.** Every good takes one town
list and one village list, then every good takes another, until a whole sweep
adds nothing anywhere. Evenness needs no quota — it is what the rounds do — and
**a location the plan can feed is never left empty**: his ruling, and the reason
the fixed round count is gone.

**Urban rights are a province's town list, and they are chosen first.** A right
is a bundle of two or three goods, which is the shape of a town list, so a right
does not compete with goods for slots — it takes the list whole. **Which right a
province gets is asked of the province, not of the rights**: there are twelve and
rarely that many provinces, so letting rights take turns would decide the outcome
by turn order alone. A right's worth on a province is its bundle's own normalized
scores added up, which costs no pass — the goods were scored anyway. Behind a
switch, on by default. **Ours, bar the priority and the switch, which are his.**

**What a good is owed is still flat.** No market, no price, no shortage — his
answer. The one ceiling is «не больше стольких провинций на товар», off by
default.

**The answer is a table and a map.** Rows are locations, ordered by province:
provinces by how much the plan put in each, their locations together, towns
before villages. The map mode paints **completeness** rather than crowding —
green where a location is filled to its cap, red where the plan put nothing —
because under the province model a full location is the normal case and the
interesting one is the ground that could not feed a whole list.

## What is built, and what is not

Built 2026-09-01, loaded once as the location-at-a-time version, and rebuilt to
the above the same day:

- **«4. Общий план»**: goods per rural location (3), per town (4), at most this
  many provinces per good (0 = no ceiling), a switch for urban rights, «План» and
  «Открыть».
- `bag_wtp_generated_plan.txt` — the scoring harvest, the rights round, the
  sweeps, the build onto locations and the ranking.
- A window of locations by province, and a map mode painting completeness.
- **A summary line of seven counters**, written by the pass itself and ordered
  so that the first zero names the step that failed — locations, towns among
  them, provinces, room, goods, list entries, buildings. An effect that merely
  does nothing logs nothing, and this is what buys a diagnosis without a zip.

**The demand knob, proposed and not built.** «Я выбираю товар и щёлкаю +1 и план
смещает» — under the province model that is a **floor in provinces**: a number
per good on the goods list, and before rights or any sweep each good with a
demand of N takes its N best provinces on whichever side suits it. It is one
`cmm_register_list_numeric_field` and one round, and it is held back on purpose
until the building rule has been seen once: it would move the whole distribution
again and make the next screenshot unreadable.

**Not built besides:** the RGO discount, and choosing which goods to plan — the
plan always plans all 47. **And not asked: whether a location can actually hold
what its province's list says.** The rank gates are in now, but terrain and a
building's own `allow` are not, so two locations of a province are still assumed
interchangeable.

## Still open

- Whether the RGO count is over the planned ground only or the country too.
  Default proposed: both, since «наша территория» was his phrase.
- **Within a sweep the goods are served in a fixed order.** After normalization
  every good's first choice is worth the same, so the first sweep is a genuine
  tie and any order is as good as another — but from the second on, fixed order
  quietly favours the goods that come first. Ordering them by regret
  (`best − second best`, so the good with the worst alternative picks first) is
  the fix, and it is worth one run against the plain order before it is built.
- Which right a province was given is not shown; the bundle's icons are the only
  sign of it. A name would want a `customizable_localization` switching on the
  index.

## The trap this must not walk into

**A whole feature finished before its first load is how `where_to_produce` ended
up with six suspects and no way to choose between them** — the rule at the top of
`CLAUDE.md`, earned here. So the first thing built is the smallest piece that
shows a signal, and the signal wanted first is the cost: scoring every good over
the picked ground is 218 method readings a location where one good is about five,
and whether that survives a button press is not knowable from here.

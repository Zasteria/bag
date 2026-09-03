# Town rights, and how `where_to_produce` should score them

The owner asked for Городские права: a location can be granted an urban right
that trades a small penalty on all its production for a large bonus to one
bundle of goods, and he wants the mod to find the best ground for the bundle.

Written before any of it was built, because the arithmetic decides the shape and
two of the four numbers people assume are wrong. The output half is built now
and has never been loaded; the level half is deferred. `common/town_rights` is in
`reference/` since 2026-08-31 — the owner copied it in by hand after `mods.bat
→ 2` turned out not to re-extract the game.

## What the seventeen production rights actually do

`python3 tools/api.py --find town_rights` for the engine side;
`reference/game/in_game/common/town_rights/` for these.

| right | what it grants |
| --- | --- |
| `royal_tooling_rights` | tools +30% |
| `royal_masonry_rights` | masonry +25%, glass +25% |
| `royal_naval_rights` | naval supplies +30%, tar +30% |
| `royal_textile_rights` | cloth +20%, fine cloth +20%, dyes +20% |
| `royal_book_rights` | paper +20%, books +20%, dyes +20% |
| `royal_weaponry_rights` | weaponry +20%, firearms +20%, cannons +20% |
| `royal_artisan_rights` | furniture +20%, pottery +20%, leather +20% |
| `royal_brewing_rights` | liquor +20%, beer +20%, wine +20% |
| `royal_jewelry_rights` | jewelry +20% **and** jewelry guild +10 levels |
| `constantinopolitan_silk_monopoly_rights` | silk +50%, cloth +25%, fine cloth +10% |
| `scandinavian_tar_privileges` | tar +20%, naval supplies +20% |
| `scandinavian_bergslag_privileges` | tools +10% |
| `flemish_cloth_industries_right` | cloth guild +5 levels, fine cloth guild +5 |
| `staple_port`, `market_charter`, `lubeck_town_rights`, `stapelrecht_town_rights` | marketplace +3…+10 levels — trade, not production |

Eleven of them also carry `local_production_efficiency =
town_right_efficiency_penalty`, which is **not defined anywhere in
`reference/`** — referenced by the rights and by nothing else we hold.

All nine general ones come from one advance, `town_rights_enable`, in
**age 3 (Discovery)**. That is the same shape as a production method's gate, so
the mod's `bag_wtp_avail_*` machinery covers it with nothing new.

## The three things that are not obvious

**1. A right's percentage cannot re-rank anything.** `+20% books` is the same
+20% in every location in the world. Multiply every candidate by 1.2 and the
order is what it was. The same goes for the efficiency penalty: one constant,
shared by eleven rights, applied to every candidate equally. So a mod that
"takes town rights into account" while still answering for one good has done
nothing at all — a whole feature that changes no answer.

**What re-ranks is the bundle.** Eight of the nine general rights cover two or
three goods, and a province's RGO bonus is *per good*: it can supply lumber and
not dyes. So «where do I put Printing Rights» is a real question with a
different answer from «where do I make books», and it is the only question here
worth a pass.

**2. Adding a bundle's goods needs their prices.** Four books a level and 0.3
masonry a level are not addable; that is the same mistake as ranking a forest
village above a weapon guild, which cost the ninth run. `common/goods` carries
`default_market_price` — books 3, paper 2, fine cloth 6, masonry 1, glass 3 —
and the bundle's score is

    Σ over the bundle:  price × output × (1 + right_output) × (1 + rgo_bonus/100)

`right_output` is in there for completeness; being constant it changes no order,
and it is what makes the number readable as "what this ground would earn".

**3. A level right is a different unit, and the mod refuses to add it to the
others.** Settled 2026-09-02: score a right by *which goods it favours* and never
by the size or the kind of the favour, because a building's level cap moves as a
location grows. The arithmetic that was written for the other answer — five levels
against +20%, and the owner's worry about a cap of 3 against a cap of 15 — is in
[`../archive/town_rights_levels.md`](../archive/town_rights_levels.md); it is what
still decides Flemish cloth against royal textile.

## Built 2026-08-31, and running since 2026-09-03

The output half is in — the plan grants a charter to every town and puts its
whole bundle up, and the owner has seen it: «города получают права и домики из
прав». It is a third list on the Goods tab, exclusive with the two
goods lists, and **a second window** rather than a third line on the first --
the owner's call, and the right one, since a bundle is a different question in a
different unit. `bag_wtp_generated_rights.txt` holds the list, the per-right
pass and the slot storage; `bag_wtp_right_window.gui` holds the window, which
redeclares nothing the results window already declares.

Three things it does that are worth knowing before reading the code:

- **The pass reuses the per-good scorers.** For each good of the bundle it runs
  that good's existing `bag_wtp_score_<n>`, keeps the better of the built-up and
  village answers in a slot, and adds `price × (1 + right)` of it to a total.
  The dispatch that turns a winning method into a building, a bonus and a goods
  list runs only for the fifty provinces that take a row -- 218 methods wide is
  far too much per candidate.
- **Three fixed slots, because three is the widest bundle in the game.** Script
  has no list of tuples and the answers are flat variables on the location, so a
  row holds a fixed number of them; an empty slot hides itself on `_r_bt_<k>`.
- **`RIGHT_SCALE` is a tenth of `RANK_SCALE`.** A bundle's total is a sum of
  scaled outputs times prices and runs an order of magnitude higher than a
  single good's -- textile rights with every input present reach 64 680 against
  a method's 4 950 -- and whether the engine's fixed point ends at 21 474 is not
  knowable from here. At a tenth the worst case is 6 468 and the smallest
  difference the bonus can make is still about 4.6.

Each window draws its own global list, filled only for the question that was
asked. Both are scripted widgets and neither ever comes down, so pointing both
at one list would keep fifty rows of each alive at all times; as it stands the
closed one's datamodel is empty and the two come to 315 static widgets between
them.

**The one guess in it** is `town_rights_type:<key>` as a value a CMM list item
can hold. The game's own script writes `has_town_rights =
town_rights_type:flemish_cloth_industries_right` and the engine dump lists
`town_rights_type` as an event target, so it should store; if it does not, the
list registration is where `error.log` will say so.

## Five things read off the files on 2026-09-02

Read rather than remembered, because the owner asked to be checked against the
game and not believed: «я могу ошибаться и в целом работаю из условностей
воспоминаний».

- **There are 41 rights in the game and the mod scores 12** — `output_rights()`
  keeps only those that raise an output. Everything else is levels, marketplaces
  or population, and is not offered at all.
- **Every country-specific right is `kept_at_conquest = no`. The nine general
  Discovery ones carry no such line, so they are kept.** That matters for this
  mod more than for the game: it plans ground you have not taken, and a right on
  ground you conquer is gone the moment it is yours. You can grant it again if
  you pass its `potential`, which is what the plan already checks.
- **Flemish cloth and `royal_textile_rights` are mutually exclusive**, and the
  game says so itself — both `allow` blocks name the other. So «which of them has
  priority» is not a question the game answers; it only forbids the pair **in one
  town**, and the choice is the player's. **`scope:target` there is the town and
  not the country, and reading it as a country rule cost two charters.** Eight
  pairs in the game carry such an `allow`; derived as «the country grants the
  excluder instead», it took `royal_naval_rights` and `royal_tooling_rights` away
  from every Scandinavian country — in both the window and the plan — in favour of
  the privileges that exclude them, at +20%/+20% and +10% against +30%. Fixed
  2026-09-03: the plan grants a town one right, so no pair can bind on it, and the
  single preference the mod holds is written down as one (`PREFERRED_RIGHT`).
- **The per-location limit is a modifier, `local_possible_town_rights`**
  («Определяет, сколько городских прав может быть у района»). **Nothing in
  `reference/` pushes it**, so the base and any per-rank steps are not knowable
  from here — they will be in `common/defines`, which the manifest does not
  extract. The owner's recollection is town +1, city +1, megalopolis +1, and it
  is his recollection and not a reading. **`capital_possible_town_rights` is
  readable**: four advances grant +1 each — Discovery, Reformation, Absolutism,
  Revolutions — so a capital ends the game with four extra.
- **`town_right_efficiency_penalty` is still defined in nothing we hold** (it
  will be in `common/defines`, which the manifest does not extract). **The owner
  states it as 5%, twice and flatly** — «штраф у всех прав 5%, я тебе это точно
  говорю» — so that is the figure to print if a row ever prints one. **It changes no answer the mod gives**:
  eleven rights carry the same constant, it applies to the whole location, and
  the plan grants a right to every town — so it cancels out of every comparison
  the mod makes. Worth knowing to explain a row, not to compute one.

## The owner's ruling on levels, 2026-09-02

**The mod must never score building levels.** «Мы смотрим на общие ячейки,
каждая из которых линейка в высоту какого-то домика, не важно будет их там 3 в
высоту или 13. Это число непостоянно и все локации растут — высчитывать это
полный абсурд.» So the level half is not deferred any more; it is out of scope by
decision, and `guild_max_level` above is not to be built into a score.

**But he also wants every right usable**: «не важно право это на бонус
производительности или на лимит домиков — все полезны и все по идее должны
использоваться… все права равны должны быть». Those two together point at one
rule, and it is not built: **score every right by how well the ground suits the
goods it favours, whatever kind of bonus it gives** — a level right for cloth and
fine cloth is scored on cloth and fine cloth, exactly like an output right, and
never on the levels. Undecided and his to call.

## The ages, read off the advances on 2026-09-02

They settle a question that had been answered from memory, and the owner's
reading of it was right:

| what | advance | age |
| --- | --- | --- |
| all nine general rights | `town_rights_enable` | **3, Discovery** |
| first firearms building, `hand_cannon_guild` | `hand_cannon_guild_advance` | 1, Traditions |
| first cannons building, `cannon_maker` | `cannon_maker_advance` | 2, Renaissance |
| flemish cloth right | `flemish_cloth_making` | 1, Traditions |

**So «a weaponry right granted where cannons cannot be built» cannot happen in
play**: by the age the rights exist at all, both buildings have been available for
an age or more. His words, and the files agree: «невозможно, чтобы произошёл
сценарий, когда ты выдал права на оружие городу, а в нём невозможно поставить
пушки или огнестрел».

**But the plan could still produce it, and that was a fault of its own.** The
«сейчас» plan handed out rights without asking `town_rights_enable` while refusing
a cannon maker because the country had not taken *its* advance — two different
moments inside one answer: rights as though it were age 3, buildings as though it
were today.

**Decided 2026-09-03, and the rights are gated on the advance.** A plan is an
answer about a moment, and «В конце» is the button that says otherwise; so
`bag_wtp_plan_right_gate_<k>` asks the right's own `potential` always and
`has_advance` unless `_plan_by_end` is set. A country before the Discovery age
now gets a «сейчас» plan with no charters at all, which is the true answer.

**This does not touch the rule above it.** «A right's gate is its `potential`,
never `has_advance`» is about the **list** in the window, which plans ahead and
must not hide a charter you will hold in two ages. The plan for today is the
opposite question and takes the opposite answer.

**One correction to his wording, not to his point.** «Первый уровень» is not free
by default: `hand_cannon_guild` needs an age-1 advance exactly as `weapon_guild`
does, and most production buildings carry one too. What his save shows is a
country that simply had not taken that particular age-1 advance.

## Flemish cloth against royal textile, which he asked to have computed

They are mutually exclusive by the game's own `allow`, so it is a real choice.

- `royal_textile_rights`: **cloth +20%, fine cloth +20%, dyes +20%.** Age 3.
- `flemish_cloth_industries_right`: **cloth guild +5 levels, fine cloth guild +5
  levels**, plus `local_trades_per_burgher +0.25` and merchant capacity +0.25,
  which are trade and not production. Age 1, Dutch culture.

`guild_max_level = 1 + development × 0.1 + population × 0.05 + 5 if city + 10 if
megalopolis`, so **five levels are worth `5 ÷ cap` in output** and the crossover
is exact: **+5 levels beats +20% while the guild's cap is under 25 levels.**

- a plain town, cap around 10: flemish is +50% against +20% — **flemish, by far**;
- a city, cap 20-25: they meet;
- a megalopolis, cap well over 25: **royal textile**, and it also carries dyes,
  which flemish does not touch at all.

And flemish is available two whole ages earlier. **The general answer is flemish
in a town, royal textile in a great city** — but the mod cannot pick between them
today, because it scores no level right at all.

## What is undecided

- **Nothing about the level rights any more.** He settled it on 2026-09-02 —
  «включай в расчёт все подобные домики, считай их как ты посчитал фламандское
  сукно» — and the merge admits exactly one, flemish cloth, because the only
  other level rights grant marketplace levels and no method produces a
  marketplace. Its own `potential` (Netherlandish culture group) is what keeps it
  off everyone else — **and Westphalian is in that group**, read off
  `cultures/german.txt` on 2026-09-03, which is why Münster's towns take Flemish
  cloth and never royal textile. The advance gate came later and for a different
  reason: «Сейчас» asks it, «В конце» does not.
- **Whether a town that suits no right at all should still get one.** The plan
  grants a right where the town can make at least one of its goods; if none of
  the twelve passes, the town gets none. It has not happened on any ground run so
  far.
- **The row.** A bundle is up to three goods, so a row wants three answers where
  it has two. A row can hold a fixed number of them and not a variable one:
  script has no list of tuples, and the answers are parked as flat variables on
  the location. Three fixed slots, not a datamodel.

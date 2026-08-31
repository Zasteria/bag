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

**3. A level right is a different unit and must not be added to the others.**
`flemish_cloth_industries_right` grants no efficiency at all: +5 levels of cloth
guild and +5 of fine cloth. An output right multiplies what you would have built
anyway; a level right adds levels. One is a ratio, the other a quantity, and a
score that sums them is the village-above-the-guild error in a new suit.

Score a level right on its own terms: **added levels × the value of one level
there**, which is the number the mod already computes.

### The cap is computable, unlike a building slot

`guild_max_level` in `common/script_values/building_caps.txt`:

    1 + development × 0.1 + population × 0.05 + (5 if city, 10 if megalopolis)

and `cloth_guild_max_level = guild_max_level + local_cloth_guild_building_levels`.
Every term is readable from a location in script. So a row for a level right can
honestly print **cap before → cap after**, which the mod could never do for
building slots (`mods/where_to_produce/CLAUDE.md`: the game exposes no slot count
at all — that stays true, a level cap is a different thing).

### The owner's worry, and where it lands

> *"в локации где лимит будет 3 и он получит бонус +5 очевидно будет выгодней,
> чем в локации где можно поставить 15 и он получит +5"*

In **absolute** terms it is the other way round or equal: five levels produce
five levels' worth in both, and what differs is the value of one level — the
RGO bonus, which the mod already ranks on. In **proportional** terms he is
right: +5 on a cap of 3 is +167% and on 15 is +33%.

Neither is the whole answer, because the term neither of us can see is
**whether the levels can be filled** — levels want pops to employ, and a cap-3
location is small precisely because its development and population are small.
The mod does not model employment and should not pretend to.

So: rank on the absolute gain, print the cap before and after beside it, and let
the proportion be read off the two numbers rather than ranked on. That is the
one place in this design where the mod hands the judgement back.

## Built, 2026-08-31, and never loaded

The output half is in: a third list on the Goods tab, exclusive with the two
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

## What is undecided

- **Level rights.** Deferred by the owner on 2026-08-31: «Давай отложим права
  на лимит пока.» Six of the seventeen are level rights and four of those are
  marketplaces, which are trade and not production at all.
- **`town_right_efficiency_penalty`.** Not needed to rank provinces — constant —
  but needed to answer «is this right worth taking», which is a different
  question the mod does not currently ask. One `grep` on his install settles it.
- **The row.** A bundle is up to three goods, so a row wants three answers where
  it has two. A row can hold a fixed number of them and not a variable one:
  script has no list of tuples, and the answers are parked as flat variables on
  the location. Three fixed slots, not a datamodel.

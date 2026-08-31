# The building ladder, and why one answer is not enough

The owner's question, 2026-08-31: *the first half of a game changes little, but
from the third age buildings improve constantly. Can I plan for the whole game
by turning the age filter off, or does that want thinking about separately?*

Turning the filter off does give the last age's method — and gives only it. The
answer below is that "best now" and "best at the end" are two different
provinces often enough to be worth two columns, and that the game hands us the
ladder for free.

## The ladder is `obsolete`, and it is the game's own

`building_types/readme.txt`: *obsolete: <building type> what building type this
one makes obsolete*. Thirty chains, every production one ending in a mill or a
factory:

    weapon_guild -> weapon_workshop -> weapon_manufactory -> weapon_factory
    cloth_guild  -> cloth_workshop  -> cloth_manufactory  -> textile_mill
    paper_guild  -> paper_workshop  -> paper_manufactory  -> paper_mill

Output along a rung: 1.0 -> 1.1 -> 2.0 -> 4.0. **Methods are almost never gated
themselves** — ten of them carry `unlock_production_method`; the other 218 ride
on their building's own advance, of which 184 buildings have one.

Two facts that made the feature cheap:

- **A building somebody obsoletes can never be the endgame answer.** 76 of them
  are; 94 methods of 228 survive. Checked at full bonus over every good and both
  sides: no obsoleted method beats a surviving one, ever. So "the best of the
  survivors" needs no age arithmetic at all.
- **The location requirements do not move along a production chain.** All thirty
  chains compared on `town`, `city`, `port`, `potential`, `can_build`: only
  `charcoal_maker -> improved_charcoal_maker` and two military chains differ.
  Where a guild can stand, its mill can stand. **So the ground never expires —
  what expires is the recipe.**

## What moves is the input mix

The bonus is `10 * (inputs the province supplies) / (all inputs)`, so the
province's rank follows the recipe's inputs, not its output. Fourteen of the
forty-two goods shift their mix along the ladder; five change it outright:

| good | first rung | last rung | ceiling |
| --- | --- | --- | --- |
| `firearms` | bronze: copper + tin | lead + saltpeter | 6.66% -> 4.45% |
| `cannons` | copper + tin | lead + saltpeter | 5.46% -> 3.48% |
| `fine_cloth` | silk | dyes | 10.00% -> **0.63%** |
| `paper` | cloth + lumber | pure lumber (wood pulp) | **1.66% -> 10.00%** |
| `weaponry` | lumber, coal, tools | steel, coal, lumber | 5.24% -> 8.10% (age 3) -> 3.75% |

The other twenty-eight — cloth, leather, beer, furniture, pottery, tools — keep
their mix and only grow, and for those one column would have done.

`weaponry` is the one that is not even monotone: the age-3 workshop is the best
place in the ladder and the age-6 factory is the worst, because steel is a
produced good and carries weight in the denominator no RGO can ever supply.

## What was built on it

A second answer per side, `bag_wtp_end_*`, found in the same walk: a survivor's
`bag_wtp_m<n>` is computed once and offered to both columns, so the far column
costs a comparison per method rather than a second pass over the province. It is
**written only where it differs from the near one**, so an empty cell is the row
saying "this province does not change" — which is what the twenty-eight stable
goods will say, and the point of showing it that way.

`bag_wtp__rank_by_end` decides which column the ranking sorts on. It matters
more than it looks: the near column decides which fifty provinces get a row at
all, so with the tick off a province that is poor now and first at the end is
never seen. **That is the known hole in this feature** and the reason the tick
exists.

## Not answered here

- **Whether a building upgrades in place or has to be rebuilt.** `obsolete` says
  only that the old one can no longer be built. If the game rebuilds a chain in
  place, the whole question is milder than the owner thinks; if it does not, the
  far column is the only one worth planning on. One look at a guild in a country
  that has reached the workshop settles it.
- **Level rights and the ladder together** — deferred with the rest of the level
  rights in [`town_rights.md`](town_rights.md).
- **The rights window has one column still.** A bundle's ladder is three
  ladders, and nothing about the shape above says how to show that in a row.

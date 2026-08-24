# Goods Target

An addon to **Construction Manager**: pick the goods you want cheap, and it
keeps building their producers until construction of everything else is as
cheap as the game will allow — ignoring the profitability rules that would
otherwise stop it, and subsidising the producers so their workers stay put.

Requires the Community Mod Framework and Construction Manager.

> **This is the first step of that, and only the first.** Nothing is built and
> nothing is subsidised yet. What ships is the measurement the rest depends on,
> put where it can be checked against the game. See
> [What is built so far](#what-is-built-so-far).

## The idea

Cheap goods make construction cheaper, up to a cap of 33%. Construction
Manager can already be told not to build below a minimum discount — but the
same profitability rules that keep it from spamming useless buildings also keep
it from building the surplus lumber, glass and masonry that would earn that
discount in the first place. The buildings that depress a price are, by
definition, the ones that stop being profitable as the price falls.

So this asks for the opposite thing, for a few goods you name: build their
producers *because* the price should fall, keep them alive with subsidies while
it does, and stop once the discount is there.

## What is built so far

**The reading.** For each of the game's 28 construction goods, a script value
saying what that good's price in your capital's market is doing to the cost of
building — `bgt_impact_lumber` and its 27 siblings, in percent, negative being a
discount.

The formula is Glorp UI's `glorpui_construction_good_adjustment`, which is what
Construction Manager's own discount gates use. Copying it rather than inventing
one means the number shown here and the number CM acts on cannot drift apart.
`tools/generate.py` writes those values, taking the list of construction goods
from Construction Manager's own `cm_construction_demand_<good>` maps rather than
from a list typed by hand.

**Two settings**, in the Mod Menu under **Goods Target**: the discount to aim
for, and whether to write a yearly line of readings into the framework's log.
Both are types CMM applies by itself.

**Nothing else.** No goods list, no building, no subsidies.

## What to look at first

The mod is in the game to answer one question: **are the readings right?**

1. Mod Menu → **Goods Target**. The tab should exist, with two settings. If it
   does not, registration failed and nothing else matters.
2. Hover **Write readings to the log**. Its tooltip prints the five standard
   construction goods — lumber, masonry, glass, sand, stone — with what each is
   doing to construction cost right now.
3. Open the build panel for any building and read the game's own construction
   cost tooltip, which breaks the cost down by good.

If the two agree, the rest of the mod is worth writing. If they disagree, the
difference is the whole story and nothing should be built on top.

`error.log` will name the file and line if a value fails to evaluate. A reading
that is simply wrong logs nothing, which is why it has to be read off the screen
against the game's own tooltip.

## What comes next, in order

1. **A goods list.** A CMM list setting, one row per construction good, with a
   tick and a target. Lists are the part of CMM that fails silently — a list is
   invisible without a `<mod>__<setting>_on_changed` scripted GUI, and CMF's
   auto-apply does not cover them — so it gets its own step and its own run.
2. **Building.** Construction Manager stages its own work into
   `cm_q_ungated_locations` / `cm_q_ungated_building_types`, a queue that skips
   the profit and discount gates; its Auto Build feature is built on exactly
   that. This mod adds its own leaf action to the monthly pulse, stages there,
   and lets CM's queue window build and pay for it. CM's dispatcher switches on
   a fixed set of feature flags with no default branch, so adding a flag to its
   priority list would do nothing at all — see
   [`RESEARCH.md`](../../docs/RESEARCH.md#construction-managers-automation-and-how-to-add-to-it).
3. **Subsidies.** `set_subsidized` in a building scope, `is_subsidized` to read
   it back. Applied to the producers of a targeted good, so a building that goes
   into loss as the price falls keeps its workers.
4. **Advice.** A targeted good whose own recipe is expensive — lumber mills held
   back by dear tools — is worth saying out loud rather than silently failing to
   reach the target.

## Layout

```
.metadata/metadata.json                       descriptor, depends on CMF and CM
in_game/common/on_action/                     CMF registration and the yearly probe
in_game/common/scripted_effects/              settings, and the probe itself
in_game/common/script_values/                 generated: one price reading per good
main_menu/localization/                       English and Russian
tools/generate.py                             writes the readings
```

Regenerate after a game patch or a Construction Manager update:

```
python3 tools/refresh.py
```

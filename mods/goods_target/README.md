# Goods Target

An addon to **Construction Manager**: pick the goods you want cheap, and it
keeps building their producers until construction of everything else is as
cheap as the game will allow — ignoring the profitability rules that would
otherwise stop it, and subsidising the producers so their workers stay put.

Requires the Community Mod Framework and Construction Manager.

> **Nothing is built and nothing is subsidised yet.** What ships so far is the
> measurement the rest depends on, and the goods list to tick in. See
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

**The goods list.** A CMM list, one row per construction good, with two ticks:
**Build** and **Subsidise**. The five goods worth targeting — lumber, masonry,
glass, sand, stone — are first; the other 23 follow. Rows, their ordinals and
their labels are generated, because a CMM list macro pastes `item = var:x`
verbatim and dies at load on it, so every ordinal has to be a literal.

**Two settings**: the discount to aim for, and whether to write a monthly line
into the framework's log naming the goods that are ticked.

**Nothing else.** No building, no subsidies — the ticks are only recorded.

## What to look at first

The readings were checked in game and match; see
[`TESTLOG.md`](../../docs/TESTLOG.md). The open question now is **whether a tick
in the goods list reaches script.**

1. Mod Menu → **Goods Target**. There should be a **Goods** list under the two
   settings, 28 rows, each naming a good behind its icon. A list that is missing
   entirely — header without rows — means the `_on_changed` scripted GUI did not
   register, which is the one failure CMM gives no other sign of.
2. Tick **Build** on lumber and **Subsidise** on glass.
3. Wait for the month to turn and open CMF's log. It should say it is watching
   1 good, then name lumber for building and glass for subsidising.

The count and the names are logged separately on purpose. The count is a bare
number and cannot fail to render; naming a good asks CMF's log to render a goods
scope, which is less certain. A right count with missing names means the list
works and only the logging is wrong.

## What comes next, in order

1. **Building.** Construction Manager stages its own work into
   `cm_q_ungated_locations` / `cm_q_ungated_building_types`, a queue that skips
   the profit and discount gates; its Auto Build feature is built on exactly
   that. This mod adds its own leaf action to the monthly pulse, stages there,
   and lets CM's queue window build and pay for it. CM's dispatcher switches on
   a fixed set of feature flags with no default branch, so adding a flag to its
   priority list would do nothing at all — see
   [`RESEARCH.md`](../../docs/RESEARCH.md#construction-managers-automation-and-how-to-add-to-it).
2. **Subsidies.** `set_subsidized` in a building scope, `is_subsidized` to read
   it back. Applied to the producers of a targeted good, so a building that goes
   into loss as the price falls keeps its workers.
3. **Advice.** A targeted good whose own recipe is expensive — lumber mills held
   back by dear tools — is worth saying out loud rather than silently failing to
   reach the target.

## Layout

```
.metadata/metadata.json                       descriptor, depends on CMF and CM
in_game/common/on_action/                     CMF registration and the monthly probe
in_game/common/scripted_effects/              settings, the probe, and the generated list
in_game/common/scripted_guis/                 the list's _on_changed, without which no list is drawn
in_game/common/script_values/                 generated: one price reading per good
main_menu/localization/                       English and Russian
tools/generate.py                             writes the readings, the list and its labels,
                                              and checks every CMM key is localized in both languages
```

Regenerate after a game patch or a Construction Manager update:

```
python3 tools/refresh.py
```

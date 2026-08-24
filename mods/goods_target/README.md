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

**The reading.** For every one of the game's 74 goods, a script value saying
where that good's price in your capital's market stands against its default, in
percent, negative being cheap — `bgt_impact_lumber` and its 73 siblings. For the
28 goods construction is charged in, that figure is also the discount the good
earns on building; for the rest it is the price and nothing more.

The formula is Glorp UI's `glorpui_construction_good_adjustment`, which is what
Construction Manager's own discount gates use. Copying it rather than inventing
one means the number shown here and the number CM acts on cannot drift apart.
`tools/generate.py` writes those values, taking the list of construction goods
from Construction Manager's own `cm_construction_demand_<good>` maps rather than
from a list typed by hand.

**Two goods lists**, because CMF initialises at most 50 list rows and 74 goods
do not fit in one: **Goods Construction Is Paid In** (28) and **Other Goods**
(46). The five a player can actually depress — lumber, masonry, glass, sand,
stone — lead the first.

Each row carries what that good is doing right now beside its name, and three
fields: **Build**, **Subsidise**, and **Target** — the discount that good should
reach, per good rather than one figure for all of them.

Rows, ordinals and labels are generated. A CMM list macro pastes `item = var:x`
verbatim and dies at load, so every ordinal has to be a literal, and the
generator refuses to emit a list longer than CMF can initialise.

**One setting**: whether to write a monthly line into the framework's log.

**Nothing else.** No building, no subsidies — the ticks are only recorded.

## What to look at first

The readings match the game and the lists draw; see
[`TESTLOG.md`](../../docs/TESTLOG.md). What is still unknown is **whether the
monthly check runs at all** — last round its log line never appeared, and the
log was the only thing that would have said so.

So the answer no longer goes through the log:

1. Tick **Build** on lumber and **Subsidise** on glass.
2. Let a month pass.
3. Mod Menu → **Goods Target**, hover **Write to the log**. The tooltip counts
   monthly checks seen, goods ticked to build, goods ticked to subsidise. Those
   are counted by the monthly check itself, so they are the ticks as script sees
   them.

**Monthly checks still 0** — the on_action never reaches us, and nothing else
here is running either. **Checks climbing, ticks 0** — the pulse runs and the
list's output is not reaching it. **Both right, log still silent** — everything
works and only CMF's log does not render what it is handed, which costs nothing.

Two things about last round were fixed blind rather than diagnosed, because
either could have caused the silence on its own: a `variable_map` read used as a
gate, which errors rather than returning false when the key was never written,
and a count passed to a CMF macro as `var:` — the same shape that kills a list
on `item = var:x`.

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

# Goods Target

An addon to **Construction Manager**: pick the goods you want cheap, and it
keeps building their producers until construction of everything else is as
cheap as the game will allow — ignoring the profitability rules that would
otherwise stop it, and subsidising the producers so their workers stay put.

Requires the Community Mod Framework and Construction Manager.

> **Paused, and not working yet.** The lists and the readings are right; nothing
> runs on a schedule, nothing is built and nothing is subsidised. See
> [Where it stands](#where-it-stands-and-what-is-wrong-with-it) before touching
> anything.

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

## Where it stands, and what is wrong with it

Paused in August 2026, at the owner's word, with four faults known and two of
them diagnosed. Everything below is from a real run whose logs are in hand;
`error.log`, its rotations, `gui.log` and `game.log` carry **not one line** about
this mod, so every fault here is of the silent kind.

**Works, seen on screen:** registration and the Mod Menu tab; both lists, all 74
rows, each naming its good; ticks; the game's own goods tooltip on a row; and the
readings, which matched the game's construction tooltip on the first run.

**1. Nothing periodic runs.** The settings tooltip counts monthly checks and it
stayed at zero. Not the display path — Construction Manager reads `var:` inside
a script value the same way. So either the leaf on
`cmf_monthly_human_country_pulse` never fires, or it fires and dies without a
trace. What is known: `monthly_country_pulse` exists in the game's own dump, CMF
chains it through `_cmf_on_monthly`, and *this mod's* other leaf — registration,
on `cmf_on_mod_registration` — demonstrably works, so on_action merging from
this file works at least once.

  **The cheapest next step** is free: Construction Manager's own automation runs
  on that same pulse. If CM still auto-builds in the same save, the on_action
  fires and the fault is ours; if CM has also gone quiet, it is not. After that,
  a leaf on the *yearly* pulse alongside the monthly one separates "this
  on_action" from "our leaves in general" in a single run.

**2. The Target column printed a key.** Diagnosed and **fixed, unverified**: a
field given `cmm_set_list_field_conditional_format` needs `_prefix`, `_postfix`
and the `_high` / `_low` pair, and CMF detects their existence by comparing
`Localize(key)` with the key itself — so a missing one renders as its own name
and logs nothing. `tools/check_cmm.py` now derives every key CMM will look for
and fails on a missing one; it reproduced this fault exactly before the twelve
keys were added.

**3. The game loses ticks while the menu is open, and 4. the readings never
change.** One cause: every one of the 74 row labels calls
`ScriptValue('bgt_impact_<good>')`, and each of those reads a market price and a
default price four times over. That is evaluated per drawn row, per frame. The
version before this one had no reading in its rows and cost nothing noticeable.

  **The fix, not yet made:** compute the readings on the pulse into
  `bgt_read_<good>` variables and let each row read its variable — cheap to draw,
  and it changes exactly when the pulse says so, which is also what "updates
  monthly" means. That fix depends on fault 1, since nothing runs on the pulse
  yet.

## What comes next, in order

1. **Building.** Construction Manager stages its own work into
   `cm_q_ungated_locations` / `cm_q_ungated_building_types`, a queue that skips
   the profit and discount gates; its Auto Build feature is built on exactly
   that. This mod adds its own leaf action to the monthly pulse, stages there,
   and lets CM's queue window build and pay for it. CM's dispatcher switches on
   a fixed set of feature flags with no default branch, so adding a flag to its
   priority list would do nothing at all — see
   [`research/cmf.md`](../../docs/research/cmf.md#construction-managers-automation-and-how-to-add-to-it).
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

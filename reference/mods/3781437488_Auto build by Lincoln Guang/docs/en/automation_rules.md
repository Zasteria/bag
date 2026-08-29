# EU5 Advanced Auto Build: Rule Guide

English | [Simplified Chinese](../zh-CN/automation_rules.md)

## Goal

Base-game economic automation primarily seeks individual high-profit buildings, which often leaves food, construction materials, civilian essentials, and wartime military supplies under-resourced. This mod proactively identifies macroeconomic bottlenecks and supply-chain deficits before selecting projects that satisfy template rules, budget limits, workforce availability, and vanilla construction requirements. Prior to breaking ground on ordinary production buildings, the system also inspects the game engine's predicted monthly income, predicted monthly profit, and construction cost against the player's chosen economic return thresholds.

## Information the Mod Uses

The mod queries live game-state metrics to evaluate construction need and feasibility:

- Market food stockpiles, monthly food balances, and projected exhaustion timelines.
- Commodity supply, demand, and price levels, with particular emphasis on construction materials, consumer necessities, and military supplies.
- Building input recipes, output goods, construction costs, and game-predicted monthly revenue and profit.
- Location-level existing infrastructure, active civil construction, cooldown status, and current/projected workforce availability.
- Resource Gathering Operations (RGO) expansion limits, current labor utilization, market demand, and vanilla unlock requirements.

The mod strictly obeys all base-game tech unlocks, construction criteria, and location slot constraints. Detailed data structures and script interfaces are documented in the Developer Notes at the end of this guide.

## How Projects Are Chosen Each Month

Automated construction works in several steps:

1. At the start of the month, the Mod reads CMF Mod Settings, updates location cooldowns, and counts
   its projects still under construction. Manual construction, roads, and other Mods do not use this
   Mod's concurrent slots.
2. In January, the Mod sets the annual budget to the chosen fixed amount or 4, 6, or 8 times monthly
   total income. Every template shares this budget.
3. From days 2–21, locations using templates are checked in batches so the whole country is not
   processed on one day. The player can limit how many locations receive a detailed check each day.
4. Each location first finds projects allowed by its template and safety rules. Supply-Demand Planning
   keeps the configured 3–30 top Planning Candidates for each ordinary build type. Predicted Profit
   Selection keeps the configured 3–30 Profit Candidates so their game-predicted monthly profit can
   be compared. RGOs follow their own rules.
5. On day 22, projects are scheduled. Urgent food projects come first, followed by upgrades, ordinary
   expansions, RGO expansions, and new buildings in the player's Automated Build Order.
6. If one project cannot start, the Mod keeps looking within the same type. It moves to the next type
   only when no project in the current type can start.
7. Budget, a concurrent slot, and the three-month location cooldown are applied only after the project
   actually enters the civil-construction queue. RGOs share the same slots and have no separate monthly cap.
8. When Build Upstream Sources on Shortage is enabled, a planned building blocked by missing inputs can
   be replaced by an allowed upstream building that helps relieve the shortage.

The player setting adds capacity beyond one base slot: 0 means this Mod may run at most one active
project and 599 means at most 600. Each month fills only this Mod's remaining slots, and each location
may receive at most one project at a time.

## Requirements Every Project Must Meet

A high price does not guarantee construction. A project must also meet these requirements:

- Building-quality priority must be above zero unless a built-in preset explicitly allows the
  building. Zero is always a hard disable in a custom template.
- The building must be allowed by policy and absent from its ban list. Special buildings require
  explicit permission.
- The location must have no civil construction in progress and no active cooldown.
- With workforce protection enabled, projected available workers must fill the new jobs by the
  selected deadline.
- With input protection enabled, industrial-input supply must be at least 75% of demand.
- Output below the policy's minimum price ratio is treated as oversupply. A high price signals
  shortage and is not rejected as "out of range."
- Ordinary production buildings must pass the selected game-predicted return requirement unless a strategic
  override applies. Infrastructure without output goods is exempt from this return check.
- Construction goods already committed to other projects in the same run count toward demand. Total
  demand must stay below the safety limit, and each required good must cost no more than 150% of its
  default price.
- An ordinary building's construction cost must fit the remaining annual budget and leave the required
  treasury reserve. RGOs use the base-game cost of 100 for budget purposes. Costs are settled only
  after the project enters the construction queue.

## Need Scores

These scores set the order used by Supply-Demand Planning. Survival needs and production-chain
bottlenecks deliberately outweigh ordinary price bonuses, so a high-priced luxury good does not
easily overtake food or critical materials during a shortage.

| Signal | Score |
| --- | ---: |
| Market projected to exhaust its food stockpile | +12000 |
| Food stockpile at or below 25% | +9000 |
| Food stockpile at or below 50% | +6000 |
| Negative monthly food balance | +4500 |
| Construction-good supply/demand at or below 65% | +5000 |
| Construction-good supply/demand at or below 90%, or price above 125% | +3000 |
| Severe/moderate population-essential shortage | +2800 / +1400 |
| Severe/moderate military-good shortage | +3500 / +1200 |
| Wartime military bonus | +1800 |
| Scarce upstream source | +3200 |
| Policy-priority goods | First +600, then -20 per later entry |
| Video-calibrated building quality | 0–10, +50 per point; inherit when possible, otherwise 0 |
| Building-role match | +300 |
| Severe input shortage | -3000 |
| Existing levels of the same building | -25 per level |

The first pass uses supply, demand, prices, building priority, and workforce to calculate a planning
score. The game-predicted monthly income, predicted monthly profit, and construction cost are read
only during the final check for ordinary buildings. This keeps food and production-chain bottlenecks
ahead during a crisis while still using price, template priority, and saturation to compare similar
projects in a stable market.

## Construction Decision Strategies

The selected return metric decides whether a project may start; it does not decide project order. A
project that meets the Income, Profit, Return on Income, or Return on Profit requirement may still rank below another
eligible project. After food-emergency handling and Automated Build Order select the current layer and
build type, CMF Mod Settings offers two ordinary-building strategies:

- **Supply-Demand Planning:** arrange construction using market shortages, strategic demand, recipe
  efficiency, local inputs, commodity prices, and workforce risk, emphasizing complete production
  chains and stable long-term supply and demand. The template's 0–10 building priority contributes
  directly to the planning score. Prefiltering and final order use the same planning score. Planning
  Candidates per Location controls how many high-scoring projects remain as fallbacks when earlier
  candidates fail later checks; this bound cannot guarantee that every feasible lower-ranked project
  is retained.
- **Predicted Profit Selection:** filter candidates through template and safety rules, then select by
  the game's predicted monthly profit. The 0–10 building priority has a soft influence when profits
  are close: `rank = predicted_profit + max(abs(predicted_profit), 1) × priority × 0.01`. This strategy
  selects only from the configured 3–30 Profit Candidates prefiltered per location and current ordinary build type and
  remains subordinate to food-emergency handling and Automated Build Order, so it does not claim the
  absolute global highest profit.

Predicted Profit Selection rechecks the predicted return, budget, treasury, material, workforce, and vanilla build conditions
before approval. It does not change the hard food-emergency layer, Automated Build Order, or RGO
ranking rules. The Action Bar explains the active mode and these boundaries in both supported UI
languages.

**Planning Candidates per Location** and **Profit Candidates per Location** appear under
**Performance Optimization → Advanced Settings**. Each is shown and used only by its matching
strategy. Raising Planning Candidates reduces missed fallbacks when higher planning scores fail later
checks. Raising Profit Candidates reduces misses caused by using planning score for prefiltering but
predicted profit for final order. They do not affect one another, though both increase later checks.
Performance presets set them to 5 / 15 for Conservative, 4 / 12 for Balanced, and 3 / 10 for Maximum
Throughput (planning / profit). Editing either value switches the performance preset to Custom.

## Automated Build Order, Returns, and Emergency Rules

Automated Build Order is a draggable four-item list shared by every template:

1. Building upgrades
2. Existing ordinary-building expansions
3. RGO expansions
4. New ordinary buildings

Scores order candidates inside the current type; they cannot make a lower type overtake it. When one
project cannot start, the Mod keeps looking within the current type before moving on.

Ordinary production buildings can use one of four return requirements:

| Setting | Requirement to start |
| --- | --- |
| Income | Game-predicted monthly income is greater than 0 |
| Profit | Game-predicted monthly profit is greater than 0 |
| Return on Income | Game-predicted monthly income is at least `actual cost × 5% ÷ 12` |
| Return on Profit | Game-predicted monthly profit is at least `actual cost × 5% ÷ 12` |

The five strategic switches are independent:

| Switch condition | Handled first | Return requirement relaxed for |
| --- | --- | --- |
| Market projected to exhaust food | Yes | Matching ordinary food buildings |
| Food stockpile at or below 25% | Yes | Matching ordinary food buildings |
| Core construction-good supply below 65% of demand | No | Buildings producing that good |
| At war and military-good supply below 65% of demand | No | Buildings producing that military good |
| Upstream input below 65% and blocking an enabled strategic building | No | Buildings producing that upstream input |

The two food switches both prioritize food projects and relax the return requirement for matching
ordinary buildings. The other three only relax the return requirement. No switch bypasses annual
budget, treasury reserve, workforce/input protection, construction goods, vanilla construction
conditions, location queue availability, or this Mod's concurrent limit.

## RGO Rules

RGO expansion is attempted only when all of the following are true:

- The RGO is not fully expanded and its current utilization meets the player-selected threshold (adjustable from 0% to 100% in 5% steps, default 75%).
- Its raw material is a scarce food good, construction good, or current policy-priority good.
- The treasury reserve and shared annual pool can cover the vanilla base cost of 100.

An RGO uses a slot, starts its cooldown, and deducts budget only after the expansion actually enters
the civil-construction queue. If the game rejects the expansion, the Mod does not charge the budget.

RGO locations are compared using food pressure, goods shortages, workforce, development, control,
market access, raw-material price, utilization, and remaining expansion space. This ordering applies
only within the RGO type and cannot overtake a build type placed above RGO in Automated Build Order.

## Where Players Change These Rules

- Template window: enable or pause a template, choose its coverage, and set each building's 0–10 priority.
- CMF Mod Settings: set the concurrent limit, annual budget, treasury reserve, price range, Construction
  Decision Strategy, Automated Build Order, return requirement, strategic switches, safety rules, RGO
  rules, and performance options.
- Construction Report: review the latest monthly check, projects that started, and reasons projects were rejected.
- [`building_quality_priorities.md`](building_quality_priorities.md): review recommended building priorities and their rationale.

## Developer Notes

- `policies/automation_rules.json`: cadence, thresholds, scores, and goods/building groups.
- `policies/building_catalog.json`: generated catalog of player-manageable vanilla buildings.
- `policies/video_building_priorities.json`: direct video scores and explicit user overrides.
- `policies/templates.json`: built-in presets, including roles, allowlists, bans, and priority goods.
- `src/eu5autobuild/catalog_builder.py`: reads vanilla buildings and advances, then refreshes the
  catalog, unlock ages, and inherited priorities.
- `src/eu5autobuild/engine.py`: testable pure-Python mirror of the decision rules.
- `src/eu5autobuild/generator.py`: generates the actual EU5 scripts, GUI, and localization.
- `tests/test_automation_generator.py`: verifies cadence, budget, need scoring, upstream recovery,
  and RGO integration in generated scripts.

## Known Limitations and Tests

- All five RGO expansion methods have a base-game gold cost of 100, which the Mod uses for budget
  settlement. Dynamic cost modifiers from the country, location, or other sources are not yet included
  in this Mod's RGO budget accounting.
- This Mod marks a location after confirming a project start and clears the marker once that location
  has no civil construction. If the player later adds manual work in the same location, the slot
  remains conservatively occupied until all civil construction there finishes.
- Static tests verify real EU5 IDs, generated files, brace balance, and key script interfaces. An
  optional interface smoke test also runs when local `script_docs` are available.

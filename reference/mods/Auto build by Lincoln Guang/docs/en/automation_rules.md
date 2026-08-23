# EU5 Advanced Auto Build: Game-File Analysis and Rule Reference

English | [Simplified Chinese](../zh-CN/automation_rules.md)

## Goal

The base game's economic automation primarily ranks candidates with
`building_potential_profit` from `common/employment_systems/00_default.txt`.
That is useful for finding profitable individual buildings, but it does not guarantee that food,
construction materials, population essentials, and military supplies are replenished first. This Mod
therefore uses layered "needs first, market signals decide" rules. Static supply, demand, market-price,
and saturation signals create the shortlist. A hidden GUI bridge then reads the engine's actual income,
profit, and cost for ordinary buildings and enforces the player's selected return requirement.

## Data Basis

The source is the repository's EU5 `common/` dataset, cross-checked against the local EU5 1.3
installation.

- The data contains 883 top-level `building_type` definitions and 85 goods. Thirteen goods have a
  positive `food` value, so apparently non-staple goods such as `fur` and `beeswax` still belong to
  the game's food-stockpile system.
- `market_triggers.txt` and market properties expose `market_food_percentage`,
  `market_monthly_food_balance`, `is_projected_to_run_out_of_food_stockpile`,
  `goods_supply_in_market`, `goods_demand_in_market`, and `market_price`.
- Building-trigger profit, input, and output queries require an existing building-instance scope and
  cannot be called directly on an unbuilt `building_type` candidate. The generator therefore uses
  static recipe data for shortlisting, then reads actual income, profit, and cost through engine GUI
  getters.
- `location_triggers.txt` exposes unemployed population, existing levels, civil-construction count,
  and RGO worker capacity by `building_type`.
- Common construction bottlenecks in building recipes include masonry, lumber, tools, glass, paper,
  and stone.
- Vanilla `common/prices/00_hardcoded.txt` sets the base gold cost of mining, farming, hunting,
  gathering, and forestry RGO expansion to 100. The generator reads all five entries and validates
  the mirror value used from `automation_rules.json`; 100 comes from vanilla and is not an independent
  estimate or a tunable balance parameter.
- The vanilla RGO expansion UI also favors economic return. `construct_rgo_upgrade` is a
  parameterless effect on the current location; vanilla still checks its internal requirements.

## Decision Pipeline

Each month is split into country initialization, twenty daily batches, and final queue settlement:

1. The monthly country pulse synchronizes CMF Mod Settings, reduces cooldowns for assigned locations,
   and counts projects confirmed by this Mod that remain under construction. Manual construction,
   roads, and projects from other Mods do not use this Mod's concurrent limit.
2. In January, the national annual pool is reset from the selected fixed amount or
   `monthly_income_total ×4/×6/×8`. Every built-in preset and custom template shares this pool; it is
   also initialized on first load.
3. Assigned locations pass a cheap filter and are distributed deterministically across twenty
   transient lists. Days 2–21 process only that day's list, avoiding a full-country deep scan on one
   day. The daily location-task limit is configurable from 1 to 30.
4. Optional Independent Location Tasks split location calculations into separate event tasks. This
   does not claim that the game uses multiple CPU threads. Country-level merging, budget settlement,
   diagnostics, and starts remain deterministic.
5. Each location retains its strongest ordinary-building candidates and any eligible RGO candidate.
   Every retained candidate enters exactly one food-emergency/build-type phase, preventing duplicate
   scoring across phases.
6. On day 22, the Mod merges the month's candidates. It first follows the player's four-type Automated
   Build Order for urgent food projects, then follows the same order for other projects. The default
   is upgrade → ordinary expansion → RGO expansion → new ordinary building.
7. The Mod exhausts viable projects in the current build type before entering the next. If an ordinary
   building fails the engine's cost, return, or construction checks, temporary reservations are
   released and the next project of the same type is tried.
8. Budget, one of this Mod's concurrent slots, and a three-month location cooldown are committed only
   after the civil-construction queue actually grows. RGO expansion uses native
   `construct_rgo_upgrade`, shares the ordinary-project slots, and has no separate monthly cap. If
   upstream recovery is enabled, a genuinely scarce source may enter the matching ordinary-building
   class when missing inputs block a normal candidate.

The player setting adds capacity beyond one base slot: 0 means this Mod may run at most one active
project and 599 means at most 600. Each month fills only this Mod's remaining slots, and each location
may receive at most one project at a time.

## Hard Gates

A candidate must pass every applicable gate; a high price alone cannot make it eligible:

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
- Ordinary production buildings must pass the selected engine return requirement unless a strategic
  override applies. Infrastructure without output goods is exempt from this return check.
- Actual construction-goods demand plus same-run reservations must remain below the stop threshold,
  and each required good must cost no more than 150% of its default price.
- For ordinary buildings, actual cost plus same-run reservations must fit both the remaining annual
  pool and the configured treasury reserve. RGOs instead use the base cost of 100 verified against
  vanilla's price table at generation time. Settlement occurs only after queue growth confirms the
  start.

## Need Scores

The following values come from `policies/automation_rules.json`. Need scores deliberately outweigh
the bounded market-price proxy.

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
| High/nonnegative/negative profit in pure-Python fixtures | +180 / +90 / -180 |
| Existing levels of the same building | -25 per level |

Generated scripts do not use `building_potential_profit` for shortlist scoring. Both built-in and
custom templates use +180 when an output good exceeds the configured high-price reference as a bounded
shortage proxy; the pure-Python evaluator retains a bounded profit term for offline tests. The hidden
GUI bridge then enforces actual income, profit, or return on cost. Food and RGO candidates therefore
remain well ahead of luxury goods during a food crisis; under stable supply, market prices, template
priority, and saturation separate candidates within one build type.

## Automated Build Order, Returns, and Emergency Rules

Automated Build Order is a draggable four-item list shared by every template:

1. Building upgrades
2. Existing ordinary-building expansions
3. RGO expansions
4. New ordinary buildings

Scores order candidates inside the current type; they cannot make a lower type overtake it. When one
project cannot start, the Mod keeps looking within the current type before moving on.

Ordinary production buildings have four final engine checks:

| Setting | Final engine check |
| --- | --- |
| Income | Actual monthly income is greater than 0 |
| Profit | Actual monthly profit is greater than 0 |
| Return on Income | Actual monthly income is at least `actual cost × 5% ÷ 12` |
| Return on Profit | Actual monthly profit is at least `actual cost × 5% ÷ 12` |

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

- The RGO is not fully expanded and its current workforce is at least 75% of capacity.
- Its raw material is a scarce food good, construction good, or current policy-priority good.
- The treasury reserve and shared annual pool can cover the vanilla base cost of 100.

After `construct_rgo_upgrade = { }` is called, the attempt uses a slot, starts cooldown, and deducts
budget only if civil construction actually appears in the location. A hidden vanilla rejection
therefore cannot charge the Mod's budget.

Final RGO location ordering directly combines General Location Need and RGO Candidate Need. The first
covers food pressure, goods shortages, population/workforce pressure, development, control, market
access, existing levels, recent construction, and wait time. The second covers raw-material supply and
demand, price, utilization, remaining expansion space, strategic category, base cost, and food
emergency. The current release has no separate player-adjustable weight. This ordering works only
inside the RGO class and cannot overtake a build type placed above RGO in Automated Build Order.

## Configuration and Implementation

- `policies/automation_rules.json`: cadence, thresholds, scores, and goods/building groups.
- `policies/building_catalog.json`: generated catalog of player-manageable vanilla buildings.
- `policies/video_building_priorities.json`: direct video scores and explicit user overrides.
- `policies/templates.json`: built-in presets, including roles, allowlists, bans, and priority goods.
- CMF Mod Settings: concurrent limit, annual pool, treasury reserve, price band, Automated Build Order,
  return requirement, five strategic switches, safety rules, RGO rules, and performance settings.
- [`building_quality_priorities.md`](building_quality_priorities.md): video-calibration seeds,
  vanilla upgrade inheritance, and the default-zero rule.
- `src/eu5autobuild/catalog_builder.py`: reads vanilla buildings and advances, then refreshes the
  catalog, unlock ages, and inherited priorities.
- `src/eu5autobuild/engine.py`: testable pure-Python mirror of the decision rules.
- `src/eu5autobuild/generator.py`: generates the actual EU5 scripts, GUI, and localization.
- `tests/test_automation_generator.py`: verifies cadence, budget, need scoring, upstream recovery,
  and RGO integration in generated scripts.

## Known Boundaries and Validation

- Vanilla exposes a base gold cost of 100 for all five RGO expansion methods, and the Mod uses that
  value for budget settlement. `rgo_budget_cost` in `automation_rules.json` is only the vanilla
  base-cost mirror needed when generating the scripts; generation rejects a value that differs from
  any of the five vanilla prices. The vanilla GUI can display the live cost after modifiers, but the
  current scripted-effect path does not use an equivalent readable script value, so country,
  location, and other dynamic RGO-cost modifiers are not yet reflected in this Mod's budget
  accounting. In other words, the missing value is the modified live cost, not the vanilla base-cost
  data.
- This Mod marks a location after confirming a project start and clears the marker once that location
  has no civil construction. If the player later adds manual work in the same location, the slot
  remains conservatively occupied until all civil construction there finishes.
- Static tests verify real EU5 IDs, generated files, brace balance, and key script interfaces. An
  optional interface smoke test also runs when local `script_docs` are available.

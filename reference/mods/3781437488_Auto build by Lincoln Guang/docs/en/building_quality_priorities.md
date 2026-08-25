# Recommended Building Priorities

English | [Simplified Chinese](../zh-CN/building_quality_priorities.md)

## How Priorities Work

Each building has a recommended priority from 0 to 10. Built-in presets and custom templates created
with recommended values use these priorities. A blank template starts with every building at 0 so the
player can decide what it should build:

- `0`: do not build automatically. A built-in preset may still enable a specific zero-priority building
  when it is needed for that preset's purpose.
- `2–4`: low demand, low efficiency, or useful only in limited or location-specific situations.
- `5–7`: situationally useful through consistently strong.
- `8–9`: core production-chain or high-impact local buildings.
- `10`: top-priority foundational infrastructure across most situations.

In **Supply-Demand Planning**, each priority point adds 50 planning-score points. This separates
similar buildings but remains weaker than food emergencies, construction-good shortages, and broken
upstream supply. The overall order is therefore survival needs and production bottlenecks first,
followed by building quality and market price. Building priority also cannot overtake Automated Build Order.
Planning Candidates per Location (3–30) controls how many high-scoring projects per location and
ordinary build type remain as fallbacks, and is shown and used only in this mode.

In **Predicted Profit Selection**, planning score first keeps the configured 3–30 Profit Candidates per
location and current ordinary build type. The game-predicted monthly profit then determines the order. When profits
are close, each priority point adds about 1% relative weight, up to about 10% at priority 10. A clearly
larger predicted profit still wins. Profit Candidates per Location is shown and used only in this mode.

## Rating Sources and Inheritance

The recommended values draw on EU5 building reviews and a farming guide from
[Shou Bianbian on Bilibili](https://space.bilibili.com/456154809), together with the production chains
and upgrade relationships defined by the game.

The source material includes a three-part building review and a general farming guide. Building
reviews set the starting priorities, while the broader guide helps check production-chain relationships:

- Wool → cloth → fine cloth is a consistently strong chain: wool upstream buildings use 7, the cloth
  chain uses 8 throughout, and the fine-cloth chain uses 9 throughout.
- Lumber → coal → iron → tools becomes stronger over time but is constrained by early iron supply:
  chain buildings use at least 6, while core lumber, iron, and tool nodes use 8–9.
- Lumber/cloth → paper → books has long-term value even though paper itself tends to be cheap: the
  paper upgrade chain uses 7 and the books/printing upgrade chain uses 6.
- Rare RGO locations such as iron and gold should not be sacrificed casually for urbanization; lumber
  can be supplemented with lumber mills.
- Tools usually have broad demand and export potential; glass, firearms, and cannons serve
  progressively narrower markets.

Because the transcripts contain speech-recognition errors, names were corrected against game
definitions and actual upgrade relationships. The evidence labels below mean:

- `Direct`: the video directly evaluates the building or an unambiguous equivalent function.
- `Inherited`: the building inherits its predecessor's score through the game's upgrade relationship.
  When several predecessors lead to one building, the highest score is used.
- `Uncalibrated`: the video supplies no score and the building has no predecessor from which to
  inherit, so it is strictly zero.
- `User override`: an explicit user value that takes precedence over video scores and inheritance.

## Recommended Priorities

The table lists buildings with a direct source, a manual adjustment, or an important inherited value.
Buildings without enough evidence and without a scored predecessor remain at 0 by default; players
can still change them in a custom template.

| Building ID | Score | Evidence | Rationale |
| --- | ---: | --- | --- |
| `windmill` | 9 | Direct | Low-input local food-output multiplier; the video rates it as a strong building. |
| `irrigation_systems` | 9 | Direct | High-value food-province multiplier that pairs well with granaries. |
| `fishing_village` | 5 | Direct | Coastal raw-material sites gain port, control, and sailor value, but the benefit is strongly location-dependent. |
| `farming_village` | 7 | Direct | Each level raises local raw-material output, producing reliable returns over several levels. |
| `granary` | 10 | Direct | Core population-growth and food-capacity infrastructure that reduces food-conversion losses. |
| `salt_collector` | 3 | Direct | Salt is useful, but the building is inefficient and should be built sparingly when supply is short. |
| `fruit_orchard` | 0 | Direct | The video explicitly describes it as an inefficient use of population, so automation disables it. |
| `fiber_crops_farm` | 6 | Direct | Fiber feeds textiles and shipbuilding; it is solid but weaker than sheep farms that also produce food. |
| `cotton_plantation` | 0 | Uncalibrated | No direct video score and no predecessor building, so automation disables it by default. |
| `sheep_farms` | 7 | Direct | Provides wool and food and is the video's preferred textile upstream source. |
| `rural_clothmaker` | 8 | User override | Converts wool directly into cloth and belongs to the stable textile chain. |
| `dyes_workshop` | 4 | Direct | Appropriate only with surplus lumber and advanced textile demand; unsuitable for broad early expansion. |
| `cloth_guild` | 8 | User override | Root of the cloth upgrade chain, aligned with the later cloth workshop. |
| `cloth_workshop` | 8 | Direct | Cloth serves population needs and connects to fine cloth, paper, and other chains. |
| `cloth_manufactory` | 8 | Inherited | Inherits 8 through the cloth upgrade chain. |
| `textile_mill` | 8 | Inherited | Final cloth-chain upgrade; inherits 8. |
| `fine_cloth_guild` | 9 | User override | Root of the fine-cloth upgrade chain, aligned with its later high-profit buildings. |
| `fine_cloth_workshop` | 9 | Direct | Fine cloth has broad demand and high value, making this a clearly strong industry. |
| `fine_cloth_manufactory` | 9 | Inherited | Inherits 9 through the fine-cloth upgrade chain. |
| `fine_cloth_mill` | 9 | Inherited | Final fine-cloth-chain upgrade; inherits 9. |
| `tools_guild` | 9 | Direct | Tools have broad demand, profit, and export potential, provided iron shortages are controlled. |
| `tools_workshop` | 9 | Inherited | Inherits the high priority of the tools chain and gains value from later production capacity. |
| `iron_foundry` | 9 | Inherited | Final tools-chain upgrade; still constrained by iron supply. |
| `iron_mill` | 9 | Inherited | Highest-capacity final tools-chain upgrade; inherits 9. |
| `paper_guild` | 7 | User override | Root of the paper upgrade chain; cheap paper still supports the long-term books chain. |
| `paper_workshop` | 7 | Direct | Paper production is valuable and feeds books, although low prices limit standalone profit. |
| `paper_manufactory` | 7 | Inherited | Inherits 7 through the paper upgrade chain. |
| `paper_mill` | 7 | Inherited | Inherits the paper chain's medium-high priority. |
| `scriptorium` | 6 | User override | Root of the books/printing upgrade chain, standardized at 6. |
| `printing_press_shop` | 6 | Inherited | The printing press shop inherits 6 through the books chain. |
| `printing_manufactory` | 6 | Inherited | The printing manufactory inherits 6 through the upgrade chain. |
| `printing_mill` | 6 | Inherited | Final printing-chain upgrade; inherits 6. |
| `glass_workshop` | 6 | Direct | Demand supports some capacity, though profitability is usually weaker than tools. |
| `glassworks` | 6 | Inherited | Inherits the glass chain's moderately high priority. |
| `mason` | 9 | Direct | Masonry is required by many construction projects and must remain available even when its price is low. |
| `lumber_mill` | 8 | Direct | Essential during lumber shortages and can free raw-lumber RGO locations for urbanization. |
| `tar_kiln` | 3 | Direct | Tar demand is narrow and estates may build their own capacity, so expansion should follow actual shortages. |
| `naval_supplies_workshop` | 3 | Direct | Naval-supplies demand is limited and does not support broad expansion. |
| `marketplace` | 6 | Direct | Improves market capacity, access, and commercial strength, but depends on trade scale and burgher power. |
| `market_warehouse` | 6 | Direct | Buffers inventories before major construction cycles and reduces abrupt supply drops. |
| `caravanserai` | 4 | Direct | Market-attraction value is situational; one in a market center is usually sufficient. |
| `port_authority` | 0 | Uncalibrated | No direct video score and no predecessor building, so automation disables it by default. |
| `commerce_center` | 6 | Inherited | Inherits `marketplace` priority through the vanilla market-building upgrade chain. |
| `funduq` | 0 | Uncalibrated | No direct video score and no predecessor building, so automation disables it by default. |
| `dock` | 8 | Direct | Sailors and port capacity are nearly essential for naval play; preset whitelists control non-naval use. |
| `dry_dock` | 8 | Inherited | Inherits the dock chain's high conditional naval priority. |
| `shipyard` | 8 | Inherited | Inherits the dock chain's high conditional naval priority. |
| `grand_shipyard` | 8 | Inherited | Inherits the dock chain's high conditional naval priority. |
| `naval_base` | 8 | Inherited | Final dock-chain building for supporting large fleets. |
| `protected_harbor` | 0 | Uncalibrated | No direct video score and no predecessor building, so automation disables it by default. |
| `stockade` | 0 | User override | Automated stockade construction is disabled by default. |
| `castle` | 0 | User override | Automated castle construction is disabled by default. |
| `bastion` | 0 | Inherited | Inherits the castle chain's user-set zero. |
| `star_fort` | 0 | Inherited | Inherits zero through the castle fortification chain. |
| `fortress` | 0 | Inherited | Final fortification upgrade; inherits zero through the castle chain. |
| `city_walls` | 0 | Direct | The video calls it expensive and warns that it strengthens burghers and distorts market attraction. |
| `armory` | 7 | Direct | Efficient manpower infrastructure for standing armies, but less valuable for mercenary-heavy play. |
| `training_fields` | 0 | Uncalibrated | A separate rural manpower building in vanilla, not an `armory` upgrade, so it remains zero. |
| `barracks` | 7 | Inherited | Inherits the manpower chain's conditional high value. |
| `horse_breeders` | 3 | Direct | Primarily serves nobles and cavalry, which limits aggregate demand. |
| `weapon_workshop` | 7 | Direct | Weapons have broad demand and are easier to absorb than cannons within the military industry. |
| `weapon_factory` | 7 | Inherited | Inherits the weapons chain's medium-high priority. |
| `cannon_workshop` | 3 | Direct | Cannon demand is low, so only military-industry templates should fill actual shortages. |
| `cannon_foundry` | 3 | Inherited | Inherits the cannon chain's low-volume, situational role. |
| `bog_iron_smelter` | 8 | Direct | Coal-to-iron conversion is powerful and relieves a key bottleneck, subject to location and era efficiency. |
| `local_smelters` | 9 | Direct | Strong local metal-output multiplier with low labor and input requirements. |
| `charcoal_maker` | 6 | User override | Key lumber-to-coal upstream building, raised to 6 for the complete coal-iron-tools chain. |
| `improved_charcoal_maker` | 6 | Inherited | Inherits 6 through the charcoal-building upgrade chain. |
| `mercury_patio` | 0 | Uncalibrated | Hospital mercury consumption is not a direct evaluation of this building, and it has no predecessor. |
| `jewelry_guild` | 2 | Direct | Difficult to run profitably for most countries; useful only with cheap precious metals and trade control. |
| `stone_quarry` | 3 | Direct | Add only when native quarry capacity is exhausted and stone is genuinely scarce. |
| `porcelain_manufactory` | 0 | Inherited | Its predecessor has no video score, so the entire porcelain upgrade chain remains zero. |
| `perfumery` | 0 | Uncalibrated | No direct video score and no predecessor building, so automation disables it by default. |

## Developer Notes

The catalog checks 465 building definitions and includes 317 that players can manage. It excludes
event-only, estate-owned, permanently unavailable, and upgrade-proxy definitions. Of the included
buildings, 31 use direct video ratings, eight have manual adjustments, 66 inherit through upgrade
chains, and 212 have no rating source. The final set contains 63 nonzero priorities and 254 zeros.

- `policies/automation_rules.json` stores the range, default, score multiplier, and effective overrides
  under `building_priorities`.
- `policies/video_building_priorities.json` stores only direct video scores and explicit user overrides.
- `src/eu5autobuild/catalog_builder.py` collects player-manageable buildings and generates the complete
  priority table through vanilla `obsolete` chains.
- `src/eu5autobuild/rules.py` validates that every value is between 0 and 10.
- `src/eu5autobuild/generator.py` writes the values into recommended custom templates, initializes
  blank templates to zero, applies the same base scores to presets, and creates an independent player
  template when a preset is copied. The editor supports 0.1/0.5/1.0 click steps and can clear the
  currently visible workforce-and-age filter intersection.
- `src/eu5autobuild/engine.py` mirrors the same ranking behavior: custom zero values disable a
  candidate, while an explicit built-in preset allowlist overrides the global zero fallback.

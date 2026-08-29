# EU5 Advanced Auto Build

English | [简体中文](README.zh-CN.md)

EU5 Advanced Auto Build is an unofficial automated regional construction planning mod for *Europa Universalis V*.

Current version: **0.9.4 Beta**.

The entire mod—including architectural design, code implementation, test suites, generated game scripts, GUI layout, multilingual localization, and documentation—was created with the assistance of OpenAI's GPT-5.6-Sol (Sol 5.6) model.

Players can configure flexible templates to specify allowed building types and priorities for different locations, while centrally managing national budgets, workforce safeguards, construction safety limits, and decision strategies via CMF Mod Settings. Full execution details of each monthly construction cycle can be inspected directly in the in-game Construction Report.

This project is an unofficial fan-made mod and is not affiliated with, endorsed by, or supported by Paradox Interactive.

## Required Dependencies

**Community Mod Framework - 1.3 Pavia** (CMF) must be installed and enabled before running the game. This mod depends on CMF for its unified Action Bar entry point and Mod Settings interface. The mod metadata declares this dependency as `community_mod_framework` with compatible version `2.*`.

Running the build scripts and test suites requires Python 3.12 or newer. The Python tooling uses only the standard library and requires no third-party runtime dependencies.

## Key Features

- **Flexible Scope Assignment**: Apply regional development templates to individual locations, entire provinces, or whole areas; customize allowed and banned building lists for each template.
- **Intelligent Need & Priority Evaluation**: Holistically evaluates regional specialization, output goods, annual budgets, market prices, and labor supply; projects are prioritized by food security, construction material bottlenecks, civilian necessities, military readiness, upstream raw materials, market supply/demand, and price tiers.
- **Game-Engine Yield Validation**: Queries the game engine's predicted monthly income, monthly profit, and actual construction costs before starting ordinary production buildings. The selected threshold can require monthly income above 0, monthly profit above 0, annualized income ROI of at least 5%, or annualized profit ROI of at least 5% (roughly a 20-year payback).
- **Dual Decision Modes**:
  - **Supply-Demand Planning**: Focuses on market balance, closed-loop supply chains, and workforce safety, with a configurable 3–30 candidate pool.
  - **Predicted Profit Selection**: Pre-filters candidates and selects by highest game-predicted monthly profit while satisfying all safety rules, using template building priorities (0–10) as a soft tiebreaker for closely matched profits (~1% weight per point, up to ~10%). Features a dedicated 3–30 profit candidate pool.
- **Building Priorities**: Flavor templates and newly created recommended templates provide 0–10 building priorities; blank templates start with all buildings disabled. Later buildings in an upgrade chain automatically inherit their predecessor's priority, while unrated buildings default to 0. Flavor templates may selectively enable specific 0-priority buildings by design, but in custom templates 0 always means completely disabled.
- **Shared Annual Budget & Treasury Safety**: All presets and custom templates share a unified national annual budget pool (a fixed amount or 4×/6×/8× monthly total income); set a minimum treasury reserve floor from 0 to 100,000 gold in steps of 100, such as keeping at least 1,000 gold to avoid an empty treasury. Ordinary buildings use the game's actual construction cost, while RGO expansions use the base cost of 100 gold.
- **Workforce & Input Safeguards**: Blocks construction when the local population in the required estate is insufficient, preventing empty, unstaffed buildings. When **Build Upstream Sources on Shortage** is enabled, the system can redirect a downstream project blocked by missing inputs to an allowed upstream supplier that provides the scarce material.
- **Special Building Toggle**: CMF Mod Settings controls whether automated construction may build or upgrade special buildings; enabled projects must still satisfy the base game's construction requirements.
- **Customizable Build Order**: Freely order the execution sequence of the 4 build types (building upgrades, existing building expansions, RGO expansions, and new buildings; default order: Upgrades → Expansions → RGOs → New Buildings); the system exhausts all feasible projects in the active type before proceeding to the next.
- **Crisis Emergency Overrides**: When market food is projected to run out or reserves fall to ≤ 25%, food production projects are prioritized and exempt from return requirements; severe construction material shortages, wartime military goods, and blocked strategic upstream chains can also selectively waive return thresholds.
- **Prudent RGO Expansion**: The minimum RGO job-utilization threshold is adjustable from 0% to 100% in steps of 5%, with a default of 75%, preventing wasteful expansion in labor-starved locations. Candidates are ranked only within the RGO build type by raw-material deficits, market prices, current utilization, strategic needs, and food pressure. RGOs share the global build capacity without a separate monthly cap; if the base game rejects an expansion, no budget is deducted.
- **Non-Intrusive Concurrency & Cooldowns**: Configure extra concurrent builds (0 = max 1 project, 599 = total 600) via the CMF slider; manual player construction, roads, and other mods never consume this quota. Each location may have at most one civil construction project active at a time and enters a 3-month cooldown when a project starts.
- **Staggered Scanning for Smooth Performance**: Locations with assigned templates are scanned in batches from day 2 to 21, and projects are committed on day 22, avoiding a single concentrated scan; multiple built-in performance presets allow adjustment of daily scanning throughput and maximum starts per cycle.
- **In-Game Construction Report**: Provides an intuitive Construction Report panel to review recent monthly build starts, actual costs, predicted yields, and detailed rejection reasons for unstarted candidate projects.
- **Shared National Settings**: Concurrent limits, budgets, treasury reserves, price bands, decision strategy, special buildings, upstream construction, workforce and input safeguards, build order, return thresholds, emergency rules, and RGO rules are configured centrally in CMF Mod Settings and shared by every template.

Default building priority ratings were inspired by EU5 guide content from [Shou Bianbian on Bilibili](https://space.bilibili.com/456154809).

## Developer: Project Structure

```text
.metadata/
  metadata.json
  thumbnail.png
docs/en/
docs/zh-CN/
in_game/
policies/
README.zh-CN.md
src/eu5autobuild/
tests/
```

Important files:

- `policies/templates.json`: Maintains the built-in preset definitions and their default building rules. Copying a preset creates an independent player template without altering the default list of custom template names.
- `policies/building_catalog.json`: Contains the catalog of player-manageable vanilla buildings extracted from game data, mapped to output/input goods, workforce pop types, tech eras, and special building flags.
- `policies/video_building_priorities.json`: Stores direct transcript scores and explicit manual priority overrides.
- `policies/automation_rules.json`: Defines evaluation cadence, market thresholds, scoring weights, building quality tiers, and goods/building categories.
- `docs/en/building_quality_priorities.md`: Documents the priority ranking rationale and vanilla upgrade inheritance.
- `src/eu5autobuild/generator.py`: Generates EU5 mod files, localization, and GUI scripts.
- `localization/translations/*.json`: Stores reviewed Brazilian Portuguese, French, German, Japanese, Korean, Polish, Russian, Spanish, and Turkish text together with the Chinese and English source strings they were translated from.
- `src/eu5autobuild/catalog_builder.py`: Refreshes the building catalog directly from game files and propagates upgrade priorities along vanilla `obsolete` chains.
- `src/eu5autobuild/rules.py`: Validates and exposes data-driven rule schemas.
- `src/eu5autobuild/engine.py`: Provides a testable, pure-Python reference implementation of the decision algorithms.
- `docs/en/automation_rules.md`: Documents the complete automation rules and system mechanics.
- `tests/`: Contains comprehensive unit tests for policy data, generated files, construction decisions, and game script integration.

When generating the nine supported languages, the generator uses a reviewed translation only if both recorded source strings still match the current Simplified Chinese and English values. A new key or a changed source string automatically falls back to the current English text, ensuring feature updates do not require immediate retranslation while preventing outdated translations from being used silently. Running `python3 -m src.eu5autobuild.generator --check` outputs a non-blocking per-language summary of translated, missing, changed, and obsolete entries. Checked-in English and Simplified Chinese localizations remain the primary source of truth and are never overwritten by this merge logic.

Running `python3 -m src.eu5autobuild.localization_check` validates translation JSONs, source string sync, EU5 markup, UTF-8 BOM/CRLF formatting, and byte-identical `in_game`/`main_menu` outputs without requiring an installed copy of EU5. GitHub Actions runs this same validation on pull requests involving localization. Missing, changed, or obsolete translations produce warnings (since they cleanly fall back to English); syntax errors, damaged markup, stale generated files, or inconsistencies between game layers will fail the check. Translation JSONs use LF line endings on all platforms, while generated EU5 localizations always use CRLF.

## Developer: Policy Data

Policy templates define:

- Template ID and localization keys
- Regional role focus
- Priority goods list
- Allowed building set
- Banned building set

Player templates persist only their identifier, enabled/paused state, assigned scope, and per-building 0–10 priorities. Country-level parameters—such as concurrent build caps, annual budget mode, Automated Build Order, return criteria, emergency switches, and RGO thresholds—are managed globally through CMF Mod Settings and shared across all templates.

The building catalog defines:

- Building ID
- Output goods
- Input goods (used to detect upstream supply shortages)
- Workforce pop types
- Special building flags
- Optional explicit mappings from goods to upstream source buildings

If vanilla EU5 building IDs, goods IDs, or pop type IDs change, run the catalog builder first, then regenerate the mod files. The catalog automatically excludes event-only placeholders, estate-owned buildings, and definitions with `country_potential = { always = no }`; buildings with country, culture, religion, foreign, unique, or organization triggers are retained and remain gated by vanilla construction requirements.

The catalog uses genuine EU5 `building_types`, `goods`, and `pop_types` IDs. Certain infrastructure and RGO-supporting buildings do not declare a direct `produced = ...` field in vanilla scripts; for these, `output_goods` specifies the real goods they boost or support, allowing the scoring engine to rank candidates correctly.

## Developer: Generate Mod Files

The repository does not hardcode machine-specific Steam library paths. Configure the EU5 installation root with `EU5_GAME_ROOT` before running either generator:

```powershell
$env:EU5_GAME_ROOT = "D:\path\to\SteamLibrary\steamapps\common\Europa Universalis V"
```

Alternatively, pass `--game-root PATH` to either command; explicit command-line arguments take precedence over environment variables. If neither is provided, the generator exits with a clear error rather than guessing a local path.

Run:

```bash
python3 -m src.eu5autobuild.catalog_builder
python3 -m src.eu5autobuild.generator
```

For example, without setting environment variables:

```powershell
python -m src.eu5autobuild.catalog_builder --game-root "D:\path\to\Europa Universalis V"
python -m src.eu5autobuild.generator --game-root "D:\path\to\Europa Universalis V"
```

Generated files are written to:

```text
.metadata/*.json
in_game/
main_menu/localization/
```

The static mod icon is stored at `.metadata/thumbnail.png` and referenced by `metadata.json`.

Use `--check` to validate generated content without writing files to disk:

```bash
python3 -m src.eu5autobuild.catalog_builder --check
python3 -m src.eu5autobuild.generator --check
```

## Developer: Run Tests

Run:

```bash
python3 -m unittest
```

The test suite covers:

- Required policy fields
- Default template coverage
- Building catalog coverage
- Generated file set integrity
- Brace balancing for generated EU5 scripts
- Localization key coverage
- Construction rule priorities
- Banned and allowed building behavior
- Budget and cash-reserve blocking logic
- Price-band blocking logic
- Workforce and pop-type blocking logic
- Input shortage blocking logic
- Upstream input-source construction
- Draggable four-type Automated Build Order and default order
- Emergency food priority and dual switch-controlled return exemptions
- Actual income/profit/ROI validation, construction material headroom, budget reservations, and queue growth settlement
- Retry logic for alternative projects of the same type upon vanilla rejection, advancing only after exhaustion
- RGO category positioning, unlimited starts within shared capacity, and internal location ranking
- Decoupling locations from province templates
- Optional validation of policy/catalog IDs against local EU5 `building_types`, `goods`, and `pop_types`

When local EU5 `script_docs` are present, script interface names are validated additionally; the absence of that optional directory does not skip other real game data validations.

## Installation & Usage

You can use this repository directory directly as a local EU5 mod folder, or copy it into the local *Europa Universalis V* mod directory recognized by the Paradox launcher.

The generated mod requires the following top-level structure:

```text
.metadata/
  metadata.json
  thumbnail.png
in_game/
```

After copying or linking the mod folder:

1. Enable both this mod and Community Mod Framework in the game launcher.
2. Start a new game or load an existing save.
3. Open the EU5 Advanced Auto Build panel from the Community Mod Framework (CMF) Action Bar.
4. In CMF Mod Settings, configure the global rules shared across all templates (concurrent build limit, minimum treasury reserve, budget mode, price bands, decision strategy, build order, return thresholds, emergency overrides, special-building and upstream-construction toggles, workforce and input safeguards, and RGO rules).
5. Create a blank template or use a template initialized with recommended priorities, then configure its enabled/paused state, geographic scope, and per-building 0–10 priorities. Click adjusts by 0.1, Ctrl+click by 0.5, and Shift+click by 1.0; `Clear Current List` resets only the buildings visible under current filters to 0.
6. Apply the template to locations, provinces, or areas; use `Clear Policy` whenever you wish to unbind a location.
7. Let the game advance to day 22 of the next month for automated construction to execute; review started projects and rejection reasons in the Construction Report.

## Known Limitations

- Vanilla EU5 currently lacks a script interface to persist custom template names across saves. All rules and location bindings within templates are fully preserved, but custom template names will revert to their default slot names upon reloading a save.
- Vanilla RGO expansions have a uniform base cost of 100 gold, which this mod uses for budget deduction. Dynamic country- or location-level construction cost modifiers are not yet included in RGO budget accounting.

## Possible Future Features

- **Automatic Imports for Scarce Inputs**: A stable, general-purpose game engine interface has not yet been identified, so this is not currently implemented.
- **Automatic Production Method Switching**: Vanilla EU5 already provides global automation and per-building locks; this mod currently lacks better algorithms and script interfaces for it, so it is not duplicated for now.
- **Automatic Town Rights**: This mod does not currently grant town rights automatically.

## Acknowledgements & Inspiration

Part of this mod's design was inspired by the following mods. Many thanks to their authors and maintainers:

- [Community Mod Framework - 1.3 Pavia](https://steamcommunity.com/sharedfiles/filedetails/?id=3692202776)
- [[1.3 & 1.2] Construction Manager / 建筑管理器](https://steamcommunity.com/sharedfiles/filedetails/?id=3736668860)

## Contributing & Support

Pull requests are welcome! If you would like to improve the code, balance, localization, documentation, or user interface, feel free to open a pull request.

If you encounter a bug, have a question, or wish to propose a new feature, please open a GitHub Issue and include any relevant reproduction steps, screenshots, save file details, or game logs.

## License

This project is licensed under the [MIT License](LICENSE).

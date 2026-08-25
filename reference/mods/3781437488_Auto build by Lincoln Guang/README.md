# EU5 Advanced Auto Build

English | [简体中文](README.zh-CN.md)

EU5 Advanced Auto Build is an automated regional construction planning mod for Europa Universalis V.

Current version: **0.9.3 Beta**.

The entire mod—including its architecture, code, test suites, generated game scripts, GUI layout, localization, and documentation—was created with the assistance of OpenAI's GPT-5.6-Sol (Sol 5.6) model.

Players can configure tailored regional development templates to guide location construction priorities, while sharing budget, workforce protection, construction safety, and decision strategies globally via CMF Mod Settings. The in-game Construction Report provides full visibility into the latest monthly construction cycle.

This project is an unofficial fan-made mod and is not affiliated with, endorsed by, or supported by Paradox Interactive.

## Required Dependency

**Community Mod Framework - 1.3 Pavia** is required at runtime. Please install and enable it before running EU5 Advanced Auto Build. CMF provides both the shared Action Bar entry point and the Mod Settings panel. The mod metadata declares this dependency as `community_mod_framework` (compatible framework version `2.*`).

Running the mod generators and test suites requires Python 3.12 or newer. The Python tooling uses only standard library modules and requires no third-party runtime dependencies.

## Key Features

- **Granular Scope Assignment**: Apply development templates to individual locations, whole provinces, or entire areas.
- **Intelligent Need-First Planning**: Prioritize projects based on food security, construction material bottlenecks, civilian necessities, military readiness, upstream raw material dependencies, market supply/demand, and price signals.
- **Game-Engine Yield Validation**: Query game-predicted monthly income, monthly profit, and actual construction costs before committing builds, ensuring projects satisfy the player's chosen economic return thresholds.
- **Flexible Decision Strategies**:
  - **Supply-Demand Planning**: Evaluates holistic supply-chain balance and raw material flow, with a configurable 3–30 candidate fallback pool per location and ordinary build category.
  - **Predicted Profit Selection**: Pre-filters a configurable 3–30 candidates per location and ordinary build category, then selects by highest game-predicted monthly profit, using template building priorities (0–10) as a soft tiebreaker for closely matched profits (~1% weight per point, up to ~10%). This shortlist setting is visible and active only in this strategy and is synchronized by performance presets.
- **Calibrated Building Priorities**: Built-in presets and recommended templates feature 0–10 priority ratings calibrated from community testing. Custom templates start with all buildings set to 0 (disabled), giving full manual control.
- **Shared Annual Budget & Treasury Protection**: Manage a unified annual budget pool (fixed amount or 4×/6×/8× monthly income) and set a minimum treasury reserve safety floor (e.g. keep at least 1,000 gold).
- **Workforce & Input Protection**: Prevent overbuilding when local population or required industrial inputs cannot support new jobs.
- **Configurable Build Order**: Freely order the 4 automated build types: building upgrades, existing building expansions, RGO expansions, and new buildings.
- **Strategic Crisis Overrides**: Automatically prioritize food production during severe shortages and selectively waive return requirements for vital war supplies or blocked strategic chains.
- **Automated Upstream Expansion**: Optionally construct missing raw material sources when downstream industries face input shortages.
- **Non-Intrusive Concurrency**: Set an extra concurrent build limit (0 to 599, total 1 to 600) via CMF slider; manual builds, roads, and other mods never consume this quota.
- **Staggered Monthly Processing**: Locations are checked in batches between days 2–21 and projects are committed on day 22, preventing single-day performance spikes.
- **In-Game Construction Report**: Review recent monthly builds, actual costs, predicted yields, and detailed pass/fail diagnostics.

The default video-calibration priority ratings were inspired by EU5 guide content from [Shou Bianbian on Bilibili](https://space.bilibili.com/456154809).

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

- `policies/templates.json` defines the built-in preset definitions and their default building rules.
- `policies/building_catalog.json` contains the catalog of player-manageable vanilla buildings, mapped to goods, pop types, and tech eras.
- `policies/video_building_priorities.json` stores direct transcript scores and explicit manual priority overrides.
- `policies/automation_rules.json` defines evaluation cadence, market thresholds, scoring weights, and building quality tiers.
- `docs/en/building_quality_priorities.md` documents the priority ranking rationale and vanilla upgrade inheritance.
- `src/eu5autobuild/generator.py` generates EU5 mod files, localization, and GUI scripts.
- `src/eu5autobuild/catalog_builder.py` refreshes the building catalog directly from game files and propagates upgrade priorities.
- `src/eu5autobuild/rules.py` validates rule schemas and data constraints.
- `src/eu5autobuild/engine.py` provides a testable Python implementation of the decision algorithms.
- `docs/en/automation_rules.md` documents the complete automation rules and system mechanics.
- `tests/` contains comprehensive unit tests for generator logic, script syntax, budget calculations, and decision algorithms.

## Developer: Policy Data

Policy templates define:

- Template ID and localization keys
- Regional role focus
- Priority goods list
- Allowed and banned building sets

Player templates persist only their slot assignment, enabled/paused state, assigned geographic scope, and per-building 0–10 priorities. Country-level parameters—such as the concurrent build cap, annual budget mode, Automated Build Order, return criteria, crisis overrides, and RGO thresholds—are managed globally through CMF Mod Settings.

The building catalog defines:

- Building ID
- Output goods
- Input goods (used to evaluate upstream supply chain bottlenecks)
- Workforce pop types
- Special building flags
- Explicit upstream dependency mappings

If actual EU5 building IDs, goods IDs, or pop type IDs change, run the catalog builder and then regenerate the mod files. Event-only placeholders, estate-owned buildings, and definitions with `country_potential = { always = no }` are excluded; conditional country, culture, religion, foreign, unique, and organization buildings remain available and are still gated by vanilla construction checks.

The catalog uses real EU5 `building_types`, `goods`, and `pop_types` IDs. Some infrastructure and RGO-helper buildings do not declare a direct `produced = ...` field in vanilla files; for those, `output_goods` represents the real goods they boost or support so the scoring engine can still rank candidates.

## Developer: Generate Mod Files

The repository does not embed a machine-specific Steam library path. Configure
the EU5 installation root with `EU5_GAME_ROOT` before running either generator:

```powershell
$env:EU5_GAME_ROOT = "D:\path\to\SteamLibrary\steamapps\common\Europa Universalis V"
```

Alternatively, pass `--game-root PATH` to either command. An explicit argument
takes precedence over the environment variable. If neither is provided, the
generator exits with an error instead of guessing a local installation path.

Run:

```bash
python3 -m src.eu5autobuild.catalog_builder
python3 -m src.eu5autobuild.generator
```

For example, without setting an environment variable:

```powershell
python -m src.eu5autobuild.catalog_builder --game-root "D:\path\to\Europa Universalis V"
python -m src.eu5autobuild.generator --game-root "D:\path\to\Europa Universalis V"
```

Generated files are written to:

```text
in_game/
.metadata/metadata.json
```

The static Mod icon is stored at `.metadata/thumbnail.png` and referenced by `metadata.json`.

Use `--check` to validate generated content without writing files:

```bash
python3 -m src.eu5autobuild.catalog_builder --check
python3 -m src.eu5autobuild.generator --check
```

## Developer: Run Tests

Run:

```bash
python3 -m unittest
```

The tests cover:

- Required policy fields
- Default template coverage
- Building catalog coverage
- Generated file set
- Brace balancing for generated EU5 scripts
- Localization key coverage
- Construction rule priority
- Banned and allowed building behavior
- Budget and cash-reserve blocking
- Price-band blocking
- Labor and workforce-pop blocking
- Input shortage blocking
- Upstream input-source construction
- Draggable four-type Automated Build Order and its default order
- Emergency food priority and the two switch-controlled return exceptions
- Predicted monthly income/profit/return validation, construction-material headroom, reservation, and queue-growth settlement
- Retry another project of the same type after the game rejects one, and move to the next type only after that type is exhausted
- RGO class placement, unlimited-within-shared-cap starts, and within-class location ordering
- Stopping a location from following its province template
- Optional validation of policy/catalog IDs against local EU5 `building_types`, `goods`, and `pop_types`

When local EU5 `script_docs` are available, the tests also validate script-interface names. The absence of that optional directory does not skip the other installed-game data checks.

## Installation

Use this directory as a local EU5 mod folder, or copy it into the local Europa Universalis V mod directory used by the launcher.

The generated mod expects the following top-level structure:

```text
.metadata/
  metadata.json
  thumbnail.png
in_game/
```

After copying or linking the mod folder:

1. Enable the mod in the launcher.
2. Start a new game or load an existing save.
3. Open EU5 Advanced Auto Build from the Community Mod Framework Action Bar.
4. In CMF Mod Settings, configure the shared concurrent limit, treasury reserve, budget, price range, Construction Decision Strategy, Automated Build Order, return requirement, emergency switches, workforce/input protection, and RGO rules.
5. Create either a blank custom template or one initialized with recommended priorities, then configure its enabled/paused state, scope, and per-building 0–10 priority. Click adjusts by 0.1, Ctrl+click by 0.5, and Shift+click by 1.0; `Clear Current List` sets only the buildings visible under the current workforce and age filters to 0.
6. Apply a template to a location, province, or area; use `Clear Policy` to remove the assignment.
7. Wait for the next monthly 22nd to finish the first check, then review starts and rejection reasons in Construction Report.


## Known Limitations

- EU5 exposes no interface that this mod can use to persist custom template names permanently. Template settings remain available, but a custom name is restored to its default value after reloading a save.
- All five RGO expansion methods have a base-game gold cost of 100, which the Mod uses for budget
  settlement. Dynamic cost modifiers from the country, location, or other sources are not yet included
  in this Mod's RGO budget accounting.

## Possible Future Features

- **Automatic imports for scarce inputs:** no stable general-purpose target interface has been found for this Mod, so this is not implemented.
- **Production-method switching:** EU5 already provides global vanilla automation and per-building locks; this Mod currently lacks better algorithms and script interfaces for it, so it is not implemented for now.
- **Automatic town rights:** this Mod does not currently grant town rights automatically.

## Acknowledgements and Inspiration

Some of this mod's design ideas were inspired by the following mods. Many thanks to their authors and maintainers:

- [Community Mod Framework - 1.3 Pavia](https://steamcommunity.com/sharedfiles/filedetails/?id=3692202776)
- [[1.3 & 1.2] 建筑管理器 / Construction Manager](https://steamcommunity.com/sharedfiles/filedetails/?id=3736668860)

## Contributing and Support

Pull requests are welcome. If you would like to improve the code, balance, localization, documentation, or user interface, feel free to open a pull request.

If you encounter a bug, have a question, or want to suggest a feature, please open a GitHub Issue and include any relevant reproduction steps, screenshots, save information, or game logs.

## License

This project is licensed under the [MIT License](LICENSE).

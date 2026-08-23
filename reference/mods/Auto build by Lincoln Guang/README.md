# EU5 Advanced Auto Build

English | [Chinese](README.zh-CN.md)

EU5 Advanced Auto Build is an unofficial Europa Universalis V mod that uses regional-development templates to plan automated construction.

Current version: **0.9.1 Beta**.

The entire mod—including its design, code, tests, generated game scripts, interface, localization, and documentation—was created with assistance from OpenAI's GPT-5.6-Sol (Sol 5.6) model.

The mod is built as a hybrid project:

- Policy rules are defined as JSON data.
- Python generator code converts those rules into EU5 `generic_actions`, `scripted_gui`, `on_action`, `scripted_effect`, `scripted_trigger`, `script_value`, GUI, and localization files.
- The shared Community Mod Framework Action Bar opens template controls for enable/pause state, scope, per-building priority, and diagnostics. Shared runtime rules for every built-in and custom template live in CMF Mod Settings, without replacing another Mod's panel-tab types.
- Python unit tests validate the policy structure, generated files, and the core auto-build decision rules.

This project is an unofficial fan-made mod and is not affiliated with, endorsed by, or supported by Paradox Interactive.

## Required Dependency

Community Mod Framework - 1.3 Pavia is required at runtime. Install and enable it before EU5 Advanced Auto Build; it provides both the shared Action Bar entry point and CMF Mod Settings. The Mod metadata declares the dependency as `community_mod_framework`, compatible framework version `2.*`.

Running the generators and tests requires Python 3.12 or newer. The Python code uses only the standard library and has no third-party runtime dependencies.

## Features

- Apply development policies to individual locations or whole provinces.
- Prioritize construction by regional role, output goods, annual budget, price band, and workforce availability.
- Configure allowed buildings and banned buildings per policy.
- Configure a reserve fund, such as keeping at least 1000 gold in the treasury after construction starts.
- Toggle whether automated construction may build or upgrade special buildings.
- Rank projects from food security, construction bottlenecks, population basics, military supply, upstream inputs, market supply/demand, and prices. Before an ordinary production building starts, the game also checks its actual cost and the return standard selected by the player.
- Apply a video-calibrated 0–10 building-quality priority to both presets and new custom templates; actual vanilla upgrade successors inherit their predecessor's value, while buildings with no video score, user override, or inherited score default to 0. An explicit built-in preset allowlist may override a global 0, while 0 remains a hard disable in custom templates.
- Block automated construction when the local workforce class for the target building has no available population.
- Use a CMF slider to set this Mod's extra concurrent construction: 0 means at most 1 active project from this Mod and 599 means at most 600. Only projects confirmed by this Mod and still under construction count; manual construction, roads, and projects from other Mods do not use this limit. Each monthly check fills only this Mod's remaining slots. Each location allows one project at a time and waits three months after a successful start.
- Give every built-in and custom template one shared national annual pool. CMF Mod Settings selects a fixed amount or an income-linked ×4/×6/×8 budget, with actual building costs and the RGO base cost verified against vanilla data at generation time deducted from that pool.
- Adjust the country treasury reserve from 0 to 100,000 gold with a CMF slider, in steps of 100.
- Drag four build types into the preferred order: building upgrades, existing ordinary-building expansions, RGO expansions, and new ordinary buildings. The default is upgrade → ordinary expansion → RGO → new build; the Mod tries all viable projects of one type before moving to the next.
- Choose the return required from ordinary production buildings: positive income, positive profit, at least 5% annualized return on cost from income, or at least 5% annualized return on cost from profit.
- When food is expected to run out or is at or below 25%, handle food projects before all other work and let ordinary food buildings ignore the selected return requirement. The construction-supply, wartime-military, and blocked-strategic-input switches relax only the return requirement for matching buildings.
- Configure this Mod's concurrent limit, budget, reserve, price band, special-building behavior, upstream recovery, workforce/input protection, Automated Build Order, return requirement, emergency rules, and RGO rules once in CMF Mod Settings.
- Expand needed RGO capacity only when it is at least 75% utilized; failed native RGO calls do not consume the automation budget, and RGOs have no separate monthly cap beyond this Mod's remaining concurrent slots.
- Rank RGO locations directly from overall local need, raw-material shortage, price, utilization, strategic importance, and food pressure. There is no separate ranking-weight setting, and RGO expansion never moves ahead of a build type placed above it.
- Put eligible locations into twenty transient lists during the single monthly coverage pass, score only that day's list on days 2–21, then validate each retained candidate only in its one food/feature-priority phase and finalize the construction queue on day 22.
- Recover from input shortages by constructing a genuinely scarce upstream source when the normal policy candidate cannot be started.

The video-calibration seeds were inspired by EU5 content from [Shou Bianbian on Bilibili](https://space.bilibili.com/456154809).

## Project Structure

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

- `policies/templates.json` defines the separately maintained built-in preset list and its rules. Copying a preset creates an independent player template without adding preset names to the six custom-name choices.
- `policies/building_catalog.json` is the generated catalog of player-manageable vanilla buildings and maps them to output/input goods, workforce pop types, age, and special-building status.
- `policies/video_building_priorities.json` stores only direct transcript scores and explicit user overrides.
- `policies/automation_rules.json` defines cadence, market thresholds, need scores, building-quality priorities, and goods/building groups.
- `docs/en/building_quality_priorities.md` records the scoring policy and the transcript rationale for the video-calibrated set.
- `src/eu5autobuild/generator.py` generates EU5 mod files.
- `src/eu5autobuild/catalog_builder.py` refreshes the vanilla building catalog and propagates priorities through real `obsolete` upgrade chains.
- `src/eu5autobuild/rules.py` validates and exposes the data-driven rule schema.
- `src/eu5autobuild/engine.py` mirrors the needs-first decision rules in pure Python for testing.
- `docs/en/automation_rules.md` records the analysis and rule design.
- `tests/` contains unit tests for policy data, generated files, construction decisions, and game-script integration.

## Policy Data

Policy templates include:

- Policy ID and localization keys
- Regional role
- Priority goods
- Allowed buildings
- Banned buildings

Player templates persist only their identity, enabled/paused state, assigned scope, and per-building 0–10 priorities. The concurrent limit, budget, Automated Build Order, return requirement, emergency switches, RGO enablement, and minimum utilization are country-level CMF Mod Settings shared by all templates.

The building catalog includes:

- Building ID
- Output goods
- Input goods used to determine whether a building lacks required materials
- Workforce pop types
- Whether the building is treated as special
- Optional explicit mappings from goods to upstream source buildings

If actual EU5 building IDs, goods IDs, or pop type IDs change, run the catalog builder and then regenerate the mod files. Event-only placeholders, estate-owned buildings, and definitions with `country_potential = { always = no }` are excluded; conditional country, culture, religion, foreign, unique, and organization buildings remain available and are still gated by vanilla construction checks.

The catalog uses real EU5 `building_types`, `goods`, and `pop_types` IDs. Some infrastructure and RGO-helper buildings do not declare a direct `produced = ...` field in vanilla files; for those, `output_goods` represents the real goods they boost or support so the scoring engine can still rank candidates.

## Generate Mod Files

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

## Run Tests

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
- Actual income/profit/return validation, construction-material headroom, reservation, and queue-growth settlement
- Same-feature retry after an engine rejection and lower-feature fallback only after exhaustion
- RGO class placement, unlimited-within-shared-cap starts, and within-class location ordering
- Province template decoupling
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
4. In CMF Mod Settings, configure the shared concurrent-limit control, treasury reserve, budget, price band, Automated Build Order, return requirement, emergency switches, workforce/input protection, and RGO rules.
5. In the Mod window, configure each template's enabled/paused state, scope, and per-building 0–10 priority (0 disables a custom-template building).
6. Apply a template to a location, province, or area; use `Clear Policy` to remove the assignment.
7. Wait for the next monthly 22nd so the Mod can merge its first candidate batch and queue projects, then review the runtime diagnostics and construction queue.

## Known Limitations

- EU5 exposes no interface that this mod can use to persist custom template names permanently. Template settings remain available, but a custom name is restored to its default value after reloading a save.
- Vanilla's price table sets the base gold cost of all five RGO expansion methods to 100. The generator reads those entries and validates the mirror value used from `automation_rules.json`; it is neither an independent estimate nor a tunable balance parameter. This Mod uses the vanilla base cost for budget settlement. The current scripted-effect path cannot read the live RGO cost after country, location, and other modifiers, so those dynamic modifiers are not yet reflected in the Mod's budget accounting.

## Possible Future Features

- **Automatic imports for scarce inputs:** no stable general-purpose target interface has been found for this Mod, so this is not implemented.
- **Production-method switching:** EU5 already provides global vanilla automation and per-building locks, so this Mod does not duplicate normal switching.
- **Automatic town rights:** technically possible, but not implemented in this release. Selection rules, eligibility, and cost policy need further research first.

## Acknowledgements and Inspiration

Some of this mod's design ideas were inspired by the following mods. Many thanks to their authors and maintainers:

- [Community Mod Framework - 1.3 Pavia](https://steamcommunity.com/sharedfiles/filedetails/?id=3692202776)
- [\[1.3 & 1.2\] 建筑管理器 / Construction Manager](https://steamcommunity.com/sharedfiles/filedetails/?id=3736668860)

## Contributing and Support

Pull requests are welcome. If you would like to improve the code, balance, localization, documentation, or user interface, feel free to open a pull request.

If you encounter a bug, have a question, or want to suggest a feature, please open a GitHub Issue and include any relevant reproduction steps, screenshots, save information, or game logs.

## License

This project is licensed under the [MIT License](LICENSE).


<!-- Written by tools/refs.py --write. Do not edit by hand. -->
# What is in `reference/` right now

Versions live here rather than in prose, so refreshing a mod needs no
edit anywhere else. Re-run after any refresh:

```
python3 tools/refresh.py
```

| Folder | Mod id | Version | Game |
| --- | --- | --- | --- |
| `3601047146_glorp_ui` | `glorp.ui` | 10.08.26 | 1.3.* |
| `3668193813_trin_national_destinies` | `trin.national_destinies` | 1.3.8 | 1.*.* |
| `3692202776_community_mod_framework` | `community_mod_framework` | 2.4.1 | 1.3.* |
| `3736668860_construction_manager` | `romaimperator.construction_manager` | 2.2.12 | 1.3.* |
| `3781437488_Auto build by Lincoln Guang` | `eu5ab_regional_development` | 0.9.3-beta | 1.3.* |

`reference/game/` holds 2384 files of EU5 itself — `in_game/gui/`, the parts
of `in_game/common/` the mods here reason about, and the game's own
localization, which is how `mods/nd_ru/tools/term.py` answers what the game
calls a concept.

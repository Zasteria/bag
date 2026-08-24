# Advanced Auto Build — Russian

Russian localization for **EU5 Advanced Auto Build** (`eu5ab_*`, 0.9.1 Beta), the
automated-construction mod by Lincoln Guang. That mod ships English and
Simplified Chinese and nothing else, so a game running in Russian shows the raw
key for every one of its 1201 strings — window titles, its Mod Menu tab, every
setting and every tooltip.

This mod adds the missing `l_russian` file and nothing else. No script, no
interface, no change to how the base mod behaves.

## Installing

Copy this folder into
`Documents/Paradox Interactive/Europa Universalis V/mod/` and enable it in the
playset alongside Advanced Auto Build and the Community Mod Framework. Order
does not matter for the translation itself; see *One key that is not ours*
below for the single exception.

## How it is built

`translations/ru.yml` is the hand written half — one entry per string, in the
base mod's own key order. `main_menu/localization/russian/eu5ab_ru_generated_l_russian.yml`
is written from it by the tool and **must not be edited by hand**:

```
python3 mods/auto_build_ru/tools/generate_ru.py
```

The base mod is found in `reference/` by itself, through `tools/refs.py`, so the
folder it was uploaded under does not matter. A path argument still overrides it.
Point it at a newer copy of the base mod after it updates: the tool fails, and
names the keys, when the base mod has added, removed or renamed any.

The tool refuses to write a file that would be wrong on screen:

- every key the base mod defines is translated, and no key it does not define
  is invented;
- the markup inside a value — `[data functions]`, `$key$` references,
  `@texticons!`, `#format` codes, `\n` — comes through unchanged, because the
  engine reads those rather than displaying them;
- no value carries a double quote, which would truncate the line, or a bare
  square bracket, which renders as `ERROR:`.

Keys that differ only by a number are written once with `{N}` — the twenty
template slots, the step buttons, the reserve presets — and expanded over
exactly the numbers the base mod uses.

## What is deliberately left in English

- **`eu5ab_action_bar_color: "gold"`.** It names a CMF palette entry, not a
  word on screen; translating it makes the action bar button invisible.
- **`eu5ab_action_bar_icon: "@production_panel!"`**, a texticon.
- **"Community Mod Framework"**, the framework's own name, which the base mod
  spells out in several tooltips.
- **The 316 `eu5ab_building_*` keys**, which are `$vanilla_key$` references.
  They already render in the game's own Russian building names, so they are
  copied through untouched rather than translated.

## One key that is not ours

The base mod redefines two of the framework's own keys,
`CMM_NUMERIC_INCREASE_MAX` and `CMM_NUMERIC_DECREASE_MIN`, so that the shift
hint on *its* sliders reads "Increase by 10" instead of "Set to Maximum". Those
keys are shared by every mod's numeric settings, so this translation keeps the
same structure and falls back to CMF's own Russian wording — "Установить на
максимум" and "Установить на минимум" — for every other mod's settings.

Whichever of this mod and CMF loads later wins that key. Both readings are
correct Russian; only the eu5ab-specific hint is lost if CMF wins.

## Terminology

Matches the Russian already used in this repository's own mods: локация,
провинция, область, регион, здание, сырьё. Two choices worth confirming in
game, because vanilla's Russian localization is not in `reference/`:

- **RGO → «добыча сырья»** (and «сырьевая локация» where the base mod means the
  place rather than the activity).
- **Template slot → «слот шаблона»**.

## State

**Never run in game.** The file is generated, complete and internally checked,
but only the player can load it. What to look at first:

1. The Mod Menu entry: **Продвинутое автостроительство** rather than
   `eu5ab_regional_development_name`.
2. Its four tabs, and the group headers inside them.
3. The action bar button — if it is missing from the bottom bars, `_color` is
   the reason, and this mod overriding it in Russian is the thing to suspect.
4. Any key still showing raw, which means the base mod defines it somewhere
   this file does not cover.

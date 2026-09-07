# Where the seven mods stand

One line each, and a link to the brief. **Read the brief for the mod the task is
about and no others** — `mods/<mod>/CLAUDE.md` is 300–800 tokens and holds the
state, the commands, and what fails silently in that mod.

| mod | state | never been in game |
| --- | --- | --- |
| [`glorpui_hints`](../mods/glorpui_hints/CLAUDE.md) | confirmed in game; ready to publish once `mods.bat` can install it | the religious-aspect gate |
| [`ru_loc_fix`](../mods/ru_loc_fix/CLAUDE.md) | working; repairs the base game's own Russian markup, 207 keys | rounds two and three |
| [`auto_build_ru`](../mods/auto_build_ru/CLAUDE.md) | done and confirmed; 1269 keys | the 0.9.3 work, 28 keys |
| [`nd_ru`](../mods/nd_ru/CLAUDE.md) | in progress; 4 174 keys, 10.2% | everything except Westphalia and the override itself |
| [`rgo_bonus_filter`](../mods/rgo_bonus_filter/CLAUDE.md) | working, in use, nothing outstanding | the location-panel chip |
| [`goods_target`](../mods/goods_target/CLAUDE.md) | paused, half working, four faults known | anything on the monthly pulse |
| [`where_to_produce`](../mods/where_to_produce/CLAUDE.md) | **Шаги 0–6 закрыты и видены в игре**; раздача уровнями, сводка по товарам и режим специализации приняты двумя прогонами на северной Германии (416 локаций, 1380 зданий на 1380 мест). **Полосы выгоды больше не решают «сколько»** — `iron` с лучшей выгодой ноль взял 39 мест из 43 — и план ровен настолько, насколько земля позволяет: только городские товары **15…17**, умеющие в село **50…65** считая РГО | **Дальше три работы, порядок его: 1 — резервация по стеснённости, 2 — перетасовка внутри провинции, 3 — шаги 7 и 8 (Glorp UI и Construction Manager).** Проект первой написан целиком и выводить его заново не надо: [`plan_reservation.md`](investigations/plan_reservation.md) — правило, три места в коде, предсказание в числах и признак, по которому её снимать. **Локация держит по одной деревне каждого из четырёх видов**, две одинаковых — нет. **Windows have their own checklist**, [`pitfalls/windows.md`](pitfalls/windows.md); остальные правила — [`archive/wtp_brief_rules.md`](archive/wtp_brief_rules.md) |

`where_to_produce` is the second attempt at a question the first one failed at
without ever being tested. Why the first was removed, and the lesson that shaped
this one, is [`archive/where_to_produce.md`](archive/where_to_produce.md).

## Two things being hunted that are not any mod's fault

- **[The widget leak](investigations/widget_leak.md)** — the game accumulates
  GUI widgets and never releases them. Measured across five runs, established as
  the base game's, and the open question is whether a mod or a setting is a
  lever. A run is prepared and the owner has agreed to it.
- **[The panel hitch](investigations/panel_hitch.md)** — panels open slower with
  the playset from the first minute. A different thing, and it must not be filed
  with the leak. The next step is a bisect the owner can do in five minutes.

## The tooling around all of it

Finished and not to be rebuilt: `mods.bat` → `tools/mods.ps1`, the menu that
does his whole mod loop, and `tools/workshop.py`, which answers whether a
refresh is owed without needing the game, an account or the files.
[`CONVENTIONS.md`](CONVENTIONS.md) is how it fits together.

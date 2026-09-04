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
| [`where_to_produce`](../mods/where_to_produce/CLAUDE.md) | **the plan works and he has seen it** — 192 buildings in 192 rooms, charters 5–6 each, goods 3–6 each. **The editor is a window of its own**: three slots, a cell per good with its building count and «−1»/«+1», a changes list in a second window. Its window opens and its presses arrive — five silent faults cost that, and all five are written down ([`pitfalls/interface.md`](pitfalls/interface.md)); two are checkers | **«+1»/«−1» confirmed working, 2026-09-04** — and the round trip is not an undo: the plan drifts by one building of two other goods (`TESTLOG.md`). **Step 1 of eight is done and confirmed in game 2026-09-05** — the press line names the good, the location and what moved, and the windows fit their content. **Step 2's share and lock are confirmed by numbers 2026-09-05** — `quota=3 free=19 pool_rooms=66`, and a fill won on shortfall with gain 0. **Its «не нужен» flag was rebuilt after that run and is unrun**: the game has no checkmark glyph anywhere, so it is the game's own checkbox now, and the plan reads the flag at last. Order and what to ask for: [`investigations/wtp_practice_plan.md`](investigations/wtp_practice_plan.md); the rules they implement are [`wtp_editor_design.md`](investigations/wtp_editor_design.md) |

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

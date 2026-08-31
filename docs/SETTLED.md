# Settled — do not measure any of this again

**This is the one document worth reading in full, and it is short.** Every row
cost the owner an evening. Asking for any of it a second time spends the one
resource this repository cannot generate for itself: only the player can run the
game.


| question | answer | where |
| --- | --- | --- |
| Whose fault are the localization errors? | The base game's Russian files. 88% of 39 289 lines. | TESTLOG 2026-08-24 |
| Did the filter fix work? | Yes. Zero `CUSTOM_SEARCH_FILTER` lines in an hour; the error rate fell about twentyfold a minute. | TESTLOG 2026-08-24 evening |
| Are the 17 `Failed parsing localized text` in `gui.log` real? | No. They are stamped sixteen seconds before the mod's localization is merged — the frontend reading vanilla on the way past. | TESTLOG 2026-08-24 evening |
| Is the slowdown memory running out? | No. The working set peaks and then falls; what grows without limit is the widget count. | TESTLOG 2026-08-24 evening |
| Do map icons / units / game time cause the widget growth? | No. It scales with neither game days nor unit count. | [investigations/widget_leak.md](investigations/widget_leak.md) |
| Does idling cost anything? | No — exactly +0, twice, across 10 800 frames each. | TESTLOG 2026-08-25 |
| Is it one bad window? | No. Diplomacy +1.86/frame, map modes +1.49, locations +0.29; none zero. | TESTLOG 2026-08-25 |
| Is it the mod set? | No. Vanilla leaks +1.99/frame against the playset's +1.86. | TESTLOG 2026-08-25 vanilla |
| Is it anything in this repository? | No. `rgo_bonus_filter` lives in the lightest panel of the three. | same |
| Does the merged `glorpui_hints` load and work? | Yes. Both blocks render, in Russian, on the same save. | TESTLOG 2026-08-25 |
| Can a mod free widgets? | No. `dump_data_types` has no `Destroy`/`Clear`/`Free`/`Collect`/`Prune` on any GUI type. | research/engine.md |
| Is there a widget limit or pool size to raise? | No. `NGUI` in `00_defines.txt` is twenty lines of name lengths, queue sizes and alert thresholds. Nothing about pools, caches or arenas. | research/engine.md |
| What does `where_to_produce`'s buildable tick filter on? | The location, not the owner. `can_build_building` is asked in the location's scope and answers about its rank, terrain and the building's requirements; a province with no town drops out, a province across a border does not. | TESTLOG 2026-08-31, seventeenth load |
| Why does `where_to_produce`'s map picker close after each pick? | The generic action's own lifecycle, not a fault. It is the only map-click channel a mod has, and clicking the map with a window open is impossible. | research/interface.md |
| Does the age filter work? | Yes. Methods and buildings change to the better ones as ages pass and the ranking follows. Seventeen loads to get it reported. | TESTLOG 2026-08-31 |
| Why keep `nd_ru` when `nation_destinies_rus` translates 93% of the mod? | **Because that one is Google's machine translation and behind on versions.** The owner loads `nd_ru` *after* it on purpose: where ours has a key, his good translation wins; everywhere else the machine one fills in. This was decided before this repository existed, and has now been asked twice. | [archive](archive/nd_ru_and_the_machine_translation.md) |


## Decisions that are closed

**And one thing the owner has already rejected as an answer:** "report it to
Paradox". They know it is a base-game defect and know other players have it. The
job is to find something that helps from the mod side, or to establish with
evidence that nothing can.

**Why `nd_ru` exists next to a 93% machine translation.** `nation_destinies_rus`
is Google's, and it lags the base mod's versions. The owner loads `nd_ru`
*after* it on purpose: where ours has a key, the human translation wins;
everywhere else the machine one fills in rather than English. This was decided
before this repository existed and **has now been asked twice**. Do not propose
dropping `nd_ru`, and do not propose reaching 93%. The measurement behind it is
in [`archive/nd_ru_and_the_machine_translation.md`](archive/nd_ru_and_the_machine_translation.md).

**`glorpui_hints` ships Russian and hands the other ten languages back.**
Settled 2026-08-30, the owner's call: he prefers this mod's Russian to Glorp
UI's copy of it and does not mind about the rest. `SHIP_GLORP_HINTS` is
`["russian"]`. Also his call: the two «показать всё» switches stay independent.

**The reference tree is there to be used.** Reading, grepping, quoting and
copying out of `reference/` into a mod is settled — see
[`../reference/README.md`](../reference/README.md). Do not stop mid-task to ask
about it, and do not report a mod arriving at a newer version as a problem: that
is the normal state of the tree.

**Nothing about updating the owner's mods may require a session of ours.** He
asked for that in those words. `mods.bat` is the menu; do not build a step only
a session can perform, and do not tell him to run the pieces by hand when the
menu covers it.

## What has never been run

Kept as one list in [`TESTLOG.md`](TESTLOG.md#never-run) rather than scattered
through prose. Check it before calling anything confirmed.

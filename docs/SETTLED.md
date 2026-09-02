# Settled — do not measure any of this again

**This is the one document worth reading in full, and it is short.** Every row
cost the owner an evening. Asking for any of it a second time spends the one
resource this repository cannot generate for itself: only the player can run the
game.


| question | answer | where |
| --- | --- | --- |
| What is settled about the widget leak? | **Eight rows of it, in the file that owns them** since this one outgrew its budget. The short of it: it is the base game's, and no mod can free a widget or raise a pool. | [investigations/widget_leak.md](investigations/widget_leak.md) |
| What was settled about the localization errors? | Three rows, closed in August and moved out when this file outgrew its budget. | [archive](archive/settled_localization.md) |
| What else is closed and out of this file? | Five rows: `glorpui_hints` loading, buildings upgrading in place, the two market-balance answers, and the age filter. | [archive](archive/settled_closed.md) |
| What does `can_build_building` answer, and where? | **Two different questions in two scopes.** In a *location's*, the rank, terrain and `location_potential` — never an advance, which is why the buildable tick filters on the location and not the owner. In a *country's*, the advance. | TESTLOG 2026-08-31, 17th |
| Do the town/village ticks reset themselves? | **No, measured.** The ones he cleared read 0 through a window close and a map change; the fourteen that «came back» are other locations, ticked earlier and outside the ground on screen, which widening it brought in. **A tick is a location variable and outlives a save** — hence «Сбросить пометки», all five continents at once. | TESTLOG 2026-09-02 |
| Why did the plan put glass in villages and never in a town? | **Because most of those «towns» were villages ticked into towns, and a guild is `town = yes`.** `rural_glassmaker` is `rural_settlement = yes, town = no`; both carry the *identical* sand-in-market condition and it passes. Measured on twenty goods at once: sixteen with no market condition at all were stopped in the same 3-of-17. **And the tick is the rank, for the whole calculation** — «расчёт должен симулировать ранги… и не важно что там стоит на самом деле», so a ticked location is scored, granted rights and built on as what it was ticked into. `bag_wtp_stands_<building>` takes the rank from the tick, the potential still from the game. | TESTLOG 2026-09-02 |
| Why does `where_to_produce`'s map picker close after each pick? | The generic action's own lifecycle, not a fault. It is the only map-click channel a mod has, and clicking the map with a window open is impossible. | research/interface.md |
| Does a building with two production slots earn one RGO bonus or two? | **Two, one per method, each over its own output.** The build panel's tooltip is headed with the *method's* name and lists the province's raw material under it, so a pair is one method of the summed output at the output-weighted blend of the two bonuses. | TESTLOG 2026-08-31, twenty-first load |
| Is a market a map region the target picker can outline and click? | **Yes**, like an area. But only markets named in `interaction_source_list` are clickable — the picker will not enumerate them itself. | TESTLOG 2026-08-31, twenty-seventh load |
| Should the owner's flag stay under an expanded `where_to_produce` row? | Yes — a row is the whole province and its locations can belong to two or three countries, which is the split the ranking deliberately ignores. | TESTLOG 2026-08-30, seventh load |


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

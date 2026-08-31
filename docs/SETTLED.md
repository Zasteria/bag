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
| What is settled about the widget leak? | **Eight rows of it, moved to the file that owns them** when this one outgrew its budget: it is not memory, not the map, not idling, not one window, not the playset and not anything here — and no mod can free a widget or raise a pool. | [investigations/widget_leak.md](investigations/widget_leak.md) |
| Does the merged `glorpui_hints` load and work? | Yes. Both blocks render, in Russian, on the same save. | TESTLOG 2026-08-25 |
| What does `where_to_produce`'s buildable tick filter on? | The location, not the owner. `can_build_building` is asked in the location's scope and answers about its rank, terrain and the building's requirements; a province with no town drops out, a province across a border does not. | TESTLOG 2026-08-31, seventeenth load |
| Why does `where_to_produce`'s map picker close after each pick? | The generic action's own lifecycle, not a fault. It is the only map-click channel a mod has, and clicking the map with a window open is impossible. | research/interface.md |
| Does a building with two production slots earn one RGO bonus or two? | **Two, one per method, each over its own output.** The build panel's tooltip is headed with the *method's* name and lists the province's raw material under it, so a pair is one method of the summed output at the output-weighted blend of the two bonuses. | TESTLOG 2026-08-31, twenty-first load |
| Does a building have to be demolished to get its better version? | **No — an obsolete building is upgraded in place, by a button on the building itself.** The owner said so on 2026-08-31. So the ladder `where_to_produce` reads off `obsolete` is an upgrade path, and «В конце» names where a province ends up, not a second thing to build. | owner, 2026-08-31 |
| Does the game already show a market's balance without trade? | **Yes.** `Market.GetBalanceWithoutTrades(goods)` is production minus local demand, trades excluded, and vanilla's market panel prints it as a sortable «Local balance» column. Halves: `GetProducedLabel`, `GetDemandLabelNoTrades`; the trade halves are `GetSupplyImportOnly` and `GetDemandExportOnly`. | `panels/market/market_goods.gui:93` |
| Can a mod get that balance for one country's share of a market? | **No, not as a number.** Every per-country breakdown returns `CString`, a formatted tooltip, and script's `goods_supply_in_market` is a comparison rather than a value. A country-only figure would have to be built from buildings and pops. | `data_types_uncategorized.txt` |
| Should the owner's flag stay under an expanded `where_to_produce` row? | Yes — a row is the whole province and its locations can belong to two or three countries, which is the split the ranking deliberately ignores. | TESTLOG 2026-08-30, seventh load |
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

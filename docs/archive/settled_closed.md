# Settled: five rows closed and moved out

Out of [`SETTLED.md`](../SETTLED.md) when it outgrew its budget again. Every one
of them is answered, shipped and no longer shapes a decision — the two market
rows are the summary of
[`../investigations/market_truth.md`](../investigations/market_truth.md), and the
upgrade-in-place row is why `where_to_produce` never asks about demolition.
`tools/kb.py` searches this file like any other.

| question | answer | where |
| --- | --- | --- |
| Does the merged `glorpui_hints` load and work? | Yes. Both blocks render, in Russian, on the same save. | TESTLOG 2026-08-25 |
| Does a building have to be demolished to get its better version? | **No — it is upgraded in place, by a button on the building itself.** So the ladder read off `obsolete` is an upgrade path: «В конце» names where a province ends up, not a second thing to build. | owner, 2026-08-31 |
| Does the game already show a market's balance without trade? | **Yes.** `Market.GetBalanceWithoutTrades(goods)` is production minus local demand, trades excluded — vanilla's market panel prints it as a sortable «Local balance» column, and the four halves are readable too. | `panels/market/market_goods.gui:93` |
| Can a mod get that balance for one country's share of a market? | **No, not as a number.** Every per-country breakdown returns `CString`, a formatted tooltip, and script's `goods_supply_in_market` is a comparison rather than a value. A country-only figure would have to be built from buildings and pops. | `data_types_uncategorized.txt` |
| Does the age filter work? | Yes. Methods and buildings change to the better ones as ages pass and the ranking follows. Seventeen loads to get it reported. | TESTLOG 2026-08-31 |

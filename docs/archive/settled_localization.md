# Settled: the localization errors, closed August 2026

Three rows out of [`SETTLED.md`](../SETTLED.md) when it outgrew its budget. They
are closed and nothing turns on them any more — `ru_loc_fix` shipped and the
error rate was measured before and after. `tools/kb.py` still searches this file.

| question | answer | where |
| --- | --- | --- |
| Whose fault are the localization errors? | The base game's Russian files. 88% of 39 289 lines. | TESTLOG 2026-08-24 |
| Did the filter fix work? | Yes. Zero `CUSTOM_SEARCH_FILTER` lines in an hour; the error rate fell about twentyfold a minute. | TESTLOG 2026-08-24 evening |
| Are the 17 `Failed parsing localized text` in `gui.log` real? | No. They are stamped sixteen seconds before the mod's localization is merged — the frontend reading vanilla on the way past. | TESTLOG 2026-08-24 evening |

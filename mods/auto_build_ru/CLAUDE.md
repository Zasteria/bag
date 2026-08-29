# `auto_build_ru` — brief

Russian for **Advanced Auto Build** (`eu5ab_regional_development`), which ships
English and Chinese only and so renders as raw keys in a Russian game. Do not
write its version down; `python3 tools/refs.py` prints it.

**State: done and confirmed in game** — the owner reports the Mod Menu tab
reading correctly. **1269 keys.** The 0.9.3 work — a second ranking strategy, 28
keys — **has not been in game.**

**Built by** `python3 mods/auto_build_ru/tools/generate_ru.py`, in `tools/refresh.py`.
It refuses to write when the base mod's English has moved, naming the keys, and
that is the whole point of it: an update to the base mod is a translation job,
not a silent gap.

**Two mechanisms worth knowing, both bought the hard way:**

- **A key can go stale without disappearing.** The throughput warning's
  `action_name` and `action_desc` were rewritten by the base mod — they used to
  be about presets, they are now about the Planning Candidates limit — under a
  Russian translation that stayed put and went on reporting itself complete. The
  generator takes a fingerprint of every translated key's English value in
  `english_generated_fingerprints.txt` and names the ones that moved. Fix the
  translation, then `generate_ru.py --accept`.
- **The base mod's folder name is not fixed.** Its id is
  `eu5ab_regional_development` and the folder carries a workshop number now.
  Both are resolved by `tools/refs.py`; neither is written down anywhere.

The dependency line declares only CMF, left over from when the base mod arrived
without its `.metadata/`. It carries one now, so that could be tightened.

Depth: [`README.md`](README.md).

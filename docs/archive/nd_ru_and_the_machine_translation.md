# `nd_ru` against the machine translation, measured

Why this repository keeps a 10% human translation next to somebody's 93%
machine one. **The decision is closed** — it is in
[`../SETTLED.md`](../SETTLED.md) and has been asked twice. The numbers are here
so the arrangement is legible, not so it can be reopened.

`nation_destinies_rus` is in his playset — a **full** Russian translation of the
mod `nd_ru` translates. Measured against the base mod's English, on the same day:

| | keys | markup faults | left in English |
| --- | --- | --- | --- |
| the base mod (English) | 40 795 | — | — |
| `mods/nd_ru` | 4 174 (10%) | 0 | 53 |
| `nation_destinies_rus` | 37 949 (93%) | 33 | 120 |

**3 787 of our 4 174 keys are keys it also translates**, and 32 of its 33 markup
faults are inside that overlap — so on those keys ours is the sound one, and
whichever of the two mounts *later* wins them.

**The decision was made long ago and is not open.** That mod is machine
translation — Google's — and it lags the base mod's versions; the owner runs it
*under* `nd_ru` deliberately, so that a key we have translated properly shows
our text and everything else falls back to the machine one rather than to
English. `nd_ru` is therefore not competing with it and does not need to reach
93% to be worth having: every key it covers is a key upgraded from machine to
human, and the 32 broken-markup keys in the overlap are repaired by the same
mechanism.

**Do not ask him about this again, and do not propose dropping `nd_ru`.** It
has come up twice; the numbers above exist to make the arrangement legible, not
to reopen it. What matters practically: **`nd_ru` must mount after
`nation_destinies_rus`** — if a load order ever puts it first, our translation
becomes invisible and the symptom is machine-Russian on keys we know we
translated.

Our 53 English leftovers are deliberate and correct: they are `_CATEGORY` keys
pointing at vanilla category names and proper nouns that stay as they are
(`Erbverbrüderung`, `Studia Generalia`).

# `goods_target` — brief

An addon to **Construction Manager**: tick the goods you want cheap and it
builds their producers, subsidising them, until construction of everything else
is as cheap as you asked.

**State: paused, half working, four faults known. Nothing builds and nothing is
subsidised.**

On screen and right: registration, both goods lists (74 rows, every good in the
game), the ticks, and the price readings, which matched the game's own
construction tooltip.

Wrong, and **none of it logs anything**:

1. **Nothing runs on the monthly pulse** — the counter stays at zero. This is
   the one that matters; the rest are cosmetic beside it.
2. **The readings never change**, and the game loses ticks while the menu is
   open. Both are the same cause: 74 row labels each evaluate a live script
   value every frame.
3. **The Target column printed a key** — missing format keys. Diagnosed, fixed,
   unverified.

**The cheapest next step, and it costs no run of ours.** Construction Manager
runs on the same monthly pulse. Whether *its* automation still works in the same
save says whose fault fault 1 is — the mod's or the pulse's — and the owner can
answer it while doing something else.

**Built by** `python3 mods/goods_target/tools/generate.py`, in `tools/refresh.py`.
It writes the goods lists, the script values and both localizations, and checks
that every key CMM derives is defined and the languages are in step.

Depth, with what is proven about each fault: [`README.md`](README.md).

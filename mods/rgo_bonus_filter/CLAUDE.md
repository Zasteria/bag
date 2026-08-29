# `rgo_bonus_filter` — brief

Two filter chips, one per building list, leaving only buildings that gain
production efficiency from a raw material the province actually has.

**State: working, in use, nothing outstanding.** The location-panel chip is the
one thing never confirmed on screen; the province one is.

**Built by** `python3 mods/rgo_bonus_filter/tools/generate_rgo_filter.py`, run from
`tools/refresh.py` with everything else. It writes the scripted triggers from
the game's own `building_types` and `goods` — 293 (good, building) pairs — so a
patch that adds a building is picked up by a rebuild and nothing is listed by
hand.

**The one thing to know before touching it.** A `building_type` filter receives
`root` and nothing else — not `scope:target`, whatever vanilla's comment says.
Reading `scope:target` logs an error every pass.

**And the one open cost.** Four of the fifteen chips mods add to the `building`
tag are this mod's, and they are not cheap: `bag_rgo_has_local_bonus` walks
`any_location_in_province` and evaluates a 40-branch `OR` per location, per
building type. On a five-location province with a hundred types that is
thousands of trigger evaluations per open of the build panel. It is a named
suspect in [`../../docs/investigations/panel_hitch.md`](../../docs/investigations/panel_hitch.md);
if the bisect lands here, the fix is to make those chips cost a variable lookup
instead of a province walk.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

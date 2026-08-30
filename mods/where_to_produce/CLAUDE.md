# `where_to_produce` — brief

Name a good and the ground; the mod finds each location the best production
method for that good and ranks the locations by what that method would earn from
the raw materials the province supplies.

**State: three loads behind us. The data half is proved; the interface has been
rebuilt twice on what the loads found.** The result table read back location
names and numbers out of global variables on screen — "Бельцы — 9.25% (2/2)" —
and the map mode paints. `docs/TESTLOG.md` has the rest.

**The mod no longer asks which method to use.** It did for one round, and that
was the design error: knowing which recipe suits which ground *is* the question,
so asking it back made the player do the work first. Every method for the chosen
good is now scored per location and the best wins; the row names the building
that won it.

## Two CMM caps, neither written near the call that cares

- **A list is good to 50 rows.** `cmm_register_settings_list` initialises items
  through an unrolled chain ending at 50, and handles a row click through
  `CMM_MarkListPosition_*`, unrolled to the same 50.
- **A dropdown is clickable only to its twentieth option.** An option click runs
  `CMM_MarkDropdownSelection_<index>` and CMF defines twenty. A 218-option
  dropdown renders and scrolls all of them and silently refuses the 21st onwards.
  That is why every picker here is a list.

## What the next run has to answer

1. **The two goods lists**, and one tick moving across both.
2. **The map picker.** Three buttons hand the game one of this mod's generic
   actions and it answers with its own target panel. Confirmed working; confirmed
   to close after each pick, which is the action lifecycle and not fixable from
   script — `fire_generic_action` executes with a supplied target rather than
   reopening the panel.
3. **The window's list** now holds the provinces something is picked in, which is
   what makes it a trimming tool and what keeps it bounded.
4. **The ranking with no method chosen** — one script value per method, one
   effect per good keeping the best.

## What is settled and should not be re-litigated

- **The window's cost is its datamodel.** 104 widgets per province row, and a
  scripted widget never comes down, so `bag_wtp_browse` holds only the picked
  provinces and is emptied when the window closes.
- **The selection is recorded twice** — a variable on the location for the map
  and the interface, a global list for the ranking — and only `bag_wtp_pick` /
  `bag_wtp_drop` may write it.
- **There is no marked zone.** A location's continent is one plain trigger
  (`continent = continent:europe`, which vanilla uses seventy times), so nothing
  is written onto a continent's locations in advance.
- **The bonus is province-level.** Every location of one province scores the
  same; what separates them is building slots, which this version does not model.

**Built by** `python3 mods/where_to_produce/tools/generate.py`, run from
`tools/refresh.py`.

Depth: [`README.md`](README.md). Anything else: `python3 tools/kb.py <words>`.

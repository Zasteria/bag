# Test log

What has actually been in the game, and what it showed.

Only the player can run EU5, so a run is the scarcest thing this repository
consumes. Everything else here — the reference tree, the generators, the
checkers — exists to spend fewer of them. This file is where a run's result
stops being a remark in a chat and becomes something a later session can rely
on.

**A session writes the entry, not the player.** The player says what happened,
in as few words as they like; the session turns it into a row and commits it. If
a run is not written down, `STATUS.md` will keep calling something "untested"
long after it was tested, which is the same cost as not having run it.

## How to fill this in

One entry per run. What matters is the last two columns: what was expected, and
what actually appeared.

- **Date and mod** — and the base mod's version if the run was about a
  translation, from `python3 tools/refs.py`.
- **What was loaded** — the playset order matters for a localization mod, since
  the mod loaded later wins the key.
- **Expected / observed** — the whole point. "Nothing happened" is a result and
  belongs here.
- **`error.log`** — quote the line if there was one. It names the file and the
  line for GUI failures and script errors. An effect that never runs logs
  nothing at all, so "log clean" is itself worth recording: it says the failure
  is the silent kind and the next step is a `cmf_log`, not another guess.

## Runs

The four most recent. Everything before 2026-08-27 is in
[`archive/testlog_2026-08.md`](archive/testlog_2026-08.md) — same entries,
moved rather than trimmed. Search both with `python3 tools/kb.py`.

### 2026-08-27 — a logs drop, and the error nobody would have seen

**Not a designed run.** The player was asked to look at the eleven-language
rebuild, said it "looks the same as before", and sent the whole `logs/` folder
instead. It answered three things anyway, one of them a real bug.

**What was loaded.** The 2026-08-25 build of `glorpui_hints`, out of
`Documents/.../mod/glorpui_hints` — **not** the 2026-08-27 rebuild, which had
not been installed. So "looks the same as before" is not evidence about the
rewrite, and the axis he was looking at (*Миролюбие*) could not have shown a
difference in any case: its extra block is two conditional lines,
«В мирное время» and «Крепостей меньше половины лимита», and those words are
identical in both builds. The catalogue lines are the ones that changed.

Also loaded: `3784988919` (`Glorp UI small fix`), the rival addon, alongside
ours. The screenshot shows **our** phrasing — «Даровать привилегию Религиозные
дипломаты», «Принять реформу правления Дипломатические традиции» — where his
says «Предоставить …» and «Добавить … ([government_reform|e])». So on this
playset ours wins the shared keys. Worth knowing and worth not relying on: the
mount lines interleave the two across several passes and the order is not
obviously ours to control.

| | |
| --- | --- |
| **`Missing loc key 'GLORP_UI_SVH_*'`** | **0.** Was 725 per load before this mod existed. The translation half does its whole job. |
| **`ru_loc_fix` round two** | **confirmed.** All six keys it was to repair — `RGO_BUILD_GOODS_PRICE_IMPACT_ON_COST`, `FILTER_BY_GOODS`, `MARKET_SURPLYS_INFO`, `ALERT_HAS_UNMARRIED_CHILDREN`, `THIRD_DESTROY_BUILDING_EFFECT`, `DESTROY_BUILDING_EFFECT` — appear **0 times** in `error.log`. Round one was already confirmed; round two now is. |
| **`glorpui_hints` gates** | **one broken gate, found only because the logs came.** |

**The bug.** One line, once, in `error.log`:

```
[jomini_trigger.cpp:803]: is_core_of: Inconsistent trigger scopes (country vs.
location) at common/customizable_localization/svx_extra_hint_loc.txt:3073
```

`svx_n_sinicized_004` is the Confucian Academy, and its gate is that building's
own `allow` block copied verbatim. **A building's `allow` is evaluated on the
location being built in**, not on the country — `is_core_of = owner`,
`owner = { ... }`, `region`, `market`, `has_building`, `dominant_culture` — and
all 179 of them were being pasted into a `type = country` customizable
localization. `is_core_of` is simply the one strict enough to say so.

On screen this shows as nothing at all: the gate does not answer, so the hint
either never appears or always does, and no player would ever connect the two.

**The repair is the exact question rather than a workaround.** Every building
push here is a `capital_country_modifier` — the building has to be *in the
capital* — so the block belongs in the capital's scope:
`exists = capital capital = { ... }`. `capital` is a country → location event
target (`python3 tools/api.py capital`) and the game writes `exists = capital`
in front of it 76 times in its own `common/`.

**And the rule went into the checker.** `check_gate_scopes` in
`mods/glorpui_hints/tools/generate.py` reads **Supported Scopes** out of the
engine's own trigger dump (`reference/game/docs/triggers.log`) and reports
any trigger called in country scope
that the engine does not allow there. It follows only the outer scope — a nested
`capital = { ... }` is a different scope and is left alone, which is precisely
what the repair is. Checked both ways: it catches the old line and passes the
new one.

**Still unrun, and unchanged by this:** everything the 2026-08-27 rebuild added.
The cheapest single check is now known — turn the mod menu switch
«Показывать всё без фильтра» on and hover **Децентрализация**: the subject type
lines should read «**Тип ленника** …» where the old build said «Тип вассала».

### 2026-08-27 — the concept tokens render, and in two languages

**The change with the widest blast radius is confirmed.** Screenshots of the
*Decentralization* tooltip with the mod menu switch «Показывать всё без фильтра»
on, in Russian and then in English — the player switches language from the
console on the fly, which turns out to make testing the other ten languages
almost free.

| expected | observed |
| --- | --- |
| the catalogue lines open with the game's own word for the category, from `[religious_aspect\|e]` and friends | **yes.** «**Религиозная особенность** Двенадцать представителей», «**Тип ленника** Феод / Пронии / Удж-бей / Вассал» — where the 2026-08-25 build said «Аспект веры» and «Тип вассала» |
| the concept renders as an encyclopedia link, not plain text | **yes** — the category word is coloured and hoverable, the object name beside it is not |
| English exists at all | **yes.** "Religious Aspect The Twelve Emissaries", "Subject Type Fiefdom". The old build shipped no English `SVX_*` keys, so this block would have been raw keys |
| the English openers are Glorp UI's own | **yes** — "Enact the Traditional Distribution Policy" |
| the unfiltered block replaces the two filtered ones | **yes**, and the block titles translate: «Влияет на смещение (без фильтра)» / "Pushes towards this (unfiltered)" |

So `catalog` in `languages.py` stays a concept token, and the seven Russian
terms it corrected are the game's own words on screen. **That was the one change
that could have gone badly, and it did not.**

**One thing the hot language switch does not do:** the vanilla block title
«Дальше продвинуться в сторону децентрализации:» stayed Russian in the English
screenshot while everything this mod owns switched. Not our key and not our bug
— but it means a language switched from the console is not a clean test of
*vanilla* strings, only of ours. A real check of another language wants a
restart.

**Still unconfirmed:** the five advance-gated privileges, the building `allow`
repair from earlier today, and nine of the eleven languages.

### 2026-08-27 — the upload button exists, and it is hidden

Two screenshots, an hour apart, and the second corrected the first.

**First read, wrong:** the launcher's «Модификации и дополнения» shows playsets,
order and checkboxes and nothing about publishing, so EU5 was written up as
having no first-party upload.

**It has one.** The player found it: the same screen, the row **«Выбранные
модификации: N/M»**, a small **sandbox icon** in that row next to the gear. It
opens **Mod Tools**, with tabs *Create mod* and *Uploaded mods*, the whole of
`metadata.json` as a form — Name, ID, Path, Version, Supported game version,
Description, and the tag list as checkboxes — and a button reading **Upload New
Mod**.

It is documented, in one sentence, in the middle of a dev diary about writing
events and situations:
[Tinto Talks 85, Modding](https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-85-22nd-of-october-modding.1864004/)
— *"navigate into the Mods & DLCs Menu in the top right corner and then open the
Mod Tools view by clicking on the sandbox icon next to Selected Mods"*. That
diary is otherwise entirely about authoring; publishing is that clause and the
button in a screenshot. The wiki does not mention it at all, which is why it
documents the third-party uploader instead — and why an hour went on finding a
button that was on screen the whole time.

**So the route is the game's own**, and the tag checkboxes in that form are the
authoritative tag vocabulary — the same one four mods here were outside of.
[PDX Workshop Manager](https://github.com/kaiser-chris/pdx-workshop-manager)
stays as the fallback; `mods.bat → 5 → «к»` still writes its config.

Also confirmed from the same screenshot: the load order the player actually
runs puts `Glorp UI` at 3 and `Glorp UI - Societal Value Hints` at 4, directly
after it, which is what the declared dependency is for.

### 2026-08-29 — `mods.bat`, an update run on the owner's own machine

Not a game run — the mod menu, on the box that has Steam, reported by the owner
in full. It is here because only he can run it and because two of the three
things it found were invisible from a session.

**Loaded:** `mods.bat → 2 → 3` (reference and playset both), against a Steam
workshop folder that had Advanced Auto Build's 2026-08-28 build and Glorp UI's
2026-08-28 build in it.
**Expected:** the copies in `reference/` replaced, the generators rebuilt, and a
report of what moved.
**Observed:** the copies were replaced; **two generators failed and stopped the
run**, and the run then ended by telling him the two mods it had just copied in
were still behind.

- `auto_build_ru` — `28 key(s) the base mod does not define`. The new Advanced
  Auto Build deleted 28 keys, the ranking-mode block among them, and no key was
  added or renamed. A deletion, and it stopped everything.
- `glorpui_hints` — `Glorp UI writes a hint this mod cannot translate:
  GLORP_UI_SVH_CENTRALIZATION_PV_PETTY_BUREAUCRACY: @hint! Grant
  [ShowEstatePrivilegeName('petty_bureaucracy')]`. Glorp UI moved its hint
  references to the engine's own data function.
- `svx_unlock_gate.txt` changed in the same run, which is the quiet half: the
  advance gates are found by a second regex that only knew the old shape, so it
  matched nothing and wrote the file empty. Nothing errored.
- `workshop.py record` then stamped both freshly copied mods `behind`, because
  it dates a copy by `git log` and the copy was not committed yet.

**Verdict:** all four are fixed and the exact run was replayed against files
rewritten into the new shapes — refresh comes out green, with one note naming
the nine dropped keys. Still his to confirm: that the real 2026-08-28 files
behave the way the rewritten ones did, which is one `mods.bat → 2` away.

**He also said the tool never actually updated a mod in Steam for him** — he
still had to unsubscribe and resubscribe. It compared install dates, and Steam
stamps a mod updated when it *notices* the update rather than when it downloads
it. It compares build ids now (`manifest` against `hcontent_file`), and will
re-fetch a mod on demand whatever the check says. Untested against a real
`appworkshop_3450310.acf`; see [`STATUS.md`](STATUS.md).

### 2026-08-30 — `glorpui_hints` against Glorp UI's 2026-08-28 build, in game

**Loaded:** the owner's playset, Glorp UI 2026-08-28 with `glorpui_hints` after it.
**Observed, reported by the owner:** with Glorp UI's new «показать недоступные»
switch **on**, the two mods conflict and something on Glorp UI's side breaks;
with it **off**, everything is fine. He also reports their version of the
feature has gaps and does not show everything worth using, and that with their
filter off it is «совсем плохо».

**Cause, found in the files and not guessed:** their update added one
`TooltipScrolledStringPairList` per side that prints vanilla's own C++ hint blob
(`[SocietalValue.GetLeftHint(Player.Self)]`) when the country variable
`showUnavailableSocietalValueSuggestions` is set, and added
`NOT = { has_variable = showUnavailableSocietalValueSuggestions }` to every one
of their `glorpui_svh_visible_*` script values. So their switch is an either/or:
their filtered lists off, vanilla's blob on. This mod replaces that whole
`blockoverride`, and rebuilt their half from the entries its regex recognised —
which the blob entry is not. Switch on: their lists gone (their own script
values say so), their blob gone (this mod dropped it). Half the tooltip empty,
nothing in `error.log`. «Совсем плохо» is vanilla's raw blob, which is what
their switch shows.

**Fixed:** their block is now spliced in byte for byte and the check compares
text rather than parsed entries. Replaying the old behaviour against the new
files reproduces the fault and the check now names it.

**Verdict:** unrun. The fix has never been in game — the next load with their
switch **on** is the test, and what should appear is vanilla's blob plus this
mod's own lists, with Glorp UI's per-axis lists hidden by their own design.


## Waiting on a run

The next session should start here rather than designing anything new. All of
these are prepared, all are cheap, and the owner has agreed to the hover one.

**The panel-open bisect — five minutes, no log to read.** Reported 2026-08-25:
any tab opens instantly in vanilla and with a hitch, sometimes a freeze, under
the playset — *on a save loaded a minute ago*, so it is not the widget leak.
Counted from the files already; the candidates and the numbers are in
[`investigations/panel_hitch.md`](investigations/panel_hitch.md).
The playset is 22 workshop mods, 17 of them touching `in_game`
(`python3 tools/playset.py <logs>` reads it out of `debug.log`), so this is a
bisect: same save, same three panels (country, diplomacy, a location's build
panel), halving the `in_game` mods until the hitch is cornered — four or five
loads of a minute each. Worth trying **Construction Manager** and
`rgo_bonus_filter` first, in case they save the bisect. No log, no timing — the
owner's own sense of the hitch is the measurement, because the difference he
describes is one anybody can feel.

Advanced Auto Build was the first version's headline and it was wrong: the owner
does not run it. Its `3781437488` is mounted in the 2026-08-24 log, so if it
turns out to be enabled and merely unused, that still costs — a scripted widget
is instantiated whether it is opened or not.

**The hover test, and the tooltip settings with it.** One session, one save,
paused throughout. Two minutes sweeping the mouse over the map and top bar with
**no clicks**; then Settings → Tooltip Settings with `Map Tooltips` set to
Disabled and both delays at maximum; then the same two minutes again. Send
`performance_degradation.log`. What each outcome means is in
[`investigations/widget_leak.md`](investigations/widget_leak.md) — read it
before asking for anything else, because the losing branch has its own next test
already written and it is not this one repeated.

~~**`ru_loc_fix` round two — eleven keys and four expansions, never in game.**~~
**Confirmed 2026-08-27** from the logs drop above: none of the six keys appears
in `error.log` any more.

**And one thing only eyes can check.** Whether the repaired Russian *reads*
correctly. The log says those keys no longer fail; it does not say the sentences
are right. Quickest look: a religion tooltip (harmony, purity, honor), the goods
filter chips in a location's buildings panel, and the price line in the build
panel.

## Never run

Kept here so it is one list rather than scattered through prose:

- whether anything in `goods_target` runs on a monthly pulse. Its lists,
  readings and ticks are confirmed on screen; nothing periodic is.
- `rgo_bonus_filter`'s build-panel chip.
- Everything `nd_ru` has translated apart from Westphalia — 3 600 keys that have
  never been on screen.

# Handoff

Where the three mods stand, and what a fresh session needs to carry on. Read this
first, then [`RESEARCH.md`](RESEARCH.md) for how EU5 modding actually works —
most of that was learnt the hard way and will save a repeat.

## Settled — do not measure any of this again

Five runs of the game went into the answers below, most of them an evening's work
for the owner. The numbers are in [`TESTLOG.md`](TESTLOG.md). Asking for any of
this a second time spends the one resource this repository cannot generate for
itself, so read the table before designing a test.

| question | answer | where |
| --- | --- | --- |
| Whose fault are the localization errors? | The base game's Russian files. 88% of 39 289 lines. | TESTLOG 2026-08-24 |
| Did the filter fix work? | Yes. Zero `CUSTOM_SEARCH_FILTER` lines in an hour; the error rate fell about twentyfold a minute. | TESTLOG 2026-08-24 evening |
| Are the 17 `Failed parsing localized text` in `gui.log` real? | No. They are stamped sixteen seconds before the mod's localization is merged — the frontend reading vanilla on the way past. | TESTLOG 2026-08-24 evening |
| Is the slowdown memory running out? | No. The working set peaks and then falls; what grows without limit is the widget count. | TESTLOG 2026-08-24 evening |
| Do map icons / units / game time cause the widget growth? | No. It scales with neither game days nor unit count. | [the slowdown](#the-slowdown--it-is-the-base-game-and-the-hunt-is-for-a-lever) |
| Does idling cost anything? | No — exactly +0, twice, across 10 800 frames each. | TESTLOG 2026-08-25 |
| Is it one bad window? | No. Diplomacy +1.86/frame, map modes +1.49, locations +0.29; none zero. | TESTLOG 2026-08-25 |
| Is it the mod set? | No. Vanilla leaks +1.99/frame against the playset's +1.86. | TESTLOG 2026-08-25 vanilla |
| Is it anything in this repository? | No. `rgo_bonus_filter` lives in the lightest panel of the three. | same |
| Can a mod free widgets? | No. `dump_data_types` has no `Destroy`/`Clear`/`Free`/`Collect`/`Prune` on any GUI type. | research/engine.md |
| Is there a widget limit or pool size to raise? | No. `NGUI` in `00_defines.txt` is twenty lines of name lengths, queue sizes and alert thresholds. Nothing about pools, caches or arenas. | research/engine.md |

**And one thing the owner has already rejected as an answer:** "report it to
Paradox". They know it is a base-game defect and know other players have it. The
job is to find something that helps from the mod side, or to establish with
evidence that nothing can.

## State

**The reference tree moved, and nothing broke.** Construction Manager 2.2.12 and
Community Mod Framework 2.4.1 came in, the second a real reorganisation of the
CMM list code. `tools/refresh.py` rebuilds everything from them and reports
clean: no generated file changed, and `tools/check_cmm.py` — the check that every
CMM macro is called with arguments CMF declares — still passes. What 2.4.1 added
is in [`research/cmf.md`](research/cmf.md#what-cmf-241-added).

**`ru_loc_fix/` — working, round one confirmed in game, round two unrun.**
Repairs the markup in the game's own Russian localization. It came out of the
player's question about why their `error.log` is full: the answer is that 88% of
it was the base game's Russian files, not any mod. **162 keys** now, in six
shapes — unclosed brackets, accessors `dump_data_types` does not have, `Custom()`
applied to a string, roots that are nothing, keys reaching a Russian case through
a helper reference, and wrong scopes the game named in its own log. Nothing is
retranslated; only the markup changes.

The mod is generated. `mods/ru_loc_fix/tools/locscan.py` is the rule set, split
into hard rules (cannot fire on a healthy key) and advisory ones (compare against
English, need a person). `generate.py` refuses to write a key that no longer
exists, a key that is no longer broken, or a repair that still trips a rule; 140
of the 162 are search-and-replace against whatever the game ships that day, so a
patch that rewrites the sentence keeps the repair. It runs from
`tools/refresh.py` with everything else.

**Confirmed in game, 2026-08-24.** An hour of play with the mod loaded: not one
`CUSTOM_SEARCH_FILTER` line in the log, and the burst that used to rotate
`error.log` five times inside one second is gone. The rate fell from 39 289
errors in three minutes to 35 455 in an hour — about twenty times fewer per
minute — and the log is legible for the first time.

What that legibility bought was round two. The same fault turned out not to be
confined to filter strings: `RGO_BUILD_GOODS_PRICE_IMPACT_ON_COST` (13 950
lines), `FILTER_BY_GOODS` (3 866) and `MARKET_SURPLYS_INFO` (1 650) took their
place, each reaching a Russian case through `$GOODS_..._RU_*$`. Eleven more keys
are fixed for the next run; the mod is at 162.

**Round two keeps the grammar.** The first fix replaced declined forms with
nominatives. This one does not have to: the same strings hold the promote both
ways — `RGO_BUILD` has `[GOODS.GetDefaultMarketPrice]` inline, which works, next
to `$GOODS_GetName_RU_GEN_lower$`, which does not — so the scope is present and
it is the *reference* that loses it. `fixes/expand.txt` writes the helper out
inside the key, seventy five `AddTextIf` tests and all.

**What still errors, and what each would need.** After round two lands, roughly
12 000 lines an hour should remain, and almost none of it is localization:

| | lines/hour | what it would take |
| --- | --- | --- |
| `ForeignCountryView` evaluated with no view context | 5 118 | vanilla's own `foreign_country_lateralview.gui`, which Glorp UI copies verbatim — the bug is Paradox's, and fixing it means carrying a copy of a large `.gui` |
| `ActionGroup.GetActions` at `gui/shared/cards.gui:2363` | 2 476 | the same: a vanilla `.gui` |
| `longname_ru_GEN` finding no entry for a country, in `game.log` | 4 108 | **nothing.** The file is in the tree now and the fault is not in it: `country_ru_flavor` ends in a `fallback = yes` entry and every one of its 218 suffixed keys exists, so the object being passed is an invalid country and that is the caller's doing |
| character nicknames: `Select_CString(Character.IsFemale, …)` given a `Container` | ~1 300 | unknown. The same 180 keys work everywhere else, so it is one caller and nothing in the log says which |
| `Custom()` handed a location where it wants a country, in `debug.log` | ~390 | unattributed. New in the second run, but the shape (`predlog_vvo`, `CL_tt`, `CL_tt`, `CL_PREP` in that order, 98 times over) matches no key this mod touches |
| other mods' scripts, `D008_pronoia`, an audio arena, an input stack | ~50 | their authors', not ours |

The `location_rank` errors of the first run — 484 lines — did not recur. If they
come back: `LR_GEN` and its four siblings in
`in_game/common/customizable_localization/ru_EU5_custom_loc.txt` test
`location_rank = location_rank:x` with no fallback, so a location that has no
rank at all falls through. That file is 49 653 lines and overriding it wholesale
to add one fallback is not worth it.

**`goods_target/` — paused, half working, four faults known.** An addon to
Construction Manager: build the producers of goods you tick until they are as
cheap as you asked, subsidising them on the way.

On screen and right: registration, both goods lists (74 rows, every good in the
game), the ticks, and the price readings, which matched the game's own
construction tooltip.

Not right, and none of it logs anything: **nothing runs on the monthly pulse**
(the counter stays at zero), the readings never change and the game loses ticks
while the menu is open (both because 74 row labels each evaluate a live script
value every frame), and the Target column printed a key (missing format keys —
diagnosed, fixed, unverified).

The mod's README has each fault, what is proven about it, and the cheapest next
step for the one that matters: Construction Manager runs on the same pulse, so
whether *its* automation still works in the same save says whose fault it is,
and costs nothing to check.

Still nothing builds and nothing is subsidised.

**`rgo_bonus_filter/` — working, in use.** Two filter chips, one per building
list. Nothing outstanding.

**`auto_build_ru/` — done, confirmed working in game.** Russian for Advanced Auto
Build, which ships English and Chinese only and so rendered as raw keys in a
Russian game. The player reports the Mod Menu tab reading correctly.

The base mod updated to 0.9.2 Beta mid-session and the generator refused to
write, naming 40 keys it had never seen — the template buttons, the priority
step tooltips, a whole R.G.O. diagnostics panel and a throughput warning. That
is what it is for. All 40 are translated now, 1241 keys in total, and the
generator is clean again. Note the base mod's id is `eu5ab_regional_development`
and its folder now carries a workshop number; both are resolved by
`tools/refs.py` and neither is written down anywhere.

**`nd_ru/` — в работе, играбелен за Вестфалию и Швабию.** Русский для National
Destinies. Базовый мод везёт одиннадцать языков, и файлы всех одиннадцати
побайтово равны английским, так что в русской игре он читается по-английски.
Объём — 40 790 ключей, **690 376 слов** прозы, 220 файлов. Версию не записывать:
её печатает `python3 tools/refs.py`.

**Перекрытие проверено в игре и работает.** Отдельный мод, загруженный после
базового, переопределяет уже определённые тем ключи. Это был главный риск, и он
снят. В лаунчере `nd_ru` должен стоять **после** National Destinies.

**Совместим с машинным переводом из мастерской.** Имена наших файлов
(`*_ru_generated_l_russian.yml`) не совпадают с именами того мода (как у
базового), значит подмены файла целиком не будет. Ставить: машинный ниже, наш
выше — получится наш текст там, где он есть, машинный везде остальном.
Английского от нас не добавится: генератор не пишет непереведённые ключи.

Сделано — **4 174 ключа** (10,2% ключей, 6,4% слов):

- все 5 правил игры;
- названия и описания 45 образуемых стран, какие мод называет сам; остальные 93
  из его 125 формируемых стран берут имя из игры и русскими были всегда, так что
  **названия стран закрыты полностью**;
- три большие системы целиком: Дунайская монархия (`nd_dnm`, 685 ключей),
  Дунайский вопрос (`nd_danube`, 443), Австрия (`nd_hab`, 150);
- **три страны целиком**: Вестфалия (`nd_wes`, 208 ключей с учётом лежащих в
  общих файлах), Швабия (`nd_swa`, 192) и объединённая Европа (`nd_eur`, 275);
- названия Ломбардии;
- общие файлы `nd_event_guards` (144) и `nd_bureaucracy_impact_modifier_types`
  (1770 из трёх шаблонов) — чинят свои строки сразу у всех стран.

Ничего из этого, кроме Вестфалии и перекрытия, в игре не проверялось.

**Обновление базового мода до 1.3.7 разобрано.** Оно тронуло ровно ту часть,
что уже была переведена: 67 новых ключей в `nd_dnm` (целая система «Вопрос о
Рейхе» — остаться в Империи или порвать с ней, утверждение Санкции рейхстагом,
два новых дипломатических действия) и два переписанных значения, `DNM_f_desc`
и `nd_dnm.21.a_tt`. Всё это переведено, `nd_dnm` снова закрыт целиком. Ещё
четыре новых ключа в `nd_event_entries` — чистые `$...$`-ссылки на заголовки
событий, переводить их не нужно.

**Устаревание перевода теперь ловится само.** Из этого обновления генератор
поймал только `nd_dnm.21.a_tt`, и только потому, что там изменилась разметка;
переписанный `DNM_f_desc` нашёлся руками, через `git diff` по `reference/`.
Поэтому `generate_ru.py` снимает отпечаток английского значения каждого
переведённого ключа в `english_generated_fingerprints.txt` и на следующем
запуске называет те, где английский сдвинулся. Поправить перевод, затем
`generate_ru.py --accept`. До этого запуск возвращает ошибку, то есть хук
начала сессии покажет `FAIL nd_ru` — ровно тогда, когда это нужно.

**Как продолжать — в [`../mods/nd_ru/README.md`](../mods/nd_ru/README.md).** Там
три команды, которыми ведётся работа, что именно проверяет генератор и порядок
работы над страной. Термины — в
[`../mods/nd_ru/GLOSSARY.md`](../mods/nd_ru/GLOSSARY.md), сверяться с ним
обязательно: расхождение в терминах на двухстах файлах читается как небрежность.
Порядок стран — в `mods/nd_ru/priority.txt`, остаток — `mods/nd_ru/tools/scope.py --plan`.

**Сколько это стоит.** Одна сессия ровной работы сдвинула около 25 000 слов
вместе с оснасткой и ошибками. Отсюда: остаток рабочего набора по Европе —
5 832 ключа, 25 тыс. слов, примерно одна такая сессия. Полная проза той же
Европы — ещё 6 693 ключа и 214 тыс. слов сверх того. Весь мод целиком —
34 618 ключей, 646 тыс. слов, около двадцати шести сессий.
На подписке Pro весь мод не окупается; объём режется по приоритету. Самый
выгодный приём — искать файлы, где одна формулировка повторяется сотнями ключей,
и переводить их шаблоном: так 1 914 ключей обошлись в два десятка строк.

**Про модель.** Смена модели не сокращает число токенов — английский всё равно
читается, русский пишется. Экономит только цена токена и понижение усилий
рассуждения: перевод не рассуждательная задача, и `high` на нём почти не
окупается. Сам перевод абзаца модель послабее сделает сопоставимо; хуже она
сделает другое — удержание единого термина на двухстах файлах и поиск дыр вроде
ключей страны в чужом файле. Отсюда разумное деление: названия — модели подешевле
и с меньшими усилиями, длинная проза и структурные разборы — сильной.

**`where_to_produce/` — removed, August 2026.** A Mod Menu tab that ranked what
was worth building in a province you picked. It never worked in game and the
owner stopped wanting it; the reason it did not work was never established,
because it was never tested. What it is worth knowing about it is in
[Why it failed](#why-where_to_produce-failed), below.

## The slowdown — it is the base game, and the hunt is for a lever

Measured across five runs. The measurement is finished; what is open is whether a
mod or a setting can do anything about it. Numbers and method in
[`TESTLOG.md`](TESTLOG.md); this is the state of it.

**What it is.** The game accumulates GUI widgets and never releases them while a
session is running. 364 at the main menu, ~37 000 once a game is loaded, 294 013
after an hour of ordinary play. Frame time follows: 14 ms early, 21 ms after an
hour.

**How big that is.** Every `.gui` file the game ships declares, in total, about
**27 800 widgets** — the whole interface, every window, counted statically
(`in_game/gui/`, widget declarations, minus properties that share the shape). So
after an hour the process is holding **more than ten copies of the entire
interface**. This is not a heavy panel; it is instances piling up.

**What causes it.** Interface interaction, and nothing else:

| | widgets per frame |
| --- | --- |
| paused, hands off | **0.00** — exactly zero, across 10 800 frames, twice |
| clicking countries, opening diplomacy | +1.86 |
| cycling map modes | +1.49 |
| clicking locations, opening the build panel | +0.29 |

**What it is not.** Ruled out, each with data rather than argument:

- *map markers, unit icons, the passage of time* — growth does not scale with
  game days (103 days added 138 widgets, 125 days added 10 936) and does not
  scale with the unit count, which swings 276 to 708 with no relation to it;
- *one bad window* — every kind of interaction leaks, at different rates and none
  of them zero;
- *the mod set* — with every mod off the same activity leaks **+1.99** widgets a
  frame against **+1.86** with the full playset. Vanilla is marginally worse;
- *anything in this repository* — `rgo_bonus_filter` adds to the location panel,
  the lightest of the three by a factor of six.

### The lead worth following

**Growth decays inside a block of unchanging activity.** Four blocks, four times
the same shape:

```
diplomacy, full playset   +24814   +8809  +11150    +140
locations, full playset    +3783   +1338   +1504    +336
map modes, full playset   +17532   +5191   +3278   +5123   +1130   +0
diplomacy, no mods        +14560   +3487   +3425    -418    +258
```

He was doing the same thing throughout each row, so a per-*action* leak would be
flat. A decaying one says the cost is per *distinct thing looked at*: the first
pass over a set of countries or map modes is expensive and the second is nearly
free. Over an hour of real play you keep meeting new things, which is why it
never plateaus.

**The engine offers nothing to release them.** `dump_data_types` has no widget
`Destroy`, `Clear`, `Free`, `Collect` or `Prune` — the only such names belong to
buildings, editors and variable systems. `PdxGuiWidget` can be hidden, found,
counted and animated, and that is all. So there is no mod-side call that undoes
this; a fix has to be something that stops the widgets being made.

### The candidate, and the lever that goes with it

Hover. It fits everything: idle costs nothing because an unmoving mouse shows no
tooltips; clicking through diplomacy sweeps the pointer over dozens of new flags,
names and numbers; map modes sweep it over a new legend each time; and the decay
within a block is what a per-subject tooltip cache would look like.

**And the defines say tooltips are built with no delay at all.**
`game/loading_screen/common/defines/jomini/00_tooltips.txt`, in full:

```
NTooltip = {
    OPEN_DELAYED_TIME = 0.0f;
    CLOSE_TIME = 0.2f;
    TENDENCY_BUFFER = 15;
    MIDDLE_MOUSE_LOCK_TIME = 0.25;
    MOUSE_MOVE_DISTANCE_TO_UPDATE_TOOLTIP_POSITION = 10.0f;
    MOUSE_MOVE_DURATION_TO_UPDATE_TOOLTIP_POSITION = 0.2;
}
```

Zero delay means every brush of the cursor over anything builds a tooltip
immediately. Sweeping across the map builds them by the dozen a second.

That file's own first line is `# This file overrides
cw/jomini/modules/tooltip_manager/data/common/defines/jomini/00_tooltips.txt`, so
overriding a defines file is the ordinary mechanism and **a mod can do the same
thing**. If hover is the source, a one-file mod setting `OPEN_DELAYED_TIME` to
something like `0.35f` cuts the creation rate by whatever fraction of hovers are
incidental — which is most of them.

Better still, the game's own **Settings → Tooltip Settings → Show Delay** almost
certainly drives the same value. So the setting tests the mod before the mod is
written.

### The run that decides it

One session, one save, paused throughout:

1. **A** — move the mouse over the map and the top bar for two minutes, sweeping
   across countries and buttons, **without a single click**.
2. Settings → Tooltip Settings: `Show Delay` to **maximum**, `Map Tooltips` to
   **Disabled**, `Map tooltips delay` to **maximum**.
3. **B** — exactly the same two minutes of sweeping.

Then `performance_degradation.log`.

- **A leaks and B does not** → the mechanism is tooltips. Write the defines mod,
  and then look at what else can be trimmed from the heaviest tooltip files
  (`shared/location_tooltips.gui` 438 widgets, `shared/combat_tooltips.gui` 428,
  `cooltip.gui` 627).
- **A leaks and B leaks the same** → the delay is not the knob, but hover still
  is. Then the tooltip `.gui` files are the place to look.
- **A does not leak at all** → hover is out entirely and the leak needs clicks.
  The next test is then the same panel opened thirty times against thirty
  different panels opened once, which separates a per-open leak (a mod can make
  panels cheaper) from a per-object cache (only Paradox can).

### The other route, if the run does not settle it

`debug_mode` in the console opens a toolbox. The buttons, as of 1.3.11:

```
TOOLBOX     Language  Environment  Map menu  Inspect  Explorer  Unit Viewer  Errors
2D Tools    UI Editor  Animator  UI Bounds  UI Library  Workbench  Reload GFX
3D Editors  E. Designer  Animation Edit  Particle Edit
```

There is **no Tweaker**, so the runtime-variable idea is out. But `UI Editor` is
the live widget tree, and that is the direct way to name what accumulates: play
until the count is high, open it, and see which container holds a quarter of a
million children. `UI Bounds` draws widget outlines and would show a stack of
invisible ones. `Inspect` reports whatever is under the cursor.

**The mitigation that is already established.** Leaving to the main menu releases
all of it — widgets back to the 364 the process starts with, memory back to what
it was before any game was loaded. So **main menu, then load the save** is worth
exactly as much as restarting the game and costs a fraction of the time.

## The second slowdown — panels open slower with mods, from the first minute

Reported 2026-08-25: *"открыть любую вкладку в ваниле происходит мгновенно, а вот
с модами с микрозадержкой или даже фризом даже при только-только запущенном
сохранении."* This is **not** the widget leak and must not be filed with it. The
leak grows over hours and reloading clears it; this is present on a save loaded a
minute ago, so it is a fixed per-frame or per-open cost that the playset adds.

**First, the size of what can be said.** The owner runs **22 workshop mods**, and
`reference/` holds five of them. `tools/playset.py` reads the mount table out of
his own `debug.log` — the engine writes one line per mod folder it mounts, in
load order — and reports that **17 of the 22 mount `in_game`**, which is the only
mount that can add a widget, a filter chip or a scripted widget to the running
game. Of those 17, at most 14 have never been looked at. So the census below is
honest about a quarter of the surface and silent about the rest; do not write
"the playset does X" on the strength of it.

**And the owner does not run Advanced Auto Build**, which the first version of
this section led with. His `debug.log` of 2026-08-24 does mount workshop id
`3781437488` — that is Auto Build, `in_game` and `main_menu` both — so either it
was turned off since, or it is enabled and unused, which costs the same because
a scripted widget is instantiated whether the player opens it or not. Its numbers
are kept below because they are the clearest example of the pattern, not because
they explain his hitch.

`tools/guicost.py` counts the rest from the files:

```
                          files  widgets GetScriptedGui   live  loops
vanilla                     387    58354              9      0      0
cmf                          44     7486             70     12      0
construction_manager         20     4545            344      3      0
glorp_ui                     49    13782             67      1      0
national_destinies            3      251              0      0      0
auto_build                    7    14125           4719      7     19
mods/rgo_bonus_filter         2      207              4      0      0
```

**The number that does not belong.** `GetScriptedGui('x')` in a `.gui` file
runs a script trigger from the interface — the expensive kind of expression,
because it enters the script engine. Vanilla uses it **nine times** in 387 files.
Advanced Auto Build uses it **4 719 times** in seven, 2 166× vanilla's density
per widget; Construction Manager **344 times**, 491×. With Auto Build out of the
playset, **Construction Manager is the heaviest thing anybody here has looked
at** — and thirteen mods nobody has looked at are still in the room.

**And all seven of Auto Build's windows are in `scripted_widgets/`,** so the
engine instantiates them at load and never takes them down: **14 125 widgets
live for the whole session** whether or not the player opens the mod. Vanilla's
entire interface, statically, is about 27 800. CMF's twelve always-live windows
come to 104 widgets and Construction Manager's three to 96 — those are probes,
which is what a scripted widget is for. This is a different order of thing.

**`eu5ab_engine_queue_window` is a background worker.** It is deliberately kept
"visible" (`visible = "[EqualTo_CFixedPoint('(CFixedPoint)0', '(CFixedPoint)0')]"`
— always true) and parked at `position = { -10000 1 }` so it keeps ticking
offscreen. Inside are **eight phases**, each a self-restarting animation state at
**0.15 s**, each walking a `datamodel` of the player's candidate locations × their
candidate building types and running per pair:

```
GetBuildOrExpandBuildingCost           GetBuildingTypeIncomeToOwnerInLocation
GetBuildingTypeProfitInLocation        CanBuildOrExpandBuilding
```

Each phase's gate is itself a `GetScriptedGui(...).IsShown(...)` evaluated every
frame. That is a plausible cause of a hitch on any panel open, for the ordinary
reason: the frame budget is already spent before the panel asks for anything.

**Static widget counts understate a `datamodel` window, and Construction
Manager is the case in point.** `cm_hidden_window` declares twenty-three widgets
— and binds `datamodel = "[GetGlobalList('cm_building_types_to_process')]"`, so
what actually lives is that subtree **once per building type**, and the game has
465 of them. Nested inside each row are two more datamodels, over the type's
construction demand entries and over its production methods. The file's own
comments say what it is for: *"Always-present hidden window that classifies every
building type once per lobby"*, kept alive with
`visible = "[EqualTo_CFixedPoint('(CFixedPoint)0', '(CFixedPoint)0')]"` — always
true — at `position = { -10000 1 }`, and *"Keeps descendant visibility gates
re-evaluating each frame."* That is a few thousand live widgets whose `visible`
expressions (`BuildingType.HasConstructionGoodsDemand`, `BuildingType.IsProducing`,
`ProductionMethod.IsProducing`) are re-asked every frame, by design.

`cm_construct_queue_window` is the same shape with sixteen datamodels over
locations × building types, and it too is always live.

None of this is a bug: it is how CM gets at engine bindings that read only in
GUI. It is simply not free, and it is paid whether or not a panel is open.
`python3 tools/guicost.py --drivers` names the list every always-live window
iterates, because the multiplier is the number that matters and no static count
can know it.

**Filter chips are the second cost, and this repository is in it.** Every chip
whose `tag` matches a list is a trigger run once per item, every time the list
draws. `python3 tools/guicost.py --filters`:

| tag | vanilla | mods add |
| --- | --- | --- |
| building | 36 | +15 (+42%) |
| town_rights | 21 | +7 (+33%) |
| raw_goods | 15 | +4 (+27%) |
| ruler | 27 | +5 (+19%) |
| province | 8 | +1 (+12%) |

Four of the fifteen added to `building` are ours. They are not cheap ones:
`bag_rgo_has_local_bonus` walks `any_location_in_province` and evaluates a
40-branch `OR` per location, per building type in the list. On a five-location
province with a hundred buildable types that is thousands of trigger evaluations
per open of the build panel.

**Two hypotheses already dead, so nobody re-checks them:**

- *Glorp draws heavier panels.* No. On the sixteen vanilla files it replaces,
  Glorp's versions hold **3 850 widgets against vanilla's 4 956** — 0.78×. It
  adds 33 files of its own (2 399 widgets) but replaces nothing with something
  bigger.
- *A mod's Russian localization is throwing parse errors on open.* No. The hard
  rules of `mods/ru_loc_fix/tools/locscan.py` run over every mod's Russian files
  find **zero** faults: CMF 94 keys, Construction Manager 451, Glorp 139,
  National Destinies 40 719, Auto Build 1 241, and our own five mods. The broken
  markup is the base game's alone.

**The test.** Seventeen mods can be halved in four or five loads, and each load
is a minute. The same save and the same three panels every time — the country
panel, diplomacy, and a location's build panel — because the owner's own sense
of the hitch is a good enough measurement for a difference he describes as
obvious:

1. Everything on. Confirm the hitch is there.
2. Half the `in_game` mods off. Instant or not?
3. Keep halving whichever half still hitches.

Two named suspects are worth trying first, in case they save the bisect
entirely: **Construction Manager**, for the reasons above, and our own
`rgo_bonus_filter`. If it is CM, the choice is the owner's — the mod or the
responsiveness; nothing here can make another author's hidden window cheaper. If
it is ours it is fixable: those four chips can be made to cost a variable lookup
instead of a province walk.

If the bisect lands on a mod nobody has looked at, copy its folder from
`steamapps/workshop/content/3450310/<id>/` into `reference/mods/` and run
`guicost.py` again — that is what the id list from `playset.py` is for. If it
lands on nothing in particular, the cost is spread and the next instrument is
`ScriptProfilerEntry`, which the engine dumps expose with
`GetAverageTimeExclusive`, `GetCallCount` and `GetFileAndLine`.

## Where to check things

Everything a session needs is in `reference/` — the game's `gui` and the parts
of `common` that matter, plus Community Mod Framework, Construction Manager,
Glorp UI and the two mods being translated. Grep it rather than asking for
uploads, and run `python3 tools/refs.py` rather than believing a version written
in prose.

The one thing that still has to come from the player is `logs/` after a test
run, because only they can run the game. After any refresh of `reference/`:

```
python3 tools/refresh.py
```

Advanced Auto Build arrived in `reference/` without its `.metadata/`, so its mod
id and version are not in the tree — it is the one mod `refs.py` has to find by
folder name. `auto_build_ru` therefore declares only CMF as a dependency; if the
base mod's id is wanted there, that file has to come from the player's mod
folder.


## Hard-won facts that are easy to lose

- The RGO bonus formula, verified to the digit against three tooltips, is in
  [`research/engine.md`](research/engine.md#the-formula-behind-the-number) and in code in
  `tools/eu5data.py`. Every input counts in the divisor, produced goods included.
- A `building_type` filter receives `root` and nothing else — not `scope:target`,
  whatever vanilla's comment says. Reading it logs an error every pass.
- A CMF action bar element is drawn from localization: `_icon` takes a texticon
  like `@good!`, and `_color` must name one of CMF's palette entries or the
  button is invisible in the bottom bars.
- Square brackets in a localization value are data function syntax, so a plain
  `[debug]` in a label renders as `ERROR:`. The same syntax is what lets a row
  label read a global variable back.
- A CMM macro called with an argument name CMF does not declare fails silently
  and takes the rest of its effect with it. One `step` instead of `step_value`
  cost a full round. `python3 tools/check_cmm.py mods/<mod>/in_game/common`
  checks a whole mod for it.

## Why `where_to_produce` failed

It was removed in August 2026, unfinished, at the owner's word: "нерабочая
помойка, я ей не пользуюсь". Written down because the next attempt at the same
question should not repeat the shape of it.

**What it was.** A tab in CMF's Mod Menu. Four CMM list settings — region, area,
province, then the answer — where picking a row in one filled the next, and the
last ranked every building by what that province's raw materials were worth to
its best production method, in percent and in volume.

**What was verified, and what was not.** The data layer was checked against the
game and was right: the bonus formula matches three tooltips to the digit, and
an earlier build of the same data answered the *opposite* question ("for this
good, which province") correctly on screen — `Рудные горы / Оружейные заводы /
1.88% / 4.075` read true. Then the front end was rebuilt around province-first
picking, and **that rebuild was never run in game even once**. Nothing about the
new front is known to be broken; nothing about it is known to work either.

**Why the cause was never found.** The failure mode this repository hits most:
an effect that never runs logs nothing at all. Six things were suspect at once —
`region = { }` and `area = { }` as scope blocks, comparing `region =
global_var:x`, reading a variable map inside a script value, re-registering a
list at a new height, `GetRegion` / `GetArea` on a global variable, and whether
`can_build_building` was stricter than it looked. Diagnosing that needs one
`cmf_log` per suspect and one game run each, and the mod was not wanted enough
to pay for them.

**The lesson worth carrying.** The mod was built to completion before anything
of it was loaded once. A `cmf_log` on the first picker, run in game, would have
cost one round trip and told us which half of six unknowns was even in play. In
a repository where only the player can run the game, the size of the untested
increment *is* the risk — and the interface half, not the data half, is where
everything here has gone wrong.

**Where its parts went.** The formula and the CMM list mechanics are in
[`RESEARCH.md`](RESEARCH.md); the game-data reader is `tools/eu5data.py`,
untouched and still correct; the CMM macro check is `tools/check_cmm.py`, which
now runs against any mod. The mod itself is in git history — `git log --
mods/where_to_produce` — if a future approach wants to read how something was  <!-- check-docs: ignore -->
done.

**If the question gets picked up again**, two things are known to be possible and
were never done: a button injected into the location panel through
`scripted_widgets`, so the province on screen is the one answered for instead of
walking three pickers; and building straight from a row, since
`construct_building = { building_type owner payer }` in a location scope queues a
real construction and Construction Manager uses exactly that. The open question
there was never the effect — it was *which* location of the province to build in.

One thing the game files in `reference/` still cannot answer: a *method* locked
behind an advance. `ProductionMethod.IsAvailable` exists as a GUI data function,
so the game knows, but there is no script-side counterpart and neither
`building_types/` nor `production_methods/` records the unlock. Answering it
needs `common/advances/` and the technology folder beside it, which are not in
the tree.

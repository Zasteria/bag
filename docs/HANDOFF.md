# Handoff

Where the two mods stand, and what a fresh session needs to carry on. Read this
first, then [`RESEARCH.md`](RESEARCH.md) for how EU5 modding actually works —
most of that was learnt the hard way and will save a repeat.

## State

**`rgo_bonus_filter/` — working, in use.** Two filter chips, one per building
list. Nothing outstanding.

**`auto_build_ru/` — complete, never loaded.** Russian for Advanced Auto Build
(`eu5ab_*` 0.9.1 Beta), which ships English and Chinese only and so renders as
raw keys in a Russian game. All 1201 keys are translated;
`tools/generate_ru.py` writes the game file from `translations/ru.yml` and
checks key coverage and markup parity, so what is left to find out is whether
the game picks the file up at all. See that mod's README for what to look at
first and for the two terminology choices worth confirming on screen.

**`nd_ru/` — в работе, играбелен за Вестфалию.** Русский для National Destinies
(`trin.national_destinies` 1.3.6). Базовый мод везёт одиннадцать языков, и файлы
всех одиннадцати побайтово равны английским, так что в русской игре он читается
по-английски. Объём — 40 719 ключей, **688 617 слов** прозы, 220 файлов.

**Перекрытие проверено в игре и работает.** Отдельный мод, загруженный после
базового, переопределяет уже определённые тем ключи. Это был главный риск, и он
снят. В лаунчере `nd_ru` должен стоять **после** National Destinies.

**Совместим с машинным переводом из мастерской.** Имена наших файлов
(`*_ru_generated_l_russian.yml`) не совпадают с именами того мода (как у
базового), значит подмены файла целиком не будет. Ставить: машинный ниже, наш
выше — получится наш текст там, где он есть, машинный везде остальном.
Английского от нас не добавится: генератор не пишет непереведённые ключи.

Сделано — **3 646 ключей** (9% ключей, 5% слов):

- все 5 правил игры;
- названия и описания 45 образуемых стран, какие мод называет сам; остальные 93
  из его 125 формируемых стран берут имя из игры и русскими были всегда, так что
  **названия стран закрыты полностью**;
- три большие системы целиком: Дунайская монархия (`nd_dnm`, 622 ключа),
  Дунайский вопрос (`nd_danube`, 443), Австрия (`nd_hab`, 150);
- **Вестфалия целиком** (`nd_wes`, 208 ключей с учётом лежащих в общих файлах);
- названия Ломбардии;
- общие файлы `nd_event_guards` (144) и `nd_bureaucracy_impact_modifier_types`
  (1770 из трёх шаблонов) — чинят свои строки сразу у всех стран.

Ничего из этого, кроме Вестфалии и перекрытия, в игре не проверялось.

**Как продолжать — в [`../mods/nd_ru/README.md`](../mods/nd_ru/README.md).** Там
три команды, которыми ведётся работа, что именно проверяет генератор и порядок
работы над страной. Термины — в
[`../mods/nd_ru/GLOSSARY.md`](../mods/nd_ru/GLOSSARY.md), сверяться с ним
обязательно: расхождение в терминах на двухстах файлах читается как небрежность.
Порядок стран — в `mods/nd_ru/priority.txt`, остаток — `tools/scope.py --plan`.

**Сколько это стоит.** Одна сессия ровной работы сдвинула около 25 000 слов
вместе с оснасткой и ошибками. Отсюда: остаток Европы — 6 000 ключей, 26 тыс.
слов, примерно одна такая сессия. Весь мод — 664 тыс. слов, около двадцати семи.
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

**`where_to_produce/` — rewritten around the opposite question; untested.**
Everything up to the last round answered "for this good, which province" and
worked: the lists populated, the volume columns and sort order were right, and
`Рудные горы / Оружейные заводы / 1.88% / 4.075` read exactly true. The player
then said that is not the mod they want. What they want — and what the community
"Province Breakdown" spreadsheet does — is the inverse: **pick a province, see
what is worth building in it.**

So the front was rebuilt: region → area → province pickers, then one ranked list
of buildings. The whole verified data layer survived unchanged — the bonus
formula, the volumes, the availability filter, the list machinery. What went was
the good picker, the recipe list and the province shortlist.

## What the spreadsheet asked for, and what it got

| Spreadsheet column | Here |
| --- | --- |
| Province / Area / Region | the three picker lists, built from land you hold |
| Top Burgher Buildings | the answer with **Show = Town** |
| Top Laborer Buildings | the answer with **Show = Rural** — `pop_type` gives the split |
| Raw Goods | not shown; it is what the percentages are computed from |
| Ideal City Locations | not done. It is a made-up topography score, and picking a location is the same problem the build button would need |

The percentages will read lower than the sheet's: it tops out at 12.5% on
single-input buildings from patch 1.0.6, and 1.3.10 tops out at 10%, verified
against three tooltips.

## Not done, and asked for

- **A button in the location panel** to jump to the province on screen instead of
  walking three pickers. `scripted_widgets` makes it possible; it was left out
  because injecting into a vanilla panel is where the old custom window already
  failed once, and the table wanted to be right first.
- **Building from the row.** `construct_building = { building_type owner payer }`
  in a location scope queues a real construction and Construction Manager uses
  exactly that. The open question is *which* location of the province — the same
  problem the spreadsheet's "Ideal City Locations" column exists to answer.

## Untested, in order of doubt

Nothing of the new front has been in game. In rough order of how likely each is
to be the thing that breaks:

1. **`region = { }` and `area = { }` as scope blocks from an owned location.**
   Both appear in vanilla (`area = { any_ownable_location_in_area = ... }`), and
   `.region` is used dotted, but this is the first thing here to rely on them.
   If the region list comes up empty, that is where to look.
2. **`region = global_var:wtp_sel_region` as a filter on `every_owned_location`.**
   Vanilla only ever compares against a literal `region:x`. If the area list
   ignores which region was picked, this comparison is why.
3. **`can_build_building` and `building_type_is_obsolete` on the country.**
   Both are engine triggers vanilla uses country-side — `country_can_build_in_location`
   splits exactly this way, and Construction Manager leans on both. They are what
   the **Only what I have now** toggle is; if it turns out stricter than it looks
   and empties the answer, that toggle is the thing to turn off and the rest of
   the filtering carries on. That is why it is its own setting rather than folded
   into the availability filter.
4. **Reading a variable map inside a script value** — `wtp_candidate_rank` does
   `"variable_map(wtp_bonus_of|scope:wtp_cand)"`. CMF uses that expression in
   triggers and effects, not in a script value. If every row scores the same, the
   selection sort is reading nothing.
5. **Re-registering a list at a new height.** Clearing `cmm_list_items_<setting>`
   and removing `cmm_list_initialized_<setting>` sends registration back through
   its first-time branch, which is how it is meant to work — but CMF has no
   caller that does this. Four lists now depend on it.
6. **`GetRegion` / `GetArea` on a global variable.** `GetProvince` is confirmed
   working from the screenshots; these two follow the same pattern and
   `Area.GetNameWithNoTooltip` exists, but they have not been seen.

`error.log` names the file and line for GUI failures. A script effect that
merely does nothing logs nothing at all, which is what made every bug in this
mod so far invisible — check `game.log` too, that is where the load-time macro
expansion errors turn up.

## Where to check things

Everything a session needs is in `reference/` — EU5 1.3.10's `gui` and the parts
of `common` that matter, plus Community Mod Framework, Construction Manager and
Glorp UI. Grep it rather than asking for uploads.

The one thing that still has to come from the player is `logs/` after a test
run, because only they can run the game. Regenerate after a patch:

```
python3 mods/rgo_bonus_filter/tools/generate_rgo_filter.py reference/game/in_game/common
python3 mods/where_to_produce/tools/generate.py reference/game/in_game/common \
        reference/mods/community_mod_framework/in_game/common/scripted_effects
python3 mods/auto_build_ru/tools/generate_ru.py
```

Advanced Auto Build arrived in `reference/` without its `.metadata/`, so its mod
id and version are not in the tree. `auto_build_ru` therefore declares only CMF
as a dependency; if the base mod's id is wanted there, that file has to come
from the player's mod folder.


## Decisions already made, worth not relitigating

- **Provinces, not locations.** The bonus is province wide; ten locations of one
  province would score identically.
- **Volume is what compares two recipes.** The bonus is production efficiency,
  so it multiplies output: a jeweller's guild at 10% turns out 1.10, a village
  carver at the same 10% turns out 0.11. Ranking on the percentage alone put
  them level, which is what "I want to see the volume too" was about.
- **A building is worth what its best method is worth here.** Scoring walks a
  building's methods and keeps the best by whatever is being ranked on, and
  reports *that* method's figures and recipe. Taking the best percentage and the
  best volume independently would have been two different methods on one row.
- **A method that gains nothing here is passed over.** Its volume is the plain
  output, which every other province matches, so it says nothing about the place.
- **A building type's key is its own localization key**, so the flag standing for
  a candidate labels its row directly. A region, an area and a province have no
  such key, so those rows park theirs in a global and a fixed key per ordinal
  reads it back.
- **Tooltips are generated without words.** They are `$key$` references to the
  game's own method and goods names plus three captions written per language by
  hand, so one generated file serves every localization.
- **Town and rural are `pop_type`.** Burghers are the town half, labourers,
  peasants, slaves and clergy the rural one — which is the split the spreadsheet
  uses, and it matters because the two go in different kinds of location.
- **Only recipes that output something count.** A monastery burns clay for
  upkeep and produces nothing, so it has no efficiency to gain — which is why
  the game gates its own shovel badge on `IsProducing`.
- **The interface lives in the Mod Menu.** A custom window was built and thrown
  away: view objects only resolve inside their own panel, and CMM gives the
  framework's look for free.

## The one thing the game files here cannot answer

*Building* unlocks are solved: `can_build_building` in the country scope is the
engine's own answer and moves with advances and ages by itself.

What is left is one *method* of an unlocked building being locked behind an
advance. `ProductionMethod.IsAvailable` exists as a GUI data function, so the
game plainly knows, but there is no script-side counterpart and nothing in
`building_types/` or `production_methods/` records the unlock. A pre-Columbian
variant of a guild you do have still counts towards that guild's figure.

It is a small error now — the ages gate buildings, not methods within them — and
fixing it would need whatever holds the unlocks, `common/advances/` and the
technology folder beside it.

## Loose ends, none blocking

- The picker lists cap at twenty rows and the answer at twelve. A realm holding
  land in more than twenty regions, or twenty areas of one region, silently sees
  only the first twenty. Raising it means changing `LISTS` in the generator,
  which emits both switches, and adding the matching localization keys.
- The generator deletes what it no longer emits, so a generated file that
  disappears after a run was left over from an earlier design rather than lost.

## Hard-won facts that are easy to lose

- The RGO bonus formula, verified to the digit against three tooltips, is in
  [`../mods/where_to_produce/README.md`](../mods/where_to_produce/README.md). Every input
  counts in the divisor, produced goods included.
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
  cost a full round. `generate.py` checks for this across both
  `scripted_effects/` and `scripted_guis/` when given CMF's path.

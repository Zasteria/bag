# Handoff

Where the three mods stand, and what a fresh session needs to carry on. Read this
first, then [`RESEARCH.md`](RESEARCH.md) for how EU5 modding actually works —
most of that was learnt the hard way and will save a repeat.

## State

**The reference tree moved, and nothing broke.** Construction Manager 2.2.12 and
Community Mod Framework 2.4.1 came in, the second a real reorganisation of the
CMM list code. `tools/refresh.py` rebuilds everything from them and reports
clean: no generated file changed, and `tools/check_cmm.py` — the check that every
CMM macro is called with arguments CMF declares — still passes. What 2.4.1 added
is in [`RESEARCH.md`](RESEARCH.md#what-cmf-241-added).

**`goods_target/` — readings confirmed in game, goods list untested.** An addon
to Construction Manager: build the producers of goods you tick until
construction hits its discount cap, subsidising them on the way.

The measurement half is **verified** — the readings matched the game's own
construction tooltip on the first load ([`TESTLOG.md`](TESTLOG.md)), so
registration, `capital.market.market_price`, the per-good script values and a
live `ScriptValue` inside a CMM tooltip all work.

What is new and unrun is the goods list: 28 rows, two ticks each, Build and
Subsidise, plus the `_on_changed` scripted GUI without which a CMM list is
invisible rather than merely inert. The question for the next run is whether a
tick reaches script, and the monthly log line answers it in two independent
ways — a count, which cannot fail to render, and the goods named, which asks
CMF's log to render a goods scope.

Still nothing builds and nothing is subsidised. The order of the rest is in the
mod's README.

**`rgo_bonus_filter/` — working, in use.** Two filter chips, one per building
list. Nothing outstanding.

**`auto_build_ru/` — done, confirmed working in game.** Russian for Advanced Auto
Build, which ships English and Chinese only and so rendered as raw keys in a
Russian game. All 1201 keys are translated, the player reports the Mod Menu tab
reading correctly, and nothing is outstanding.

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
Порядок стран — в `mods/nd_ru/priority.txt`, остаток — `mods/nd_ru/tools/scope.py --plan`.

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

**`where_to_produce/` — removed, August 2026.** A Mod Menu tab that ranked what
was worth building in a province you picked. It never worked in game and the
owner stopped wanting it; the reason it did not work was never established,
because it was never tested. What it is worth knowing about it is in
[Why it failed](#why-where_to_produce-failed), below.

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
  [`RESEARCH.md`](RESEARCH.md#the-formula-behind-the-number) and in code in
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

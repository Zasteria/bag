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

**Do not ask for logs by default.** The owner said so on 2026-08-31 — a zip is
his time and the session's tokens both — and three loads running the answer was
"clean". Ask when something *did nothing* and the reason has to be either a GUI
error or a silent effect, when a crash or a load failure is in play, or when a
`cmf_log` was added for this run. A layout question, a number that looks wrong,
a filter that filters: the screenshot already says it.

## Runs

**2026-09-06, сборка `e9e1e2` — трёхклассовая доля отработала, число в число.**

`WTP SHARE rooms_town=24 rooms_village=126 | goods town_only=15 village_only=6
either=17 | ceilings town=1 village=21 all=3 -> bind=1 level=1 rest=5`

**Проверено арифметикой:** 24 ÷ 15 = 1.6, 126 ÷ 6 = 21, 150 ÷ 38 = 3.9 →
связывает городская сторона на 1; остальным (150 − 15) ÷ 23 = 5.87 → 5. Модель и
игра совпали до последней цифры. **Все пятнадцать «только городских» товаров
вышли ровно на 1** — старая формула обещала им 3, чего шесть городов не платят
никогда.

**Земля забита целиком** (150 из 150), покрытие выполнено (38 из 38), выгода от
места 80 % при 71.6 % от потолка — лучшие числа из всех прогонов.

**Что осталось неровным и почему:** ткань 15, кладка 12, лошади 10 против доли 5.
Это последний проход, `open800…open0`: он поднимает квоту всем по слою за круг и
дальше решает выгода — 33 домика из 150 (22 %) розданы после того, как все квоты
были взяты. Ровнее это сделает только правило «комнату берёт тот, у кого меньше
всех», и **это отдельный вопрос к владельцу, а не правка мимоходом**.

**Починен заголовок отчёта:** он печатал «доля земли 1 на товар» — один уровень
там, где их теперь два. Теперь «доли две: городской стороне 1, всем остальным 5».

**2026-09-06, сборка `54c7cd` — выхлоп отвергнут владельцем, доля переписана на
три класса.** Прогона у этой правки ещё не было.

**Его решение, и оно закрывает вопрос выхлопа:** «величина выхлопа не постоянна…
пивоварня 4 уровня = 4 выхлоп, гончарный завод 4 уровня = 3.25… решаю
довериться балансу разработчиков и посчитать, что мне не важен выхлоп, а важен
всё таки лимит домиков». Зонд `out=` при этом оставлен — он ничего не решает.

**Что построено вместо:** доля считается по трём классам товара («только
город», «только село», «где угодно») и двум видам комнат. На его земле A
(13 городов, 88 сёл) это 3.47 городским и 11.5 остальным вместо 8 всем; на
земле B (55 городов) — 9.42 всем, то есть **не меняется ничего**, и это верный
признак.

**Что ещё не согласовано:** доля редактора делит один котёл и классов не знает.

**2026-09-06, сборка `28788f` — иконки приняты, две земли разделены, и прогон
поймал мою ошибку в счётчиках.**

Его отчёт: «1. Всё хорошо» (товар над домиком), «выбор карты в общем плане и
выбор карты в расширении редактора — обособлены теперь и это хорошо»,
`ROWPAIR mismatched=0` — столбики не врут.

**Ошибка, которую нашёл сам отчёт.** Заголовок сказал «358 зданий на 690 мест
(52 % заполнено)» — а земля была забита целиком: 55 городов × 4 + 46 сёл × 3 =
**358**, ровно `placed`. Раздуты оказались `_plan_rooms` (690 вместо 358),
`_plan_towns` (69 вместо 55) и вместе с ними **доля: 18 вместо 9**, то есть
квота не ограничивала никого и раздачу решала одна выгода. Причина — доливка
**копила** эти три числа, а обнуляет их только `_plan_prepare`, которого она не
зовёт; загрузка слота при этом перестраивает `_plan_touched`, ничего не вычитая.
Теперь они пересчитываются по списку (`_ext_recount`), и разойтись им не с чем.

**Ещё два, оба его:** «в список не добавляется расширенная земля» — доливка
звала `_plan_rank`, но не `_plan_show`, и новые локации появлялись только после
переоткрытия окна; загрузка слота не переносила землю редактора на землю
загруженного плана.

**Что работало как задумано, хотя выглядело странно:** после расширения земля
редактора при переоткрытии осталась расширенной — она и должна, `_plan_touched`
теперь включает Нижнюю Саксонию, и это ровно «земля, на которой план стоит».

**И главное, что дал прогон, — первый настоящий замер выхлопа.** `out=`:
домиков от 1 до 24, выхлопа от 3.5 до 99.5, городской домик даёт 10–13.7 против
0.84–3.7 у сельского. Кладка с 20 домиками делает 27.5, пушки с 6 — 80.0.
Разбор и ответ на «как находить число, к которому стремиться»:
[`investigations/plan_share_sides.md`](investigations/plan_share_sides.md).

**2026-09-06, сборка `fa2dd1` — «Расширить» прошло на обоих прогонах, и проба
сошлась дважды из двух независимых мест.**

| | прогон A | прогон B |
| --- | --- | --- |
| локаций добавилось | 53 | 90 |
| мест было / добавилось | 150 / 166 | 150 / 286 |
| домиков поставлено | 166 | 286 |
| **сдвинулось на старой земле** | **0** | **0** |
| закреплений снято | 0 | 2 |

**Ноль подтверждён вторым счётчиком, который считает другое.** `WTP ROOM` в том
же отчёте печатает `moved=` — сколько локаций отличается от сохранённого плана, —
и там 53 и 90, ровно число **новых** локаций. Две метрики, посчитанные разными
обходами, говорят одно: доливка не тронула ни одного домика на земле X. Его
слова: «сдвинулось на основной земле 0».

**Снятие замка тоже сработало и тоже с числами.** В прогоне B доля выросла с 3
(150 комнат ÷ 38 товаров) до 11 (436 ÷ 38), и `pins_lifted=2` — оба закрепления
были ниже новой доли. Это то самое правило «замок спадает, когда доля его
перерастает», и оно впервые сработало в игре.

**`error.log` чист по доливке.** Из мода в нём только два давних: ключ
`bag_wtp_no_markets` без иконки и «`bag_wtp_end_out_rural` set but never used».
**И один настоящий, тоже давний:** у четырёх действий карты
(`bag_wtp_select_location/_province/_area/_market`) нет своих ключей имени и
описания — игра печатает `bag_wtp_select_location: "Bag wtp select location"`.
Кнопки читаются, потому что окна дают им `title`/`description` своими ключами,
но само действие безымянно.

**Что этот прогон не проверял:** большую вторую землю (90 локаций — не 233) и
доливку поверх плана, который уже правили руками.

**И один разбор, который прогон оплатил, — про равномерность.** Он смотрел на
«некрасивые числа» и на 25 пива при четырёх городах. Оба объяснились числами, и
второе объяснение — настоящая находка:
[`investigations/plan_share_sides.md`](investigations/plan_share_sides.md).

**2026-09-06, три прогона, которыми закрылись окна** — рамка, шапка и грамоты в ней: «Всё, окна починили». Записи целиком в
[`archive/testlog_wtp_windows.md`](archive/testlog_wtp_windows.md); правило — [`pitfalls/windows.md`](pitfalls/windows.md).

**2026-09-06, прогоны `dba516` и `00e5a2` — шаг 4 собран и принят: «выглядит
очень хорошо».** Провинции сворачиваются в обоих окнах плана, сортируются внутри
своих областей (обход внутри обхода, не упаковка ключей), свёрнутый вид включён
по умолчанию. Там же нашлись два молчаливых дубля script value и родилась
проверка на них. Записи целиком:
[`archive/testlog_wtp_provinces.md`](archive/testlog_wtp_provinces.md).

**2026-09-06, сборка `e00483` — шаг 5 закрыт, окно изменений отложено им самим.**
Прогона диагностики он не присылал и сказал, что она не нужна: «связка приезжает
целиком — всё хорошо», «строка нажатия — всё хорошо». Грамота из одного домика,
уступающая место связке из двух-трёх, была тем самым случаем, который терял домик
молча, и он больше не теряет.

**«Окно изменений задвигаем в дальний ящик»** — его слова: правок оно требует
много, а функциональности несёт мало. Грамоты в нём показываются, огрехи
остались, и **браться за них незачем, пока он не попросит**.

**2026-09-06, прогоны `6f094f0a` и `e170d103` — грамоты в редакторе, от «не
работает ни одна кнопка» до рабочего переезда.** Две ошибки, обе от чужой машины
плана: `_plan_right_fits_<k>` требует свободную комнату (ложно в готовом плане
всегда), и `_edit_place_town_<n>` отказывает на полном городе, так что связка
больше уходящей теряла домик молча. Оба правила — в
[`PITFALLS.md`](PITFALLS.md). Записи целиком:
[`archive/testlog_wtp_charters.md`](archive/testlog_wtp_charters.md).

**2026-09-06, прогоны `83ea98a6` и `23a56b9e` — журнал нажатий доехал, шаги 2а и
3 закрыты счётчиками.** Десять «+1» по одному товару выселили десять разных, а
`swaps=0` перестановки оказался ответом, а не поломкой: `pairs=23270 same=685
nofit=8844 worse=13730`. Оттуда же правило **разница — не журнал, хронологию
держит только лог** ([`pitfalls/diagnosis.md`](pitfalls/diagnosis.md)). Записи
целиком: [`archive/testlog_wtp_journal.md`](archive/testlog_wtp_journal.md).

**2026-09-06, прогоны `a69370f2` и сборка `ae1ed0` — доля редактора научилась
считать РГО, шаг 2а подтверждён числами.** Его находка: план вычитал РГО из доли
товара, а заливка редактора — нет. Починено (`_eq<n>`), зонд `eq=` в строке
`G<n>`, и `check_script.py` с тех пор разрешает каждый `ScriptValue`. Записи
целиком: [`archive/testlog_wtp_rgo.md`](archive/testlog_wtp_rgo.md).


**2026-09-06, сборки `be43d2` и `0b854a` — меню перестроено, интерфейс принят,
шаг 2 и шаг 2в закрыты.** Три прогона, всё принято его словами: «столбцы встали
как надо», «права встали как надо», «пикер товаров стал более читаемым», «сетка
редактора встала просто отлично». Правило, которое объяснило все три перекоса
сразу, — коробка с запасом места делит его между детьми — в
[`pitfalls/interface.md`](pitfalls/interface.md). Записи целиком:
[`archive/testlog_wtp_menu.md`](archive/testlog_wtp_menu.md).


## Waiting on a run

The next session should start here rather than designing anything new. All of
these are prepared, all are cheap, and the owner has agreed to the hover one.

**`where_to_produce`, twenty-eighth load.** Four small things and one question,
all of it one glance with the results window open. Not worth a run of its own.

1. **Any market can be taken now**, the neighbour's included — the list is every
   market in the world, framed by the ticked continents. Hover a market you hold
   nothing in and it should outline and click like the rest.
2. **The four picker buttons look like «Очистить выбор»** — solid, not
   transparent. Same in the rights window.
3. **The corner above the +/- buttons has a «+» in it** and «№» has not moved.
4. **«Восточная Мунтения» does not touch «Валахия»**, «Трансильвания» does not
   touch its percentage, and the row is four pixels narrower than it was.
5. **The one question: «Из чего».** The header and the row are identical column
   for column in the file, so if the icons still sit right of the heading, the
   cause is a constant inset the rows carry and the header does not. **What
   settles it in one look:** does «Сейчас» sit exactly over its percentages? If
   yes, the drift starts somewhere in the middle and I have the wrong model of
   it; if «Сейчас» is *also* slightly left of its numbers, every heading is, and
   `margin_left` is the one number to move.

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
- ~~**`where_to_produce`'s «В конце» plan.**~~ **Run 2026-09-03**, three times.
  What is still never run is **the whole plan on a large ground since the
  ladders were rebuilt**: Westphalia is 48 locations and its answer came back
  identical to the old build's, so nothing there tests the change. The press
  that would is the one of the earlier report — northern Germany, 233 locations,
  where the open pass used to place 271 buildings of 770.
- Everything `nd_ru` has translated apart from Westphalia — 3 600 keys that have
  never been on screen.

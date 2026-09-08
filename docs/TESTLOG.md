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

**2026-09-09, первая «Перетасовать» в игре — три ошибки, все названы числами**
(домики грамот уходили в обмен, ни одна деревня не менялась, «город 578 из
528», и `EDIT shuffle rounds=0` после перетасовки, переставившей 36 локаций).
Все четыре починены в тот же день, запись целиком —
[`archive/testlog_wtp_shares2.md`](archive/testlog_wtp_shares2.md).

**2026-09-09 — фильтр принят.** «Окей, фильтр работает.» Ступень по зубам и
деревни в списке — оба недочёта закрыты, шаг 7 видён в игре целиком.

**2026-09-09, сборка `57987f9` — «Из плана — сюда» показывает, и остались два
недочёта.** Владелец: «всё работает. И есть вероятность что и раньше работала,
просто я не те локации проверял» — но прошлый прогон это исключает: `target =
root` сравнивал список зданий локации с тем, что зданием не является, совпасть
не могло нигде. Временная проба «видна ли локация» своё отработала и снята.

**Первое: план «на конец» ставит ступень, которой ещё нет.** «Если в плане стоит
домик, который не доступен мне по уровню — мне не показывается… если мне в плане
стоит гончарка 4 уровня — надо чтобы мне показывался домик гончарки который мне
доступен по уровню». Панель сама не показывает недоступное, так что строка
товара пропадала целиком. Лестницу называет игра (`obsolete` в
`building_types`), «по зубам ли ступень» — `can_build_building` в скоупе страны;
у фильтра страны нет, поэтому ответ считается заранее в `_ba_<здание>`
(«Пересчитать» и `cmf_on_mod_registration`, то есть и на загрузке сохранения).
Фишка пропускает **самую высокую доступную ступень той же лестницы**.

**Второе: деревни не предлагались, а должны.** Ошибка была моя и одна строка:
список веток фишки собирался с вычетом `village_entities` — форма, верная для
обмена, где деревня стоит за несколько товаров, и неверная для списка зданий,
куда план кладёт деревню наравне со всеми.

**2026-09-09, сборка `ae7e5f1` — перетасовка работает, а фишка «Из плана — сюда»
не оставляет ничего, и это `root`.** Владелец: «Фильтр который показывает что мод
вообще может ставить в своих планах — работает. Из плана сюда — нет». Остальное
он «мельком потыкал, свиду работает», в числа не смотрел.

Что сказали логи, и они сказали всё: `FILTER view_location=1` — проба в панели
записала локацию; `ROWPAIR rows=454 mismatched=0` — `_plan_builds` заполнен на
454 локациях наравне с `_plan_goods`; `PASS placed=1503 rooms=1503` — земля
полная; `error.log` про фильтр молчит вовсе (2777 его строк — чужая
`LOCATION.GetRank.Custom('LR_PREP')`). Значит и проба, и данные на месте, а не
совпадает сам вопрос.

**Причина: `root` в фильтре — не отфильтровываемый объект**, что бы ни обещал
`58_building_type.txt`. Единственная другая фишка в репозитории, читавшая `root`
(`bag_rgo_has_local_bonus`), — ровно та, что никогда не работала; всё, что
спрашивает неявный `this`, работает; сама игра пишет «root is player» в
`06_country.txt`. Обе фишки переписаны на `this = building_type:X` **до** смены
скоупа, разбор — [`research/interface.md`](research/interface.md#filter-scopes-what-a-trigger-actually-gets).

**Перетасовка в том же прогоне сработала**: `button rounds=3 swaps=19 gain=8454
| rights rounds=3 swaps=3` — три грамоты переехали первым проходом, девятнадцать
домиков вторым. В числа он не смотрел, так что это лог, а не приёмка.

**2026-09-07, сборка `aff13a` — резервация по стеснённости отработала в полную
силу и не сдвинула ничего**, а прогон закрыл сам вопрос: план уже был ровен.
Правило снято тем же днём, разбор целиком —
[`archive/plan_reservation.md`](archive/plan_reservation.md).

**2026-09-06 и 09-07, восемь прогонов до потолка здания** — иконки, две земли,
«Расширить», первый замер выхлопа, специализация, трёхклассовая доля и приём
раздачи уровнями. Записи целиком в
[`archive/testlog_wtp_editor.md`](archive/testlog_wtp_editor.md) и
[`archive/testlog_wtp_northern_germany.md`](archive/testlog_wtp_northern_germany.md).

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
- `rgo_bonus_filter`'s build-panel chip. Его же **панельная пара чинилась**
  2026-09-09 по чужой причине: она читала `root`, и это была та же
  ошибка, что у `where_to_produce`.
- ~~**`where_to_produce`'s «В конце» plan.**~~ **Run 2026-09-03**, three times.
  What is still never run is **the whole plan on a large ground since the
  ladders were rebuilt**: Westphalia is 48 locations and its answer came back
  identical to the old build's, so nothing there tests the change. The press
  that would is the one of the earlier report — northern Germany, 233 locations,
  where the open pass used to place 271 buildings of 770.
- Everything `nd_ru` has translated apart from Westphalia — 3 600 keys that have
  never been on screen.

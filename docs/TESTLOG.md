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

**2026-09-08, одиннадцатый прогон — раздача принята.** «Кажется постановка всего
что надо наконец отрабатывает как положено». Земля 1380 из 1380, **обе стороны
полные** (город 528 из 528, село 852 из 852), доли 19/55/74, 36 товаров из 37
остановила своя квота, единственный по земле — железо (43 при квоте 63). Средняя
выгода 64.0 % против 63.0 % накануне.

**Остаток «−1» измерен и он весь — остаток от деления.** Сумма городских потолков
544 на 528 комнат: лишних 16. Ниже своего городского потолка ровно 18 товаров, и
двое (`dyes`, `wine`) стоят на единицу **выше** — грамота потолка не спрашивает.
18 − 2 = 16, сходится до единицы. В селе: 709 + 151 у деревень = 860 на 852,
лишних 8 — и ровно 8 товаров на единицу ниже. **Ни один домик никуда не пропал:
все комнаты заняты**, а товар ниже потолка стоит потому, что комната досталась
соседу.

**2026-09-08, десятый прогон — земля 1380 из 1380, и арифметика поймана на
четырёх местах.** Скидка внутри дележки сработала: доли 21/56, «Доля» три
числа, рыба ушла, прочерки на месте. Владелец: «арифметика любит красоту» —
и назвал четыре расхождения, все настоящие.

**Все на единицу ниже своей доли.** Раздача кончается двумя пустыми кругами
подряд, а прибавку сделал первый из них: она заведомо никому не досталась, но
осталась в доле. Теперь последняя прибавка отменяется.

**И доля росла сразу на обеих сторонах.** Городу хватало 19, селу нужно было
55; поднимали обе вместе, и городской потолок уходил на 21 там, где товар
доходил до 18. Теперь сухой круг поднимает долю **той стороны, где ещё есть
свободные комнаты** — считают их `_plan_pt`/`_plan_pr`, они же в отчёте как
`filled=`.

**Камень 73 домика при квоте 62, 88 «с РГО» против 75 у всех.** Проход
стеснённых ставил домик в **каждую** подходящую локацию и квоту не спрашивал,
а «стеснённая сторона» снимала потолок с обеих сторон сразу — камень получал
`_pq` на каждой. Проход теперь держит квоту (`limit` пересчитывается на каждой
локации), а стеснённой стороны как особого случая больше нет.

**Соль 42 из 60 при 68 доступных местах.** Два виновника. Сельской доли 55 её
земля (42) принять не может, и тринадцать доли пропадали — теперь **переливаются
в город**. И проход стеснённых заливал 42 сельских домика разом, `_pn` уходил
выше уровня, а к тому кругу, когда уровень догонял, городов не оставалось —
**уровень теперь считается по своей стороне**, как и всё остальное в двух котлах.

**Доля стороны теперь берётся на единицу ниже найденной**, а сухой круг доводит
её ровно до той, на которой земля заполнилась: наименьшее X по формуле накрывает
комнаты с запасом (при 20 потолков выходило на 577 домиков при 528 комнатах).

**2026-09-08, девятый прогон — таблица принята, а земля недобрала 259 комнат.**
Доли встали как считалось: город 12, село 50, «Доля» ровно три числа (12, 50,
62), прочерки на месте, шерсть 18, рыбацкая деревня 42 из 42, железо 43 из 43.
Ровность идеальная — 37 товаров остановила своя квота. **Но земля 1121 из
1380.**

**Причина названа числом, а не догадкой, и она одна: скидка за РГО считалась
после дележки, а не внутри неё.** Доля искала наименьшее X, при котором
`Σ min(своя земля, X) >= комнаты` — а строил товар `X − свои РГО`. Всех РГО на
этой земле 284, и ровно столько комнат оставалось пустым (259 из 284; остальное
съели товары, которым и земли не хватило). Модель проверена на самом прогоне:
ёмкость села по формуле 767 при 758 поставленных, ёмкость города 305 при 363 —
разница ровно грамоты, которые потолка не спрашивают.

**Формула теперь ищет X по тому, что товар действительно поставит**:
`Σ min(земля, X − РГО) >= комнаты`. Тогда каждый кончает ровно на X **считая
РГО** — та самая мерка равномерности, — и земля заполняется. **И комнаты снова
берутся все, включая занятые грамотами**: грамота ставит домик того же товара,
потолок товара его накрывает, а вычет считал их дважды. Считанные числа: город
**20**, село **55**, двусторонний товар кончает на **75**. **Сухой круг снова
поднимает долю** — но уже только как страховка от спора за общее здание.

**Его правки по сводке того же дня**: прочерк в столбце РГО у товаров, у
которых РГО не бывает (все готовые), и **рыба уходит из корзины совсем**, как
шёлк: «мы смотрим на домики, которые можно сделать, а рыба нынче такой не
является». `_ng` теперь сумма своих сторон, а не «где товар может появиться».

**2026-09-08, восьмой прогон — доли встали, но три товара считались в сельском
котле призраками.** Железо взяло все свои 43, рыбацкая деревня — все 42, доли
город 12 / село 42. Скриншот сводки вскрыл другое: у украшений, инструментов и
оружия «доля 54» при вечном нуле в столбце «село». Их сельское здание —
`pounamou_carver` и `tatara`, в Европе их нет; в село их пускали 284 места
торговой деревни, которые им не принадлежат. Они входили третьими лишними в
сельский делитель: 21 участник вместо 18, и сельская доля выходила 42 вместо
50. Считать сельские места теперь можно только под своё здание — тем же
условием, что стоит в воротах `_plan_can_rural_<n>`. **В игре не было.**

**Тем же прогоном: `_pqt`/`_pqr` вычитали РГО со стороны, которой у товара
нет.** Шерсть: доля 42, РГО 32, `q=10` — а сельский потолок 22, потому что 12
скидки ушли в несуществующий городской. Теперь сторона, которой нет, стартует с
нуля, и `доля город + доля село = доля − РГО` сходится.

**Его правки по сводке, 2026-09-08** (все построены): «Всего (с РГО)» → «С
РГО»; «Домиков» → «Домики»; прочерк вместо нуля там, где товар не может стоять
на этой стороне вовсе; и вместо одной «доли» — четыре столбца: доля, доля −РГО,
доля город, доля село. «Доля» — ровно три числа на всю таблицу: 12, 50 и 62.

**2026-09-08, прогоны третий–седьмой** — регрессия `_plan_set_caps`, «доля
минус один», сельский котёл принят (1380 из 1380), пустой проход стеснённых
и грамоты вон из городской доли. Записи целиком в
[`archive/testlog_wtp_shares.md`](archive/testlog_wtp_shares.md).

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
- `rgo_bonus_filter`'s build-panel chip.
- ~~**`where_to_produce`'s «В конце» plan.**~~ **Run 2026-09-03**, three times.
  What is still never run is **the whole plan on a large ground since the
  ladders were rebuilt**: Westphalia is 48 locations and its answer came back
  identical to the old build's, so nothing there tests the change. The press
  that would is the one of the earlier report — northern Germany, 233 locations,
  where the open pass used to place 271 buildings of 770.
- Everything `nd_ru` has translated apart from Westphalia — 3 600 keys that have
  never been on screen.

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

**2026-09-06, прогон на `dba516` — свёртка провинций принята, три правки по его
списку и два молчаливых дубля, найденных по дороге.**

**Его вердикт:** «выглядит очень хорошо», интерфейс в остальном устраивает.
Заказано: сортировка внутри областей, галочка включённой по умолчанию, и окно
редактора — грамоты в две строки, пустота под ними, шапка не тянется.

**Сортировка: области сперва, провинции внутри области.** «Я не хочу, чтобы
провинции разных областей были в перемешку.» Сделано **обходом внутри обхода**, а
не упаковкой двух ключей в одно `order_by`: предел фиксированной точки движка
отсюда неизвестен. Область узнаётся через `area = scope:X.area` — идиома взята из
`reference/playset/…/OGAS_script_values.txt`, а не выдумана. **Порядок один на оба
вида списка:** `_plan_prank` несёт его целиком.

**Шапка окна не тянулась ни в одном из пяти окон, и он говорил об этом трижды.**
Причина одна строка: `layoutpolicy_horizontal = expanding` на
`window_header_alt`. **Собственные окна игры её несут все** —
`multiplayer_lobby.gui`, `automation_lateralview.gui`. Дописана во все пять.

**Грамоты: пять колонок по три вместо трёх по пять**, блок 100 в высоту вместо
168 — это и была «пустота под ними». Держава выдаёт девять-десять из тринадцати, а
невидимая ячейка в колонке места не занимает, так что на его земле выходит две
строки.

**И два дубля script value, оба мои и оба немые.** `bag_wtp_show_edit_presses` и
`bag_wtp_show_plan_provn` были определены дважды: первый выигрывает, второй
молча выбрасывается, и правка не в той копии просто ничего не делает.
**Теперь это ловит `check_script.py`** — проверено на подломленном имени.

**2026-09-06, сборка `dba516` — шаг 4 собран, в игре не запускался.** Провинции
сворачиваются в окне плана и в окне редактора: галочка «По провинциям» одна на оба
окна, свёрнутый вид — **второй список рядом с плоским**, а не другая его форма
(строка датамодели видит один скоуп, так что строка провинции и строка локации не
могут быть одной строкой). Локации под провинцией берутся из
`GetProvinceDefinition.GetLocations` и гасятся по `_plan_rank`; строка — тот же
`bag_wtp_plan_entry`, что и в плоском списке.

**И одна находка проверки по дороге:** `bag_wtp_plan_area_tt` стоял подсказкой в
строке плана и **не был определён нигде** — ключ рисовался бы на экране. Поймал
`check_script.py`, когда я скопировал ту же строку в строку провинции.

**2026-09-06, сборка `e00483` — шаг 5 закрыт, окно изменений отложено им самим.**
Прогона диагностики он не присылал и сказал, что она не нужна: «связка приезжает
целиком — всё хорошо», «строка нажатия — всё хорошо». Грамота из одного домика,
уступающая место связке из двух-трёх, была тем самым случаем, который терял домик
молча, и он больше не теряет.

**«Окно изменений задвигаем в дальний ящик»** — его слова: правок оно требует
много, а функциональности несёт мало. Грамоты в нём показываются, огрехи
остались, и **браться за них незачем, пока он не попросит**.

**2026-09-06, прогон `6f094f0a` — грамоты переезжают, и он поймал в них
настоящую дыру.**

**Что подтвердилось.** 156 нажатий по грамотам, все прошли: «+1» забирает город у
той, что выше доли, «−1» отдаёт наследнику, строка нажатия называет обе грамоты и
город. По отчёту **47 связок из 47 целы** (48-я строка обрезана на конце лога).
Шрифт грамот принят: «пойдёт».

**Его находка, и она верна по коду, а не по прогону.** «Из города уходит только
ювелирный домик, а стекольному праву надо два — стекло и кладка, но для кладки
места не нашлось.» **`_edit_place_town_<n>` отказывает на полном городе** — это
инвариант, поставленный 2026-09-04 после 27 домиков сверх лимита, — а обмен
сажал до того, как освобождал место. Связка больше входящей уходящей теряла
лишний домик **молча**.

**Починено порядком: сначала место, потом связка.** `_edit_right_need_<k>`
считает, сколько комнат связка действительно хочет здесь (товар, который уже
стоит, комнаты не просит), `_edit_right_make_room` трижды освобождает по одной,
пока `load + need` выше лимита, и только потом сажает. **Тот же счёт после
посадки — это то, что не влезло**: `_edit_rshort` в журнале (`short=`) и своя
строка нажатия, потому что связка наполовину не должна читаться с карты.

**Три правки интерфейса по его словам:**

- **«Снять закрепления» и «Показать изменения» переехали в строку слотов**, где
  место стояло пустым; строка нажатия забрала всю освободившуюся ширину — «текст
  не показывается полностью».
- **Окно изменений называет грамоту с обеих сторон** — «право, товары ушли —
  право, товары встали». Слева `_save_right_label`, справа `_plan_right_label`.
- **Переезд грамоты считается изменением, даже если ни один домик не двинулся**:
  корабельные и смоляные — одна и та же связка, и без этого город выпал бы из
  списка.

**2026-09-06, прогон `e170d103` — блок грамот встал, а нажатия по ним ничего не
делали. Причина одна на оба симптома, и она в диагностике.**

**Что он увидел.** «+1» — «не нашлось города», все четыре нажатия. «−1» — город
находился (Фехта, Варбург, Эссен, Бохум, Дортмунд), но «город передать некому».

**Причина: я спросил чужой вопрос.** Обе стороны проверяли
`bag_wtp_plan_right_fits_<k>`, а он собран из `_plan_can_town_<n>`, у которого в
условии стоит **`var:_load < global_var:_plan_cap_urban`** — свободная комната. Он
верен для раздачи, которая обходит **пустые** города; в готовом плане свободных
комнат нет вовсе (`ROOM … towns_with_room=0`), так что триггер ложен везде. «+1»
не находил ни одного кандидата, «−1» не находил наследника — **одна причина, оба
симптома, и оба на экране читаются как «кнопка не работает»**.

**Починено тремя правками:**

- **`_edit_right_fits_<k>` — свой вопрос редактора:** город, и `var:_pm<n> > 0`
  хотя бы у одного товара связки. Что уже стоит — не отказ: обмен ставит
  недостающее, а остальное входит в связку через `_plan_right`.
- **Подстановка `glass` → `sand` тоже решала по `_plan_can_town_<n>`** — на полном
  городе она сажала бы заменитель всегда, а снятие вынимало бы не тот домик.
  Теперь решает `var:_pm<n> > 0`.
- **Недобор грамоты больше не прижат к нулю.** При доле 5 грамота с шестью
  городами и грамота с пятью обе давали «недобора нет», и «−1» мог отдать город
  тому, у кого их и так больше всех. Теперь `_rsh<k> = доля − города` со знаком.

**И журнал называл «+1» грамотой №0** — он печатал `rto`, который ставится только
внутри обхода, а обход не запускался. В строку добавлено `right=` — то, на что
нажали, а не то, чем кончилось.

**Правка интерфейса по его словам** «текст городских прав можно попытаться
увеличить… шрифт и иконки слегка»: ячейка 330×28 → 360×32, имя 14 → 17, счётчик
16 → 18, кнопки 14 → 16. Иконка — тексикон внутри имени, растёт вместе со шрифтом.

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

# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## Работа: `where_to_produce` — один прогон, и это последнее

**Раздача закрыта прогоном 2026-09-08**, разбор —
[`archive/wtp_brief_plan_rules.md`](archive/wtp_brief_plan_rules.md).
**Перетасовка — кнопка в окне редактора, два прохода, переезд между
провинциями**; первый проход — сами грамоты. Прогон 2026-09-09 напечатал
`rights rounds=3 swaps=3 | button rounds=3 swaps=19`, но в числа он не смотрел —
это лог, а не приёмка. Разбор —
[`investigations/plan_gaps.md`](investigations/plan_gaps.md).

**Шаг 7 видён в игре, шаг 8 нет.** Устройство обоих и три правила, которые
дороже прочих (`root` в фильтре — не сам объект; `_stands_<здание>` слушается
тумблера ранга и потому не годится ни для чего, что делает игра; ступень берётся
по `_ba_<здание>`) — [`investigations/wtp_integration.md`](investigations/wtp_integration.md).

**Житницы CM план обходит стороной**: ни домика, ни грамоты, и её мест не
считает — но из списка она не пропадает, РГО считается как раньше и выгода
провинции не меняется. Кнопка житницы стоит в ряду локации там же, где её
предлагает CM.

**Мод строит и зданиями чужих модов** — их читает генератор, кладя `common/`
каждого мода из `reference/mods` поверх игровой. **Цена измерена и она немалая**:
241 → 656 методов, `in_game` 11 → 18 МБ, `check_script` 1.8 минуты. Если
загрузка или «Пересчитать» станут заметно дольше — резать по `country_potential`
(почти вся прибавка — национальные здания ND), а не по категории.

**«Снести лишнее»** — три кнопки теми же группами, сносят производственные
здания вне плана и только их. **Мод ничего не делает периодически** — это его
требование; строка `CM found/were_on/touched` говорит, что сделало последнее
нажатие отмашки, а `found=0` значит «в группе нечему стоять», а не «кнопка не
работает».

**Просить один прогон, и он закрывает всё разом:**

1. «Пересчитать» → «Перетасовать» → «Диагностика», и отдельно «Расширить».
   Ждём: домиков ровно столько же, `по сторонам` ровно 528/852, ни один домик
   грамоты не тронут.
2. **Житница.** Включить в CM режим житницы на одной локации плана, нажать
   «Пересчитать»: домиков в ней стать не должно, «мест» в шапке — на её потолок
   меньше, а РГО и выгода соседей по провинции — прежними.
3. **Чужие здания.** У страны, у которой `trin_national_destinies` даёт свои
   производственные здания, пересчитать план: её здания должны в нём появиться
   наравне со всеми. И заметить, не стала ли загрузка или «Пересчитать» заметно
   дольше — файлы выросли с 11 до 18 МБ.
4. **«Снести лишнее».** В локации с лишними производственными зданиями нажать
   иконку сноса: лишние уходят, плановые остаются, всё непроизводственное
   (гарнизон, порт) не трогается. Начать с одной локации, а не с «всего плана».
5. **Автострой.** Открыть локацию рядом с окном плана, нажать иконку со
   стрелками вверх в её ряду — галочки автостроя у домиков плана в этой локации
   должны включиться разом. Второе нажатие — снять. То же по провинции и по
   всему плану. Строку «Автострой CM» в диагностике смотреть, только если
   ничего не переключилось.

**Что читать про `_plan_*`, и больше ничего:**
[`plan_gaps.md`](investigations/plan_gaps.md) — открытое и закрытое;
[`plan_as_reservation.md`](investigations/plan_as_reservation.md) — раздача
уровнями; [`wtp_editor_design.md`](investigations/wtp_editor_design.md) —
правила редактора.

### Что стоит и работает — шаги 0–6

Земля, ранжирование, план, редактор, слоты, «Расширить», сводка и специализация
— всё видено в игре; числа в [`TESTLOG.md`](TESTLOG.md). **Три правила, которые
переживают всё:** состояние редактора — редакторово, и
свежий план его не читает; работа с `.gui` начинается с
[`pitfalls/windows.md`](pitfalls/windows.md); локация держит по одной деревне
каждого из четырёх видов, а две одинаковых — нет.

**Instrument before the third theory** and **do not spend his run on a guess** —
[`pitfalls/diagnosis.md`](pitfalls/diagnosis.md).

## The job: `mods.bat`, and one run to confirm it

**Both halves are repaired and neither has been run on his machine** — a failed
steamcmd run looked exactly like a successful one
([`archive/mods_bat_repair.md`](archive/mods_bat_repair.md)). **Ask for:**
`mods.bat → 1`, `→ 4`, `mods.bat check`, and the output of all three. Logs go
through `python3 tools/which_build.py <logs folder>` first, as always.

## Then `glorpui_hints` goes out

Nothing outstanding; publishing is five steps in
[`WORKSHOP.md`](WORKSHOP.md#putting-glorpui_hints-out-in-order), the lists are in
[`archive/next_glorpui_publish.md`](archive/next_glorpui_publish.md).

## Also waiting on the owner, all of it cheap

- **`mods.bat → 2` on his machine.** The 2026-08-28 files of Advanced Auto Build
  and Glorp UI are still not in this tree; both generators were fixed against
  rewritten copies. Entry 2 does **not** re-extract the game.
- **The panel-open bisect and the hover run** — protocols written out in
  [`investigations/panel_hitch.md`](investigations/panel_hitch.md) and
  [`investigations/widget_leak.md`](investigations/widget_leak.md), every branch
  with its next step. **Do not design a different test until they have run.**

## Before asking him for anything

Read [`SETTLED.md`](SETTLED.md). And walk the protocol as the person who has to
do it: *"sit on the map and open nothing"* is impossible while events fire, which
is why everything is paused now. He cannot be asked to run a thing twice.

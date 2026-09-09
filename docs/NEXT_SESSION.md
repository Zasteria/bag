# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## Работа: `where_to_produce` — построено всё, остался прогон

**Раздача закрыта прогоном 2026-09-08**
([`archive/wtp_brief_plan_rules.md`](archive/wtp_brief_plan_rules.md)).
**Перетасовка, шаг 7 и шаг 8 построены**; фильтр «Из плана — сюда», кнопка
житницы и «снести лишнее» видены в игре, автострой и здания чужих модов — нет.
Устройство всего, что мод делает в чужих окнах, и правила, которые дороже
прочих, — [`investigations/wtp_integration.md`](investigations/wtp_integration.md);
про `_plan_*` — [`plan_gaps.md`](investigations/plan_gaps.md) и
[`plan_as_reservation.md`](investigations/plan_as_reservation.md).

**Три числа в диагностике существуют затем, чтобы не гадать**, и все три обязаны
быть тем, чем названы: `FOREIGN ... unbuildable=` — ноль; `EXT ... moved=` —
ноль; `CM found/were_on/touched` — что сделало последнее нажатие отмашки.

**Цена чужих модов измерена**: 241 → 656 методов, `in_game` 11 → 18 МБ,
`check_script` 1.8 минуты. Загрузка, по его слову, «как обычно». Если станет
дорого — резать по `country_potential`, а не по категории.

**Продовольственный потенциал стоит в строке каждой локации с
продовольственным сырьём** — то же число, что красит режим карты CM, но своим
значением: формула списана генератором, мод без CM от этого не ломается.

### Идея, названная 2026-09-09 и не построенная: грамоты из плана

Он хочет выдавать грамоты по плану и предложил подсунуть в список приоритетов CM
абстрактную строку «право из плана», у которой CM спросил бы, что лежит в ячейке
этого города. **Так нельзя, и это факт из его кода**: `cm_run_auto_town_rights`
идёт по `cm_auto_town_rights_list` и выдаёт `scope:cm_town_right` — ровно то, что
лежит в строке; ветки «спроси у мода» там нет, как нет `default` в его `switch`
возможностей. **CM расширяем там, где он сам это предусмотрел.**

**Но цель достижима короче, и всё нужное уже стоит**: право города план держит на
локации (`_plan_right`), `grant_town_rights` — обычный эффект в скоупе локации,
ворота (`has_max_town_rights`, `can_grant_town_rights`, `price:grant_town_rights`)
читаются из скрипта. Это ещё одна **отмашка** той же формы, что автострой: три
кнопки — локация, провинция, весь план. Производственные права в списке CM и так
намеренно выключены. Работа небольшая: новых механизмов не нужно ни одного.

**Просить один прогон, и он закрывает всё разом:**

1. «Пересчитать» → «Перетасовать» → «Диагностика», и отдельно «Расширить».
   Ждём: домиков ровно столько же, `по сторонам` ровно 528/852, ни один домик
   грамоты не тронут, `unbuildable` и `moved` — нули.
2. **Чужие здания.** Держава, которой ND что-то даёт: её здания в плане есть,
   чужих нет. И галочка мода на «Технической» — снять, пересчитать, вернуть.
3. **Автострой.** Иконка со стрелками в ряду локации: галочки автостроя у
   домиков плана включаются разом, второе нажатие снимает. То же по провинции и
   по всему плану.

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

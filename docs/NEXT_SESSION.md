# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## Вторая версия мода закрыта, работа возвращается в первую

**2026-09-12: `where_to_produce_v2` построен и удалён в тот же день**
([`archive/wtp2_failed.md`](archive/wtp2_failed.md)). Его решение: править
готовую первую версию, а не строить рядом новую. **Чужой инструмент, который
просят «взять», — копировать файлами, а не воспроизводить формулой.**

**Список пришёл 2026-09-12 и записан целиком** —
[`investigations/wtp_backlog.md`](investigations/wtp_backlog.md). Девять пунктов
плюс решение, из которого следует половина работы: **он снял с плейсета CM и
Glorp UI** («оба снижают производительность, особенно CM»); CMF остаётся.

## Работа: `where_to_produce` — пять пунктов списка построены, прогона не видели

**Построено 2026-09-12 и ни разу не загружено**: лесопилка и её класс (пункт 1),
галочка «Режим специализации» вместо кнопки на странице мода (2), две карты CM
перенесены файлом (3), одна грамота на провинцию от девяти провинций (5), ворота
`allow` у самого метода (8). Что именно смотреть в игре — в конце
[`wtp_backlog.md`](investigations/wtp_backlog.md); разбор двух закрытых дыр —
[`archive/wtp_lumber_and_allow.md`](archive/wtp_lumber_and_allow.md).

**Не построено и ждёт**: план для житниц (4), ручная замена домика и грамоты в
плане (6), карта «предлагаемые городские права» из CM dev (7), режим ручного
заполнения (9) — и **ванильная отмашка автостроя**, которая без CM молча
перестала работать. Её API измерен и он только интерфейсный
(`ToggleAutoExpandBuilding`, `ToggleAutoExpandBuildings`,
`BuildInLocationLateralView.ToggleAutoExpandAllBuildings`); эффекта в скрипте
нет. **Проектировать её надо с зондом, а не сразу целиком.**

## Старое по `where_to_produce`, до его списка

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

### Отложено: грамоты из плана

Идея 2026-09-09, разобранная до конца и не построенная:
[`archive/wtp_charters_from_plan.md`](archive/wtp_charters_from_plan.md). Новых
механизмов не нужно ни одного; встала в очередь за его списком.

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

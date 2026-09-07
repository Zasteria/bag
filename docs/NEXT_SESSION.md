# Next session: the job in progress

Six mods, a pile of documents and more history than any session should read.
This file is the part that is live. What has already been settled is in
[`SETTLED.md`](SETTLED.md); where each mod stands is [`STATUS.md`](STATUS.md).

## Работа: `where_to_produce` — резервация по стеснённости, потом перетасовка

**Он выбрал порядок, 2026-09-07: сначала резервация, потом перетасовка.**
Проект первой написан целиком и его не надо выводить заново:
**[`investigations/plan_reservation.md`](investigations/plan_reservation.md)** —
правило, три места в коде, что оно должно дать в числах и по какому признаку его
снимать. Перетасовка описана там же, в конце, и берётся **после** прогона первой.

**Что читать про `_plan_*`:**
[`investigations/plan_gaps.md`](investigations/plan_gaps.md) — открытое и
закрытое; [`plan_as_reservation.md`](investigations/plan_as_reservation.md) —
как устроена раздача уровнями; [`wtp_practice_plan.md`](investigations/wtp_practice_plan.md)
— порядок шагов; [`wtp_editor_design.md`](investigations/wtp_editor_design.md) —
правила редактора. Больше ничего.

### Что стоит и работает — шаги 0–6 плюс три вещи 2026-09-07

Земля, ранжирование, план, редактор, слоты, «Расширить» — всё видено в игре.
**Раздача уровнями**: круг поднимает уровень на единицу, товар берёт не больше
одного домика за круг, полоса выгоды решает «где», а не «сколько». **Сводка** —
иконка в окне плана: строка на товар и причина остановки. **Специализация** —
кнопка на странице мода
([`plan_specialisation.md`](investigations/plan_specialisation.md), закрыта как
есть, редкость в неё не добавлять).

**Два прогона на северной Германии приняли всё это.** 416 локаций, 1380 зданий на
1380 мест, кругов 89 при пределе 150. Только городские товары легли в **15…17**,
умеющие в село — в **50…65** считая РГО; ниже только рыба (39) и судовые припасы
(38), потому что 42 прибрежные локации заняты рыбацкими деревнями на 93 %.
`iron` с лучшей выгодой **ноль** взял 39 мест из 43 — полосы выгоды действительно
перестали решать «сколько».

**Три правила, которые переживают всё:** состояние редактора — редакторово, и
свежий план его не читает; работа с `.gui` начинается с
[`pitfalls/windows.md`](pitfalls/windows.md); локация держит по одной деревне
каждого из четырёх видов, а две одинаковых — нет.

### The share, and the tiers, as they stand

A good builds while under the **level**, its **total quota** and the **cap of the
side it builds on**; the scarce tiers are a **share of the ground** (2…32 %) with
1/2/4/8/16 as floors, counted **per side** since 2026-09-07. Side quotas alone and
output weights were rejected on numbers
([`investigations/plan_share_sides.md`](investigations/plan_share_sides.md)).

### Порядок работ, и он его: 1 — резервация, 2 — перетасовка, 3 — шаги 7 и 8

Ни один из трёх не начинать раньше предыдущего. **Просить у него один прогон на
пункт**: «Пересчитать» на северной Германии и «Диагностика» — этого хватает,
чтобы сказать, работает правка или снимается.

### Шаги 7 и 8 — чужие моды, и они последние

**His order, 2026-09-04: «доработать все начатые функции мода и потом уже
пытаться интегрировать его в функционал CM и glorp».** 7 is the plan shown in
the location panel, inside Glorp UI's own interface. 8 stamps the plan onto
Construction Manager, gated on CM being present — and the space the goods icons
used to hold in the plan rows is the space he is keeping for CM's links.
**A session taking either one re-reads those mods' files** — `python3
tools/refs.py` for the version, grep for the name. He also offered `cheatmenu` and
Advanced Auto Build's interface for `reference/`
([`CONVENTIONS.md`](CONVENTIONS.md)).

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

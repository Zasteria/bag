# Pitfalls — the interface

Split out of [`../PITFALLS.md`](../PITFALLS.md) when it outgrew its budget. Same
rule as the rest of that file: every entry here cost a round trip through the
game, and none of them raises an error you would notice.

Ask for one rather than reading the file: `python3 tools/kb.py <words>`.


**«An expanding child in a sized parent» is about the child, not the parent.** An
expanding child inside a sized parent comes out at zero; a widget that has both
an expanding policy **and a size of its own** is a different thing and is not
fatal — three of them have drawn correctly since the first build. Reaching for
that line to explain an empty window on 2026-09-04 was a guess and did not
survive the scan that tested it.

**A `flowcontainer` with a `datamodel` of its own crashes the game.** Silently,
natively, with nothing in `error.log`, `gui.log` or `debug.log`. It cost four
builds, five of the owner's runs and four sessions, because each of those
sessions looked at what was *inside* the window instead of at the widget holding
it. **Seven builds settle it zero for zero and one for one**: the three without
the widget opened, the four with it crashed — one of them on loading, with 47
written-out children instead of a datamodel. **The variable map, the flag key, the `ScriptValue`
in a localization value and the texticon were all innocent** — three of them were
reverted for nothing, and the fourth build removed every map in the mod and still
died, harder, because static children are built when the window is created rather
than when the list fills.

**The game's own files say it plainly, and nobody asked them.** There is no
`flowcontainer` with a real datamodel anywhere in vanilla; a wrapping grid of a
list is a `fixedgridbox`, all 138 times the game draws one. **`check_script.py`
refuses the pairing now.** And **the `fixedgridbox` that replaced it laid the
cells out wrong on its first load** — some past the window's edge, some drawn
underneath each other — so **the picker does not wrap at all**: the rows are cut
in the generator and the window draws five of them. **Where a layout can be
decided in script, decide it in script.**

**A variable read on the wrong scope is a condition that is quietly false, for
ever.** The plan editor's `_edit_good` was written with `set_variable` in a
country-scoped effect and read with `var:` in two places: at the top of the
effect, where the scope is the country and it worked, and inside
`ordered_in_global_list`, where the scope is **the location the walk stands on**
and the variable is not there. So the dispatch that places the building matched
nothing, ever — three builds of «+1» evicting a building, failing to place, and
putting the victim back, with nothing on screen able to tell that from a rule
refusing. **A number carried across scopes is a global, no exceptions**, and
`check_script.py` now refuses a name written only globally and read as `var:`.

**And it was named the first time the numbers were in the report**, not the
fourth: `evicted=1 room=1 | placed_before=191 placed_after=192` with `done=0
fail=1` says the whole story in one line. **Instrument the thing before the
third guess, not after the fourth.**

**A shape is only proven for what it was proven doing.** `hbox` + `datamodel` +
`datacontext = "[Scope.GetGoods]"` draws every location's goods in the plan
window and has never come out wrong — but its cell is a `text_single`. **A
clickable cell in one was never tested**, and when the picker became one, 15
presses did nothing at all. Say what a shape is proven for, not that it is
proven.

**And a global that survives a save will lie about the present.** The editor's
«Последнее нажатие: сделано» came from an `_edit_done` set an hour earlier, and
because that branch is tested first it hid the branch that says the press never
arrived. Worse, it read as *evidence the press worked*. **A window that opens
has taken no presses: reset what it reports, and put a counter on it** — a press
counter separates «the button is not wired» from «a rule refused» at a glance,
which is two runs' worth of question answered without a log.

**And the lesson under the lesson: a build that was never loaded is not a
baseline.** `c14aa0f` introduced the flowcontainer and was never run; every
session after it read «the last build opened fine» from the *previous* one and
looked for the fault in whatever it had added since. **Before blaming a change,
check that the thing it was added to was ever in the game.**

**`And(...)` in a GUI expression is eager**, which one of those runs proved
separately: build `feded5f` asked a CMM switch first in a `visible` and crashed
with it off. A `visible` cannot stop a sub-expression being evaluated, so a guard
is not a safety valve and must not be sold as one.

**`check_script.py` refuses a map nothing writes** — read from a `.gui` or from
inside a localization value, both, because a map read only from localization
would be missed by looking in the `.gui` alone.

**A window that says «a rule refused it, or there was nowhere» has said
nothing.** Those are two answers and the reader takes the first. An «or» in a
failure message is a message that has not been written yet — count the thing that
decides, and say which.

**One good to a row with its name beside it is half a window.** 35 goods came to
35 rows and he could not use it; the icon's tooltip already carries the name, so
the cell is «−1, icon, +1» and nothing else.

**A control you have to discover by clicking is a control that is not there.**
The editor's first working build showed bare icons; clicking one made «−1» and
«+1» appear on a row elsewhere, and he reported there was no way to edit anything
— true of everything he could see. The buttons went into the cells themselves.

**And when a press does nothing, say whether it arrived.** A button that never
reaches its effect and a rule that refuses look identical on screen; the editor
keeps `_edit_reached` beside `_edit_done` so the label can tell them apart. Both
of this window's earlier failures were diagnosed as the wrong one.

**`tools/check_script.py` resolves every name a window says** — a `text` or
`tooltip` key against the mod's own localization, a `Custom()` against
`customizable_localization/`, a `GetScriptedGui()` against `scripted_guis/`, a
datamodel's list against anything in `scripted_effects/` that writes it, and
english against russian because he plays in Russian. All five are tested by
breaking them on purpose. It is scoped to the prefix a majority of the mod's own
keys share, because a mod reuses vanilla keys freely and vanilla's localization
is not all in `reference/`.

**A window the engine is not told about is never created, and logs nothing at
all.** A `window = { name = "x" }` in a mod's `.gui` does not exist because the
file exists: it exists because a line in `in_game/gui/scripted_widgets/*.txt`
says `gui/<file>.gui = x`. Without that line the game parses the file, registers
its `types`, reports no error of any kind — and never builds the widget.

**The symptom is the worst one in this repository: everything works and nothing
happens.** 2026-09-03, two new windows shipped after a full session of work. The
button's effect logged that it ran. `error.log` had no line for the file,
`gui.log` had no type clash, the braces balanced, every localization key and
scripted GUI and script value it named resolved, and the owner pressed the button
three times to nothing. Two rounds went into the wrong question — whether some
widget type was unavailable — while the registry sat in the same folder, three
lines long, listing the three windows that did work.

**`tools/check_script.py` now refuses a window that no `scripted_widgets` line
names, and a line whose name does not match the window's own `name`** — the
engine looks the widget up by that name, so a typo there fails the same silent
way. Both halves are tested by breaking the registry on purpose.

**View objects only resolve inside their own panel.** Reading
`LocationProductionView.GetSelectedLocation` from a scripted widget returns null
and logs once per frame. Vanilla never reads a `*View` outside its own file;
elsewhere it only calls `Show<X>View(...)` to open one. If a probe has to watch a
panel, it has to live in that panel.

**Skins go on the widget, not in a `background` block.** `background = { using =
bg_paper_card }` does nothing at all; vanilla writes `using = bg_paper_card` on
the widget itself. Symptom: a window drawing its text straight onto the map.

**Copying a vanilla `.gui` brings its `types` block with it.** Construction
Manager and Glorp UI both restyle panels by redefining `types` from files of
their own, so a copy carrying vanilla's versions of those same types clobbers
them, load order deciding who loses. Copy the *window* and leave the types alone.

**Hidden rows still occupy their cell.** The list bodies are `fixedgridbox`es
with fixed row heights and no `ignoreinvisible`, so hiding a row from the
interface leaves a hole. Filter the data instead, or resize the list.

**A `widget` does not size itself to its child, so `layoutpolicy_vertical =
preferred` on one collapses whatever is inside it.** `where_to_produce`'s result
rows overlapped into a smear the moment a row grew a second line: the card is a
`widget` with `using = bg_paper_card`, and it was given a policy instead of a
height. A container that must grow with its content is a `vbox`; a `widget`
needs a number.

**A `block` nested inside a `blockoverride` never reaches the instance.** A
column type whose header was a plain `block` and whose rows were a `block` inside
the `blockoverride` of its scrollbox drew four headers and not one row.
`blockoverride` fills a block declared in the type it overrides; a block declared
*inside* an override of another type is not one of those. Vanilla only ever
nests a `blockoverride` in a `blockoverride`, never a `block`.

**An `icon` in an hbox takes a share of the row; a text icon takes its glyph.**
Two goods icons sat 77px apart at every size the container was given. The fix was
not another size but `text_single` with `raw_text = "[Goods.GetIcon]"`, which is
how vanilla writes goods into its own strings.

**An anchor on a direct child of an hbox or vbox is refused, and says so 124
times.** `gui.log`, not `error.log`: `Widget cannot have a position in a layout`,
one line per row drawn, from a `parentanchor = vcenter` on a button inside a row.
A layout places its own children; anchors belong to children of a plain
`widget`. Glorp UI has four of the same in `glorpUI_country_header.gui`.

**An hbox with a fixed width spreads its children across it.** Two goods icons
26px wide sat 77px apart inside an hbox told to be 144 wide. A container that
should hug its content gets no `size` at all — and where the column *must* have a
width, because it has to line up with a header, the width goes on a plain
`widget` and the content inside it gets `parentanchor = left|vcenter`. With one
child the spread reads as centring rather than as a gap: `where_to_produce`'s
«Из чего» sat half a column right of its heading for two runs, further on the
rows with fewer icons, and `ignoreinvisible` is what left it holding one child.

**A datamodel item needs a `datacontext` of its own, or the object it repeats
over is not there.** `where_to_produce`'s results row drew its goods icons off
`Scope.GetGoods` from inside the item's type and drew nothing at all — while the
count beside it, `GetDataModelSize` over the same list, was right, which is what
proved the list was fine and the item was not. Vanilla's shape, on every scope
list it repeats over: `datamodel = "[X.MakeScope.GetList('name')]"`, then
`item = { row_type = { datacontext = "[Scope.GetGoods]" } }`, then the object by
its type name inside the type — `GetGoodsIcon(Goods.Self)`, `Goods.GetName`.

**An hbox sizes itself to its children, so anything after a datamodel moves with
it.** A count printed before a row of icons sat a few pixels further right on
rows with one icon than on rows with two. Fixed positions inside a plain
`widget` are what hold a column still.

**`GetLocations` hands out lakes, sea zones and impassables.** A province's
locations are not all ground: `ProvinceDefinition.GetLocations` filled the
expanded rows with «Ничья земля». `Location.IsPossibleToOwn` is the interface's
filter and `is_ownable` — "not sea, lake or an impassable" — is script's.

**A `text_multi` with `autoresize` and no `maximumsize` does not wrap — it grows,
and `allow_outside` lets it drag the window apart.** `where_to_produce`'s results
window looked "broken at the top right": the frame ended where it should, and the
header, the rows and the scrollbar carried on past it over the game's own top
bar. The cause was one description line. `autoresize = yes` with no width bound
laid a long Russian sentence out on a single line about 1400px wide, the window
widget's `allow_outside = yes` let it draw outside the frame, and every row with
`layoutpolicy_horizontal = expanding` stretched to the new width. A `text_multi`
wraps only inside a `maximumsize`. Advanced Auto Build's windows have the same
defect from the same shape, which is where this mod copied it from.

**Vanilla pairs `parentanchor = center` with `widgetanchor = center`**, and every
centred window in the game does. With only the first, a window's top-left corner
is what lands in the middle of the screen.

**An expanding column does not line up between a header and a row.** It is as
wide as whatever is left, and a row inside a scrollbox has less left than a
header outside one — by the content margin and the scrollbar. Every column after
the expanding one then sits somewhere else in the two. Give the column a fixed
width and put the slack in a spacer at the far right.

**And then `layoutpolicy_horizontal = expanding` inside a sized hbox leaves the
child at zero width** — a text so sized elides to nothing at all, which reads
exactly like a variable that failed to print. `where_to_produce` lost the
building's name and its «×» that way and kept the `autoresize = yes` widget
beside it, which is what made it look like a scripting fault. Inside a parent
with a size of its own, size the children too.

---

**Шапка не отстаёт — рамка стоит на месте, а содержимое из неё вылезает.** Шесть
раз подряд это чинили как «шапка не растягивается», и правильное описание пришло
от владельца: «рамка всего окна вместе с шапкой не увеличивается, а содержимое и
"лист" внутри окна выходит за пределы рамки в правую сторону», 2026-09-06. Рамка,
фон и крестик — единственное, что остаётся при объявленном размере; всё остальное
`allow_outside` выпускает наружу. **Мерить, а не смотреть**: у окна редактора было
объявлено 1500 при ряде в 1544.

**И запас вычитается из коробки, а не прибавляется к ней.** `check_script.py` →
`overflowing_windows` разрешал ряду быть шире коробки на 60 «под поля», и именно
поэтому пропустил эти 1544. Поля и полоса прокрутки отнимают ширину у ряда, а не
добавляют её: ряду разрешено `ширина − запас`. Проверка, повёрнутая не в ту
сторону, — это шестой прогон, потраченный на уже измеренную вещь.

**Рамку окна рисует одна строка, и её отсутствие молчит.** `using =
bg_window_default_alt` на самом `window` — это и граница, и подложка шапки, и
лист; без неё окно открывается, работает и не имеет краёв вовсе. Три окна
потеряли её разом, когда скрипт перенёс её «на первую строку `size = {`» — а в
четырёх файлах из пяти типы объявлены выше `window`, и строка попала внутрь типа.
**`check_script.py` → `frameless_windows`** проверяет обе половины: каждое окно
её несёт, и ничто, кроме окна, её не несёт.

**Свободное окно — это `window` с `size` и `using = bg_window_default_alt` на нём
самом, и `vbox` внутри напрямую.** Лишний `widget` между ними держит свою ширину,
и шапка внутри него не тянется за окном: владелец сообщал об этом трижды, и две
попытки починить её свойствами самой шапки не дали ничего. **`window_header_alt`
не объявлен нигде в `reference/`** — читать, что держит его ширину, отсюда нечем.
**Зато `ai_settings_menu.gui` — свободное окно ровно этой формы**, и копия его
структуры отвечает на вопрос, на который свойство не отвечало.
**Когда тип не читается, читается окно игры, которое им пользуется.**

**Ячейка, написанная под номер, держит своё место даже невидимой.** Тринадцать
грамот в окне при девяти доступных вставали рваными столбцами: `ignoreinvisible`
убирает ребёнка из раскладки, но ряд из пяти ячеек, где видимы вторая и пятая,
всё равно ряд с дырами. Его слова, 2026-09-06: «мод должен сначала узнать какие
грамоты доступны, а потом загружать доступные в окна». **Ячейку писать под
*место*, а не под сущность**: `_rslot<p>` говорит, что на месте p, заполняется
подряд, и дыр не бывает вовсе. Имя, счётчик и кнопки попадают в свою сущность
через диспетчер.

## Окно, коробка и её содержимое

**Коробка окна — цифра, набранная руками, а содержимое растёт**, и `allow_outside`
выпускает наружу то, что не влезло, — на экране это читается как «плашка не
растягивается». **Ширину мерить, а не прикидывать**: `check_script.py` →
`overflowing_windows` делает это на каждой сборке. Правила целиком, с числами:
[`../archive/wtp_window_rules.md`](../archive/wtp_window_rules.md), расследование —
[`../archive/wtp_window_width.md`](../archive/wtp_window_width.md).

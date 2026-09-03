# Pitfalls — the interface

Split out of [`../PITFALLS.md`](../PITFALLS.md) when it outgrew its budget. Same
rule as the rest of that file: every entry here cost a round trip through the
game, and none of them raises an error you would notice.

Ask for one rather than reading the file: `python3 tools/kb.py <words>`.


**A control you have to discover by clicking is a control that is not there.**
The plan editor's first working build showed the goods as bare icons; clicking
one added a row elsewhere, and «−1» and «+1» appeared on that row. He opened the
window and reported there was no way to edit anything — «там только их иконки и
ничего больше, что могло бы дать мне инструмент влияния, никаких кнопочек +1 или
-1» — which was true of everything he could see. The buttons went into the picker
rows themselves and the second list was deleted.

**And when a press does nothing, say whether it arrived.** A button that never
reaches its effect and a rule that refuses look identical on screen. The editor
keeps `_edit_reached` beside `_edit_done` for exactly that: the label reads
«кнопка не донесла товар» when the scope never came through, and «правило не
дало» only when it did. Both of this window's earlier failures were diagnosed as
the wrong one of those.

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

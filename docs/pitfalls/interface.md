# Pitfalls — the interface

Split out of [`../PITFALLS.md`](../PITFALLS.md) when it outgrew its budget. Same
rule as the rest of that file: every entry here cost a round trip through the
game, and none of them raises an error you would notice.

Ask for one rather than reading the file: `python3 tools/kb.py <words>`.


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
should hug its content gets no `size` at all.

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

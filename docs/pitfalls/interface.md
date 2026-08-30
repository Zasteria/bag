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

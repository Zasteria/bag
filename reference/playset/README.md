# The rest of the playset

Empty until somebody runs the sync with `-Playset`. Then this holds a **text
only** copy of every mod the owner is subscribed to that is not one of the five
in `../mods/` — no textures, no sound, English and Russian localization and
nothing else:

```
.\tools\sync_workshop.ps1 -Playset
python3 tools/workshop.py playset          # the same, where Python is nearer
```

Every run rebuilds the picture: a mod he has unsubscribed from is removed, and
`../INVENTORY.md` lists what is left with the mounts each one declares.

## What it is for, and what it is not for

**For reading and measuring.** `tools/guicost.py` counts the interface cost of
everything here beside vanilla's, which is the only way that census stops being
a statement about five mods out of twenty-two. `tools/playset.py` reads the
mount table out of a `debug.log` and can then say which id is which.

**Not for building against.** `refs.mods()` does not see this folder, no
generator compiles from it, and nothing under `mods/` may depend on it — these
copies come and go with a subscription, and half of each mod is missing on
purpose. When a mod here turns out to matter, it graduates: add its workshop id
to `tools/workshop_mods.txt` and it starts arriving whole, in `../mods/`.

A session should not grep this tree by default. `../mods/` and `../game/`
answer nearly every question; this one answers questions about the playset.

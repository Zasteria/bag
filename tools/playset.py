#!/usr/bin/env python3
"""Which mods the player actually runs, read out of his own `debug.log`.

Twice now a session has reasoned about "the playset" from what happens to be in
`reference/`, and been wrong: `reference/` holds the five mods somebody thought
to upload, and the game loads twenty-two. The launcher's list is not in any log,
but the mount table is — the engine writes one
`virtualfilesystem_physfs.cpp: Mounted Data: .../workshop/content/3450310/<id>/<part>`
line per mod folder it mounts, in load order, every time it starts.

That gives three things nothing else does:

- **the real playset**, by workshop id, and how many of them there are;
- **load order**, which is mount order, so the last mod to mount wins a file;
- **what each mod can touch.** A mod that mounts only `main_menu` cannot add a
  widget to the running game — it is localization, a launcher entry, a menu. Only
  `in_game` mounts can add panels, filters or scripted widgets, and only
  `loading_screen` mounts can override a define.

So the interface census in `guicost.py` is honest only about the mods that are
also in `reference/`; this says how much of the playset that is.

    python3 tools/playset.py <path to debug.log>
    python3 tools/playset.py <path to a logs/ folder>

The log is the player's, so it does not live in this repository — point the tool
at wherever the last archive was unpacked.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import refs  # noqa: E402

# `.../steamapps/workshop/content/<appid>/<mod id>/<part>`
MOUNT = re.compile(r"workshop/content/\d+/(\d+)/(\w+)")
# The folder a mod arrives in is often named for its workshop id.
ID_IN_FOLDER = re.compile(r"(\d{6,})")


def find_log(target: Path) -> Path:
    if target.is_file():
        return target
    for candidate in ("debug.log", "logs/debug.log"):
        if (target / candidate).is_file():
            return target / candidate
    matches = sorted(target.rglob("debug.log"))
    if not matches:
        raise SystemExit("no debug.log under %s" % target)
    return matches[0]


def reference_by_id() -> dict[str, str]:
    """Workshop id -> folder name, for whatever is in `reference/mods/`."""
    out = {}
    for mod in refs.mods():
        found = ID_IN_FOLDER.search(mod.folder)
        if found:
            out[found.group(1)] = mod.id or mod.folder
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.strip().splitlines()[0])
        print("\nusage: python3 tools/playset.py <debug.log | logs folder>")
        return 2

    log = find_log(Path(argv[0]))
    order: list[str] = []
    parts: dict[str, set[str]] = {}
    with log.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            found = MOUNT.search(line)
            if not found:
                continue
            mod_id, part = found.groups()
            if mod_id not in parts:
                parts[mod_id] = set()
                order.append(mod_id)
            parts[mod_id].add(part)

    if not order:
        print("%s mounts no workshop content — this is a vanilla run." % log)
        return 0

    have = reference_by_id()
    print("%s\n%d mods, in load order. The last to mount wins a shared file.\n"
          % (log, len(order)))
    print("  %-3s %-12s %-32s %s" % ("#", "workshop id", "mounts", "in reference/"))
    for index, mod_id in enumerate(order, 1):
        print("  %-3d %-12s %-32s %s"
              % (index, mod_id, ",".join(sorted(parts[mod_id])),
                 have.get(mod_id, "—")))

    in_game = [m for m in order if "in_game" in parts[m]]
    defines = [m for m in order if "loading_screen" in parts[m]]
    missing = [m for m in in_game if m not in have]
    print("\n  %d of %d mods mount `in_game` — only those can add widgets,"
          % (len(in_game), len(order)))
    print("  filter chips or scripted widgets to the running game.")
    print("  %d mount `loading_screen`, so those can override a define." % len(defines))
    stray = [m.folder for m in refs.mods() if not ID_IN_FOLDER.search(m.folder)]
    if stray:
        print("\n  In `reference/` but not matchable to a mount, because the folder")
        print("  arrived without its workshop id — assume these are in the playset")
        print("  under one of the ids above rather than that they are absent:")
        for folder in stray:
            print("    %s" % folder)

    if missing:
        print("\n  at most %d of the %d are not in `reference/`, so `guicost.py` has"
              % (len(missing), len(in_game)))
        print("  never seen them, and a statement about \"the playset\" is that short:")
        print("    " + " ".join(missing))
        print("\n  To close the gap, copy these from")
        print("  steamapps/workshop/content/3450310/<id>/ into")
        print("  %s/." % refs.MODS.relative_to(refs.REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Is a mod ready to be uploaded to the workshop?

Nothing here talks to Steam. It checks the things that are wrong *before* the
upload and that the upload does not complain about — the launcher simply does
not list the mod, or the workshop page comes out blank, and the first anyone
knows is a subscriber saying it does nothing.

    python3 tools/publish.py                 every mod under mods/
    python3 tools/publish.py glorpui_hints   just that one, with the text to paste

What it knows that a person cannot check by looking:

* **the tag vocabulary is fixed.** A tag that is not one of the game's own is
  not an error, it is simply dropped, and the mod is then in no category on a
  hub where people browse by category. The list below was read off the EU5
  workshop hub's own filter sidebar on 2026-08-27, and it already caught four
  of this repository's mods filing themselves under "Localization", which is
  not a tag the game has — the tag for that is "Translation";
* **the thumbnail is the workshop page's picture**, not only the launcher's,
  and it has a size limit;
* **`version` has to parse.** The launcher reads x.y or x.y.z and a version it
  cannot read makes the mod look older than whatever a subscriber already has;
* **`id` has to be stable forever.** Change it after publishing and every
  subscriber has two mods, both mounted, fighting each other.

The upload itself is in [`docs/WORKSHOP.md`](../docs/WORKSHOP.md).
"""

from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import refs  # noqa: E402

# The EU5 workshop hub's own category filter, read from
# https://steamcommunity.com/app/3450310/workshop/ on 2026-08-27. Anything else
# is dropped on upload rather than rejected.
WORKSHOP_TAGS = {
    "Advancements", "Alternative History", "Balance", "Characters",
    "Culture & Art", "Diplomacy", "Events", "Fixes", "Flags", "Gameplay",
    "Government and Estates", "Historical", "International Organizations",
    "Loading Screen", "Map", "Military", "Missions", "Overhaul", "Religion",
    "Sound", "Textures", "Trade and Economics", "Translation", "User Interface",
    "Utilities",
}
# Mods in `reference/` also carry a game version as a tag — Community Mod
# Framework, Glorp UI and Construction Manager all tag "1.3". It is not in the
# category sidebar, so it is allowed here rather than required.
VERSION_TAG = re.compile(r"^\d+\.\d+$")

# What the launcher will read. `x.y` and `x.y.z` both parse; anything else does
# not, and a version that does not parse never looks newer.
VERSION = re.compile(r"^\d+\.\d+(\.\d+)?$")

REQUIRED = ("name", "id", "version", "game_id", "supported_game_version",
            "short_description", "tags")

# What the game mounts. Anything else in the folder is this repository's and is
# not uploaded — `tools/mods.py` copies only these into the game.
GAME_PARTS = {".metadata", "in_game", "main_menu", "loading_screen", "jomini",
              "gfx", "sound", "music"}

THUMBNAIL_LIMIT = 1_000_000     # the workshop's own ceiling
THUMBNAIL_SIZE = (512, 512)     # what Paradox recommends


def png_size(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    return struct.unpack(">II", data[16:24])


def check(folder: Path) -> list[str]:
    """Everything wrong with one mod folder, as sentences."""
    problems: list[str] = []
    metadata = folder / ".metadata/metadata.json"
    if not metadata.is_file():
        return ["нет .metadata/metadata.json — лаунчер такой мод не покажет"]
    try:
        data = json.loads(metadata.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return ["metadata.json не читается: %s" % exc]

    for field in REQUIRED:
        if not data.get(field):
            problems.append("в metadata.json нет %s" % field)
    if data.get("version") and not VERSION.match(str(data["version"])):
        problems.append("version = %r: лаунчер читает x.y или x.y.z, "
                        "и версию, которую он не прочитал, он не считает новее"
                        % data["version"])
    if data.get("id") and not re.match(r"^[a-z0-9._]+$", str(data["id"])):
        problems.append("id = %r: держи его коротким и латиницей, и никогда "
                        "не меняй после публикации — у подписчиков окажется "
                        "два мода сразу" % data["id"])
    for tag in data.get("tags", []):
        if tag in WORKSHOP_TAGS or VERSION_TAG.match(str(tag)):
            continue
        problems.append("тег %r мастерская не знает и молча выбросит "
                        "(её теги — в WORKSHOP_TAGS в tools/publish.py)" % tag)

    thumbnail = folder / ".metadata/thumbnail.png"
    if not thumbnail.is_file():
        problems.append("нет .metadata/thumbnail.png — это картинка страницы "
                        "в мастерской, а не только иконка в лаунчере")
    else:
        raw = thumbnail.read_bytes()
        size = png_size(raw)
        if size is None:
            problems.append("thumbnail.png — не PNG")
        elif size != THUMBNAIL_SIZE:
            problems.append("thumbnail.png %dx%d, Paradox советует %dx%d"
                            % (size + THUMBNAIL_SIZE))
        if len(raw) > THUMBNAIL_LIMIT:
            problems.append("thumbnail.png %d байт, потолок мастерской %d"
                            % (len(raw), THUMBNAIL_LIMIT))

    mounts = [p.name for p in folder.iterdir()
              if p.is_dir() and p.name in GAME_PARTS and p.name != ".metadata"]
    if not mounts:
        problems.append("в моде нет ни одной папки, которую игра монтирует "
                        "(%s)" % ", ".join(sorted(GAME_PARTS - {".metadata"})))

    for part in mounts:
        for path in (folder / part).rglob("*.yml"):
            if not path.read_bytes().startswith(b"\xef\xbb\xbf"):
                problems.append("%s без BOM — в игре будет каша вместо текста"
                                % path.relative_to(folder))
    return problems


def languages(folder: Path) -> list[str]:
    localization = folder / "main_menu/localization"
    if not localization.is_dir():
        return []
    return sorted(p.name for p in localization.iterdir() if p.is_dir())


def describe(folder: Path) -> None:
    """What to paste into the workshop page."""
    data = json.loads((folder / ".metadata/metadata.json").read_text(
        encoding="utf-8-sig"))
    print()
    print("  Название:  %s" % data.get("name", ""))
    print("  Теги:      %s" % ", ".join(data.get("tags", [])))
    print("  Версия:    %s   (для игры %s)"
          % (data.get("version"), data.get("supported_game_version")))
    print("  Языки:     %s" % (", ".join(languages(folder)) or "—"))
    for rel in ("workshop/description_english.bbcode",
                "workshop/description_russian.bbcode"):
        path = folder / rel
        if path.is_file():
            print("  Описание:  %s (%d символов)"
                  % (rel, len(path.read_text(encoding="utf-8"))))
        else:
            print("  Описание:  нет %s" % rel)
    dependencies = [r.get("display_name") or r.get("id")
                    for r in data.get("relationships", [])
                    if r.get("rel_type") == "dependency"]
    if dependencies:
        print("  Зависит:   %s" % ", ".join(dependencies))
        print("             их надо добавить на странице мода в мастерской "
              "вручную — «Add/Remove Required Items»")


def main(argv: list[str]) -> int:
    wanted = [a for a in argv[1:] if not a.startswith("-")]
    folders = sorted(p for p in (refs.REPO / "mods").iterdir() if p.is_dir())
    if wanted:
        folders = [p for p in folders if p.name in wanted]
        if not folders:
            print("нет такого мода: %s" % ", ".join(wanted), file=sys.stderr)
            return 2

    total = 0
    for folder in folders:
        problems = check(folder)
        total += len(problems)
        print("%-4s %s" % ("ok" if not problems else "!!", folder.name))
        for problem in problems:
            print("     %s" % problem)
        if len(folders) == 1:
            describe(folder)
    if len(folders) > 1:
        print()
        print("%d мод(ов): %s" % (len(folders),
                                  "всё готово" if not total
                                  else "%d замечаний" % total))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

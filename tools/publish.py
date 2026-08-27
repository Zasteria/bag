#!/usr/bin/env python3
"""Is a mod ready to be uploaded to the workshop?

Nothing here talks to Steam. It checks the things that are wrong *before* the
upload and that the upload does not complain about — the launcher simply does
not list the mod, or the workshop page comes out blank, and the first anyone
knows is a subscriber saying it does nothing.

    python3 tools/publish.py                 every mod under mods/
    python3 tools/publish.py glorpui_hints   just that one, with the text to paste
    python3 tools/publish.py glorpui_hints --config "<папка мода в игре>"
                                             write manager-config.json for the
                                             uploader, with the paths filled in

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
  subscriber has two mods, both mounted, fighting each other;
* **a workshop page takes a description per language**, and a language with no
  description falls back to the default one. So a mod shipping eleven languages
  wants eleven descriptions, and this reports which ones are missing.

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
# One description field per language on the workshop page, each with this
# ceiling. Steam does not refuse a longer one, it truncates it.
DESCRIPTION_LIMIT = 8000


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

    for path in sorted((folder / "workshop").glob("description_*.bbcode")):
        length = len(path.read_text(encoding="utf-8"))
        if length > DESCRIPTION_LIMIT:
            problems.append(
                "workshop/%s — %d символов, а поле описания держит %d. "
                "Steam не откажет, он обрежет." % (path.name, length,
                                                   DESCRIPTION_LIMIT))
    described = {path.stem[len("description_"):]
                 for path in (folder / "workshop").glob("description_*.bbcode")}
    for language in languages(folder):
        if described and language not in described:
            problems.append("мод есть на языке %s, а описания для него нет — "
                            "на странице подставится описание по умолчанию"
                            % language)

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
    files = sorted((folder / "workshop").glob("description_*.bbcode"))
    if files:
        print("  Описание:  workshop/, по файлу на язык — вставляй каждый в "
              "своё поле на странице:")
        for path in files:
            print("             %-34s %5d символов"
                  % (path.name, len(path.read_text(encoding="utf-8"))))
    else:
        print("  Описание:  нет ни одного workshop/description_*.bbcode")
    dependencies = [r.get("display_name") or r.get("id")
                    for r in data.get("relationships", [])
                    if r.get("rel_type") == "dependency"]
    if dependencies:
        print("  Зависит:   %s" % ", ".join(dependencies))
        print("             их надо добавить на странице мода в мастерской "
              "вручную — «Add/Remove Required Items»")


# EU5's Steam app id. Not the wiki's — its PDX Workshop Manager page says
# 529340, which is Imperator: Rome. 3450310 is what steamcmd downloads EU5
# workshop items with in tools/workshop.py, and what the game's own workshop
# content folder is named.
APP_ID = 3450310


def write_manager_config(folder: Path, installed: Path, out: Path) -> str:
    """A ready `manager-config.json` for kaiser-chris/pdx-workshop-manager.

    Three things in it are easy to get wrong by hand and are why this exists at
    all: the app id above; `thumbnail`, which the tool defaults to
    `thumbnail.png` in the mod root while every EU5 mod keeps it in
    `.metadata/`; and `directory`, which has to be the *installed* copy — the
    one the game mounts — rather than this repository, because the repository
    folder also holds `tools/` and `workshop/`, which are not the mod.

    **`id` is never overwritten.** After the first upload the tool writes the
    workshop id it was given back into this file, and that number is the only
    link between the mod and its page. So an existing config with a real id is
    left exactly as it is.
    """
    data = json.loads((folder / ".metadata/metadata.json").read_text(
        encoding="utf-8-sig"))
    if out.is_file():
        try:
            old = json.loads(out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old = {}
        for mod in old.get("mods", []):
            if mod.get("id"):
                return ("%s уже есть, и в нём workshop id %s — не трогаю. "
                        "Это единственная связь мода со своей страницей."
                        % (out, mod["id"]))

    descriptions = {
        path.stem[len("description_"):]: str(path.resolve())
        for path in sorted((folder / "workshop").glob("description_*.bbcode"))}

    config = {
        "game": APP_ID,
        "mods": [{
            "id": 0,
            "directory": str(installed),
            "thumbnail": ".metadata/thumbnail.png",
            "names": {"english": data.get("name", folder.name)},
            "descriptions": descriptions,
        }],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    return "написал %s — id 0 значит «мода в мастерской ещё нет, создай»" % out


def main(argv: list[str]) -> int:
    wanted = [a for a in argv[1:] if not a.startswith("-")]
    if "--config" in argv:
        installed = Path(argv[argv.index("--config") + 1])
        wanted = [a for a in wanted if a != str(installed)]
        if len(wanted) != 1:
            print("--config берёт ровно один мод", file=sys.stderr)
            return 2
        folder = refs.REPO / "mods" / wanted[0]
        print(write_manager_config(
            folder, installed, installed.parent / "manager-config.json"))
        return 0

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

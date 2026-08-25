#!/usr/bin/env python3
"""Pull the game files this repository needs out of an EU5 install.

`reference/game/` deliberately holds only part of EU5 — the parts the mods here
reason about. When a task needs more, the fix is to copy the missing
directories in, and doing that by hand means hunting through a hundred folders
and getting one of them wrong. This does it in one command, preserving the
layout `reference/game/` already uses, so the result can be dropped straight on
top of it.

    python3 tools/extract_game_files.py
    python3 tools/extract_game_files.py --game "D:/Steam/steamapps/common/Europa Universalis V"
    python3 tools/extract_game_files.py --out C:/Users/me/eu5_extract

Without `--game` it looks in the usual Steam locations for this platform. The
output is a folder shaped exactly like `reference/game/`; copy its contents over
`reference/game/` in a checkout, `git add`, and push.

Nothing is overwritten in place and nothing is deleted: the script only reads
the install and writes the output folder.

What it takes, and why, is the manifest below. Every entry names the tool that
wants it, so an entry with no reason left can be dropped. On top of the
manifest it sweeps `in_game/common/` for any file mentioning
`monthly_towards_`, which is how a directory that Paradox renames still comes
along — the sweep does not care what the folder is called.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

# Directory under the game root -> what needs it. Missing ones are reported,
# not fatal: Paradox renames folders, and the sweep below catches the important
# case anyway.
MANIFEST = {
    # mods/glorpui_hints — the axis list, without which nothing can be built
    "in_game/common/societal_values":
        "glorpui_hints: the 34 axis pairs",
    "in_game/common/modifier_type_definitions":
        "glorpui_hints: which modifiers are societal value changes",
    # mods/glorpui_hints — where the pushes come from
    "in_game/common/laws": "glorpui_hints: 442 pushes",
    "in_game/common/static_modifiers": "glorpui_hints: 298 pushes, the scaling ones",
    "in_game/common/government_reforms": "glorpui_hints: 235 pushes",
    "in_game/common/estate_privileges": "glorpui_hints: 150 pushes",
    "in_game/common/auto_modifiers": "glorpui_hints: 87 pushes",
    "in_game/common/religious_aspects": "glorpui_hints: 60 pushes, and their gates",
    "in_game/common/parliament_issues": "glorpui_hints: 24 pushes, and their gates",
    "in_game/common/employment_systems": "glorpui_hints: 9 pushes, mutually exclusive",
    "in_game/common/chivalric_orders": "glorpui_hints: 8 pushes, and their gates",
    "in_game/common/subject_types": "glorpui_hints: 6 pushes, and their gates",
    "in_game/common/international_organizations": "glorpui_hints: 5 pushes",
    "in_game/common/estates": "glorpui_hints: 5 pushes, and their gates",
    "in_game/common/cabinet_actions": "glorpui_hints: 5 pushes",
    "in_game/common/religious_schools": "glorpui_hints: 4 pushes, and their gates",
    "in_game/common/missions": "glorpui_hints: 4 pushes",
    "in_game/common/advances": "glorpui_hints: 2 pushes",
    "in_game/common/parliament_types": "glorpui_hints: 1 push",
    "in_game/common/traits": "glorpui_hints: scanned, currently not listed",
    "in_game/common/regencies": "glorpui_hints: scanned, currently not listed",
    "in_game/common/disasters": "glorpui_hints: scanned, currently not listed",
    "in_game/common/script_values":
        "glorpui_hints: societal_value_monthly_move and its siblings",
}

# Any file under here mentioning this comes along whatever its folder is called.
SWEEP_ROOT = "in_game/common"
SWEEP_MARKER = "monthly_towards_"

# Where the game usually is, per platform. First one that exists wins.
CANDIDATES = {
    "win32": [
        r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V",
        r"C:\Program Files\Steam\steamapps\common\Europa Universalis V",
        r"D:\Steam\steamapps\common\Europa Universalis V",
        r"D:\SteamLibrary\steamapps\common\Europa Universalis V",
        r"E:\SteamLibrary\steamapps\common\Europa Universalis V",
    ],
    "darwin": [
        "~/Library/Application Support/Steam/steamapps/common/Europa Universalis V",
    ],
    "linux": [
        "~/.steam/steam/steamapps/common/Europa Universalis V",
        "~/.local/share/Steam/steamapps/common/Europa Universalis V",
    ],
}

# The install root has the game files either at the top or one level down.
INSIDE = ("", "game")


def find_game(given: str | None) -> Path:
    """The folder that directly contains `in_game/`, or a failure that says why."""
    tried: list[Path] = []
    roots = [Path(given).expanduser()] if given else [
        Path(p).expanduser() for p in CANDIDATES.get(sys.platform, CANDIDATES["linux"])]
    for root in roots:
        for inside in INSIDE:
            candidate = root / inside if inside else root
            tried.append(candidate)
            if (candidate / "in_game").is_dir():
                return candidate
    print("no EU5 game files found. Looked for an `in_game/` folder in:",
          file=sys.stderr)
    for path in tried:
        print("  %s" % path, file=sys.stderr)
    print("\nPass the install folder explicitly:\n"
          "  python3 tools/extract_game_files.py --game \"<path to Europa Universalis V>\"",
          file=sys.stderr)
    raise SystemExit(2)


def copy_tree(source: Path, target: Path) -> tuple[int, int]:
    """Copy source over target, keeping layout. Returns (files, bytes)."""
    files = size = 0
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        destination = target / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        files += 1
        size += path.stat().st_size
    return files, size


def sweep(game: Path, out: Path, already: set[Path]) -> list[tuple[str, int]]:
    """Files under `in_game/common/` that mention the marker, folder be damned."""
    root = game / SWEEP_ROOT
    if not root.is_dir():
        return []
    found: dict[str, int] = {}
    for path in sorted(root.rglob("*.txt")):
        if not path.is_file() or path in already:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        if SWEEP_MARKER not in text:
            continue
        relative = path.relative_to(game)
        destination = out / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        folder = str(relative.parent).replace(os.sep, "/")
        found[folder] = found.get(folder, 0) + 1
    return sorted(found.items())


def human(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return "%.1f %s" % (size, unit) if unit != "B" else "%d B" % size
        size /= 1024.0
    return "%d B" % size


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Copy the game directories this repository needs into one "
                    "folder shaped like reference/game/.")
    parser.add_argument("--game", help="the Europa Universalis V install folder")
    parser.add_argument("--out", default="eu5_extract",
                        help="where to write it (default: ./eu5_extract)")
    parser.add_argument("--no-sweep", action="store_true",
                        help="skip the content sweep for renamed folders")
    args = parser.parse_args(argv[1:])

    game = find_game(args.game)
    out = Path(args.out).expanduser().resolve()
    print("game:   %s" % game)
    print("out:    %s" % out)
    print()

    if out.exists() and any(out.iterdir()):
        print("%s already has something in it. Delete it or pass a different "
              "--out; this script will not merge into it." % out, file=sys.stderr)
        return 2

    total_files = total_size = 0
    missing: list[str] = []
    copied: set[Path] = set()
    for relative, reason in MANIFEST.items():
        source = game / relative
        if not source.is_dir():
            missing.append("%-46s %s" % (relative, reason))
            continue
        files, size = copy_tree(source, out / relative)
        copied.update(p for p in source.rglob("*") if p.is_file())
        total_files += files
        total_size += size
        print("  %-46s %4d file%s %9s"
              % (relative, files, " " if files == 1 else "s", human(size)))

    if not args.no_sweep:
        extra = sweep(game, out, copied)
        if extra:
            print("\nalso, by content — files mentioning %r outside the list above:"
                  % SWEEP_MARKER)
            for folder, count in extra:
                print("  %-46s %4d file%s" % (folder, count, "" if count == 1 else "s"))
                total_files += count

    if missing:
        print("\nnot in this install, and skipped:")
        for line in missing:
            print("  %s" % line)
        print("\nA folder Paradox renamed is not a problem by itself — the "
              "content sweep above catches the ones that matter. A folder that "
              "matters and is missing from both is worth saying so.")

    print("\n%d files, %s." % (total_files, human(total_size)))
    print("\nNext: copy the *contents* of\n  %s\non top of `reference/game/` in "
          "a checkout of this repository, then\n"
          "  git add reference/game && git commit && git push" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

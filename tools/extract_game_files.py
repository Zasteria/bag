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
    python3 tools/extract_game_files.py --out /somewhere/else

There is a PowerShell twin, `tools/extract_game_files.ps1`, for the machine that
has the game on it. The two do the same thing; use whichever runs.

Without `--game` it looks in the usual Steam locations for this platform.
Without `--out` it writes straight into this repository's `reference/game/`,
which is where the files are wanted — so the next step is `git status`, not a
copy. Existing files are overwritten with the newer copy from the install, which
is the point of a refresh; nothing is deleted, and `git` is the undo.

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

# The list of directories lives in a file both this and the PowerShell twin
# read, so adding one adds it to both.
MANIFEST_FILE = Path(__file__).resolve().parent / "game_files_manifest.txt"


def manifest() -> dict[str, str]:
    """Directory under the game root -> what needs it."""
    wanted: dict[str, str] = {}
    for line in MANIFEST_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        path, _, reason = line.partition("#")
        wanted[path.strip()] = reason.strip()
    return wanted


# Any .txt under the whole install mentioning this comes along, whatever folder
# it is in. The sweep used to cover `in_game/common/` alone, which is where a
# mod's `common/` lives — but the game puts some of its own data elsewhere
# (`loading_screen/common/defines/` is the known case), and `static_modifiers`
# turned out to be one of those: 298 of the societal value pushes, absent from
# the first extraction and missed by a sweep that never left `in_game/`.
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


def elsewhere(game: Path, relative: str) -> Path | None:
    """The directory `relative` names, wherever in the install it actually is.

    Paradox moves a folder between mounts — `static_modifiers` is not under
    `in_game/` at all — so a manifest entry that misses at its written path gets
    one search by name before it is called missing.
    """
    name = relative.rsplit("/", 1)[-1]
    for candidate in sorted(game.rglob(name)):
        if candidate.is_dir():
            return candidate
    return None


def sweep(game: Path, out: Path, already: set[Path]) -> list[tuple[str, int]]:
    """Every .txt in the install that mentions the marker, folder be damned."""
    root = game
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
    parser.add_argument("--out", type=Path,
                        help="where to write it (default: this repository's "
                             "reference/game/)")
    parser.add_argument("--no-sweep", action="store_true",
                        help="skip the content sweep for renamed folders")
    args = parser.parse_args(argv[1:])

    game = find_game(args.game)
    out = (args.out.expanduser() if args.out
           else Path(__file__).resolve().parent.parent / "reference/game").resolve()
    print("game:   %s" % game)
    print("out:    %s" % out)
    print()

    total_files = total_size = 0
    missing: list[str] = []
    copied: set[Path] = set()
    for relative, reason in manifest().items():
        source = game / relative
        found_at = relative
        if not source.is_dir():
            moved = elsewhere(game, relative)
            if moved is None:
                missing.append("%-46s %s" % (relative, reason))
                continue
            source = moved
            found_at = str(moved.relative_to(game)).replace(os.sep, "/")
        files, size = copy_tree(source, out / found_at)
        copied.update(p for p in source.rglob("*") if p.is_file())
        total_files += files
        total_size += size
        note = "" if found_at == relative else "   <- found at %s" % found_at
        print("  %-46s %4d file%s %9s%s"
              % (relative, files, " " if files == 1 else "s", human(size), note))

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
    print("\nNext:\n  git status          # what the install brought\n"
          "  git add reference/game && git commit -m \"reference: game files\" "
          "&& git push")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

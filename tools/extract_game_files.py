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
    # **`utf-8-sig`, and a second guard after the split.** Read as plain
    # `utf-8` the first line keeps its BOM, so `lstrip().startswith("#")` is
    # false for the file's own header and it became an entry with an empty path
    # -- printed on 2026-09-03 at the top of "not in this install" as a blank
    # name and the header's own words as its reason. A path that is empty after
    # the split is a comment however it got here.
    for line in MANIFEST_FILE.read_text(encoding="utf-8-sig").splitlines():
        path, _, reason = line.partition("#")
        if not path.strip():
            continue
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

# Where under an install the mounts may sit. Tried in order, first hit wins.
INSIDE = ("", "game", "game/game")

# **What proves a folder is the one.** `in_game/` alone does not: on 2026-09-03
# it matched `…/Europa Universalis V/game`, and not one manifest entry was under
# it -- 0 files copied, every entry reported missing, and nothing in the output
# said what the folder actually held. A mount root has script data in it, so the
# landmark is a directory the repository already carries a copy of.
LANDMARKS = ("in_game/common/goods", "in_game/common/production_methods",
             "in_game/common/building_types")


def looks_like_root(path: Path) -> bool:
    return any((path / mark).is_dir() for mark in LANDMARKS)


def show_tree(path: Path, depth: int = 2, indent: str = "    ") -> None:
    """What is actually there, so a failure can be read rather than guessed at."""
    if not path.is_dir():
        print("%s%s — not a directory" % (indent, path), file=sys.stderr)
        return
    try:
        entries = sorted(path.iterdir())
    except OSError as problem:
        print("%s%s — %s" % (indent, path, problem), file=sys.stderr)
        return
    for entry in entries[:40]:
        mark = "/" if entry.is_dir() else ""
        print("%s%s%s" % (indent, entry.name, mark), file=sys.stderr)
        if entry.is_dir() and depth > 1:
            show_tree(entry, depth - 1, indent + "    ")
    if len(entries) > 40:
        print("%s… and %d more" % (indent, len(entries) - 40), file=sys.stderr)


def find_game(given: str | None) -> Path:
    """The folder the mounts sit in, or a failure that says what was there instead."""
    tried: list[Path] = []
    roots = [Path(given).expanduser()] if given else [
        Path(p).expanduser() for p in CANDIDATES.get(sys.platform, CANDIDATES["linux"])]
    fallback: Path | None = None
    for root in roots:
        for inside in INSIDE:
            candidate = root / inside if inside else root
            tried.append(candidate)
            if looks_like_root(candidate):
                return candidate
            if fallback is None and (candidate / "in_game").is_dir():
                fallback = candidate
    print("no EU5 script data found. A folder counts as the root when one of",
          file=sys.stderr)
    for mark in LANDMARKS:
        print("  %s" % mark, file=sys.stderr)
    print("is a directory inside it. Looked in:", file=sys.stderr)
    for path in tried:
        print("  %-70s %s" % (path, "exists" if path.is_dir() else "no"),
              file=sys.stderr)
    if fallback is not None:
        print("\n`%s` has an `in_game/` but none of the landmarks. What is in it:"
              % fallback, file=sys.stderr)
        show_tree(fallback)
    else:
        for root in roots:
            if root.is_dir():
                print("\n`%s` exists. What is in it:" % root, file=sys.stderr)
                show_tree(root, depth=1)
                break
    print("\nPaste that back, or pass the folder explicitly:\n"
          "  python3 tools/extract_game_files.py --game \"<path>\"",
          file=sys.stderr)
    raise SystemExit(2)


def copy_tree(source: Path, target: Path) -> tuple[int, int, int]:
    """Copy source over target, keeping layout. Returns (files, bytes, changed).

    **`changed` is the number that matters and it was not reported.** On
    2026-09-03 the extraction said «1098 files, 13.2 MB» and GitHub Desktop then
    said there was nothing to commit, which read like the commit failing. It had
    not: every one of those files was already in the repository, byte for byte.
    A copy is not a change, and a tool that counts copies cannot tell the two
    apart for him.
    """
    files = size = changed = 0
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        destination = target / path.relative_to(source)
        before = destination.read_bytes() if destination.is_file() else None
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        files += 1
        size += path.stat().st_size
        if before != path.read_bytes():
            changed += 1
    return files, size, changed


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

    total_files = total_size = total_changed = 0
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
        files, size, changed = copy_tree(source, out / found_at)
        copied.update(p for p in source.rglob("*") if p.is_file())
        total_files += files
        total_size += size
        total_changed += changed
        note = "" if found_at == relative else "   <- found at %s" % found_at
        if changed:
            note = ("   %d new or changed" % changed) + note
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

    print("\n%d files, %s — %d of them new or changed."
          % (total_files, human(total_size), total_changed))
    # **No git here.** He commits through GitHub Desktop and asked that nothing
    # in this repository's tooling write the working tree behind him.
    if total_changed:
        print("\nIn %s now. Commit it in GitHub Desktop — until it is committed "
              "and pushed, a session cannot see any of it." % out.name)
    else:
        print("\nNothing differs from what the repository already has, so there "
              "is nothing to commit. That is the answer, not a failure.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
"""Which build of each mod the game actually ran, read out of the player's `gui.log`.

Twice now a run has been read as a bug in a mod when the mod on disk was fine and
the folder the game loads held an older build. Nothing says so on screen, and
`error.log` cannot: a stale build is not an error, it is a different mod.

`gui.log` does say so, by accident. Every time one template overrides another the
engine writes the file **and the line** for both:

    Template 'SocietalValueCountryLeft_tooltip' at gui/svx_extra_societal_value_hints.gui:6
        overrides previous definition at gui/glorpUI_generated_societal_value_hints.gui:3

Line numbers are a fingerprint. Match them against the file in this tree, and
against every revision `git log` has of it, and the log names the build.

    python3 tools/which_build.py <path to gui.log>
    python3 tools/which_build.py <path to a logs/ folder>
    python3 tools/which_build.py <path> --all       every file, not just ours

The log is the player's, so it does not live in this repository — point the tool
at wherever the last archive was unpacked. Only templates that took part in an
override are logged, so a match is on the subset the log happens to name; that is
enough to separate two builds, and never enough to prove a file untouched
elsewhere.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# `Template 'X' at <file>:<line>`, and the `previous definition at <file>:<line>`
# that follows it on the same line.
TEMPLATE = re.compile(r"Template '(\w+)' at (\S+?\.gui):(\d+)")
PREVIOUS = re.compile(r"previous definition at (\S+?\.gui):(\d+)")
# A `template Foo {` at the start of a line, which is how every one of ours is written.
DECLARED = re.compile(r"^template\s+(\w+)\s*\{", re.MULTILINE)


def find_log(target: Path) -> Path:
    if target.is_file():
        return target
    for candidate in ("gui.log", "logs/gui.log"):
        if (target / candidate).is_file():
            return target / candidate
    matches = sorted(target.rglob("gui.log"))
    if not matches:
        raise SystemExit("no gui.log under %s" % target)
    return matches[0]


def observed(log: Path) -> dict[str, dict[str, int]]:
    """gui file (as the log spells it) -> {template: line} the engine reported."""
    seen: dict[str, dict[str, int]] = {}
    with log.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            found = TEMPLATE.search(line)
            if not found:
                continue
            name, path, number = found.groups()
            seen.setdefault(path, {})[name] = int(number)
            older = PREVIOUS.search(line)
            if older:
                path, number = older.groups()
                seen.setdefault(path, {})[name] = int(number)
    return seen


def declared(text: str) -> dict[str, int]:
    """{template: line} for a file's own text, counting from 1 as the engine does."""
    out: dict[str, int] = {}
    for found in DECLARED.finditer(text):
        out[found.group(1)] = text.count("\n", 0, found.start()) + 1
    return out


def agrees(fingerprint: dict[str, int], candidate: dict[str, int]) -> bool:
    """Every template the log named is where this text puts it."""
    return all(candidate.get(name) == line for name, line in fingerprint.items())


def candidates(logged: str) -> list[Path]:
    """Repository files a log path could be naming, ours first.

    A mod overrides a vanilla file by shipping it at the same virtual path, so one
    logged name can belong to the game, to a mod in `reference/`, or to a mod that
    is in neither — the playset is fifteen and `reference/` holds six.
    """
    name = Path(logged).name
    ours = sorted(ROOT.glob("mods/*/**/gui/**/" + name))
    theirs = sorted(ROOT.glob("reference/**/gui/**/" + name))
    return ours + theirs


def revisions(path: Path) -> list[tuple[str, str]]:
    """(short hash, date) for every commit that touched the file, newest first."""
    out = subprocess.run(
        ["git", "log", "--format=%h %ad", "--date=short", "--", str(path)],
        cwd=ROOT, capture_output=True, text=True)
    rows = []
    for line in out.stdout.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            rows.append((parts[0], parts[1]))
    return rows


def at_revision(commit: str, path: Path) -> str | None:
    out = subprocess.run(
        ["git", "show", "%s:%s" % (commit, path.relative_to(ROOT).as_posix())],
        cwd=ROOT, capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def verdict(logged: str, fingerprint: dict[str, int]) -> tuple[str, str]:
    """(state, sentence) for one logged gui file. State is `ours`, `ok` or `odd`."""
    for path in candidates(logged):
        where = path.relative_to(ROOT).as_posix()
        if agrees(fingerprint, declared(path.read_text(encoding="utf-8-sig"))):
            if where.startswith("mods/"):
                return "ours", "current — this tree's %s" % where
            return "ok", "matches %s" % where

    for path in candidates(logged):
        where = path.relative_to(ROOT).as_posix()
        if not where.startswith("mods/"):
            continue
        for commit, date in revisions(path):
            text = at_revision(commit, path)
            if text is not None and agrees(fingerprint, declared(text.lstrip("\ufeff"))):
                return "ours", ("STALE — the game ran %s (%s), not %s.\n"
                                "      Deploy it before reading anything else "
                                "into this run." % (commit, date, where))
        return "ours", ("matches no revision of %s this repository has — "
                        "a build made outside it" % where)

    return "odd", ("no file here has those templates at those lines — a mod "
                   "outside `reference/`, or a build we do not have")


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip().splitlines()[0])
        print("\nusage: python3 tools/which_build.py <gui.log | logs folder> [--all]")
        return 2

    everything = "--all" in argv
    log = find_log(Path([a for a in argv if not a.startswith("-")][0]))
    seen = observed(log)
    if not seen:
        print("%s names no template overrides — nothing to fingerprint." % log)
        return 0

    print("%s\n" % log)
    counts = {"ours": 0, "ok": 0, "odd": 0}
    stale = 0
    for logged in sorted(seen):
        state, sentence = verdict(logged, seen[logged])
        counts[state] += 1
        stale += "STALE" in sentence
        if state == "ours" or everything:
            print("  %s  (%d templates)\n      %s"
                  % (logged, len(seen[logged]), sentence))

    if not counts["ours"]:
        print("  none of this repository's own gui files took part in an override,\n"
              "  so this log cannot say which build of them ran.")
    if not everything:
        print("\n  %d other file(s) fingerprinted: %d match this tree, %d match "
              "nothing in it\n  (a mod outside `reference/`). `--all` lists them."
              % (counts["ok"] + counts["odd"], counts["ok"], counts["odd"]))
    if stale:
        print("\n  A run against a stale build tests the old bug, not the fix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

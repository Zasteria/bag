#!/usr/bin/env python3
"""The one command to run after `reference/` is refreshed.

The owner updates the game files and the workshop mods by hand, at no fixed
time and under whatever folder names the upload produced. Nothing in this
repository needs to be told about it — but the generated files do have to be
rebuilt, because they are compiled out of exactly those files, and it is worth
seeing *what* the update moved underneath the mods.

    python3 tools/refresh.py

It re-reads the inventory, runs every generator, and then reports which
generated files changed. A clean report means the update touched nothing this
repository depends on. A changed file is not a problem by itself — it is the
patch's effect, made visible, and `git diff` says what it was.

Add `--check` to leave nothing changed on disk and only report, which is what a
session should run before trusting anything a doc says about the tree.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import refs  # noqa: E402

# Every generator, in the order that makes the output read sensibly. Each takes
# its reference paths from `refs`, so none of them is given an argument here.
GENERATORS = (
    ("rgo_bonus_filter", "mods/rgo_bonus_filter/tools/generate_rgo_filter.py"),
    ("where_to_produce", "mods/where_to_produce/tools/generate.py"),
    ("auto_build_ru", "mods/auto_build_ru/tools/generate_ru.py"),
    ("nd_ru", "mods/nd_ru/tools/generate_ru.py"),
)


def run(script: str) -> tuple[int, str]:
    done = subprocess.run(
        [sys.executable, str(refs.REPO / script)],
        capture_output=True, text=True, cwd=refs.REPO,
    )
    return done.returncode, (done.stdout + done.stderr).strip()


def changed_files() -> list[str]:
    """What git sees as different, generated files and inventory alike."""
    done = subprocess.run(
        ["git", "status", "--porcelain", "--", "mods", "reference/INVENTORY.md"],
        capture_output=True, text=True, cwd=refs.REPO,
    )
    if done.returncode != 0:
        return []
    return [line[3:] for line in done.stdout.splitlines() if line.strip()]


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    before = set(changed_files())

    print("reference/")
    for mod in refs.mods():
        print("  %-40s %-34s %s" % (mod.folder, mod.id or "(no metadata)", mod.version or "—"))

    failed = []
    print()
    for name, script in GENERATORS:
        code, output = run(script)
        marker = "ok " if code == 0 else "FAIL"
        print("%s %s" % (marker, name))
        for line in output.splitlines():
            print("     %s" % line)
        if code != 0:
            failed.append(name)

    refs.INVENTORY.write_text(refs.table(), encoding="utf-8")

    after = [path for path in changed_files() if path not in before]
    print()
    if after:
        print("changed by this run (%d):" % len(after))
        for path in after:
            print("  %s" % path)
        print("`git diff` for what the update did; commit it with the reference refresh.")
    else:
        print("nothing changed: the refresh touched nothing this repository compiles from.")

    if check_only and after:
        subprocess.run(["git", "checkout", "--"] + after, cwd=refs.REPO)
        print("(--check: reverted)")

    if failed:
        print()
        print("FAILED: %s" % ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

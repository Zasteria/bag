#!/usr/bin/env python3
"""Check that the documents still describe the repository that exists.

Everything here is written down so a session with no memory can trust it. That
only works while it is true, and the ways it stops being true are dull and
repeatable: a mod is deleted and four documents still link to it, a folder in
`reference/` is renamed and the path in a code block is now wrong, a mod updates
and a version typed into prose quietly becomes a lie.

    python3 tools/check_docs.py

Each rule below exists because the mistake was actually made in this repository.
Two of them are hard failures — a path that does not exist, and a reference
folder named literally. Versions written in prose are only listed, because a
version is a lie when it claims what is in the tree and a fact when it records
what something was checked against, and no regular expression can tell those
apart.

A line carrying `check-docs: ignore` is skipped, for the case where a document
deliberately talks about something that is gone.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import refs  # noqa: E402

SKIP_DIRS = {".git", "reference", "__pycache__"}

# A repository path written in a document: a link target, or a bare path in
# backticks or a code block. No spaces — what follows a path is an argument or a
# description of it, and neither is part of the path.
PATHS = re.compile(r"(?:\]\(|`|^|\s)((?:mods|docs|tools|reference)/[\w./-]*[\w/])")
IGNORE = "check-docs: ignore"
# A version number sitting next to a mod's name, which `tools/refs.py` owns.
VERSIONS = re.compile(
    r"(?:CMF|Community Mod Framework|Construction Manager|Glorp UI|"
    r"National Destinies|Advanced Auto Build|community_mod_framework|glorp\.ui)"
    r"[^\n.]{0,30}?\b(\d+\.\d+\.\d+[\w.]*)"
)
# A folder inside reference/mods/ named literally. The name depends on how the
# owner's upload happened and has changed before; ask refs.py instead.
REFERENCE_FOLDER = re.compile(r"reference/mods/(?!\*)[\w.'-]+")


def documents() -> list[Path]:
    found = []
    for path in refs.REPO.rglob("*.md"):
        if not any(part in SKIP_DIRS for part in path.relative_to(refs.REPO).parts):
            found.append(path)
    return sorted(found)


def scripts() -> list[Path]:
    found = []
    for path in refs.REPO.rglob("*.py"):
        if not any(part in SKIP_DIRS for part in path.relative_to(refs.REPO).parts):
            found.append(path)
    return sorted(found)


def check_path(text: str, document: Path) -> bool:
    """Does this path exist — from the repository root, or from the document?

    A mod's own README writes `tools/generate_ru.py` meaning its own tools
    folder, which is right there on the page and wrong from the root.
    """
    if "*" in text or "<" in text:
        # `mods/*/tools/` and friends describe a shape rather than name a file.
        return True
    target = text.rstrip("/")
    return (refs.REPO / target).exists() or (document.parent / target).exists()


def main(argv: list[str]) -> int:
    problems: list[str] = []
    notes: list[str] = []

    for path in documents():
        where = path.relative_to(refs.REPO)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if IGNORE in line:
                continue
            for match in PATHS.finditer(line):
                target = match.group(1)
                if not check_path(target, path):
                    problems.append(f"{where}:{number}: no such path: {target}")
            for match in VERSIONS.finditer(line):
                notes.append(
                    "%s:%d: a version in prose (%s) — fine as a record of what was"
                    " checked, wrong as a claim about the tree"
                    % (where, number, match.group(1)))
            for match in REFERENCE_FOLDER.finditer(line):
                problems.append(
                    "%s:%d: names a folder inside reference/mods/ (%s) — the name"
                    " depends on the upload; ask refs.known()"
                    % (where, number, match.group(0)))

    # The same rule for the tools, where a hardcoded reference folder is worse:
    # it breaks silently rather than reading wrong.
    for path in scripts():
        if path.name == "check_docs.py":
            continue
        where = path.relative_to(refs.REPO)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("#") or IGNORE in line:
                continue
            for match in REFERENCE_FOLDER.finditer(line):
                problems.append(
                    "%s:%d: hardcodes %s — use refs.known(); a renamed folder"
                    " fails silently" % (where, number, match.group(0)))

    for problem in problems:
        print(problem, file=sys.stderr)
    if notes and "--quiet" not in argv:
        print("worth a look:")
        for note in notes:
            print("  %s" % note)
    print("%d documents, %d scripts: %s"
          % (len(documents()), len(scripts()),
             "%d problems" % len(problems) if problems else "clean"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

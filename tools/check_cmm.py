#!/usr/bin/env python3
"""Check that every CMM macro a mod calls exists and is called the way CMF declares it.

This is the check for the worst failure mode in this repository. A CMM macro
called with an argument name CMF does not declare **fails silently and takes the
rest of its effect with it** — one `step` where CMF declares `step_value` once
cost a full round trip through the game, and the symptom was an interface that
rendered perfectly and did nothing.

    python3 tools/check_cmm.py mods/<mod>/in_game/common

Reads every `cmm_*` call in that mod's `scripted_effects/` and `scripted_guis/`,
finds the same macro in CMF's own script (in `reference/`, resolved by mod id),
and reports any argument CMF does not declare. Silence means clean.

CMF moves its macros between files across versions — 2.4.1 split the list
settings into three — so declarations are read from whole folders and never from
a named file. Point `--cmf` at another copy of CMF to check against a version
that is not the one in `reference/`.

Written for `where_to_produce`, which was removed. It is kept here because the
mistake it catches belongs to CMM rather than to that mod, and the next mod
built on the Mod Menu will be able to make it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import refs  # noqa: E402

CALL = re.compile(r"(cmm_[a-z_]+) = \{([^{}]*)\}")
ARGUMENT = re.compile(r"\b(\w+)\s*=")
DECLARED_PLACEHOLDER = re.compile(r"\$(\w+)\$")

# Where a mod keeps script that may call CMM, relative to its in_game/common.
MOD_FOLDERS = ("scripted_effects", "scripted_guis")
# Where CMF declares its macros, relative to its in_game/common.
CMF_FOLDERS = ("scripted_effects", "scripted_guis")


def read_folders(root: Path, folders: tuple[str, ...]) -> str:
    text = []
    for folder in folders:
        for path in sorted((root / folder).glob("*.txt")):
            text.append(path.read_text(encoding="utf-8-sig"))
    return "".join(text)


def check(mod_common: Path, cmf_common: Path) -> list[str]:
    declared = read_folders(cmf_common, CMF_FOLDERS)
    if not declared.strip():
        raise SystemExit(f"no CMF script under {cmf_common}")
    ours = read_folders(mod_common, MOD_FOLDERS)

    problems = []
    for call in CALL.finditer(ours):
        name, body = call.group(1), call.group(2)
        block = re.search(r"^%s = \{(.*?)^\}" % re.escape(name), declared, re.S | re.M)
        if block is None:
            problems.append(f"unknown CMM effect: {name}")
            continue
        allowed = set(DECLARED_PLACEHOLDER.findall(block.group(1)))
        extra = set(ARGUMENT.findall(body)) - allowed
        if extra:
            problems.append("%s called with %s; CMF declares %s"
                            % (name, sorted(extra), sorted(allowed)))
    return problems


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2

    cmf = refs.known("cmf")
    if "--cmf" in argv:
        cmf = Path(argv[argv.index("--cmf") + 1])

    mod_common = Path(args[0])
    if not mod_common.is_dir():
        raise SystemExit(f"no such folder: {mod_common}")

    problems = check(mod_common, cmf / "in_game/common")
    for problem in problems:
        print(problem, file=sys.stderr)
    calls = len(set(CALL.findall(read_folders(mod_common, MOD_FOLDERS))))
    print("%d distinct CMM calls checked against %s: %s"
          % (calls, cmf.name, "%d problems" % len(problems) if problems else "clean"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
"""Two ways a mod file fails at load, both findable from here.

Every other checker in this tree answers a question about one mod's meaning.
This one answers a question about the file: the game read it and gave up, and
said so in `error.log` once per line while the session that wrote it saw nothing
at all. Both rules below cost a run on 2026-08-31, in one build, together.

**A trigger's conditional is `trigger_if`.** `if` is an *effect* — the engine's
own dump says so — and `else_if` is not in the dump at all. Written in a file
under `common/scripted_triggers/` they produce `Unknown trigger type: else_if`
once per line and a scripted trigger that comes back true no matter what, which
is the worst possible failure for a filter: it filters nothing and looks fine.
`where_to_produce`'s "only where it can be built today" was that, from the day
it was written.

**A file carries one byte order mark, at byte zero.** A second one is a
character in the text, and the interface parser answers
`'﻿' is not a valid widget/type/property` and then abandons the whole
file — every type in it missing, the window never found. Writing a string that
already begins with `﻿` through `encoding='utf-8-sig'` is how it happens,
and nothing about the file looks wrong afterwards.

    python3 tools/check_script.py                 every mod in mods/
    python3 tools/check_script.py mods/<mod>      one of them
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# `if`, `else` and `else_if` as a block key. Anything under `scripted_triggers/`
# is a trigger all the way down, so depth does not enter into it.
EFFECT_CONDITIONAL = re.compile(r'(?<![\w.])(if|else|else_if)\s*=\s*\{')

# Files the game parses. `.yml` is localization and carries a BOM too, but a
# doubled one there is a broken first key rather than a broken file, and
# `check_cmm.py` already reads those.
PARSED = ("*.txt", "*.gui")

# And only under a mount the game reads. A generator's fingerprint table and a
# translator's rewrite list are `.txt` in the same repository and are nobody's
# game files; asking them for a byte order mark is noise.
MOUNTS = ("in_game", "main_menu", "loading_screen")


def problems(root: Path) -> list[str]:
    found: list[str] = []
    for pattern in PARSED:
        for path in sorted(root.rglob(pattern)):
            if not path.is_file() or not set(path.parts) & set(MOUNTS):
                continue
            raw = path.read_bytes()
            where = path.relative_to(REPO)

            if not raw.startswith(b"\xef\xbb\xbf"):
                found.append(f"{where}: no byte order mark — "
                             f"the game reads the first key as part of it")
                text = raw.decode("utf-8", "replace")
            else:
                text = raw.decode("utf-8-sig")

            if "﻿" in text:
                line = text[:text.index("﻿")].count("\n") + 1
                found.append(f"{where}:{line}: a second byte order mark, in the "
                             f"text — the interface parser abandons the file "
                             f"and every type in it goes missing")

            if "scripted_triggers" not in path.parts:
                continue
            for match in EFFECT_CONDITIONAL.finditer(text):
                # A comment saying so is not a use of it.
                start = text.rfind("\n", 0, match.start()) + 1
                if "#" in text[start:match.start()]:
                    continue
                line = text[:match.start()].count("\n") + 1
                found.append(f"{where}:{line}: `{match.group(1)}` in a trigger — "
                             f"`if` is an effect and `else_if` is nothing; a "
                             f"trigger wants `trigger_{match.group(1)}`")
    return found


def main(argv: list[str]) -> int:
    roots = [Path(a) for a in argv[1:]] or sorted((REPO / "mods").iterdir())
    total = 0
    for root in roots:
        if not root.is_dir():
            continue
        found = problems(root if root.is_absolute() else REPO / root)
        total += len(found)
        for line in found:
            print(line)
    checked = ", ".join(r.name for r in roots if r.is_dir())
    print(f"{checked}: {'clean' if not total else f'{total} problem(s)'}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

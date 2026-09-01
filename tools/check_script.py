#!/usr/bin/env python3
"""Three ways a mod file fails at load, all findable from here.

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

**A name that nothing defines is not an error the game reports usefully.**
`bag_wtp_store_right_row_if_worth_it` called `bag_wtp_right_row_is_worth_it` and
the patch that was to have written that trigger died half way; the call stayed,
the definition never existed, and the `limit` it sat in passed for every
province. The symptom was a filter that filtered nothing — which is the same
symptom as the `trigger_if` rule above, and cost a run of its own. Every
`<name> = yes` in a mod's own `common/` has to resolve: to something the mod
defines, to something a mod in `reference/` defines (CMF's macros), or to an
effect or trigger in the engine's own dumps.

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

# `<name> = { ... }` at the top of a line is a definition; `<name> = yes` is a
# call. `yes` is also how a hundred ordinary keys are written -- `always = yes`,
# `is_ownable = yes` -- so a call only counts as unresolved when nothing in the
# game, in `reference/`, or in the mod itself defines it.
DEFINITION = re.compile(r'^(\w+)\s*=\s*\{', re.M)
CALL = re.compile(r'(?<![\w.:])(\w+)\s*=\s*yes\b')


def known_names() -> set[str]:
    """Everything a call may legitimately name, gathered once.

    The engine's own dumps carry `## <name>` per effect and trigger, which is
    where `always`, `is_ownable` and the rest come from; `reference/mods/` is
    where CMF's macros and every other mod's scripted effects live.
    """
    names: set[str] = set()
    for log in ("effects.log", "triggers.log"):
        path = REPO / "reference/game/docs" / log
        if path.is_file():
            names.update(line[3:].strip()
                         for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
                         if line.startswith("## "))
    for base in ((REPO / "reference/game/in_game/common"),
                 *(p / "in_game/common" for p in (REPO / "reference/mods").glob("*"))):
        if not base.is_dir():
            continue
        for path in base.rglob("*.txt"):
            names.update(DEFINITION.findall(path.read_text(encoding="utf-8-sig",
                                                           errors="replace")))
    return names


def unresolved(root: Path, known: set[str]) -> list[str]:
    """Calls in this mod's own `common/` that name nothing that exists."""
    defined: set[str] = set()
    sources: list[tuple[Path, str]] = []
    for path in sorted((root / "in_game/common").rglob("*.txt")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        defined.update(DEFINITION.findall(text))
        sources.append((path, text))
    if not defined:
        return []
    # Only names in this mod's own namespace: `always = yes` is the engine's and
    # a call into another mod is that mod's business.
    prefixes = tuple(sorted({n.split("_")[0] + "_" for n in defined}))
    found = []
    for path, text in sources:
        for match in CALL.finditer(text):
            name = match.group(1)
            if name in defined or name in known or not name.startswith(prefixes):
                continue
            line = text[:match.start()].count("\n") + 1
            found.append(f"{path.relative_to(REPO)}:{line}: `{name}` is called and "
                         f"nothing defines it — the block it sits in passes or "
                         f"does nothing, and the game says so nowhere useful")
    return found


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

            # **Braces, counted over the whole file, comments included.** Two
            # faults on 2026-09-01 that nothing here caught: a generator's
            # f-string nested one level too deep and shipped a literal `{{` into
            # every line of an effect, and a comment quoting `divide = {` left
            # the file one brace open. The engine ignores a brace in a comment
            # and chokes on the other, and neither says which file in
            # `error.log`, so both are cheaper to catch here.
            body = "\n".join(l.split("#", 1)[0] for l in text.splitlines())
            if "{{" in body or "}}" in body:
                token = "{{" if "{{" in body else "}}"
                line = body[:body.index(token)].count("\n") + 1
                found.append(f"{where}:{line}: `{token}` in script — a "
                             f"generator's f-string escaped one level too many, "
                             f"and the engine reads the whole block as one key")
            opened, closed = text.count("{"), text.count("}")
            if opened != closed:
                found.append(f"{where}: {opened} `{{` against {closed} `}}` — "
                             f"count them in the comments too; a stray brace in "
                             f"one is invisible to the engine and to a reader")

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
    known = known_names()
    total = 0
    for root in roots:
        if not root.is_dir():
            continue
        root = root if root.is_absolute() else REPO / root
        found = problems(root) + unresolved(root, known)
        total += len(found)
        for line in found:
            print(line)
    checked = ", ".join(r.name for r in roots if r.is_dir())
    print(f"{checked}: {'clean' if not total else f'{total} problem(s)'}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

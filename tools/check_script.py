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

import os
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
# A variable this mod writes, reads, or hands to CMF to write. **The game logs
# the fault this catches** -- «Variable 'X' is used but is never set» -- but only
# once the mod is loaded, and what it costs is a run: on 2026-09-01 a rename in
# `where_to_produce`'s generator caught `set_variable` for the plan window's own
# open flag along with the three it meant, and both plan buttons stopped opening
# anything. Nothing else in the mod said a word.
WRITTEN = (
    # **`remove_variable` is not a write.** A variable only ever removed and read
    # is precisely the fault: the rename that broke both plan buttons left the
    # window's flag with a reader, a remover, and nobody to set it.
    re.compile(r'(?:set|change)(?:_global)?_variable(?:_list)?\s*=\s*'
               r'\{\s*name\s*=\s*(\w+)'),
    re.compile(r'add_to(?:_global)?_variable_list\s*=\s*\{\s*name\s*=\s*(\w+)'),
    # CMF owns these: a setting alias and a list it builds are written by the
    # framework, and the mod only ever reads them back.
    re.compile(r'(?:alias|list_name)\s*=\s*(\w+)'),
)
BEING_READ = re.compile(
    r'(?:global_var|var):(\w+)'
    r'|has(?:_global)?_variable\s*=\s*(\w+)'
    r"|GetVariable\('(\w+)'\)"
    r'|is_target_in(?:_global)?_variable_list\s*=\s*\{\s*name\s*=\s*(\w+)'
    r'|(?<![\w])variable\s*=\s*(\w+)')

# A read the mod knows can never be written, with the reason beside it. Put on
# the line, the way `check_docs.py` takes `check-docs: ignore`.
IGNORE_READ = "check-script: never set"


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


def unwritten(root: Path) -> list[str]:
    """Variables this mod reads that nothing in it, and not CMF, ever writes.

    The game says this itself once loaded, so the only thing bought here is the
    run it would have cost. Scoped to the mod's own prefix: a variable belonging
    to the base game or to another mod is that mod's to set.
    """
    written: set[str] = set()
    ignored: set[str] = set()
    read: dict[str, tuple[Path, int]] = {}
    raw_lines: dict[Path, list[str]] = {}
    # `PARSED` holds globs, not suffixes -- matching a suffix against them reads
    # nothing at all and calls every mod clean, which is how this check first
    # shipped and passed.
    for path in sorted(root.rglob("*")):
        if not any(path.match(g) for g in PARSED) or not set(path.parts) & set(MOUNTS):
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        raw_lines[path] = text.splitlines()
        text = "\n".join(l.split("#", 1)[0] for l in text.splitlines())
        for pattern in WRITTEN:
            written.update(pattern.findall(text))
        for match in BEING_READ.finditer(text):
            name = next(g for g in match.groups() if g)
            line = text[:match.start()].count("\n") + 1
            if IGNORE_READ in raw_lines[path][line - 1]:
                ignored.add(name)
                continue
            read.setdefault(name, (path, line))
    # A mod's own namespace is the prefix its files are named for -- `bag_wtp`
    # from `bag_wtp_compute.txt`. Taken off the writes, so a mod that has not
    # settled on one is simply not checked rather than checked wrongly.
    prefixes = {n.rsplit("_", 1)[0] + "_" for n in written if n.count("_") >= 2}
    if not prefixes:
        return []
    found = []
    for name, (path, line) in sorted(read.items()):
        if name in written or name in ignored or not name.startswith(tuple(prefixes)):
            continue
        found.append(f"{path.relative_to(REPO)}:{line}: `{name}` is read and "
                     f"nothing sets it — the game logs this only once loaded, "
                     f"and finding out that way costs a run")
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


def unresolved_interface(root: Path) -> list[str]:
    """Every name a window says, checked against the thing that has to define it.

    Five kinds of name, and each one fails the same silent way -- the window
    draws, the cell is empty or the button does nothing, and no log says which:

    - a `text` or `tooltip` key with no localization behind it;
    - a `Custom('x')` with no `customizable_localization` of that name;
    - a `GetScriptedGui('x')` with no scripted GUI of that name;
    - a `GetList` / `GetGlobalList` nothing in `scripted_effects/` ever writes;
    - a key in one language and not the other -- the owner plays in Russian, so
      a key missing there shows on screen as the raw key.

    **This was done by hand three times in one day and caught something every
    time**, the last of them a `\\n` that stayed a backslash and glued two
    localization keys onto one line.
    """
    gui_dir = root / "in_game/gui"
    if not gui_dir.is_dir():
        return []

    def slurp(pattern: str) -> str:
        return "".join(path.read_text(encoding="utf-8-sig")
                       for path in sorted(root.glob(pattern)))

    languages: dict[str, set[str]] = {}
    for folder in sorted((root / "main_menu/localization").glob("*")):
        if not folder.is_dir():
            continue
        keys = set()
        for path in sorted(folder.glob("*.yml")):
            for line in path.read_text(encoding="utf-8-sig").split("\n"):
                match = re.match(r"\s+([A-Za-z0-9_]+):", line)
                if match:
                    keys.add(match.group(1))
        languages[folder.name] = keys
    if not languages:
        return []
    known = set().union(*languages.values())

    # **Only the keys this mod invents.** A mod reuses vanilla keys freely --
    # `rgo_bonus_filter` prints `game_concept_province`, `ru_loc_fix` is nothing
    # but vanilla keys -- and vanilla's own localization is not all in
    # `reference/`, so a name this file cannot find is usually the game's and
    # not a fault. The mod's own prefix is what its keys agree on: `bag_wtp_` for
    # `where_to_produce`. A mod whose keys agree on nothing is a mod that invents
    # none, and there is nothing here to check in it.
    # **The prefix most of the keys share, not the one all of them do.** The
    # common prefix of every key is empty the moment a mod defines one key that
    # does not fit -- `where_to_produce` has `mapmode_bag_wtp_*` beside its 345
    # `bag_wtp_*` -- and this returned nothing at all for it, which is the exact
    # failure this file exists to catch. So: the leading segment a majority of
    # the keys agree on, and no check at all when they agree on nothing.
    heads: dict[str, int] = {}
    for key in known:
        head = key.split("_")[0]
        heads[head] = heads.get(head, 0) + 1
    head, count = max(heads.items(), key=lambda pair: pair[1]) if heads else ("", 0)
    if len(head) < 2 or count * 2 < len(known):
        return []
    prefix = head + "_"
    mine = {key for key in known if key.startswith(prefix)}

    custom = set(re.findall(r"^(\w+) = \{",
                            slurp("in_game/common/customizable_localization/*.txt"), re.M))
    guis = set(re.findall(r"^(\w+) = \{",
                          slurp("in_game/common/scripted_guis/*.txt"), re.M))
    effects = slurp("in_game/common/scripted_effects/*.txt")

    found = []
    for path in sorted(gui_dir.glob("*.gui")):
        text = path.read_text(encoding="utf-8-sig")
        where = path.relative_to(REPO)
        for name in sorted(set(re.findall(
                r'(?:text|tooltip)\s*=\s*"([a-z][A-Za-z0-9_]*)"', text))):
            if name.startswith(prefix) and name not in mine:
                found.append(f"{where}: `{name}` on a widget, and no localization "
                             f"defines it — the key itself draws on screen")
        for name in sorted(set(re.findall(r"Custom\('(\w+)'\)", text))):
            if name not in custom:
                found.append(f"{where}: `Custom('{name}')`, and no "
                             f"customizable_localization of that name — the cell "
                             f"comes out empty")
        for name in sorted(set(re.findall(r"GetScriptedGui\('(\w+)'\)", text))):
            if name not in guis:
                found.append(f"{where}: `GetScriptedGui('{name}')`, and no "
                             f"scripted GUI of that name — the button does nothing")
        for name in sorted(set(re.findall(r"Get(?:Global)?List\('(\w+)'\)", text))):
            if name not in effects:
                found.append(f"{where}: the datamodel reads `{name}`, and nothing "
                             f"in scripted_effects/ ever writes it — the list is "
                             f"always empty")
    # **A global variable map nothing writes.** The interface reads one through
    # `GetVariableFromGlobalVariableMap('name', ...)`, in a `.gui` or inside a
    # localization value, and a name nothing ever writes returns an unset scope:
    # the number comes out blank and the `visible` that reads it is false for
    # ever. `bag_wtp_held` is read only from localization, so looking in the
    # `.gui` alone would have missed it.
    written_maps = set(re.findall(r"name = (\w+) key = ", effects))
    for where, text in ([(path.relative_to(REPO), path.read_text(encoding="utf-8-sig"))
                         for path in sorted(gui_dir.glob("*.gui"))]
                        + [(path.relative_to(REPO), path.read_text(encoding="utf-8-sig"))
                           for path in sorted((root / "main_menu/localization").glob("*/*.yml"))]):
        for name in sorted(set(re.findall(
                r"GetVariableFromGlobalVariableMap\('(\w+)'", text))):
            if name.startswith(prefix) and name not in written_maps:
                found.append(f"{where}: reads the variable map `{name}`, and "
                             f"nothing in scripted_effects/ ever writes it — the "
                             f"value comes back unset every time")

    # Custom localizations point at keys of their own.
    for name in sorted(set(re.findall(r"localization_key = (\S+)",
                                      slurp("in_game/common/customizable_localization/*.txt")))):
        if name.startswith(prefix) and name not in mine:
            found.append(f"{root.name}: a customizable_localization points at "
                         f"`{name}`, and no localization defines it")
    # **English against Russian, and no other pair.** He plays in Russian, and
    # `CLAUDE.md` says what that costs: a key missing there shows on screen as
    # the raw key. Every other language a mod ships is somebody else's promise --
    # `glorpui_hints` carries seven and translates into some of them partly, and
    # comparing all pairs turned that into 7 560 findings that are not faults.
    english, russian = languages.get("english"), languages.get("russian")
    if english and russian:
        for name in sorted((english - russian) & mine):
            found.append(f"{root.name}: `{name}` is in english and not in "
                         f"russian — a missing key draws as itself on screen, "
                         f"and he plays in Russian")
    return found


def unregistered_windows(root: Path) -> list[str]:
    """A `window` in a .gui that no `scripted_widgets` file names.

    **The game does not create a window because it is there.** It creates the
    ones a `gui/scripted_widgets/*.txt` line points at, `gui/<file>.gui = <name>`,
    and it says nothing at all about the rest: no parse error, no missing type,
    no line in `error.log` — the file simply is not asked for. That cost a whole
    round trip on 2026-09-03. Two new windows were written, checked, localized,
    wired to their buttons and shipped; the button's effect logged that it ran,
    the .gui had no error of any kind, and nothing appeared. The registry was in
    the same folder the whole time.

    The name in the registry has to match the window's own `name`, because that
    is what the engine looks the widget up by.
    """
    gui = root / "in_game/gui"
    if not gui.is_dir():
        return []
    registered: dict[str, str] = {}
    for path in sorted((gui / "scripted_widgets").glob("*.txt")):
        for line in path.read_text(encoding="utf-8-sig").split("\n"):
            line = line.split("#")[0].strip()
            if "=" not in line:
                continue
            where, name = (part.strip() for part in line.split("=", 1))
            registered[where] = name
    found = []
    for path in sorted(gui.glob("*.gui")):
        text = path.read_text(encoding="utf-8-sig")
        # A top-level `window = {` and its `name`. Only the first is asked for:
        # every window in this repository is one file, and a second in the same
        # file could not be registered separately anyway.
        if not re.search(r"^window = \{", text, re.M):
            continue
        match = re.search(r'^window = \{[^}]*?name = "([^"]+)"', text, re.M | re.S)
        name = match.group(1) if match else None
        key = f"gui/{path.name}"
        where = f"{path.relative_to(REPO)}"
        if key not in registered:
            found.append(f"{where}: a window nothing registers — add "
                         f"`{key} = {name or path.stem}` to "
                         f"in_game/gui/scripted_widgets/, or the game never "
                         f"creates it and says so nowhere")
        elif name and registered[key] != name:
            found.append(f"{where}: registered as `{registered[key]}` but the "
                         f"window is named `{name}` — the engine looks it up by "
                         f"the name and finds nothing")
    return found


def main(argv: list[str]) -> int:
    roots = [Path(a) for a in argv[1:]] or sorted((REPO / "mods").iterdir())
    known = known_names()
    total = 0
    for root in roots:
        if not root.is_dir():
            continue
        root = root if root.is_absolute() else REPO / root
        found = (problems(root) + unresolved(root, known) + unwritten(root)
                 + unregistered_windows(root) + unresolved_interface(root))
        total += len(found)
        for line in found:
            print(line)
    checked = ", ".join(r.name for r in roots if r.is_dir())
    print(f"{checked}: {'clean' if not total else f'{total} problem(s)'}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

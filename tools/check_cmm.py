#!/usr/bin/env python3
"""Check a mod's CMM calls: the arguments CMF declares, and the keys it will look for.

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

It also derives every localization key CMM will read — settings, tabs, groups,
list columns, list fields, and the prefix/postfix keys a formatted field needs —
and reports the ones no language defines. None of those raise anything in game:
CMF decides whether a key exists by comparing `Localize(key)` against the key
itself, so a missing one renders as its own name, in the middle of the
framework's own interface. `--args-only` skips that half.

Written for `where_to_produce`, which was removed, and grown by `goods_target`,
which printed `bgt__construction__target_prefix` in a column where a number
should have been. Both mistakes belong to CMM rather than to either mod.
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
ARG_PAIR = re.compile(r"(\w+)\s*=\s*([\w:]+)")
KEY_LINE = re.compile(r'^\s*([A-Za-z0-9_.]+):\s*"')

# What each format macro makes the widget look for, on top of _name and _desc.
FORMAT_SUFFIXES = {
    "cmm_set_list_field_format": ("_prefix", "_postfix"),
    "cmm_set_list_field_conditional_format": (
        "_prefix", "_postfix",
        "_prefix_high", "_postfix_high", "_prefix_low", "_postfix_low"),
}

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
        supplied = set(ARGUMENT.findall(body))
        extra = supplied - allowed
        if extra:
            problems.append("%s called with %s; CMF declares %s"
                            % (name, sorted(extra), sorted(allowed)))
        # The mirror image, and it fails the same way. A macro has no defaults:
        # an argument CMF declares and the call omits leaves `$name$` in the
        # pasted text, and the whole effect dies from there on. `where_to_produce`
        # lost every one of its lists to a missing `is_ordered` and showed a tab
        # with the settings that came after it in the same effect simply absent.
        missing = allowed - supplied
        if missing:
            problems.append("%s called without %s; CMF declares %s"
                            % (name, sorted(missing), sorted(allowed)))
    return problems


def required_keys(mod_common: Path) -> set[str]:
    """Every localization key CMM will look for, derived as CMM derives it."""
    text = read_folders(mod_common, MOD_FOLDERS)
    keys: set[str] = set()
    mods_seen: set[str] = set()

    for call in CALL.finditer(text):
        name, args = call.group(1), dict(ARG_PAIR.findall(call.group(2)))
        mod, setting = args.get("mod_id"), args.get("setting_id")
        if not mod or not setting:
            continue
        mods_seen.add(mod)

        if name in FORMAT_SUFFIXES:
            field = args.get("field_id")
            if field:
                keys |= {f"{mod}__{setting}__{field}{s}" for s in FORMAT_SUFFIXES[name]}
            continue
        if not name.startswith("cmm_register"):
            continue
        if "field_id" in args:
            keys.add(f"{mod}__{setting}__{args['field_id']}_name")
            continue
        if "settings_list" in name:
            # A list is its own group, so its header is keyed through the tab.
            if "tab_id" in args:
                keys.add(f"{mod}__{args['tab_id']}__{setting}_name")
            keys.add(f"{mod}__{setting}_item_column_name")
            continue
        keys.add(f"{mod}__{setting}_name")
        if "tab_id" in args:
            keys.add(f"{mod}__{args['tab_id']}_name")
            if "group_id" in args:
                keys.add(f"{mod}__{args['tab_id']}__{args['group_id']}_name")

    for mod in mods_seen:
        keys |= {f"{mod}_name", f"{mod}_desc"}
    return keys


def defined_keys(mod_root: Path) -> dict[str, set[str]]:
    """What each language of the mod actually defines."""
    found: dict[str, set[str]] = {}
    localization = mod_root / "main_menu/localization"
    if not localization.is_dir():
        return found
    for folder in sorted(p for p in localization.iterdir() if p.is_dir()):
        keys = set()
        for path in sorted(folder.glob("*.yml")):
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                match = KEY_LINE.match(line)
                if match:
                    keys.add(match.group(1))
        found[folder.name] = keys
    return found


def defined_elsewhere(keys: set[str], languages: set[str]) -> dict[str, set[str]]:
    """Which of `keys` the game or a reference mod already defines, per language.

    Only ever called about keys that are already known to be uneven across a
    mod's own languages, and only about those keys — so the common case, where
    nothing has drifted, reads nothing at all.
    """
    found: dict[str, set[str]] = {language: set() for language in languages}
    roots = [refs.GAME] + [mod.path for mod in refs.mods()]
    for root in roots:
        for language in languages:
            folder = root / "main_menu/localization" / language
            if not folder.is_dir():
                continue
            for path in folder.rglob("*.yml"):
                for line in path.read_text(encoding="utf-8-sig",
                                           errors="replace").splitlines():
                    match = KEY_LINE.match(line)
                    if match and match.group(1) in keys:
                        found[language].add(match.group(1))
    return found


def check_localization(mod_common: Path) -> list[str]:
    """Missing keys, and languages that have drifted apart."""
    mod_root = mod_common.parent.parent
    defined = defined_keys(mod_root)
    if not defined:
        return ["no localization folders under %s" % (mod_root / "main_menu/localization")]

    wanted = required_keys(mod_common)
    problems = []
    for language, keys in defined.items():
        for key in sorted(wanted - keys):
            problems.append(f"{language}: no localization for {key}")

    # A key one language defines and another does not usually means somebody
    # forgot, and it shows on screen as the raw key. But a mod may also override
    # *another* mod's key in one language and leave the rest alone - repairing
    # broken grammar in one language is exactly that, and copying the other ten
    # in unchanged would only pin text that is fine. So the drift is reported
    # only where nothing else defines the key either.
    first, *rest = sorted(defined)
    drifted = set()
    for language in rest:
        drifted |= defined[first] ^ defined[language]
    covered = defined_elsewhere(drifted, set(defined)) if drifted else {}
    for language in rest:
        for key in sorted(defined[first] ^ defined[language]):
            short = first if key not in defined[first] else language
            if key in covered.get(short, ()):
                continue
            problems.append(f"{key} is in {first} or {language} but not both")
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
    if "--args-only" not in argv:
        problems += check_localization(mod_common)
    for problem in problems:
        print(problem, file=sys.stderr)
    calls = len(set(CALL.findall(read_folders(mod_common, MOD_FOLDERS))))
    print("%d distinct CMM calls checked against %s: %s"
          % (calls, cmf.name, "%d problems" % len(problems) if problems else "clean"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

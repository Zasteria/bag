#!/usr/bin/env python3
"""Rebuild `glorpui_hints` from Glorp UI, and refuse to write it broken.

Two things live in this mod and only one of them can be rebuilt from what
`reference/` holds:

* **The Russian hint text** is Glorp UI's own English file with three verb
  phrases replaced, so it is regenerated here on every run — a Glorp UI update
  that adds hints is picked up without anyone noticing it happened.
* **The extra hint lists** are compiled out of the *game's* `common/` tree —
  laws, static modifiers, religious aspects, employment systems and the rest —
  and almost none of that is in `reference/`. They are committed as generated
  files and rebuilt only when the game files are handed over:

      python3 mods/glorpui_hints/tools/generate.py --game-files <unpacked game>

What runs unconditionally is the part that catches the update this mod is most
likely to be broken by. The mod **overrides Glorp UI's own override** of
`SocietalValueCountryLeft_tooltip` / `SocietalValueCountryRight_tooltip`, and it
re-emits Glorp UI's list inside it. If Glorp UI restructures those templates,
nothing errors at load: the player simply gets our older copy of Glorp UI's list
and never sees whatever Glorp UI added. So the checks below compare the two
files every run and fail naming the difference.

    python3 mods/glorpui_hints/tools/generate.py
    python3 mods/glorpui_hints/tools/generate.py --check    # write nothing
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
MOD = TOOLS.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(MOD.parent.parent / "tools"))

import refs  # noqa: E402
import translate_hints  # noqa: E402

RU_HINTS = MOD / "main_menu/localization/russian" / translate_hints.OUTPUT_NAME
EXTRA_LOC = MOD / "main_menu/localization/russian/svx_extra_hints_l_russian.yml"
EXTRA_GUI = MOD / "in_game/gui/svx_extra_societal_value_hints.gui"
EXTRA_CUSTOM = MOD / "in_game/common/customizable_localization/svx_extra_hint_loc.txt"
EXTRA_VALUES = MOD / "in_game/common/script_values/svx_extra_hint_script_values.txt"

GLORP_HINTS_GUI = "in_game/gui/glorpUI_generated_societal_value_hints.gui"
GLORP_HINTS_VALUES = (
    "in_game/common/script_values/glorpui_generated_societal_value_hint_script_values.txt")
GLORP_HINTS_EN = ("main_menu/localization/english/"
                  + translate_hints.SOURCE_NAME)

# One TooltipScrolledStringPairList, reduced to what it actually does: which
# script value gates it, what title it carries, which body key it prints.
ENTRY_RE = re.compile(
    r"ScriptValue\('(?P<value>\w+)'\).*?"
    r'text = "(?P<title>[A-Z_]+)".*?'
    r"Localize\('(?P<body>\w+)'\)",
    re.S)
TEMPLATE_RE = re.compile(r"^template (\w+) \{", re.M)
LOC_KEY_RE = re.compile(r"^ (\w+):", re.M)
CUSTOM_RE = re.compile(r"^(\w+) = \{$", re.M)
SCRIPT_VALUE_RE = re.compile(r"^(\w+) = \{$", re.M)
PLAYER_CUSTOM_RE = re.compile(r"\[Player\.Custom\('(\w+)'\)\]")


def entries(text: str) -> list[tuple[str, str, str, str]]:
    """(template, gating script value, title key, body key), in file order."""
    found = []
    for match in ENTRY_RE.finditer(text):
        template = "?"
        for candidate in TEMPLATE_RE.finditer(text[:match.start()]):
            template = candidate.group(1)
        found.append((template, match.group("value"),
                      match.group("title"), match.group("body")))
    return found


def check_glorp_list_is_current(problems: list[str], glorp: Path) -> None:
    """Our re-emission of Glorp UI's list must still be Glorp UI's list.

    Compared as an ordered sequence rather than as text: the mod interleaves two
    lists of its own between Glorp UI's entries, so the file cannot match, but
    Glorp UI's entries must appear in the same order and say the same thing.
    """
    theirs = entries((glorp / GLORP_HINTS_GUI).read_text(encoding="utf-8-sig"))
    ours = [entry for entry in entries(EXTRA_GUI.read_text(encoding="utf-8-sig"))
            if entry[1].startswith("glorpui_svh_visible_")]
    if ours == theirs:
        return
    theirs_set, ours_set = set(theirs), set(ours)
    for entry in theirs:
        if entry not in ours_set:
            problems.append(
                "Glorp UI now lists %s (%s) in %s and this mod does not — "
                "rebuild with --game-files" % (entry[3], entry[1], entry[0]))
    for entry in ours:
        if entry not in theirs_set:
            problems.append(
                "this mod re-emits %s (%s) in %s and Glorp UI no longer does"
                % (entry[3], entry[1], entry[0]))
    if not problems:
        problems.append("Glorp UI's hint entries are the same but in a "
                        "different order — rebuild with --game-files")


def check_references_resolve(problems: list[str], glorp: Path, ru_hints: str) -> None:
    """Every name the `.gui` reaches for is defined by us or by Glorp UI.

    A `.gui` asking for a script value or a loc key that nothing defines does not
    fail to load; it prints zero, or the raw key, which is exactly the fault this
    mod exists to repair.
    """
    gui = EXTRA_GUI.read_text(encoding="utf-8-sig")
    defined_values = set(SCRIPT_VALUE_RE.findall(
        EXTRA_VALUES.read_text(encoding="utf-8-sig")))
    defined_values |= set(SCRIPT_VALUE_RE.findall(
        (glorp / GLORP_HINTS_VALUES).read_text(encoding="utf-8-sig")))
    defined_keys = set(LOC_KEY_RE.findall(EXTRA_LOC.read_text(encoding="utf-8-sig")))
    defined_keys |= set(LOC_KEY_RE.findall(ru_hints))

    for _, value, _, body in entries(gui):
        if value not in defined_values:
            problems.append("%s: no script value %s" % (EXTRA_GUI.name, value))
        if body not in defined_keys:
            problems.append("%s: no localization key %s" % (EXTRA_GUI.name, body))
    for title in {entry[2] for entry in entries(gui)}:
        # The two titles this mod adds are its own; the vanilla ones are not.
        if title.startswith("SVX_") and title not in defined_keys:
            problems.append("%s: no localization key %s" % (EXTRA_GUI.name, title))

    # And every gated line the localization prints has a rule behind it.
    loc = EXTRA_LOC.read_text(encoding="utf-8-sig")
    declared = set(CUSTOM_RE.findall(EXTRA_CUSTOM.read_text(encoding="utf-8-sig")))
    used = set(PLAYER_CUSTOM_RE.findall(loc))
    for name in sorted(used - declared):
        problems.append("%s: no customizable localization %s"
                        % (EXTRA_LOC.name, name))
    for name in sorted(declared - used):
        problems.append("%s: %s is declared and never printed"
                        % (EXTRA_CUSTOM.name, name))
    for key in sorted({m.group(1) for m in re.finditer(
            r"localization_key = (\w+)",
            EXTRA_CUSTOM.read_text(encoding="utf-8-sig"))}):
        if key != "empty_text" and key not in defined_keys:
            problems.append("%s: no localization key %s" % (EXTRA_CUSTOM.name, key))


def check_localization_conventions(problems: list[str], ru_hints: str) -> None:
    """A BOM, one leading space per key, and brackets that close.

    All three are silent in game: a file with no BOM is read as some other
    encoding and its Russian arrives as mojibake, a key without its leading
    space is not a key at all, and an unbalanced bracket renders as `ERROR:`.
    """
    for name, text in ((RU_HINTS.name, ru_hints),
                       (EXTRA_LOC.name, EXTRA_LOC.read_text(encoding="utf-8-sig"))):
        raw = (RU_HINTS if name == RU_HINTS.name else EXTRA_LOC).read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            problems.append("%s: no UTF-8 BOM" % name)
        header = [line for line in text.splitlines() if line.strip().startswith("l_")]
        if header != ["l_russian:"]:
            problems.append("%s: header is %r, want ['l_russian:']" % (name, header))
        for number, line in enumerate(text.splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#") or line.strip() == "l_russian:":
                continue
            if not re.match(r'^ \w+: ".*"$', line):
                problems.append("%s:%d: not ` KEY: \"value\"`" % (name, number))
                continue
            value = line.split(":", 1)[1]
            if value.count("[") != value.count("]"):
                problems.append("%s:%d: brackets do not balance" % (name, number))


def known_triggers() -> set[str]:
    """Every name a trigger clause may legitimately start with.

    Three sources, and all three are needed:

    * the engine's own dump, which is the authority on named triggers;
    * the game's `scripted_triggers/`, for things like
      `game_has_missions_enabled` that the dump does not know about;
    * **every name the game itself writes in the same position** anywhere in
      its `common/` tree. Not everything valid is a named trigger:
      `religion = religion:catholic` and `culture = culture:low_frankish` are
      scope comparisons, appear in the dump nowhere, and are written 598 and
      1 418 times by the game. Without this third source the check reports them
      and gets ignored, which is worse than not checking.

    What survives all three is a name nothing in the game has ever written —
    which is what `country_religion` was, in 492 gates.
    """
    names = set(re.findall(
        r"^## (\w+)", (refs.GAME / "docs/triggers.log").read_text(
            encoding="utf-8", errors="replace"), re.M))
    scripted = refs.GAME_COMMON / "scripted_triggers"
    if scripted.is_dir():
        for path in scripted.glob("*.txt"):
            names |= set(re.findall(r"^(\w+)\s*=\s*\{", path.read_text(
                encoding="utf-8-sig", errors="replace"), re.M))
    for path in refs.GAME_COMMON.rglob("*.txt"):
        names |= set(TRIGGER_CALL.findall(path.read_text(
            encoding="utf-8-sig", errors="replace")))
    return names


# A `name = ` at the start of a trigger clause. Values, targets and the right
# hand side of a comparison are not names being called.
TRIGGER_CALL = re.compile(r"(?:^|[{\s])([a-z_][a-z_0-9]*)\s*(?:=|<|>|<=|>=)")
# Logic and control words, which are the engine's own and not in the dump.
TRIGGER_KEYWORDS = {
    "and", "or", "not", "nor", "nand", "if", "else", "else_if", "limit",
    "trigger_if", "trigger_else", "trigger_else_if", "custom_tooltip",
    "custom_description", "hidden_trigger", "value", "add", "subtract",
    "multiply", "divide", "min", "max", "desc", "type", "text",
    "localization_key", "trigger", "scale", "count", "percent", "amount",
}


def trigger_blocks(text: str) -> str:
    """Just the insides of every `trigger = { ... }`, joined.

    The rest of the file is definition names and `localization_key = X`, and
    reading those as trigger calls reports every gate in the mod as unknown.
    """
    out = []
    for match in re.finditer(r"\btrigger\s*=\s*\{", text):
        depth = 0
        for index in range(match.end() - 1, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    out.append(text[match.end():index])
                    break
    return "\n".join(out)


def check_triggers_exist(problems: list[str]) -> None:
    """Every trigger the gates call is one the engine or the game defines.

    A mistyped trigger name is a load error, not a quiet nothing — but it is a
    load error in the *player's* game, found by them, a round trip away. The
    names come out of the shipped files and the engine's own dump, so checking
    them costs nothing and closes the one way this file can be wrong by a
    keystroke.
    """
    known = known_triggers()
    if not known:
        problems.append("no triggers.log in reference/ — cannot check trigger names")
        return
    seen: dict[str, int] = {}
    for name in TRIGGER_CALL.findall(trigger_blocks(EXTRA_CUSTOM.read_text(
            encoding="utf-8-sig"))):
        if name in TRIGGER_KEYWORDS or name in known:
            continue
        seen[name] = seen.get(name, 0) + 1
    for name, count in sorted(seen.items()):
        problems.append("%s: no trigger named %s (%d call%s)"
                        % (EXTRA_CUSTOM.name, name, count, "" if count == 1 else "s"))


def rebuild_extra(game_files: Path) -> int:
    """Re-scan the game and rewrite the three generated files."""
    findings = MOD.parent.parent / "sv_findings.json"
    for command in (
            [sys.executable, str(TOOLS / "scan_sources.py"), str(game_files),
             "--json", str(findings)],
            [sys.executable, str(TOOLS / "generate_extra.py"),
             "--findings", str(findings), "--game-files", str(game_files),
             "--out", str(MOD)]):
        done = subprocess.run(command, capture_output=True, text=True)
        for line in (done.stdout + done.stderr).strip().splitlines():
            print("     %s" % line)
        if done.returncode != 0:
            return done.returncode
    findings.unlink(missing_ok=True)
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-files", type=Path,
                        help="unpacked EU5 game files, to rebuild the extra "
                             "hint lists; without it they are only checked")
    parser.add_argument("--check", action="store_true",
                        help="report, write nothing")
    args = parser.parse_args(argv[1:])

    glorp = refs.known("glorp_ui")

    if args.game_files:
        code = rebuild_extra(args.game_files)
        if code:
            return code

    try:
        text, translated, bodies = translate_hints.render(glorp / GLORP_HINTS_EN)
    except translate_hints.Unrecognised as exc:
        print("Glorp UI writes a hint this mod cannot translate. Add the shape to "
              "TEMPLATES in translate_hints.py:\n  %s" % exc, file=sys.stderr)
        return 1
    if not args.check:
        RU_HINTS.parent.mkdir(parents=True, exist_ok=True)
        RU_HINTS.write_text(text, encoding="utf-8-sig", newline="\n")
        print("wrote %s" % RU_HINTS.relative_to(refs.REPO))
    print("%d hints translated, %d body keys copied from Glorp UI"
          % (translated, bodies))

    problems: list[str] = []
    check_glorp_list_is_current(problems, glorp)
    check_references_resolve(problems, glorp, text)
    check_localization_conventions(problems, text)
    check_triggers_exist(problems)
    if problems:
        print()
        for problem in problems:
            print("     %s" % problem, file=sys.stderr)
        return 1

    gui_entries = entries(EXTRA_GUI.read_text(encoding="utf-8-sig"))
    gated = len(CUSTOM_RE.findall(EXTRA_CUSTOM.read_text(encoding="utf-8-sig")))
    print("%d tooltip lists over 34 directions, %d of them Glorp UI's own"
          % (len(gui_entries),
             sum(1 for e in gui_entries if e[1].startswith("glorpui_svh_visible_"))))
    print("%d hint lines gated by a country trigger" % gated)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
"""Generate the "extra societal value hints" add-on mod for Glorp UI.

Glorp UI's generated hints cover three source types - government reforms,
laws/policies and estate privileges. The game pushes societal values from far
more than that: employment systems, buildings, religious aspects, parliament
issues, cabinet actions, and modifiers that are either scaled by some country
state (fort maintenance, army size, average control) or switched on by a
condition (bankruptcy, being at war, exceeding the fort limit).

Entries whose availability can be checked with a trigger form that appears
verbatim in the shipped game files are wrapped in customizable localization, so
hints for other religions, estates or subject types drop out. The rest are
emitted as plain text - see mods/glorpui_hints/tools/gates.py for why nothing is guessed.

Inputs:
  - the scan produced by mods/glorpui_hints/tools/scan_sources.py
  - the extracted game files, for axis pairs and availability blocks

Usage:
    python3 mods/glorpui_hints/tools/generate_extra.py \
        --findings sv_findings.json --game-files <game-files> --out glorpui_svh_extra
"""

import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gates as svx_gates

# Source types the add-on lists, with the Russian noun that introduces them.
# Reforms, laws and estate privileges are omitted - Glorp UI generates those.
# Russian noun that introduces the entry, and the tooltip registry the object
# lives in. Registry names come from the game's own #TOOLTIP: tokens.
CATALOG_SOURCES = {
    "employment_systems": ("Способ найма рабочих", "EMPLOYMENT_SYSTEM"),
    "building_types": ("Построить в столице", "BUILDING_TYPE"),
    "religious_aspects": ("Аспект веры", "RELIGIOUS_ASPECT"),
    "religious_schools": ("Религиозная школа", "RELIGIOUS_SCHOOL"),
    "parliament_issues": ("Вопрос парламента", "PARLIAMENT_ISSUE"),
    "chivalric_orders": ("Рыцарский орден", "CHIVALRIC_ORDER"),
    "subject_types": ("Тип вассала", "SUBJECT_TYPE"),
    "estates": ("Сословие", "ESTATE_TYPE"),
    "cabinet_actions": ("Действие совета", "CABINET_ACTION"),
    "international_organizations": ("Международная организация",
                                    "INTERNATIONAL_ORGANIZATION"),
    "international_organization_special_statuses": ("Статус в организации",
                                                    "SPECIAL_STATUS"),
    "advances": ("Достижение", "ADVANCE_DEFINITION"),
    "missions": ("Миссия", "MISSION"),
    "parliament_types": ("Тип парламента", "PARLIAMENT_TYPE"),
}

# Only one of these can be in force at a time, so a weaker one is pointless
# while a stronger one is already active.
EXCLUSIVE_SOURCES = {"employment_systems"}

# Where the object definitions live, for the availability gates.
SOURCE_DIRS = {
    "building_types": "in_game/common/building_types",
    "missions": "in_game/common/missions",
    "parliament_types": "in_game/common/parliament_types",
    "religious_aspects": "in_game/common/religious_aspects",
    "religious_schools": "in_game/common/religious_schools",
    "estates": "in_game/common/estates",
    "subject_types": "in_game/common/subject_types",
    "chivalric_orders": "in_game/common/chivalric_orders",
    "parliament_issues": "in_game/common/parliament_issues",
}

# Always active, magnitude proportional to some country state. The listed value
# is the maximum, hence "до".
SCALED = {
    "fort_maintenance_mod": "Содержание крепостей",
    "army_maintenance_mod": "Содержание армии",
    "navy_maintenance_mod": "Содержание флота",
    "army_experience": "Опыт армии",
    "navy_experience": "Опыт флота",
    "army_tradition": "Традиции армии",
    "navy_tradition": "Традиции флота",
    "current_army_size": "Размер армии",
    "current_navy_size": "Размер флота",
    "average_control": "Средний контроль",
    "average_development": "Среднее развитие",
    "average_literacy": "Средняя грамотность",
    "num_of_market_centers_in_country": "Число рыночных центров",
    "trade_vs_tax": "Доля торговли в доходах",
    "burghers_percentage_in_country": "Доля горожан в населении",
    "peasants_percentage_in_country": "Доля крестьян в населении",
    "soldier_percentage_in_country": "Доля солдат в населении",
    "state_religion_clergy_ratio": "Доля духовенства госрелигии",
    "proper_culture_nobles_ratio": "Доля знати основной культуры",
}

# On or off, no scaling - the label is the condition, so the exact value holds.
CONDITIONAL = {
    "is_bankrupt": "Во время банкротства",
    "at_peace": "В мирное время",
    "at_war": "Во время войны",
    "attacker_in_war": "Нападающая сторона в войне",
    "defender_in_war": "Обороняющаяся сторона в войне",
    "over_fort_limit": "Превышен лимит крепостей",
    "below_half_fort_limit": "Крепостей меньше половины лимита",
    "larger_than_expected_army": "Армия больше ожидаемой",
    "high_legitimacy": "Высокая легитимность",
    "high_republican_tradition": "Высокие республиканские традиции",
    "positive_self_control": "Высокое самообладание правителя",
    "negative_self_control": "Низкое самообладание правителя",
    "parliament_in_capital": "Парламент в столице",
    "parliament_outside_capital": "Парламент вне столицы",
    "ruler_is_general": "Правитель - генерал",
    "ruler_is_admiral": "Правитель - адмирал",
    "ruler_has_general_trait": "У правителя черта генерала",
    "ruler_has_admiral_trait": "У правителя черта адмирала",
    "heir_is_general": "Наследник - генерал",
    "heir_is_admiral": "Наследник - адмирал",
    "regent_is_general": "Регент - генерал",
    "regent_is_admiral": "Регент - адмирал",
}

CABINET_SUFFIX = "_progress_cabinet_efficiency"

STEPS = {
    "societal_value_min_scaling_monthly_move": 0.01,
    "societal_value_tiny_monthly_move": 0.025,
    "societal_value_minor_monthly_move": 0.05,
    "societal_value_monthly_move": 0.1,
    "societal_value_large_monthly_move": 0.2,
    "societal_value_significant_monthly_move": 0.33,
    "societal_value_huge_monthly_move": 0.5,
}

HEADER = ("# Auto-generated by mods/glorpui_hints/tools/generate_extra.py from the EU5 game "
          "files. Do not edit by hand.")


def axis_pairs(path):
    pairs = []
    with open(path, encoding="utf-8-sig") as handle:
        for line in handle:
            match = re.match(r'^([a-z_]+)_vs_([a-z_]+)\s*=\s*\{', line.strip())
            if match:
                pairs.append((match.group(1), match.group(2),
                              "%s_vs_%s" % (match.group(1), match.group(2))))
    return pairs


def amount(raw):
    if raw in STEPS:
        return STEPS[raw]
    try:
        return float(raw)
    except ValueError:
        return None


def collect(findings, game_files):
    """direction -> ordered list of entry dicts."""
    caches = {}
    for source_type, relative in SOURCE_DIRS.items():
        caches[source_type] = svx_gates.scan_objects(game_files, relative)
    # Which organization grants each special status, read from the
    # organizations rather than from the statuses. See gates.status_owners.
    extra = {"status_owners": svx_gates.status_owners(game_files)}

    entries = collections.defaultdict(list)
    for row in findings:
        axis, obj, raw = row["axis"], row["object"], row["raw_value"]
        source_type = row["source_type"]
        value = amount(raw)
        if value is None:
            continue

        if source_type in CATALOG_SOURCES:
            label, registry = CATALOG_SOURCES[source_type]
            text = ("@hint! %s #TOOLTIP:%s,%s #L $%s$#!#!: #color_green +%.2f#!\\n"
                    % (label, registry, obj, obj, value))
            gate = svx_gates.gate_for(source_type, obj, caches.get(source_type, {}), extra)
            if source_type in EXCLUSIVE_SOURCES:
                # Suppress once the country holds this one, or any peer that
                # already pushes this axis at least as hard.
                peers = sorted(
                    other["object"] for other in findings
                    if other["source_type"] == source_type
                    and other["axis"] == axis
                    and (amount(other["raw_value"]) or 0) >= value)
                gate = {
                    "reach": list(gate["reach"]),
                    "now": list(gate["now"]) + [
                        "NOT = { has_employment_system = employment_system:%s }" % peer
                        for peer in dict.fromkeys(peers)],
                }
            entries[axis].append({"sort": (-value, obj), "text": text, "gate": gate})
        elif obj in SCALED:
            entries[axis].append({
                "sort": (-value, obj),
                "text": "@hint! %s #help (масштабируется)#!: #color_green до +%.2f#!\\n"
                        % (SCALED[obj], value),
                "gate": {"reach": [], "now": []}})
        elif obj in CONDITIONAL:
            entries[axis].append({
                "sort": (-value, obj),
                "text": "@hint! %s: #color_green +%.2f#!\\n" % (CONDITIONAL[obj], value),
                "gate": {"reach": [], "now": []}})
        elif obj.endswith(CABINET_SUFFIX):
            entries[axis].append({
                "sort": (-99, obj),
                "text": "@hint! Направить совет на эту ценность "
                        "#help (масштабируется от эффективности совета)#!\\n",
                "gate": {"reach": [], "now": []}})

    ordered = {}
    for axis, rows in entries.items():
        seen, out = set(), []
        for row in sorted(rows, key=lambda r: r["sort"]):
            if row["text"] in seen:
                continue
            seen.add(row["text"])
            out.append(row)
        ordered[axis] = out
    return ordered


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--findings", required=True)
    parser.add_argument("--game-files", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with open(args.findings, encoding="utf-8") as handle:
        findings = json.load(handle)
    pairs = axis_pairs(os.path.join(
        args.game_files, "in_game/common/societal_values/00_default.txt"))
    entries = collect(findings, args.game_files)

    loc = [HEADER, "l_russian:",
           ' SVX_ALSO_PUSHES: "Также влияет на смещение:"',
           ' SVX_REACHABLE: "Станет доступно при условиях:"']
    custom = [HEADER, ""]
    soon_gates = collections.defaultdict(list)
    counts = {"now": 0, "soon": 0}

    def emit(name, key, trigger_lines, text):
        loc.append(' %s: "%s"' % (key, text))
        custom.append("%s = {" % name)
        custom.append("\ttype = country")
        custom.append("\ttext = {")
        custom.append("\t\ttrigger = {")
        for line in trigger_lines:
            custom.append("\t\t\t%s" % line)
        custom.append("\t\t}")
        custom.append("\t\tlocalization_key = %s" % key)
        custom.append("\t}")
        custom.append("\ttext = {")
        custom.append("\t\tlocalization_key = empty_text")
        custom.append("\t}")
        custom.append("}")
        custom.append("")

    for left, right, _ in pairs:
        for direction in (left, right):
            now_body, soon_body = [], []
            for index, row in enumerate(entries.get(direction, [])):
                gate = row["gate"]
                if not gate["now"]:
                    now_body.append(row["text"])
                    continue

                name = "svx_n_%s_%03d" % (direction, index)
                emit(name, name.upper(), gate["now"], row["text"])
                now_body.append("[Player.Custom('%s')]" % name)
                counts["now"] += 1

                # Attainable-but-not-yet needs a real "reach" condition to be
                # about. Without one, failing "now" does not mean "later" - a
                # mutually exclusive option displaced by a better one is simply
                # out, not pending.
                if not gate["reach"] or gate["now"] == gate["reach"]:
                    continue
                soon = list(gate["reach"]) + [
                    "NOT = { AND = { %s } }" % " ".join(gate["now"])]
                name = "svx_s_%s_%03d" % (direction, index)
                emit(name, name.upper(), soon, row["text"])
                soon_body.append("[Player.Custom('%s')]" % name)
                soon_gates[direction].append(soon)
                counts["soon"] += 1

            loc.append(' SVX_BODY_%s: "%s"' % (direction.upper(), "".join(now_body)))
            loc.append(' SVX_SOON_%s: "%s"' % (direction.upper(), "".join(soon_body)))

    write(os.path.join(args.out,
                       "main_menu/localization/russian/svx_extra_hints_l_russian.yml"),
          "\n".join(loc) + "\n")
    write(os.path.join(args.out,
                       "in_game/common/customizable_localization/svx_extra_hint_loc.txt"),
          "\n".join(custom))

    values = [HEADER, ""]
    for left, right, pair in pairs:
        values += ["svx_axis_%s = {" % pair,
                   "\tvalue = 0",
                   "\tif = {",
                   "\t\tlimit = { scope:glorpui_sv = societal_value_type:%s }" % pair,
                   "\t\tadd = 1",
                   "\t}",
                   "}",
                   ""]
        for direction in (left, right):
            gates = soon_gates.get(direction, [])
            values.append("svx_soon_visible_%s = {" % direction)
            values.append("\tvalue = 0")
            if gates:
                values.append("\tif = {")
                values.append("\t\tlimit = {")
                values.append("\t\t\tscope:glorpui_sv = societal_value_type:%s" % pair)
                values.append("\t\t\tscope:glorpui_country = {")
                values.append("\t\t\t\tOR = {")
                for gate in gates:
                    values.append("\t\t\t\t\tAND = { %s }" % " ".join(gate))
                values.append("\t\t\t\t}")
                values.append("\t\t\t}")
                values.append("\t\t}")
                values.append("\t\tadd = 1")
                values.append("\t}")
            values += ["}", ""]
    write(os.path.join(args.out,
                       "in_game/common/script_values/svx_extra_hint_script_values.txt"),
          "\n".join(values))

    def scroll_list(visible_value, title, body_key):
        return "\n".join([
            "\t\tTooltipScrolledStringPairList = {",
            "\t\t\tvisible = \"[GreaterThan_CFixedPoint(GuiScope"
            ".AddScope('glorpui_sv', SocietalValue.MakeScope)"
            ".AddScope('glorpui_country', Player.MakeScope)"
            ".ScriptValue('%s'), '(CFixedPoint)0')]\"" % visible_value,
            "\t\t\tblockoverride \"block_scrollarea\" {",
            "\t\t\t\tmaximumsize = { -1 160 }",
            "\t\t\t}",
            "",
            "\t\t\tblockoverride \"block_title\" {",
            "\t\t\t\ttext = \"%s\"" % title,
            "\t\t\t\tdefault_format = \"#help\"",
            "\t\t\t}",
            "",
            "\t\t\ttextcontext = \"[Localize('%s')]\"" % body_key,
            "\t\t}",
            "",
        ])

    gui = [HEADER,
           "# Overrides Glorp UI's own override, so this mod must load AFTER Glorp UI.",
           "# Glorp UI's takeable-only list is re-emitted first, unchanged in behaviour:",
           "# same GLORP_UI_SVH_BODY_* body keys, same glorpui_svh_visible_* gate.",
           ""]
    for side, index, block_name, vanilla_title in (
            ("Left", 0, "societal_value_left_tooltip_extra", "TO_MOVE_FURTHER_TO_LEFT"),
            ("Right", 1, "societal_value_right_tooltip_extra", "TO_MOVE_FURTHER_TO_RIGHT")):
        gui.append("template SocietalValueCountry%s_tooltip {" % side)
        gui.append("\tusing = SocietalValue%s_tooltip" % side)
        gui.append("\tblockoverride \"%s\" {" % block_name)
        for parts in pairs:
            direction = parts[index]
            gui.append(scroll_list("glorpui_svh_visible_%s" % direction,
                                   vanilla_title,
                                   "GLORP_UI_SVH_BODY_%s" % direction.upper()))
            gui.append(scroll_list("svx_axis_%s" % parts[2], "SVX_ALSO_PUSHES",
                                   "SVX_BODY_%s" % direction.upper()))
            gui.append(scroll_list("svx_soon_visible_%s" % direction, "SVX_REACHABLE",
                                   "SVX_SOON_%s" % direction.upper()))
        gui += ["\t}", "}", ""]
    write(os.path.join(args.out, "in_game/gui/svx_extra_societal_value_hints.gui"),
          "\n".join(gui))

    total = sum(len(v) for v in entries.values())
    print("%d hint lines: %d gated as available now, %d also listed as attainable"
          % (total, counts["now"], counts["soon"]))


if __name__ == "__main__":
    main()

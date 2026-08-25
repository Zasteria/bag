#!/usr/bin/env python3
"""Availability gates for the extra societal value hints.

Reads the game files a second time to learn, per object, what a country needs in
order for that object to be reachable at all - so hints for other religions,
other estates or other subject types stop showing up.

Only triggers whose exact syntax is confirmed by usage in the shipped game files
are emitted. Anything unconfirmed is left ungated rather than guessed at: a
mistyped trigger is a load error, an ungated hint is only noise.
"""

import os
import re

CONFIRMED_NOTE = "# gates use only trigger forms found verbatim in the game files"


def find_blocks(text):
    """Yield (object_key, body_text) for each top-level `key = { ... }`."""
    depth = 0
    key = None
    start = None
    i = 0
    line_start = True
    while i < len(text):
        ch = text[i]
        if ch == "#":
            j = text.find("\n", i)
            i = len(text) if j < 0 else j
            continue
        if ch == "{":
            if depth == 0 and key:
                start = i + 1
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and key and start is not None:
                yield key, text[start:i]
                key = None
                start = None
        elif depth == 0:
            match = re.match(r'([a-zA-Z_][a-zA-Z_0-9]*)\s*=\s*\{', text[i:])
            if match:
                key = match.group(1)
                i += match.end() - 1
                continue
        i += 1


def sub_block(body, name):
    """Return the raw text of `name = { ... }` inside body, or None."""
    match = re.search(r'\b%s\s*=\s*\{' % re.escape(name), body)
    if not match:
        return None
    depth = 0
    for i in range(match.end() - 1, len(body)):
        if body[i] == "{":
            depth += 1
        elif body[i] == "}":
            depth -= 1
            if depth == 0:
                return body[match.end():i].strip()
    return None


def scan_objects(root, relative_dir):
    """object key -> body text, for every .txt under root/relative_dir."""
    objects = {}
    directory = os.path.join(root, relative_dir)
    if not os.path.isdir(directory):
        return objects
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".txt"):
            continue
        with open(os.path.join(directory, name),
                  encoding="utf-8-sig", errors="replace") as handle:
            for key, body in find_blocks(handle.read()):
                objects[key] = body
    return objects


def gate_for(source_type, key, objects):
    """Return {"reach": [...], "now": [...]} trigger lines for one hint.

    "reach" is what the country can never change on a whim - its tag, religion,
    which estates it has. Failing it means the hint is impossible and is dropped
    entirely. "now" adds what has to be true to act on it today. An entry that
    passes "reach" but not "now" is listed as merely attainable.

    Empty lists mean unconditional.
    """
    body = objects.get(key, "")

    if source_type == "religious_aspects":
        religions = re.findall(r'^\s*religion\s*=\s*([a-z_0-9]+)\s*$', body, re.M)
        reach = []
        if religions:
            # `country_religion = religion:X` - confirmed in common/religious_aspects
            reach.append("OR = { %s }" % " ".join(
                "country_religion = religion:%s" % r for r in sorted(set(religions))))
        # `has_religious_aspect = religious_aspect:X` - confirmed in the same files
        now = reach + ["NOT = { has_religious_aspect = religious_aspect:%s }" % key]
        enabled = sub_block(body, "enabled")
        if enabled:
            now.append(" ".join(enabled.split()))
        return {"reach": reach, "now": now}

    if source_type == "building_types":
        # The game's own blocks, copied verbatim: country_potential says which
        # countries may ever have it, allow says whether it can be built now.
        potential = sub_block(body, "country_potential")
        reach = [" ".join(potential.split())] if potential else []
        allow = sub_block(body, "allow")
        now = reach + ([" ".join(allow.split())] if allow else [])
        return {"reach": reach, "now": now}

    if source_type == "religious_schools":
        enabled = sub_block(body, "enabled_for_country")
        lines = [" ".join(enabled.split())] if enabled else []
        return {"reach": lines, "now": lines}

    if source_type == "estates":
        # `country_has_estate = estate_type:X` - confirmed in Glorp UI and game files
        lines = ["country_has_estate = estate_type:%s" % key]
        return {"reach": lines, "now": lines}

    if source_type == "parliament_issues":
        return {"reach": ["has_parliament = yes"], "now": ["has_parliament = yes"]}

    if source_type == "subject_types":
        lines = ["is_subject_type = %s" % key]
        return {"reach": lines, "now": lines}

    if source_type == "chivalric_orders":
        lines = ["has_chivalric_order = yes"]
        return {"reach": lines, "now": lines}

    return {"reach": [], "now": []}

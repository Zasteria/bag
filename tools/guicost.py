#!/usr/bin/env python3
"""What the interface costs before anybody clicks anything.

The owner reports that a panel opens instantly in vanilla and with a hitch —
sometimes a freeze — under his playset, on a save loaded a minute ago. That is
not the widget leak: the leak grows over hours, this is there from the first
second. So it is something the mods do every frame, or every time a list is
drawn, and it can be counted in the files.

Three things cost that way, and this tool counts all three.

**`scripted_widgets/`** is a promise that a window exists for the whole session.
The engine instantiates every entry into the running interface at load and never
takes it down; a window hidden behind `visible = no` is still a live widget tree
whose `visible`, `enabled` and `datacontext` expressions are asked every frame.
A mod with seven of them has seven trees running whether or not the player has
ever opened the mod.

**`GetScriptedGui('x')`** in a `.gui` file runs a script trigger from the
interface. That is the expensive kind of expression — it enters the script
engine — and vanilla uses it nine times in three hundred and eighty-seven files.
A mod that uses it thousands of times is doing something categorically different
from what the base game does, and the count says so at a glance.

**Animation states with a `duration` and a `next`** are how a `.gui` file gets a
timer. A state that names itself as its own successor is a loop running at that
period for as long as its widget is alive; inside an always-live window that is a
background worker, and its period is the tool's best guess at how often.

The widget counts here are **static declarations, and they understate a window
built on `datamodel`**: one declared item becomes one live widget per row of the
list it binds. `cm_hidden_window` declares twenty-three widgets and binds a
datamodel over every building type in the game, so what actually lives is that
subtree times four hundred and sixty-five. `--drivers` names the list each
always-live window iterates, because the multiplier is the number that matters
and no static count can know it.

`gui/filters/` is counted too, by tag: every chip whose tag matches a list is a
trigger evaluated once per item in that list, so chips added to a busy tag are
paid at every open.

    python3 tools/guicost.py            the census, vanilla first
    python3 tools/guicost.py --drivers  the always-live windows, in detail
    python3 tools/guicost.py --filters  filter chips by tag
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import refs  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

# `name = {` at the start of a line is a widget in a .gui file.
WIDGET = re.compile(r"(?m)^\s*[a-z_]+\s*=\s*\{")
# `gui/x.gui = widget_name` — one permanently instantiated window per line.
SCRIPTED_WIDGET = re.compile(r"(?m)^\s*(\S+\.gui)\s*=\s*(\S+)\s*$")
# A filter chip is a top-level entry; the file has no indentation above it.
FILTER_ENTRY = re.compile(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{")
STATE = re.compile(r"state\s*=\s*\{")
DURATION = re.compile(r"duration\s*=\s*([0-9.]+)")
NEXT = re.compile(r"next\s*=\s*(\S+)")
STATE_NAME = re.compile(r"name\s*=\s*(\S+)")

# `datamodel = "[...GetList('x')...]"` — what a repeated widget is repeated over.
DATAMODEL = re.compile(r'datamodel\s*=\s*"\[([^"]*)\]"')
# The engine calls that cost real work when a .gui asks for them per item.
EXPENSIVE = (
    "GetBuildOrExpandBuildingCost",
    "GetBuildingTypeIncomeToOwnerInLocation",
    "GetBuildingTypeProfitInLocation",
    "CanBuildOrExpandBuilding",
)


@dataclass
class Census:
    name: str
    root: Path
    files: int = 0
    widgets: int = 0
    scripted_gui: int = 0
    live_windows: list[tuple[str, str]] = field(default_factory=list)
    loops: list[tuple[str, str, float]] = field(default_factory=list)
    datamodels: list[tuple[str, str]] = field(default_factory=list)
    filters: dict[str, int] = field(default_factory=dict)
    expensive: dict[str, int] = field(default_factory=dict)

    @property
    def live_widgets(self) -> int:
        """Widgets in the always-instantiated windows, which never come down."""
        return sum(w for _, w in self._live_sizes)

    _live_sizes: list[tuple[str, int]] = field(default_factory=list)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def gui_dir(root: Path) -> Path | None:
    for candidate in (root / "in_game" / "gui", root / "gui"):
        if candidate.is_dir():
            return candidate
    return None


def self_restarting_loops(text: str) -> list[tuple[str, float]]:
    """States that name themselves, directly or through a second state, as next.

    One `duration` plus a `next` pointing back into the same cycle is a timer
    that never stops. The period reported is the shortest duration in the cycle,
    which is the interval at which something happens.
    """
    states: dict[str, tuple[float, str]] = {}
    for match in STATE.finditer(text):
        body = text[match.end():match.end() + 600]
        name = STATE_NAME.search(body)
        duration = DURATION.search(body)
        nxt = NEXT.search(body)
        if name and duration and nxt:
            states[name.group(1)] = (float(duration.group(1)), nxt.group(1))
    loops = []
    for name, (duration, nxt) in states.items():
        seen, cursor, period = {name}, nxt, duration
        while cursor in states and cursor not in seen:
            seen.add(cursor)
            period = min(period, states[cursor][0])
            cursor = states[cursor][1]
        if cursor in seen:                       # the chain closed on itself
            loops.append((name, period))
    return loops


def census(name: str, root: Path) -> Census:
    out = Census(name, root)
    gui = gui_dir(root)
    if gui is None:
        return out

    live = {}
    for path in sorted((gui / "scripted_widgets").glob("*.txt")) if (gui / "scripted_widgets").is_dir() else []:
        for match in SCRIPTED_WIDGET.finditer(read(path)):
            live[match.group(2)] = Path(match.group(1)).name

    for path in sorted(gui.rglob("*.gui")):
        text = read(path)
        out.files += 1
        widgets = len(WIDGET.findall(text))
        out.widgets += widgets
        out.scripted_gui += text.count("GetScriptedGui")
        for call in EXPENSIVE:
            if call in text:
                out.expensive[call] = out.expensive.get(call, 0) + text.count(call)
        for widget, source in live.items():
            if source != path.name:
                continue
            out.live_windows.append((widget, path.name))
            out._live_sizes.append((widget, widgets))
            for state, period in self_restarting_loops(text):
                out.loops.append((widget, state, period))
            for match in DATAMODEL.finditer(text):
                out.datamodels.append((widget, match.group(1)))

    filters = gui / "filters"
    if filters.is_dir():
        for path in sorted(filters.glob("*.txt")):
            text = read(path)
            marks = [(m.start(), m.group(1)) for m in FILTER_ENTRY.finditer(text)]
            for index, (start, _) in enumerate(marks):
                end = marks[index + 1][0] if index + 1 < len(marks) else len(text)
                found = re.search(r"(?m)^\s*tag\s*=\s*(\S+)", text[start:end])
                key = found.group(1) if found else "-"
                out.filters[key] = out.filters.get(key, 0) + 1
    return out


def everything() -> list[Census]:
    out = [census("vanilla", refs.GAME)]
    for key in refs.KNOWN:
        try:
            path = refs.known(key)
        except (KeyError, FileNotFoundError):
            continue
        out.append(census(key, Path(path)))
    for path in sorted((REPO / "mods").iterdir()):
        if path.is_dir() and gui_dir(path):
            out.append(census("mods/" + path.name, path))
    return out


def tag_matches(tag: str, wanted: str) -> bool:
    return wanted in tag.split("|")


def main(argv: list[str]) -> int:
    rows = everything()

    if "--filters" in argv:
        tags = sorted({t for row in rows for tag in row.filters for t in tag.split("|")})
        print("Filter chips, by the tag a list asks for. Every chip whose tag")
        print("matches is a trigger run once per item, every time the list draws.\n")
        width = max(len(row.name) for row in rows)
        print(" " * (width + 2) + "".join("%14s" % t[:13] for t in tags))
        for row in rows:
            if not row.filters:
                continue
            counts = [sum(n for tag, n in row.filters.items() if tag_matches(tag, t)) for t in tags]
            print("%-*s  " % (width, row.name) + "".join("%14d" % c for c in counts))
        base = rows[0]
        print()
        for t in tags:
            v = sum(n for tag, n in base.filters.items() if tag_matches(tag, t))
            m = sum(sum(n for tag, n in r.filters.items() if tag_matches(tag, t)) for r in rows[1:])
            if m:
                print("  %-30s vanilla %3d, mods add %3d  (+%d%%)" % (t, v, m, round(100 * m / max(v, 1))))
        return 0

    if "--drivers" in argv:
        print("Windows listed in scripted_widgets/ are instantiated at load and")
        print("stay for the session. A self-restarting animation state inside one")
        print("is a background worker running at that period.\n")
        for row in rows:
            if not row.live_windows:
                continue
            print("%s — %d always-live window(s), %d widgets in them"
                  % (row.name, len(row.live_windows), row.live_widgets))
            for widget, source in row.live_windows:
                loops = [(s, p) for w, s, p in row.loops if w == widget]
                size = dict(row._live_sizes).get(widget, 0)
                print("    %-42s %-38s %5d widgets declared" % (widget, source, size))
                if loops:
                    print("        loops: " + ", ".join("%s every %gs" % (s, p) for s, p in loops))
                bound = [b for w, b in row.datamodels if w == widget]
                for expression in bound:
                    print("        one per row of: %s" % expression)
            print()
        return 0

    print("%-24s %6s %8s %14s %6s %6s" % ("", "files", "widgets", "GetScriptedGui", "live", "loops"))
    for row in rows:
        if not row.files:
            continue
        print("%-24s %6d %8d %14d %6d %6d"
              % (row.name, row.files, row.widgets, row.scripted_gui,
                 len(row.live_windows), len(row.loops)))

    base = rows[0]
    density = base.scripted_gui / max(base.widgets, 1)
    print("\nVanilla asks the script engine from the interface %d time(s) across %d"
          % (base.scripted_gui, base.widgets))
    print("widgets — %.4f calls per widget. Against that:\n" % density)
    for row in rows[1:]:
        if not row.widgets:
            continue
        mine = row.scripted_gui / row.widgets
        if mine > density * 10 and row.scripted_gui > 100:
            print("  %-24s %.3f per widget — %dx vanilla's density"
                  % (row.name, mine, round(mine / max(density, 1e-9))))
    hot = [(r.name, r.expensive) for r in rows[1:] if r.expensive]
    if hot:
        print("\nEngine calls that price a building in a location, asked from a .gui:")
        for name, calls in hot:
            print("  %s" % name)
            for call, n in sorted(calls.items()):
                print("      %-42s %d" % (call, n))
    print("\n  --drivers   the always-live windows and their loops")
    print("  --filters   filter chips by tag")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

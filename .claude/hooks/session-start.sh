#!/bin/bash
# Hand a fresh session the state of the tree, before it reads a single document.
#
# There is nothing to install here — the tooling is Python 3 and the standard
# library. What a session actually needs at minute zero is the opposite of
# setup: the facts that the documents cannot keep current on their own, because
# the owner refreshes `reference/` by hand and without notice.
#
# So this runs the repository's own checkers and hands their output back as
# context: what is in reference/ and at which version, whether the generated
# files still match it, and whether the documents still describe files that
# exist. Nothing is written to the working tree — refresh runs with --check.
set -uo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0

briefing=$(
    echo "State of the tree, read just now — trust this over any version or path written in a document."
    echo
    python3 tools/refresh.py --check 2>&1 | sed -n '/^reference\//,$p'
    echo
    python3 tools/check_docs.py --quiet 2>&1
    echo
    # Whether the workshop has moved under the reference copies. Needs the
    # network, so it is given a short leash and allowed to say nothing: a
    # session that cannot reach Steam is not a session that should stall here.
    timeout 20 python3 tools/workshop.py status --quiet 2>/dev/null
    echo
    echo "Reminders that cost a round trip when forgotten:"
    echo "  - Only the player can run the game. Nothing here can be tested from a session."
    echo "  - Build the smallest thing that shows a signal, then ask for a run."
    echo "  - A run the player reports goes into docs/TESTLOG.md in the same session."
    echo "  - Verify against reference/ rather than memory; docs/PITFALLS.md is the list of what has already gone wrong quietly."
)

python3 - "$briefing" <<'PY'
import json
import sys

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": sys.argv[1],
    }
}))
PY

#!/bin/bash
# qa-check push gate (PreToolUse hook on Bash).
# Blocks `git push` until /qa-check has run against the current HEAD
# (or within the last 30 minutes). Deterministic — no LLM calls, no API cost.
#
# Opt-in per repo: create a `.qa-check-required` file at the repo root.
# Escape hatch:    QA_CHECK_SKIP=1 git push
# Marker file:     .git/qa-check-ok (written by /qa-check Step 9: sha + epoch)

set -u

INPUT=$(cat)

CMD=$(printf '%s' "$INPUT" | python3 -c '
import json,sys
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))
except Exception:
    print("")
' 2>/dev/null)

# Only gate git push commands; let everything else through.
case "$CMD" in
  *"git push"*) ;;
  *) exit 0 ;;
esac

# Explicit override.
case "$CMD" in
  *"QA_CHECK_SKIP=1"*) exit 0 ;;
esac

REPO_ROOT=$(git -C "${CLAUDE_PROJECT_DIR:-.}" rev-parse --show-toplevel 2>/dev/null)
[ -z "$REPO_ROOT" ] && exit 0

# Opt-in: only enforce in repos that ask for it.
[ -f "$REPO_ROOT/.qa-check-required" ] || exit 0

MARKER="$(git -C "$REPO_ROOT" rev-parse --absolute-git-dir)/qa-check-ok"
BLOCK_MSG="qa-check gate: this repo requires a QA check before push (.qa-check-required). Run /qa-check, then push. Override for this push only: QA_CHECK_SKIP=1 git push"

if [ ! -f "$MARKER" ]; then
  echo "$BLOCK_MSG" >&2
  exit 2
fi

MARKER_SHA=$(sed -n '1p' "$MARKER")
MARKER_TIME=$(sed -n '2p' "$MARKER")
HEAD_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null)
NOW=$(date +%s)
AGE=$(( NOW - ${MARKER_TIME:-0} ))

# Fresh if the check ran against this exact HEAD, or ran recently
# (covers the normal flow: qa-check -> fix -> commit -> push).
if [ "$MARKER_SHA" = "$HEAD_SHA" ] || [ "$AGE" -lt 1800 ]; then
  exit 0
fi

echo "qa-check gate: last QA check is stale (ran against ${MARKER_SHA:0:8}, $(( AGE / 60 )) minutes ago; HEAD is ${HEAD_SHA:0:8}). Run /qa-check again, then push. Override: QA_CHECK_SKIP=1 git push" >&2
exit 2

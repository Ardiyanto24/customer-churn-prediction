#!/bin/bash
# Hook: post-commit-update-progress.sh
# Trigger: PostToolUse — runs after every tool call
# Purpose: After a git commit, extract task code from commit message
#          and mark it as done [x] in docs/DEV-PROGRESS.md.
#
# Watches only for git commit tool calls. Ignores all other tool calls.
# If DEV-PROGRESS.md does not contain the task line, exits silently.

set -euo pipefail

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")

# Only act on bash tool calls
if [[ "$TOOL_NAME" != "bash" ]]; then
  exit 0
fi

COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
inp = d.get('tool_input', {})
print(inp.get('command', ''))
" 2>/dev/null || echo "")

# Only act on git commit commands
if [[ "$COMMAND" != git\ commit* ]]; then
  exit 0
fi

# Skip progress-update commits to avoid infinite loop
if echo "$COMMAND" | grep -q "chore: progress"; then
  exit 0
fi

# Extract task code pattern X.X.X from commit message
TASK_CODE=$(echo "$COMMAND" | grep -oP 'Task \d+\.\d+\.\d+' | head -1 || echo "")

if [[ -z "$TASK_CODE" ]]; then
  exit 0
fi

PROGRESS_FILE="docs/DEV-PROGRESS.md"

if [[ ! -f "$PROGRESS_FILE" ]]; then
  exit 0
fi

# Check if task line exists and is unchecked
if grep -q "\- \[ \].*${TASK_CODE}" "$PROGRESS_FILE"; then
  # Mark task as done: [ ] → [x]
  sed -i "s/- \[ \] \(.*${TASK_CODE}\)/- [x] \1/" "$PROGRESS_FILE"

  git add "$PROGRESS_FILE"
  git commit -m "chore: progress ${TASK_CODE}"

  echo "DEV-PROGRESS.md updated: ${TASK_CODE} marked done." >&2
else
  # Task line not found or already checked — exit silently
  exit 0
fi

exit 0
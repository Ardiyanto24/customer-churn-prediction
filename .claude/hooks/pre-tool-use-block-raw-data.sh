#!/bin/bash
# Hook: pre-tool-use-block-raw-data.sh
# Trigger: PreToolUse — runs before every tool call
# Purpose: Block any write operation targeting data/raw/ or model artifacts
#
# Claude Code passes tool call info as JSON via stdin.
# Exit code 0 = allow, Exit code 1 = block (with message to Claude Code).

set -euo pipefail

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")

if [[ "$TOOL_NAME" != "write_file" && "$TOOL_NAME" != "create_file" && "$TOOL_NAME" != "str_replace" && "$TOOL_NAME" != "edit_file" ]]; then
  exit 0
fi

FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
inp = d.get('tool_input', {})
print(inp.get('path', inp.get('file_path', inp.get('target_file', ''))))
" 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Normalize: strip leading ./
NORMALIZED="${FILE_PATH#./}"

# Block: data/raw/
if [[ "$NORMALIZED" == data/raw/* ]]; then
  echo "BLOCKED: data/raw/ is immutable. No file in data/raw/ may be created or modified." >&2
  echo "If you need to add raw data, do it manually outside of Claude Code." >&2
  exit 1
fi

# Block: model artifacts
if [[ "$NORMALIZED" == models/artifacts/*.joblib || "$NORMALIZED" == models/artifacts/*.pkl ]]; then
  echo "BLOCKED: models/artifacts/*.joblib and *.pkl are protected artifacts." >&2
  echo "These files are produced by the training pipeline and must not be overwritten by Claude Code." >&2
  echo "To update model_final.joblib, copy the correct tuned_{key}.joblib manually." >&2
  exit 1
fi

exit 0
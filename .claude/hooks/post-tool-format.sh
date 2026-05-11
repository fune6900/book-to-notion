#!/bin/bash
# PostToolUse: Write/Edit 後に対象ファイルを自動フォーマット
# Python: ruff format → 失敗時は black → どちらもなければ no-op
# その他: 何もしない（HTML/CSS/JS は素のまま運用）

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

case "$FILE_PATH" in
  *.py)
    if command -v ruff &>/dev/null; then
      ruff format "$FILE_PATH" 2>/dev/null
      ruff check --fix --quiet "$FILE_PATH" 2>/dev/null
    elif command -v black &>/dev/null; then
      black --quiet "$FILE_PATH" 2>/dev/null
    fi
    ;;
  *.json)
    if command -v jq &>/dev/null; then
      TMP=$(mktemp)
      if jq '.' "$FILE_PATH" > "$TMP" 2>/dev/null; then
        mv "$TMP" "$FILE_PATH"
      else
        rm -f "$TMP"
      fi
    fi
    ;;
  *)
    # HTML/CSS/JS/MD は手動運用。自動整形しない
    ;;
esac

exit 0

#!/bin/bash
# PreToolUse: 危険なコマンド実行前にブロック
# exit 2 = ブロック（stderr が Claude に渡される）
# exit 0 = 続行

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# 危険パターン
DANGEROUS_PATTERNS=(
  "rm -rf"
  "rm -r /"
  "DROP TABLE"
  "DROP DATABASE"
  "TRUNCATE"
  "git push --force"
  "git push -f"
  "git reset --hard"
  "git clean -fd"
  "chmod -R 777"
  "> /dev/sda"
  "mkfs"
  "dd if="
  ":(){ :|:& };:"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qi "$pattern"; then
    echo "⚠ 危険なコマンドを検知: $COMMAND" >&2
    echo "パターン: $pattern" >&2
    echo "このコマンドはブロックされた。実行を拒否する。" >&2
    exit 2
  fi
done

# .env / credentials.json への書き込みは念押しでブロック
if echo "$COMMAND" | grep -qE '(>|tee).*\.env([^.a-z]|$)' ; then
  echo "⚠ .env への書き込みを検知。シェル経由での編集は禁止。" >&2
  exit 2
fi

if echo "$COMMAND" | grep -qE '(>|tee).*credentials\.json' ; then
  echo "⚠ credentials.json への書き込みを検知。シェル経由での編集は禁止。" >&2
  exit 2
fi

exit 0

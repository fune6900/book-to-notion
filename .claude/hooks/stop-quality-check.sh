#!/bin/bash
# Stop: エージェント停止時に Python の静的チェックを走らせる
# ruff / mypy / py_compile を順に試し、問題があれば exit 2 で報告

PROJECT_DIR="$CLAUDE_PROJECT_DIR"

# Python ファイルが存在しない場合はスキップ
if ! ls "$PROJECT_DIR"/*.py >/dev/null 2>&1; then
  exit 0
fi

ERRORS=""

# 1. 構文チェック（最低ライン）
SYNTAX_OUTPUT=$(cd "$PROJECT_DIR" && python3 -m py_compile *.py 2>&1)
if [ $? -ne 0 ]; then
  ERRORS="${ERRORS}\n[Python 構文エラー]\n${SYNTAX_OUTPUT}\n"
fi

# 2. ruff（インストールされていれば）
if command -v ruff &>/dev/null; then
  RUFF_OUTPUT=$(cd "$PROJECT_DIR" && ruff check . 2>&1)
  if [ $? -ne 0 ]; then
    ERRORS="${ERRORS}\n[ruff 警告]\n${RUFF_OUTPUT}\n"
  fi
fi

# 3. mypy（インストールされていれば・厳しすぎるので警告のみ）
if command -v mypy &>/dev/null && [ -f "$PROJECT_DIR/mypy.ini" ]; then
  MYPY_OUTPUT=$(cd "$PROJECT_DIR" && mypy . 2>&1)
  if [ $? -ne 0 ]; then
    ERRORS="${ERRORS}\n[mypy 警告]\n${MYPY_OUTPUT}\n"
  fi
fi

if [ -n "$ERRORS" ]; then
  echo -e "⚠ 品質チェックで問題を検出:${ERRORS}" >&2
  exit 2
fi

exit 0

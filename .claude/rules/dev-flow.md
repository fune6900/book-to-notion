# 開発フロー（軽量版）

このプロジェクトは個人用ツール。重厚な TDD は不要だが、フローの骨組みは守る。
違反はメイド長（Benz）が差し戻す。

---

## Step 1: Plan Mode（設計）

`/plan` を使い、実装前に設計を行う。

- 要件を分解する
- 影響範囲（`app.py` / `main.py` / `slide_image.py` / `static/`）を特定する
- 新規ファイルを追加するなら、既存3ファイルで吸収できないか先に検討する
- 実装方針が固まるまでコードに触れない

**参照**: `@.claude/rules/agents.md`（Benz が担当）

---

## Step 2: ISSUE 作成

```bash
gh issue create \
  --title "<機能名または修正内容>" \
  --body "$(cat <<'EOF'
## 概要
<!-- 何を実装/修正するか -->

## 受け入れ条件
- [ ] 条件1
- [ ] 条件2

## 技術的メモ
<!-- 実装方針・参照ファイル・依存関係 -->

## 関連
<!-- 関連 ISSUE / PR があればリンク -->
EOF
)"
```

軽微な fix（typo・README）であれば ISSUE 省略可。

---

## Step 3: ブランチ作成

```bash
git checkout -b feat/<issue番号>-<内容>
# 例: feat/12-add-pdf-support
# 例: fix/15-sse-buffering-on-render
```

**参照**: `@.claude/rules/git-strategy.md`

---

## Step 4: 実装

### 4-1. 設計確認（Architect、必要な場合）

データ構造の追加・モジュール分割・型ヒントの追加が必要なら Architect を呼ぶ。

**参照**: `@.claude/rules/conventions.md`

### 4-2. 実装（Coder）

`@.claude/rules/conventions.md` / `@.claude/rules/security.md` / `@.claude/rules/api-design.md` を守る。

- 型ヒント必須
- 例外を握りつぶさない
- `secure_filename` を必ず通す
- Gemini レスポンスを盲信しない

### 4-3. UI 変更（Designer、必要な場合）

`static/index.html` を変更する場合は Designer を呼ぶ。

- サイバーパンク調のデザイン言語を維持する
- 既存の CSS 変数 (`--cyan` / `--pink` 等) を使う
- レスポンシブ（〜768px / 〜480px）を確認する

### 4-4. テスト / スモーク確認（QA）

`@.claude/rules/testing.md` を参照。pytest 導入前は手動スモーク確認が基本。

新しいルートを足した時:
```bash
curl -s http://localhost:5001/api/photos
```

UI 変更時は `/visual-regression` を使う。

### 4-5. 品質評価（Evaluator）【必須】

**Coder/Designer の実装完了後、必ず評価のメイド（Evaluator）を呼び出す。**

- `python3 -m py_compile app.py main.py slide_image.py` を実行する
- `ruff check .` / `mypy .` をインストール済みなら実行する
- セキュリティ・コード規約に違反していないか確認する
- 動作確認手順を PR に書けるレベルで把握する
- **PASS** → 4-6 へ
- **FAIL** → 差し戻し事項を Coder/Designer に渡してループ

```
┌──────────────────────────────┐
│    Cybernetic Loop           │
│  Coder/Designer（実装）       │
│        ↓                    │
│  Evaluator（評価）            │
│   FAIL ↙       ↘ PASS       │
│  差し戻し      4-6 へ        │
└──────────────────────────────┘
```

### 4-6. リファクタリング（Benz 監督）

テストが通ったまま品質を上げる。リファクタ後も Evaluator が PASS していること。

---

## Step 5: /smart-commit

Evaluator が PASS を出した後、`/smart-commit` でコミットする。

- 機密ファイル（`.env` / `credentials.json`）が混入していないことを確認
- コミットメッセージは変更の「理由」を書く

**参照**: `@.claude/rules/git-strategy.md`

---

## Step 6: PR 作成

`/create-pr` で PR を作成する。

- タイトルは英語または日本語・70文字以内
- body は `.github/pull_request_template.md` に従う
- `Closes #<issue番号>` を必ず記載する

**参照**: `@.claude/rules/git-strategy.md`

---

## Step 7: ローカル動作確認

PR 作成前後に必ずローカルで確認する。

```bash
# 構文チェック
python3 -m py_compile app.py main.py slide_image.py

# Docker で起動
docker compose up

# ブラウザで http://localhost:5001 を開いて主要フロー確認
```

UI 変更があれば `/visual-regression`。フロー全体に影響がある変更なら `/e2e-test`。

### 7-1. スクショ・検証画像の後始末【必須】

- 検証用に `photos/` に入れた `*.jpg` / `*.png` は実行後に削除する
- ルート直下に残ったスクリーンショット（Playwright 経由の `*.png` 等）も削除する
- `static/` 配下の本番画像（favicon・icon-*）は削除しない

```bash
ls -1 *.png *.jpeg 2>/dev/null   # 確認
rm *.png *.jpeg 2>/dev/null      # 削除
```

`/smart-commit` 実行前に `git status` で残骸が無いことを確認する。

---

## Step 8: CI 確認（GitHub Actions）

push 後、GitHub Actions のジョブがグリーンになることを確認する。

| ジョブ        | 確認内容                              |
| ------------- | ------------------------------------- |
| Lint (ruff)   | ruff check 違反なし                   |
| Syntax        | `python -m py_compile` 成功           |
| Docker Build  | Dockerfile がビルド可能（任意）       |

red の場合はマージしない。原因を特定して修正する。

---

## Step 9: AI コードレビュー

`/review-pr` で AI による独立レビュー（Evaluator）を実施する。

照合ルール:
- `@.claude/rules/conventions.md`
- `@.claude/rules/security.md`
- `@.claude/rules/testing.md`
- `@.claude/rules/api-design.md`
- `@.claude/rules/git-strategy.md`

重要度「高」の指摘がある場合はマージしない。Step 4 に戻る。

---

## Step 10: LGTM

レビュー指摘が全て解消されたら LGTM。

- チェックリスト全完了を確認
- CI 全件グリーンを再確認

---

## Step 11: マージ

```bash
gh pr merge <PR番号> --squash --delete-branch
```

- `--squash` でコミットを1つに圧縮
- `--delete-branch` でブランチ削除
- マージ後、ISSUE が自動クローズされることを確認

**参照**: `@.claude/rules/git-strategy.md`

---

## Step 12: リリース確認

main へのマージ = Render の自動デプロイがトリガーされる。

- https://book-to-notion.onrender.com を開いて起動確認
- 主要フロー（アップロード → 実行 → Notion 反映）を1回試す
- Render ダッシュボードでデプロイログを確認（エラー時）
- 無料プランは初回アクセスから数十秒スリープ復帰がかかる。即時応答を期待しない

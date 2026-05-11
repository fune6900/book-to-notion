# Git / ブランチ戦略

## ブランチモデル

```
main
  └── feat/<issue番号>-<内容>      # 新機能
  └── fix/<issue番号>-<内容>       # バグ修正
  └── refactor/<issue番号>-<内容>  # リファクタリング
  └── chore/<issue番号>-<内容>     # 設定・依存関係変更
  └── ci/<issue番号>-<内容>        # CI/CD 変更
  └── docs/<issue番号>-<内容>      # ドキュメントのみ
```

- `main` は常に **Render にデプロイ可能な状態** を維持する（push が即デプロイ）
- 直接 `main` へのコミットは禁止。必ずブランチを切って PR を通す
- 1ブランチ = 1 ISSUE が原則

---

## ブランチ命名規則

```
<種別>/<issue番号>-<内容の短縮（英語・kebab-case）>

feat/12-add-pdf-support
fix/15-sse-buffering-on-render
refactor/20-extract-notion-block-builder
chore/25-bump-google-genai
ci/30-add-ruff-check
docs/8-update-readme-deploy-steps
```

| 種別        | 用途                                  |
| ----------- | ------------------------------------- |
| `feat/`     | 新機能の追加                          |
| `fix/`      | バグ修正                              |
| `refactor/` | 機能変更を伴わない構造改善            |
| `chore/`    | 設定・依存・docker・render.yaml 変更  |
| `ci/`       | GitHub Actions の変更                 |
| `docs/`     | README / CLAUDE.md 等のドキュメント   |

---

## コミット規約

```
<種別>: <変更の理由または内容（英語または日本語・50文字以内）>

本文（省略可）:
- 詳細な理由・背景
- 意思決定の記録

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

| 種別       | 用途                       |
| ---------- | -------------------------- |
| `feat`     | 新機能                     |
| `fix`      | バグ修正                   |
| `refactor` | リファクタリング           |
| `test`     | テスト追加・修正           |
| `chore`    | 設定変更・依存更新         |
| `ci`       | CI/CD 変更                 |
| `docs`     | ドキュメントのみ           |

**NG 例**: `update`, `WIP`, `あとでなおす`, `fix bug`
**OK 例**: `fix: prevent SSE buffering on Render free plan`, `feat: 画像アップロード枚数を最大10枚に制限する`

既存リポジトリの履歴（`085c8ee`, `5d043f4` 等）は日本語コミットメッセージが多い。ローカルな話題は日本語、英語コミュニティに見せたい変更は英語で問題ない。

コミットには `/smart-commit` を使う。機密ファイル混入チェックを通過してからコミットする。

---

## ISSUE との紐付け

- PR の body に `Closes #<issue番号>` を記載する
- マージ時に ISSUE が自動クローズされることを確認する
- ISSUE なしの PR は原則禁止（緊急 hotfix と typo 修正を除く）

---

## PR ルール

- タイトルは英語または日本語・70文字以内
- body は `.github/pull_request_template.md` に従う
- `Closes #<issue番号>` を必ず記載する
- セルフレビュー（`/review-pr`）後にマージする
- CI（lint・py_compile）が全件グリーンになるまでマージしない
- 重要度「高」の指摘が残っている場合はマージしない

---

## マージ戦略

```bash
gh pr merge <PR番号> --squash --delete-branch
```

- **Squash merge** を使う。`main` 履歴を意味のある単位に保つ
- マージ後はフィーチャーブランチを削除する
- Rebase merge・Merge commit は使わない

---

## デプロイ

- `main` への push = Render の自動ビルド/デプロイがトリガーされる
- デプロイ後は https://book-to-notion.onrender.com で起動確認
- Render 無料プランは数十秒スリープ復帰がかかる。「すぐ動かない = 故障」と早合点しない

---

## 禁止操作

- `git push --force` / `git push -f` は `main` ブランチへは絶対禁止
- `git reset --hard` は確認なしに実行しない
- `git commit --amend` は push 済みのコミットに対して行わない
- `--no-verify` でフックをスキップしない

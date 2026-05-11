Pull Request を作成する。以下の手順を厳守すること。

## 手順

1. `git status` と `git diff` で未コミットの変更を確認し、あればコミットするか確認する。
2. `git log main..HEAD --oneline` で main からの全コミットを取得する。
3. `git diff main...HEAD` で差分の全体像を把握する。
4. `git branch --show-current` で現在のブランチ名を取得し、`origin` に push されているか確認する。未 push なら `git push -u origin HEAD` を実行する。
5. 差分とコミット履歴を分析し、`.github/pull_request_template.md` のテンプレートに従い以下の形式で PR を作成する:

```bash
gh pr create --title "<70文字以内の簡潔なタイトル>" --body "$(cat <<'EOF'
## 変更の概要
<このPRで何を変更するか簡潔に説明>

## 変更の理由
<なぜこの変更が必要なのか>

## 変更内容
<具体的にどのような変更を行ったか>

## テスト方法
<どのようにテストしたか、またはテストすべきか>

例:
- ローカルで `docker compose up` を起動し http://localhost:5001 を開く
- 検証用画像をドロップして EXECUTE → NOTION を実行
- Notion 側に新規ページが作成されることを確認
- curl で各 API エンドポイントの正常系/異常系を確認

## 影響範囲
<この変更が他の機能に与える影響>
例: SSE 周りを触ったので Render 本番でのバッファリング挙動を要確認

## チェックリスト
- [ ] コードレビューを依頼した
- [ ] 動作確認を行った（ローカル / 本番）
- [ ] ドキュメントを更新した（必要に応じて）
- [ ] コミットメッセージが適切である
- [ ] 検証用画像・スクショを削除した

Closes #<issue番号>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

6. 作成後、PR の URL を報告する。

## 注意

- タイトルは英語または日本語で、変更の本質を端的に表す。70文字以内。
- body は日本語で記述する。
- 全コミットの内容を反映する。最新コミットだけを見ない。
- ベースブランチの指定が必要な場合は `$ARGUMENTS` を使用する（デフォルト: main）。
- `Closes #<issue番号>` を必ず付ける（hotfix で ISSUE が無い場合のみ省略可）。
- Render 本番にデプロイされる変更（`render.yaml` / `Dockerfile` / `requirements.txt`）の場合、影響範囲に明記する。

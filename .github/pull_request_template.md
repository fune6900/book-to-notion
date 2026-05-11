# プルリクエスト

## 変更の概要
<!-- このPRで何を変更するか簡潔に説明してください -->

## 変更の理由
<!-- なぜこの変更が必要なのか説明してください -->

## 変更内容
<!-- 具体的にどのような変更を行ったか説明してください -->
<!-- 影響ファイル例: app.py / main.py / slide_image.py / static/index.html / Dockerfile / render.yaml -->

## テスト方法
<!-- どのようにテストしたか、またはテストすべきかを説明してください -->
<!-- 例:
- docker compose up でローカル起動 (http://localhost:5001)
- 検証用画像をドロップして EXECUTE → NOTION を実行
- Notion 側に新規ページが作成されることを確認
- curl で API 動作確認: curl -s http://localhost:5001/api/photos
-->

## 影響範囲
<!-- この変更が他の機能に与える影響について説明してください -->
<!-- Render 本番デプロイへの影響、Gemini/Notion API 呼び出しへの影響など -->

## チェックリスト
- [ ] `python3 -m py_compile app.py main.py slide_image.py` が成功する
- [ ] ローカルで動作確認した
- [ ] 検証用画像・スクショを削除した（`photos/` / ルート直下）
- [ ] `.env` / `credentials.json` を含めていない
- [ ] コミットメッセージが規約に従っている

Closes #

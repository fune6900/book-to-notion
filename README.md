# BOOK TO NOTION

> 技術書の写真を撮るだけで、Gemini AI が解説ページを自動生成して Notion に保存するツール

```
📸 写真をドラッグ＆ドロップ
        ↓
🤖 Gemini Vision API が内容を解析
        ↓
📒 Notion にページが自動生成される
```

**🌐 公開URL**: https://book-to-notion.onrender.com

---

## 使い方（Web UI）

ブラウザで公開URLを開き、以下の3ステップで使えます。

1. 技術書のページを撮影した写真（JPG / PNG / HEIC）をドロップゾーンにドラッグ＆ドロップ
2. **▶ EXECUTE → NOTION** ボタンをクリック
3. ログにページタイトルが流れ、Notion にページが自動生成される

---

## ローカルで動かす（Docker）

### 1. API キーの取得

**Gemini API キー**
1. https://aistudio.google.com/app/apikey にアクセス
2. 「Create API key」をクリックしてコピー

**Notion API キー**
1. https://www.notion.so/my-integrations にアクセス
2. 「+ New integration」→ 名前（例: book-to-notion）を入力して作成
3. 「Internal Integration Token」をコピー

**Notion データベース ID**
1. Notion でページを保存したいデータベースを開く
2. URL をコピー: `https://www.notion.so/xxxx/{DATABASE_ID}?v=...`
3. `DATABASE_ID` の部分（32文字）をコピー
4. データベースの右上「…」→「Connections」→ 作った Integration を追加

### 2. .env ファイルの作成

```bash
cp .env.example .env
```

`.env` を開いて3つのキーを貼り付ける：

```
GEMINI_API_KEY=AIza...
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. 起動

```bash
docker compose up
```

ブラウザで http://localhost:5001 を開く。

---

## Render へのデプロイ

このリポジトリは `render.yaml` を含んでいるため、ワンクリックでデプロイできます。

1. [Render](https://render.com) でアカウントを作成し、このリポジトリを連携
2. **New → Web Service** → `fune6900/book-to-notion` を選択
3. Language: **Docker** / Branch: **main** / Plan: **Free** を確認
4. Environment Variables に以下を追加：
   - `GEMINI_API_KEY`
   - `NOTION_API_KEY`
   - `NOTION_DATABASE_ID`
5. 「Deploy Web Service」をクリック

デプロイ後、`https://book-to-notion.onrender.com` で公開されます。

> **スリープ対策**: 無料プランは一定時間アクセスがないとスリープします。[UptimeRobot](https://uptimerobot.com) に URL を登録して5分ごとに監視すると常時起動になります。

---

## フォルダ構成

```
book_to_notion/
├── app.py               # Flask Web サーバー（UI・API）
├── main.py              # Gemini → Notion 変換コア
├── slide_image.py       # スライド画像処理
├── static/
│   ├── index.html       # サイバーパンク Web UI
│   ├── favicon.ico      # ファビコン（マルチサイズ）
│   ├── favicon-32.png
│   ├── apple-touch-icon.png  # iOS ホーム画面アイコン
│   └── icon-192.png     # Android / PWA アイコン
├── render.yaml          # Render デプロイ設定
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                 # APIキー（Git に含めないこと）
├── .env.example         # テンプレート
└── photos/              # アップロード写真の一時保存先
```

---

## Notion ページの構成

各ページには以下が自動生成されます：

| セクション | 内容 |
|---|---|
| 💡 要点 | そのスライドの要点を1〜2文で |
| 📖 解説 | 初学者向けの詳細解説（300〜500文字） |
| ✅ キーポイント | 覚えるべきポイントの箇条書き |
| 💻 コード例 | 関連するJavaScriptコード（あれば） |

---

## トラブルシューティング

**`.env` が読み込まれない**
→ `.env` ファイルが `docker-compose.yml` と同じフォルダにあるか確認

**`APIResponseError` (Notion)**
→ データベースに Integration が追加されているか確認（セットアップ手順1の最後）

**`photos/` に画像がないと言われる**
→ `photos/` フォルダ自体が存在するか確認: `mkdir -p photos`

**JSON パース失敗**
→ Gemini のレスポンスが不安定な場合があります。再実行してください

**Render デプロイ後に 503 エラー**
→ 無料プランのスリープ中です。初回アクセスから約30秒待つと起動します

# book_to_notion

技術書の写真 → Gemini Vision API → Notion ページ自動生成スクリプト

```
📸 photos/ に写真を入れる
      ↓
docker compose up
      ↓
🎉 Notion にページが自動生成される
```

---

## セットアップ（初回のみ）

### 1. API キーの取得

**Gemini API キー**
1. https://aistudio.google.com/app/apikey にアクセス
2. 「Create API key」をクリックしてコピー

**Notion API キー**
1. https://www.notion.so/my-integrations にアクセス
2. 「+ New integration」→ 名前（例: book-to-notion）を入力して作成
3. 「Internal Integration Token」をコピー

**Notion データベース ID**
1. Notionでスライドを保存したいデータベースを開く
2. URLをコピー: `https://www.notion.so/xxxx/{DATABASE_ID}?v=...`
3. `DATABASE_ID` の部分（32文字）をコピー
4. そのデータベースの右上「…」→「Connections」→ 作ったIntegrationを追加

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

### 3. イメージをビルド（初回のみ）

```bash
docker compose build
```

---

## 毎日の使い方

```bash
# 1. 今日の写真を photos/ フォルダに入れる
cp ~/Downloads/IMG_*.jpg ./photos/

# 2. 実行
docker compose up

# 3. 終わったら photos/ を空にしておく（任意）
rm ./photos/*
```

### 実行例

```
book_to_notion-1  | 📸 25 枚の画像を読み込みます...
book_to_notion-1  |   ✓ IMG_001.jpg
book_to_notion-1  |   ✓ IMG_002.jpg
book_to_notion-1  |   ...
book_to_notion-1  |
book_to_notion-1  | 🤖 Gemini に送信中...
book_to_notion-1  | ✅ 8 スライドを生成しました
book_to_notion-1  |
book_to_notion-1  | 📒 Notion にページを作成中...
book_to_notion-1  |   📝 [1] 変数とデータ型
book_to_notion-1  |   📝 [2] 関数の基本
book_to_notion-1  |   ...
book_to_notion-1  |
book_to_notion-1  | 🎉 完了！ 8 ページを Notion に保存しました
```

---

## フォルダ構成

```
book_to_notion/
├── main.py              # メインスクリプト
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                 # APIキー（Gitに含めないこと）
├── .env.example         # テンプレート
├── .dockerignore
└── photos/              # ここに今日の写真を入れる（空でOK）
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
→ データベースにIntegrationが追加されているか確認（セットアップ手順1の最後）

**`photos/` に画像がないと言われる**
→ `photos/` フォルダ自体が存在するか確認: `mkdir -p photos`

**JSONパース失敗**
→ Geminiのレスポンスが不安定な場合があります。`docker compose up` を再実行

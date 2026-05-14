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

> ⚠️ **罠注意**: Notion の URL には **DB ID** と **View ID** の2つが含まれる。混同すると `Could not find database` や `is a page, not a database` で弾かれる。

1. Notion でページを保存したいデータベースを開く
   - インライン DB（ページ内に埋め込み）の場合は右上「⋮」→「ページとして開く」でフルページ表示にする
2. ブラウザの URL は以下の形式になる:
   ```
   https://www.notion.so/<workspace>/<DATABASE_ID>?v=<VIEW_ID>
                                     ↑ コレ(32文字)         ↑ ?v= 以降は View ID（使わない）
   ```
3. **`?v=` より前**の 32 文字（または 8-4-4-4-12 形式の UUID）が `NOTION_DATABASE_ID`
4. データベースの右上「⋯」→「接続」→「接続を追加」→ 作った Integration を選んで接続

設定が正しいかは以下で検証できる。`"object": "database"` が返れば成功:

```bash
curl -s "https://api.notion.com/v1/databases/${NOTION_DATABASE_ID}" \
  -H "Authorization: Bearer ${NOTION_API_KEY}" \
  -H "Notion-Version: 2022-06-28" | python3 -m json.tool | head -5
```

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

このリポジトリは `render.yaml` を含んでいるため、Blueprint からまとめてデプロイできる。

1. [Render](https://render.com) でアカウントを作成し、このリポジトリを連携
2. **New → Blueprint** → `fune6900/book-to-notion` を選択
3. `render.yaml` が読み込まれ、サービス名・Region (`oregon`)・プラン (`free`) が提示される
4. Environment Variables に以下を追加:
   - `GEMINI_API_KEY`
   - `NOTION_API_KEY`
   - `NOTION_DATABASE_ID`
5. **Apply** をクリック

デプロイ後、`https://book-to-notion.onrender.com` で公開される。

### ⚠️ Region は Oregon 等の US/EU 必須

`render.yaml` に `region: oregon` を明示している。これを Singapore 等のアジア地域に変更すると Gemini API に弾かれる:

```
google.genai.errors.ClientError: 400 FAILED_PRECONDITION.
{"error": {"code": 400, "message": "User location is not supported for the API use."}}
```

- Render が自動配置する Singapore Region は Gemini の公開 API がブロックしている
- 過去動いていた IP でもポリシー変更で塞がれることがある
- 対応 Region: `oregon`（推奨）/ `virginia` / `ohio` / `frankfurt`

**既存サービスの Region は変更不可**。`render.yaml` を編集して push しただけでは反映されないため、Dashboard で**既存サービスを削除 → 同名で再作成**する必要がある。

### ⚠️ 無料プランは Persistent Disk 非対応

`/photos` は **コンテナ内の一時 FS**。再起動・スリープ復帰で中身は消える。アップロード → EXECUTE → CLEAR の運用前提なので問題ないが、画像を長時間保持したい場合は Starter プラン以上にして `render.yaml` の `disk:` ブロックを復活させる:

```yaml
disk:
  name: photos-storage
  mountPath: /photos
  sizeGB: 1
```

> **スリープ対策**: 無料プランは一定時間アクセスがないとスリープする。[UptimeRobot](https://uptimerobot.com) に URL を登録して5分ごとに監視すると常時起動になる。

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
└── photos/              # アップロード写真の一時保存先（Render 本番では揮発性。再起動・スリープで消える）
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

**`User location is not supported for the API use.` (Gemini, 400)**
→ Render の Region が Singapore 等の非対応地域。`render.yaml` で `region: oregon` を指定し、Dashboard で**既存サービスを削除 → 同名で再作成**する。詳細は「Render へのデプロイ」セクション参照

**`Provided database_id ... is a page, not a database.` (Notion, 400)**
→ `NOTION_DATABASE_ID` にページ ID を渡している。Notion のデータベース（インラインDBなら「ページとして開く」した状態）の URL から `?v=` 以前の 32 文字を取り直す

**`Could not find database with ID: ...` (Notion, 404)**
→ 原因は2つ:
- ID が **View ID** になっている（`?v=` 以降の値を誤って使った）。「Notion データベース ID」セクションを参照
- Integration がそのデータベースに**接続されていない**。DB の「⋯」→「接続」→「接続を追加」で API トークンを発行した Integration を追加

**`APIResponseError` (Notion, 上記以外)**
→ Notion 側のレートリミット (429) や Integration 権限不足。エラー本文のステータスコードを確認

**`photos/` に画像がないと言われる**
→ `photos/` フォルダ自体が存在するか確認: `mkdir -p photos`

**Render 本番でアップロードした画像が消える**
→ 仕様。無料プランは Persistent Disk 非対応で `/photos` はコンテナ内一時 FS。再起動・スリープ復帰で消える。Starter プラン以上にすれば永続化可能

**JSON パース失敗**
→ Gemini のレスポンスが不安定な場合がある。再実行する

**Render デプロイ後に 503 エラー**
→ 無料プランのスリープ中。初回アクセスから約30秒待つと起動する

蒐集のメイド（sub-agent-knowledge）を起動し、Gemini プロンプト・Notion ブロック構造・Render 運用ノウハウを Markdown 形式でローカルに保存し、（環境変数が設定されていれば）Notion ナレッジベースにも同期する。

## 引数

引数なしで起動した場合はマスターに以下を対話形式で確認する:

- **カテゴリ**: `gemini` / `notion` / `ops` のいずれか
- **トピック**: 例「JSON 出力の安定化」「rich_text 2000文字制限」「Render SSE バッファリング」
- **発見した事実**: 試行錯誤の結果・観測された挙動
- **再現環境**: ライブラリ・モデル・プラン名・日付
- **引用元**: 公式ドキュメント URL（あれば）

## 手順

### Phase 1: 情報収集

引数またはマスターへの確認で以下を収集:

```
category: gemini | notion | ops
topic: <トピック名>
conclusion: <3行以内の要点>
background: <なぜこの知見が必要になったか>
detail:
  - 具体的な挙動・コード例・設定値
versions:
  - <例: google-genai 1.0.0, gemini-2.5-pro, notion-client 2.2.1, Render Free>
sources:
  - <公式ドキュメントURL>
  - <試した日付・コミットハッシュ>
related:
  - <他のナレッジファイルへのリンク>
```

### Phase 2: 重複チェック

1. `Glob` で `.claude/knowledge-base/<category>/` の既存ファイルを確認
2. 同名トピックや関連トピックがあれば `Read` で内容を確認
3. 既存エントリと矛盾する場合はマスターに確認（追記/上書き/スキップ）

### Phase 3: Markdown ファイルへの保存

1. カテゴリディレクトリが存在しなければ `Bash` で作成:
   ```bash
   mkdir -p .claude/knowledge-base/<category>
   ```
2. トピック名を kebab-case に変換（例: "JSON 出力の安定化" → `json-output-stability`）
3. `.claude/knowledge-base/<category>/<topic>.md` に書き込む
   - 存在しない場合: `Write` で新規作成
   - 存在する場合: `Edit` で末尾に追記
4. フォーマット:

```markdown
# <トピック名>

**カテゴリ**: gemini | notion | ops
**更新日**: YYYY-MM-DD
**バージョン**: <例: google-genai 1.0.0, gemini-2.5-pro>

## 結論

<3行以内で要点>

## 背景

<なぜこの知見が必要になったか・遭遇した問題>

## 詳細

<具体的な挙動・コード例・設定値>

```python
# コード例があれば
```

## 引用元

- <公式ドキュメントURL>
- <試した日付・コミットハッシュ>

## 関連

- <他のナレッジファイルへのリンク>

---
```

### Phase 4: Notion へのページ作成（任意）

「BOOK TO NOTION 運用ナレッジ」用の Notion データベースが整備されていれば実行する。

**前提**: 環境変数 `NOTION_KNOWLEDGE_DATA_SOURCE_ID` が設定されていること。
未設定なら**スキップ**し、「Notion 同期はスキップした（環境変数未設定）」とマスターに報告する。

設定済みの場合:
1. `mcp__notion__notion-search` で「BOOK TO NOTION 運用ナレッジ」を検索しデータソース ID を取得（環境変数優先）
2. `mcp__notion__notion-create-pages` で新規ページを作成:
   - `parent.type`: `data_source_id`
   - `parent.data_source_id`: `NOTION_KNOWLEDGE_DATA_SOURCE_ID`
   - `properties.名前`: `<カテゴリ>: <トピック名>`
   - `content`: Phase 3 と同内容を Notion Markdown 形式で記述

### Phase 5: 完了報告

```
## ナレッジ保存完了

- **ローカル**: `.claude/knowledge-base/<category>/<topic>.md`
- **Notion**: <ページURL> / スキップ（環境変数未設定）
- **カテゴリ**: <category>
- **トピック**: <topic>

### 要約
<結論を1〜3行で>
```

## 注意

- 情報の信頼性をマスターに確認してから保存する
- 同名エントリが既に存在する場合は新規作成せずマスターに確認する
- Notion への作成は環境変数 `NOTION_KNOWLEDGE_DATA_SOURCE_ID` の値を使用する（未設定ならローカル保存のみ）
- バージョン情報（ライブラリ・モデル）を必ず記録する（時間で挙動が変わるため）
- 古着・ファッション関連のナレッジ依頼が来た場合は、本プロジェクトのスコープ外として丁寧に断る（過去にこのコマンドは古着用だったが、現在は Gemini/Notion/運用専任）

# BOOK TO NOTION 運用ナレッジベース

`/knowledge-update` コマンドで自動的に追記される、Gemini プロンプト・Notion ブロック構造・Render 運用に関する経験則の置き場。

## 構造

```
knowledge-base/
├── README.md            — このファイル
├── gemini/              — Gemini Vision API のプロンプト設計・JSON 安定化等
├── notion/              — Notion API のブロックスキーマ・rich_text 制限等
└── ops/                 — Render / Docker / SSE の運用ノウハウ
```

## 担当エージェント

蒐集のメイド（`sub-agent-knowledge`）。詳細は `@.claude/agents/sub-agent-knowledge.md` を参照。

## 記録ルール

- バージョン情報（ライブラリ・モデル・プラン）を必ず明記する（時間で挙動が変わるため）
- 引用元（公式ドキュメント URL・試した日付・コミットハッシュ）を必ず添える
- 「経験的に〜」だけは禁止。再現できる事実のみを書く
- 古着・ファッション関連は対象外（過去の DIG プロジェクトの名残）

## Notion 同期先（任意）

環境変数 `NOTION_KNOWLEDGE_DATA_SOURCE_ID` が設定されていれば、`/knowledge-update` 実行時に Notion にも同期される。
未設定の場合はローカル Markdown のみ保存される。

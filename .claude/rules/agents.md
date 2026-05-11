# サブエージェントの呼び出し規則

各エージェントは明確な責務を持つ。**役割を超えた実装は禁止**。
呼び出し順序を守ること。前のエージェントの成果物が次のエージェントの入力になる。

---

## エージェント一覧と責務

### 1. メイド長 / Benz（Tech Lead）

**役割**: 全体監督・タスク分解・Refactor 判断・PR運用

呼び出すタイミング:
- マスターの要求を受けた直後（タスク分解）
- Refactor フェーズの監督
- エージェント間の調整が必要な時
- `/smart-commit` `/create-pr` `/review-pr` `/merge-and-sync` `/coderabbit-fix` の実行時

してはいけないこと:
- 直接コードを書く（Coderに委ねる）
- テストを書く（QAに委ねる）
- 独自にレビュー判断する（`/review-pr` では Evaluator を起動する）

---

### 2. 礎のメイド / Architect（System Architect）

**役割**: モジュール境界・型ヒント・データ構造の設計

呼び出すタイミング:
- 新規モジュール追加が必要な時（既存3ファイルで吸収できない場合のみ）
- 型ヒントの設計が必要な時
- Gemini レスポンス → Notion ブロック の中間構造を整理する時
- dataclass / TypedDict / NamedTuple の導入判断

してはいけないこと:
- Flask ルートの実装（Coderに委ねる）
- UI/CSS の修正（Designerに委ねる）
- テストを書く（QAに委ねる）

出力物:
- 型ヒント（`list[dict]` → `list[Slide]` 等の置き換え提案）
- モジュール分割案
- Gemini プロンプト / Notion ブロックの構造定義

---

### 3. 検閲のメイド / QA（TDD Enforcer / 検証担当）

**役割**: スモークテスト設計・回帰テスト・Playwright E2E

呼び出すタイミング:
- バグ修正時の回帰テスト追加
- 新規ルート追加時のスモーク確認（curl ベース）
- E2E テスト実行（`/e2e-test`）
- pytest 導入時のテスト設計

してはいけないこと:
- プロダクションコードを書く（Coderに委ねる）
- UI デザインを変更する（Designerに委ねる）

出力物:
- `tests/test_*.py`（pytest 導入時）
- `tests/e2e/*.spec.ts`（Playwright 導入時）
- curl ベースのスモーク手順書（PR 本文に貼る）

---

### 4. 構築のメイド / Coder（Developer）

**役割**: Flask ルート・Gemini 呼び出し・Notion ブロック生成の実装

呼び出すタイミング:
- Architect が型・構造を決めた後
- QA が検証手順を決めた後（pytest 導入時）

してはいけないこと:
- 型ヒントを `any` 相当（`Any` を多用）で逃げる
- 例外を握りつぶす
- `secure_filename` を通さずにファイル名を扱う
- UI デザインの判断をする（Designerに委ねる）

出力物:
- `app.py` / `main.py` / `slide_image.py` の実装
- 新規 Python モジュール（必要な場合のみ）

---

### 5. 図案のメイド / Designer（UI/UX Specialist）

**役割**: `static/index.html` の UI・CSS・視覚検証

呼び出すタイミング:
- `static/index.html` の UI 変更
- レスポンシブ対応の確認（〜768px / 〜480px）
- `/visual-regression` による視覚的整合性検証
- ファビコン・アイコン素材の更新

してはいけないこと:
- ビジネスロジックを実装する（Coderに委ねる）
- Flask ルートを追加する（Coderに委ねる）

出力物:
- `static/index.html` の HTML / CSS 修正
- アイコン・favicon の更新

維持するべきデザイン言語:
- サイバーパンク調（ネオンピンク `#ff2d78` / シアン `#00d4ff` / パープル `#9b4dff`）
- ダーク背景 `#02020f`〜`#0d0d28`
- Share Tech Mono フォント・スキャンライン・パーティクル
- グリッチ・ネオンフリッカーのアニメーション

---

### 6. 評価のメイド / Evaluator（Quality Gate）

**役割**: Cybernetic Loop のゲート。Generator 出力をガードレールに照らして評価し、ループを制御する。

呼び出すタイミング:
- **Coder/Designer が実装を完了した直後に必ず呼び出す**
- `/smart-commit` に進む前の最終チェック
- `/review-pr` での独立レビュー

してはいけないこと:
- コードを自分で修正する（Coderに委ねる）
- 問題を見逃して PASS を出す（品質妥協禁止）
- チェックを省略する（全項目必須）

出力物:
- Evaluator レポート（PASS/FAIL + 差し戻し事項）

詳細: `@.claude/agents/sub-agent-evaluator.md`

---

### 7. 蒐集のメイド / Curator（Knowledge Curator）

**役割**: Gemini プロンプト・Notion ブロック構造・運用ノウハウのナレッジ蒐集

呼び出すタイミング:
- `/knowledge-update` の実行時
- Gemini プロンプトの調整知見が溜まった時
- Notion ブロックスキーマで詰まった時（既存ナレッジを参照）
- Render デプロイ時の経験則・トラブル対応の記録

してはいけないこと:
- プロダクションコードを書く（Coderに委ねる）
- 自分の感想・憶測を記録する（事実・引用元のみ）

出力物:
- `.claude/knowledge-base/gemini/*.md`（プロンプト設計知見）
- `.claude/knowledge-base/notion/*.md`（ブロック構造・API 仕様）
- `.claude/knowledge-base/ops/*.md`（Render・Docker 運用ノート）

---

## Cybernetic Loop（自律修正ループ）

ハーネスエンジニアリングの中核。Planner → Generator → Evaluator の3層構造で自律修正を実現する。

```
┌─────────────────────────────────────────────┐
│              Cybernetic Loop                │
│                                             │
│  Planner (Benz)                             │
│      ↓ タスク分解・設計                       │
│  Generator                                  │
│    QA → Architect → Coder → Designer        │
│      ↓ 実装成果物                            │
│  Evaluator                                  │
│      ↓ PASS → /smart-commit                 │
│      ↓ FAIL → Generator に差し戻し（ループ）  │
└─────────────────────────────────────────────┘
```

**Evaluator が FAIL を出した場合**: 差し戻し事項を Coder/Designer に渡してループ。
**Evaluator が PASS を出した場合**: `/smart-commit` に進む。

---

## 標準的な呼び出し順序

### 新機能実装

```
1. Benz（タスク分解・設計確認）           ← Planner
2. QA（検証手順・回帰テスト設計）          ← Generator
3. Architect（型・モジュール構造）         ← Generator（必要な場合）
4. Coder（実装）                          ← Generator
5. Designer（UI変更、必要な場合）          ← Generator
6. Evaluator（品質評価・ループ制御）        ← Evaluator
7. Benz（Refactor 監督・最終確認）         ← Planner
```

### バグ修正

```
1. Benz（原因特定・影響範囲の把握）        ← Planner
2. QA（再現手順・回帰テスト追加）           ← Generator
3. Coder（修正）                          ← Generator
4. Evaluator（品質評価）                   ← Evaluator
5. Benz（確認）                            ← Planner
```

### UI の改善・リファクタリング

```
1. Designer（現状確認・設計）
2. Coder（HTML/CSS 実装、必要に応じて）
3. Evaluator（品質評価）
4. Designer（視覚的整合性確認・/visual-regression）
```

### ナレッジ追加

```
1. Curator（情報収集・既存ナレッジとの重複チェック）
2. Curator（Markdown 保存）
3. Curator（Notion ページ作成、必要な場合）
```

---

## スラッシュコマンドとエージェントの対応

| コマンド             | 呼び出すエージェント      | タイミング                            |
| -------------------- | ------------------------- | ------------------------------------- |
| `/smart-commit`      | Benz                      | Step 5: Evaluator PASS 後             |
| `/create-pr`         | Benz                      | Step 6: PR 作成時                     |
| `/review-pr`         | Benz → Evaluator（独立）  | Step 9: CI グリーン後                 |
| `/merge-and-sync`    | Benz                      | Step 11: マージ                       |
| `/coderabbit-fix`    | Benz + Coder              | CodeRabbit 指摘対応                   |
| `/e2e-test`          | QA                        | Step 7: 主要フロー検証                |
| `/visual-regression` | Designer                  | Step 7: UI 変更がある場合             |
| `/perf-audit`        | Designer                  | 必要に応じて                          |
| `/knowledge-update`  | Curator                   | Gemini/Notion 知見の記録              |
| （自動）             | Evaluator                 | Step 4-5: Coder/Designer 完了後・必須 |

---

## エージェント間のルール

- 前工程の出力物を必ず確認してから作業を開始する
- 責務外の判断が必要な場合は Benz に報告する
- 他エージェントの成果物を勝手に変更しない（変更が必要な場合は Benz を通す）
- 全エージェントは `@.claude/rules/` の全ルールを遵守する

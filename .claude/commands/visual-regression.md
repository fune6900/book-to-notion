Playwright MCP を使用して `static/index.html` の視覚的整合性を自動検閲する。図案のメイド（Designer サブエージェント）を起動し、以下の手順を厳守すること。

## 対象
- 引数 `$ARGUMENTS` に検査対象の URL またはページパスを指定する。
- 未指定の場合は `http://localhost:5001` を対象とする。
- このプロジェクトは SPA 1ページ構成のため、デフォルトでは `/` のみが対象。

## 手順

### Phase 0: 事前確認

- ローカルサーバーが起動していなければ `docker compose up -d` または `python app.py` を促す。
- `mcp__playwright__browser_navigate` で対象 URL へ遷移する。
- `mcp__playwright__browser_console_messages` でロード時のエラー/警告を確認する。

### Phase 1: ベースライン確認（デスクトップ）

- `mcp__playwright__browser_resize` で `1280×800` に設定
- `mcp__playwright__browser_take_screenshot` でフルページキャプチャ
- `mcp__playwright__browser_snapshot` でアクセシビリティツリーと DOM 構造を取得
- 以下を確認:
  - ロゴ (`BOOK ▶ NOTION`) のネオンフリッカーが動作している
  - パーティクル背景が描画されている
  - ドロップゾーン・サムネグリッド・アクションバーのレイアウトが整っている
  - フッター (`BOOK_TO_NOTION · DOCKER · v2.0`) が表示されている

### Phase 2: インタラクティブ・ステート検証

各状態を順に操作してスクリーンショットを撮影:

1. **Default**: ページ初期表示
2. **Drop Zone Hover**: `mcp__playwright__browser_hover` でドロップゾーンにホバー（実際にドラッグオーバーする場合は `evaluate` で `dragover` イベントを発火）
3. **Help Modal Open**: `[ ? ]` ボタンをクリックしてヘルプモーダルを表示
4. **Help Modal Close**: `[ ✕ CLOSE ]` クリック後の状態
5. **Thumb Hover**: アップロード済みサムネにホバー（削除ボタン `del-btn` の表示確認）
6. **Run Button Running**: ※実 API を叩くため通常はスキップ。CSS 確認のみであれば `mcp__playwright__browser_evaluate` でクラス `running` を強制付与する:
   ```javascript
   document.getElementById("run-btn").classList.add("running");
   ```
7. **Log Panel Visible**: SSE ログパネル表示時のレイアウト

### Phase 3: レスポンシブ・ストレステスト

`mcp__playwright__browser_resize` で以下のビューポートに順次リサイズしてスクリーンショットを取得する。

| デバイス       | 幅   | 高さ |
| -------------- | ---- | ---- |
| iPhone SE      | 375  | 667  |
| iPhone 14 Pro  | 393  | 852  |
| iPad           | 768  | 1024 |
| Laptop         | 1280 | 800  |
| Full HD        | 1920 | 1080 |

各解像度で以下を確認:
- ロゴサイズが `@media (max-width: 768px)` / `(max-width: 480px)` で正しく縮小されているか
- ドロップゾーン padding がモバイルで詰まっているか
- サムネグリッドの `minmax(110px, 1fr)` / `minmax(90px, 1fr)` / `minmax(76px, 1fr)` 切り替えが効いているか
- アクションバー (`#run-btn` `#clear-btn` `#help-btn`) がスマホで縦積みになっているか
- ヘルプモーダルが画面内に収まっているか

### Phase 4: アニメーション・キーフレーム確認

`mcp__playwright__browser_evaluate` で計算済みスタイルを取得し、以下が機能しているか確認:

```javascript
getComputedStyle(document.querySelector(".logo .word-book")).animation
// 期待: neon-flicker-cyan が含まれる

getComputedStyle(document.querySelector(".panel-corner.tl")).animation
// 期待: corner-pulse が含まれる
```

- ネオンフリッカー（cyan / pink）
- パネルスキャン
- コーナーパルス
- アイコンフロート（drop-icon）
- パーティクルの描画（canvas 内 fps が極端に低くないか）

### Phase 5: コンソール・ネットワーク確認

- `mcp__playwright__browser_console_messages` でコンソール出力を取得し、error / warning を抽出
- `mcp__playwright__browser_network_requests` で 404 / 500 / 不要に重いリソースを確認
  - `static/icon-512.png` が 222KB ある点に注意（過去にすでに把握）

### Phase 6: 後始末

- 検証中に撮影したスクリーンショットをルート直下から削除する:
  ```bash
  ls -1 *.png *.jpeg 2>/dev/null
  rm *.png *.jpeg 2>/dev/null
  ```
- `static/` の本番アセット（favicon・icon-* 等）は絶対に削除しない
- Playwright ブラウザを `mcp__playwright__browser_close` で閉じる

## 報告形式

```
## 視覚的整合性 検閲報告: <対象 URL>

### 総合判定: [合格 / 要修正 / 緊急対応]

---

### Phase 1: デスクトップ表示
- ロゴ・ネオンフリッカー: 正常 / 異常
- パーティクル: 正常 / 異常（fps: XX）
- 全体レイアウト: 正常 / 異常

### Phase 2: インタラクティブ・ステート
| 状態                | 判定  | 詳細                                  |
| ------------------- | ----- | ------------------------------------- |
| Default             | OK/NG | 所見                                  |
| Drop Zone Hover     | OK/NG | 所見                                  |
| Help Modal Open     | OK/NG | 所見                                  |
| Thumb Hover         | OK/NG | del-btn 表示遅延: XXms                |
| Run Button Running  | OK/NG | パルスアニメ周期: X.Xs                |
| Log Panel Visible   | OK/NG | scroll behavior: 正常 / カクツキあり |

### Phase 3: レスポンシブ検証
| デバイス              | 判定  | 検出された問題                  |
| --------------------- | ----- | ------------------------------- |
| iPhone SE (375px)     | OK/NG | 詳細                            |
| iPhone 14 Pro (393px) | OK/NG | 詳細                            |
| iPad (768px)          | OK/NG | 詳細                            |
| Laptop (1280px)       | OK/NG | 詳細                            |
| Full HD (1920px)      | OK/NG | 詳細                            |

### Phase 4: アニメーション
- neon-flicker-cyan: 動作 / 停止
- neon-flicker-pink: 動作 / 停止
- corner-pulse: 動作 / 停止
- icon-float: 動作 / 停止
- particle canvas: XX fps

### Phase 5: コンソール / ネットワーク
- エラー: X件（詳細）
- 警告: X件（詳細）
- 重いリソース: <ファイル>（XXX KB）

---

### 検閲指摘事項（修正命令）
1. [緊急] 具体的な問題と修正箇所（`static/index.html:XXX行` / 該当 CSS セレクタ）
2. [要対応] 具体的な問題と修正箇所
3. [推奨] 具体的な問題と修正箇所

### 修正方針
（コード変更が必要な場合、対象セレクタ・class・style プロパティの具体値まで落とし込む）
```

## 注意

- ローカルサーバーが起動していない場合は `docker compose up -d` または `python app.py` を促す
- 「なんとなく崩れている」という曖昧な報告は不可。ズレは px 単位、遅延は ms 単位で報告する
- `mcp__playwright__browser_evaluate` で `getComputedStyle` を取得し、設計値との乖離を数値で示す
- スクリーンショットで視認できた問題は、どの CSS プロパティが原因かまで特定する
- 修正提案は「色を調整しましょう」のような曖昧なものは不可。`className` の変更、CSS 変数の差し替え、具体値まで落とし込む
- デザイン言語（サイバーパンク調・CSS 変数 `--cyan` `--pink` `--purple`）からの逸脱を見逃さない

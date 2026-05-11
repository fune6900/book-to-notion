Chrome DevTools MCP を使用して BOOK TO NOTION のパフォーマンス計測・改善提案を行う。以下の手順を厳守すること。

## 対象
- 引数 `$ARGUMENTS` に計測対象の URL を指定する。未指定の場合は `http://localhost:5001`。
- 本番計測の場合は `https://book-to-notion.onrender.com`（無料プランスリープに注意）。

## 手順

1. 図案のメイド（Designer サブエージェント）を起動し、以下の計測を実行させる。

### Phase 1: Lighthouse 監査

- `mcp__chrome-devtools__navigate_page` で対象 URL へ遷移
- `mcp__chrome-devtools__lighthouse_audit` で Lighthouse 監査を実行
- Performance / Accessibility / Best Practices / SEO の各スコアを取得
- 個人ツールのため SEO スコアは参考程度でよい

### Phase 2: パフォーマンストレース

- `mcp__chrome-devtools__performance_start_trace` でトレース開始
- `mcp__chrome-devtools__navigate_page` でページをリロード
- `mcp__chrome-devtools__performance_stop_trace` でトレース停止
- `mcp__chrome-devtools__performance_analyze_insight` で分析

### Phase 3: スクリーンショット取得

- `mcp__chrome-devtools__take_screenshot` で現在の画面をキャプチャ
- レイアウト崩れや視覚的な問題がないか確認

### Phase 4: ネットワーク分析

- `mcp__chrome-devtools__list_network_requests` でネットワークリクエスト一覧を取得
- 大きなリソース、遅いリクエスト、不要なリクエストを特定
- このプロジェクトで特に確認すべき項目:
  - `static/index.html` のサイズ（インラインCSS/JSで膨らんでいる）
  - `static/icon-512.png` (222KB) — favicon としては大きすぎる可能性
  - Google Fonts (`Share Tech Mono` / `Noto Sans JP`) のロード時間
  - パーティクル canvas の再描画頻度

### Phase 5: コンソールエラー確認

- `mcp__chrome-devtools__list_console_messages` でコンソール出力を取得
- エラー・警告を抽出

### Phase 6: SSE 計測（実行時パフォーマンス）

EXECUTE ボタン押下から完了までの SSE 経路を計測する。**実 API を叩くためマスター承認後のみ実行**。

- `performance.mark()` を `mcp__chrome-devtools__evaluate_script` で仕込む
- 各 `data: ...` イベントの到達タイミングを記録
- Render 本番では Cold Start のため初回が極端に遅い点に注意

2. 計測結果を以下の形式で報告する:

```
## パフォーマンス計測結果: <対象 URL>

### Lighthouse スコア
| カテゴリ        | スコア | 判定        |
| --------------- | ------ | ----------- |
| Performance     | XX     | OK / 要改善 |
| Accessibility   | XX     | OK / 要改善 |
| Best Practices  | XX     | OK / 要改善 |
| SEO (参考)      | XX     | OK / 要改善 |

### Core Web Vitals
- **LCP (Largest Contentful Paint)**: X.X s
- **FID / INP**: XX ms
- **CLS (Cumulative Layout Shift)**: 0.XX
- **TTFB (Time to First Byte)**: XXX ms
- **FCP (First Contentful Paint)**: X.X s

### 検出された問題
- [重要度: 高/中/低] 問題の説明

### ネットワーク概要
- リクエスト数: XX
- 総転送サイズ: XXX KB
- 重いリソース上位3件:
  1. <ファイル>: XXX KB
  2. <ファイル>: XXX KB
  3. <ファイル>: XXX KB

### コンソールエラー
- （あれば記載）

### SSE 経路（実行時、該当時）
- アップロード API 応答時間: XXX ms
- Gemini 解析時間: XX s
- Notion ページ作成（1ページあたり）: XXX ms

### 改善提案
1. [優先度: 高] 具体的な改善内容 — 期待される効果
2. [優先度: 中] 具体的な改善内容 — 期待される効果
3. [優先度: 低] 具体的な改善内容 — 期待される効果

例:
- [優先度: 中] `static/icon-512.png` を WebP に変換 → 70% 削減見込み
- [優先度: 低] パーティクル数を 40 → 30 に削減 → 低スペック端末で fps 向上
- [優先度: 中] Google Fonts を `display=swap` に変更し FCP を改善

### 改善の実装案
（コード変更が必要な場合、対象ファイルと具体的な修正方針）
```

## 注意

- ローカルサーバーが起動していない場合は `docker compose up -d` または `python app.py` を促す
- モバイル・デスクトップ両方の計測が求められた場合は `mcp__chrome-devtools__emulate` でデバイスを切り替えて2回計測する
- 改善提案は具体的なコード変更レベルまで落とし込む。「画像を最適化しましょう」のような曖昧な提案は不可
- 計測値が良好（Performance 90 以上）でも、Render 無料プランのスリープ復帰時間は別問題として注記する
- 本番計測時は Render Cold Start の影響を分離して報告する（初回 vs 2回目）

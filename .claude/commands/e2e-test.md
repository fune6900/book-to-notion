検閲のメイド（QA サブエージェント）を起動し、Playwright MCP で BOOK TO NOTION の E2E テストを実行する。

## 対象
- 引数 `$ARGUMENTS` にテスト対象の URL またはフロー名を指定する。
- 未指定の場合は `http://localhost:5001` を起点に全主要フローをテストする。
- フロー名指定例: `upload`（写真アップロード）、`run`（Gemini→Notion 実行）、`delete`（削除系）

## 注意（本番系）

- Gemini / Notion を実際に叩くフロー（`/api/run`）は**コストとゴミデータが発生する**。
- 可能なら **テスト用 Notion データベース**を一時的に `.env` で指定するか、`run` フローはスキップしてマスターに任せる。
- 検証用にアップロードした `photos/*.jpg` は終了時に必ず `DELETE /api/photos` でクリアする。

## 手順

### Phase 0: 事前確認

- ローカルサーバーが起動しているか確認する:
  ```bash
  curl -s http://localhost:5001/api/photos
  ```
  起動していなければ `docker compose up -d` または `python app.py &` を促す。
- `mcp__playwright__browser_navigate` で対象 URL へ遷移し、ページが正常に表示されることを確認する。
- `mcp__playwright__browser_console_messages` でページロード時のエラーを確認する。
- エラーがある場合はテスト続行前にマスターへ報告する。

### Phase 1: 写真アップロードフロー（`upload`）

1. ドロップゾーンの存在確認（`mcp__playwright__browser_snapshot`）
2. `mcp__playwright__browser_file_upload` でテスト画像（小サイズの JPG を1〜3枚）をアップロード
3. アップロード進捗（`COMPRESSING` → `UPLOADING` → 100%）が表示されることを確認
4. サムネが表示されることを `mcp__playwright__browser_take_screenshot` で確認
5. カウントバッジが正しい枚数を表示することを確認
6. 11枚目を追加した時にアラートが出ることを確認（`mcp__playwright__browser_handle_dialog` でキャプチャ）
7. 非対応形式（`.exe` など）が無視されることを確認

**検証項目**:
- [ ] ドロップゾーンが表示されている
- [ ] ファイル選択ダイアログが開く
- [ ] アップロード進捗が表示される（圧縮 → 送信）
- [ ] サムネがグリッドに表示される
- [ ] カウントバッジが反映される
- [ ] 10枚を超えるアップロードでアラートが出る
- [ ] 非対応形式が拒否される

### Phase 2: 削除フロー（`delete`）

1. アップロード済みのサムネにホバーし、`✕` ボタンが表示されることを確認
2. `✕` をクリックして1枚削除（フェードアウトアニメーション確認）
3. `[ CLEAR ]` ボタンをクリックし、確認ダイアログ → OK で全削除
4. ドロップゾーンが空状態（`NO FILES UPLOADED`）に戻ることを確認

**検証項目**:
- [ ] 個別削除ボタンが機能する
- [ ] 削除アニメーションが再生される
- [ ] CLEAR で全削除される
- [ ] 確認ダイアログが表示される

### Phase 3: Gemini → Notion 実行フロー（`run`）【注意：実 API を叩く】

**実行前にマスターに必ず確認を取る**。コストとゴミページが発生する。

1. テスト画像をアップロード（1〜2枚）
2. `[ ▶ EXECUTE → NOTION ]` をクリック
3. ボタンが `running` 状態（パルスアニメ）になることを確認
4. SSE ログがリアルタイムで流れることを確認
   - `📸 N 枚の画像を読み込みました`
   - `🤖 Gemini に送信中...`
   - `✅ X スライドを生成しました`
   - `📒 Notion に解説ページを作成中...`
   - `🎉 完了！`
5. 完了後、ボタンが disabled 解除されることを確認
6. （手動）Notion 側で新規ページが作成されているか確認

**検証項目**:
- [ ] EXECUTE ボタンが有効化される
- [ ] SSE ログが順次表示される
- [ ] エラーログ（赤色）と完了ログ（シアン）の色分けが機能する
- [ ] 完了後にボタンが有効に戻る
- [ ] Notion にページが作成される

### Phase 4: モーダル動作（ヘルプ）

1. `[ ? ]` ボタンをクリックしてヘルプモーダルを開く
2. モーダル内の項目（MAX UPLOAD / IMAGE QUALITY / PROCESSING TIME / FILE FORMATS / CLEANUP）が表示されることを確認
3. `[ ✕ CLOSE ]` で閉じる
4. オーバーレイクリックでも閉じることを確認
5. `[ UNDERSTOOD ]` で閉じた後、localStorage に `b2n_usage_seen: 1` が保存されることを確認:
   ```javascript
   localStorage.getItem("b2n_usage_seen")
   ```

### Phase 5: 共通 UX 検証

1. **レスポンシブ**: `mcp__playwright__browser_resize` で 1280×800 / 768×1024 / 393×852 / 375×667 に切り替えてレイアウト崩れを確認
2. **ネットワークエラー**: `mcp__playwright__browser_evaluate` で `fetch` を override してエラーをシミュレートし、ハンドリングを確認
3. **コンソールエラー**: `mcp__playwright__browser_console_messages` で error / warning を取得

### Phase 6: クリーンアップ

1. テスト中にアップロードした画像を全削除（`DELETE /api/photos`）
2. Notion 側に作成されたテストページがあれば、マスターに削除を促す（自動削除はしない）
3. Playwright で開いたブラウザを `mcp__playwright__browser_close` で閉じる

## 報告形式

```
## E2E テスト 検閲報告

### 総合判定: [全件合格 / X件失敗 / 実行不能]
実行日時: <timestamp>
対象 URL: <url>

---

### Phase 1: アップロードフロー
| # | テスト項目                | 結果      | 備考         |
|---|---------------------------|-----------|--------------|
| 1 | ドロップゾーン表示        | PASS/FAIL |              |
| 2 | ファイル選択              | PASS/FAIL |              |
| 3 | 圧縮 → アップロード進捗   | PASS/FAIL | 所要: XXms   |
| 4 | サムネ表示                | PASS/FAIL |              |
| 5 | カウントバッジ            | PASS/FAIL |              |
| 6 | 10枚超過アラート          | PASS/FAIL |              |
| 7 | 非対応形式の拒否          | PASS/FAIL |              |

### Phase 2: 削除フロー
（同様）

### Phase 3: Gemini→Notion フロー
（マスターの承認後のみ実行）

### Phase 4: モーダル
（同様）

### Phase 5: 共通 UX
（同様）

---

### FAIL 一覧（修正命令）
1. [FAIL] <フロー名> > <テスト項目>
   - 期待値: <expected>
   - 実際の挙動: <actual>
   - 原因箇所（推定）: <ファイル名:行数>
   - 修正方針: <具体的な修正内容>

### クリーンアップ
- photos/ 残骸: 0件 / X件削除
- Notion ページ: マスターに削除依頼済 / 該当なし
```

## 注意

- ローカルサーバーが起動していない場合は `docker compose up -d` または `python app.py` の実行をマスターに促す
- FAIL の原因を「不明」で終わらせない。`mcp__playwright__browser_evaluate` で DOM 状態や JS エラーを掘り下げ、根本原因まで特定する
- 応答時間が500ms 超のステップは「要改善」として別途フラグを立てる
- Gemini / Notion を叩くテストはコストとゴミデータが発生する。マスターの承認なしに実行しない
- 検証用画像は終了時に必ず削除する

# API 設計ルール（Flask）

`app.py` の Flask ルートと SSE エンドポイントを対象とする。

---

## ルート一覧（現状）

| メソッド | パス                         | 用途                              |
| -------- | ---------------------------- | --------------------------------- |
| GET      | `/`                          | Web UI（`static/index.html`）     |
| GET      | `/api/photos`                | アップロード済みファイル一覧      |
| POST     | `/api/upload`                | 画像アップロード                  |
| DELETE   | `/api/photos/<filename>`     | 写真1枚削除                       |
| DELETE   | `/api/photos`                | 全写真削除                        |
| GET      | `/api/run`                   | Gemini→Notion 実行（SSE）          |
| GET      | `/api/photos/<filename>/thumb` | サムネイル配信                  |

新規エンドポイントを足す前に、既存ルートで吸収できないか検討する。

---

## レスポンス形式

JSON は **常に `jsonify(...)` で返す**。生 dict を return しない。

```python
# OK
return jsonify({"uploaded": uploaded, "count": len(uploaded)})
return jsonify({"error": "ファイルがありません"}), 400

# NG
return {"uploaded": uploaded}, 200  # dict そのまま
```

---

## ステータスコード

| 操作                       | メソッド | 成功時      | 失敗時        |
| -------------------------- | -------- | ----------- | ------------- |
| 一覧取得                   | GET      | 200         | 500 / 503     |
| 作成（アップロード）       | POST     | 200         | 400 / 413     |
| 削除                       | DELETE   | 200 (data付き) | 404         |
| SSE                        | GET      | 200 (text/event-stream) | 200 + error イベント |

DELETE は本来 204 だが、現状の実装は `{"deleted": filename}` を返すため 200 とする（既存仕様を踏襲）。

---

## SSE エンドポイント（`/api/run`）

進捗ストリーミングは SSE で実装する。WebSocket は不要。

### 必須ヘッダー

```python
return Response(generate(), mimetype="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

- `Cache-Control: no-cache` — プロキシキャッシュ防止
- `X-Accel-Buffering: no` — Render / Nginx でのバッファリング防止（**外したら本番でログが詰まる**）

### メッセージ形式

`main.run()` ジェネレータが yield する dict をそのまま JSON 化して `data: ...\n\n` で送る。

```python
{"type": "log",   "message": "📸 5 枚の画像を読み込みました"}
{"type": "log",   "message": "  ✓ image.jpg"}
{"type": "error", "message": ".env に GEMINI_API_KEY が設定されていません"}
{"type": "done",  "message": "🎉 完了！ 12 ページを Notion に保存しました"}
```

`type` は `log` / `error` / `done` の3種類。これ以外を追加する時はクライアント側 (`static/index.html` の `es.onmessage`) も更新する。

### バッファフラッシュ

`time.sleep(0.05)` を yield 間に挟む（既存実装）。Render の `text/event-stream` バッファに対する経験則。

---

## 入力バリデーション

- ファイル名: `secure_filename()` を必ず通す
- 拡張子: `IMAGE_EXTENSIONS` ホワイトリストでチェック
- 枚数: `MAX_IMAGES = 10` をサーバー側でも再確認する
- パスパラメータ（`<filename>`）: ディレクトリトラバーサル防止のため `secure_filename` で正規化

```python
@app.route("/api/photos/<filename>", methods=["DELETE"])
def delete_photo(filename):
    path = UPLOAD_DIR / secure_filename(filename)  # ← 必須
    if path.exists():
        path.unlink()
        return jsonify({"deleted": filename})
    return jsonify({"error": "ファイルが見つかりません"}), 404
```

---

## エラーハンドリング

- エラーは `{"error": "<メッセージ>"}` 形式で返す
- スタックトレース・内部パス・APIキーをレスポンスに含めない
- SSE では `{"type": "error", "message": ...}` イベントで返してから `return`（ストリームを閉じる）

```python
# OK
try:
    slides = call_gemini(images)
except ValueError as e:
    yield {"type": "error", "message": str(e)}
    return

# NG（スタックトレースをレスポンスに含める）
except Exception as e:
    return jsonify({"error": traceback.format_exc()}), 500
```

---

## CLI ジェネレータと Web 共通インターフェース

`main.run(folder: Path)` はジェネレータ。CLI でも Web SSE でも**同じインターフェース**を使う。これを崩さない。

```python
# CLI
for msg in run(folder):
    print(("❌ " if msg["type"] == "error" else "") + msg["message"])

# Web
for msg in run(UPLOAD_DIR):
    yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"
```

新規処理を足す場合も「yield する dict」のインターフェースで統一する。

---

## `/review-pr` でのチェック項目

- [ ] ルート追加時に `secure_filename` / 拡張子チェックを通しているか
- [ ] SSE 追加時に `Cache-Control: no-cache` と `X-Accel-Buffering: no` を付けているか
- [ ] エラーレスポンスにスタックトレース・APIキー・内部パスが含まれていないか
- [ ] `main.run()` のジェネレータ契約（`{"type": ..., "message": ...}`）が崩れていないか
- [ ] HTTP ステータスコードが妥当か（成功時 200、入力エラー 400、Not Found 404）

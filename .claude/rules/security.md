# セキュリティルール

`/review-pr` では必ずこのルールを照合する。違反があれば重要度「高」で差し戻す。

---

## APIキー・機密情報

- **APIキーは環境変数のみ**（`GEMINI_API_KEY` / `NOTION_API_KEY` / `NOTION_DATABASE_ID`）
- コードに直書き禁止。ログにも出さない（エラーメッセージへの混入注意）
- `.env` / `credentials.json` は `.gitignore` 済み。間違っても commit しない
- Render では Web Service の Environment Variables にセットする（`render.yaml` で `sync: false`）

```python
# OK
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    yield {"type": "error", "message": ".env に GEMINI_API_KEY が設定されていません"}
    return

# NG
client = genai.Client(api_key="AIzaSyXXXXXXXXX")
```

---

## ファイル名・パス安全性

- ユーザーアップロードのファイル名は必ず `werkzeug.utils.secure_filename()` を通す
- 拡張子チェックは `IMAGE_EXTENSIONS` ホワイトリストで。MIME だけを信用しない
- 保存先パス（`UPLOAD_DIR / filename`）はディレクトリトラバーサル防止のため `secure_filename` 必須
- `send_from_directory` は安全だが、第1引数のディレクトリを動的に変えない

```python
# OK
filename = secure_filename(f.filename)
f.save(UPLOAD_DIR / filename)

# NG
f.save(UPLOAD_DIR / f.filename)  # ../../etc/passwd 等を通す
```

---

## アップロード制限

- **画像枚数の上限**: `MAX_IMAGES = 10`（クライアント・サーバー両方で enforce）
- アップロード時に既存枚数を再カウントしてから受け入れる（クライアント側だけを信用しない）
- 拡張子以外（MIME・実際のバイト列）まで検証するかどうかは現状割愛。攻撃面を増やしたくないなら追加検討
- Flask 標準の `MAX_CONTENT_LENGTH` を `app.config` で設定するのも検討（巨大ファイルでのメモリ枯渇防止）

---

## SSE / 入力検証

- `/api/run` は `GET` だが画像は事前に POST 済みのもののみ処理する。クエリパラメータでパスを受け取らない
- `/api/photos/<filename>` 系は `secure_filename` で正規化してから扱う
- 「現在画像が `MAX_IMAGES` を超えていないか」は SSE 側でも再チェックする（クライアントを信用しない）

---

## XSS

- Web UI は静的 HTML を `send_from_directory` で返すだけ（テンプレートエンジン非使用）
- SSE のログメッセージは `JSON.parse` 後 `textContent` で表示している（`innerHTML` 禁止）
- 今後動的 HTML を返す場合は **Jinja2 の自動エスケープを切らない**

---

## CSRF / CORS

- 個人ツールのため CSRF トークンは未導入。**第三者公開する場合は導入必須**
- CORS は同一オリジン前提。設定していない（FlaskCors を入れる場合は許可ドメインを絞る）

---

## 外部 API 利用時の注意

- **Gemini レスポンスを信用しない**: `json.loads` 失敗を必ず捕捉する（`call_gemini` の `JSONDecodeError`）
- **Notion API のレートリミット**: 連続作成時は失敗時に再試行ロジックを検討（現状は順次・無制限）
- Gemini に画像と一緒に**機密ドキュメント**を投げないこと（プロンプト・画像は Google に送信される）

---

## ログ

- 例外を `print` でログ出力する場合、APIキー・トークン・ユーザーパスが含まれていないか確認する
- SSE のログメッセージにスタックトレース全文を含めない（攻撃面が広がる）

---

## 依存関係

- `pip install` で追加する前に、メンテナ・最終更新・GitHub Star を確認する
- `requirements.txt` のバージョン下限固定は緩めで OK（個人ツールのため）。脆弱性が報じられたら都度更新する

---

## `/review-pr` でのチェック項目

- [ ] APIキー・トークンがコードに直書きされていないか
- [ ] アップロードファイル名が `secure_filename` を通っているか
- [ ] `IMAGE_EXTENSIONS` 等のホワイトリストを迂回するパスがないか
- [ ] SSE / ルートで Gemini レスポンスや外部入力をそのまま信用していないか
- [ ] `.env` / `credentials.json` が差分に含まれていないか
- [ ] 新規依存パッケージが正当か（不審なパッケージでないか）

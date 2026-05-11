# コーディング規約（Python / Flask）

## Python

- Python **3.12** 前提（`Dockerfile` の `python:3.12-slim`）
- PEP 8 準拠。インデント4スペース、行長は120まで許容（黒魔術の `# noqa` は最終手段）
- **型ヒント必須**: 関数シグネチャ・公開関数の戻り値には型ヒントを付ける
- `from __future__ import annotations` は必要に応じて使用可
- 例外を握りつぶさない。最低でも `yield {"type": "error", "message": ...}` か `raise` で表に出す

```python
# OK
def load_images(folder: Path) -> list[dict]:
    files = sorted([f for f in folder.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS])
    if not files:
        raise FileNotFoundError(f"画像が見つかりません: {folder}")
    ...

# NG
def load_images(folder):  # 型なし
    try:
        ...
    except Exception:
        pass  # 黙って握りつぶす
```

---

## 命名規則

| 対象             | 規則              | 例                            |
| ---------------- | ----------------- | ----------------------------- |
| 関数・変数       | snake_case        | `create_notion_page()`        |
| 定数             | UPPER_SNAKE_CASE  | `MAX_IMAGES`, `GEMINI_PROMPT` |
| クラス           | PascalCase        | `SlideRenderer`               |
| モジュール       | snake_case        | `slide_image.py`              |
| 内部実装         | 先頭 `_`          | `_font()`                     |

---

## ファイル構造

```
book_to_notion/
├── app.py            # Flask Web サーバー（ルート定義のみ。重い処理は main.py に委譲）
├── main.py           # Gemini + Notion のコアロジック（ジェネレータで進捗 yield）
├── slide_image.py    # Pillow による画像生成ユーティリティ
└── static/           # フロントエンド（ビルドツール無し）
```

- **新規モジュールを増やす前に既存3ファイルに収まらないか検討する。** 機能ごとにファイルを分割するのは行数が400を超えてから。
- グローバルステートを増やさない。設定は `os.getenv(...)` でモジュール先頭にまとめる。
- I/O 関数（Flask ルート・CLI エントリ）と純粋ロジック（Gemini パース・Notion ブロック生成）を分けて書く。

---

## Flask ルート

- ルートは `app.py` に集約する。ビジネスロジックは `main.py` に分離する。
- レスポンスは `jsonify(...)` または `Response(..., mimetype=...)` で返す。`return dict` は使わない。
- ステータスコードは省略せず明示する（`jsonify({...}), 400`）。
- SSE エンドポイントでは `Cache-Control: no-cache` と `X-Accel-Buffering: no` を必ず付ける。

---

## Gemini / Notion 連携

- Gemini プロンプトは**モジュール先頭の定数**として宣言する（`main.py: GEMINI_PROMPT`）
- JSON パース失敗は致命的なので、再現できる情報（レスポンス先頭500文字）を例外メッセージに含める
- Notion のリッチテキスト最大長は2000文字。**1900文字でチャンク分割する**（既存実装に倣う）
- Notion ブロックは `dict` で組み立てる。専用 dataclass は不要

---

## 禁止事項

- `print()` のデバッグ残し（実装後は削除。CLI 出力は `main.py` の `if __name__ == "__main__"` 内のみ許可）
- `TODO:` コメントの放置（ISSUE 起票してから消す）
- `.env` / `credentials.json` の commit
- ベアな `except:`（最低でも `except Exception:`、できれば具体例外）
- 黒魔術的なメタプログラミング（このプロジェクトのスケールでは不要）
- ライブラリの新規追加を**理由なく**行う（`requirements.txt` は5パッケージで足りている）

---

## コメント

- **WHY** だけ書く。WHAT はコードを読めば分かる。
- 例: `# Gemini が ```json ... ``` で囲んでくることがあるので剥がす`
- 1行で済まないコメントは大抵設計が悪い。リファクタを優先する。

# テスト方針

## 基本姿勢

このプロジェクトは**個人用の小さなツール**で、現状自動テストは導入していない。

- 重厚な TDD は要求しない。3ファイルのスクリプトに pytest 100% カバレッジを敷くのは過剰
- **ただし**: 外部 API（Gemini / Notion）の挙動が変わった時のスモーク確認は必須
- 新規ロジックを足す時 / バグ修正時は、再現できる最小スクリプトを残すこと

---

## 必須となる検証（テストの代わり）

### Web UI 動作確認

`/visual-regression` または手動で確認する。最低限:

- ドラッグ&ドロップ → サムネ表示
- `EXECUTE → NOTION` → SSE のログがリアルタイムで流れる
- CLEAR で全件削除
- 10枚を超えるアップロードでアラートが出る
- 完了後 Notion に新規ページが作成されている

### CLI 動作確認

```bash
python main.py ./photos
```

`photos/` に検証用画像を置いて手元で実行。Notion 側にゴミページができることに注意（実行前に確認）

### 構文・型チェック

```bash
python3 -m py_compile app.py main.py slide_image.py
ruff check .                  # インストール済みなら
mypy app.py main.py           # インストール済みなら
```

---

## 自動テストを導入する場合

導入する場合は `pytest` を採用する。

```
tests/
├── __init__.py
├── conftest.py
├── test_main.py          # Gemini レスポンスのパース・Notion ブロック生成
├── test_app.py           # Flask クライアントでのルートテスト
└── fixtures/
    ├── gemini_ok.json    # 正常系の Gemini レスポンス
    ├── gemini_bad.json   # JSONパース失敗ケース
    └── sample.jpg        # 1px のダミー画像
```

外部 API は**必ずモック**する（実行ごとに Gemini / Notion を叩かない）:

```python
from unittest.mock import patch

@patch("main.genai.Client")
def test_call_gemini_strips_codeblock(mock_client):
    mock_client.return_value.models.generate_content.return_value.text = (
        "```json\n{\"slides\": []}\n```"
    )
    result = call_gemini([{"mime_type": "image/jpeg", "data": "", "name": "t.jpg"}])
    assert result == []
```

```python
# Flask テストクライアント
def test_upload_rejects_non_image(client, tmp_path):
    response = client.post("/api/upload", data={"files": (BytesIO(b"x"), "evil.exe")})
    assert response.json["count"] == 0
```

---

## モック方針

- **外部 API は必ずモック**: Gemini / Notion / ネットワーク I/O
- **ファイルシステムは tmp_path で本物を使う**: モックすると逆に壊れる
- **環境変数は monkeypatch**: `monkeypatch.setenv("GEMINI_API_KEY", "dummy")`

---

## テストファイル命名

- `tests/test_<対象モジュール>.py`
- 関数名は `test_<対象>_<期待される挙動>`: `test_create_notion_page_chunks_long_explanation`

---

## CI でのテスト実行

`pytest` を導入したら `.github/workflows/ci.yml` に追加する:

```yaml
- run: pip install -r requirements.txt -r requirements-dev.txt
- run: pytest -v
```

---

## `/review-pr` でのチェック項目

- [ ] 新規ロジックに対応する手動検証手順が PR 本文に書かれているか
- [ ] バグ修正の場合、再現条件と修正後の確認手順が明記されているか
- [ ] pytest を導入済みなら、対応するテストが追加されているか
- [ ] 検証用に置いた `*.jpg` / `*.png` がリポジトリに残っていないか

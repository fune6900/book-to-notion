"""
app.py
------
Web UI サーバー（Flask）
- ドラッグ＆ドロップで写真アップロード
- SSE でリアルタイム進捗表示
- Notion 連携実行ボタン
"""

import os
import json
import time
import threading
from pathlib import Path
from flask import Flask, request, jsonify, Response, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from main import run, IMAGE_EXTENSIONS

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="static")

UPLOAD_DIR = Path("/photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ── ルート：Web UI を返す ──────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# ── アップロード済みファイル一覧 ────────────────────────
@app.route("/api/photos", methods=["GET"])
def list_photos():
    files = sorted([
        f.name for f in UPLOAD_DIR.iterdir()
        if f.suffix.lower() in IMAGE_EXTENSIONS
    ])
    return jsonify({"files": files})

# ── 写真アップロード ────────────────────────────────────
MAX_IMAGES = 10

@app.route("/api/upload", methods=["POST"])
def upload():
    if "files" not in request.files:
        return jsonify({"error": "ファイルがありません"}), 400

    current_count = len([
        f for f in UPLOAD_DIR.iterdir()
        if f.suffix.lower() in IMAGE_EXTENSIONS
    ])

    uploaded = []
    for f in request.files.getlist("files"):
        if current_count + len(uploaded) >= MAX_IMAGES:
            break
        if Path(f.filename).suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        filename = secure_filename(f.filename)
        f.save(UPLOAD_DIR / filename)
        uploaded.append(filename)

    return jsonify({"uploaded": uploaded, "count": len(uploaded)})

# ── 写真を1枚削除 ───────────────────────────────────────
@app.route("/api/photos/<filename>", methods=["DELETE"])
def delete_photo(filename):
    path = UPLOAD_DIR / secure_filename(filename)
    if path.exists():
        path.unlink()
        return jsonify({"deleted": filename})
    return jsonify({"error": "ファイルが見つかりません"}), 404

# ── 全写真を削除 ────────────────────────────────────────
@app.route("/api/photos", methods=["DELETE"])
def clear_photos():
    for f in UPLOAD_DIR.iterdir():
        if f.suffix.lower() in IMAGE_EXTENSIONS:
            f.unlink()
    return jsonify({"cleared": True})

# ── 実行（SSE ストリーミング）──────────────────────────
@app.route("/api/run", methods=["GET"])
def run_pipeline():
    def generate():
        files = [
            f for f in UPLOAD_DIR.iterdir()
            if f.suffix.lower() in IMAGE_EXTENSIONS
        ]
        if not files:
            data = json.dumps({"type": "error", "message": "写真がアップロードされていません"})
            yield f"data: {data}\n\n"
            return

        if len(files) > MAX_IMAGES:
            data = json.dumps({"type": "error", "message": f"送信できる画像は1度に{MAX_IMAGES}枚までです。現在{len(files)}枚あります。不要な画像を削除してください。"})
            yield f"data: {data}\n\n"
            return

        for msg in run(UPLOAD_DIR):
            yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"
            time.sleep(0.05)  # バッファフラッシュのための微小な遅延

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

# ── サムネイル配信 ─────────────────────────────────────
@app.route("/api/photos/<filename>/thumb")
def thumbnail(filename):
    return send_from_directory(str(UPLOAD_DIR), secure_filename(filename))

# ── 一時デバッグ：Render egress IP と Gemini 到達確認 ────────────
# Gemini の地域制限調査用。確認後すぐに削除すること。
# API キーはレスポンスに含めない（URL クエリで送るのみ）。
@app.route("/api/debug/egress")
def debug_egress():
    import urllib.request
    import urllib.error

    out: dict = {}

    try:
        with urllib.request.urlopen("https://ipinfo.io/json", timeout=5) as r:
            out["ip_info"] = json.loads(r.read())
    except Exception as e:
        out["ip_info"] = {"error": str(e)}

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        out["gemini_check"] = "skipped: no GEMINI_API_KEY"
    else:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            with urllib.request.urlopen(url, timeout=10) as r:
                out["gemini_check"] = {"status": r.status, "ok": True}
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode()[:400]
            except Exception:
                body = ""
            out["gemini_check"] = {"status": e.code, "ok": False, "body": body}
        except Exception as e:
            out["gemini_check"] = {"error": str(e)}

    return jsonify(out)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)

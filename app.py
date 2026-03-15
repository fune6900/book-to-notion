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
@app.route("/api/upload", methods=["POST"])
def upload():
    if "files" not in request.files:
        return jsonify({"error": "ファイルがありません"}), 400

    uploaded = []
    for f in request.files.getlist("files"):
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

        for msg in run(UPLOAD_DIR):
            yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"
            time.sleep(0.05)  # バッファフラッシュのための微小な遅延

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

# ── サムネイル配信 ─────────────────────────────────────
@app.route("/api/photos/<filename>/thumb")
def thumbnail(filename):
    return send_from_directory(str(UPLOAD_DIR), secure_filename(filename))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)

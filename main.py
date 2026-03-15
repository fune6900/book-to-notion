"""
main.py
-------
指定フォルダの写真 → Gemini Vision API → Notion 自動ページ作成
CLI・Web UI 両対応（ジェネレータで進捗を yield）
"""

import os
import sys
import json
import base64
import re
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from notion_client import Client

load_dotenv()

# ── 設定 ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DB_ID   = os.getenv("NOTION_DATABASE_ID")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}

GEMINI_PROMPT = """
あなたはJavaScriptの技術書の内容を整理するエキスパートです。
添付した画像は技術書のページ写真です。

以下のJSON形式で出力してください。コードブロックや説明文は不要で、JSONのみ返してください。

{
  "slides": [
    {
      "title": "スライドのタイトル（短く明確に）",
      "slide_body": ["スライドに表示する箇条書き1（短く端的に）", "箇条書き2", "箇条書き3"],
      "summary": "このスライドの要点を1〜2文で",
      "explanation": "初学者にもわかりやすい詳細解説（300〜500文字程度）",
      "code_example": "関連するコード例があれば記載（なければ空文字）",
      "key_points": ["ポイント1", "ポイント2", "ポイント3"]
    }
  ]
}

- slide_body は実際のスライドに表示するような簡潔な箇条書き（3〜5項目）
- ページ内容を論理的なまとまりでスライドに分割し、各スライドに丁寧な解説をつけてください
"""

# ── 画像読み込み ───────────────────────────────────────
def load_images(folder: Path) -> list[dict]:
    files = sorted([
        f for f in folder.iterdir()
        if f.suffix.lower() in IMAGE_EXTENSIONS
    ])
    if not files:
        raise FileNotFoundError(f"画像が見つかりません: {folder}")
    images = []
    for f in files:
        with open(f, "rb") as img:
            data = base64.b64encode(img.read()).decode("utf-8")
        ext = f.suffix.lower().lstrip(".")
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        images.append({"mime_type": mime, "data": data, "name": f.name})
    return images

# ── Gemini 呼び出し ────────────────────────────────────
def call_gemini(images: list[dict]) -> list[dict]:
    client = genai.Client(api_key=GEMINI_API_KEY)

    contents = []
    for img in images:
        contents.append(types.Part.from_bytes(
            data=base64.b64decode(img["data"]),
            mime_type=img["mime_type"]
        ))
    contents.append(types.Part.from_text(text=GEMINI_PROMPT))

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=contents
    )
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
        return data.get("slides", [])
    except json.JSONDecodeError as e:
        raise ValueError(f"JSONパース失敗: {e}\n--- Gemini レスポンス ---\n{raw[:500]}")

# ── Notion：解説ページ作成 ─────────────────────────────
def create_notion_page(notion: Client, slide: dict, index: int) -> str:
    title       = slide.get("title", f"スライド {index + 1}")
    slide_body  = slide.get("slide_body", [])
    summary     = slide.get("summary", "")
    explanation = slide.get("explanation", "")
    code        = slide.get("code_example", "")
    points      = slide.get("key_points", [])

    children = []

    # スライド内容（テキストブロック）
    if slide_body:
        slide_text = "\n".join(f"• {b}" for b in slide_body)
        children.append({
            "object": "block", "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": slide_text}}],
                "icon": {"emoji": "🖼"},
                "color": "blue_background",
            }
        })
        children.append({"object": "block", "type": "divider", "divider": {}})

    # 要点
    if summary:
        children.append({
            "object": "block", "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": summary}}],
                "icon": {"emoji": "💡"},
                "color": "yellow_background",
            }
        })

    # 解説
    if explanation:
        children.append({
            "object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📖 解説"}}]}
        })
        for chunk in [explanation[i:i+1900] for i in range(0, len(explanation), 1900)]:
            children.append({
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]}
            })

    # キーポイント
    if points:
        children.append({
            "object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "✅ キーポイント"}}]}
        })
        for pt in points:
            children.append({
                "object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": pt}}]}
            })

    # コード例
    if code:
        children.append({
            "object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "💻 コード例"}}]}
        })
        children.append({
            "object": "block", "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": code[:1900]}}],
                "language": "javascript",
            }
        })

    notion.pages.create(
        parent={"database_id": NOTION_DB_ID},
        properties={"title": {"title": [{"type": "text", "text": {"content": title}}]}},
        children=children,
    )
    return title

# ── Notion：NotebookLM プロンプトページ作成 ───────────────
def create_prompt_page(notion: Client, slides: list[dict]) -> str:
    """
    生成したスライドのタイトル一覧をもとに、
    NotebookLM にそのままペーストできるプロンプトページを作成する。
    """
    today      = date.today().strftime("%Y-%m-%d")
    page_title = f"📋 NotebookLM スライド生成プロンプト（{today}）"
    titles     = [s.get("title", f"スライド {i+1}") for i, s in enumerate(slides)]

    # ── プロンプト本文を組み立てる ──────────────────────
    prompt_lines = [
        "以下のトピックそれぞれについて、1枚ずつスライドを作成してください。",
        "",
        "【各スライドに含める内容】",
        "・スライドタイトル（トピック名をそのまま使用）",
        "・視覚的にわかりやすい箇条書き（3〜5項目、短く端的に）",
        "・重要な概念や用語のハイライト",
        "・可能であればJavaScriptのコード例（短いもの）",
        "",
        "【デザインの方針】",
        "・対象：JavaScriptを学ぶ初学者",
        "・テーマ：ダークベース、シンプルで読みやすいレイアウト",
        "・1スライドに情報を詰め込みすぎない",
        "",
        "【生成するスライドのトピック一覧】",
    ]
    for i, t in enumerate(titles, 1):
        prompt_lines.append(f"{i}. {t}")

    prompt_lines += [
        "",
        f"合計 {len(titles)} 枚のスライドを作成してください。",
    ]
    prompt_text = "\n".join(prompt_lines)

    # ── Notion ブロックを組み立てる ──────────────────────
    children = [
        # 使い方の説明
        {
            "object": "block", "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {
                    "content": "このページのプロンプトをコピーして NotebookLM に貼り付けてください。"
                                "\nアップロード済みの技術書のソース資料をもとに、スライドを自動生成できます。"
                }}],
                "icon": {"emoji": "📌"},
                "color": "purple_background",
            }
        },
        {"object": "block", "type": "divider", "divider": {}},
        # プロンプト見出し
        {
            "object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📝 NotebookLM に貼り付けるプロンプト"}}]}
        },
        # プロンプト本文（コードブロックで囲むとコピーしやすい）
        {
            "object": "block", "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": prompt_text}}],
                "language": "plain text",
            }
        },
        {"object": "block", "type": "divider", "divider": {}},
        # トピック一覧（参照用）
        {
            "object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": f"📚 本日の解説ページ一覧（{len(titles)} 件）"}}]}
        },
    ]

    for i, t in enumerate(titles, 1):
        children.append({
            "object": "block", "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": [{"type": "text", "text": {"content": t}}]
            }
        })

    notion.pages.create(
        parent={"database_id": NOTION_DB_ID},
        properties={"title": {"title": [{"type": "text", "text": {"content": page_title}}]}},
        children=children,
    )
    return page_title

# ── メイン処理（ジェネレータ）────────────────────────────
def run(folder: Path):
    for key, name in [(GEMINI_API_KEY, "GEMINI_API_KEY"),
                      (NOTION_API_KEY,  "NOTION_API_KEY"),
                      (NOTION_DB_ID,    "NOTION_DATABASE_ID")]:
        if not key:
            yield {"type": "error", "message": f".env に {name} が設定されていません"}
            return

    try:
        images = load_images(folder)
    except FileNotFoundError as e:
        yield {"type": "error", "message": str(e)}
        return

    yield {"type": "log", "message": f"📸 {len(images)} 枚の画像を読み込みました"}
    for img in images:
        yield {"type": "log", "message": f"  ✓ {img['name']}"}

    yield {"type": "log", "message": "\n🤖 Gemini に送信中...（少し時間がかかります）"}
    try:
        slides = call_gemini(images)
    except ValueError as e:
        yield {"type": "error", "message": str(e)}
        return

    yield {"type": "log", "message": f"✅ {len(slides)} スライドを生成しました\n"}

    # 解説ページを作成
    yield {"type": "log", "message": "📒 Notion に解説ページを作成中..."}
    notion = Client(auth=NOTION_API_KEY)
    for i, slide in enumerate(slides):
        title = create_notion_page(notion, slide, i)
        yield {"type": "log", "message": f"  📝 [{i + 1}/{len(slides)}] {title}"}

    yield {"type": "done", "message": f"🎉 完了！ {len(slides)} ページを Notion に保存しました"}

# ── CLI エントリポイント ───────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python main.py <写真フォルダのパス>")
        sys.exit(1)

    folder = Path(sys.argv[1]).expanduser().resolve()
    if not folder.is_dir():
        print(f"❌ フォルダが見つかりません: {folder}")
        sys.exit(1)

    for msg in run(folder):
        prefix = "❌ " if msg["type"] == "error" else ""
        print(prefix + msg["message"])
        if msg["type"] == "error":
            sys.exit(1)

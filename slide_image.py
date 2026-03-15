"""
slide_image.py
--------------
Pillow でスライド画像（PNG）を生成する
"""

import io
import textwrap
from PIL import Image, ImageDraw, ImageFont

# ── デザイン定数 ───────────────────────────────────────
W, H      = 1200, 675
BG        = (13, 13, 32)        # 背景（ダークネイビー）
ACCENT    = (124, 106, 247)     # パープル
TITLE_COL = (255, 255, 255)     # タイトル文字（白）
BODY_COL  = (210, 210, 240)     # 本文文字（薄紫白）
NUM_COL   = (255, 255, 255)     # スライド番号
DIM_COL   = (80, 80, 120)       # フッター

FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_NORMAL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()

def generate_slide_image(title: str, bullets: list[str], index: int) -> bytes:
    """
    スライド画像を生成して PNG bytes を返す。
    """
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    f_title = _font(FONT_BOLD,   54)
    f_body  = _font(FONT_NORMAL, 33)
    f_num   = _font(FONT_BOLD,   20)
    f_foot  = _font(FONT_NORMAL, 18)

    # ── 左アクセントバー ─────────────────────────────────
    draw.rectangle([0, 0, 7, H], fill=ACCENT)

    # ── スライド番号バッジ（右上）────────────────────────
    badge_x = W - 70
    draw.rounded_rectangle([badge_x, 18, W - 18, 50],
                            radius=6, fill=ACCENT)
    draw.text((badge_x + 12, 22), f"#{index + 1}",
              font=f_num, fill=NUM_COL)

    # ── タイトル ─────────────────────────────────────────
    title_lines = textwrap.wrap(title, width=28)
    y = 72
    for line in title_lines[:2]:
        draw.text((38, y), line, font=f_title, fill=TITLE_COL)
        y += 65

    # ── 区切り線 ─────────────────────────────────────────
    y += 10
    draw.rectangle([38, y, W - 38, y + 3], fill=ACCENT)
    y += 22

    # ── 箇条書き ─────────────────────────────────────────
    for bullet in bullets[:6]:
        # ドット
        dot_y = y + 14
        draw.ellipse([38, dot_y, 50, dot_y + 12], fill=ACCENT)

        # テキスト（折り返し対応）
        wrapped = textwrap.wrap(bullet, width=52)
        for i, wline in enumerate(wrapped[:2]):
            draw.text((60, y), wline, font=f_body, fill=BODY_COL)
            y += 44
        y += 6

    # ── フッター ─────────────────────────────────────────
    draw.rectangle([0, H - 36, W, H], fill=(20, 20, 45))
    draw.text((38, H - 25), "JavaScript 技術書ノート",
              font=f_foot, fill=DIM_COL)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

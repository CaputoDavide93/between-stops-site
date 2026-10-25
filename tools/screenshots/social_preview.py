#!/usr/bin/env python3
"""Draw docs/assets/brand/icon.png (512x512) and docs/assets/social-preview.png
(1280x640) from the site's own mark and colour tokens. Metadata is stripped.

  make social
"""
from __future__ import annotations

import pathlib

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
W, H = 1280, 640
BG, SURFACE, LINE = (15, 24, 38), (23, 34, 51), (37, 50, 70)       # dark --bg, --surface, --line
TEXT, MUTED, ACCENT = (232, 237, 242), (164, 175, 188), (140, 199, 191)
PAPER = "#f7f4ee"
FONTS = ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/SFNS.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for path in FONTS:
        try:
            return ImageFont.truetype(path, size, index=1 if bold and path.endswith(".ttc") else 0)
        except OSError:
            continue
    return ImageFont.load_default()


def clean(im: Image.Image, path: pathlib.Path) -> None:
    """Save pixels only, so no text chunks or timestamps remain."""
    out = Image.new("RGB", im.size)
    out.putdata(list(im.convert("RGB").getdata()))
    out.save(path, optimize=True)


def draw_icon() -> Image.Image:
    svg = (ROOT / "assets" / "mark.svg").read_text(encoding="utf-8")
    html = (f'<body style="margin:0;background:{PAPER};width:512px;height:512px;display:flex;'
            f'align-items:center;justify-content:center"><div style="width:320px;height:320px">{svg}</div></body>')
    tmp = ROOT / "docs" / "assets" / "brand" / "_icon.png"
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 512, "height": 512})
        page.set_content(html.replace("<svg ", '<svg width="320" height="320" ', 1))
        page.screenshot(path=str(tmp))
        browser.close()
    im = Image.open(tmp).convert("RGB")
    tmp.unlink()
    clean(im, ROOT / "docs" / "assets" / "brand" / "icon.png")
    return im


def main() -> None:
    icon = draw_icon().resize((200, 200), Image.LANCZOS).convert("RGBA")
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    mask = Image.new("L", (200, 200), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 199, 199], 44, fill=255)
    im.paste(icon, (96, 96), mask)
    d.text((96, 330), "Between Stops site", font=font(80, True), fill=TEXT)
    d.text((96, 436), "Privacy policy and contact pages for an", font=font(36), fill=MUTED)
    d.text((96, 484), "app that keeps everything on your phone.", font=font(36), fill=MUTED)
    x = 96
    for chip in ("Privacy policy", "Light and dark", "No scripts or cookies", "Static HTML"):
        f = font(26)
        w = d.textlength(chip, font=f)
        d.rounded_rectangle([x, 548, x + w + 40, 596], 24, fill=SURFACE, outline=LINE)
        d.text((x + 20, 560), chip, font=f, fill=ACCENT)
        x += w + 40 + 16
    clean(im, ROOT / "docs" / "assets" / "social-preview.png")
    print("wrote docs/assets/brand/icon.png and docs/assets/social-preview.png")


if __name__ == "__main__":
    main()

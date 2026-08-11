#!/usr/bin/env python3
"""Generate DocAI promo banners (LinkedIn/OG, Twitter, Instagram square)."""
from PIL import Image, ImageDraw, ImageFont

LOGO = r"C:/Users/MSI/business-exploration/docai/assets/logo_docai_400.png"
OUT_DIR = r"C:/Users/MSI/business-exploration/docai/assets/promo"
F_ARIAL_B = r"C:/Windows/Fonts/arialbd.ttf"
F_ARIAL = r"C:/Windows/Fonts/arial.ttf"
F_CALIBRI = r"C:/Windows/Fonts/calibri.ttf"

NAVY = (13, 27, 58)
BLUE = (37, 99, 235)
CYAN = (125, 211, 252)
WHITE = (255, 255, 255)
GRAY = (226, 232, 240)
MUTED = (148, 163, 184)
GREEN = (52, 211, 153)
AMBER = (251, 191, 36)


def draw_gradient(size, top=NAVY, bottom=(23, 45, 88)):
    w, h = size
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def autofit_font(draw, text, font_path, start_size, max_width):
    size = start_size
    while size > 12:
        f = ImageFont.truetype(font_path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 1
    return ImageFont.truetype(font_path, 12)


def make_banner(size, out_path, tagline, layout="wide"):
    w, h = size
    img = draw_gradient(size)
    d = ImageDraw.Draw(img, "RGBA")

    # accent glow
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * 0.60, -h * 0.35, w * 1.30, h * 0.50], fill=(37, 99, 235, 60))
    gd.ellipse([w * 0.70, -h * 0.28, w * 1.16, h * 0.38], fill=(56, 189, 248, 40))
    img.paste(glow, (0, 0), glow)
    d.rectangle([0, h - 10, w, h], fill=BLUE)

    if layout == "square":
        # vertical stack: logo top-center -> title -> tagline -> badges -> footer
        logo_w = int(w * 0.22)
        logo_pos = (int(w / 2 - logo_w / 2), int(h * 0.06))
        title_y = h * 0.55
        tag_y = h * 0.68
        badge_y = h * 0.79
        foot_y = h * 0.93
        title_size = int(w * 0.16)
    else:
        logo_w = int(w * 0.11)
        logo_pos = (int(w * 0.07), int(h * 0.16))
        title_y = h * 0.48
        tag_y = h * 0.62
        badge_y = h * 0.72
        foot_y = h * 0.90
        title_size = int(w * 0.10) if w >= 1200 else int(w * 0.11)

    try:
        logo = Image.open(LOGO).convert("RGBA").resize((logo_w, logo_w), Image.LANCZOS)
        img.paste(logo, logo_pos, logo)
    except Exception as e:
        print("logo err", e)

    # title
    d.text((w * 0.5, title_y), "DocAI", font=ImageFont.truetype(F_ARIAL_B, title_size),
           fill=WHITE, anchor="mm")

    # tagline (auto-fit to 92% width)
    tag_font = autofit_font(d, tagline, F_CALIBRI, int(w * 0.033), int(w * 0.92))
    d.text((w * 0.5, tag_y), tagline, font=tag_font, fill=CYAN, anchor="mm")

    # badges
    small_font = ImageFont.truetype(F_CALIBRI, max(int(tag_font.size * 0.85), 14))
    b1 = "BCA  READY"
    b2 = "Mandiri . BNI . BRI  SOON"
    b1w = d.textlength(b1, font=small_font) + 48
    b2w = d.textlength(b2, font=small_font) + 48
    gap = 26
    total = b1w + b2w + gap
    x0 = w * 0.5 - total / 2
    badge_h = int(small_font.size * 1.7)
    y0 = badge_y - badge_h / 2
    d.rounded_rectangle([x0, y0, x0 + b1w, y0 + badge_h], radius=badge_h / 2, fill=(16, 185, 129, 60))
    d.rectangle([x0, y0, x0 + b1w, y0 + badge_h], outline=GREEN, width=2)
    d.text((x0 + b1w / 2, y0 + badge_h / 2), b1, font=small_font, fill=GREEN, anchor="mm")
    x1 = x0 + b1w + gap
    d.rounded_rectangle([x1, y0, x1 + b2w, y0 + badge_h], radius=badge_h / 2, fill=(251, 191, 36, 40))
    d.rectangle([x1, y0, x1 + b2w, y0 + badge_h], outline=AMBER, width=2)
    d.text((x1 + b2w / 2, y0 + badge_h / 2), b2, font=small_font, fill=AMBER, anchor="mm")

    # footer
    foot_font = ImageFont.truetype(F_CALIBRI, max(int(small_font.size * 0.72), 13))
    d.text((w * 0.5, foot_y), "rapidapi.com/oyi77/api/docai", font=foot_font, fill=GRAY, anchor="mm")
    d.text((w * 0.5, foot_y + foot_font.size * 1.15),
           "Free tier - deterministik, zero LLM cost, balance check built-in",
           font=ImageFont.truetype(F_CALIBRI, max(int(foot_font.size * 0.8), 11)),
           fill=MUTED, anchor="mm")

    img.save(out_path, "PNG")
    print("saved", out_path, img.size, "tagfont", tag_font.size)


import os
os.makedirs(OUT_DIR, exist_ok=True)

TAG = "Parse e-statement bank Indonesia -> JSON & CSV dalam detik"
make_banner((1200, 630), OUT_DIR + "/docai_banner_linkedin.png", TAG, "wide")
make_banner((1600, 900), OUT_DIR + "/docai_banner_twitter.png", TAG, "wide")
make_banner((1080, 1080), OUT_DIR + "/docai_banner_square.png", TAG, "square")
print("done")
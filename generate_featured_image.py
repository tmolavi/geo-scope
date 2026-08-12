"""
High-End 1200x630 Featured Hero Image Generator for GEO-Scope Blog Post
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_BLACK = "/home/user/fonts/fonts/ttf/Vazirmatn-Black.ttf"
FONT_BOLD = "/home/user/fonts/fonts/ttf/Vazirmatn-Bold.ttf"
FONT_SEMI_BOLD = "/home/user/fonts/fonts/ttf/Vazirmatn-SemiBold.ttf"
FONT_MEDIUM = "/home/user/fonts/fonts/ttf/Vazirmatn-Medium.ttf"


def draw_centered_text(draw, y, text, font, fill, W=1200, direction="ltr"):
    bbox = draw.textbbox((0, 0), text, font=font, direction=direction)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, y), text, fill=fill, font=font, direction=direction)
    return x, y, tw, bbox[3] - bbox[1]


def create_featured_image(out_path):
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), (10, 14, 26, 255))
    draw = ImageDraw.Draw(img)

    # 1. Dark Gradient Background
    for y in range(H):
        r = int(10 + (y / H) * 12)
        g = int(14 + (y / H) * 14)
        b = int(26 + (y / H) * 36)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # 2. Glowing Ambient Orbs
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([80, -80, 550, 400], fill=(79, 70, 229, 80))       # Indigo glow top-left
    gdraw.ellipse([700, 220, 1250, 750], fill=(147, 51, 234, 65))    # Purple glow bottom-right
    gdraw.ellipse([920, -100, 1350, 320], fill=(16, 185, 129, 55))   # Emerald glow top-right
    gdraw.ellipse([-50, 350, 400, 750], fill=(59, 130, 246, 55))     # Blue glow bottom-left
    glow = glow.filter(ImageFilter.GaussianBlur(100))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # 3. Fine Grid Lines
    grid_color = (255, 255, 255, 12)
    for x in range(0, W, 50):
        draw.line([(x, 0), (x, H)], fill=grid_color)
    for y in range(0, H, 50):
        draw.line([(0, y), (W, y)], fill=grid_color)

    # 4. Neural Nodes (Perplexity, ChatGPT, Gemini, Claude)
    nodes = [
        (130, 135, "Perplexity Sonar", (129, 140, 248)),
        (1070, 135, "ChatGPT Search", (52, 211, 153)),
        (130, 495, "Google Gemini", (96, 165, 250)),
        (1070, 495, "Claude 3.7", (192, 132, 252))
    ]
    center_x, center_y = 600, 315

    for nx, ny, label, col in nodes:
        draw.line([(nx, ny), (center_x, center_y)], fill=(*col, 75), width=2)
        draw.ellipse([nx-22, ny-22, nx+22, ny+22], fill=(*col, 40), outline=(*col, 95), width=1)
        draw.ellipse([nx-10, ny-10, nx+10, ny+10], fill=(*col, 235))
        font_node = ImageFont.truetype(FONT_SEMI_BOLD, 14)
        n_bbox = draw.textbbox((0, 0), label, font=font_node)
        nw = n_bbox[2] - n_bbox[0]
        draw.text((nx - nw // 2, ny + 26), label, fill=(226, 232, 240, 240), font=font_node)

    # 5. Central Glassmorphism Card
    card_w, card_h = 820, 440
    cx1 = (W - card_w) // 2
    cy1 = (H - card_h) // 2
    cx2 = cx1 + card_w
    cy2 = cy1 + card_h

    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(card)
    cdraw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=24, fill=(15, 23, 42, 235), outline=(99, 102, 241, 130), width=2)
    img = Image.alpha_composite(img, card)
    draw = ImageDraw.Draw(img)

    # 6. Card Content
    # A. Top Badge
    badge_text = "⟠ GEO-SCOPE RESEARCH  •  1,000 PROMPTS BENCHMARK"
    font_badge = ImageFont.truetype(FONT_BOLD, 13)
    b_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = b_bbox[2] - b_bbox[0]
    bx = (W - bw) // 2
    by = cy1 + 35
    draw.rounded_rectangle([bx - 16, by - 6, bx + bw + 16, by + 24], radius=12, fill=(99, 102, 241, 45), outline=(129, 140, 248, 120))
    draw.text((bx, by), badge_text, fill=(165, 180, 252, 255), font=font_badge)

    # B. Main Persian Title
    title_fa = "مهندسی معکوس الگوریتم‌های هوش مصنوعی"
    font_title = ImageFont.truetype(FONT_BLACK, 36)
    draw_centered_text(draw, by + 50, title_fa, font_title, (255, 255, 255, 255), W=1200, direction="rtl")

    # C. English Subtitle
    sub_en = "Generative Engine Optimization (GEO) & AI Search Visibility"
    font_sub = ImageFont.truetype(FONT_MEDIUM, 17)
    draw_centered_text(draw, by + 115, sub_en, font_sub, (148, 163, 184, 255), W=1200, direction="ltr")

    # D. Feature Chips Row (Persian RTL)
    chips = [
        "تحلیل ۱,۰۰۰ پرسش",
        "۴ موتور هوش مصنوعی",
        "گراف استنادها و ردیت",
        "Share of Model (SoM)"
    ]
    font_chip = ImageFont.truetype(FONT_MEDIUM, 13)
    chip_y = by + 175

    chip_metrics = []
    total_w = 0
    for c in chips:
        is_fa = any('\u0600' <= ch <= '\u06FF' for ch in c)
        direction = "rtl" if is_fa else "ltr"
        bbox = draw.textbbox((0, 0), c, font=font_chip, direction=direction)
        tw = bbox[2] - bbox[0]
        cw = tw + 28
        chip_metrics.append((c, tw, cw, direction))
        total_w += cw + 10
    total_w -= 10

    cur_x = (W - total_w) // 2
    for c, tw, cw, direction in chip_metrics:
        draw.rounded_rectangle([cur_x, chip_y, cur_x + cw, chip_y + 34], radius=8, fill=(30, 41, 59, 235), outline=(51, 65, 85, 255))
        tx = cur_x + (cw - tw) // 2
        draw.text((tx, chip_y + 6), c, fill=(203, 213, 225, 255), font=font_chip, direction=direction)
        cur_x += cw + 10

    # E. Divider Line
    div_y = cy2 - 62
    draw.line([cx1 + 40, div_y, cx2 - 40, div_y], fill=(51, 65, 85, 180), width=1)

    # F. Author Footer
    footer_text = "تقی مولوی (Taqi Molavi)   •   molavi.pro   •   github.com/tmolavi/geo-scope"
    font_footer = ImageFont.truetype(FONT_SEMI_BOLD, 14)
    draw_centered_text(draw, div_y + 18, footer_text, font_footer, (165, 180, 252, 255), W=1200, direction="rtl")

    # Save
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, format="PNG", quality=95)
    print(f"✓ Featured image created successfully at {out_path}")


if __name__ == "__main__":
    create_featured_image("/home/user/geo-scope/static/featured_image_geo.png")
    create_featured_image("/home/user/featured_image_geo.png")

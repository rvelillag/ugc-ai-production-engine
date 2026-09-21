import sys, os, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_cover_advanced(
    input_image_path: Path,
    headline: str,
    output_image_path: Path,
    target_width: int = 1080,
    target_height: int = 1920,
    highlight_color_hex: str = "#FFE500" # Neon viral yellow
):
    # Open and scale input image
    img = Image.open(input_image_path).convert("RGBA")
    
    # Crop / resize to 1080x1920 (9:16)
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        offset = (img.width - new_width) // 2
        img = img.crop((offset, 0, offset + new_width, img.height))
    else:
        new_height = int(img.width / target_ratio)
        offset = (img.height - new_height) // 2
        img = img.crop((0, offset, img.width, offset + new_height))

    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Font setup - Impact or Arial Black
    font_candidates = [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/ariblk.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font_path = next((p for p in font_candidates if os.path.exists(p)), None)
    if font_path is None:
        raise FileNotFoundError(
            "No se encontró ninguna fuente bold (Impact/Arial Black/Arial Bold/DejaVu Bold). "
            "Instala una o añade su ruta a font_candidates en cover_generator.py."
        )

    words = headline.strip().split()

    # Smart line splitting (max 2-3 words per line for high visual impact)
    lines = []
    if len(words) <= 3:
        lines = [headline.upper()]
    elif len(words) == 4:
        lines = [" ".join(words[:2]).upper(), " ".join(words[2:]).upper()]
    elif len(words) in [5, 6]:
        lines = [" ".join(words[:3]).upper(), " ".join(words[3:]).upper()]
    else:
        mid = len(words) // 2
        lines = [" ".join(words[:mid]).upper(), " ".join(words[mid:]).upper()]

    # Dynamic font scaling to guarantee text + generous padding never overflows screen boundaries
    max_allowed_width = int(target_width * 0.84) # 84% safe screen width
    stroke_w = 4

    font_size = 96
    while font_size >= 40:
        font = ImageFont.truetype(font_path, font_size)
        pad_x = int(font_size * 0.40)
        dummy_img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        dummy_draw = ImageDraw.Draw(dummy_img)

        fits = True
        for line in lines:
            bb = dummy_draw.textbbox((0, 0), line, font=font, stroke_width=stroke_w)
            w = bb[2] - bb[0]
            if w + (2 * pad_x) > max_allowed_width:
                fits = False
                break
        if fits:
            break
        font_size -= 2

    font = ImageFont.truetype(font_path, font_size)
    pad_x = int(font_size * 0.40)
    pad_y = int(font_size * 0.26)
    line_gap = int(font_size * 0.20)

    dummy_img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy_img)

    line_metrics = []
    total_height = 0
    for line in lines:
        bb = dummy_draw.textbbox((0, 0), line, font=font, stroke_width=stroke_w)
        x0, y0, x1, y1 = bb
        w = x1 - x0
        h = y1 - y0
        box_h = h + (2 * pad_y)
        box_w = w + (2 * pad_x)
        line_metrics.append({
            "line": line,
            "x0": x0,
            "y0": y0,
            "w": w,
            "h": h,
            "box_w": box_w,
            "box_h": box_h
        })
        total_height += box_h

    total_height += (len(lines) - 1) * line_gap

    # Position in center (40% vertical for Instagram Reels grid safe preview)
    start_box_y = int(target_height * 0.40 - total_height / 2)
    center_x = target_width // 2

    overlay = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    curr_box_y = start_box_y
    for idx, lm in enumerate(line_metrics):
        box_x0 = center_x - lm["box_w"] // 2
        box_x1 = center_x + lm["box_w"] // 2
        box_y0 = curr_box_y
        box_y1 = curr_box_y + lm["box_h"]

        is_first = (idx == 0)
        border_color = (255, 229, 0, 255) if is_first else (255, 255, 255, 220)

        # High-contrast rounded rectangle sticker badge
        overlay_draw.rounded_rectangle(
            [box_x0, box_y0, box_x1, box_y1],
            radius=18,
            fill=(0, 0, 0, 235),
            outline=border_color,
            width=4
        )

        # Exact mathematical offset to center glyph bounding box inside the rectangle
        text_x = box_x0 + pad_x - lm["x0"]
        text_y = box_y0 + pad_y - lm["y0"]

        text_color = (255, 229, 0, 255) if is_first else (255, 255, 255, 255)

        # Drop shadow
        overlay_draw.text((text_x + 3, text_y + 3), lm["line"], font=font, fill=(0, 0, 0, 200))

        # Main text with stroke
        overlay_draw.text(
            (text_x, text_y),
            lm["line"],
            font=font,
            fill=text_color,
            stroke_width=stroke_w,
            stroke_fill=(0, 0, 0, 255)
        )

        curr_box_y += lm["box_h"] + line_gap

    img = Image.alpha_composite(img, overlay)

    # Save
    output_image_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_image_path, "JPEG", quality=95)
    print(f"Generated High-Impact Cover: {output_image_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--headline", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    generate_cover_advanced(Path(args.input), args.headline, Path(args.output))

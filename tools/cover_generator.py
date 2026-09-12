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
    font_path = "C:/Windows/Fonts/impact.ttf"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/ariblk.ttf"
    
    # Dynamic font sizing based on headline length
    words = headline.strip().split()
    if len(words) <= 3:
        font_size = int(target_height * 0.058) # ~110px
    elif len(words) <= 5:
        font_size = int(target_height * 0.052) # ~100px
    else:
        font_size = int(target_height * 0.046) # ~88px

    font = ImageFont.truetype(font_path, font_size)
    dummy_draw = ImageDraw.Draw(img)

    # Smart line splitting (max 2-3 words per line for high visual weight)
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

    # Trigger words that get neon yellow highlight
    trigger_words = [
        "STOP", "NEVER", "BABY OIL", "OIL", "BAKING SODA", "EGG", "RAW EGG",
        "THINNING", "BALD", "ROOTS", "REGROW", "SECRET", "RUINING", "SHOCKING",
        "TRICK", "MISTAKE", "HAIR LOSS", "DENSITY", "CORTISOL", "FASTER", "DO THIS"
    ]

    # Calculate bounding boxes
    line_bboxes = [dummy_draw.textbbox((0, 0), l, font=font) for l in lines]
    line_widths = [bb[2] - bb[0] for bb in line_bboxes]
    line_heights = [bb[3] - bb[1] for bb in line_bboxes]
    
    line_spacing = int(font_size * 0.22)
    total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing
    max_line_width = max(line_widths)

    # Position in center (42% vertical for Instagram Reels grid safe preview)
    start_y = int(target_height * 0.42 - total_text_height / 2)

    # Draw individual high-contrast sticker badges per line (MrBeast / Hormozi style)
    overlay = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    pad_x = int(font_size * 0.35)
    pad_y = int(font_size * 0.16)

    curr_y = start_y
    for i, line in enumerate(lines):
        lw = line_widths[i]
        lh = line_heights[i]
        lx = (target_width - lw) // 2

        box = [
            lx - pad_x,
            curr_y - pad_y,
            lx + lw + pad_x,
            curr_y + lh + pad_y + 4
        ]
        
        # Black sticker background with slight angle or solid presence
        overlay_draw.rounded_rectangle(
            box,
            radius=16,
            fill=(0, 0, 0, 235),
            outline=(255, 229, 0, 255) if i == 0 else (255, 255, 255, 200),
            width=3
        )
        curr_y += lh + line_spacing

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Render text with rich colors & outline
    curr_y = start_y
    for i, line in enumerate(lines):
        lw = line_widths[i]
        lh = line_heights[i]
        lx = (target_width - lw) // 2

        # Check if line has trigger keywords
        is_highlight = any(tw in line for tw in trigger_words) or (i == 0 and len(lines) > 1)
        text_color = (255, 229, 0, 255) if is_highlight else (255, 255, 255, 255)

        # Drop shadow
        draw.text((lx + 4, curr_y + 4), line, font=font, fill=(0, 0, 0, 255))
        
        # Stroke + Fill
        draw.text(
            (lx, curr_y),
            line,
            font=font,
            fill=text_color,
            stroke_width=3,
            stroke_fill=(0, 0, 0, 255)
        )
        curr_y += lh + line_spacing

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

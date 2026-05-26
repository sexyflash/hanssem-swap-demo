"""밀로 product references → smart sheet 합성.

GIF 3 frames + visual annotations를 1장 composite로 묶음 (3차 fallback에 사용).
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
USER_DIR = HERE / "user_products/milo_777039"
OUT = USER_DIR / "smart_sheet.jpg"

frames = sorted((USER_DIR / "gif_frames").glob("frame_*.jpg"))[:3]
assert len(frames) == 3

# load
imgs = [Image.open(f).convert("RGB") for f in frames]
# resize to same height
target_h = 580
imgs_r = [im.resize((int(target_h * im.width / im.height), target_h)) for im in imgs]
widths = [im.width for im in imgs_r]
total_w = sum(widths) + 20 * (len(imgs_r) + 1)  # 20px gap
sheet_h = target_h + 80  # space for labels

sheet = Image.new("RGB", (total_w, sheet_h), (255, 255, 255))
draw = ImageDraw.Draw(sheet)

# title
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 22)
    font_label = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 14)
except OSError:
    font_title = ImageFont.load_default()
    font_label = ImageFont.load_default()

draw.text(
    (20, 12),
    "MILO 패브릭소파 2인용 — Multi-angle Reference (GIF 360°)",
    fill=(20, 20, 20), font=font_title,
)

# paste frames with labels
x = 20
labels = ["3/4 front", "side profile", "back/angle"]
for im, label in zip(imgs_r, labels):
    sheet.paste(im, (x, 50))
    # label below
    draw.text((x + 8, 50 + target_h + 6), label, fill=(80, 80, 80), font=font_label)
    x += im.width + 20

sheet.save(OUT, quality=92)
print(f"wrote {OUT} ({sheet.size})")

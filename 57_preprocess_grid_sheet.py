"""전처리 — milo strict95 패턴 smart sheet + product grid + 모든 use_product 활용.

strict95 패턴 (5th/experiment/build_smart_sheet.py 차용):
- 헤더 + 다각도 3컷 + PRESERVE/NEVER 박스
- "제품 원형 보존 레퍼런스" — 이미지 첨부 시 맨 뒤에 항상 함께 보냄

추가 전처리:
- product_grid.jpg: 다각도 + 컬러 variants
- material_close.jpg: 소재 close-up
- color_chart.jpg: 컬러 grid

출력: user_products/milo_777039/preprocessed/
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
USER_DIR = HERE / "user_products/milo_777039"
USE_PROD = USER_DIR / "use_product"
PREP = USER_DIR / "preprocessed"
PREP.mkdir(exist_ok=True)

# fonts
_FONTS = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]


def _font(size):
    for p in _FONTS:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fit(path, w, h):
    img = Image.open(path).convert("RGB")
    img.thumbnail((w, h), Image.Resampling.LANCZOS)
    return img


def _paste_center(canvas, img, cx, top, box_h):
    x = cx - img.width // 2
    y = top + (box_h - img.height) // 2
    canvas.paste(img, (x, y))


# ============= MILO SMART SHEET (strict95 패턴) =============
print("building milo_smart_sheet.jpg (strict95 패턴)...")

W, H = 1640, 1340
MARGIN = 40
BG = (255, 255, 255)
INK = (28, 28, 30)
GRAY = (110, 110, 115)
GREEN, GREEN_BG = (34, 139, 76), (233, 246, 238)
RED, RED_BG = (198, 56, 48), (250, 235, 234)
LINE = (220, 220, 224)

f_title = _font(38)
f_sub = _font(22)
f_sec = _font(26)
f_label = _font(20)
f_body = _font(22)

canvas = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(canvas)

# Header
d.text((MARGIN, 30), "MILO 패브릭소파 2인용", font=f_title, fill=INK)
d.text((MARGIN, 78), "PRODUCT FIDELITY SHEET · 제품 원형 보존 레퍼런스",
       font=f_sub, fill=GRAY)
d.line([(MARGIN, 120), (W - MARGIN, 120)], fill=LINE, width=2)

# 다각도 3컷
photos = [
    (USE_PROD / "p08_frame_01.jpg", "FRONT · 정면"),
    (USE_PROD / "p08_frame_02.jpg", "SIDE A · 측면"),
    (USE_PROD / "p08_frame_03.jpg", "ANGLE · 각도"),
]
cell_w = (W - 2 * MARGIN - 2 * 45) // 3
box_h = 430
for i, (fpath, label) in enumerate(photos):
    if not fpath.exists():
        continue
    cx = MARGIN + cell_w // 2 + i * (cell_w + 45)
    img = _fit(fpath, cell_w, box_h)
    _paste_center(canvas, img, cx, 145, box_h)
    bb = d.textbbox((0, 0), label, font=f_label)
    d.text((cx - (bb[2] - bb[0]) // 2, 145 + box_h + 8),
           label, font=f_label, fill=GRAY)

d.line([(MARGIN, 640), (W - MARGIN, 640)], fill=LINE, width=2)

# 하단 좌: 컬러 variants 3컷 (실측 도면 자리 대체 — milo는 도면 없으니)
d.text((MARGIN, 662), "COLOR VARIANTS · 컬러 옵션 3종", font=f_sec, fill=INK)
variants = [
    (USE_PROD / "p08_frame_01.jpg", "오트밀"),
    (USE_PROD / "p08_frame_01_color_2.webp", "라이트그레이"),
    (USE_PROD / "p08_frame_01_color_3.webp", "더스티로즈"),
]
v_w = 200
v_h = 180
v_gap = 14
for i, (fpath, name) in enumerate(variants):
    if not fpath.exists():
        continue
    x = MARGIN + i * (v_w + v_gap)
    img = _fit(fpath, v_w, v_h)
    canvas.paste(img, (x + (v_w - img.width) // 2, 705))
    d.text((x + 4, 705 + v_h + 8), name, font=f_label, fill=GRAY)

# 컬러 swatch 3 (라벨 아래)
swatch_y = 705 + v_h + 50
for i, sw in enumerate(["color_01.png", "color_02.png", "color_03.png"]):
    swp = USE_PROD / sw
    if not swp.exists():
        continue
    x = MARGIN + i * (v_w + v_gap)
    sim = _fit(swp, v_w, 80)
    canvas.paste(sim, (x + (v_w - sim.width) // 2, swatch_y))

# 우측 PRESERVE 박스
panel_x = MARGIN + 3 * (v_w + v_gap) + 20
panel_w_end = W - MARGIN
d.rounded_rectangle([panel_x, 700, panel_w_end, 985], radius=14,
                    fill=GREEN_BG, outline=GREEN, width=2)
d.text((panel_x + 24, 716), "PRESERVE · 반드시 유지", font=f_sec, fill=GREEN)
preserve = [
    "2인용 STRICT — 좌석수 변경 X",
    "패브릭 (linen-look matte) — 가죽 X",
    "thin slim 직각 팔걸이",
    "loose puffy 등쿠션 2개",
    "slim cylindrical 매트블랙 다리 5개 (모서리 4 + 중앙 1)",
    "좌방석 MEDIUM SOFT · 등쿠션 SOFT",
]
for i, t in enumerate(preserve):
    y = 760 + i * 36
    d.ellipse([panel_x + 26, y + 7, panel_x + 38, y + 19], fill=GREEN)
    d.text((panel_x + 52, y), t, font=f_body, fill=INK)

# NEVER 박스
d.rounded_rectangle([panel_x, 1005, panel_w_end, 1230], radius=14,
                    fill=RED_BG, outline=RED, width=2)
d.text((panel_x + 24, 1021), "NEVER · 절대 금지", font=f_sec, fill=RED)
never = [
    "가죽 광택 · leather sheen 추가",
    "V자 메탈 다리 · 두꺼운 padded 팔걸이",
    "헤드레스트 · 리클라이너 · USB/control",
    "tufting · 버튼 · 무늬 · 프린트",
]
for i, t in enumerate(never):
    y = 1066 + i * 40
    d.line([(panel_x + 26, y + 12), (panel_x + 40, y + 12)], fill=RED, width=4)
    d.text((panel_x + 52, y), t, font=f_body, fill=INK)

sheet_out = PREP / "milo_smart_sheet.jpg"
canvas.save(sheet_out, optimize=True, quality=92)
print(f"  → {sheet_out} ({W}×{H})")

# ============= product_grid.jpg =============
print("\nbuilding product_grid.jpg...")
gw, gh = 1600, 1100
canvas2 = Image.new("RGB", (gw, gh), BG)
d2 = ImageDraw.Draw(canvas2)
d2.text((MARGIN, 30), "MILO 제품 다각도 + 컬러 그리드", font=f_title, fill=INK)
d2.line([(MARGIN, 90), (gw - MARGIN, 90)], fill=LINE, width=2)

cells = [
    (USE_PROD / "p08_frame_01.jpg", "정면 (오트밀)"),
    (USE_PROD / "p08_frame_02.jpg", "측면 A"),
    (USE_PROD / "p08_frame_03.jpg", "측면 B"),
    (USE_PROD / "p08_frame_01_color_2.webp", "라이트그레이"),
    (USE_PROD / "p08_frame_01_color_3.webp", "더스티로즈"),
    (USER_DIR / "_cover_1000.jpg", "Hero (커버)"),
]
cells = [(p, l) for p, l in cells if p.exists()]
cols, rows = 3, 2
cell_w_grid = (gw - 2 * MARGIN - (cols - 1) * 24) // cols
cell_h_grid = (gh - 110 - 60 - (rows - 1) * 24) // rows
for i, (p, label) in enumerate(cells):
    r, c = divmod(i, cols)
    img = _fit(p, cell_w_grid, cell_h_grid)
    x = MARGIN + c * (cell_w_grid + 24)
    y = 110 + r * (cell_h_grid + 50)
    canvas2.paste(img, (x + (cell_w_grid - img.width) // 2, y + (cell_h_grid - img.height) // 2))
    d2.text((x + 8, y + cell_h_grid + 6), label, font=f_label, fill=GRAY)

grid_out = PREP / "product_grid.jpg"
canvas2.save(grid_out, quality=90)
print(f"  → {grid_out} ({gw}×{gh})")

# ============= material_close.jpg =============
print("\nbuilding material_close.jpg...")
material_p = USE_PROD / "material.png"
if material_p.exists():
    mat_src = _fit(material_p, 1200, 800)
    mw, mh = mat_src.width + 80, mat_src.height + 120
    mat = Image.new("RGB", (mw, mh), BG)
    mat_d = ImageDraw.Draw(mat)
    mat_d.text((40, 24), "MILO 마감재 — 폴리니크 패브릭 (생활발수, OEKO-TEX)",
               font=f_sec, fill=INK)
    mat.paste(mat_src, (40, 80))
    mat_out = PREP / "material_close.jpg"
    mat.save(mat_out, quality=92)
    print(f"  → {mat_out} ({mw}×{mh})")

# ============= color_chart.jpg =============
print("\nbuilding color_chart.jpg...")
cs = [(USE_PROD / f"color_0{i}.png", n) for i, n in
      [(1, "오트밀"), (2, "라이트그레이"), (3, "더스티로즈")]]
cs = [(p, n) for p, n in cs if p.exists()]
ccw, cch = 1400, 540
cc = Image.new("RGB", (ccw, cch), BG)
ccd = ImageDraw.Draw(cc)
ccd.text((40, 24), "MILO 컬러 옵션 3종", font=f_sec, fill=INK)
swatch_w = (ccw - 2 * 40 - (len(cs) - 1) * 30) // max(len(cs), 1)
for i, (p, n) in enumerate(cs):
    sim = _fit(p, swatch_w, 380)
    x = 40 + i * (swatch_w + 30)
    cc.paste(sim, (x + (swatch_w - sim.width) // 2, 80))
    ccd.text((x + 8, 80 + 380 + 12), n, font=f_label, fill=GRAY)
cc_out = PREP / "color_chart.jpg"
cc.save(cc_out, quality=92)
print(f"  → {cc_out} ({ccw}×{cch})")

print("\n=== DONE ===")
print("전처리 산출물 (이미지 첨부 시 항상 함께):")
for f in sorted(PREP.glob("*.jpg")):
    print(f"  {f.relative_to(USER_DIR)}")

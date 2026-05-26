"""밀로(777039) — 2가지 vision 입력 결합:

1. 사용자 업로드 GIF 3 frames → visual description (보이는 그대로)
2. 한샘 페이지의 제품/소재/컬러 panel (이미 spec.json에 추출됨) — 담당자라면 갖고 있을 정보

결과: user_products/milo_777039/visual_description.json
- gif_visual: 3 frames 합쳐서 1장 description (시각적 사실)
- spec (이미 있음, spec.json에서 가져옴)
- combined_summary: swap prompt에 통째 박을 풍부한 1-블록 description
"""

import json
import os
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import openai_client as client, data_uri  # noqa: E402

HERE = Path(__file__).parent
USER_DIR = HERE / "user_products/milo_777039"
OUT = USER_DIR / "visual_description.json"

if OUT.exists():
    print(f"cached: {OUT} — skip")
    sys.exit(0)

spec = json.loads((USER_DIR / "spec.json").read_text())["spec"]
gif_frames = sorted((USER_DIR / "gif_frames").glob("frame_*.jpg"))[:3]
assert len(gif_frames) >= 1

GIF_VISION_PROMPT = """\
You are analysing 3 frames from a 360° product rotation GIF of a Korean
fabric sofa called "밀로 패브릭소파" (MILO fabric 2-seat sofa). Describe
every visible product detail precisely — these frames are the authoritative
reference for an AI image generator that must reproduce this sofa exactly.

Describe:
- Overall silhouette: seat count (count cushions carefully — 2 vs 3 seats),
  shape proportions, length-to-height ratio
- Arm shape: rolled / boxy / squared-off / tapered / pillow-top
- Arm height relative to backrest
- Back: number of back cushions and shape, attached or loose, headrest yes/no
- Seat: number of seat cushions, depth, firmness implied by shape (puffy
  loose / tight tailored / structured)
- Upholstery: fabric (NOT leather), texture (smooth / textured / boucle /
  linen-look), seam style (none / piped / topstitched), any visible color
- Legs: number, shape (block / tapered / hairpin / metal slim), color
- Any decorative elements (none / piping / nailheads / tufting / quilting)
- Symmetry, decorative pillows count and shape

CRITICAL: 좌석 개수(seat count) — DO NOT confuse with 3-seat. Verify
carefully from the cushion arrangement.

Return JSON:
{
  "seat_count": int,
  "silhouette": str,
  "arm": {"shape": str, "height_relative": str},
  "back": {"cushion_count": int, "shape": str, "attached_or_loose": str, "headrest": bool},
  "seat": {"cushion_count": int, "depth": str, "firmness": str},
  "upholstery": {"material": str, "texture": str, "seams": str, "primary_color": str},
  "legs": {"count": int, "shape": str, "color": str},
  "decorative_pillows": {"count": int, "shape": str},
  "decorative_elements": str,
  "full_visual_paragraph": "5-7 dense English sentences describing exactly what to render"
}
No preamble. Be conservative with seat_count — count cushions.
"""

# 3 frames 동시에 vision에 보냄
print(f"analysing {len(gif_frames)} GIF frames...")
resp = client.chat.completions.create(
    model=config.VISION_MODEL,
    messages=[{"role": "user", "content": [
        {"type": "text", "text": GIF_VISION_PROMPT},
        *[
            item
            for f in gif_frames
            for item in [
                {"type": "text", "text": f"Frame {gif_frames.index(f)+1}:"},
                {"type": "image_url", "image_url": {"url": data_uri(f)}},
            ]
        ],
    ]}],
    response_format={"type": "json_object"},
    temperature=0.1,
)
gif_visual = json.loads(resp.choices[0].message.content)
print(f"  seat_count: {gif_visual.get('seat_count')}")
print(f"  silhouette: {gif_visual.get('silhouette','')[:80]}")
print(f"  arm: {gif_visual.get('arm')}")
print(f"  upholstery: {gif_visual.get('upholstery')}")
print(f"  legs: {gif_visual.get('legs')}")

# combined paragraph for swap prompts
spec_dims = spec.get("dimensions", {})
spec_mat = spec.get("material", {})
spec_colors = spec.get("colors") or []

# combine into one rich product description block
COMBINED_PROMPT = f"""\
PRODUCT: 밀로 패브릭소파 2인용 (MILO fabric 2-SEAT sofa) — STRICTLY 2 seats.

VISUAL (from user-uploaded 360° GIF — authoritative for rendering):
{gif_visual.get('full_visual_paragraph','')}

DETAILED FORM:
- Seat count: {gif_visual.get('seat_count')} (STRICTLY 2 — do not render 3-seat variant)
- Silhouette: {gif_visual.get('silhouette','')}
- Arms: {gif_visual.get('arm',{}).get('shape','')}, {gif_visual.get('arm',{}).get('height_relative','')}
- Back: {gif_visual.get('back',{}).get('cushion_count','?')} {gif_visual.get('back',{}).get('shape','')} cushions, {gif_visual.get('back',{}).get('attached_or_loose','')}, headrest: {gif_visual.get('back',{}).get('headrest', False)}
- Seat: {gif_visual.get('seat',{}).get('cushion_count','?')} cushions, {gif_visual.get('seat',{}).get('depth','')} depth, {gif_visual.get('seat',{}).get('firmness','')} firmness
- Upholstery: {gif_visual.get('upholstery',{}).get('material','fabric')} ({gif_visual.get('upholstery',{}).get('texture','')}), {gif_visual.get('upholstery',{}).get('seams','')} seams, color: {gif_visual.get('upholstery',{}).get('primary_color','')}
- Legs: {gif_visual.get('legs',{}).get('count','?')} {gif_visual.get('legs',{}).get('shape','')}, {gif_visual.get('legs',{}).get('color','')}
- Decorative elements: {gif_visual.get('decorative_elements','none')}

SPEC (from product page metadata — for size/material chart panels):
- Seat height: {spec_dims.get('seat_height_cm','?')}cm
- Arm height: {spec_dims.get('arm_height_cm','?')}cm
- Upholstery material: {spec_mat.get('upholstery','')}
- Seat cushion fill: {spec_mat.get('seat_cushion','')}
- Back cushion fill: {spec_mat.get('back_cushion','')}
- Frame: {spec_mat.get('frame','')}
- Available colors: {', '.join(spec_colors)}

ABSOLUTE: this is the 2-seat (2인용) variant. NOT 3-seat. NOT 4-seat.
Fabric upholstery, NOT leather. Do not invent tufting/buttons/quilting
absent from the visual description.
"""

OUT.write_text(json.dumps({
    "gif_visual": gif_visual,
    "spec_from_page": spec,
    "combined_swap_block": COMBINED_PROMPT.strip(),
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote {OUT}")

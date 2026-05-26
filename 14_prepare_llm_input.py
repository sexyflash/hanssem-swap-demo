"""#1 sofa 992474 swap에 들어갈 LLM 입력 콘텐츠 사전 준비 (vision 호출 X).

생성물 (templates/01_sofa_992474/llm_input.json):
- target template fact (#1 한샘 sofa 정보)
- user product fact (밀로)
- product reference shots (panel/frame 후보 리스트)
- system prompts (SCENE_ANALYZE / PRODUCT_ANALYZE / SWAP_PROMPT)
- per-panel placeholder (vision 분석 시 채워질 자리)
- default user LLM request (자동 생성)
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATE_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"
OUT = TEMPLATE_DIR / "llm_input.json"


# 5th experiment에서 차용한 system prompts
SCENE_ANALYZE_PROMPT = """\
You are analysing a single panel image from a furniture product detail page so
it can be reproduced by an image generator. Describe ONLY the staging (not the
specific furniture model): camera viewpoint and angle, framing and crop, the
position of the furniture in frame, the room or backdrop, props, lighting, the
intent of this panel (e.g. introduces material, shows size, highlights option,
demonstrates module variants), and overall mood. Write 3-5 dense sentences in
English. Be specific and concrete. No preamble.
"""

PRODUCT_ANALYZE_PROMPT = """\
You are analysing a sofa product from a multi-angle reference set so an image
generator can preserve it exactly. Describe its defining form precisely:
overall silhouette and proportions, seat count, the arm shape (boxy, rolled,
flat, etc.), the back and seat cushion count and shape, the leg or base style,
the upholstery material and color, and any decorative seams or surface
details. Write 3-5 dense sentences in English, concrete and specific. No
preamble.
"""

SWAP_INSTRUCTION_PROMPT = """\
You are generating a replacement image for one panel of a furniture detail
page. CONSTRAINTS in priority order:
1. Product fidelity ≥ 93 (cover panel ≥ 95). The user product must be
   preserved exactly — silhouette, proportions, cushion arrangement, arm
   shape, upholstery material and color must match the product reference.
   No invented patterns, tufting, buttons, or trims.
2. Composition fidelity is secondary (≥ 60 OK). The staging may differ from
   the original panel's exact camera angle so long as the panel's intent
   (introduce / size / material / option / module) is preserved.
3. Cover panel only: white seamless backdrop, straight-on eye-level view,
   centered framing, soft even light, no props. Composition fidelity ≥ 95.
4. Output a single photograph. No text, no logos, no watermarks.
"""

# load facts
milo_fact = json.loads((USER_DIR / "fact.json").read_text())
template_meta = json.loads((TEMPLATE_DIR / "meta.json").read_text())
page_meta = json.loads((TEMPLATE_DIR / "page_meta.json").read_text())

# choose product reference shots: panel_01 (main) + GIF frames + selected panels
gif_frames = sorted((USER_DIR / "gif_frames").glob("frame_*.jpg"))
product_refs = []
# panel_01 메인 컷
main_panel = USER_DIR / "panel_01.jpg"
if main_panel.exists():
    product_refs.append(
        {
            "src": "../user_products/milo_777039/panel_01.jpg",
            "role": "main_panel",
            "note": "메인 화이트백 컷 추정 (가장 큰 높이)",
        }
    )
# GIF frames
for f in gif_frames:
    product_refs.append(
        {
            "src": f"../user_products/milo_777039/gif_frames/{f.name}",
            "role": "gif_frame",
            "note": "panel_08.gif 슬라이스 (총 3 frames)",
        }
    )
# selected panel 사진 (정사각 580 height — 다각도 가능성)
for pi in [5, 7, 9, 12]:
    p = USER_DIR / f"panel_{pi:02d}.jpg"
    if p.exists():
        product_refs.append(
            {
                "src": f"../user_products/milo_777039/{p.name}",
                "role": "candidate_angle",
                "note": f"panel_{pi:02d} (다각도 후보)",
            }
        )

# panel-by-panel placeholder for the target template
panel_count_total = (
    template_meta.get("detail_img_count")
    or template_meta.get("panel_count")
    or len(template_meta.get("detail_imgs", []))
)
panel_placeholders = []
for i in range(1, panel_count_total + 1):
    src = f"../templates/01_sofa_992474/panel_{i:02d}"
    # find actual ext
    matches = list(TEMPLATE_DIR.glob(f"panel_{i:02d}.*"))
    if matches:
        src = f"../templates/01_sofa_992474/{matches[0].name}"
    panel_placeholders.append(
        {
            "panel_idx": i,
            "src": src,
            "scene_description": None,  # to be filled by vision
            "swap_prompt": None,  # to be filled after vision
        }
    )

# default user LLM request (자동 생성, 사용자가 수정 가능)
default_user_request = (
    f"제품: {milo_fact['gdsNm']} (한샘 패브릭 소파 3인용, {milo_fact['price']['dc']:,}원). "
    "패브릭 소재 특성을 살리고, 거실에서 가족이 편안하게 사용하는 분위기로. "
    "원본 detail page의 panel별 의도(소재 설명, 사이즈 정보, 옵션 안내)는 유지하되 "
    "제품은 밀로 패브릭소파로 정확히 swap. 천연가죽 느낌으로 보이게 하지 말 것."
)

# compose final
out = {
    "target_template": {
        "rank": 1,
        "gdsNo": template_meta["gdsNo"],
        "name": template_meta["name"],
        "url": template_meta["url"],
        "panel_count": template_meta.get("detail_img_count") or template_meta.get("panel_count") or len(template_meta.get("detail_imgs", [])),
        "category": template_meta["category"],
    },
    "user_product": {
        "gdsNo": milo_fact["gdsNo"],
        "name": milo_fact["gdsNm"],
        "brand": milo_fact["brand"],
        "category_path": milo_fact["categories"],
        "price": milo_fact["price"],
        "description": milo_fact["description"],
        "keywords": milo_fact["searchKeywords"],
        "thumbnail": "../user_products/milo_777039/_thumbnail.jpg",
    },
    "product_reference_shots": product_refs,
    "system_prompts": {
        "scene_analyze": SCENE_ANALYZE_PROMPT.strip(),
        "product_analyze": PRODUCT_ANALYZE_PROMPT.strip(),
        "swap_instruction": SWAP_INSTRUCTION_PROMPT.strip(),
    },
    "panels": panel_placeholders,
    "user_request": {
        "default": default_user_request,
        "current": default_user_request,
        "editable": True,
    },
    "status": "input_ready",
    "vision_calls_pending": template_meta.get("detail_img_count") or template_meta.get("panel_count") or len(template_meta.get("detail_imgs", [])) + 1,  # +1 for product
}

OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {OUT}")
print(f"  target: {out['target_template']['name']}")
print(f"  user product: {out['user_product']['name']}")
print(f"  product refs: {len(product_refs)}")
print(f"  panel placeholders: {len(panel_placeholders)}")
print(f"  status: {out['status']} (vision calls pending: {out['vision_calls_pending']})")

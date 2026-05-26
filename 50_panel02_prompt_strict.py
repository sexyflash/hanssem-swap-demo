"""panel_02만 다시 — milo 3 frames + 극단 strict close-up framing prompt.

핵심: panel C 없음. milo refs 3장 (그대로). prompt만 강화해서 모델이 close-up
framing을 강제로 만들도록.

prompt 강화 포인트:
- "EXTREME CLOSE-UP" 명시
- "DO NOT render full sofa"
- "Camera 30cm from sofa surface"
- "Only left ⅓ of sofa visible"
- "Crop tight on lower-left corner: left arm + seat cushion edge + leg base"
- "Like a macro detail shot"
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
import fal_client  # noqa: E402
from lib import download, upload, openai_client, data_uri  # noqa: E402

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"
PRODUCT_INPUT = json.loads((USER_DIR / "product_input.json").read_text())

OUT_ROOT = TPL_DIR / "swap_results"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = OUT_ROOT / f"panel02_strict_{ts}"
RUN_DIR.mkdir()
OUT_DIR = RUN_DIR / "gpt_image"
OUT_DIR.mkdir()

ENDPOINT = config.MODELS["gpt_image"]

USE_PROD = USER_DIR / "use_product"
GIF_FRAMES = sorted(USE_PROD.glob("p08_frame_0?.jpg"))


PROMPT = """\
TASK: Photorealistic EXTREME CLOSE-UP detail shot of a fabric sofa (밀로 패브릭소파 2인용).

IMAGES 1, 2, 3 = 밀로 product references (the fabric sofa to render).

=== [PRODUCT TARGET] ===
밀로 패브릭소파 2인용:
- Fabric: matte linen-look texture in light beige/oatmeal
- Arms: VERY THIN slim straight profile, square edges, height ~57cm (NOT thick padded, NOT rolled)
- Cushions: 2 seat + 2 back, all LOOSE puffy with piped seams (NOT tight tailored)
- Legs: 4 SLIM cylindrical matte black metal, ~14cm height, straight cylinder pointing straight down (NOT V-shape, NOT angled, NOT block)
- Frame: 직각 boxy silhouette, low profile

=== [CRITICAL — FRAMING INSTRUCTION] ===
RENDER AN EXTREME CLOSE-UP / DETAIL MACRO SHOT.

⚠️ DO NOT render the full sofa. DO NOT show the entire sofa silhouette.
⚠️ This is a TIGHT CROPPED DETAIL SHOT — like a macro photography close-up.

Composition (very specific):
- Camera position: very close, ~30-50cm from the sofa, eye-level
- Angle: slight 3/4 from front-left, looking toward the lower-left corner of the sofa
- Crop: ZOOMED IN on the LOWER-LEFT CORNER of the sofa
- Visible elements (left to right):
  · Left edge: arm of sofa (just the lower part, vertical profile of the thin arm)
  · Center-left: left front leg (slim cylindrical matte black, full leg visible from sofa bottom to floor)
  · Center: left edge of seat cushion (just the corner, piped seam visible)
  · Right side: a bit of the seat cushion + back cushion bottom (only partial — the sofa extends beyond the right frame)
- Frame: only ~30-40% of sofa horizontally is visible. Rest is cropped out.
- Background: pure white seamless backdrop, soft floor shadow under the leg.
- Lighting: soft daylight from above-left, gentle shadow on the right side of the leg.

This is a CLOSE-UP detail shot showing fabric texture, leg detail, and piped seam.
The full sofa view is NOT what we want — only the cropped corner detail.

=== [ABSOLUTE RULES] ===
1. EXTREME CLOSE-UP (not wide view, not full sofa).
2. Show ONLY the lower-left corner area as described.
3. NO text in output (zero characters).
4. NO leather, NO V-shape legs, NO thick arms, NO tufting.
5. Fabric linen-look matte texture only.
6. Sharp focus on fabric texture and leg detail (macro-style).
"""


def qa(swap_result, panel_orig):
    qa_prompt = (
        "Panel 2 검증. 매우 엄격 한국어 QA. gpt-5.\n"
        "타겟: 밀로 close-up detail (좌측 하단 모서리 — arm + leg + cushion edge). 가죽 X, V자 다리 X.\n"
        "원본 C: 한샘 가죽 sofa의 좌측 모서리 close-up (가죽 광택, V자 메탈 다리).\n\n"
        "이미지: A=milo ref, B=swap 결과, C=한샘 원본 panel.\n\n"
        "검증:\n"
        "1) framing_is_closeup (1-5): B가 close-up crop인가, full sofa view인가? close-up=5, full sofa=1\n"
        "2) arm_thinness (1-5): B 팔걸이 thin slim?\n"
        "3) cushion_loose (1-5): B 쿠션 loose puffy?\n"
        "4) fabric_matte (1-5): B 패브릭 matte linen (가죽 광택 X)?\n"
        "5) leg_slim_cylinder (1-5): B 다리 slim cylindrical 직립 (V자 X)?\n"
        "6) full_swap (1-5): 부분 swap 아닌가?\n\n"
        "JSON: {\"scores\":{...}, \"product_score\":0-100, \"composition_score\":0-100, \"underswap\":bool, \"text_in_image\":bool, \"specific_failures\":[한국어], \"reference_influences\":[{\"element_ko\":..,\"source\":\"C\",\"correction_ko\":..}], \"notes\":\"한국어\", \"verdict\":\"pass\"|\"retry\"} — pass = all scores >= 4."
    )
    resp = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": qa_prompt},
            {"type": "text", "text": "IMAGE A (milo product reference):"},
            {"type": "image_url", "image_url": {"url": data_uri(GIF_FRAMES[0])}},
            {"type": "text", "text": "IMAGE B (swap 결과):"},
            {"type": "image_url", "image_url": {"url": data_uri(swap_result)}},
            {"type": "text", "text": "IMAGE C (한샘 원본 panel for layout reference):"},
            {"type": "image_url", "image_url": {"url": data_uri(panel_orig)}},
        ]}],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


async def generate(prompt, ref_urls, ar):
    args = {"prompt": prompt, "image_urls": ref_urls, "aspect_ratio": ar}
    result = await fal_client.subscribe_async(ENDPOINT, arguments=args)
    imgs = result.get("images") or result.get("image")
    if isinstance(imgs, list) and imgs:
        first = imgs[0]
        return first["url"] if isinstance(first, dict) else first
    if isinstance(imgs, dict):
        return imgs["url"]
    raise ValueError("no url")


async def main():
    print("=== panel_02 strict close-up prompt — milo 3 frames only, no panel C ===\n")
    print(f"prompt length: {len(PROMPT)} chars\n")

    panel_path = TPL_DIR / "panel_02.jpg"
    gif_urls = await asyncio.gather(*[upload(p) for p in GIF_FRAMES])
    ref_urls = list(gif_urls)
    print(f"refs uploaded: {len(ref_urls)} (milo GIF frames only, no panel C)\n")

    # 3 attempts with same strict prompt (no retry feedback variation — pure prompt test)
    for attempt_n in range(1, 4):
        print(f"--- attempt #{attempt_n} ---")
        img = OUT_DIR / f"panel_02__a{attempt_n}_strict.png"
        gurl = await generate(PROMPT, ref_urls, "3:2")
        await download(gurl, img)
        print(f"  saved: {img.name}")

        verdict = qa(img, panel_path)
        scores = verdict.get("scores", {})
        print(f"  scores: {scores}")
        print(f"  prod={verdict.get('product_score')} comp={verdict.get('composition_score')} "
              f"verdict={verdict.get('verdict')}")
        for f in (verdict.get("specific_failures") or []):
            print(f"    ✗ {f}")

        (OUT_DIR / f"panel_02__a{attempt_n}_verdict.json").write_text(
            json.dumps({"prompt": PROMPT, **verdict}, ensure_ascii=False, indent=2)
        )

        if verdict.get("verdict") == "pass":
            print(f"\n  ✓ PASSED at attempt {attempt_n}")
            break
        print()

    print(f"\nDONE → {RUN_DIR}")


if __name__ == "__main__":
    asyncio.run(main())

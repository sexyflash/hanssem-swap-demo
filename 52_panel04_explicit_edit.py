"""panel_04 explicit edit — gpt-image-2 + panel C base + 명시적 변경 지시.

핵심:
- endpoint: fal-ai/gpt-image-2/edit (이전 1.5 → 2.0)
- quality: high
- image_size: custom (원본 panel 비율 매칭)
- IMAGE 1 = panel C (한샘 사이즈 chart). 이건 edit base.
- prompt: "Edit panel: change 4-seat leather → 2-seat fabric. Change dim 300→200. Change firmness MEDIUM→MEDIUM SOFT..." 명시적 변경 지시.
- 한국어 텍스트 + 다이어그램 layout 그대로 유지.
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
RUN_DIR = OUT_ROOT / f"panel04_explicit_{ts}"
RUN_DIR.mkdir()
OUT_DIR = RUN_DIR / "gpt_image"
OUT_DIR.mkdir()

ENDPOINT_V2 = "fal-ai/gpt-image-2/edit"

USE_PROD = USER_DIR / "use_product"
GIF_FRAMES = sorted(USE_PROD.glob("p08_frame_0?.jpg"))

# Explicit edit prompt — "X를 Y로 변경" 식
PROMPT = """\
TASK: Edit this size-chart product detail panel (한국 가구 상세페이지 사이즈 도면).

IMAGE 1 = ORIGINAL panel (한샘 MVME 키안티 가죽 리클라이너 4인 사이즈 차트).
IMAGES 2, 3, 4 = milo 패브릭소파 2인용 product references (target product).

EDIT INSTRUCTIONS — make these specific changes while keeping the chart LAYOUT identical:

[1] CHANGE SOFA in the diagram:
- FROM: 4-seat leather 리클라이너 (dark leather, thick padded arms, V-shape chrome legs, headrest)
- TO: 2-seat fabric MILO sofa (light beige linen-look fabric, thin slim straight arms, slim cylindrical matte-black metal legs, NO headrest, loose puffy cushions with piped seams)

[2] CHANGE DIMENSION NUMBERS (keep dim line POSITIONS but change values):
- 가로 "300" → "200"
- 세로 "86" → "85"
- 깊이 "112" → "90"

[3] CHANGE TEXT below sofa (keep text POSITIONS, change values):
- "다릿발 높이 : 12cm" → "다릿발 높이 : 14cm"
- "좌방석 깊이 : 55cm" → "좌방석 깊이 : 52cm"
- "좌방석 높이 : 49cm" → "좌방석 높이 : 45cm"

[4] CHANGE FIRMNESS BAR red dot positions (keep bar structure):
- 좌방석 bar: move red dot from position 3 (MEDIUM, center) → position 4 (MEDIUM SOFT, between center and far-right)
- 등쿠션 bar: move red dot from position 3 (MEDIUM, center) → position 5 (SOFT, far-right end)

KEEP IDENTICAL:
- Background color, layout, spacing, dim-line stroke style, arrowhead style
- All Korean text (단위:cm, 좌방석, 등쿠션, HARD, MEDIUM HARD, MEDIUM, MEDIUM SOFT, SOFT) — same font and size
- "* 착석감은 개인에 따라 차이가 있을 수 있습니다." note at bottom
- The 5-dot pattern on each firmness bar (only red dot position changes)

This is a TEXT-CONTAINING edit — Korean text/numbers should remain readable and accurate after edit.
"""


def qa(panel_orig, swap_result):
    qa_prompt = """\
한국어 엄격 QA (gpt-5). Panel 4 size chart 검증.

IMAGE A = milo 제품 reference.
IMAGE B = swap 결과 (검증 대상).
IMAGE C = 한샘 원본 panel.

검증 항목 (각 1-5점):
1) sofa_milo (소파가 milo 2인 패브릭으로 변경?)
2) dim_correct (수치 200/90/85 정확?)
3) sub_dim_correct (다릿발 14, 좌방석 깊이 52, 좌방석 높이 45 정확?)
4) firmness_seat (좌방석 빨간점 MEDIUM SOFT 위치 = 4번째?)
5) firmness_back (등쿠션 빨간점 SOFT 위치 = 5번째?)
6) layout_preserved (차트 layout 동일 보존?)
7) text_readable (한국어 텍스트 깨짐 없이 정확히 읽힘?)

JSON: {"scores":{...}, "product_score":0-100, "specific_failures":[한국어], "notes":"한국어", "verdict":"pass"|"retry"} — pass = all scores >= 4.
"""
    resp = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": qa_prompt},
            {"type": "text", "text": "IMAGE A:"},
            {"type": "image_url", "image_url": {"url": data_uri(GIF_FRAMES[0])}},
            {"type": "text", "text": "IMAGE B:"},
            {"type": "image_url", "image_url": {"url": data_uri(swap_result)}},
            {"type": "text", "text": "IMAGE C:"},
            {"type": "image_url", "image_url": {"url": data_uri(panel_orig)}},
        ]}],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


async def generate_v2(prompt, ref_urls, image_size):
    """gpt-image-2 with quality=high."""
    args = {
        "prompt": prompt,
        "image_urls": ref_urls,
        "quality": "high",
        "image_size": image_size,
        "output_format": "png",
    }
    result = await fal_client.subscribe_async(ENDPOINT_V2, arguments=args)
    imgs = result.get("images") or result.get("image")
    if isinstance(imgs, list) and imgs:
        first = imgs[0]
        return first["url"] if isinstance(first, dict) else first
    if isinstance(imgs, dict):
        return imgs["url"]
    raise ValueError(f"no url: {str(result)[:200]}")


async def main():
    from PIL import Image

    print(f"=== panel_04 explicit edit — gpt-image-2 quality=high ===")
    print(f"  endpoint: {ENDPOINT_V2}")
    print(f"  prompt length: {len(PROMPT)} chars\n")

    panel_path = TPL_DIR / "panel_04.jpg"
    w, h = Image.open(panel_path).size
    print(f"original panel size: {w}×{h} (ratio {w/h:.2f})\n")

    # custom image_size — match original ratio
    if w / h < 0.8:
        image_size = "portrait_4_3"
    elif w / h > 1.2:
        image_size = "landscape_4_3"
    else:
        image_size = "square"
    print(f"image_size: {image_size}\n")

    print("uploading refs...")
    panel_c_url = await upload(panel_path)
    gif_urls = await asyncio.gather(*[upload(p) for p in GIF_FRAMES])
    ref_urls = [panel_c_url] + list(gif_urls)
    print(f"  refs: {len(ref_urls)} (panel C + 3 milo GIF frames)\n")

    for attempt_n in range(1, 4):
        print(f"--- attempt #{attempt_n} ---")
        t0 = time.time()
        img = OUT_DIR / f"panel_04__a{attempt_n}_explicit_v2.png"
        try:
            gurl = await generate_v2(PROMPT, ref_urls, image_size)
            await download(gurl, img)
            t_gen = time.time()
        except Exception as e:
            print(f"  GEN ERR: {e}\n")
            continue
        print(f"  saved: {img.name} (gen {t_gen-t0:.1f}s)")

        verdict = qa(panel_path, img)
        scores = verdict.get("scores", {})
        print(f"  scores: {scores}")
        print(f"  prod={verdict.get('product_score')} verdict={verdict.get('verdict')}")
        for f in (verdict.get("specific_failures") or []):
            print(f"    ✗ {f}")
        print(f"  notes: {verdict.get('notes','')[:150]}")

        (OUT_DIR / f"panel_04__a{attempt_n}_verdict.json").write_text(
            json.dumps({"prompt": PROMPT, **verdict}, ensure_ascii=False, indent=2)
        )

        if verdict.get("verdict") == "pass":
            print(f"\n  ✓ PASS at #{attempt_n}\n")
            break
        print()

    print(f"DONE → {RUN_DIR}")


if __name__ == "__main__":
    asyncio.run(main())

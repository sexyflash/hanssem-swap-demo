"""Tier-2 컬러 시트 — color_variants(3) + swatches(3) → 1장으로 압축.

다층 시트 아키텍처 (사용자 제안):
- 슬롯 1~3: 메인 대표 사진 (원본 그대로)
- 슬롯 4: 디테일 시트 (담당자 업로드 후 — 추후)
- 슬롯 5: 이 컬러 시트
- 슬롯 6: PRESERVE/NEVER 가이드 시트
- 슬롯 7: panel C
→ 7장 슬롯에 무한히 많은 컬러/디테일 정보 압축

출력: user_products/milo_777039/preprocessed/milo_color_sheet.png
"""

import asyncio
import sys
from pathlib import Path

import fal_client

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402

HERE = Path(__file__).parent
USER_DIR = HERE / "user_products/milo_777039"
USE_PROD = USER_DIR / "use_product"
OUT_DIR = USER_DIR / "preprocessed"
OUT_PATH = OUT_DIR / "milo_color_sheet.png"

ENDPOINT = "fal-ai/gpt-image-2/edit"

# 컬러 입력 — variants 3 + swatches 3
REFS = [
    USE_PROD / "p08_frame_01.jpg",            # 정면 (오트밀) — variant 1
    USE_PROD / "p08_frame_01_color_2.webp",   # 라이트그레이 — variant 2
    USE_PROD / "p08_frame_01_color_3.webp",   # 더스티로즈 — variant 3
    USE_PROD / "color_01.png",                # 오트밀 swatch
    USE_PROD / "color_02.png",                # 라이트그레이 swatch
    USE_PROD / "color_03.png",                # 더스티로즈 swatch
]
REFS = [r for r in REFS if r.exists()]
print(f"color refs ({len(REFS)}):")
for r in REFS:
    print(f"  {r.name}")

PROMPT = """\
당신은 한국 가구 운영팀의 COLOR REFERENCE SHEET를 1장의 합성 이미지로
만듭니다. 출력은 단일 LANDSCAPE PNG.

상단 헤더 (가로띠):
  "MILO 패브릭소파 — COLOR OPTIONS · 3종"

2 rows × 3 columns 그리드:

ROW 1 — 제품 컷 (3종 컬러 variants)
  Cell 1: 오트밀 (warm neutral, 크림톤)
    - reference: IMAGE 1 (정면, 오트밀)
    - 라벨: "COLOR · 오트밀"
  Cell 2: 라이트그레이 (cool neutral, 도시적)
    - reference: IMAGE 2 (라이트그레이 variant)
    - 라벨: "COLOR · 라이트그레이"
  Cell 3: 더스티로즈 (말린 장미색, 파우더리)
    - reference: IMAGE 3 (더스티로즈 variant)
    - 라벨: "COLOR · 더스티로즈"

ROW 2 — 컬러 swatch (원단 짜임 close-up 3종)
  Cell 4: 오트밀 swatch — reference: IMAGE 4
    라벨: "오트밀 · OATMEAL"
    하단 톤 설명: "warm neutral · 크림 → 그레이"
  Cell 5: 라이트그레이 swatch — reference: IMAGE 5
    라벨: "라이트그레이 · LIGHT GRAY"
    하단 톤 설명: "cool neutral · 차분한 회색"
  Cell 6: 더스티로즈 swatch — reference: IMAGE 6
    라벨: "더스티로즈 · DUSTY ROSE"
    하단 톤 설명: "warm rose · 파우더리"

GLOBAL RULES:
- 각 셀의 라벨 텍스트는 정확한 한글/영문 그대로 인쇄. 글자 깨짐 X.
- swatches는 멜란지 패브릭 짜임이 또렷이 보이게 close-up.
- 컬러 톤은 reference swatches 그대로 — 임의 변형 금지.
- 셀 사이 흰색 거터, 얇게.
- 깨끗한 sans-serif 폰트 (Pretendard 스타일).
- 출력은 단일 합성 PNG 1장.

이 시트는 swap 공정에서 color_option / module_lineup panel을 만들 때 항상 첨부됩니다.
3컬러 정보가 모두 1장에 들어가므로 슬롯을 1개만 차지합니다.
"""


async def main():
    print(f"\nuploading {len(REFS)} refs to fal...")
    ref_urls = await asyncio.gather(*[
        asyncio.to_thread(fal_client.upload_file, str(p)) for p in REFS
    ])
    for r, u in zip(REFS, ref_urls):
        print(f"  {r.name} -> ...{u[-40:]}")

    print(f"\ncalling {ENDPOINT}...")
    args = {
        "prompt": PROMPT,
        "image_urls": ref_urls,
        "quality": "high",
        "image_size": "landscape_4_3",
        "output_format": "png",
    }
    result = await fal_client.subscribe_async(ENDPOINT, arguments=args)
    imgs = result.get("images") or result.get("image")
    if isinstance(imgs, list) and imgs:
        url = imgs[0]["url"] if isinstance(imgs[0], dict) else imgs[0]
    elif isinstance(imgs, dict):
        url = imgs["url"]
    else:
        raise ValueError(f"no url: {result}")

    print(f"\ndownloading {url}")
    import httpx
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.get(url)
        r.raise_for_status()
        OUT_PATH.write_bytes(r.content)
    print(f"\n✓ wrote {OUT_PATH} ({OUT_PATH.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    asyncio.run(main())

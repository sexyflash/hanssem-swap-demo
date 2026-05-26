"""마스터 시트 v3 — 메타 자료 디자인 (DO NOT REPLICATE).

사용자 비판:
"스마트시트는 참고용 메타 자료. 출력에서 grid 형태로 나오면 안 됨.
섹션 분리 + 여백 + '이건 사용하는 이미지가 아니다' 명시 필요."

v3 차이점 vs v2:
- 최상단/하단/각 코너에 **워터마크**: "⚠ REFERENCE METADATA — DO NOT REPLICATE"
- 시트 자체에 "GUIDE / RULE BOOK" 같은 비-product 메타 라벨
- 섹션 분리 명확 (📷 제품 reference / 🚫 특이사항 / ✓ PRESERVE / ✗ NEVER)
- 여백 풍부 — 시트가 product photo 같이 안 보이게
- 컬러 톤도 product photo가 아님을 강조 (회색 톤 배경, 박스 윤곽 명확)

출력: user_products/milo_777039/preprocessed/milo_master_sheet.png (덮어쓰기)
"""

import asyncio
import json
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
OUT_PATH = OUT_DIR / "milo_master_sheet.png"

ENDPOINT = "fal-ai/gpt-image-2/edit"

# v3 — main 3 + 핵심 디테일 4 + 컬러 2 + 소재 1 = 10장
REFS_META = [
    (USE_PROD / "p08_frame_01.jpg",            "MAIN · 정면"),
    (USE_PROD / "p08_frame_02.jpg",            "MAIN · 측면"),
    (USE_PROD / "p08_frame_03.jpg",            "MAIN · 각도"),
    (USE_PROD / "p08_frame_04.png",            "DETAIL · 다리/하부"),
    (USE_PROD / "p08_frame_05.png",            "DETAIL · 팔걸이"),
    (USE_PROD / "detail_02.png",               "DETAIL · 좌방석"),
    (USE_PROD / "detail_05.png",               "DETAIL · 등쿠션 시접"),
    (USE_PROD / "p08_frame_01_color_2.webp",   "COLOR · 라이트그레이"),
    (USE_PROD / "p08_frame_01_color_3.webp",   "COLOR · 더스티로즈"),
    (USE_PROD / "material.png",                "MATERIAL · 멜란지 패브릭"),
]
REFS_META = [(p, l) for p, l in REFS_META if p.exists()]
REFS = [p for p, l in REFS_META]
print(f"refs ({len(REFS)}):")
for i, (p, lbl) in enumerate(REFS_META, 1):
    print(f"  IMAGE {i:2}: {p.name:35} → {lbl}")

PROD_INPUT = json.loads((USER_DIR / "product_input_v3.json").read_text())
sp = PROD_INPUT.get("spec", {})


PROMPT = f"""\
당신은 한국 가구(MILO 패브릭소파 2인용) 운영팀의 PRODUCT GUIDE / RULE BOOK을
1장으로 만듭니다. 이것은 **참고용 메타 자료**이며, swap 엔진이 출력에 사용하는
이미지가 아닙니다. 출력은 단일 LANDSCAPE 16:9 PNG.

=== 절대 원칙 ===
[A] 이 시트는 **REFERENCE METADATA** — swap 엔진이 결과 이미지로 출력하지 않습니다.
    시트 자체에 "REFERENCE METADATA — DO NOT REPLICATE" 워터마크가 들어가야 합니다.
[B] 다리는 **정확히 4개** (모서리 4, 중앙 X). hallucination 절대 금지.
[C] 첨부된 reference 이미지의 픽셀 그대로 표시. 새로 그리지 마세요.

=== 시트 디자인 (Product Photo가 아닌 GUIDE 형태) ===

배경: 옅은 회색/베이지 (#fafafa 또는 #f5f5f3) — product photo가 아님을 시각적으로
      구분. 셀 사이 큰 여백.

상단 헤더 가로띠 (큰 폰트, 명확):
  좌측: "MILO 패브릭소파 2인용 — PRODUCT GUIDE"
  우측 워터마크 (빨간/회색 약간 투명 reverse-out):
    "⚠ REFERENCE METADATA · DO NOT REPLICATE IN OUTPUT"

각 코너 + 시트 중앙 하단에 작은 반복 워터마크:
  "GUIDE · NOT FOR OUTPUT"

본문 — 4개 섹션으로 명확히 그룹핑, 섹션 사이 큰 여백 + 섹션 헤더:

──── 섹션 1: 📷 PRODUCT REFERENCE (제품 컷) ────
  3 cells in a row (큰 여백 두고)
  Cell 1: IMAGE 1 (정면) — 라벨 "MAIN · 정면"
  Cell 2: IMAGE 2 (측면) — 라벨 "MAIN · 측면"
  Cell 3: IMAGE 3 (각도) — 라벨 "MAIN · 3/4 각도"
  하단 텍스트:
    "🦵 다리 4개 (모서리, 중앙 X) · 매트블랙 슬림 메탈 · 14cm
     💪 슬림 박스 팔걸이 · 안쪽 보조쿠션 flange
     🛋 루스 puffy 등쿠션 2 · 좌방석 MEDIUM SOFT
     🧵 멜란지 무광 평직 · 생활발수 · OEKO-TEX"

──── 섹션 2: 🔍 DETAIL CLOSE-UPS ────
  4 cells in a row
  Cell 4: IMAGE 4 — 라벨 "다리/하부"
  Cell 5: IMAGE 5 — 라벨 "팔걸이"
  Cell 6: IMAGE 6 — 라벨 "좌방석"
  Cell 7: IMAGE 7 — 라벨 "등쿠션 시접"

──── 섹션 3: 🎨 COLOR & MATERIAL ────
  3 cells in a row + 패브릭 셀
  Cell 8: IMAGE 8 (라이트그레이 variant) — "라이트그레이"
  Cell 9: IMAGE 9 (더스티로즈 variant) — "더스티로즈"
  Cell 10: IMAGE 10 (material) — "멜란지 패브릭"

──── 섹션 4: ✓ PRESERVE / ✗ NEVER ────
  두 박스 좌우 배치 (이미지 셀 없음, 텍스트 박스만)

  좌 박스 (외곽 초록 #22c55e, 배경 #f0fdf4):
    헤더: "✓ PRESERVE · 반드시 유지"
      ● 2-SEAT STRICT
      ● 패브릭 (matte linen) · 가죽 X
      ● 슬림 박스 팔걸이
      ● 루스 puffy 등쿠션 2
      ● **다리 4개** (모서리, 중앙 X)
      ● 좌방석 topstitch · 등쿠션 flange

  우 박스 (외곽 빨강 #ef4444, 배경 #fef2f2):
    헤더: "✗ NEVER · 절대 금지"
      ✗ 가죽 광택
      ✗ V자 두꺼운 팔걸이
      ✗ **5번째 중앙 다리**
      ✗ 헤드레스트 · 리클라이너 · USB
      ✗ tufting · 버튼 · 무늬
      ✗ 한샘 컬러명 (그레이/도브그레이/스카이그레이) 잔존

하단 가로띠 (작은 폰트, 회색):
  "이 시트는 swap 엔진의 PRESERVE/NEVER 규칙과 디테일 reference를 정리한
   메타 자료입니다. 결과 이미지로 출력하지 마세요. 결과는 한샘 panel C와 같은
   single panel layout이어야 합니다."

=== 출력 형식 강제 ===
- 모든 한글/영문 텍스트 또렷이 인쇄. 글자 깨짐 X.
- 폰트: 깨끗한 sans-serif.
- 시트가 **product photo가 아닌 문서/가이드처럼** 보이게 — 옅은 배경,
  섹션 헤더 라벨 큼직, 박스 윤곽 명확, 워터마크 항상 visible.
- 단일 PNG 1장 (16:9 landscape).

이 시트의 목적은 swap 엔진에게 강한 reference + 운영 규칙 전달입니다.
출력 이미지로 절대 복제되어서는 안 됩니다.
"""


async def main():
    print(f"\nuploading {len(REFS)} refs...")
    ref_urls = await asyncio.gather(*[
        asyncio.to_thread(fal_client.upload_file, str(p)) for p in REFS
    ])
    for (p, lbl), u in zip(REFS_META, ref_urls):
        print(f"  {p.name:35} -> ...{u[-30:]}")

    print(f"\ncalling {ENDPOINT} (16:9, quality=high)...")
    args = {
        "prompt": PROMPT, "image_urls": ref_urls,
        "quality": "high", "image_size": "landscape_16_9", "output_format": "png",
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
    async with httpx.AsyncClient(timeout=180) as c:
        r = await c.get(url)
        r.raise_for_status()
        OUT_PATH.write_bytes(r.content)
    print(f"\n✓ wrote {OUT_PATH} ({OUT_PATH.stat().st_size // 1024}KB)")
    print(f"  fal url: {url}")


if __name__ == "__main__":
    asyncio.run(main())

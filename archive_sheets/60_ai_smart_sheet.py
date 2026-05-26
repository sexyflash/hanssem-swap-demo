"""AI smart sheet — gpt-image-2/edit로 1장의 합성 시트 생성.

4th VideoGen 패턴 차용:
- 1장 composite (4×3 grid)
- 다각도 + 다리 close-up + 쿠션 close-up + 시접 close-up
  + 컬러 옵션 + PRESERVE/NEVER 텍스트 박스
- gpt-image-2/edit (한글 텍스트 깨짐 없음)
- quality=high, landscape_4_3 (gpt-image-2 supports up to 1536px)

레퍼런스: use_product/ 전체
출력: user_products/milo_777039/preprocessed/milo_ai_smart_sheet.png
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
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH = OUT_DIR / "milo_ai_smart_sheet.png"

ENDPOINT = "fal-ai/gpt-image-2/edit"

# 입력 — gpt-image-2/edit max 10 (use_product 11개 중 p08_frame_05 제외 — 중복 각도)
REFS = [
    USE_PROD / "p08_frame_01.jpg",            # 정면 (오트밀)
    USE_PROD / "p08_frame_02.jpg",            # 측면
    USE_PROD / "p08_frame_03.jpg",            # 각도
    USE_PROD / "p08_frame_04.png",            # 추가 각도/디테일
    USE_PROD / "p08_frame_01_color_2.webp",   # 라이트그레이
    USE_PROD / "p08_frame_01_color_3.webp",   # 더스티로즈
    USE_PROD / "color_01.png",                # 오트밀 swatch
    USE_PROD / "color_02.png",                # 라이트그레이 swatch
    USE_PROD / "color_03.png",                # 더스티로즈 swatch
    USE_PROD / "material.png",                # 패브릭 close-up
]
REFS = [r for r in REFS if r.exists()]
print(f"refs ({len(REFS)}):")
for r in REFS:
    print(f"  {r.name}")

PROMPT = """\
당신은 한국 가구 운영팀의 정밀 제품 레퍼런스 시트(PRODUCT FIDELITY SHEET)를
한 장의 4×3 그리드 이미지로 합성합니다. 출력은 단일 LANDSCAPE 시트입니다.

상단 헤더 영역 (페이지 맨 위 가로띠, 전체 width):
  "MILO 패브릭소파 2인용 · PRODUCT FIDELITY SHEET"
  부제: "제품 원형 보존 레퍼런스 — strict95"

본 시트는 4 columns × 3 rows = 12 셀로 구성됩니다. 셀 사이 흰색 거터.
모든 셀에 영어/한글 라벨 텍스트를 정확히 인쇄.

ROW 1 — 다각도 (FRONT / SIDE / ANGLE / TOP-VIEW)
  Cell 1: "FRONT · 정면" — 정면 다각도 view (제품 전체)
  Cell 2: "SIDE A · 측면" — 측면 view
  Cell 3: "ANGLE · 3/4 각도" — 3/4 angle view
  Cell 4: "DETAIL · 디테일" — 또 다른 각도 (구겨진 쿠션 표면 보이게)

ROW 2 — 클로즈업 디테일 (LEGS / CUSHION / SEAM / FABRIC)
  Cell 5: "LEGS · 다리 (5개: 모서리 4 + 중앙 1)"
    매트 블랙 파우더 코팅 원통형 14cm 다리 close-up
    바닥과 닿는 글라이드까지 보이게. 중앙 5번째 다리 위치 표시.
  Cell 6: "CUSHION · 쿠션 볼륨 (좌방석 MS · 등쿠션 SOFT)"
    좌방석 + 등쿠션 단면이 보이는 close-up. 루스 puffy 쿠션 표면.
  Cell 7: "SEAM · 시접 차이"
    좌방석 topstitch vs 등쿠션 flange(겉시접) 봉제 비교 close-up.
    봉제 라인이 또렷이 보이게.
  Cell 8: "FABRIC · 멜란지 패브릭 (무광 평직)"
    원단 짜임 close-up. 미세한 헤더 톤 강조.

ROW 3 — 컬러 옵션 (3종 + PRESERVE/NEVER 박스)
  Cell 9: "COLOR · 오트밀"
    오트밀 색상 제품 컷 (또는 swatch)
  Cell 10: "COLOR · 라이트그레이"
    라이트그레이 색상 제품 컷
  Cell 11: "COLOR · 더스티로즈"
    더스티로즈 색상 제품 컷
  Cell 12: 두 박스가 위/아래로 분할된 정보 박스 (제품 이미지 NO).
    위 절반 — 초록 박스 "PRESERVE · 반드시 유지":
      • 2인용 STRICT (좌석수 변경 X)
      • 패브릭 (linen-look matte) — 가죽 X
      • 직각 박스형 팔걸이 (slim)
      • 루스 puffy 등쿠션 2개
      • 매트블랙 다리 5개 (모서리 4 + 중앙 1)
    아래 절반 — 빨간 박스 "NEVER · 절대 금지":
      • 가죽 광택 · leather sheen
      • V자 메탈 다리 · 두꺼운 padded 팔걸이
      • 헤드레스트 · 리클라이너 · USB
      • tufting · 버튼 · 무늬

GLOBAL RULES:
- 모든 셀의 라벨 텍스트는 정확한 한글/영문 그대로 인쇄.
  글자 깨짐 절대 X.
- 거터는 흰색, 얇게.
- 첨부된 reference 이미지들을 셀별 제품 컷의 시각적 anchor로 사용:
  IMAGE 1~4 — 다각도 (Row 1)
  IMAGE 5,6 — 컬러 variants
  IMAGE 7~9 — 컬러 swatches (Row 3)
  IMAGE 10 — 패브릭 텍스처 (Cell 8)
- 다리는 정확히 5개 (모서리 4 + 가운데 1) — Cell 5에 화살표 + 카운트 표시.
- 컬러 톤은 swatches 그대로 — 임의 변형 금지.
- 출력은 단일 합성 PNG. 4×3 grid + 상단 헤더 1장.
- 텍스트 폰트: 깨끗한 sans-serif (Pretendard / Apple SD Gothic Neo 스타일).
- 한글과 영문 모두 정확히 가독.

이 시트는 swap 공정에서 항상 마지막 reference로 첨부됩니다 — 운영진의 PRESERVE/NEVER 의사가
명확히 전달되어야 합니다.
"""


async def main():
    print(f"\nuploading {len(REFS)} reference images to fal...")
    ref_urls = await asyncio.gather(*[
        asyncio.to_thread(fal_client.upload_file, str(p)) for p in REFS
    ])
    for r, u in zip(REFS, ref_urls):
        print(f"  {r.name} -> {u[-40:]}")

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
        first = imgs[0]
        url = first["url"] if isinstance(first, dict) else first
    elif isinstance(imgs, dict):
        url = imgs["url"]
    else:
        raise ValueError(f"no url in result: {result}")

    print(f"\ndownloading {url}")
    import httpx
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.get(url)
        r.raise_for_status()
        OUT_PATH.write_bytes(r.content)
    print(f"\n✓ wrote {OUT_PATH} ({OUT_PATH.stat().st_size // 1024}KB)")
    print(f"  fal url: {url}")


if __name__ == "__main__":
    asyncio.run(main())

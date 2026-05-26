"""Tier-2 가이드 시트 — PRESERVE/NEVER + 미니 다각도 → 1장.

운영팀의 strict95 가이드를 AI가 항상 시각/텍스트로 인지하도록 만든
'rules-as-an-image' 시트. swap 호출 시 PRESERVE/NEVER 박스를 명시적으로
함께 보내서 모델이 절대 violate 하지 않게 함.

출력: user_products/milo_777039/preprocessed/milo_guide_sheet.png
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
OUT_PATH = OUT_DIR / "milo_guide_sheet.png"

ENDPOINT = "fal-ai/gpt-image-2/edit"

# 미니 다각도 — PRESERVE/NEVER 박스의 시각적 anchor
REFS = [
    USE_PROD / "p08_frame_01.jpg",   # 정면
    USE_PROD / "p08_frame_02.jpg",   # 측면
    USE_PROD / "p08_frame_03.jpg",   # 각도
    USE_PROD / "p08_frame_04.png",   # 추가 디테일 각도
]
REFS = [r for r in REFS if r.exists()]
print(f"guide refs ({len(REFS)}):")
for r in REFS:
    print(f"  {r.name}")

PROMPT = """\
당신은 한국 가구 운영팀의 PRODUCT GUIDE SHEET를 1장의 합성 이미지로 만듭니다.
이 시트는 'rules-as-an-image' 형식으로 swap 모델에게 PRESERVE/NEVER 의지를
명확히 전달합니다.

상단 헤더 (가로띠):
  "MILO 패브릭소파 2인용 · STRICT95 GUIDE"
  부제: "PRESERVE & NEVER · 절대 violate 금지"

레이아웃 — 좌측 시각 anchor + 우측 텍스트 박스:

LEFT HALF (좌측 절반) — 미니 다각도 2×2 그리드
  좌상: 정면 (reference: IMAGE 1) — 라벨 "FRONT"
  우상: 측면 (reference: IMAGE 2) — 라벨 "SIDE"
  좌하: 3/4 각도 (reference: IMAGE 3) — 라벨 "ANGLE"
  우하: 디테일 (reference: IMAGE 4) — 라벨 "DETAIL"
  각 셀 우상단 작은 칩 — "RANK #1 · 2-SEAT STRICT"

RIGHT HALF (우측 절반) — 상하 2박스

  상단 박스 (초록 #16a34a 윤곽, #e9f6ee 배경) — PRESERVE
    제목: "PRESERVE · 반드시 유지"
    리스트 (초록 ● bullet):
      ● 2-SEAT STRICT — 좌석수 변경 X
      ● 패브릭 (linen-look matte) — 가죽 X
      ● 직각 박스형 슬림 팔걸이
      ● 루스 puffy 등쿠션 2개
      ● 매트블랙 원통형 다리 5개 (모서리 4 + 중앙 1)
      ● 좌방석 MEDIUM SOFT · 등쿠션 SOFT
      ● 좌방석 topstitch / 등쿠션 flange(겉시접)
      ● 컬러: 오트밀 / 라이트그레이 / 더스티로즈

  하단 박스 (빨간 #dc2626 윤곽, #fdebea 배경) — NEVER
    제목: "NEVER · 절대 금지"
    리스트 (빨간 ✗ bullet):
      ✗ 가죽 광택 · leather sheen
      ✗ V자 메탈 다리 · 두꺼운 padded 팔걸이
      ✗ 헤드레스트 · 리클라이너 · USB / control
      ✗ tufting · 버튼 · 무늬 · 프린트
      ✗ 1-seat / 3-seat / 4-seat 변형
      ✗ 우드 / 화이트 다리

GLOBAL RULES:
- 텍스트는 정확한 한글/영문 그대로 인쇄. 깨끗한 sans-serif 폰트.
  글자 깨짐 절대 X (모든 한국어 letter 또렷이).
- PRESERVE 박스는 초록 톤, NEVER 박스는 빨강 톤으로 명확히 구분.
- 미니 다각도 셀의 제품 컷은 reference 이미지의 비율/실루엣 그대로.
- 좌측 시각 anchor와 우측 텍스트 박스의 연결성을 시각적으로 강조.
- 출력은 단일 합성 PNG 1장.

이 시트는 모든 swap 호출에서 마지막 reference로 첨부됩니다.
모델이 PRESERVE/NEVER 를 매번 인지하도록.
"""


async def main():
    print(f"\nuploading {len(REFS)} refs...")
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

"""단일 통합 마스터 시트 — 4K급, 디테일+컬러+가이드+연출 모두 1장.

원칙 (사용자 강조):
- **할루시네이션 절대 금지** — 제공된 이미지에 없는 정보 만들지 마라
- **이미지 그대로 사용** — 새로 그리지 마라, 픽셀 그대로
- 셀 사이 라벨/박스/구분선만 새로 그림
- 다리 개수, 쿠션 모양, 색상 등 reference에 보이는 그대로

분류 결과 (66번 vision):
- main_view: p08_frame_01, 02, 03
- detail_close_up: p08_frame_04, 05 + detail_02, 03, 05 (사용자 의도)
- color_variant: p08_frame_01_color_2, 3 (+ detail_01 핑크)
- material/swatch: color_01, 02, 03 + material.png

10장 슬롯 선별 (가장 정보 풍부한 것):
  [1] p08_frame_01.jpg (메인 정면)
  [2] p08_frame_02.jpg (메인 측면)
  [3] p08_frame_03.jpg (메인 각도)
  [4] p08_frame_04.png (디테일: 쿠션/시접)
  [5] p08_frame_05.png (디테일: 팔걸이/다리)
  [6] detail_02.png (디테일: 좌방석/팔걸이 close-up)
  [7] detail_05.png (디테일: 팔걸이/등쿠션 close-up)
  [8] p08_frame_01_color_2.webp (컬러 variant: 라이트그레이)
  [9] p08_frame_01_color_3.webp (컬러 variant: 더스티로즈)
  [10] material.png (소재 패브릭)

레이아웃: 16:9 landscape, 4 columns × 3 rows + 상단 헤더.
출력: user_products/milo_777039/preprocessed/milo_master_sheet.png
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
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH = OUT_DIR / "milo_master_sheet.png"

ENDPOINT = "fal-ai/gpt-image-2/edit"

# 분류 기반 10장 선별
REFS_META = [
    (USE_PROD / "p08_frame_01.jpg",            "MAIN · 정면",              "main"),
    (USE_PROD / "p08_frame_02.jpg",            "MAIN · 측면",              "main"),
    (USE_PROD / "p08_frame_03.jpg",            "MAIN · 3/4 각도",          "main"),
    (USE_PROD / "p08_frame_04.png",            "DETAIL · 쿠션/시접",       "detail"),
    (USE_PROD / "p08_frame_05.png",            "DETAIL · 팔걸이/다리",     "detail"),
    (USE_PROD / "detail_02.png",               "DETAIL · 좌방석 close-up", "detail"),
    (USE_PROD / "detail_05.png",               "DETAIL · 팔걸이 close-up", "detail"),
    (USE_PROD / "p08_frame_01_color_2.webp",   "COLOR · 라이트그레이",     "color"),
    (USE_PROD / "p08_frame_01_color_3.webp",   "COLOR · 더스티로즈",       "color"),
    (USE_PROD / "material.png",                "MATERIAL · 멜란지 패브릭", "material"),
]
REFS_META = [(p, l, c) for p, l, c in REFS_META if p.exists()]
REFS = [p for p, l, c in REFS_META]
assert len(REFS) <= 10, f"too many refs: {len(REFS)}"
print(f"refs ({len(REFS)}/10):")
for i, (p, lbl, cat) in enumerate(REFS_META, 1):
    print(f"  IMAGE {i:2}: {p.name:35} → [{cat}] {lbl}")

LAYOUT_BLOCK = "\n".join(
    f"  Cell {i} ({cat}): IMAGE {i} 픽셀 그대로 + 라벨 \"{lbl}\""
    for i, (p, lbl, cat) in enumerate(REFS_META, 1)
)

PROMPT = f"""\
당신은 한국 가구(MILO 패브릭소파 2인용) 운영팀의 PRODUCT MASTER SHEET를
1장의 통합 합성 이미지로 만듭니다. 출력은 단일 LANDSCAPE 16:9 PNG.

=== 절대 원칙 (CRITICAL) ===
[1] **할루시네이션 금지**: 첨부된 reference 이미지에 보이지 않는 정보를
    절대 만들지 마세요. 다리 개수, 쿠션 모양, 색상, 시접, 재질 등
    reference에 없는 디테일을 임의로 추가하면 안 됩니다.
[2] **이미지 그대로 사용**: 각 셀의 제품 컷은 해당 IMAGE의 픽셀을
    원본 그대로 보여주세요. 새로 그리거나 재해석하거나 색을 변경하지
    마세요. 컷 자체는 reference를 충실히 reproduce.
[3] **추가 요소는 라벨/박스만**: 셀 사이의 라벨 텍스트, 구분선, 상단
    헤더, 우측 PRESERVE/NEVER 박스 정도만 새로 그리세요. 그 외에는
    이미지를 보존.

=== 레이아웃 ===
상단 헤더 (가로띠, 페이지 width 전체):
  "MILO 패브릭소파 2인용 · MASTER SHEET"
  부제: "strict95 product fidelity — 모든 reference 정보 통합"

그 아래 4 columns × 3 rows = 12 셀.
단, 마지막 셀(Cell 11, 12)은 PRESERVE/NEVER 텍스트 박스로 사용
(이미지 reference 없는 셀). 나머지 10셀은 IMAGE 1~10 그대로.

셀 매핑:
{LAYOUT_BLOCK}
  Cell 11 (rules): 초록 박스 "PRESERVE · 반드시 유지"
    ● 2-SEAT STRICT
    ● 패브릭 (linen-look matte) — 가죽 X
    ● 직각 슬림 팔걸이
    ● 루스 puffy 등쿠션 2개
    ● 매트블랙 원통형 다리 (reference 참조 — 임의 개수 X)
    ● 좌방석 topstitch · 등쿠션 flange
  Cell 12 (rules): 빨간 박스 "NEVER · 절대 금지"
    ✗ 가죽 광택 · leather sheen
    ✗ V자 메탈 다리 · 두꺼운 padded 팔걸이
    ✗ 헤드레스트 · 리클라이너 · USB
    ✗ tufting · 버튼 · 무늬

=== 라벨 인쇄 규칙 ===
- 각 셀 상단 또는 하단에 라벨 정확히 인쇄. 한글/영문 모두 또렷.
- 셀 구분선은 얇은 흰색 거터.
- 폰트: 깨끗한 sans-serif (Pretendard / Apple SD Gothic Neo 계열).
- 글자 깨짐 절대 X.

=== 추가 확인 ===
- 다리 개수 같은 critical 정보는 reference 이미지가 보여주는 그대로
  유지. 새 개수 추가 X, 빠짐 X.
- 컬러 톤은 reference variant 이미지의 톤을 그대로 사용.
- 패브릭 짜임은 material reference의 짜임 그대로.

이 시트는 swap 공정에서 모든 panel 작업에 마지막 reference로 첨부됩니다.
운영팀의 모든 의지가 1슬롯에 압축됩니다.
"""


async def main():
    print(f"\nuploading {len(REFS)} refs...")
    ref_urls = await asyncio.gather(*[
        asyncio.to_thread(fal_client.upload_file, str(p)) for p in REFS
    ])
    for (p, lbl, cat), u in zip(REFS_META, ref_urls):
        print(f"  {p.name:35} -> ...{u[-30:]}")

    print(f"\ncalling {ENDPOINT} (16:9 landscape, quality=high)...")
    args = {
        "prompt": PROMPT,
        "image_urls": ref_urls,
        "quality": "high",
        "image_size": "landscape_16_9",  # 16:9 — 시트에 적합
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
    async with httpx.AsyncClient(timeout=180) as c:
        r = await c.get(url)
        r.raise_for_status()
        OUT_PATH.write_bytes(r.content)
    print(f"\n✓ wrote {OUT_PATH} ({OUT_PATH.stat().st_size // 1024}KB)")
    print(f"  fal url: {url}")


if __name__ == "__main__":
    asyncio.run(main())

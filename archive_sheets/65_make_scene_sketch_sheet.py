"""Tier-2 연출컷 스케치 시트 — VideoGen ghost_sheet 패턴.

원칙 (4th VideoGen 차용):
- 제품(소파) = photo-real (정확한 색상/재질/디테일)
- 배경/외부 (벽/바닥/조명/소품/사람) = 흑백 라인 스케치 (chroma-out)
- 결과: 룸 내 제품 스케일/위치/구도 가늠 가능 + 디테일 정확 표현

용도:
- lifestyle_scene panel swap 시 reference로 첨부
- 모델이 "어떤 룸/구도에 소파가 들어가는지" 시각화하면서도 제품 디테일은 그대로

입력:
- 메인 대표 사진 (p08_frame_01.jpg)
- (옵션) use_product/scenes/scene_01~05 — 사용자가 추가한 룸 연출 plate

scenes/ 없으면 기본 룸 sketch 생성 (모델이 임의 룸 sketch + 소파 photo-real)

출력: user_products/milo_777039/preprocessed/milo_scene_sketch_sheet.png
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
SCENES_DIR = USE_PROD / "scenes"
OUT_PATH = USER_DIR / "preprocessed" / "milo_scene_sketch_sheet.png"

ENDPOINT = "fal-ai/gpt-image-2/edit"

# 제품 anchor + (있다면) scene plates
PRODUCT_REFS = [
    USE_PROD / "p08_frame_01.jpg",   # 메인 정면
    USE_PROD / "p08_frame_02.jpg",   # 측면
]
SCENE_REFS = []
if SCENES_DIR.exists():
    SCENE_REFS = sorted(SCENES_DIR.glob("scene_*.jpg")) + sorted(SCENES_DIR.glob("scene_*.png"))

REFS = PRODUCT_REFS + SCENE_REFS[:7]  # 총 ≤ 9장
print(f"refs ({len(REFS)}): product {len(PRODUCT_REFS)} + scenes {len(SCENE_REFS)}")
for r in REFS:
    print(f"  {r.name}")

if SCENE_REFS:
    layout_desc = f"{min(len(SCENE_REFS), 4)} columns × {1 if len(SCENE_REFS)<=4 else 2} rows"
    scenes_block = "\n".join(
        f"  Cell {i+1}: SCENE {i+1:02d} 라벨 + IMAGE {i+3}의 룸 배경을 sketch + 소파 photo-real"
        for i in range(min(len(SCENE_REFS), 7))
    )
else:
    layout_desc = "2 columns × 2 rows"
    scenes_block = """\
  Cell 1: LIVING ROOM · 거실 (밝은 미니멀 거실, sketch line-drawing 벽/바닥/식물)
  Cell 2: BEDROOM · 침실 (sketch 침대/스탠드 옆에 소파 photo-real)
  Cell 3: STUDIO · 작업실 (sketch 책상/창문/책장)
  Cell 4: LOUNGE · 라운지 (sketch 러그/조명/사이드 테이블)
"""

PROMPT = f"""\
당신은 한국 가구 운영팀의 SCENE SKETCH SHEET를 1장의 합성 이미지로 만듭니다.
4th VideoGen의 ghost_sheet 패턴 — 제품은 photo-real, 배경은 흑백 라인 스케치.

상단 헤더 (가로띠):
  "MILO 패브릭소파 2인용 · SCENE SKETCH · 스케일 & 구도 가늠"

레이아웃 — {layout_desc} 그리드.

각 셀의 처리 방식 (chroma-out hybrid):
- SOFA (제품): photo-real, 정확한 색상/재질/디테일 — IMAGE 1, 2의 메인 대표 사진을 anchor로.
  매트한 linen-look 패브릭, slim 직각 박스 팔걸이, 매트블랙 원통형 다리 5개.
  좌석수 정확히 2.
- 배경/룸/소품 (제품 외 영역): **흑백 라인 스케치** (pencil sketch / line drawing 스타일).
  - 벽/바닥/조명/창문/식물/사이드 테이블/러그 등 모두 sketch.
  - 사람이 있다면 silhouette outline만.
  - 색이 들어가지 않게 — 흑백 라인만.
- 셀별 라벨: 정확한 한글/영문 인쇄.

각 셀:
{scenes_block}

GLOBAL RULES:
- 소파의 photo-real ↔ 배경 sketch의 대비가 명확.
- 소파의 사이즈/위치가 룸 sketch와 잘 어울려 스케일 감각이 자연스럽게 전달되어야.
- 라벨 텍스트: 깨끗한 sans-serif, 한글/영문 정확. 글자 깨짐 X.
- 셀 사이 흰색 거터 얇게.
- 출력은 단일 합성 PNG 1장.

이 시트는 swap 공정의 lifestyle_scene panel을 만들 때 첨부됩니다.
모델이 룸-스케일과 소파 디테일을 동시에 인지하도록.
"""


async def main():
    print(f"\nuploading {len(REFS)} refs...")
    ref_urls = await asyncio.gather(*[
        asyncio.to_thread(fal_client.upload_file, str(p)) for p in REFS
    ])
    for r, u in zip(REFS, ref_urls):
        print(f"  {r.name} -> ...{u[-40:]}")

    print(f"\ncalling {ENDPOINT}...")
    args = {"prompt": PROMPT, "image_urls": ref_urls,
            "quality": "high", "image_size": "landscape_4_3", "output_format": "png"}
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

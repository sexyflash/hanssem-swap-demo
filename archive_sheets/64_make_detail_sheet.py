"""Tier-2 디테일 시트 — detail_01~05.jpg → 1장.

담당자가 use_product/ 또는 use_product/details/에 detail_01.jpg ~ detail_NN.jpg
파일명으로 디테일 close-up을 업로드하면 자동으로 1장 시트로 압축.

각 셀 라벨은 자동: "DETAIL N" (사용자 metadata 있으면 활용 — meta.json)
또는 use_product/details/meta.json에서 셀별 설명 읽어옴:
  {"detail_01": "다리 close-up", "detail_02": "쿠션 시접", ...}

출력: user_products/milo_777039/preprocessed/milo_detail_sheet.png
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
DETAILS_DIR = USE_PROD / "details"
OUT_PATH = USER_DIR / "preprocessed" / "milo_detail_sheet.png"

ENDPOINT = "fal-ai/gpt-image-2/edit"

# 디테일 후보 — use_product/ 또는 details/ 양쪽 탐색
candidates = []
for d in (USE_PROD, DETAILS_DIR):
    if d.exists():
        candidates += sorted(d.glob("detail_*.jpg")) + sorted(d.glob("detail_*.png")) + sorted(d.glob("detail_*.webp"))

# 최대 9장 (gpt-image-2 10장 제한 — 0번은 result anchor)
REFS = candidates[:9]

# 메타 (사용자 명시) — details/meta.json
meta_path = DETAILS_DIR / "meta.json"
meta = {}
if meta_path.exists():
    meta = json.loads(meta_path.read_text())

if not REFS:
    print("디테일 사진 없음 — use_product/details/detail_01.jpg ~ 09 업로드 후 다시 실행하세요.")
    print(f"또는 {USE_PROD}/detail_01.jpg ~ 09")
    sys.exit(0)

print(f"detail refs ({len(REFS)}):")
for r in REFS:
    label = meta.get(r.stem, "")
    print(f"  {r.name} {f'· {label}' if label else ''}")

# 셀별 라벨 (메타 있으면 그것, 없으면 자동)
labels = []
for i, r in enumerate(REFS, 1):
    lbl = meta.get(r.stem) or f"DETAIL {i:02d}"
    labels.append(lbl)
labels_md = "\n".join(f"  Cell {i}: {lbl} ← IMAGE {i}" for i, lbl in enumerate(labels, 1))

# 그리드 — 3×3 (9장 기준) 또는 자동 조정
if len(REFS) <= 3:
    grid = "1 row × {} columns".format(len(REFS))
elif len(REFS) <= 6:
    grid = "2 rows × 3 columns"
else:
    grid = "3 rows × 3 columns"

PROMPT = f"""\
당신은 한국 가구 운영팀의 DETAIL REFERENCE SHEET를 1장의 합성 이미지로 만듭니다.
출력은 단일 LANDSCAPE PNG.

상단 헤더 (가로띠):
  "MILO 패브릭소파 — DETAIL CLOSE-UPS · {len(REFS)}장"

레이아웃 — {grid} 그리드.

각 셀에 정확한 라벨 인쇄:
{labels_md}

각 셀의 제품 컷:
- 첨부된 reference 이미지 N (해당 셀 라벨 옆 IMAGE N)을 close-up 그대로 사용.
- 각 셀에 라벨 텍스트를 명확히 인쇄 (한글/영문 정확, 글자 깨짐 X).
- 디테일 정보가 또렷이 보이게 — 다리 형태/쿠션 시접/패브릭 짜임 등.

GLOBAL RULES:
- 라벨 텍스트: 깨끗한 sans-serif (Pretendard 스타일), 한글/영문 정확히.
- 셀 사이 흰색 거터, 얇게.
- 출력은 단일 합성 PNG 1장.

이 시트는 swap 공정에서 detail_close_up / intro_hero / product_shot panel을 만들 때
1슬롯만으로 모든 디테일 정보를 전달합니다.
"""


async def main():
    print(f"\nuploading {len(REFS)} detail refs...")
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

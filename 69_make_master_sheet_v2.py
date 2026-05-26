"""마스터 시트 v2 — 사용자 비판 반영.

v1 문제:
- 단순 이미지 그리드
- 다리 5개 hallucination 표시
- 텍스트 특징이 시트에 반영 안 됨
- 연출 크로키 없음

v2 개선:
- 다리 4개 명시 + reference 그대로 (5번째 절대 X)
- 입체적 구성: 메인 큰 컷 + 디테일 close-up + 텍스트 박스 통합
- 연출 크로키 cell: 룸/사람/소품 line sketch + 소파 photo-real
- PRESERVE/NEVER 박스 우측
- 각 디테일 셀 옆 한국어 텍스트 박스 (legs_detail 등 dense vision 텍스트 반영)

레이아웃 (16:9 landscape):
  헤더 가로띠
  Row1 (3 cell): 메인 정면 / 측면 / 각도
  Row2 (4 cell): 다리 detail + 텍스트 / 팔걸이 + 텍스트 / 쿠션 + 텍스트 / 패브릭 + 텍스트
  Row3: 좌측 = 컬러 3 swatch | 중앙 = 연출 크로키 wide cell | 우측 = PRESERVE/NEVER 박스
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
OUT_PATH = OUT_DIR / "milo_master_sheet.png"  # v1 덮어쓰기

ENDPOINT = "fal-ai/gpt-image-2/edit"

# 10장 reference (가장 정보 풍부한 것)
REFS_META = [
    (USE_PROD / "p08_frame_01.jpg",            "MAIN · 정면",         "main_front"),
    (USE_PROD / "p08_frame_02.jpg",            "MAIN · 측면",         "main_side"),
    (USE_PROD / "p08_frame_03.jpg",            "MAIN · 3/4 각도",     "main_angle"),
    (USE_PROD / "p08_frame_04.png",            "DETAIL · 다리/하부",  "detail_legs"),
    (USE_PROD / "p08_frame_05.png",            "DETAIL · 팔걸이",     "detail_arm"),
    (USE_PROD / "detail_02.png",               "DETAIL · 쿠션",       "detail_cushion"),
    (USE_PROD / "material.png",                "DETAIL · 패브릭",     "detail_fabric"),
    (USE_PROD / "p08_frame_01_color_2.webp",   "COLOR · 라이트그레이", "color_gray"),
    (USE_PROD / "p08_frame_01_color_3.webp",   "COLOR · 더스티로즈",   "color_rose"),
    (USE_PROD / "detail_05.png",               "DETAIL · 등쿠션 시접", "detail_seam"),
]
REFS_META = [(p, l, c) for p, l, c in REFS_META if p.exists()]
REFS = [p for p, l, c in REFS_META]
assert len(REFS) <= 10
print(f"refs ({len(REFS)}/10):")
for i, (p, lbl, cat) in enumerate(REFS_META, 1):
    print(f"  IMAGE {i:2}: {p.name:35} → {lbl}")

# 텍스트 특징 (dense vision 결과를 시트에 직접 반영)
PROD_INPUT = json.loads((USER_DIR / "product_input_v3.json").read_text())
sp = PROD_INPUT.get("spec", {})
fd = PROD_INPUT.get("feature_descriptions", {})


PROMPT = f"""\
당신은 한국 가구(MILO 패브릭소파 2인용) 운영팀의 PRODUCT MASTER SHEET를
1장의 입체적 합성 이미지로 만듭니다. 출력은 단일 LANDSCAPE 16:9 PNG.

=== 절대 원칙 ===
[1] **다리는 정확히 4개**. 네 모서리에 각각 1개씩. **중앙(5번째) 다리 절대 그리지 마라**.
    사용자 reference 이미지에 다리는 4개로 보이고, 정답도 4개임.
[2] **할루시네이션 금지**: reference 이미지에 없는 정보 (다리 개수,
    쿠션 모양, 색상, 시접 형태)를 임의로 추가하거나 변경하지 마라.
[3] **이미지 그대로 사용**: 각 셀의 제품 컷은 해당 IMAGE의 픽셀을
    원본 그대로 보여주세요. 새로 그리거나 재해석 X.

=== 레이아웃 (16:9, 입체적 구성 — 단순 그리드 아님) ===

상단 헤더 (가로띠, 페이지 width 전체):
  좌측: "MILO 패브릭소파 2인용"
  우측: "{sp.get('width_cm',200)}×{sp.get('depth_cm',90)}×{sp.get('height_cm',85)}cm · 좌면 깊이 {sp.get('seat_depth_cm',52)}cm · 다리 {sp.get('leg_height_cm',14)}cm"

ROW 1 — MAIN VIEWS (큰 사이즈, 3 cells, 가로 1/2 영역 차지)
  Cell A: IMAGE 1 정면 (가장 크게)
    하단 라벨: "MAIN · 정면"
  Cell B: IMAGE 2 측면 — 라벨: "MAIN · 측면"
  Cell C: IMAGE 3 각도 — 라벨: "MAIN · 3/4 각도"

ROW 2 — DETAIL CLOSE-UPS (4 cells, 각 셀에 이미지 + 텍스트 박스)
  Cell D: IMAGE 4 (다리/하부)
    하단 텍스트 박스:
      "🦵 다리 — 4개, 모서리 (중앙 다리 없음)
       매트블랙 슬림 메탈, 14cm, 안쪽으로 살짝 angle"
  Cell E: IMAGE 5 (팔걸이)
    하단 텍스트 박스:
      "💪 팔걸이 — 박스형 슬림, 모서리 둔각 라운드
       안쪽 보조쿠션 flange 시접, 57cm"
  Cell F: IMAGE 6 (쿠션)
    하단 텍스트 박스:
      "🛋 쿠션 — 좌방석 MEDIUM SOFT (32kg 통스펀지+덕페더)
       등쿠션 SOFT (덕페더 67%+마이크로 33%), 루스 puffy"
  Cell G: IMAGE 7 (패브릭)
    하단 텍스트 박스:
      "🧵 패브릭 — 멜란지 woven 무광 평직
       생활발수 · OEKO-TEX · FITI 인증"

ROW 3 — 좌·중·우 3분할

  좌측 1/4 — COLOR VARIANTS (3 chips 세로 또는 가로)
    상단: IMAGE 8 (라이트그레이) — chip
    중단: IMAGE 9 (더스티로즈) — chip
    하단: 오트밀 chip (메인 컬러 = 정면샷에서 추출, 또는 작은 텍스트만)
    라벨: "COLOR · 오트밀 / 라이트그레이 / 더스티로즈"

  중앙 1/2 — 연출 크로키 cell (LIFESTYLE SKETCH)
    이 셀은 다른 셀과 다르게 처리:
    - 룸 배경 (벽/바닥/창문/식물/사이드 테이블) 은 **흑백 라인 펜슬 스케치** 로
    - 그 안에 소파 (IMAGE 1을 참조한 정면 컷)만 **photo-real**
    - 사람 silhouette outline 하나가 소파 옆에 sketch로 (스케일 가늠)
    - 라벨: "LIFESTYLE · 스케일 & 구도 가늠"

  우측 1/4 — PRESERVE/NEVER 박스 (상하 분할)
    상단: 초록 박스 (#22c55e 외곽, #f0fdf4 배경)
      제목: "✓ PRESERVE"
      ● 2-SEAT STRICT
      ● 패브릭 (matte linen) · 가죽 X
      ● 슬림 박스 팔걸이
      ● 루스 puffy 등쿠션 2
      ● **다리 4개** (모서리, 중앙 X)
      ● 좌방석 topstitch · 등쿠션 flange
    하단: 빨간 박스 (#ef4444 외곽, #fef2f2 배경)
      제목: "✗ NEVER"
      ✗ 가죽 광택
      ✗ V자 두꺼운 팔걸이
      ✗ **5번째 중앙 다리** (다리는 항상 4)
      ✗ 헤드레스트 · 리클라이너 · USB
      ✗ tufting · 버튼 · 무늬

=== 라벨 인쇄 규칙 ===
- 모든 한글 텍스트는 또렷이 인쇄. 글자 깨짐 X. 한·영·숫자 모두 정확.
- 폰트: 깨끗한 sans-serif (Pretendard / Apple SD Gothic Neo 계열).
- 텍스트 박스 안의 줄바꿈 유지.
- 셀 사이는 얇은 흰색 거터.

=== 연출 크로키 처리 (중앙 셀) ===
- 펜슬/잉크 라인 스케치 스타일 — 흑백, 채색 X
- 룸 요소: 벽선, 바닥선, 창문, 식물, 사이드 테이블, 러그 — 라인 sketch
- 소파만 정확한 photo-real (IMAGE 1 reference 그대로). 다리 4개 명확.
- 사람 silhouette: outline 만, 표정/디테일 X (스케일 reference 용)
- 채도 대비: sketch는 black & white, 소파는 컬러 photo-real

이 시트는 swap 공정의 모든 panel 작업에 마지막 reference로 첨부됩니다.
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
        "image_size": "landscape_16_9",
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

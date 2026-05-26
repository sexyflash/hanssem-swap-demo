"""use_product/ 모든 자산 — gpt-5 vision으로 자동 분류.

분류 카테고리:
- main_view: 제품 전체샷 (정면/측면/각도)
- detail_close_up: 부분 close-up (다리/쿠션/시접/팔걸이 등)
- color_variant: 같은 제품의 다른 컬러 (전체샷이지만 색만 다름)
- color_swatch: 컬러 swatch 카드
- material: 소재 패브릭 close-up

출력: user_products/milo_777039/use_product/classification.json
"""

import json
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import openai_client, data_uri  # noqa: E402

HERE = Path(__file__).parent
USER_DIR = HERE / "user_products/milo_777039"
USE_PROD = USER_DIR / "use_product"
OUT = USE_PROD / "classification.json"

# 분류 대상 (DS_Store, classification.json 제외)
all_files = sorted([
    p for p in USE_PROD.iterdir()
    if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    and not p.name.startswith(".")
])
print(f"classifying {len(all_files)} assets:")
for p in all_files:
    print(f"  {p.name}")

PROMPT = """\
당신은 한국 가구(소파) 자산 분류기입니다. 첨부된 N개 이미지를 다음 5개 카테고리로 정확히 분류하세요.

카테고리:
- main_view: 제품 전체샷 (정면 / 측면 / 각도). 소파 전체가 보이고 배경은 제품 정보를 위한 단순 배경.
- detail_close_up: 부분 close-up (다리만 / 쿠션 시접만 / 팔걸이만 / 봉제 디테일 등). 제품의 일부만 크게 확대된 컷.
- color_variant: 같은 제품의 다른 컬러 (전체샷이지만 색만 변경).
- color_swatch: 컬러 swatch 카드 (작은 사각형 패브릭 견본만 있는 컷).
- material: 소재 패브릭 close-up (원단 짜임만 크게 확대된 컷).

판단 기준:
- 전체샷이지만 다른 컬러 → color_variant
- 전체샷이고 메인 컬러 (혹은 기본) → main_view
- "이건 제품 일부의 close-up이야" → detail_close_up
- swatch 카드 (보통 색만 박스로 보이는 컷) → color_swatch
- 패브릭 원단 결만 보이는 컷 → material

각 이미지에 대해:
- filename (정확히)
- category (5개 중 하나)
- subject (어떤 부분의 close-up인지 — 다리/쿠션/시접/팔걸이/등판/전체정면/전체측면 등)
- confidence (0.0~1.0)
- reasoning (한국어 한 줄)

JSON 응답:
{
  "items": [
    {"filename": "...", "category": "...", "subject": "...", "confidence": 0.0, "reasoning": "..."},
    ...
  ]
}

No preamble. JSON only.
"""

msg_content = [{"type": "text", "text": PROMPT}]
for p in all_files:
    msg_content.append({"type": "text", "text": f"--- {p.name} ---"})
    msg_content.append({"type": "image_url", "image_url": {"url": data_uri(p)}})

print(f"\ncalling gpt-5 vision (분류 mode)...")
resp = openai_client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": msg_content}],
    response_format={"type": "json_object"},
)
result = json.loads(resp.choices[0].message.content)

# 정리 + group by category
grouped = {}
for item in result.get("items", []):
    cat = item.get("category", "unknown")
    grouped.setdefault(cat, []).append(item)

out = {"items": result.get("items", []), "by_category": grouped}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote {OUT}\n")

# 콘솔 요약
print("=== 분류 결과 ===")
for cat in ["main_view", "detail_close_up", "color_variant", "color_swatch", "material"]:
    items = grouped.get(cat, [])
    print(f"\n[{cat}] {len(items)}개")
    for it in items:
        print(f"  {it.get('filename','?'):30} · {it.get('subject','?'):20} (conf={it.get('confidence',0):.2f})")
        print(f"    → {it.get('reasoning','')[:120]}")

"""use_product/ 자산 자동 분류 — CLI 일반화 (소파/책상/옷장 등 카테고리 무관).

사용:
  python3 96_classify_assets_cli.py user_products/milo_777039/use_product
  # 출력: <dir>/classification.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import openai_client, data_uri  # noqa: E402


PROMPT = """\
당신은 가구/생활용품 자산 분류기다. 첨부된 N개 이미지를 다음 5개 카테고리로 정확히 분류하라.

카테고리 (카테고리/소재/사용 시나리오에 무관하게 동일):
- main_view: 제품 전체샷 (정면/측면/각도). 제품 전체가 단순 배경에 보임.
- detail_close_up: 부분 close-up (다리/쿠션/팔걸이/서랍/문/손잡이/상판 모서리 등 일부만 크게 확대).
- color_variant: 같은 제품의 다른 컬러 (전체샷이지만 색만 변경).
- color_swatch: 작은 swatch 카드 (사각형 색 견본).
- material: 소재/원단/마감 close-up (표면 짜임 또는 마감재 표면만 확대).

판단 기준:
- 전체샷이지만 다른 컬러 → color_variant
- 전체샷이고 메인 컬러 (혹은 기본) → main_view
- "제품 일부의 close-up" → detail_close_up
- swatch 카드 → color_swatch
- 표면/소재만 확대 → material

각 이미지마다 출력:
- filename (정확히)
- category (5개 중 하나)
- subject (어떤 부분 — 다리/쿠션/시접/팔걸이/문/손잡이/상판/내부/전체정면/전체측면 등)
- confidence (0.0~1.0)
- reasoning (한국어 한 줄)

JSON only:
{
  "items": [
    {"filename": "...", "category": "...", "subject": "...", "confidence": 0.0, "reasoning": "..."}
  ]
}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("use_product_dir", help="use_product/ 디렉토리 경로 (자산이 있는 곳)")
    parser.add_argument("--force", action="store_true", help="기존 classification.json 있어도 재생성")
    args = parser.parse_args()

    use_prod = Path(args.use_product_dir).resolve()
    if not use_prod.exists():
        sys.exit(f"디렉토리 없음: {use_prod}")
    out = use_prod / "classification.json"
    if out.exists() and not args.force:
        print(f"이미 존재 (--force 로 재생성): {out}")
        return

    all_files = sorted([
        p for p in use_prod.iterdir()
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        and not p.name.startswith(".")
    ])
    print(f"classifying {len(all_files)} assets in {use_prod.name}:")
    for p in all_files:
        print(f"  {p.name}")
    if not all_files:
        sys.exit("이미지 없음")

    msg_content = [{"type": "text", "text": PROMPT}]
    for p in all_files:
        msg_content.append({"type": "text", "text": f"--- {p.name} ---"})
        msg_content.append({"type": "image_url", "image_url": {"url": data_uri(p)}})

    print(f"\ncalling vision 분류...")
    resp = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": msg_content}],
        response_format={"type": "json_object"},
    )
    result = json.loads(resp.choices[0].message.content)
    grouped = {}
    for item in result.get("items", []):
        cat = item.get("category", "unknown")
        grouped.setdefault(cat, []).append(item)
    out_data = {"items": result.get("items", []), "by_category": grouped}
    out.write_text(json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {out}")
    for cat in ["main_view", "detail_close_up", "color_variant", "color_swatch", "material"]:
        items = grouped.get(cat, [])
        print(f"  [{cat}] {len(items)}개")


if __name__ == "__main__":
    main()

"""한샘 777039 페이지 vision 정밀 재추출 — 필드 분리 (운영 시 담당자 입력 시뮬레이션).

기존 spec.json은 통합 schema. 사용자 요구: 입력 영역을 필드별로 분리해서
panel별 prompt에 zone-specific text를 정확히 inject할 수 있게.

추출 필드:
- intro (제품 소개 카피)
- spec (제품 제원: 사이즈/무게/원산지)
- features (제품 특징: firmness 5단계 정확한 값, 인증, 기능, 좌방석/등쿠션 내장재)
- model_options (2인/3인 등 사이즈 옵션)
- color_options (오트밀/라이트그레이/더스티로즈)
- material_info (마감재 / 내장재 / 프레임 / 다리)
- delivery_info (배송 / 품질보증)

결과: user_products/milo_777039/product_input.json
"""

import json
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import openai_client as client, data_uri  # noqa: E402

HERE = Path(__file__).parent
USER_DIR = HERE / "user_products/milo_777039"
OUT = USER_DIR / "product_input.json"

# 모든 panel 이미지 vision 일괄 분석
panels = sorted([p for p in USER_DIR.glob("panel_*.*") if p.suffix in {".jpg", ".jpeg", ".png"}])

# 또한 cover (1:1)
cover = USER_DIR / "_cover_1000.jpg"
all_imgs = ([cover] if cover.exists() else []) + panels[:18]

print(f"deep vision read on {len(all_imgs)} milo images...")

EXTRACT_PROMPT = """\
당신은 한국 가구 detail page를 보고 운영 담당자에게 필요한 모든 정보를 필드별로
추출합니다. 출력은 detail page swap 시스템의 사용자 입력 영역에 그대로 들어갑니다.

여러 panel 이미지가 주어집니다. 모든 panel에서 보이는 텍스트/수치/정보를 종합해
다음 schema로 반환하세요. 가능한 한 한샘 페이지의 정확한 한국어 텍스트를 그대로
유지하고, 보이지 않는 값은 null/빈 list.

{
  "product_name": "정확한 한국어 제품명 (예: 밀로 패브릭소파 2인용)",
  "seat_count_selected": 2,
  "intro": {
    "headline": "한 줄 헤드 카피 (panel에 박혀있는 경우 그대로)",
    "body": "2-3 문장 제품 소개 본문"
  },
  "spec": {
    "width_cm": int|null,
    "depth_cm": int|null,
    "height_cm": int|null,
    "seat_depth_cm": int|null,
    "seat_height_cm": int|null,
    "arm_height_cm": int|null,
    "leg_height_cm": int|null,
    "weight_kg": float|null,
    "origin": str|null
  },
  "features": {
    "seat_cushion_firmness": "HARD|MEDIUM HARD|MEDIUM|MEDIUM SOFT|SOFT",
    "back_cushion_firmness": "HARD|MEDIUM HARD|MEDIUM|MEDIUM SOFT|SOFT",
    "seat_cushion_fill": "정확한 한국어 내용 (예: 32kg 고밀도 통스펀지 + 덕페더 67% + 마이크로화이버 33%)",
    "back_cushion_fill": str,
    "upholstery": "마감재 정확히 (예: 폴리니크 패브릭, 생활발수)",
    "certifications": [list of cert names — OEKO-TEX, FITI, EO 등],
    "frame": "프레임 구성 (EO 건조목 / S자 스프링 / 엘라스틱벨트 등)",
    "legs": "다리 (스틸 다릿발 등)",
    "key_features_korean": [짧은 한국어 특징 문구 list, 5-8개]
  },
  "model_options": [
    {"name": "2인용", "dimensions": "200×90×85cm", "selected": true},
    {"name": "3인용", "dimensions": "280×90×85cm", "selected": false}
  ],
  "color_options": [
    {"name": "오트밀", "hex_guess": "#color"},
    {"name": "라이트그레이", "hex_guess": "#color"},
    {"name": "더스티로즈", "hex_guess": "#color"}
  ],
  "delivery_info": {
    "warranty": str|null,
    "delivery_method": str|null,
    "notes": [list of bullet-point notes from 배송/품질보증 panel]
  },
  "guidance_for_swap": {
    "size_chart_overlay_text": "한샘 panel_04 같은 사이즈 chart panel에 HTML overlay할 텍스트들 — 좌방석 깊이 52, 좌방석 높이 45, 팔걸이 높이 57, 다릿발 높이 14",
    "firmness_chart_korean": {
      "seat": "좌방석 미디엄 소프트",
      "back": "등쿠션 소프트"
    },
    "color_chart_korean": ["오트밀", "라이트그레이", "더스티로즈"],
    "lineup_korean": "밀로 2인 200×90×85 / 밀로 3인 280×90×85"
  }
}

No preamble. JSON only.
"""

msg_content = [{"type": "text", "text": EXTRACT_PROMPT}]
for p in all_imgs[:12]:  # vision 한 번에 최대 12장
    msg_content.append({"type": "text", "text": f"--- {p.name} ---"})
    msg_content.append({"type": "image_url", "image_url": {"url": data_uri(p)}})

resp = client.chat.completions.create(
    model=config.VISION_MODEL,
    messages=[{"role": "user", "content": msg_content}],
    response_format={"type": "json_object"},
    temperature=0.1,
)
result = json.loads(resp.choices[0].message.content)

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote {OUT}")
print(f"  product: {result.get('product_name')}")
print(f"  intro: {result.get('intro',{}).get('headline','')}")
print(f"  seat firmness: {result.get('features',{}).get('seat_cushion_firmness')}")
print(f"  back firmness: {result.get('features',{}).get('back_cushion_firmness')}")
print(f"  size: {result.get('spec',{}).get('width_cm')}×{result.get('spec',{}).get('depth_cm')}×{result.get('spec',{}).get('height_cm')}")
print(f"  models: {[m['name'] for m in result.get('model_options',[])]}")
print(f"  colors: {[c['name'] for c in result.get('color_options',[])]}")

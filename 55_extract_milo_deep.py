"""milo 777039 vision 매우 정밀 재추출 — 사용자 지적사항 반영.

추가 추출 항목:
- 좌방석-팔걸이 쿠션 연결 여부 (연결되어 있는지, 분리인지)
- 시접 모양 (piped/topstitched/flat/welt)
- 다리 위치 (모서리 4개만? 가운데 추가? 5번째 중앙 다리 있는지)
- 헤드레스트 유무
- 리클라이너/USB 유무
- 커버 분리 가능 여부
- 좌방석/등쿠션 분리/통합
- 제품 소개 본문 (자세히)
- 제원 (모든 수치 + 무게 + 원산지)
- 특징 (key features 풍부하게)
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
OUT = USER_DIR / "product_input_v2.json"

# all milo panel images (정밀 분석용)
panels = sorted([p for p in USER_DIR.glob("panel_*.*") if p.suffix in {".jpg", ".jpeg", ".png"}])
cover = USER_DIR / "_cover_1000.jpg"
all_imgs = ([cover] if cover.exists() else []) + panels[:14]
print(f"deep vision read on {len(all_imgs)} milo images (정밀 모드)")

PROMPT = """\
당신은 한국 가구 detail page 모든 panel을 분석해서 운영 담당자가 swap 시스템에
입력할 모든 정보를 정밀하게 추출합니다. 이 정보는 AI 이미지 생성에 직접 사용됩니다.

극도로 자세히 추출 — 다음 schema:

{
  "product_name": "정확한 한국어 제품명 (예: 밀로 패브릭소파 2인용)",
  "seat_count_selected": 2,
  "intro": {
    "headline": "panel에 있는 한 줄 헤드 카피",
    "body": "3-5 문장 제품 소개 본문 — 가능한 한 자세히. 사용자 카피, 분위기, 핵심 메시지 포함"
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
    "origin": str|null,
    "model_number": str|null
  },
  "features": {
    "seat_cushion_firmness": "HARD|MEDIUM HARD|MEDIUM|MEDIUM SOFT|SOFT (단단 점수와 함께)",
    "back_cushion_firmness": "HARD|MEDIUM HARD|MEDIUM|MEDIUM SOFT|SOFT",
    "seat_cushion_fill": "32kg 고밀도 통스펀지 + 덕페더 67% + 마이크로화이버 33% 같은 정확한 한국어 내용",
    "back_cushion_fill": str,
    "cushion_connected_to_arm": bool,
    "cushion_connection_note": "쿠션이 팔걸이/프레임에 어떻게 연결됐는지 설명 (예: 좌방석과 팔걸이 쿠션은 연결되어 있어 프레임만 제외하면 통째로 보이는 식)",
    "seam_style_seat": "piped|topstitched|flat|welted",
    "seam_style_arm": "piped|topstitched|flat|welted",
    "seam_difference": "팔걸이 시접과 좌방석 시접이 다르면 어떻게 다른지 설명",
    "upholstery": "마감재 정확히 (예: 폴리니크 패브릭, 생활발수)",
    "certifications": [str list — OEKO-TEX, FITI, EO 등],
    "frame": "프레임 구성",
    "legs_count": int,
    "legs_position": "모서리 4개 / 모서리 4개 + 가운데 1개 / 6개 등 — 정확한 다리 배치",
    "legs_shape": "slim cylindrical / V자 / block / 등 정확한 모양",
    "legs_color": str,
    "has_headrest": bool,
    "has_recliner": bool,
    "has_usb_or_control": bool,
    "cover_removable": bool,
    "key_features_korean": [짧은 한국어 특징 문구 list — 가능한 한 풍부하게 8-12개]
  },
  "model_options": [
    {"name": "2인용", "dimensions": "200×90×85cm", "selected": true},
    ...
  ],
  "color_options": [
    {"name": "오트밀", "hex_guess": "#color"},
    ...
  ],
  "delivery_info": {
    "warranty": str,
    "delivery_method": str,
    "notes": [list]
  },
  "panel_specific_guidance": {
    "size_chart_overlay_text": "사이즈 chart panel에 표시할 정확한 텍스트들",
    "firmness_chart_korean": {
      "seat": "좌방석 미디엄 소프트 (4번째 위치)",
      "back": "등쿠션 소프트 (5번째 위치)"
    },
    "color_chart_korean": ["오트밀", "라이트그레이", "더스티로즈"],
    "lineup_korean": "밀로 2인 200×90×85"
  }
}

특히 다음에 주의:
- 좌방석과 팔걸이 쿠션이 연결됐는지 (정확히 본 후)
- 다리가 몇 개고 어디 위치하는지 (가운데 5번째 있는지 확실히)
- 시접 모양이 부위마다 다른지 (팔걸이 vs 좌방석 vs 등쿠션)
- 헤드레스트/리클라이너/USB 유무

No preamble. JSON only.
"""

msg_content = [{"type": "text", "text": PROMPT}]
for p in all_imgs[:12]:
    msg_content.append({"type": "text", "text": f"--- {p.name} ---"})
    msg_content.append({"type": "image_url", "image_url": {"url": data_uri(p)}})

print("calling gpt-5 vision (deep extract)...")
resp = client.chat.completions.create(
    model="gpt-5",  # 최고 모델
    messages=[{"role": "user", "content": msg_content}],
    response_format={"type": "json_object"},
)
result = json.loads(resp.choices[0].message.content)

# patch user override (2-seat)
result["user_override"] = {"seat_count": 2, "reason": "담당자 입력 — 2인용 한정"}
result["product_name"] = "밀로 패브릭소파 2인용"
result["seat_count_selected"] = 2

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote {OUT}")
print(f"  product: {result.get('product_name')}")
print(f"  intro headline: {result.get('intro',{}).get('headline','')}")
print(f"  intro body: {result.get('intro',{}).get('body','')[:120]}")
feat = result.get("features", {})
print(f"  seat firmness: {feat.get('seat_cushion_firmness','')}")
print(f"  back firmness: {feat.get('back_cushion_firmness','')}")
print(f"  cushion connected to arm: {feat.get('cushion_connected_to_arm')}")
print(f"  cushion connection note: {feat.get('cushion_connection_note','')[:100]}")
print(f"  seam seat: {feat.get('seam_style_seat')} / arm: {feat.get('seam_style_arm')}")
print(f"  seam difference: {feat.get('seam_difference','')[:100]}")
print(f"  legs: {feat.get('legs_count')}개 {feat.get('legs_shape','')} ({feat.get('legs_position','')})")
print(f"  has_headrest: {feat.get('has_headrest')}, recliner: {feat.get('has_recliner')}, usb: {feat.get('has_usb_or_control')}")
print(f"  key features ({len(feat.get('key_features_korean', []) or [])}):")
for f in (feat.get("key_features_korean", []) or [])[:6]:
    print(f"    · {f}")

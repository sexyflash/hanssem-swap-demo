"""dense vision 재추출 — use_product 전체 활용, dense paragraph 형식.

원칙:
- 이미지를 못 봐도 글만으로 그림을 그릴 수 있을 정도로 상세
- 다리: 굵기/위치/각도/마감/길이 모두 묘사
- 쿠션: 모양/볼륨/시접/내장재/연결방식 dense
- 시접: 부위별 차이 자세히
- 텍스트는 dense paragraph (단답 X)

결과: user_products/milo_777039/product_input_v3.json
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
USE_PROD = USER_DIR / "use_product"
OUT = USER_DIR / "product_input_v3.json"

# 모든 use_product 이미지 + 추가 milo panel (텍스트 정보용)
use_imgs = sorted([p for p in USE_PROD.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}])
text_panels = [USER_DIR / f for f in ["panel_02.jpg", "panel_04.jpg", "panel_10.jpg", "panel_11.jpg", "panel_13.jpg", "panel_17.jpg"]]
text_panels = [p for p in text_panels if p.exists()]
all_imgs = use_imgs + text_panels[:6]
print(f"deep vision read on {len(all_imgs)} images (use_product {len(use_imgs)} + text panels {len(text_panels)})")
print(f"use_product files: {[p.name for p in use_imgs]}")

PROMPT = """\
당신은 한국 가구 detail page를 정밀 분석해서, AI 이미지 생성기가 사용할 모든 제품
정보를 dense paragraph 형식으로 추출합니다. **이미지를 못 봐도 글만으로 정확히
그림을 그릴 수 있을 정도로 상세히** 묘사하세요. 단답 X, paragraph X (풍부한 문장).

다음 schema (JSON):

{
  "product_name": "정확한 한국어 제품명",
  "seat_count_selected": 2,

  "intro_full": "5-8 문장 dense paragraph — 제품 전체 첫인상, 콘셉트, 무드, 핵심 셀링 포인트, 디자인 철학",

  "spec": {
    "width_cm": int, "depth_cm": int, "height_cm": int,
    "seat_depth_cm": int, "seat_height_cm": int, "arm_height_cm": int,
    "leg_height_cm": int, "weight_kg": float|null, "origin": str|null
  },

  "feature_descriptions": {
    "overall_silhouette": "전체 실루엣 dense paragraph — 비율, 모서리, 라인, 부피감, 전체적 인상 (5-7 문장)",
    "arms_detail": "팔걸이 dense paragraph — 두께, 형태, 모서리, 높이, 안쪽 vs 바깥쪽 시각 차이, 등받이 대비 높이, 곡선 vs 직각, 패딩감, 매트 vs 광택 등 모든 디테일 (5-7 문장)",
    "back_cushions_detail": "등쿠션 dense paragraph — 개수, 모양, loose/tight, 두께, 볼륨, headrest 유무, 시접 위치, 봉제 라인, 내장재가 비치는 정도, 헐렁한 정도 (5-7 문장)",
    "seat_cushions_detail": "좌방석 dense paragraph — 개수, depth, 볼륨, 모서리 firm/soft, 시접 형태, 내장재(통스펀지+덕페더 등), 가장자리 piped/topstitched, 가운데 vs 가장자리 두께 차이 (5-7 문장)",
    "legs_detail": "다리 dense paragraph — 개수(반드시 정확), 위치(모서리 4 + 가운데 N), 굵기, 모양(원통/V자/block/tapered), 색상, 길이, 바닥 닿는 부분 모양(평평/뾰족), 재질(메탈/우드/플라스틱) 등 정확히 (5-7 문장)",
    "fabric_texture": "패브릭 dense paragraph — 직물 종류, 짜임(linen/woven/twill), 표면 무광/유광, 색상 정확히, 두께, 빛 반사 패턴, 패턴 유무, 가까이 봤을 때 결, 멀리서 봤을 때 톤 (5-7 문장)",
    "seam_styles": "시접 dense paragraph — 좌방석 vs 등쿠션 vs 팔걸이 각각의 봉제 방식 정확히 묘사 (topstitched / 플랜지(겉시접) / piped / welted 등), 어떤 효과인지, 왜 다른지 (5-7 문장)",
    "cushion_connection": "쿠션 연결 방식 dense paragraph — 좌방석과 팔걸이가 연결됐는지, 분리됐는지, 등쿠션이 attached 인지 loose throw인지, 보조 쿠션 유무 등 정확히 (3-5 문장)",
    "frame_structure": "프레임 dense paragraph — 내장 프레임 (EO 건조목, S자 스프링, 엘라스틱벨트), 내구성, 무게 받침, 발받침 구조 등 (3-5 문장)"
  },

  "color_options_detail": [
    {"name": "오트밀", "description": "이 컬러를 자세히 묘사 — 톤, 따뜻함/차가움, 다른 컬러 대비, 어떤 분위기"},
    {"name": "라이트그레이", "description": "..."},
    {"name": "더스티로즈", "description": "..."}
  ],

  "model_options": [
    {"name": "2인용", "dimensions": "200×90×85cm", "selected": true},
    {"name": "3인용", "dimensions": "...", "selected": false}
  ],

  "delivery_warranty": "배송 + 품질보증 dense paragraph",

  "certifications_full": "인증 (OEKO-TEX 등) dense paragraph — 어떤 인증, 왜 중요, 어떤 안전성 보장",

  "comprehensive_paragraph": "제품 전체를 한 글로 풀어쓴 dense full paragraph (15-20 문장) — 위 모든 정보를 자연스럽게 결합. AI 이미지 생성기가 이 글만 읽고도 정확히 그림을 그릴 수 있게."
}

매우 중요:
- 다리 개수와 위치를 정확히 (모서리 4개만? 5개? 6개? 가운데 추가?)
- 각 dense field는 단답 X, 풍부한 paragraph
- 이미지 마다 매우 자세히 봐서 추출

No preamble. JSON only.
"""

msg_content = [{"type": "text", "text": PROMPT}]
for p in all_imgs:
    msg_content.append({"type": "text", "text": f"--- {p.name} ---"})
    msg_content.append({"type": "image_url", "image_url": {"url": data_uri(p)}})

print(f"\ncalling gpt-5 dense vision (input {len(all_imgs)} images)...")
resp = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": msg_content}],
    response_format={"type": "json_object"},
)
result = json.loads(resp.choices[0].message.content)

# patch override 2-seat
result["user_override"] = {"seat_count": 2}
result["product_name"] = "밀로 패브릭소파 2인용"
result["seat_count_selected"] = 2

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote {OUT}")
print(f"\n  product: {result.get('product_name')}")
print(f"\n=== intro ===\n{result.get('intro_full','')[:300]}...\n")
fd = result.get("feature_descriptions", {})
print(f"=== silhouette ===\n{fd.get('overall_silhouette','')[:200]}...\n")
print(f"=== legs ===\n{fd.get('legs_detail','')[:300]}...\n")
print(f"=== seams ===\n{fd.get('seam_styles','')[:250]}...\n")
print(f"=== comprehensive ===\n{result.get('comprehensive_paragraph','')[:300]}...")

"""panel별 LLM 한국어 카피 생성 — 사진 밑에 들어갈 광고 텍스트.

입력: 한샘 panel scene description (precomputed.json) + 밀로 spec (spec.json)
       + 사용자 LLM 요청 (llm_input.json)
출력: panel_copy.json {panel_idx: {title, body}}

1회 실행 후 캐시. 매번 X.
"""

import json
import os
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402  (also triggers lib env load if imported)
from lib import openai_client as client  # noqa: E402  (has correct .env-loaded key)

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"
OUT = TPL_DIR / "panel_copy.json"

if OUT.exists():
    print(f"cached: {OUT} — skip")
    sys.exit(0)

precomp = json.loads((TPL_DIR / "precomputed.json").read_text())
spec = json.loads((USER_DIR / "spec.json").read_text())["spec"]
llm_input = json.loads((TPL_DIR / "llm_input.json").read_text())

# user request 2인용 한정으로 재작성
user_request = (
    f"제품: {spec['product_name']} ({spec['ko_summary']}). "
    "패브릭 소재 특성을 살리고, 가족 거실에서 편안하게 사용하는 따뜻한 분위기로. "
    "원본 detail page panel의 의도(소재 설명, 사이즈, 옵션 안내)는 유지하되 "
    "제품은 밀로 패브릭소파 2인용으로 정확히 swap. 가죽 느낌 X."
)

COPY_PROMPT = """\
당신은 한국 가구 상세페이지 카피라이터입니다. 주어진 panel 정보를 보고
사진 밑에 들어갈 짧은 한국어 광고 카피를 작성하세요.

INPUT:
- panel scene description (영문, 어떤 구도/의도의 panel인지)
- panel class (intro/detail/design_chart/lifestyle 등)
- 제품 spec (밀로 패브릭소파 2인용)
- 사용자 LLM 요청 (전체 톤/방향)

OUTPUT: JSON
{
  "title": "1줄 강한 헤드라인 (5-12 한국어 글자)",
  "body": "1-2 문장 본문 (40-80 한국어 글자, 제품 특성/이점/감성 중 하나)"
}

규칙:
- panel_class="intro" → 제품 첫 인상, 가장 강한 헤드라인 (브랜드/제품명 부각)
- "design_chart" / "spec" → 정보 중심 (사이즈/소재/사양 등 실제 수치)
- "detail" → 디테일/마감/포인트 강조
- "lifestyle" → 분위기/감성/사용 시나리오
- 가짜 광고 클리셰(혁신적/획기적/완벽한 등) 피하고 fact 기반
- 제품명은 "밀로 패브릭소파 2인용" 또는 "밀로"로 일관 (다른 이름 X)
"""


def gen_copy(panel_idx, panel_data, panel_class):
    scene_desc = panel_data.get("description", "")
    payload = {
        "panel_idx": panel_idx,
        "panel_class": panel_class,
        "scene_description": scene_desc,
        "product_spec": spec,
        "user_request": user_request,
    }
    resp = client.chat.completions.create(
        model=config.VISION_MODEL,
        messages=[{"role": "user", "content":
            COPY_PROMPT + "\n\nPanel info:\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        }],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    return json.loads(resp.choices[0].message.content)


results = {}
# cover 카피 (별도)
print("generating cover copy...")
cover_data = {"description": "Hero cover shot of the sofa on a clean white seamless backdrop, straight-on eye-level view, centered framing, soft even light, no props."}
results["cover"] = gen_copy("cover", cover_data, "cover")
print(f"  cover: {results['cover']['title']} / {results['cover']['body'][:40]}...")

# panel 1..12
for sname, pdata in precomp["scenes"].items():
    if not sname.startswith("panel_"):
        continue
    idx = int(sname.split("_")[1])
    pcls = pdata.get("panel_class", "unknown")
    print(f"  panel_{idx:02d} [{pcls}]...", end=" ", flush=True)
    try:
        copy_data = gen_copy(idx, pdata, pcls)
        results[f"panel_{idx:02d}"] = copy_data
        print(f"{copy_data['title']}")
    except Exception as e:
        print(f"ERR: {e}")
        results[f"panel_{idx:02d}"] = {"title": "", "body": "", "error": str(e)}

OUT.write_text(json.dumps({
    "user_request": user_request,
    "product_spec_summary": {
        "name": spec.get("product_name"),
        "summary": spec.get("ko_summary"),
    },
    "copies": results,
}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\nwrote {OUT}")

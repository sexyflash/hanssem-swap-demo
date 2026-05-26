"""한샘 992474 panel별 vs 밀로 spec → mismatch 자동 판정.

각 panel에 대해:
- 한샘 panel이 어떤 기능/정보를 강조하는지 (panel_layout_types.json + visible text)
- 밀로 spec에 그 기능/정보 있나?
- 있음 → match (그대로 swap)
- 없음 (feature) → bypass (다른 milo 강점으로 카피 대체)
- 없음 (info) → skip (정보 누락 — 건너뜀)

결과: templates/01_sofa_992474/mismatch_resolution.json
"""

import json
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import openai_client as client  # noqa: E402

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"
OUT = TPL_DIR / "mismatch_resolution.json"

panel_layouts = json.loads((TPL_DIR / "panel_layout_types.json").read_text())["panels"]
panel_copy = json.loads((TPL_DIR / "panel_copy.json").read_text())["copies"]
milo_spec = json.loads((USER_DIR / "auto_pipeline_output.json").read_text())["spec"]
milo_visual = json.loads((USER_DIR / "auto_pipeline_output.json").read_text())["visual"]

# panel별 정보 collect
panel_facts = []
for p in panel_layouts:
    if "panel_idx" not in p:
        continue
    panel_facts.append({
        "panel_idx": p["panel_idx"],
        "panel_name": p["panel"],
        "zone": p.get("input_zone"),
        "layout": p.get("layout_type"),
        "visible_text": p.get("visible_korean_text", ""),
        "key_facts": p.get("key_facts_to_preserve", []),
        "swap_hint": p.get("swap_strategy_hint", ""),
    })

PROMPT = """\
당신은 가구 detail page swap engineer입니다.

[원본 한샘 템플릿] = MVME 키안티 천연가죽 리클라이너 4인 (PRODUCT_TEMPLATE)
- 가죽 / 리클라이너 / 헤드레스트 / 발받침 / USB·컨트롤 패널 등 기능형 sofa

[사용자 제품] = 밀로 패브릭소파 2인용 (USER_PRODUCT)
{milo_summary}

각 panel을 살펴서, 한샘 원본이 강조하는 기능/정보가 밀로에 있는지 판정:

- "match" — 밀로에도 있음 → 그대로 swap (예: 사이즈 차트, 컬러 옵션, 패브릭 클로즈업)
- "bypass" — 밀로에 그 기능 없음 → swap에서 그 기능 그리지 않고 milo의 다른 강점으로 대체 카피
  (예: 한샘 panel이 리클라이너 강조면, 밀로엔 리클라이너 없으니 → 덕페더 포근함 강조 카피로 대체)
- "skip" — 밀로에 그 정보 누락 (예: 한샘 panel이 품질보증·delivery 등 detail page에 없는 정보를 강조하면 — 정보 부재)

각 panel에 대해 JSON으로:
{{
  "panel_idx": int,
  "verdict": "match|bypass|skip",
  "hanssem_feature": "한샘 panel이 강조하는 기능/정보 한 줄",
  "milo_has_it": bool,
  "reasoning": "왜 그렇게 판단했는지 한 줄",
  "alt_title": "bypass 시 milo 강점 헤드라인 (한국어 짧게)" or null,
  "alt_body": "bypass 시 milo 본문 (한국어 1-2문장)" or null,
  "overlay_label": "우회 | 정보누락 | null"
}}

INPUT panels:
{panels}

Return JSON: {{ "resolutions": [...] }}. No preamble.
"""

panels_str = json.dumps(panel_facts, ensure_ascii=False, indent=2)
milo_summary = (
    f"- 좌석수: {milo_spec.get('seat_count')}인\n"
    f"- 사이즈: {milo_spec.get('dimensions',{}).get('width_cm','?')}×"
    f"{milo_spec.get('dimensions',{}).get('depth_cm','?')}×"
    f"{milo_spec.get('dimensions',{}).get('height_cm','?')}cm\n"
    f"- 패브릭 (가죽 X): {milo_spec.get('material',{}).get('upholstery','')}\n"
    f"- 좌방석: {milo_spec.get('material',{}).get('seat_cushion','')}\n"
    f"- 등쿠션: {milo_spec.get('material',{}).get('back_cushion','')}\n"
    f"- 컬러: {', '.join(milo_spec.get('colors') or [])}\n"
    f"- 리클라이너: 없음 / 헤드레스트: {milo_visual.get('back',{}).get('headrest', False)} / USB·컨트롤: 없음\n"
    f"- 다리: {milo_visual.get('legs',{}).get('count')} 슬림 메탈"
)

print("analysing panel mismatches...")
resp = client.chat.completions.create(
    model=config.VISION_MODEL,
    messages=[{"role": "user", "content":
        PROMPT.format(milo_summary=milo_summary, panels=panels_str)
    }],
    response_format={"type": "json_object"},
    temperature=0.1,
)
result = json.loads(resp.choices[0].message.content)

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {OUT}\n")
for r in result["resolutions"]:
    label = r.get("overlay_label") or "—"
    print(f"  panel_{r['panel_idx']:02d}: {r['verdict']:>6}  [{label:>6}]  {r.get('hanssem_feature','')[:60]}")
    if r["verdict"] == "bypass":
        print(f"    → {r.get('alt_title','')} / {r.get('alt_body','')[:50]}")

"""밀로(777039) 페이지의 design_chart/size/소재/컬러 panel을 vision으로 분석.

운영 시 가정: 제품 담당자가 업로드 존(제품샷/소재/컬러) 분리 입력.
지금: 우리가 panel들을 다 vision으로 훑어 분류 + spec 추출.

캐시: user_products/milo_777039/spec.json
"""

import json
import os
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
from openai import OpenAI  # noqa: E402
import config  # noqa: E402
from lib import data_uri  # noqa: E402

HERE = Path(__file__).parent
USER_DIR = HERE / "user_products/milo_777039"
OUT = USER_DIR / "spec.json"

if OUT.exists():
    print(f"cached: {OUT} — skip")
    sys.exit(0)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# 모든 panel을 vision으로 분류 + spec 추출
panels = sorted(USER_DIR.glob("panel_*.*"))
print(f"analysing {len(panels)} milo panels for spec...")

CLASSIFY_PROMPT = """\
You are analysing a single panel image from a Korean furniture (sofa) product
detail page. Classify and extract structured information.

Return JSON with these keys:
- "category" (str): one of "intro" / "size_chart" / "material" / "color_option" /
  "seat_cushion" / "back_cushion" / "model_option" / "lifestyle" / "detail" /
  "delivery" / "guarantee" / "other"
- "extracted_info" (str): any visible text/numbers about dimensions, material
  composition, color names, model variants, or other spec — verbatim if Korean
- "for_input_zone" (str): which upload zone this image would belong to —
  one of "product_shot" / "material" / "color" / "spec" / "context" / "skip"
No preamble.
"""

results = []
for p in panels:
    if p.suffix == ".gif":
        continue
    print(f"  {p.name}...", end=" ", flush=True)
    try:
        resp = client.chat.completions.create(
            model=config.VISION_MODEL,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": CLASSIFY_PROMPT},
                {"type": "image_url", "image_url": {"url": data_uri(p)}},
            ]}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        data = json.loads(resp.choices[0].message.content)
        data["panel"] = p.name
        results.append(data)
        print(f"[{data.get('category','?')}/{data.get('for_input_zone','?')}]")
    except Exception as e:
        print(f"ERR: {e}")

# Now synthesize a structured product spec from all collected info
SYNTHESIZE_PROMPT = """\
You are given multiple structured analyses of panels from a Korean sofa
detail page for "밀로 패브릭소파" (MILO fabric sofa). Synthesise the product
spec into a clean JSON. The product is the **2-seat (2인용)** variant
specifically — extract only the 2인용 information when multiple options exist.

Return JSON:
{
  "product_name": "밀로 패브릭소파 2인용",
  "seat_count": 2,
  "dimensions": {"width_cm": int|null, "depth_cm": int|null, "height_cm": int|null,
                 "seat_height_cm": int|null, "arm_height_cm": int|null},
  "material": {"upholstery": str, "seat_cushion": str, "back_cushion": str,
               "frame": str|null},
  "colors": [list of color names in Korean],
  "warranty": str|null,
  "key_features": [list of short Korean phrases],
  "delivery": str|null,
  "ko_summary": "2-3 Korean sentences summarising the product"
}
No preamble. If a field is unknown, use null or empty list.
"""

print("\nsynthesizing spec from all panels...")
resp = client.chat.completions.create(
    model=config.VISION_MODEL,
    messages=[{"role": "user", "content": (
        "Panel analyses (JSON list):\n"
        + json.dumps(results, ensure_ascii=False, indent=2)
        + "\n\n" + SYNTHESIZE_PROMPT
    )}],
    response_format={"type": "json_object"},
    temperature=0.1,
)
spec = json.loads(resp.choices[0].message.content)

OUT.write_text(json.dumps({
    "spec": spec,
    "panel_classifications": results,
}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\nspec extracted to {OUT}")
print(f"  product: {spec.get('product_name')}")
print(f"  dimensions: {spec.get('dimensions')}")
print(f"  material: {spec.get('material')}")
print(f"  colors: {spec.get('colors')}")
print(f"  ko_summary: {spec.get('ko_summary')}")

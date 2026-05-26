"""992474 template panel 재분류 — input_zone + layout_type 정확히.

기존 precomputed.json (intro/detail/design_chart)을 더 세분화.
결과: templates/01_sofa_992474/panel_layout_types.json
"""

import json
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import openai_client as client, data_uri  # noqa: E402

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
OUT = TPL_DIR / "panel_layout_types.json"

CLASSIFY_PROMPT = """\
You are analysing a single panel image from a Korean sofa detail page.
Classify the panel's role and the layout-preservation requirement for image
generation (swap).

Return JSON:
- "input_zone" (str): one of
    "product_shot" / "material_swatch" / "color_option" / "size_chart" /
    "structure_chart" / "module_lineup" / "lifestyle_scene" /
    "detail_close_up" / "intro_hero" / "delivery_info" / "context" / "other"
- "layout_type" (str):
    "fixed_layout" — chart/diagram/grid/table — STRUCTURE MUST BE PRESERVED
        (size_chart / structure_chart / color_option / module_lineup /
        material_swatch in chart form)
    "flexible_staging" — room/lifestyle/detail close-up — staging can vary
    "strict_white_bg" — cover/intro hero on clean white backdrop
    "other"
- "visible_korean_text" (str): all visible Korean text/numbers verbatim
- "swap_strategy_hint" (str): brief instruction for how to swap this panel —
    e.g. "preserve dimension lines, replace sofa silhouette only" or
    "reproduce room lighting but render new sofa"
- "key_facts_to_preserve" (list of str): what must be kept (text, charts,
    dimensions, color swatches, etc.)
No preamble.
"""


def main():
    panel_paths = sorted([p for p in TPL_DIR.glob("panel_*.*") if p.is_file()])
    print(f"classifying {len(panel_paths)} template panels...")

    results = []
    for p in panel_paths:
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
            d = json.loads(resp.choices[0].message.content)
            d["panel"] = p.name
            d["panel_idx"] = int(p.stem.split("_")[1])
            results.append(d)
            print(f"  {p.name}: zone={d.get('input_zone'):>18}  layout={d.get('layout_type'):>16}")
        except Exception as e:
            print(f"  {p.name}: ERR {e}")
            results.append({"panel": p.name, "error": str(e)})

    OUT.write_text(json.dumps({"panels": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")

    # tally
    by_layout = {}
    by_zone = {}
    for r in results:
        by_layout[r.get("layout_type", "?")] = by_layout.get(r.get("layout_type", "?"), 0) + 1
        by_zone[r.get("input_zone", "?")] = by_zone.get(r.get("input_zone", "?"), 0) + 1
    print(f"\nby layout: {by_layout}")
    print(f"by zone: {by_zone}")


if __name__ == "__main__":
    main()

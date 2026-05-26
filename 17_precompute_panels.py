"""#1 sofa 992474의 12 panels scene + 밀로 product reference vision 분석.

캐시: templates/01_sofa_992474/precomputed.json
이미 있으면 skip — 매번 호출 X.
"""

import json
import sys
from pathlib import Path

# add 5th/experiment to import path
EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import vision_describe  # noqa: E402

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"
OUT = TPL_DIR / "precomputed.json"

# panel별 scene 분석 prompt (5th SCENE_ANALYZE 패턴 + panel intent 추가)
SCENE_ANALYZE_PROMPT = """\
You are analysing a single panel image from a furniture (sofa) product detail
page so it can be reproduced by an image generator. Describe ONLY the staging
(not the specific sofa model itself): camera viewpoint and angle, framing and
crop (full / wide / close / partial), how the furniture is positioned in
frame, the room/backdrop, props, lighting, the apparent intent of this panel
(cover / introduces material / shows size / highlights option / demonstrates
module / lifestyle scene / detail crop / chart-style informative graphic),
and overall mood.

Also classify the panel as one of: "cover", "design_chart" (size/material/
spec diagram, mostly informational), "lifestyle" (room/model context),
"detail" (close-up texture/component), "intro" (hero shot).

Return JSON: {"description": "3-5 dense sentences", "panel_class": "cover|design_chart|lifestyle|detail|intro"}.
No preamble.
"""

PRODUCT_ANALYZE_PROMPT = """\
You are analysing a Korean fabric sofa product called "밀로 패브릭소파 3인용"
(MILO fabric 3-seat sofa) from a multi-angle reference set so an image
generator can preserve it exactly. Describe its defining form precisely:
overall silhouette and proportions, seat count, arm shape (rounded, boxy,
rolled, flat, etc.), back and seat cushion count/shape, leg or base style,
upholstery material and color (fabric — not leather), and any decorative
seams or surface details. Write 3-5 dense sentences in English, concrete and
specific. Emphasise that this is fabric (not leather). No preamble.
"""


def main():
    if OUT.exists():
        print(f"cached: {OUT} — skip vision calls")
        return

    # collect panels
    panel_imgs = sorted(TPL_DIR.glob("panel_*.*"))
    print(f"found {len(panel_imgs)} panels")

    scenes = {}
    import json as _json
    for p in panel_imgs:
        idx = int(p.stem.split("_")[1])
        print(f"  analysing panel_{idx:02d}...", end=" ", flush=True)
        try:
            # request JSON response
            from openai import OpenAI
            import os
            from lib import data_uri as _data_uri
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            resp = client.chat.completions.create(
                model=config.VISION_MODEL,
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": SCENE_ANALYZE_PROMPT},
                    {"type": "image_url", "image_url": {"url": _data_uri(p)}},
                ]}],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = resp.choices[0].message.content
            data = _json.loads(content)
            scenes[f"panel_{idx:02d}"] = data
            print(f"[{data.get('panel_class','?')}] {data['description'][:60]}...")
        except Exception as e:
            print(f"ERR: {e}")
            scenes[f"panel_{idx:02d}"] = {"description": "", "panel_class": "unknown", "error": str(e)}

    # product analyse — use main panel_01 of milo
    product_refs = [USER_DIR / "panel_01.jpg"]  # main hero
    # also include gif frames for multi-angle
    product_refs += sorted((USER_DIR / "gif_frames").glob("frame_*.jpg"))[:3]
    # combined description using first ref only (simpler)
    product_ref = USER_DIR / "panel_01.jpg"
    print(f"\n  analysing product {product_ref.name}...", end=" ", flush=True)
    product_desc = vision_describe(product_ref, PRODUCT_ANALYZE_PROMPT)
    print(product_desc[:80] + "...")

    OUT.write_text(json.dumps({
        "scenes": scenes,
        "product": product_desc,
        "product_refs": [str(p.relative_to(HERE)) for p in product_refs],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()

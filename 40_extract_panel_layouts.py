"""각 panel(992474)을 vision으로 자세히 묘사 — layout map.

기존 precomputed.json의 scene description은 너무 일반적. swap prompt에서
"어떤 element가 어디에 있는지" 명시 부족.

각 panel에 대해 vision으로 추출:
- spatial_layout: 5-8 dense sentences (요소가 어디에 어떻게 위치)
- key_elements: list — {role, position, description}
- text_overlay_zones: 한샘 텍스트가 어디에 있는지 (HTML overlay 위치 후보)
- zone-specific data:
  · size_chart: dim_lines [{start, end, label, value}]
  · color_option: swatches [{position, color_name, ...}]
  · structure_chart: regions [{anchor, material}]

결과: templates/01_sofa_992474/panel_layout_maps.json
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
OUT = TPL_DIR / "panel_layout_maps.json"

PROMPT = """\
당신은 가구 detail page panel을 vision으로 정밀 분석합니다.
출력은 AI 이미지 생성기의 swap prompt에 통째 inject되어, 새 sofa로 swap한
결과가 원본 panel의 layout을 정확히 보존하도록 사용됩니다.

이 panel 이미지를 다음 schema로 반환하세요:
{
  "panel_class": str — "intro_hero" / "lifestyle_scene" / "size_chart" /
    "structure_chart" / "color_option" / "module_lineup" / "material_swatch" /
    "detail_close_up" / "delivery_info" / "context" / "other"
  "spatial_layout": str — 5-8 dense sentences. 각 요소가 어디에 어떻게 위치하는지
    구체 묘사 (예: "sofa가 frame 좌측 상단 60% 영역에 정면 측면으로 배치, 우측
    하단에 dim line 좌→우로 측정값 표시, 좌하단에 firmness bar 2개 수직 배치").
    좌측/우측/상단/하단/중앙 명확히. 텍스트 위치도 명시 (있다면).
  "elements": [{"role": str, "position": str, "description": str}] — 각 요소
    리스트 (sofa / dim_line / firmness_bar / color_swatch / chart_region /
    text_label / room_props 등).
  "text_zones": [{"region": str, "content": str}] — 한국어 텍스트가 박힌 영역
    (HTML overlay 후보).
  "fixed_layout": bool — 이 panel이 chart/diagram/grid (구조 보존 필수)인지.
  "swap_instruction": str — swap 시 정확히 어떻게 sofa region만 교체하고 layout을
    보존할지 1-2 문장 instruction.
}
No preamble. JSON only.
"""


def main():
    panels = sorted([p for p in TPL_DIR.glob("panel_*.*") if p.suffix in {".jpg", ".jpeg", ".png", ".gif"}])
    print(f"analysing {len(panels)} panels with vision...")
    results = []
    for p in panels:
        idx = int(p.stem.split("_")[1])
        print(f"  panel_{idx:02d}...", end=" ", flush=True)
        try:
            target = p
            if p.suffix == ".gif":
                # use a frame instead (vision can't always handle GIF)
                # find any frame in user_products or use the gif directly (PIL handles it)
                pass
            resp = client.chat.completions.create(
                model=config.VISION_MODEL,
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": data_uri(target)}},
                ]}],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            d = json.loads(resp.choices[0].message.content)
            d["panel"] = p.name
            d["panel_idx"] = idx
            results.append(d)
            print(f"[{d.get('panel_class','?'):>16}] fixed={d.get('fixed_layout', False)}")
        except Exception as e:
            print(f"ERR: {e}")
            results.append({"panel": p.name, "panel_idx": idx, "error": str(e)})

    # cover separate (1:1)
    cover = TPL_DIR / "_cover_1000.jpg"
    if cover.exists():
        print(f"  cover...", end=" ", flush=True)
        try:
            resp = client.chat.completions.create(
                model=config.VISION_MODEL,
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": data_uri(cover)}},
                ]}],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            d = json.loads(resp.choices[0].message.content)
            d["panel"] = "cover"
            d["panel_idx"] = 0
            results.append(d)
            print(f"[{d.get('panel_class','?'):>16}]")
        except Exception as e:
            print(f"ERR: {e}")

    OUT.write_text(json.dumps({"panels": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()

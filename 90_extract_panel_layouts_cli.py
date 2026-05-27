"""template 디렉토리 인자로 받는 일반화 panel_layout_maps.json 추출기.

사용:
  python3 90_extract_panel_layouts_cli.py templates/02_wardrobe_1066850
  python3 90_extract_panel_layouts_cli.py --all   # 모든 templates/0?_*/ 처리
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import openai_client as client, data_uri  # noqa: E402

HERE = Path(__file__).parent

PROMPT = """\
당신은 가구/생활용품 detail page panel을 vision으로 정밀 분석합니다.
출력은 swap pipeline의 prompt에 inject되어 layout 보존에 사용됩니다.

이 panel 이미지를 다음 schema로 반환:
{
  "panel_class": str,  # intro_hero / lifestyle_scene / size_chart / structure_chart /
                       # color_option / module_lineup / material_swatch / detail_close_up /
                       # delivery_info / context / other
  "spatial_layout": str,  # 5~8개 dense 문장. 각 요소의 위치/크기/방향 명확
  "elements": [{"role": str, "position": str, "description": str}],
  "text_zones": [{"region": str, "content": str}],
  "fixed_layout": bool,  # chart/diagram/grid 인지
  "swap_instruction": str  # swap 시 어떻게 product region만 교체하고 layout 보존할지
}

No preamble. JSON only.
"""


async def analyze_panel(panel_path: Path, panel_label: str) -> dict:
    try:
        resp = await asyncio.to_thread(
            client.chat.completions.create,
            model=config.VISION_MODEL,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": data_uri(panel_path)}},
            ]}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        d = json.loads(resp.choices[0].message.content)
        d["panel"] = panel_label
        return d
    except Exception as e:
        return {"panel": panel_label, "error": str(e)}


async def process_template(tpl_dir: Path) -> None:
    out_path = tpl_dir / "panel_layout_maps.json"
    if out_path.exists():
        print(f"  ✓ {tpl_dir.name}: 이미 존재 — skip ({out_path.name})")
        return
    panels = sorted([p for p in tpl_dir.glob("panel_*.*") if p.suffix in {".jpg", ".jpeg", ".png", ".gif"}])
    cover = tpl_dir / "_cover_1000.jpg"
    print(f"  {tpl_dir.name}: {len(panels)} panels + {'cover' if cover.exists() else 'no cover'}")

    tasks = []
    for p in panels:
        idx = int(p.stem.split("_")[1])
        label_data = {"path": p, "label": p.name, "panel_idx": idx}
        tasks.append((label_data, analyze_panel(p, p.name)))
    if cover.exists():
        tasks.append(({"path": cover, "label": "cover", "panel_idx": 0}, analyze_panel(cover, "cover")))

    results = await asyncio.gather(*[t[1] for t in tasks])
    panels_out = []
    for (meta, _), d in zip(tasks, results):
        d["panel_idx"] = meta["panel_idx"]
        panels_out.append(d)
    panels_out.sort(key=lambda x: x.get("panel_idx", 999))

    out_path.write_text(
        json.dumps({"panels": panels_out}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    classes = ", ".join(f"{p.get('panel_idx',0):02d}={p.get('panel_class','?')[:14]}" for p in panels_out)
    print(f"  → {out_path.relative_to(HERE)} · classes: {classes[:200]}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", nargs="?", help="templates/0X_<category>_<gdsNo>")
    parser.add_argument("--all", action="store_true", help="모든 templates/ 처리")
    parser.add_argument("--force", action="store_true", help="기존 panel_layout_maps.json 있어도 재생성")
    args = parser.parse_args()

    if args.all:
        targets = sorted((HERE / "templates").glob("0?_*"))
    elif args.template:
        targets = [Path(args.template).resolve()]
    else:
        parser.error("template 인자 또는 --all 필요")
    print(f"processing {len(targets)} template(s)...\n")
    for tpl in targets:
        if args.force:
            (tpl / "panel_layout_maps.json").unlink(missing_ok=True)
        await process_template(tpl)


if __name__ == "__main__":
    asyncio.run(main())

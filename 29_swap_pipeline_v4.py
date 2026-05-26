"""Swap pipeline v4 — panel layout-type별 다른 entry strategy + zone-aware refs.

panel별 처리:
  strict_white_bg (cover, product_shot)
    → entry: aligned, 1:1 white seamless, GIF refs
  fixed_layout (size_chart, structure_chart, color_option, module_lineup)
    → entry: structure_preserve_overpaint, 원본 layout/chart/text 그대로 유지하면서
      sofa region만 정확히 swap. dim 수치 / 컬러명 / 구조 정보는 spec에서 정확히 prompt에.
  flexible_staging (lifestyle, detail_close_up)
    → entry: aligned, 원본 staging 따라가되 sofa는 정확

fallback: aligned → overpaint → smart_sheet.

각 panel은 zone에 맞는 spec sub-section만 prompt에 (예: size_chart에는 dimensions만,
material 관련 panel에는 material만).
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
import fal_client  # noqa: E402
from lib import download, upload, openai_client, data_uri  # noqa: E402

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"

LAYOUT_TYPES = json.loads((TPL_DIR / "panel_layout_types.json").read_text())
PANEL_LAYOUT = {p["panel"]: p for p in LAYOUT_TYPES["panels"] if "panel_idx" in p}
PRECOMP = json.loads((TPL_DIR / "precomputed.json").read_text())
USER_OUTPUT = json.loads((USER_DIR / "auto_pipeline_output.json").read_text())

SPEC = USER_OUTPUT["spec"]
VISUAL = USER_OUTPUT["visual"]
USER_REQUEST_TXT = USER_OUTPUT.get("user_override", {}).get(
    "user_request_text", "패브릭 강조, 거실 따뜻한 톤. 2인용 STRICT."
)

OUT_ROOT = TPL_DIR / "swap_results"
OUT_ROOT.mkdir(exist_ok=True)

MODEL_NAME = "gpt_image"
ENDPOINT = config.MODELS[MODEL_NAME]
CONCURRENCY = 4
MAX_ATTEMPTS = 3

# References by zone (milo) — use_product 폴더에 담당자 분류된 자료
USE_PROD = USER_DIR / "use_product"
GIF_FRAMES = sorted(USE_PROD.glob("p08_frame_*.jpg"))  # 제품 다각도
MATERIAL_REFS = sorted(USE_PROD.glob("material*.png"))  # 소재
COLOR_REFS = sorted(USE_PROD.glob("color_*.png"))  # 컬러 3종
SMART_SHEET = USER_DIR / "smart_sheet.jpg"
USER_COVER = USER_DIR / "_cover_1000.jpg"

# zone별 reference 매핑 — 어떤 zone panel에 어떤 ref 추가로 보낼지
def refs_for_zone(zone: str, urls: dict) -> list[str]:
    """Return list of fal-uploaded ref URLs for this panel zone (after base panel)."""
    base = list(urls["gif"])  # always include product
    if zone in ("material_swatch",):
        return base + list(urls.get("material", []))
    if zone in ("color_option", "module_lineup"):
        return base + list(urls.get("color", []))
    return base


def thresholds_for(layout_type: str, zone: str) -> tuple[int, int]:
    if layout_type == "strict_white_bg":
        return (95, 95)
    if layout_type == "fixed_layout":
        return (93, 92)  # composition must be high (layout preserved)
    return (93, 80)


def aspect_ratio_for(w: int, h: int) -> str:
    r = w / h
    candidates = [
        ("21:9", 21/9), ("16:9", 16/9), ("3:2", 3/2), ("4:3", 4/3),
        ("1:1", 1.0), ("3:4", 3/4), ("2:3", 2/3), ("9:16", 9/16), ("9:21", 9/21),
    ]
    return min(candidates, key=lambda c: abs(c[1] - r))[0]


def build_zone_facts_block(zone: str) -> str:
    """Return only the spec sub-section relevant to this panel's zone."""
    dims = SPEC.get("dimensions", {}) or {}
    mat = SPEC.get("material", {}) or {}
    colors = SPEC.get("colors") or []
    seat_n = SPEC.get("seat_count", 2)

    base = f"PRODUCT: {SPEC.get('product_name')} ({seat_n}-seat STRICTLY)"

    if zone == "size_chart":
        return f"""\
{base}
PANEL ZONE: size_chart
Exact dimensions to render visually (NO TEXT in output):
  - seat_height: {dims.get('seat_height_cm','?')}cm
  - arm_height: {dims.get('arm_height_cm','?')}cm
  - seat_depth: {dims.get('seat_depth_cm','?')}cm
The size_chart visual layout (dimension lines, the small silhouette diagram)
must be preserved exactly. Only the sofa silhouette inside the chart should
match MILO 2-seat. Do NOT render dimension numbers as text — render as
visual lines only (numbers will be HTML-overlaid)."""
    if zone == "structure_chart":
        return f"""\
{base}
PANEL ZONE: structure_chart
Material structure to depict (no text in output):
  - seat cushion: {mat.get('seat_cushion','')}
  - back cushion: {mat.get('back_cushion','')}
  - frame: {mat.get('frame','')}
  - upholstery: {mat.get('upholstery','')}
Preserve the cross-section / cutaway diagram layout exactly. Replace only the
sofa silhouette with MILO 2-seat. Internal layer labels will be HTML-overlaid."""
    if zone == "color_option":
        return f"""\
{base}
PANEL ZONE: color_option
Color variants (render as fabric swatches in grid — NO TEXT):
  {', '.join(colors)}
Preserve the grid layout exactly. Each cell shows the MILO 2-seat in the
respective fabric color. Color names will be HTML-overlaid."""
    if zone == "module_lineup":
        return f"""\
{base}
PANEL ZONE: module_lineup — show ONLY the {seat_n}-seat variant.
Do not render multiple seat counts in a row."""
    if zone == "material_swatch":
        return f"""\
{base}
PANEL ZONE: material_swatch
Show fabric texture close-up: {mat.get('upholstery','패브릭')}.
Render the fabric weave and primary color ({VISUAL.get('upholstery',{}).get('primary_color','beige')})."""

    # general
    return f"""\
{base}
PANEL ZONE: {zone}
Full spec available — use product references (GIF frames) for visual fidelity."""


def build_prompt(panel_meta: dict, *, strategy: str, layout_type: str) -> str:
    zone = panel_meta.get("input_zone", "other")
    visible_text = panel_meta.get("visible_korean_text", "")
    swap_hint = panel_meta.get("swap_strategy_hint", "")
    facts = build_zone_facts_block(zone)

    layout_rule = ""
    if layout_type == "fixed_layout":
        layout_rule = (
            "\n\nFIXED LAYOUT — STRUCTURE PRESERVATION RULE:\n"
            "- The ORIGINAL panel is a chart / diagram / grid / table.\n"
            "- Preserve the EXACT layout: dimension lines, swatch cells, grid "
            "alignment, cross-sections, internal structure.\n"
            "- Replace ONLY the sofa silhouette with MILO 2-seat.\n"
            "- Do NOT redraw the chart structure with creative staging.\n"
            f"- Original visible Korean text (DO NOT render in output, will be HTML-overlaid): {visible_text[:200]}\n"
        )
    elif layout_type == "strict_white_bg":
        layout_rule = (
            "\n\nSTRICT WHITE-BG RULE:\n"
            "- Clean white seamless backdrop, eye-level straight-on view.\n"
            "- Centered framing, soft even shadowless light, no props.\n"
            "- Sofa fills ~70-75% of horizontal frame.\n"
            "- STRICTLY 2-seat. Count cushions before rendering."
        )
    else:  # flexible_staging
        layout_rule = (
            "\n\nFLEXIBLE STAGING RULE:\n"
            "- Reproduce the original panel's room/lighting/camera/atmosphere.\n"
            "- Sofa staging can vary slightly but product fidelity is critical."
        )

    strat_note = ""
    if strategy == "overpaint":
        strat_note = (
            "\n\nOVERPAINT PASS: IMAGE 1 is the previous attempt. Redraw the "
            "sofa region only; keep the rest intact."
        )
    elif strategy == "smart_sheet":
        strat_note = (
            "\n\nSMART-SHEET ASSIST: IMAGE 2 is the multi-angle product "
            "composite (use as authoritative product reference)."
        )

    text_rule = (
        "\n\nABSOLUTE — NO TEXT IN OUTPUT:\n"
        "- Zero Korean/English characters/numbers/captions.\n"
        "- Render only visual elements; text is added as HTML overlay."
    )

    visual_para = VISUAL.get("full_visual_paragraph", "")
    return f"""\
TASK: photorealistic furniture detail-page panel reproduction (product swap).

Reference images (in order):
- IMAGE 1 = {'PREVIOUS ATTEMPT' if strategy == 'overpaint' else 'ORIGINAL PANEL'}.
- {'IMAGE 2 = SMART SHEET (multi-angle composite). IMAGES 3-N = individual frames.' if strategy == 'smart_sheet' else 'IMAGES 2..N = MILO product frames (GIF 360° slices).'}

ORIGINAL PANEL STAGING (vision-extracted):
{panel_meta.get('scene_desc','(no desc)')}

PANEL ZONE & FACTS:
{facts}

USER REQUEST: {USER_REQUEST_TXT}

PRODUCT VISUAL REFERENCE (the MILO 2-seat sofa):
{visual_para}

{layout_rule}{strat_note}{text_rule}

Render the MILO 2-seat fabric sofa. Fabric (NOT leather). 4 slim matte-black
metal legs. 2 seat + 2 back cushions. Boxy arms slightly lower than backrest.
Light-beige linen-look upholstery with piped seams.
"""


def qa_one(panel_orig: Path, swap_result: Path, layout_type: str, zone: str) -> dict:
    prod_thr, comp_thr = thresholds_for(layout_type, zone)
    product_ref = GIF_FRAMES[0] if GIF_FRAMES else USER_COVER

    qa_prompt = (
        f"You are evaluating an AI-generated panel swap.\n"
        f"Panel layout_type: '{layout_type}', zone: '{zone}'.\n"
        f"Product threshold: {prod_thr}+. Composition threshold: {comp_thr}+.\n"
        "Target: MILO 2-SEAT fabric sofa. STRICTLY 2 seats. Fabric not leather.\n\n"
        f"{'For fixed_layout: the chart/diagram/grid STRUCTURE of C must be preserved in B. Score composition based on layout preservation.' if layout_type == 'fixed_layout' else ''}\n\n"
        "Compare:\n  A = product reference (MILO 2-seat)\n  B = generated swap\n  C = original panel\n\n"
        "Return JSON:\n"
        '  "seat_count_in_B" (int)\n'
        '  "product_score" (0-100)\n'
        '  "composition_score" (0-100)\n'
        '  "text_in_image" (bool)\n'
        '  "structure_preserved" (bool): for fixed_layout, was chart/diagram structure kept?\n'
        '  "notes" (str)\n'
        f'  "verdict" ("pass"|"retry"): pass only if seat_count_in_B == 2 AND '
        f"product_score >= {prod_thr} AND composition_score >= {comp_thr} AND "
        "not text_in_image" +
        (" AND structure_preserved" if layout_type == "fixed_layout" else "") + "."
    )
    resp = openai_client.chat.completions.create(
        model=config.VISION_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": qa_prompt},
            {"type": "text", "text": "IMAGE A:"},
            {"type": "image_url", "image_url": {"url": data_uri(product_ref)}},
            {"type": "text", "text": "IMAGE B:"},
            {"type": "image_url", "image_url": {"url": data_uri(swap_result)}},
            {"type": "text", "text": "IMAGE C:"},
            {"type": "image_url", "image_url": {"url": data_uri(panel_orig)}},
        ]}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)


async def generate(prompt: str, ref_urls: list[str], aspect_ratio: str) -> str:
    args = {"prompt": prompt, "image_urls": ref_urls, "aspect_ratio": aspect_ratio}
    try:
        result = await fal_client.subscribe_async(ENDPOINT, arguments=args)
    except Exception:
        args.pop("aspect_ratio", None)
        result = await fal_client.subscribe_async(ENDPOINT, arguments=args)
    imgs = result.get("images") or result.get("image")
    if isinstance(imgs, list) and imgs:
        first = imgs[0]
        return first["url"] if isinstance(first, dict) else first
    if isinstance(imgs, dict):
        return imgs["url"]
    raise ValueError(f"no image url: {str(result)[:200]}")


async def run_target(label: str, base_img: Path, panel_meta: dict,
                     urls: dict, out_dir: Path, ratio: str,
                     sem: asyncio.Semaphore) -> dict:
    layout_type = panel_meta.get("layout_type", "flexible_staging")
    zone = panel_meta.get("input_zone", "other")

    # entry strategy by layout type
    # all layouts: try aligned first, fall through to overpaint then smart_sheet
    strategies = ["aligned", "overpaint", "smart_sheet"]
    attempts = []
    prev_output: Path | None = None

    for attempt_n, strategy in enumerate(strategies, 1):
        tag = f"[{label}/{strategy}/#{attempt_n}]"
        async with sem:
            t0 = time.time()
            zone = panel_meta.get("input_zone", "other")
            zone_refs = refs_for_zone(zone, urls)
            if strategy == "overpaint":
                if not prev_output:
                    continue
                prev_url = await upload(prev_output)
                ref_urls = [prev_url] + zone_refs
            elif strategy == "smart_sheet":
                ref_urls = [urls[f"base_{label}"], urls["smart_sheet"]] + zone_refs
            else:
                ref_urls = [urls[f"base_{label}"]] + zone_refs

            prompt = build_prompt(panel_meta, strategy=strategy, layout_type=layout_type)
            print(f"{tag} layout={layout_type} zone={zone} ar={ratio} refs={len(ref_urls)}", flush=True)
            img = out_dir / f"{label}__a{attempt_n}_{strategy}.png"
            try:
                gurl = await generate(prompt, ref_urls, ratio)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"{tag} GEN ERR: {e}")
                attempts.append({"attempt": attempt_n, "strategy": strategy, "error": str(e)})
                continue

            try:
                verdict = await asyncio.to_thread(qa_one, base_img, img, layout_type, zone)
            except Exception as e:
                print(f"{tag} QA ERR: {e}")
                attempts.append({"attempt": attempt_n, "strategy": strategy, "image": img.name, "error": f"QA: {e}"})
                break

            t_end = time.time()
            attempts.append({
                "attempt": attempt_n, "strategy": strategy, "image": img.name,
                "gen_seconds": round(t_gen - t0, 1),
                "qa_seconds": round(t_end - t_gen, 1),
                "fal_url": gurl, "aspect_ratio": ratio,
                **verdict,
            })
            prev_output = img
            sf = "" if verdict.get("seat_count_in_B") == 2 else f" SEAT={verdict.get('seat_count_in_B')}"
            tf = " TEXT!" if verdict.get("text_in_image") else ""
            sp = "" if (layout_type != "fixed_layout" or verdict.get("structure_preserved")) else " STR!"
            print(f"{tag} prod={verdict.get('product_score','?')} comp={verdict.get('composition_score','?')}{sf}{tf}{sp} -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (passers[0] if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))

    prod_thr, comp_thr = thresholds_for(layout_type, zone)
    return {
        "label": label,
        "panel_idx": panel_meta.get("panel_idx"),
        "input_zone": zone,
        "layout_type": layout_type,
        "aspect_ratio": ratio,
        "thresholds": {"product": prod_thr, "composition": comp_thr},
        "attempts": attempts,
        "final": final,
        "passed": bool(passers),
        "strategies_used": [a["strategy"] for a in attempts if "strategy" in a],
    }


async def main():
    from PIL import Image

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"v4_{ts}"
    run_dir.mkdir()
    out_dir = run_dir / MODEL_NAME
    out_dir.mkdir()

    # build targets
    targets = []
    # cover
    cover_path = TPL_DIR / "_cover_1000.jpg"
    targets.append({
        "label": "cover", "path": cover_path,
        "panel_meta": {
            "panel": "cover", "panel_idx": None,
            "input_zone": "intro_hero", "layout_type": "strict_white_bg",
            "scene_desc": "Hero cover shot on a clean white seamless backdrop. "
                          "Eye-level straight-on view, centered framing, soft even "
                          "shadowless light, no props.",
        },
    })
    # template panels
    for sname, pdata in PRECOMP["scenes"].items():
        if not sname.startswith("panel_"):
            continue
        idx = int(sname.split("_")[1])
        ppath = next(TPL_DIR.glob(f"panel_{idx:02d}.*"))
        layout = PANEL_LAYOUT.get(ppath.name, {})
        targets.append({
            "label": sname, "path": ppath,
            "panel_meta": {
                "panel": ppath.name, "panel_idx": idx,
                "input_zone": layout.get("input_zone", "other"),
                "layout_type": layout.get("layout_type", "flexible_staging"),
                "visible_korean_text": layout.get("visible_korean_text", ""),
                "swap_strategy_hint": layout.get("swap_strategy_hint", ""),
                "scene_desc": pdata.get("description", ""),
            },
        })

    print(f"=== swap v4 — panel-aware ===")
    print(f"  model: {MODEL_NAME}")
    print(f"  targets: {len(targets)}")
    print(f"  strategies: aligned → overpaint → smart_sheet (auto)")

    print("\nuploading references...")
    gif_urls = await asyncio.gather(*[upload(p) for p in GIF_FRAMES])
    material_urls = await asyncio.gather(*[upload(p) for p in MATERIAL_REFS])
    color_urls = await asyncio.gather(*[upload(p) for p in COLOR_REFS])
    smart_url = await upload(SMART_SHEET)
    base_urls = {}
    for tg in targets:
        base_urls[f"base_{tg['label']}"] = await upload(tg["path"])
    urls = {
        **base_urls,
        "gif": list(gif_urls),
        "material": list(material_urls),
        "color": list(color_urls),
        "smart_sheet": smart_url,
    }
    print(f"  uploaded: {len(gif_urls)} gif, {len(material_urls)} material, {len(color_urls)} color")

    sem = asyncio.Semaphore(CONCURRENCY)
    t0 = time.time()
    jobs = []
    for tg in targets:
        w, h = Image.open(tg["path"]).size
        ratio = aspect_ratio_for(w, h)
        jobs.append(run_target(tg["label"], tg["path"], tg["panel_meta"],
                               urls, out_dir, ratio, sem))

    results = await asyncio.gather(*jobs, return_exceptions=True)
    cells = [r for r in results if isinstance(r, dict)]
    for r in results:
        if not isinstance(r, dict):
            print(f"  raised: {r!r}")

    wall = round(time.time() - t0, 1)
    summary = {
        "run": run_dir.name, "model": MODEL_NAME,
        "target_template": "01_sofa_992474",
        "user_product": "milo_777039",
        "wall_seconds": wall, "auto_fallback": True,
        "strategies": ["aligned", "overpaint", "smart_sheet"],
        "user_request": USER_REQUEST_TXT,
        "cells": cells,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_ROOT / "latest_v4.txt").write_text(run_dir.name)

    passers = sum(1 for c in cells if c["passed"])
    print(f"\n=== DONE === {run_dir}")
    print(f"  wall: {wall}s")
    print(f"  passers: {passers}/{len(cells)}")
    for c in cells:
        v = c.get("final") or {}
        s = "/".join(c.get("strategies_used", []))
        print(f"    {c['label']:12} [{c['layout_type']:>17}/{c['input_zone']:>15}] "
              f"prod={v.get('product_score','?')} comp={v.get('composition_score','?')} "
              f"seats={v.get('seat_count_in_B','?')} via={s} pass={c['passed']}")


if __name__ == "__main__":
    asyncio.run(main())

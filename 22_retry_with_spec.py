"""Retry — cover separate + design_chart panels with new prompts.

변경:
- cover: _cover_1000.jpg (1:1) base, GIF 3 frames만 ref
- design_chart (panel_04, 08, 11, 12): aspect ratio per panel, GIF refs only,
  text-free 강조, 밀로 spec 정보 포함
- 일반 panel (intro/detail): retain (기존 swap 결과 그대로)
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
from lib import download, upload, openai_client, data_uri  # noqa: E402
import fal_client  # noqa: E402

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"
PRECOMP = json.loads((TPL_DIR / "precomputed.json").read_text())
SPEC = json.loads((USER_DIR / "spec.json").read_text())["spec"]

OUT_ROOT = TPL_DIR / "swap_results"
OUT_ROOT.mkdir(exist_ok=True)
LATEST = (OUT_ROOT / "latest.txt").read_text().strip() if (OUT_ROOT / "latest.txt").exists() else None

CONCURRENCY = 4
MAX_ATTEMPTS = 2

# 운영 시나리오: GIF slice (사용자가 업로드한 것)만 reference
PRODUCT_REFS = sorted((USER_DIR / "gif_frames").glob("frame_*.jpg"))[:3]
assert PRODUCT_REFS, "GIF frames empty"

# panel별 aspect_ratio 매핑 (fal API enum)
def aspect_ratio_for(w: int, h: int) -> str:
    r = w / h
    candidates = [
        ("21:9", 21/9), ("16:9", 16/9), ("3:2", 3/2), ("4:3", 4/3),
        ("1:1", 1.0), ("3:4", 3/4), ("2:3", 2/3), ("9:16", 9/16), ("9:21", 9/21),
    ]
    return min(candidates, key=lambda c: abs(c[1] - r))[0]


def thresholds_for(panel_class: str) -> tuple[int, int]:
    if panel_class in ("cover", "intro"):
        return (95, 95)
    if panel_class == "design_chart":
        return (93, 90)
    return (93, 80)


def build_prompt(scene_desc: str, panel_class: str, is_cover: bool = False,
                 is_overpaint: bool = False) -> str:
    spec_block = (
        f"PRODUCT SPEC (the MILO fabric 2-seat sofa to render):\n"
        f"  Name: {SPEC.get('product_name')}\n"
        f"  Seat count: {SPEC.get('seat_count')}\n"
        f"  Material — upholstery: {SPEC.get('material',{}).get('upholstery','')}\n"
        f"  Material — seat cushion: {SPEC.get('material',{}).get('seat_cushion','')}\n"
        f"  Material — back cushion: {SPEC.get('material',{}).get('back_cushion','')}\n"
        f"  Frame: {SPEC.get('material',{}).get('frame','')}\n"
        f"  Colors: {', '.join(SPEC.get('colors') or [])}\n"
        f"  Seat height: {SPEC.get('dimensions',{}).get('seat_height_cm','?')}cm\n"
        f"  Arm height: {SPEC.get('dimensions',{}).get('arm_height_cm','?')}cm\n"
        f"  Summary (Korean for ref only — DO NOT render any text): {SPEC.get('ko_summary','')}\n"
    )

    cover_note = ""
    if is_cover or panel_class in ("cover", "intro"):
        cover_note = (
            "\nCOVER REQUIREMENTS: white seamless backdrop, eye-level "
            "straight-on view, perfectly centered framing, soft even "
            "shadowless light, no props, no shadows beyond a subtle floor "
            "shadow. Square 1:1 composition. The sofa should fill ~75% of "
            "the frame horizontally."
        )

    overpaint_note = ""
    if is_overpaint:
        overpaint_note = (
            "\n\nOVERPAINT PASS: IMAGE 1 is your previous attempt with "
            "product-fidelity issues. Redraw the sofa region to match the "
            "MILO references exactly. KEEP the rest intact."
        )

    text_rule = (
        "\n\nABSOLUTE RULE — NO TEXT IN OUTPUT IMAGE:\n"
        "- Do NOT render any Korean, English, numbers, brand marks, or "
        "captions in the output image. Zero text characters.\n"
        "- If the original panel showed dimension labels, color swatches, "
        "or spec text, render ONLY the visual elements (dimension lines "
        "without numbers, color swatches without color names). All text "
        "will be added separately as HTML.\n"
        "- The output must be a clean photograph or clean diagram, free of "
        "any written language."
    )

    return f"""\
TASK: photorealistic furniture detail-page panel reproduction (product swap).

Reference images (in order):
- IMAGE 1 = {'PREVIOUS ATTEMPT' if is_overpaint else 'ORIGINAL PANEL'}. Camera angle, framing, composition, backdrop, lighting.
- IMAGES 2..N = MILO product references (3 frames from product page GIF, multi-angle).

ORIGINAL PANEL STAGING (reproduce):
{scene_desc}

{spec_block}
PANEL TYPE: {panel_class}.{cover_note}{overpaint_note}{text_rule}

Render the MILO fabric 2-seat sofa in IMAGE 1's camera angle and staging.
FABRIC upholstery (not leather). Preserve silhouette / proportions / cushion
arrangement / color shown in the product references.
"""


# Custom generate that accepts aspect_ratio
async def generate_with_ratio(endpoint: str, prompt: str, ref_urls: list[str],
                              aspect_ratio: str) -> str:
    args = {
        "prompt": prompt,
        "image_urls": ref_urls,
        "aspect_ratio": aspect_ratio,
    }
    try:
        result = await fal_client.subscribe_async(endpoint, arguments=args)
    except Exception:
        # fallback: try without aspect_ratio
        args.pop("aspect_ratio", None)
        result = await fal_client.subscribe_async(endpoint, arguments=args)
    imgs = result.get("images") or result.get("image")
    if isinstance(imgs, list) and imgs:
        first = imgs[0]
        return first["url"] if isinstance(first, dict) else first
    if isinstance(imgs, dict):
        return imgs["url"]
    raise ValueError(f"no image url in fal result: {str(result)[:200]}")


def qa_one(panel_orig: Path, swap_result: Path, panel_class: str) -> dict:
    prod_thr, comp_thr = thresholds_for(panel_class)
    product_ref = USER_DIR / "gif_frames" / "frame_01.jpg"  # GIF first frame

    qa_prompt = (
        f"You are evaluating an AI-generated sofa-detail-page panel.\n"
        f"Panel class: '{panel_class}'. "
        f"Product fidelity threshold: {prod_thr}+. Composition threshold: {comp_thr}+.\n"
        "Compare IMAGE A (MILO product reference) vs IMAGE B (generated swap) "
        "vs IMAGE C (original panel for composition).\n\n"
        "Return JSON:\n"
        '  "product_score" (0-100): silhouette/proportions/fabric/cushions match\n'
        '  "composition_score" (0-100): camera/staging match to C\n'
        '  "text_in_image" (bool): true if any text/numbers/labels visible in B\n'
        '  "notes" (str): brief reason\n'
        f'  "verdict" ("pass"|"retry"): pass only if product_score >= {prod_thr} AND '
        f"composition_score >= {comp_thr} AND not text_in_image.\n"
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


async def run_cell(label: str, base_img: Path, scene_desc: str, panel_class: str,
                   model: str, urls: dict, out_dir: Path, ratio: str,
                   sem: asyncio.Semaphore) -> dict:
    endpoint = config.MODELS[model]
    out_dir = out_dir / model
    out_dir.mkdir(exist_ok=True)

    attempts = []
    prev_output = None
    is_cover_label = label == "cover"

    for attempt in range(1, MAX_ATTEMPTS + 1):
        tag = f"[{label}/{model}/#{attempt}]"
        async with sem:
            t0 = time.time()
            is_overpaint = attempt > 1 and prev_output is not None
            if is_overpaint:
                prev_url = await upload(prev_output)
                ref_urls = [prev_url] + urls["product"]
                mode = "K2_overpaint"
            else:
                ref_urls = [urls["base_" + label]] + urls["product"]
                mode = "K2_aligned"

            prompt = build_prompt(scene_desc, panel_class,
                                  is_cover=is_cover_label, is_overpaint=is_overpaint)

            print(f"{tag} {mode} ar={ratio} ({len(ref_urls)} refs)", flush=True)
            img = out_dir / f"{label}__a{attempt}.png"
            try:
                gurl = await generate_with_ratio(endpoint, prompt, ref_urls, ratio)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"{tag} GEN ERR: {e}")
                attempts.append({"attempt": attempt, "mode": mode, "error": str(e)})
                continue

            try:
                verdict = await asyncio.to_thread(qa_one, base_img, img, panel_class)
            except Exception as e:
                print(f"{tag} QA ERR: {e}")
                attempts.append({"attempt": attempt, "mode": mode, "image": img.name, "error": f"QA: {e}"})
                break

            t_end = time.time()
            attempts.append({
                "attempt": attempt, "mode": mode, "image": img.name,
                "gen_seconds": round(t_gen - t0, 1),
                "qa_seconds": round(t_end - t_gen, 1),
                "fal_url": gurl,
                "aspect_ratio": ratio,
                **verdict,
            })
            prev_output = img
            text_flag = " TEXT!" if verdict.get("text_in_image") else ""
            print(f"{tag} prod={verdict.get('product_score','?')} "
                  f"comp={verdict.get('composition_score','?')}{text_flag} -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (max(passers, key=lambda a: a.get("product_score", 0)) if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))

    return {
        "label": label,
        "model": model,
        "panel_class": panel_class,
        "aspect_ratio": ratio,
        "attempts": attempts,
        "final": final,
        "passed": bool(passers),
    }


async def main():
    from PIL import Image

    # targets: cover + design_chart panels
    cover_path = TPL_DIR / "_cover_1000.jpg"
    targets = [("cover", cover_path, "cover")]

    # design_chart panels from precomputed
    for sname, pdata in PRECOMP["scenes"].items():
        if pdata.get("panel_class") == "design_chart":
            idx = int(sname.split("_")[1])
            ppath = next(TPL_DIR.glob(f"panel_{idx:02d}.*"))
            targets.append((f"panel_{idx:02d}", ppath, "design_chart"))

    print(f"=== retry pipeline ===")
    print(f"  targets: {len(targets)}")
    for label, path, cls in targets:
        w, h = Image.open(path).size
        print(f"    {label} ({cls}) {w}x{h} -> ar {aspect_ratio_for(w, h)}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"retry_{ts}"
    run_dir.mkdir()

    print("\nuploading product refs (GIF 3 frames)...")
    product_urls = await asyncio.gather(*[upload(p) for p in PRODUCT_REFS])
    print(f"  done ({len(product_urls)})")

    print("uploading target panels...")
    target_urls = {}
    for label, path, _ in targets:
        target_urls[f"base_{label}"] = await upload(path)
        print(f"  {label} uploaded")

    urls = {**target_urls, "product": list(product_urls)}

    sem = asyncio.Semaphore(CONCURRENCY)
    t0 = time.time()
    scene_descs = PRECOMP["scenes"]

    jobs = []
    for label, path, cls in targets:
        if label == "cover":
            scene_desc = (
                "Hero cover shot of the sofa on a clean white seamless backdrop. "
                "Straight-on eye-level view, centered framing, soft even shadowless "
                "light, no props. 1:1 square aspect ratio."
            )
        else:
            scene_desc = scene_descs.get(label, {}).get("description", "")
        w, h = Image.open(path).size
        ratio = aspect_ratio_for(w, h)
        for model in config.MODELS:
            jobs.append(run_cell(label, path, scene_desc, cls, model,
                                 urls, run_dir, ratio, sem))

    results = await asyncio.gather(*jobs, return_exceptions=True)
    cells = [r for r in results if isinstance(r, dict)]
    for r in results:
        if not isinstance(r, dict):
            print(f"  raised: {r!r}")

    wall = round(time.time() - t0, 1)
    summary = {
        "run": run_dir.name,
        "target_template": "01_sofa_992474",
        "user_product": "milo_777039",
        "models": list(config.MODELS),
        "concurrency": CONCURRENCY,
        "max_attempts": MAX_ATTEMPTS,
        "total_wall_seconds": wall,
        "scope": "cover + design_chart only (others retained from previous run)",
        "previous_run": LATEST,
        "cells": cells,
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    passers = sum(1 for c in cells if c["passed"])
    print(f"\n=== DONE === {run_dir}")
    print(f"  wall: {wall}s")
    print(f"  passers: {passers}/{len(cells)}")
    for c in cells:
        v = c.get("final") or {}
        print(f"    {c['label']:12} {c['model']:18} prod={v.get('product_score','?')} "
              f"comp={v.get('composition_score','?')} pass={c['passed']}")


if __name__ == "__main__":
    asyncio.run(main())

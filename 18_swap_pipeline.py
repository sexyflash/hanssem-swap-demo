"""Swap pipeline — #1 sofa 992474 × 밀로 777039.

- 12 panels × 2 models (NB2, GPT-image-1.5) = 24 cells
- K2 정밀 = 1차 aligned + retry 시 overpaint (max 2회)
- Tiered thresholds: cover/intro 95/95, design_chart 93/90, 그 외 93/80
- 결과: templates/01_sofa_992474/swap_results/run_<ts>/{model}/panel_NN__aN.png
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
from lib import download, generate, upload, openai_client, data_uri  # noqa: E402

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"
PRECOMP = json.loads((TPL_DIR / "precomputed.json").read_text())
LLM_INPUT = json.loads((TPL_DIR / "llm_input.json").read_text())

OUT_ROOT = TPL_DIR / "swap_results"
OUT_ROOT.mkdir(exist_ok=True)

CONCURRENCY = 4
MAX_ATTEMPTS = 2

PRODUCT_REFS = [
    USER_DIR / "panel_01.jpg",
    *sorted((USER_DIR / "gif_frames").glob("frame_*.jpg"))[:3],
    USER_DIR / "panel_05.jpg",
    USER_DIR / "panel_07.jpg",
]
PRODUCT_REFS = [p for p in PRODUCT_REFS if p.exists()]


def thresholds_for(panel_class: str) -> tuple[int, int]:
    """(product, composition)."""
    if panel_class in ("cover", "intro"):
        return (95, 95)
    if panel_class == "design_chart":
        return (93, 90)
    return (93, 80)  # detail / lifestyle / default


def build_panel_prompt(scene_desc: str, product_desc: str, panel_class: str,
                       user_request: str, is_overpaint: bool) -> str:
    cover_note = ""
    if panel_class in ("cover", "intro"):
        cover_note = (
            " This panel is a hero/cover shot — STRICT requirements: white "
            "seamless backdrop, eye-level straight-on view, centered framing, "
            "soft even light, no props, no shadows beyond a subtle floor "
            "shadow."
        )
    overpaint_note = ""
    if is_overpaint:
        overpaint_note = (
            "\n\nOVERPAINT PASS: IMAGE 1 is your PREVIOUS attempt at this "
            "panel that had product-fidelity issues. Redraw ONLY the sofa "
            "region so it matches the MILO product references exactly. "
            "KEEP the rest of the panel intact (background, props, lighting, "
            "any informational graphics)."
        )
    return f"""\
TASK: photorealistic furniture detail-page panel reproduction (product swap).

Reference images (in order):
- IMAGE 1 = {'PREVIOUS ATTEMPT' if is_overpaint else 'ORIGINAL PANEL TO REPLACE'}. Defines camera
  angle, framing, composition, backdrop, lighting and staging.
- IMAGES 2..N = USER PRODUCT references (밀로 패브릭소파 / MILO fabric 3-seat
  sofa). Multi-angle clean references: main hero shot, rotation frames,
  detail shots.

ORIGINAL PANEL STAGING (analysed in advance — reproduce):
{scene_desc}

USER PRODUCT TO INSERT EXACTLY (FABRIC upholstery — NOT leather):
{product_desc}

USER REQUEST: {user_request}

PANEL TYPE: {panel_class}.{cover_note}{overpaint_note}

GENERATE one photorealistic detail-page panel: the MILO fabric sofa rendered
in IMAGE 1's exact camera angle, framing, composition and staging. The sofa
is fabric (not leather), with the silhouette and form shown in the product
references. KEEP any informational graphics/charts/dimensions visible in the
original panel — adapt their values to MILO's product if dimensions appear.

DO NOT invent decorations not present in the product references (no tufting,
no buttons, no quilting, no embossed patterns). DO NOT add Korean or other
text labels other than those already present. NO watermarks, NO logos.
"""


def qa_one(panel_orig: Path, swap_result: Path, panel_class: str) -> dict:
    prod_thr, comp_thr = thresholds_for(panel_class)
    product_ref = USER_DIR / "panel_01.jpg"

    qa_prompt = (
        "You are evaluating an AI-generated sofa-detail-page panel.\n"
        f"Panel class: '{panel_class}'. "
        f"Product fidelity threshold: {prod_thr}+. Composition threshold: {comp_thr}+.\n"
        "Compare:\n"
        "  IMAGE A = USER PRODUCT REFERENCE (밀로 fabric sofa — the true product to render)\n"
        "  IMAGE B = GENERATED SWAP RESULT (the panel candidate)\n"
        "  IMAGE C = ORIGINAL PANEL (reference for composition/staging)\n\n"
        "Return JSON with keys:\n"
        '  "product_score" (0-100): how exactly the sofa in B matches A in silhouette, '
        'proportions, fabric (NOT leather), cushion count/shape, arm shape, leg style, color\n'
        '  "composition_score" (0-100): how well B reproduces C\'s camera angle, framing, '
        "backdrop, lighting, staging\n"
        '  "ornament_violation" (bool): true if B has invented patterns/tufting/buttons absent in A\n'
        '  "notes" (str): brief reason\n'
        '  "verdict" ("pass"|"retry"): pass only if product_score >= '
        f"{prod_thr} AND composition_score >= {comp_thr} AND not ornament_violation.\n\n"
        "Be strict on product fidelity. Composition can be lenient for class='detail' "
        "(close-up texture doesn't need same camera). Cover/intro must be strict on both."
    )

    resp = openai_client.chat.completions.create(
        model=config.VISION_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": qa_prompt},
            {"type": "text", "text": "IMAGE A = USER PRODUCT REFERENCE:"},
            {"type": "image_url", "image_url": {"url": data_uri(product_ref)}},
            {"type": "text", "text": "IMAGE B = GENERATED SWAP:"},
            {"type": "image_url", "image_url": {"url": data_uri(swap_result)}},
            {"type": "text", "text": "IMAGE C = ORIGINAL PANEL:"},
            {"type": "image_url", "image_url": {"url": data_uri(panel_orig)}},
        ]}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)


async def run_panel(panel_idx: int, scene_data: dict, panel_path: Path,
                    user_request: str, urls: dict, model: str,
                    run_dir: Path, sem: asyncio.Semaphore) -> dict:
    panel_class = scene_data.get("panel_class", "unknown")
    scene_desc = scene_data.get("description", "")
    product_desc = PRECOMP["product"]
    endpoint = config.MODELS[model]
    prod_thr, comp_thr = thresholds_for(panel_class)

    out_dir = run_dir / model
    out_dir.mkdir(exist_ok=True)

    attempts = []
    prev_output = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        tag = f"[p{panel_idx:02d}/{model}/#{attempt}]"
        async with sem:
            t0 = time.time()
            is_overpaint = attempt > 1 and prev_output is not None
            if is_overpaint:
                prev_url = await upload(prev_output)
                ref_urls = [prev_url] + urls["product"]
                mode = "K2_overpaint"
            else:
                ref_urls = [urls["panels"][panel_idx]] + urls["product"]
                mode = "K2_aligned"

            prompt = build_panel_prompt(scene_desc, product_desc, panel_class,
                                        user_request, is_overpaint)

            print(f"{tag} {mode} ({len(ref_urls)} refs)", flush=True)
            img = out_dir / f"panel_{panel_idx:02d}__a{attempt}.png"
            try:
                gurl = await generate(endpoint, prompt, ref_urls)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"{tag} GEN ERR: {e}")
                attempts.append({"attempt": attempt, "mode": mode, "error": str(e)})
                continue

            try:
                verdict = await asyncio.to_thread(qa_one, panel_path, img, panel_class)
            except Exception as e:
                print(f"{tag} QA ERR: {e}")
                attempts.append({"attempt": attempt, "mode": mode, "image": img.name, "error": f"QA: {e}"})
                break

            t_end = time.time()
            attempts.append({
                "attempt": attempt, "mode": mode, "image": img.name,
                "gen_seconds": round(t_gen - t0, 1),
                "qa_seconds": round(t_end - t_gen, 1),
                "fal_url": gurl, **verdict,
            })
            prev_output = img
            print(f"{tag} prod={verdict.get('product_score','?')} "
                  f"comp={verdict.get('composition_score','?')} -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (max(passers, key=lambda a: a.get("product_score", 0)) if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))

    return {
        "panel_idx": panel_idx,
        "model": model,
        "panel_class": panel_class,
        "scene": scene_desc[:200],
        "thresholds": {"product": prod_thr, "composition": comp_thr},
        "attempts": attempts,
        "final": final,
        "passed": bool(passers),
    }


async def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"run_{ts}"
    run_dir.mkdir()

    user_request = LLM_INPUT["user_request"]["current"]
    scenes = PRECOMP["scenes"]

    panel_paths = sorted(TPL_DIR.glob("panel_*.*"))
    print(f"=== swap pipeline ===")
    print(f"  target: #{LLM_INPUT['target_template']['rank']} {LLM_INPUT['target_template']['name']}")
    print(f"  user product: {LLM_INPUT['user_product']['name']}")
    print(f"  panels: {len(panel_paths)} × models {list(config.MODELS)}")
    print(f"  product refs: {len(PRODUCT_REFS)}")
    print(f"  run dir: {run_dir}")

    print("\nuploading product refs...")
    product_urls = await asyncio.gather(*[upload(p) for p in PRODUCT_REFS])
    print(f"  done ({len(product_urls)})")

    print("uploading panel originals...")
    panel_url_list = await asyncio.gather(*[upload(p) for p in panel_paths])
    panel_urls = {int(p.stem.split("_")[1]): u for p, u in zip(panel_paths, panel_url_list)}

    urls = {"product": list(product_urls), "panels": panel_urls}

    sem = asyncio.Semaphore(CONCURRENCY)
    t0 = time.time()
    jobs = []
    for p in panel_paths:
        idx = int(p.stem.split("_")[1])
        sname = f"panel_{idx:02d}"
        scene_data = scenes.get(sname, {})
        for model in config.MODELS:
            jobs.append(run_panel(idx, scene_data, p, user_request, urls, model, run_dir, sem))

    results = await asyncio.gather(*jobs, return_exceptions=True)
    cells = [r for r in results if isinstance(r, dict)]
    for r in results:
        if not isinstance(r, dict):
            print(f"  cell raised: {r!r}")

    wall = round(time.time() - t0, 1)
    summary = {
        "run": run_dir.name,
        "target_template": "01_sofa_992474",
        "user_product": "milo_777039",
        "user_request": user_request,
        "models": list(config.MODELS),
        "panel_count": len(panel_paths),
        "concurrency": CONCURRENCY,
        "max_attempts": MAX_ATTEMPTS,
        "total_wall_seconds": wall,
        "cells": cells,
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_ROOT / "latest.txt").write_text(run_dir.name, encoding="utf-8")

    passers = sum(1 for c in cells if c["passed"])
    print(f"\n=== DONE === {run_dir}")
    print(f"  wall: {wall}s")
    print(f"  passers: {passers}/{len(cells)}")
    by_model = {m: sum(1 for c in cells if c["model"] == m and c["passed"]) for m in config.MODELS}
    for m, n in by_model.items():
        print(f"    {m}: {n}/{len(panel_paths)}")


if __name__ == "__main__":
    asyncio.run(main())

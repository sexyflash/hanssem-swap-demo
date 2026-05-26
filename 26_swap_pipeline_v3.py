"""Swap pipeline v3 — GPT 기본 + 자동 3-strategy fallback + 풍부한 prompt.

각 panel:
  Attempt 1 (S1: 재시도)        — GIF refs + 강력한 prompt with visual description + spec
  Attempt 2 (S2: overpaint)     — fail시 previous output overpaint
  Attempt 3 (S3: smart sheet)   — fail시 smart sheet 추가 ref + 처음부터 aligned

panel별 aspect ratio 매칭. text-free 강제. design_chart panel은 spec 수치 명시.
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

PRECOMP = json.loads((TPL_DIR / "precomputed.json").read_text())
VISUAL = json.loads((USER_DIR / "visual_description.json").read_text())
COMBINED = VISUAL["combined_swap_block"]
SPEC = VISUAL["spec_from_page"]

OUT_ROOT = TPL_DIR / "swap_results"
OUT_ROOT.mkdir(exist_ok=True)

# GPT only (NB2 옵션은 그대로 유지하되 기본 GPT)
MODEL_NAME = "gpt_image"
ENDPOINT = config.MODELS[MODEL_NAME]
CONCURRENCY = 4

GIF_REFS = sorted((USER_DIR / "gif_frames").glob("frame_*.jpg"))[:3]
SMART_SHEET = USER_DIR / "smart_sheet.jpg"


def thresholds_for(panel_class: str) -> tuple[int, int]:
    if panel_class in ("cover", "intro"):
        return (95, 95)
    if panel_class == "design_chart":
        return (93, 90)
    return (93, 80)


def aspect_ratio_for(w: int, h: int) -> str:
    r = w / h
    candidates = [
        ("21:9", 21/9), ("16:9", 16/9), ("3:2", 3/2), ("4:3", 4/3),
        ("1:1", 1.0), ("3:4", 3/4), ("2:3", 2/3), ("9:16", 9/16), ("9:21", 9/21),
    ]
    return min(candidates, key=lambda c: abs(c[1] - r))[0]


def build_prompt(scene_desc: str, panel_class: str, *,
                 is_cover: bool, strategy: str, design_spec_hint: str = "") -> str:
    cover_note = ""
    if is_cover or panel_class in ("cover", "intro"):
        cover_note = (
            "\nCOVER PANEL: white seamless backdrop, eye-level straight-on view, "
            "centered framing, soft even shadowless light, no props, no shadows "
            "beyond subtle floor shadow. Square 1:1 composition. Sofa fills ~75% "
            "of horizontal frame. Crystal product fidelity. STRICTLY 2-seat."
        )

    strategy_note = ""
    if strategy == "overpaint":
        strategy_note = (
            "\n\nOVERPAINT PASS: IMAGE 1 is the previous attempt. Redraw the sofa "
            "region to match the MILO references and the product description "
            "exactly. KEEP the rest of the panel (room, props, lighting, charts) "
            "intact."
        )
    elif strategy == "smart_sheet":
        strategy_note = (
            "\n\nSMART-SHEET REINFORCEMENT: IMAGE 2 is a multi-angle composite of "
            "the MILO 2-seat sofa with explicit angle labels (3/4 front, side, "
            "back). Use it as authoritative product reference together with "
            "IMAGES 3-5 (individual frames). RENDER STRICTLY 2 SEATS — count "
            "cushions before committing."
        )

    text_rule = (
        "\n\nABSOLUTE RULE — NO TEXT IN OUTPUT IMAGE:\n"
        "- Zero Korean / English / numbers / brand marks / captions.\n"
        "- For dimension/spec/color panels: render only the visual elements "
        "(dimension lines without numbers, color swatches without color names, "
        "cushion cross-sections without labels). All text is added separately "
        "as HTML overlay."
    )

    design_block = ""
    if panel_class == "design_chart" and design_spec_hint:
        design_block = (
            f"\n\nDESIGN-CHART PANEL — exact specifications for the MILO 2-seat:\n"
            f"{design_spec_hint}\n"
            "Render the dimension/structure/material visuals graphically without "
            "any text labels. The visible cushion / leg / arm structure must "
            "match the spec above and the product references."
        )

    return f"""\
TASK: photorealistic furniture detail-page panel reproduction (product swap).

Reference images (in order):
- IMAGE 1 = {'PREVIOUS ATTEMPT' if strategy == 'overpaint' else 'ORIGINAL PANEL'}. Defines camera angle, framing, composition, backdrop, lighting, staging.
- {'IMAGE 2 = SMART SHEET (multi-angle product composite). IMAGES 3-N = individual GIF frames.' if strategy == 'smart_sheet' else 'IMAGES 2..N = MILO product reference frames (GIF 360° slices, 3 angles).'}

ORIGINAL PANEL STAGING (reproduce):
{scene_desc}

{COMBINED}

PANEL TYPE: {panel_class}.{cover_note}{strategy_note}{design_block}{text_rule}

Render the MILO 2-seat fabric sofa in IMAGE 1's exact staging. Fabric (NOT
leather). Match the product references exactly: 2 seat cushions, 2 back
cushions, boxy arms slightly lower than backrest, 4 slim matte-black metal
legs, light-beige linen-look upholstery with piped seams. No invented
decoration. NO text in the output.
"""


def design_spec_hint_for(panel_class: str, idx: int) -> str:
    """For design_chart panels, give exact dim/material spec to anchor the swap."""
    if panel_class != "design_chart":
        return ""
    dims = SPEC.get("dimensions", {}) or {}
    mat = SPEC.get("material", {}) or {}
    colors = ", ".join(SPEC.get("colors") or [])
    return (
        f"- Seat height: {dims.get('seat_height_cm','?')}cm; arm height: "
        f"{dims.get('arm_height_cm','?')}cm\n"
        f"- Seat cushion fill: {mat.get('seat_cushion','')}\n"
        f"- Back cushion fill: {mat.get('back_cushion','')}\n"
        f"- Upholstery: {mat.get('upholstery','')}\n"
        f"- Frame: {mat.get('frame','')}\n"
        f"- Colors available: {colors}"
    )


def qa_one(panel_orig: Path, swap_result: Path, panel_class: str) -> dict:
    prod_thr, comp_thr = thresholds_for(panel_class)
    product_ref = GIF_REFS[0]  # 3/4 front

    qa_prompt = (
        f"You are evaluating an AI-generated sofa-detail-page panel.\n"
        f"Panel class: '{panel_class}'. "
        f"Product fidelity threshold: {prod_thr}+. Composition threshold: {comp_thr}+.\n"
        "The target product is the MILO 2-SEAT fabric sofa (밀로 패브릭소파 2인용). "
        "STRICTLY 2 seats. Fabric upholstery, not leather.\n\n"
        "Compare:\n"
        "  IMAGE A = USER PRODUCT REFERENCE (one frame of MILO 2-seat)\n"
        "  IMAGE B = GENERATED SWAP RESULT\n"
        "  IMAGE C = ORIGINAL PANEL (composition reference)\n\n"
        "Return JSON:\n"
        '  "seat_count_in_B" (int): count visible seat cushions in B\n'
        '  "product_score" (0-100): how exactly B matches A in silhouette, '
        'proportions, fabric (NOT leather), cushion count, arm shape, leg style, color\n'
        '  "composition_score" (0-100): how well B reproduces C\'s camera/staging\n'
        '  "text_in_image" (bool): true if any text/numbers/labels visible in B\n'
        '  "wrong_seat_count" (bool): true if seat_count_in_B != 2\n'
        '  "notes" (str): brief reason\n'
        f'  "verdict" ("pass"|"retry"): pass only if seat_count_in_B == 2 AND '
        f"product_score >= {prod_thr} AND composition_score >= {comp_thr} AND "
        "not text_in_image."
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


async def run_target(label: str, base_img: Path, scene_desc: str, panel_class: str,
                     urls: dict, out_dir: Path, ratio: str,
                     sem: asyncio.Semaphore, *, is_cover: bool = False,
                     idx: int | None = None) -> dict:
    """Run 3-strategy auto-fallback. Returns final result."""
    attempts = []
    prev_output: Path | None = None
    spec_hint = design_spec_hint_for(panel_class, idx or 0)
    strategies = ["aligned", "overpaint", "smart_sheet"]

    for attempt, strategy in enumerate(strategies, 1):
        tag = f"[{label}/{strategy}/#{attempt}]"
        async with sem:
            t0 = time.time()
            if strategy == "overpaint":
                if not prev_output:
                    continue
                prev_url = await upload(prev_output)
                ref_urls = [prev_url] + urls["gif"]
            elif strategy == "smart_sheet":
                ref_urls = [urls["base_" + label], urls["smart_sheet"]] + urls["gif"]
            else:  # aligned
                ref_urls = [urls["base_" + label]] + urls["gif"]

            prompt = build_prompt(scene_desc, panel_class, is_cover=is_cover,
                                  strategy=strategy, design_spec_hint=spec_hint)
            print(f"{tag} ar={ratio} ({len(ref_urls)} refs)", flush=True)
            img = out_dir / f"{label}__a{attempt}_{strategy}.png"
            try:
                gurl = await generate(prompt, ref_urls, ratio)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"{tag} GEN ERR: {e}")
                attempts.append({"attempt": attempt, "strategy": strategy, "error": str(e)})
                continue

            try:
                verdict = await asyncio.to_thread(qa_one, base_img, img, panel_class)
            except Exception as e:
                print(f"{tag} QA ERR: {e}")
                attempts.append({"attempt": attempt, "strategy": strategy, "image": img.name, "error": f"QA: {e}"})
                break

            t_end = time.time()
            attempts.append({
                "attempt": attempt, "strategy": strategy, "image": img.name,
                "gen_seconds": round(t_gen - t0, 1),
                "qa_seconds": round(t_end - t_gen, 1),
                "fal_url": gurl, "aspect_ratio": ratio,
                **verdict,
            })
            prev_output = img
            seat_flag = "" if verdict.get("seat_count_in_B") == 2 else f" SEAT={verdict.get('seat_count_in_B')}"
            text_flag = " TEXT!" if verdict.get("text_in_image") else ""
            print(f"{tag} prod={verdict.get('product_score','?')} "
                  f"comp={verdict.get('composition_score','?')}{seat_flag}{text_flag} -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (passers[0] if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))

    prod_thr, comp_thr = thresholds_for(panel_class)
    return {
        "label": label,
        "panel_idx": idx,
        "panel_class": panel_class,
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
    run_dir = OUT_ROOT / f"v3_{ts}"
    run_dir.mkdir()
    out_dir = run_dir / MODEL_NAME
    out_dir.mkdir()

    # targets: cover + all 12 panels (full re-run)
    targets = []
    cover_path = TPL_DIR / "_cover_1000.jpg"
    targets.append({"label": "cover", "path": cover_path, "class": "cover",
                    "scene": "Hero cover shot of the sofa on a clean white seamless "
                             "backdrop. Eye-level straight-on view, centered framing, "
                             "soft even shadowless light, no props. 1:1 square."})
    for sname, pdata in PRECOMP["scenes"].items():
        if not sname.startswith("panel_"):
            continue
        idx = int(sname.split("_")[1])
        ppath = next(TPL_DIR.glob(f"panel_{idx:02d}.*"))
        targets.append({"label": sname, "idx": idx, "path": ppath,
                        "class": pdata.get("panel_class", "unknown"),
                        "scene": pdata.get("description", "")})

    print(f"=== swap v3 — full re-run ===")
    print(f"  model: {MODEL_NAME} only")
    print(f"  targets: {len(targets)} (cover + 12 panels)")
    print(f"  strategies: aligned → overpaint → smart_sheet (auto-fallback)")
    print(f"  thresholds: cover 95/95, design_chart 93/90, default 93/80")

    print("\nuploading references...")
    gif_urls = await asyncio.gather(*[upload(p) for p in GIF_REFS])
    smart_url = await upload(SMART_SHEET)
    base_urls = {}
    for tg in targets:
        base_urls[f"base_{tg['label']}"] = await upload(tg["path"])
    print(f"  done")
    urls = {**base_urls, "gif": list(gif_urls), "smart_sheet": smart_url}

    sem = asyncio.Semaphore(CONCURRENCY)
    t0 = time.time()
    jobs = []
    for tg in targets:
        w, h = Image.open(tg["path"]).size
        ratio = aspect_ratio_for(w, h)
        jobs.append(run_target(
            tg["label"], tg["path"], tg["scene"], tg["class"],
            urls, out_dir, ratio, sem,
            is_cover=(tg["label"] == "cover"),
            idx=tg.get("idx"),
        ))

    results = await asyncio.gather(*jobs, return_exceptions=True)
    cells = [r for r in results if isinstance(r, dict)]
    for r in results:
        if not isinstance(r, dict):
            print(f"  raised: {r!r}")

    wall = round(time.time() - t0, 1)
    summary = {
        "run": run_dir.name, "model": MODEL_NAME, "target_template": "01_sofa_992474",
        "user_product": "milo_777039", "wall_seconds": wall,
        "strategies": ["aligned", "overpaint", "smart_sheet"],
        "auto_fallback": True, "cells": cells,
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # update latest pointer to v3 (keep old runs)
    (OUT_ROOT / "latest_v3.txt").write_text(run_dir.name)
    passers = sum(1 for c in cells if c["passed"])
    print(f"\n=== DONE === {run_dir}")
    print(f"  wall: {wall}s")
    print(f"  passers: {passers}/{len(cells)}")
    for c in cells:
        v = c.get("final") or {}
        s = "/".join(c.get("strategies_used", []))
        print(f"    {c['label']:12} [{c['panel_class']:12}] "
              f"prod={v.get('product_score','?')} comp={v.get('composition_score','?')} "
              f"seats={v.get('seat_count_in_B','?')} via={s} pass={c['passed']}")


if __name__ == "__main__":
    asyncio.run(main())

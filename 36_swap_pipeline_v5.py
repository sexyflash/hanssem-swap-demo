"""Swap pipeline v5 — QA feedback loop + retry threshold 99.

핵심:
- attempt 1: 기본 prompt
- retry (attempt 2+): 이전 attempt의 QA verdict (notes/wrong_seat_count/text_in_image)를
  prompt에 explicit feedback으로 inject — 방석/프레임/팔걸이 특징 강조 + 잘못된 부분 명시
- retry 시 product threshold 99 (더 엄격)
- 자동 fallback: aligned → overpaint → smart_sheet

기존 v4와 차이:
- QA feedback inject (재합류)
- retry product threshold 99 (was 93/95)
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

USE_PROD = USER_DIR / "use_product"
GIF_FRAMES = sorted(USE_PROD.glob("p08_frame_*.jpg"))
MATERIAL_REFS = sorted(USE_PROD.glob("material*.png"))
COLOR_REFS = sorted(USE_PROD.glob("color_*.png"))
SMART_SHEET = USER_DIR / "smart_sheet.jpg"


def refs_for_zone(zone, urls):
    base = list(urls["gif"])
    if zone == "material_swatch":
        return base + list(urls.get("material", []))
    if zone in ("color_option", "module_lineup"):
        return base + list(urls.get("color", []))
    return base


def thresholds_for(layout_type, zone, attempt_n):
    """Attempt 1: normal thresholds. Attempt 2+: STRICT product = 99."""
    if attempt_n == 1:
        if layout_type == "strict_white_bg":
            return (95, 95)
        if layout_type == "fixed_layout":
            return (93, 92)
        return (93, 80)
    # retry — strict
    if layout_type == "strict_white_bg":
        return (99, 95)
    if layout_type == "fixed_layout":
        return (99, 92)
    return (99, 80)


def aspect_ratio_for(w, h):
    r = w / h
    candidates = [
        ("21:9", 21/9), ("16:9", 16/9), ("3:2", 3/2), ("4:3", 4/3),
        ("1:1", 1.0), ("3:4", 3/4), ("2:3", 2/3), ("9:16", 9/16), ("9:21", 9/21),
    ]
    return min(candidates, key=lambda c: abs(c[1] - r))[0]


def build_prompt(panel_meta, *, strategy, layout_type, attempt_n,
                 prev_verdict=None):
    zone = panel_meta.get("input_zone", "other")
    visible_text = panel_meta.get("visible_korean_text", "")
    scene_desc = panel_meta.get("scene_desc", "")

    # ====== SPEC block — zone aware ======
    dims = SPEC.get("dimensions", {}) or {}
    mat = SPEC.get("material", {}) or {}
    colors = SPEC.get("colors") or []
    seat_n = SPEC.get("seat_count", 2)

    spec_base = (
        f"PRODUCT: {SPEC.get('product_name')} ({seat_n}-seat STRICTLY)\n"
        f"Visual: {VISUAL.get('full_visual_paragraph','')[:300]}\n"
        f"좌석수: {seat_n}인 (count carefully — must be {seat_n})\n"
        f"팔걸이 (arms): {VISUAL.get('arm',{}).get('shape','boxy')}, "
        f"{VISUAL.get('arm',{}).get('height_relative','slightly lower than back')}\n"
        f"등쿠션: {VISUAL.get('back',{}).get('cushion_count','?')}개 "
        f"{VISUAL.get('back',{}).get('shape','rectangular')} ({VISUAL.get('back',{}).get('attached_or_loose','loose')})\n"
        f"좌방석: {VISUAL.get('seat',{}).get('cushion_count','?')}개 "
        f"{VISUAL.get('seat',{}).get('depth','deep')} {VISUAL.get('seat',{}).get('firmness','soft')}\n"
        f"패브릭: {VISUAL.get('upholstery',{}).get('material','fabric')} "
        f"({VISUAL.get('upholstery',{}).get('texture','linen-look')}, "
        f"{VISUAL.get('upholstery',{}).get('primary_color','light beige')}), "
        f"{VISUAL.get('upholstery',{}).get('seams','piped')} seams\n"
        f"다리: {VISUAL.get('legs',{}).get('count',4)} {VISUAL.get('legs',{}).get('shape','slim metal')} "
        f"({VISUAL.get('legs',{}).get('color','matte black')})\n"
        f"프레임: {mat.get('frame','EO 건조목, S자 스프링')}\n"
        f"좌석 높이: {dims.get('seat_height_cm','?')}cm; 팔걸이 높이: {dims.get('arm_height_cm','?')}cm\n"
        f"컬러: {', '.join(colors)}"
    )

    # ====== ZONE-specific facts ======
    if zone == "size_chart":
        spec_block = spec_base + (
            f"\n\nSIZE CHART FACTS (no text rendered, visuals only):\n"
            f"  seat_height={dims.get('seat_height_cm','?')}cm, arm={dims.get('arm_height_cm','?')}cm, "
            f"seat_depth={dims.get('seat_depth_cm','?')}cm. Preserve dimension lines."
        )
    elif zone == "structure_chart":
        spec_block = spec_base + (
            f"\n\nSTRUCTURE FACTS: 좌방석={mat.get('seat_cushion','')}, "
            f"등쿠션={mat.get('back_cushion','')}, 프레임={mat.get('frame','')}, "
            f"upholstery={mat.get('upholstery','')}. Preserve cross-section layout."
        )
    elif zone == "color_option":
        spec_block = spec_base + f"\n\nCOLOR OPTIONS (render as fabric swatches): {', '.join(colors)}. Preserve grid layout."
    elif zone == "material_swatch":
        spec_block = spec_base + f"\n\nMATERIAL: {mat.get('upholstery','')}. Show fabric weave + primary color {VISUAL.get('upholstery',{}).get('primary_color','beige')}."
    else:
        spec_block = spec_base

    # ====== Layout rule ======
    if layout_type == "fixed_layout":
        layout_rule = (
            "\n\nFIXED LAYOUT — chart/diagram/grid STRUCTURE MUST BE PRESERVED.\n"
            "Replace only the sofa silhouette with MILO 2-seat. Do not redraw the chart.\n"
            f"Original Korean text in panel (DO NOT render): {visible_text[:150]}"
        )
    elif layout_type == "strict_white_bg":
        layout_rule = (
            "\n\nSTRICT WHITE-BG: clean white backdrop, eye-level straight-on, centered, "
            "soft even light, no props. STRICTLY 2-seat."
        )
    else:
        layout_rule = "\n\nFLEXIBLE STAGING: reproduce original room/lighting/camera; sofa fidelity priority."

    # ====== Strategy note ======
    if strategy == "overpaint":
        strat_note = (
            "\n\nOVERPAINT: IMAGE 1 is the previous attempt. Redraw sofa region only; keep rest intact."
        )
    elif strategy == "smart_sheet":
        strat_note = (
            "\n\nSMART-SHEET: IMAGE 2 is multi-angle product composite. Use it as authoritative reference."
        )
    else:
        strat_note = ""

    # ====== Retry feedback (QA → prompt loop) ======
    retry_feedback = ""
    if attempt_n > 1 and prev_verdict:
        wrong_parts = []
        if prev_verdict.get("seat_count_in_B") and prev_verdict["seat_count_in_B"] != seat_n:
            wrong_parts.append(
                f"이전 시도에서 좌석 수가 {prev_verdict['seat_count_in_B']}인으로 잘못 렌더됨. "
                f"이번엔 반드시 {seat_n}인 (정확히 {seat_n}개의 seat cushion)."
            )
        if prev_verdict.get("text_in_image"):
            wrong_parts.append(
                "이전 시도에서 이미지 안에 텍스트/숫자가 들어감. 이번엔 절대 금지 — 글자 0개."
            )
        if layout_type == "fixed_layout" and not prev_verdict.get("structure_preserved", True):
            wrong_parts.append(
                "이전 시도에서 차트/도면 구조가 변형됨. 이번엔 원본 layout 정확히 보존하고 sofa만 교체."
            )
        notes = prev_verdict.get("notes", "")
        if notes:
            wrong_parts.append(f"QA 코멘트: {notes}")

        retry_feedback = (
            "\n\n==== RETRY FEEDBACK (이전 시도 분석) ====\n"
            "PREVIOUS ATTEMPT FAILED. 다음 부분이 잘못됐음:\n"
            + "\n".join(f"- {w}" for w in wrong_parts)
            + "\n\nThis time, EMPHASIZE precisely:\n"
            f"- 좌석 수 {seat_n}인 (cushion 개수 세고 시작)\n"
            f"- 좌방석/등쿠션 모양: 직사각, loose, {VISUAL.get('seat',{}).get('firmness','soft')} (절대 미디엄/하드 X)\n"
            f"- 팔걸이: boxy 직각, 백쿠션보다 낮음 (가죽 두꺼운 팔걸이 X)\n"
            f"- 다리: 슬림 메탈 4개 (블록 다리 X, 가죽 다리 X)\n"
            f"- 패브릭 texture: linen-look, piped seams (가죽 광택 X, 무늬 X)\n"
            f"- 색상: light beige (오트밀톤). 짙은 갈색/회색 X.\n"
        )

    text_rule = (
        "\n\nABSOLUTE — NO TEXT IN OUTPUT:\n"
        "- Zero Korean/English characters/numbers/captions in output.\n"
        "- Charts: visual elements only (lines, swatches) — text added as HTML overlay."
    )

    return f"""\
TASK: photorealistic furniture detail-page panel reproduction (product swap).

References:
- IMAGE 1 = {'PREVIOUS ATTEMPT' if strategy == 'overpaint' else 'ORIGINAL PANEL'}.
- {'IMAGE 2 = SMART SHEET. IMAGES 3-N = GIF frames.' if strategy == 'smart_sheet' else 'IMAGES 2..N = MILO product frames.'}

ORIGINAL PANEL STAGING:
{scene_desc}

{spec_block}

USER REQUEST: {USER_REQUEST_TXT}

PANEL TYPE: {panel_meta.get('layout_type','flexible_staging')}.{layout_rule}{strat_note}{retry_feedback}{text_rule}

Render the MILO 2-seat fabric sofa precisely. Fabric (NOT leather).
"""


def qa_one(panel_orig, swap_result, layout_type, zone, attempt_n):
    prod_thr, comp_thr = thresholds_for(layout_type, zone, attempt_n)
    product_ref = GIF_FRAMES[0] if GIF_FRAMES else None

    qa_prompt = (
        f"You are evaluating an AI-generated sofa-detail-page panel.\n"
        f"Panel layout_type: '{layout_type}', zone: '{zone}', attempt: #{attempt_n}.\n"
        f"Product threshold: {prod_thr}+. Composition threshold: {comp_thr}+.\n"
        "Target: MILO 2-SEAT fabric sofa (밀로 패브릭소파 2인용). STRICTLY 2 seats. Fabric (not leather).\n\n"
        + ("For fixed_layout: chart/diagram STRUCTURE of C must be preserved in B.\n\n" if layout_type == "fixed_layout" else "")
        + "Compare:\n  A = product reference (MILO 2-seat)\n  B = generated swap\n  C = original panel\n\n"
        "Return JSON with these keys:\n"
        '  "seat_count_in_B" (int) — count visible seat cushions\n'
        '  "product_score" (0-100) — silhouette, proportions, fabric, cushion match\n'
        '  "composition_score" (0-100) — staging match to C\n'
        '  "text_in_image" (bool) — any text/numbers/labels visible in B\n'
        + ('  "structure_preserved" (bool) — chart/diagram structure intact\n' if layout_type == "fixed_layout" else '  "structure_preserved" (bool, default true)\n')
        + '  "specific_failures" (list of str) — WHAT specifically is wrong in B (be detailed: arm shape, leg style, cushion count, fabric texture, color, etc.). EMPTY if perfect.\n'
        '  "notes" (str) — brief reason\n'
        f'  "verdict" ("pass"|"retry") — pass only if seat_count_in_B == 2 AND '
        f"product_score >= {prod_thr} AND composition_score >= {comp_thr} AND not text_in_image"
        + (" AND structure_preserved" if layout_type == "fixed_layout" else "")
        + "."
    )
    msg_content = [{"type": "text", "text": qa_prompt}]
    if product_ref:
        msg_content += [
            {"type": "text", "text": "IMAGE A:"},
            {"type": "image_url", "image_url": {"url": data_uri(product_ref)}},
        ]
    msg_content += [
        {"type": "text", "text": "IMAGE B:"},
        {"type": "image_url", "image_url": {"url": data_uri(swap_result)}},
        {"type": "text", "text": "IMAGE C:"},
        {"type": "image_url", "image_url": {"url": data_uri(panel_orig)}},
    ]
    resp = openai_client.chat.completions.create(
        model=config.VISION_MODEL,
        messages=[{"role": "user", "content": msg_content}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)


async def generate(prompt, ref_urls, aspect_ratio):
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


async def run_target(label, base_img, panel_meta, urls, out_dir, ratio, sem):
    layout_type = panel_meta.get("layout_type", "flexible_staging")
    zone = panel_meta.get("input_zone", "other")
    strategies = ["aligned", "overpaint", "smart_sheet"]
    attempts = []
    prev_output = None
    prev_verdict = None

    for attempt_n, strategy in enumerate(strategies, 1):
        tag = f"[{label}/{strategy}/#{attempt_n}]"
        async with sem:
            t0 = time.time()
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

            prompt = build_prompt(
                panel_meta, strategy=strategy, layout_type=layout_type,
                attempt_n=attempt_n, prev_verdict=prev_verdict,
            )
            prod_thr, comp_thr = thresholds_for(layout_type, zone, attempt_n)
            fb = " FB✓" if attempt_n > 1 and prev_verdict else ""
            print(f"{tag} ar={ratio} refs={len(ref_urls)} thr=p{prod_thr}/c{comp_thr}{fb}", flush=True)
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
                verdict = await asyncio.to_thread(qa_one, base_img, img, layout_type, zone, attempt_n)
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
                "thresholds": {"product": prod_thr, "composition": comp_thr},
                **verdict,
            })
            prev_output = img
            prev_verdict = verdict
            sf = "" if verdict.get("seat_count_in_B") == 2 else f" SEAT={verdict.get('seat_count_in_B')}"
            tf = " TEXT!" if verdict.get("text_in_image") else ""
            print(f"{tag} prod={verdict.get('product_score','?')} comp={verdict.get('composition_score','?')}{sf}{tf} -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (passers[0] if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))

    last_thr = thresholds_for(layout_type, zone, len(attempts) or 1)
    return {
        "label": label,
        "panel_idx": panel_meta.get("panel_idx"),
        "input_zone": zone,
        "layout_type": layout_type,
        "aspect_ratio": ratio,
        "thresholds": {"product": last_thr[0], "composition": last_thr[1]},
        "attempts": attempts,
        "final": final,
        "passed": bool(passers),
        "strategies_used": [a["strategy"] for a in attempts if "strategy" in a],
    }


async def main():
    from PIL import Image

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"v5_{ts}"
    run_dir.mkdir()
    out_dir = run_dir / MODEL_NAME
    out_dir.mkdir()

    targets = []
    cover_path = TPL_DIR / "_cover_1000.jpg"
    targets.append({
        "label": "cover", "path": cover_path,
        "panel_meta": {
            "panel": "cover", "panel_idx": None,
            "input_zone": "intro_hero", "layout_type": "strict_white_bg",
            "scene_desc": "Hero cover shot on a clean white seamless backdrop. "
                          "Eye-level straight-on, centered, soft even light, no props.",
        },
    })
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
                "scene_desc": pdata.get("description", ""),
            },
        })

    print(f"=== swap v5 — QA feedback loop ===")
    print(f"  model: {MODEL_NAME}")
    print(f"  targets: {len(targets)}")
    print(f"  retry product threshold: 99")
    print(f"  retry: feedback loop (prev QA → next prompt)")

    print("\nuploading references...")
    gif_urls = await asyncio.gather(*[upload(p) for p in GIF_FRAMES])
    material_urls = await asyncio.gather(*[upload(p) for p in MATERIAL_REFS]) if MATERIAL_REFS else []
    color_urls = await asyncio.gather(*[upload(p) for p in COLOR_REFS]) if COLOR_REFS else []
    smart_url = await upload(SMART_SHEET)
    base_urls = {}
    for tg in targets:
        base_urls[f"base_{tg['label']}"] = await upload(tg["path"])
    urls = {**base_urls, "gif": list(gif_urls), "material": list(material_urls),
            "color": list(color_urls), "smart_sheet": smart_url}

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
        "target_template": "01_sofa_992474", "user_product": "milo_777039",
        "wall_seconds": wall, "auto_fallback": True,
        "retry_threshold_product": 99,
        "feedback_loop": True,
        "user_request": USER_REQUEST_TXT,
        "cells": cells,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_ROOT / "latest_v5.txt").write_text(run_dir.name)

    passers = sum(1 for c in cells if c["passed"])
    print(f"\n=== DONE === {run_dir}")
    print(f"  wall: {wall}s")
    print(f"  passers: {passers}/{len(cells)}")
    for c in cells:
        v = c.get("final") or {}
        s = "/".join(c.get("strategies_used", []))
        print(f"    {c['label']:12} [{c['layout_type']:>17}/{c['input_zone']:>16}] "
              f"prod={v.get('product_score','?')} comp={v.get('composition_score','?')} "
              f"seats={v.get('seat_count_in_B','?')} via={s} pass={c['passed']}")


if __name__ == "__main__":
    asyncio.run(main())

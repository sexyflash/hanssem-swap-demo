"""Swap pipeline v6 — layered prompt + bidirectional QA + attempts[i].prompt 저장.

prompt 구조 (4-layer):
  [CORE]     항상 inject — milo 시각 특징 + 절대 규칙
  [PRESET]   zone별 layout preset (예: size_chart = "좌측 silhouette + 우측 dim")
  [PANEL]    panel layout map (vision 추출, 정확한 위치 묘사)
  [FEEDBACK] retry 시만 — 이전 실패 + reference influence detection

bidirectional QA:
  - 제품 fidelity (B vs A) — 형태/소재/좌석수 매치
  - reference influence — C(원본 panel) 또는 A(product ref)의 잘못된 요소가
    B에 전이됐는지 detect → 다음 retry prompt에 "DO NOT inherit ___" 명시

각 attempt의 full prompt가 summary.json에 저장됨.
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

LAYOUTS = {p["panel"]: p for p in json.loads((TPL_DIR / "panel_layout_maps.json").read_text())["panels"] if "panel_idx" in p or p.get("panel") == "cover"}
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


# ============= 4-Layer Prompt Architecture =============

def core_block() -> str:
    """[CORE] — 모든 panel에 공통 inject. milo 제품 시각 특징 + 절대 규칙."""
    dims = SPEC.get("dimensions", {}) or {}
    mat = SPEC.get("material", {}) or {}
    colors = SPEC.get("colors") or []
    seat_n = SPEC.get("seat_count", 2)
    return f"""\
=== [CORE — PRODUCT IDENTITY] ===
PRODUCT: {SPEC.get('product_name')} (밀로 패브릭소파 {seat_n}인용)
STRICT SEAT COUNT: {seat_n} (count cushions visually before rendering)

VISUAL DESCRIPTION (from 360° GIF + product photos — authoritative):
{VISUAL.get('full_visual_paragraph','')}

PHYSICAL ATTRIBUTES:
- Silhouette: {VISUAL.get('silhouette','')}
- Arms: {VISUAL.get('arm',{}).get('shape','boxy')} shape, {VISUAL.get('arm',{}).get('height_relative','slightly lower than backrest')}
- Back: {VISUAL.get('back',{}).get('cushion_count','?')}개 {VISUAL.get('back',{}).get('shape','rectangular')} cushions, {VISUAL.get('back',{}).get('attached_or_loose','loose')}, headrest: {VISUAL.get('back',{}).get('headrest', False)}
- Seat: {VISUAL.get('seat',{}).get('cushion_count','?')}개 cushions, {VISUAL.get('seat',{}).get('depth','deep')} depth, {VISUAL.get('seat',{}).get('firmness','soft')} firmness
- Upholstery: {VISUAL.get('upholstery',{}).get('material','fabric')} ({VISUAL.get('upholstery',{}).get('texture','linen-look')}), color={VISUAL.get('upholstery',{}).get('primary_color','light beige')}, seams={VISUAL.get('upholstery',{}).get('seams','piped')}
- Legs: {VISUAL.get('legs',{}).get('count',4)} {VISUAL.get('legs',{}).get('shape','slim metal')} legs, {VISUAL.get('legs',{}).get('color','matte black')}
- Frame: {mat.get('frame','EO 건조목, S자 스프링')}
- Dimensions: {dims.get('width_cm','?')}×{dims.get('depth_cm','?')}×{dims.get('height_cm','?')}cm, seat_height={dims.get('seat_height_cm','?')}cm, arm_height={dims.get('arm_height_cm','?')}cm
- Available colors: {', '.join(colors)}

=== [ABSOLUTE RULES] ===
1. STRICTLY {seat_n}-seat. Not 3-seat. Not 4-seat.
2. FABRIC upholstery (linen-look texture). NOT leather. No leather sheen.
3. NO TEXT in output image — zero Korean/English/numbers/labels.
4. NO invented decorations (no tufting, no buttons, no quilting, no patterns).
5. Slim metal legs (not block/thick leg, not wood leg).
6. Piped seams along cushion edges.
"""


# Zone presets — layout grammar for each panel type
PRESETS = {
    "intro_hero": """\
=== [LAYOUT PRESET: COVER / HERO] ===
- White seamless backdrop, eye-level straight-on view, centered framing.
- Soft even shadowless light, no props.
- 1:1 square composition. Sofa fills ~70% horizontal frame.
- Subtle floor contact shadow only.""",
    "lifestyle_scene": """\
=== [LAYOUT PRESET: LIFESTYLE SCENE] ===
- Reproduce the original room/lighting/atmosphere from IMAGE 1.
- Sofa placement matches original framing.
- Background/floor/props stay consistent with original; only the sofa itself swaps.""",
    "size_chart": """\
=== [LAYOUT PRESET: SIZE CHART (FIXED LAYOUT — STRUCTURE MUST BE PRESERVED)] ===
Standard layout:
- Sofa silhouette (side-profile or 3/4 view) in upper or left zone.
- Dimension lines with arrowheads showing width/depth/height/seat_height/arm_height.
- Optional firmness comparison bar(s) (좌방석 / 등쿠션) in lower zone.
The CHART STRUCTURE (lines, arrows, bars) is from the ORIGINAL panel (IMAGE 1).
Replace ONLY the sofa silhouette with MILO. KEEP dim lines, arrows, bar shapes
exactly. NO text/numbers rendered (HTML overlay will add).""",
    "structure_chart": """\
=== [LAYOUT PRESET: STRUCTURE CROSS-SECTION (FIXED LAYOUT)] ===
- Cross-section / cutaway diagram showing internal layers.
- Each layer corresponds to a material region (좌방석 / 등쿠션 / 프레임 / 다리).
- Sofa silhouette outline preserved from IMAGE 1.
- Replace sofa surface with MILO upholstery; internal layer shapes kept.
- NO text rendered.""",
    "color_option": """\
=== [LAYOUT PRESET: COLOR OPTION GRID (FIXED LAYOUT)] ===
- Multiple sofa instances side-by-side, each in a different fabric color.
- Use the COLOR REFERENCES (오트밀 / 라이트그레이 / 더스티로즈) as the actual fabrics.
- Each variant: same sofa pose, only fabric color differs.
- Grid layout from IMAGE 1 preserved. NO text rendered (color names HTML overlay).""",
    "module_lineup": """\
=== [LAYOUT PRESET: MODULE LINEUP (FIXED LAYOUT)] ===
- Multiple sofa variants in a row (e.g. 2인 / 3인 different lengths).
- IMPORTANT: this template uses 4인 leather variants — REPLACE with milo {SEAT}인 fabric only.
- DO NOT show multiple seat counts; show only the milo {SEAT}-seat variant in each cell, with different colors if applicable.
- NO text rendered.""",
    "material_swatch": """\
=== [LAYOUT PRESET: MATERIAL SWATCH] ===
- Close-up of fabric weave / texture.
- Wide flat fabric area filling the frame, slight angle for texture visibility.
- Use the MATERIAL REFERENCE image as the authoritative texture.
- Primary color: light beige (linen-look). NO text rendered.""",
    "detail_close_up": """\
=== [LAYOUT PRESET: DETAIL CLOSE-UP] ===
- Same camera angle/framing as IMAGE 1.
- Reproduce the detail focus (seam / leg / arm / cushion edge etc).
- NO leather sheen — fabric texture only.""",
    "delivery_info": """\
=== [LAYOUT PRESET: DELIVERY / WARRANTY INFO] ===
- Skip — no product rendering. HTML text overlay only.""",
    "context": """\
=== [LAYOUT PRESET: CONTEXT / BRANDING] ===
- Reproduce room/scene from IMAGE 1.
- Sofa swap only.""",
    "other": "",
}


def panel_block(layout_map: dict) -> str:
    """[PANEL] — vision으로 추출한 이 panel의 정확한 layout map."""
    spatial = layout_map.get("spatial_layout", "")
    elements = layout_map.get("elements", [])
    text_zones = layout_map.get("text_zones", [])
    swap_inst = layout_map.get("swap_instruction", "")

    elems_str = "\n".join(
        f"  - {e.get('role','?')}: at {e.get('position','?')} — {e.get('description','')}"
        for e in elements
    )
    texts_str = "\n".join(
        f"  - {tz.get('region','?')}: \"{tz.get('content','')}\""
        for tz in text_zones
    )
    return f"""\
=== [PANEL LAYOUT MAP (this specific panel)] ===
Spatial layout: {spatial}

Elements present:
{elems_str or '  (none)'}

Korean text zones (DO NOT render — HTML overlay only):
{texts_str or '  (none)'}

Swap instruction: {swap_inst}"""


def feedback_block(prev_qa: dict, panel_idx) -> str:
    """[FEEDBACK] — 이전 attempt 실패 분석 + reference influence detection."""
    if not prev_qa:
        return ""
    failures = []
    if prev_qa.get("seat_count_in_B") and prev_qa["seat_count_in_B"] != SPEC.get("seat_count", 2):
        failures.append(f"좌석 수가 {prev_qa['seat_count_in_B']}인으로 잘못 렌더됨 — 반드시 {SPEC.get('seat_count')}인 (cushion 개수 다시 세기).")
    if prev_qa.get("text_in_image"):
        failures.append("이미지 안에 텍스트/숫자/라벨 들어감 — ABSOLUTELY 0 characters.")
    specific = prev_qa.get("specific_failures") or []
    for sf in specific:
        failures.append(f"잘못된 부분: {sf}")
    notes = prev_qa.get("notes", "")
    if notes:
        failures.append(f"QA 코멘트: {notes}")
    ref_influences = prev_qa.get("reference_influences") or []
    influence_lines = []
    for ri in ref_influences:
        influence_lines.append(f"  DO NOT inherit '{ri.get('element','?')}' from {ri.get('source','reference')} — instead, use {ri.get('correction','MILO authoritative description')}")

    return f"""\
==== [QA FEEDBACK — PREVIOUS ATTEMPT FAILED] ====
Failures:
{chr(10).join(f'  - {f}' for f in failures) or '  (none specific)'}

Reference influence (잘못 영향 받은 부분 → 다음엔 이렇게 하지 마):
{chr(10).join(influence_lines) or '  (none detected)'}

THIS TIME, EMPHASIZE:
- Cushion count = exactly {SPEC.get('seat_count')} seats
- Arm shape: boxy slightly lower than back (NOT thick leather padded arm)
- Legs: 4 slim cylindrical matte-black metal (NOT thick wood/block)
- Fabric: linen-look light beige with piped seams (NOT leather sheen, NOT smooth)
- Seat firmness: soft/loose (NOT firm tight tailored)"""


def build_prompt(panel_idx, layout_map, scene_desc, attempt_n, strategy, prev_qa=None) -> str:
    """4-layer prompt 결합."""
    panel_class = layout_map.get("panel_class", "other")
    preset = PRESETS.get(panel_class, "").replace("{SEAT}", str(SPEC.get("seat_count", 2)))

    strat_note = ""
    if strategy == "overpaint":
        strat_note = "\n\n[STRATEGY: OVERPAINT] IMAGE 1 = previous attempt. Redraw only sofa region; keep rest intact."
    elif strategy == "smart_sheet":
        strat_note = "\n\n[STRATEGY: SMART-SHEET] IMAGE 2 = multi-angle product composite. Use as authoritative product reference."
    else:
        strat_note = "\n\n[STRATEGY: ALIGNED] IMAGE 1 = original panel. Reproduce layout, swap sofa."

    return f"""\
TASK: Photorealistic furniture detail-page panel reproduction (product swap).

References:
- IMAGE 1 = {'PREVIOUS ATTEMPT' if strategy == 'overpaint' else 'ORIGINAL PANEL'}.
- {'IMAGE 2 = SMART SHEET. IMAGES 3-N = GIF frames + zone refs.' if strategy == 'smart_sheet' else 'IMAGES 2..N = MILO product references (GIF frames + zone-specific).'}

{core_block()}

{preset}

{panel_block(layout_map)}{strat_note}

{feedback_block(prev_qa, panel_idx)}

USER REQUEST: {USER_REQUEST_TXT}

OUTPUT: A single photorealistic image. No text in output."""


# ============= Bidirectional QA =============

def qa_bidirectional(panel_orig: Path, swap_result: Path, panel_class: str, attempt_n: int) -> dict:
    """제품 fidelity + reference influence detection."""
    # threshold by attempt
    if attempt_n == 1:
        prod_thr = 93 if panel_class in ("fixed_layout", "size_chart", "structure_chart", "color_option", "module_lineup") else 93
        comp_thr = 92 if panel_class in ("size_chart", "structure_chart", "color_option", "module_lineup", "intro_hero") else 80
    else:
        prod_thr = 99
        comp_thr = 95 if panel_class in ("size_chart", "structure_chart", "color_option", "module_lineup", "intro_hero") else 80

    product_ref = GIF_FRAMES[0]
    qa_prompt = (
        f"You are evaluating an AI-generated sofa-detail-page panel — BIDIRECTIONAL CHECK.\n"
        f"Panel class: '{panel_class}'. Attempt #{attempt_n}. Product threshold: {prod_thr}+. Composition: {comp_thr}+.\n"
        f"Target: MILO 2-SEAT fabric sofa. STRICT 2 seats. Fabric (not leather).\n\n"
        "Compare:\n"
        "  A = MILO product reference (the ground truth product)\n"
        "  B = generated swap result (the AI output to evaluate)\n"
        "  C = original panel (the layout template used as reference)\n\n"
        "CHECK 1 (forward fidelity): B should match A's product attributes.\n"
        "CHECK 2 (reference influence): B should NOT inherit incorrect elements from C "
        "(e.g. if C is leather sofa with thick block legs, B should NOT have leather sheen or block legs).\n\n"
        "Return JSON:\n"
        '  "seat_count_in_B" (int)\n'
        '  "product_score" (0-100): B vs A match\n'
        '  "composition_score" (0-100): B vs C layout reproduction\n'
        '  "text_in_image" (bool)\n'
        '  "structure_preserved" (bool): for fixed_layout panels — chart layout intact in B\n'
        '  "specific_failures" (list of str): WHAT in B is wrong vs A (be detailed)\n'
        '  "reference_influences" (list of {"element": str, "source": "C" or "A", "correction": str}): '
        "elements where B incorrectly inherited from C (or A) rather than matching MILO. "
        "Example: {\"element\": \"leather sheen on sofa\", \"source\": \"C\", \"correction\": \"replace with fabric linen-look texture\"}\n"
        '  "notes" (str): brief summary\n'
        f'  "verdict" ("pass"|"retry"): pass if seat_count_in_B == 2 AND product_score >= {prod_thr} '
        f"AND composition_score >= {comp_thr} AND not text_in_image AND structure_preserved AND no reference_influences."
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


# ============= fal generate =============

def aspect_ratio_for(w, h):
    r = w / h
    candidates = [("21:9", 21/9), ("16:9", 16/9), ("3:2", 3/2), ("4:3", 4/3),
                  ("1:1", 1.0), ("3:4", 3/4), ("2:3", 2/3), ("9:16", 9/16), ("9:21", 9/21)]
    return min(candidates, key=lambda c: abs(c[1] - r))[0]


def refs_for_panel_class(panel_class, urls):
    base = list(urls["gif"])
    if panel_class == "material_swatch":
        return base + list(urls.get("material", []))
    if panel_class in ("color_option", "module_lineup"):
        return base + list(urls.get("color", []))
    return base


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


async def run_target(label, base_img, layout_map, urls, out_dir, ratio, sem):
    panel_class = layout_map.get("panel_class", "other")
    scene_desc = layout_map.get("spatial_layout", "")
    panel_idx = layout_map.get("panel_idx", 0)
    strategies = ["aligned", "overpaint", "smart_sheet"]
    attempts = []
    prev_output = None
    prev_qa = None

    for attempt_n, strategy in enumerate(strategies, 1):
        tag = f"[{label}/{strategy}/#{attempt_n}]"
        async with sem:
            t0 = time.time()
            zone_refs = refs_for_panel_class(panel_class, urls)
            if strategy == "overpaint":
                if not prev_output:
                    continue
                prev_url = await upload(prev_output)
                ref_urls = [prev_url] + zone_refs
            elif strategy == "smart_sheet":
                ref_urls = [urls[f"base_{label}"], urls["smart_sheet"]] + zone_refs
            else:
                ref_urls = [urls[f"base_{label}"]] + zone_refs

            prompt = build_prompt(panel_idx, layout_map, scene_desc, attempt_n, strategy, prev_qa)

            print(f"{tag} cls={panel_class} ar={ratio} refs={len(ref_urls)}", flush=True)
            img = out_dir / f"{label}__a{attempt_n}_{strategy}.png"
            try:
                gurl = await generate(prompt, ref_urls, ratio)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"{tag} GEN ERR: {e}")
                attempts.append({"attempt": attempt_n, "strategy": strategy, "error": str(e), "prompt": prompt})
                continue

            try:
                verdict = await asyncio.to_thread(qa_bidirectional, base_img, img, panel_class, attempt_n)
            except Exception as e:
                print(f"{tag} QA ERR: {e}")
                attempts.append({"attempt": attempt_n, "strategy": strategy, "image": img.name, "error": f"QA: {e}", "prompt": prompt})
                break

            t_end = time.time()
            attempts.append({
                "attempt": attempt_n, "strategy": strategy, "image": img.name,
                "gen_seconds": round(t_gen - t0, 1),
                "qa_seconds": round(t_end - t_gen, 1),
                "fal_url": gurl, "aspect_ratio": ratio,
                "prompt": prompt,  # ★ 회차별 prompt 저장
                "ref_count": len(ref_urls),
                **verdict,
            })
            prev_output = img
            prev_qa = verdict
            sf = "" if verdict.get("seat_count_in_B") == 2 else f" SEAT={verdict.get('seat_count_in_B')}"
            tf = " TEXT!" if verdict.get("text_in_image") else ""
            ri = f" RI={len(verdict.get('reference_influences', []))}" if verdict.get("reference_influences") else ""
            print(f"{tag} prod={verdict.get('product_score','?')} comp={verdict.get('composition_score','?')}{sf}{tf}{ri} -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (passers[0] if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))

    return {
        "label": label, "panel_idx": panel_idx, "panel_class": panel_class,
        "aspect_ratio": ratio,
        "attempts": attempts, "final": final, "passed": bool(passers),
        "strategies_used": [a["strategy"] for a in attempts if "strategy" in a],
    }


async def main():
    from PIL import Image

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"v6_{ts}"
    run_dir.mkdir()
    out_dir = run_dir / MODEL_NAME
    out_dir.mkdir()

    # targets: cover + all panels using layout_maps
    targets = []
    for layout_map in LAYOUTS.values():
        if "error" in layout_map:
            continue
        panel = layout_map.get("panel", "")
        if panel == "cover":
            target_path = TPL_DIR / "_cover_1000.jpg"
            label = "cover"
        else:
            idx = layout_map.get("panel_idx")
            if idx is None:
                continue
            target_path = next(TPL_DIR.glob(f"panel_{idx:02d}.*"), None)
            if not target_path:
                continue
            label = f"panel_{idx:02d}"
        targets.append({"label": label, "path": target_path, "layout_map": layout_map})

    print(f"=== swap v6 — 4-layer prompt + bidirectional QA ===")
    print(f"  targets: {len(targets)}")
    print(f"  model: {MODEL_NAME}")

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
        jobs.append(run_target(tg["label"], tg["path"], tg["layout_map"],
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
        "prompt_architecture": "4-layer (core/preset/panel/feedback)",
        "qa": "bidirectional (fidelity + reference_influences)",
        "saves_prompt_per_attempt": True,
        "user_request": USER_REQUEST_TXT,
        "cells": cells,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_ROOT / "latest_v6.txt").write_text(run_dir.name)

    passers = sum(1 for c in cells if c["passed"])
    print(f"\n=== DONE === {run_dir}")
    print(f"  wall: {wall}s")
    print(f"  passers: {passers}/{len(cells)}")
    for c in cells:
        v = c.get("final") or {}
        s = "/".join(c.get("strategies_used", []))
        ri = len(v.get("reference_influences") or [])
        print(f"    {c['label']:12} [{c['panel_class']:>16}] prod={v.get('product_score','?')} "
              f"comp={v.get('composition_score','?')} seats={v.get('seat_count_in_B','?')} RI={ri} via={s} pass={c['passed']}")


if __name__ == "__main__":
    asyncio.run(main())

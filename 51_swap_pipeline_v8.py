"""Swap pipeline v8 — strict prompt + image-less (milo refs only) + panel-class 맞춤 framing.

핵심 발견 (panel_02 검증): milo 3 frames만으로도 prompt 강화하면 close-up swap 가능.
- "EXTREME CLOSE-UP", "DO NOT render full sofa", "Camera 30cm" 같은 framing instruction strict
- panel C 이미지 X (시각 영향 방지)
- panel-class별 다른 framing template

13 panels (cover + 12) 전체 실행.
QA: gpt-5, 5점 만점, 모든 score >= 4 = pass.
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
LAYOUTS = {p["panel"]: p for p in json.loads((TPL_DIR / "panel_layout_maps.json").read_text())["panels"]}
USER_OUT = json.loads((USER_DIR / "auto_pipeline_output.json").read_text())
PRODUCT_INPUT = json.loads((USER_DIR / "product_input.json").read_text())

OUT_ROOT = TPL_DIR / "swap_results"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = OUT_ROOT / f"v8_{ts}"
RUN_DIR.mkdir()
OUT_DIR = RUN_DIR / "gpt_image"
OUT_DIR.mkdir()

ENDPOINT = config.MODELS["gpt_image"]
VISION_MODEL = "gpt-5"
CONCURRENCY = 4
MAX_ATTEMPTS = 3

USE_PROD = USER_DIR / "use_product"
GIF_FRAMES = sorted(USE_PROD.glob("p08_frame_0?.jpg"))
COLOR_REFS = sorted(USE_PROD.glob("color_*.png"))
COLOR_VARIANTS = sorted(USE_PROD.glob("p08_frame_*_color_*.webp"))
MATERIAL_REFS = sorted(USE_PROD.glob("material*.png"))


def target_block():
    pi_spec = PRODUCT_INPUT.get("spec", {})
    pi_feat = PRODUCT_INPUT.get("features", {})
    return f"""\
=== [TARGET PRODUCT: 밀로 패브릭소파 2인용] ===
References (IMAGES 1, 2, 3) = 밀로 product (정답 product 모습).
- Fabric: matte linen-look in light beige/oatmeal (NOT leather, NO sheen)
- Arms: VERY THIN slim straight profile, square edges, ~{pi_spec.get('arm_height_cm', 57)}cm (NOT thick padded, NOT rolled)
- Cushions: 2 seat + 2 back, LOOSE puffy with piped seams (NOT tight tailored)
- Seat firmness: {pi_feat.get('seat_cushion_firmness', 'MEDIUM SOFT')}, back: {pi_feat.get('back_cushion_firmness', 'SOFT')}
- Legs: 4 SLIM cylindrical matte black metal, ~{pi_spec.get('leg_height_cm', 14)}cm height, straight cylinder DOWNWARD (NOT V-shape, NOT angled, NOT block)
- Frame: 직각 boxy silhouette, low profile, 2 seats STRICTLY
- Dimensions: {pi_spec.get('width_cm', 200)}×{pi_spec.get('depth_cm', 90)}×{pi_spec.get('height_cm', 85)}cm
"""


# Panel-class별 framing template
FRAMING_TEMPLATES = {
    "intro_hero": """\
=== [FRAMING — COVER HERO SHOT] ===
- White seamless backdrop, eye-level straight-on view
- Centered framing, sofa fills ~70% horizontally
- Soft even shadowless light, subtle floor contact shadow
- 1:1 square composition
- FULL sofa visible (entire 2-seat sofa frame)""",
    "lifestyle_scene": """\
=== [FRAMING — LIFESTYLE ROOM SCENE] ===
Reproduce the lifestyle scene from the spatial layout description below.
- Living room setting with warm wood/concrete tones
- Sofa as the centerpiece
- Soft ambient lighting, natural mood
- Wide-angle composition showing room context""",
    "detail_close_up": """\
=== [FRAMING — EXTREME CLOSE-UP DETAIL SHOT] ===
⚠️ RENDER A MACRO/DETAIL CLOSE-UP — NOT THE FULL SOFA.
⚠️ DO NOT show the entire sofa silhouette.
- Camera: very close, 30-50cm from sofa surface
- Crop: ZOOM IN on the specific detail mentioned in the spatial description below
- Only ~30-40% of sofa visible horizontally; rest is cropped out
- Sharp focus on fabric texture, leg detail, seam, or cushion edge
- White or neutral background, soft directional light
- Like macro product photography""",
    "size_chart": """\
=== [FRAMING — SIZE CHART DIAGRAM (FIXED LAYOUT)] ===
- Light gray flat background (no room, no props)
- Sofa rendered as 3/4-side illustration in upper center
- Dimension lines on RIGHT side (vertical: height 85cm) and BOTTOM (horizontal: 200cm × 90cm depth)
- Dimension line marks with simple arrowheads (no numbers — text added by HTML overlay later)
- Below sofa: empty space for "다릿발 높이/좌방석 깊이/좌방석 높이" labels (HTML overlay)
- Below that: 2 firmness bars (좌방석 + 등쿠션), 5 dots each, red dot positions:
  · 좌방석 bar: red dot at position 4 of 5 (MEDIUM SOFT, NOT center)
  · 등쿠션 bar: red dot at position 5 of 5 (SOFT, far right, NOT center)
- ABSOLUTELY NO Korean/English text in output — render only the visual chart elements (sofa, lines, arrow heads, dots, bar lines)""",
    "structure_chart": """\
=== [FRAMING — STRUCTURE / MATERIAL DIAGRAM (FIXED LAYOUT)] ===
- Light background, infographic style
- Sofa illustration showing internal layers/cross-section
- Different material regions highlighted (좌방석 / 등쿠션 / 프레임 / 다리)
- ABSOLUTELY NO text rendered""",
    "color_option": """\
=== [FRAMING — COLOR OPTION GRID (FIXED LAYOUT)] ===
- 3 sofa instances arranged in a row, identical pose (3/4 side view, hero style)
- Each in a different fabric color (오트밀 / 라이트그레이 / 더스티로즈) — use the color reference images
- White seamless background, equal spacing
- NO text rendered (color names HTML overlay later)""",
    "module_lineup": """\
=== [FRAMING — MODULE LINEUP] ===
- Multiple sofa variants side by side, in a row, same pose
- Use color variant reference images
- Show ONLY the 2-seat MILO (not multiple seat counts)
- White seamless background, NO text rendered""",
    "material_swatch": """\
=== [FRAMING — MATERIAL SWATCH / TEXTURE CLOSE-UP] ===
- Macro shot of fabric weave texture
- Wide flat fabric area filling the frame
- Slight angle to show weave detail and seam piping
- Light beige (oatmeal tone), matte linen-look
- NO text rendered""",
    "product_shot": """\
=== [FRAMING — CLEAN PRODUCT SHOT] ===
- White seamless backdrop
- 3/4-side view of full sofa, hero pose
- Eye-level, centered, soft even light
- Subtle floor shadow""",
    "delivery_info": """\
=== [FRAMING — DELIVERY INFO PANEL] ===
- Plain background, infographic style
- Visual icons only, NO text (HTML overlay)""",
    "context": """\
=== [FRAMING — CONTEXT/BRANDING] ===
- Soft ambient scene, atmospheric
- Sofa partial view OK, mood-focused
- NO text""",
    "other": "",
}


def build_prompt(panel_idx, layout_map, attempt_n, prev_qa=None):
    panel_class = layout_map.get("panel_class", "other")
    spatial = layout_map.get("spatial_layout", "")
    elements = layout_map.get("elements", []) or []
    elements_str = "\n".join(f"  - {e.get('role','?')} @ {e.get('position','?')}: {e.get('description','')}"
                              for e in elements)

    feedback = ""
    if attempt_n > 1 and prev_qa:
        failures = prev_qa.get("specific_failures", []) or []
        ris = prev_qa.get("reference_influences", []) or []
        if failures or ris:
            fb_lines = []
            for f in failures:
                fb_lines.append(f"  - {f}")
            for r in ris:
                fb_lines.append(f"  - {r.get('element_ko','?')} 잘못 → {r.get('correction_ko','?')}")
            feedback = f"\n\n=== [PREVIOUS ATTEMPT FAILED — FIX THESE] ===\n" + "\n".join(fb_lines)

    return f"""\
TASK: Photorealistic furniture detail-page panel rendering.

References: IMAGES 1+ = MILO product references (the actual product to render).

{target_block()}

{FRAMING_TEMPLATES.get(panel_class, FRAMING_TEMPLATES['other'])}

=== [PANEL SPATIAL LAYOUT (reproduce composition, render milo sofa)] ===
{spatial}

Elements present:
{elements_str or '  (none)'}

{feedback}

=== [ABSOLUTE RULES] ===
1. Sofa = ENTIRE milo (body + arms + cushions + fabric + legs).
2. NO leather, NO V-shape legs, NO thick padded arms, NO tufting.
3. Strictly 2 seats.
4. NO text in output (zero characters in any language).
"""


def qa(panel_orig, swap_result, panel_idx, panel_class):
    is_chart = panel_class in ("size_chart", "structure_chart", "color_option", "module_lineup")
    is_closeup = panel_class == "detail_close_up"
    extra = ""
    if is_chart:
        extra = "5) chart_layout (1-5): chart structure (line/arrow/bar/grid) 정확 보존?\n"
    if is_closeup:
        extra = "5) closeup_framing (1-5): close-up crop (full sofa view 아님)?\n"

    qa_prompt = (
        f"한국어 엄격 QA (gpt-5). Panel {panel_idx} class={panel_class}.\n"
        "타겟: 밀로 2인 패브릭소파 (가죽 X, V자 다리 X, thin slim 팔걸이, loose puffy 쿠션).\n"
        "원본 C: 한샘 가죽 sofa (영향 받으면 안 됨).\n\n"
        "이미지: A=milo ref, B=swap 결과, C=한샘 원본 panel.\n\n"
        "5점 만점 평가 (각 1-5):\n"
        "1) arm_thinness: B 팔걸이 thin slim (vs C thick padded)\n"
        "2) cushion_loose: B 쿠션 loose puffy (vs C tailored)\n"
        "3) fabric_matte: B 패브릭 matte linen (vs C 가죽 광택)\n"
        "4) leg_slim_cylinder: B 다리 slim cylindrical 직립 (vs C V자)\n"
        f"{extra}"
        "JSON: {\"scores\":{...}, \"product_score\":0-100, \"composition_score\":0-100, \"seat_count_in_B\":int, "
        "\"underswap\":bool, \"text_in_image\":bool, "
        "\"specific_failures\":[한국어 list], "
        "\"reference_influences\":[{\"element_ko\":..,\"source\":\"C\",\"correction_ko\":..}], "
        "\"notes\":\"한국어 요약\", "
        "\"verdict\":\"pass\"|\"retry\"} — pass = all scores >= 4 AND not underswap AND not text_in_image."
    )
    resp = openai_client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": qa_prompt},
            {"type": "text", "text": "IMAGE A:"},
            {"type": "image_url", "image_url": {"url": data_uri(GIF_FRAMES[0])}},
            {"type": "text", "text": "IMAGE B:"},
            {"type": "image_url", "image_url": {"url": data_uri(swap_result)}},
            {"type": "text", "text": "IMAGE C:"},
            {"type": "image_url", "image_url": {"url": data_uri(panel_orig)}},
        ]}],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


def aspect_ratio_for(w, h):
    r = w / h
    candidates = [("21:9", 21/9), ("16:9", 16/9), ("3:2", 3/2), ("4:3", 4/3),
                  ("1:1", 1.0), ("3:4", 3/4), ("2:3", 2/3), ("9:16", 9/16), ("9:21", 9/21)]
    return min(candidates, key=lambda c: abs(c[1] - r))[0]


def refs_for_class(panel_class, urls):
    base = list(urls["gif"])
    if panel_class == "color_option" or panel_class == "module_lineup":
        return base + list(urls.get("color_variants", [])) + list(urls.get("color", []))
    if panel_class == "material_swatch":
        return base + list(urls.get("material", []))
    return base


async def generate(prompt, ref_urls, ar):
    args = {"prompt": prompt, "image_urls": ref_urls, "aspect_ratio": ar}
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
    raise ValueError("no url")


async def run_target(label, base_img, layout_map, urls, ratio, sem):
    panel_idx = layout_map.get("panel_idx", 0)
    panel_class = layout_map.get("panel_class", "other")
    attempts = []
    prev_qa = None
    prev_output = None

    for attempt_n in range(1, MAX_ATTEMPTS + 1):
        tag = f"[{label}/#{attempt_n}]"
        async with sem:
            t0 = time.time()
            prompt = build_prompt(panel_idx, layout_map, attempt_n, prev_qa)
            zone_refs = refs_for_class(panel_class, urls)
            # attempt 2+: include prev output as overpaint (still no panel C)
            if attempt_n > 1 and prev_output:
                prev_url = await upload(prev_output)
                ref_urls = [prev_url] + zone_refs
                strategy = "overpaint_no_C"
            else:
                ref_urls = zone_refs  # image-less, panel C 없음
                strategy = "imageless"

            print(f"{tag} cls={panel_class} ar={ratio} refs={len(ref_urls)} strat={strategy}", flush=True)
            img = OUT_DIR / f"{label}__a{attempt_n}_{strategy}.png"
            try:
                gurl = await generate(prompt, ref_urls, ratio)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"{tag} GEN ERR: {e}")
                attempts.append({"attempt": attempt_n, "strategy": strategy, "error": str(e), "prompt": prompt})
                continue

            try:
                verdict = await asyncio.to_thread(qa, base_img, img, panel_idx, panel_class)
            except Exception as e:
                print(f"{tag} QA ERR: {e}")
                attempts.append({"attempt": attempt_n, "strategy": strategy, "image": img.name, "error": f"QA: {e}", "prompt": prompt})
                break

            t_end = time.time()
            attempts.append({
                "attempt": attempt_n, "strategy": strategy, "image": img.name,
                "gen_seconds": round(t_gen - t0, 1), "qa_seconds": round(t_end - t_gen, 1),
                "fal_url": gurl, "aspect_ratio": ratio, "prompt": prompt, **verdict,
            })
            prev_output = img
            prev_qa = verdict
            scores = verdict.get("scores", {})
            min_score = min(scores.values()) if scores else 0
            us = " UNDERSWAP" if verdict.get("underswap") else ""
            tf = " TEXT" if verdict.get("text_in_image") else ""
            print(f"{tag} prod={verdict.get('product_score','?')} comp={verdict.get('composition_score','?')} "
                  f"min_score={min_score}{us}{tf} -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (passers[0] if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))
    return {
        "label": label, "panel_idx": panel_idx, "panel_class": panel_class,
        "aspect_ratio": ratio, "attempts": attempts, "final": final,
        "passed": bool(passers),
        "strategies_used": [a["strategy"] for a in attempts if "strategy" in a],
    }


async def main():
    from PIL import Image

    targets = []
    cover_path = TPL_DIR / "_cover_1000.jpg"
    cover_layout = LAYOUTS.get("cover", {"panel_class": "intro_hero", "spatial_layout": "Cover hero shot, white seamless backdrop, centered."})
    cover_layout["panel_idx"] = 0
    targets.append({"label": "cover", "path": cover_path, "layout_map": cover_layout})

    for layout_map in LAYOUTS.values():
        panel = layout_map.get("panel", "")
        if panel == "cover" or "error" in layout_map:
            continue
        idx = layout_map.get("panel_idx")
        if idx is None:
            continue
        ppath = next(TPL_DIR.glob(f"panel_{idx:02d}.*"), None)
        if not ppath:
            continue
        targets.append({"label": f"panel_{idx:02d}", "path": ppath, "layout_map": layout_map})

    print(f"=== swap v8 — strict prompt + image-less + panel-class framing ===")
    print(f"  targets: {len(targets)}")
    print(f"  QA: gpt-5\n")

    print("uploading refs...")
    gif_urls = await asyncio.gather(*[upload(p) for p in GIF_FRAMES])
    color_urls = await asyncio.gather(*[upload(p) for p in COLOR_REFS]) if COLOR_REFS else []
    color_variant_urls = await asyncio.gather(*[upload(p) for p in COLOR_VARIANTS]) if COLOR_VARIANTS else []
    material_urls = await asyncio.gather(*[upload(p) for p in MATERIAL_REFS]) if MATERIAL_REFS else []
    urls = {"gif": list(gif_urls), "color": list(color_urls),
            "color_variants": list(color_variant_urls), "material": list(material_urls)}
    print(f"  gif={len(gif_urls)} color={len(color_urls)} variants={len(color_variant_urls)} material={len(material_urls)}\n")

    sem = asyncio.Semaphore(CONCURRENCY)
    t0 = time.time()
    jobs = []
    for tg in targets:
        w, h = Image.open(tg["path"]).size
        ratio = aspect_ratio_for(w, h)
        jobs.append(run_target(tg["label"], tg["path"], tg["layout_map"], urls, ratio, sem))

    results = await asyncio.gather(*jobs, return_exceptions=True)
    cells = [r for r in results if isinstance(r, dict)]

    wall = round(time.time() - t0, 1)
    summary = {
        "run": RUN_DIR.name, "model": "gpt_image", "vision_qa": VISION_MODEL,
        "wall_seconds": wall, "approach": "strict prompt + image-less (no panel C as ref) + panel-class framing",
        "cells": cells,
    }
    (RUN_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_ROOT / "latest_v8.txt").write_text(RUN_DIR.name)

    passers = sum(1 for c in cells if c["passed"])
    print(f"\n=== DONE === {RUN_DIR}")
    print(f"  wall: {wall}s · passers: {passers}/{len(cells)}")
    for c in cells:
        v = c.get("final") or {}
        scores = v.get("scores", {})
        print(f"    {c['label']:12} [{c['panel_class']:>17}] prod={v.get('product_score','?'):>3} "
              f"min_score={min(scores.values()) if scores else 0} pass={c['passed']}")


if __name__ == "__main__":
    asyncio.run(main())

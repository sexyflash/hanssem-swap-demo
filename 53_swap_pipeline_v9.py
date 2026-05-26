"""Swap pipeline v9 — gpt-image-2 + quality=high + 명시적 edit (X→Y) + panel C base + milo refs.

발견:
- gpt-image-2가 1.5보다 압도적으로 정확 (한글 텍스트 깨짐 없음, panel_04 1차 PASS prod 100)
- "X → Y" 명시적 edit 지시가 모델에게 정확한 신호
- panel C base + milo refs 조합이 정답 (edit task)

panel-class별 explicit edit template:
- intro_hero / product_shot: full sofa swap (4-seat leather → 2-seat fabric MILO)
- lifestyle_scene: 같은 룸/조명/구도 보존 + sofa만 milo로
- detail_close_up: layout 그대로, sofa region만 milo로 (특히 arm/leg/cushion edge 정확)
- size_chart: dim 수치 + firmness 빨간점 위치 명시 변경
- structure_chart: 마감재 영역 변경
- color_option: 컬러 swatch 변경
- module_lineup: 사이즈/seat count 변경

retry feedback loop (gpt-5 QA).
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
PRODUCT_INPUT = json.loads((USER_DIR / "product_input.json").read_text())

OUT_ROOT = TPL_DIR / "swap_results"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = OUT_ROOT / f"v9_{ts}"
RUN_DIR.mkdir()
OUT_DIR = RUN_DIR / "gpt_image"
OUT_DIR.mkdir()

ENDPOINT = "fal-ai/gpt-image-2/edit"  # 2.0 — 큰 개선
VISION_MODEL = "gpt-5"
CONCURRENCY = 3  # gpt-image-2 generation 느림 (~2min) — concurrency 적당히
MAX_ATTEMPTS = 2  # 2.0이 더 정확하니 attempt 줄임

USE_PROD = USER_DIR / "use_product"
GIF_FRAMES = sorted(USE_PROD.glob("p08_frame_0?.jpg"))
COLOR_REFS = sorted(USE_PROD.glob("color_*.png"))
COLOR_VARIANTS = sorted(USE_PROD.glob("p08_frame_*_color_*.webp"))


# ====== common product target block ======
def target_summary():
    pi_spec = PRODUCT_INPUT.get("spec", {})
    pi_feat = PRODUCT_INPUT.get("features", {})
    return (
        f"TARGET: 밀로 패브릭소파 2인용 — 가로 {pi_spec.get('width_cm',200)} × 깊이 {pi_spec.get('depth_cm',90)} × 높이 {pi_spec.get('height_cm',85)}cm, "
        f"좌방석 깊이 {pi_spec.get('seat_depth_cm',52)}cm, 좌방석 높이 {pi_spec.get('seat_height_cm',45)}cm, "
        f"팔걸이 높이 {pi_spec.get('arm_height_cm',57)}cm, 다릿발 {pi_spec.get('leg_height_cm',14)}cm. "
        f"좌방석 firmness {pi_feat.get('seat_cushion_firmness','MEDIUM SOFT')} (4번째 점), "
        f"등쿠션 {pi_feat.get('back_cushion_firmness','SOFT')} (5번째 점). "
        f"패브릭 (linen-look matte, 라이트 베이지/오트밀), thin slim 팔걸이, loose puffy 쿠션, slim cylindrical matte-black 다리. "
        f"가죽 X, V자 다리 X, 두꺼운 팔걸이 X, 헤드레스트 X, USB/control X."
    )


# ====== panel-class별 explicit edit template ======
def build_explicit_prompt(panel_idx, layout_map, attempt_n, prev_qa=None):
    panel_class = layout_map.get("panel_class", "other")
    spatial = layout_map.get("spatial_layout", "")
    elements = layout_map.get("elements", []) or []
    visible_text = layout_map.get("text_zones", []) or []
    elements_str = "\n".join(f"  - {e.get('role','?')} @ {e.get('position','?')}: {e.get('description','')}" for e in elements)

    edit_block = ""
    if panel_class == "size_chart":
        edit_block = """\
EXPLICIT EDITS for this size chart panel:
[1] CHANGE SOFA: 4-seat leather → 2-seat fabric MILO (white→beige fabric, slim arms, slim cylindrical legs)
[2] CHANGE DIMENSION NUMBERS: "300"→"200", "112"→"90", "86"→"85"
[3] CHANGE SUB-DIMENSIONS: "다릿발 높이 : 12cm"→"다릿발 높이 : 14cm", "좌방석 깊이 : 55cm"→"좌방석 깊이 : 52cm", "좌방석 높이 : 49cm"→"좌방석 높이 : 45cm"
[4] CHANGE FIRMNESS RED DOT POSITIONS:
  - 좌방석 bar: red dot move from position 3 (MEDIUM, center) → position 4 (MEDIUM SOFT)
  - 등쿠션 bar: red dot move from position 3 (MEDIUM) → position 5 (SOFT, far-right)
KEEP: layout, dim-line style, all other Korean text, bar structure with 5 dots.
"""
    elif panel_class == "structure_chart":
        edit_block = """\
EXPLICIT EDITS for this structure/material chart panel:
[1] CHANGE SOFA in diagram: 4-seat leather → 2-seat fabric MILO
[2] CHANGE MATERIAL LABELS (if Korean text appears):
  - 마감재: "이태리 펠레밀라노 천연 소가죽 + PVC" → "폴리니크 패브릭 (생활발수, OEKO-TEX 인증)"
  - 좌방석: 기존 → "32kg 고밀도 통스펀지 + 덕페더 67% + 마이크로화이버 33%"
  - 등쿠션: 기존 → "덕페더 67% + 마이크로화이버 33%"
  - 프레임: 기존 → "EO 건조목, S자 스프링, 엘라스틱벨트"
  - 헤드레스트 항목: REMOVE (milo엔 없음)
KEEP: cross-section layout, region highlighting style, table structure.
"""
    elif panel_class == "color_option":
        edit_block = """\
EXPLICIT EDITS for this color option/module panel:
[1] CHANGE SOFAS: 4-seat leather (그레이/도브그레이/스카이그레이) → 2-seat fabric MILO (오트밀/라이트그레이/더스티로즈)
[2] CHANGE LABELS (if Korean text):
  - "키안티 가죽 3인 / 4인" → "밀로 패브릭 2인용"
  - Dimensions: "221 X 112 X 86" or "300 X 112 X 86" → "200 X 90 X 85"
  - Color names: 한샘 colors → "오트밀 / 라이트그레이 / 더스티로즈"
KEEP: grid layout, equal spacing, swatch positions.
Use color reference images for accurate fabric colors.
"""
    elif panel_class == "module_lineup":
        edit_block = """\
EXPLICIT EDITS for module lineup panel:
[1] CHANGE all sofas: 4-seat or different-seat-count leather variants → SAME 2-seat fabric MILO variant in different colors
[2] CHANGE LABELS:
  - "키안티 4인" or other → "밀로 2인용"
  - Dimensions → "200 X 90 X 85" for all
  - Show 3 milo variants in 3 colors (오트밀/라이트그레이/더스티로즈) using color reference images
KEEP: side-by-side layout, equal spacing.
"""
    elif panel_class == "detail_close_up":
        edit_block = f"""\
EXPLICIT EDITS for this close-up detail panel:
[1] CHANGE SOFA SURFACE: leather (광택, smooth) → fabric (matte linen-look, light beige)
[2] CHANGE ARMS: thick padded leather arm → thin slim straight fabric arm
[3] CHANGE LEGS: V-shape chrome metal → slim cylindrical matte-black metal (straight down)
[4] CHANGE CUSHIONS: tailored tight → loose puffy with piped seams
[5] REMOVE: any USB/control panel, headrest, recliner mechanism (milo doesn't have these)
KEEP: camera angle, framing/crop (close-up, not full sofa view), lighting direction, background, shadow.
This panel's spatial layout: {spatial[:200]}
"""
    elif panel_class == "lifestyle_scene":
        edit_block = """\
EXPLICIT EDITS for this lifestyle scene:
[1] CHANGE SOFA: 4-seat leather (dark/light leather, V-shape legs, thick arms, headrest) → 2-seat fabric MILO (light beige fabric, slim arms, slim cylindrical legs, NO headrest)
[2] CHANGE SCALE: sofa is smaller (2-seat) — adjust positioning if needed to maintain natural scale in room
KEEP: room (wall, floor, coffee table, lighting, props), camera angle, framing, mood, color tone.
"""
    elif panel_class in ("intro_hero", "product_shot"):
        edit_block = """\
EXPLICIT EDITS for this hero/product shot:
[1] CHANGE SOFA completely: 4-seat leather → 2-seat fabric MILO
- Body: leather sheen → matte linen fabric in light beige
- Arms: thick padded → thin slim straight
- Legs: V-shape chrome → slim cylindrical matte-black
- Cushions: tailored → loose puffy with piped seams
- Frame: 4-seat → 2-seat (smaller)
- Headrest: REMOVE
KEEP: white seamless background, eye-level camera, soft even lighting, centered framing, subtle floor shadow.
"""
    elif panel_class == "material_swatch":
        edit_block = """\
EXPLICIT EDITS for material swatch panel:
[1] CHANGE TEXTURE: leather/other → matte linen-look fabric (light beige/oatmeal weave)
[2] CHANGE LABELS (if Korean text):
  - 가죽 관련 → "폴리니크 패브릭, 생활발수, OEKO-TEX"
KEEP: close-up framing, lighting that shows weave detail.
"""
    else:
        edit_block = """\
EXPLICIT EDITS:
[1] CHANGE SOFA: any leather sofa variant → 2-seat fabric MILO (위 TARGET 참조)
KEEP: layout, composition, lighting, all non-sofa elements.
"""

    feedback = ""
    if attempt_n > 1 and prev_qa:
        failures = prev_qa.get("specific_failures", []) or []
        ris = prev_qa.get("reference_influences", []) or []
        if failures or ris:
            lines = []
            for f in failures:
                lines.append(f"  - {f}")
            for r in ris:
                lines.append(f"  - {r.get('element_ko','?')} 잘못 → {r.get('correction_ko','?')}")
            feedback = "\n\n=== [PREVIOUS ATTEMPT FAILED — FIX THESE] ===\n" + "\n".join(lines)

    return f"""\
TASK: Edit this Korean furniture detail-page panel.

IMAGE 1 = ORIGINAL panel (한샘 가죽 sofa template — edit base).
IMAGES 2+ = MILO product references (the new product to replace with).

{target_summary()}

=== [SPATIAL LAYOUT TO PRESERVE] ===
{spatial}

Elements:
{elements_str or '  (none)'}

=== [EDIT INSTRUCTIONS] ===
{edit_block}

{feedback}

=== [ABSOLUTE RULES] ===
- Result must look like a Korean detail-page panel (한국 가구 상세페이지) — same visual style as the original.
- Any remaining Korean text must be readable and accurate (not garbled).
- No leather sheen, no V-shape legs, no thick padded arms, no headrest, no USB.
- Strictly 2 seats.
"""


def qa(panel_orig, swap_result, panel_idx, panel_class):
    is_chart = panel_class in ("size_chart", "structure_chart", "color_option", "module_lineup")
    extra = ""
    if is_chart:
        extra = """\
5) chart_layout_preserved (1-5): chart 구조 (line/arrow/bar/grid) 정확 보존?
6) text_readable_korean (1-5): 한국어 텍스트 깨짐 없이 정확히 읽힘?
7) numbers_correct (1-5): 수치 변경 정확? (size chart: 200/90/85, 52/45/14 / firmness 빨간점 위치)
"""

    qa_prompt = (
        f"한국어 엄격 QA (gpt-5). Panel {panel_idx} class={panel_class}.\n"
        "타겟: 밀로 2인 패브릭소파.\n"
        "원본 C: 한샘 가죽 sofa.\n\n"
        "이미지: A=milo ref, B=swap 결과, C=한샘 원본 panel.\n\n"
        "5점 만점 평가:\n"
        "1) arm_thinness: B 팔걸이 thin slim?\n"
        "2) cushion_loose: B 쿠션 loose puffy?\n"
        "3) fabric_matte: B 패브릭 matte linen?\n"
        "4) leg_slim_cylinder: B 다리 slim cylindrical?\n"
        f"{extra}"
        "JSON: {\"scores\":{...}, \"product_score\":0-100, \"composition_score\":0-100, \"seat_count_in_B\":int, "
        "\"underswap\":bool, \"text_in_image_garbled\":bool, "
        "\"specific_failures\":[한국어 list], "
        "\"reference_influences\":[{\"element_ko\":..,\"source\":\"C\",\"correction_ko\":..}], "
        "\"notes\":\"한국어\", "
        "\"verdict\":\"pass\"|\"retry\"} — pass = all scores >= 4 AND not underswap AND not text_garbled."
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


def image_size_for(w, h):
    r = w / h
    if r < 0.8:
        return "portrait_4_3"
    if r > 1.2:
        return "landscape_4_3"
    return "square"


def refs_for_class(panel_class, urls, base_url):
    """panel C as base + milo refs (+ zone-specific)."""
    refs = [base_url] + list(urls["gif"])
    if panel_class in ("color_option", "module_lineup"):
        refs += list(urls.get("color_variants", [])) + list(urls.get("color", []))
    return refs


async def generate(prompt, ref_urls, image_size):
    args = {
        "prompt": prompt, "image_urls": ref_urls,
        "quality": "high", "image_size": image_size, "output_format": "png",
    }
    result = await fal_client.subscribe_async(ENDPOINT, arguments=args)
    imgs = result.get("images") or result.get("image")
    if isinstance(imgs, list) and imgs:
        first = imgs[0]
        return first["url"] if isinstance(first, dict) else first
    if isinstance(imgs, dict):
        return imgs["url"]
    raise ValueError("no url")


async def run_target(label, base_img, layout_map, urls, image_size, sem):
    panel_idx = layout_map.get("panel_idx", 0)
    panel_class = layout_map.get("panel_class", "other")
    base_url = urls[f"base_{label}"]
    attempts = []
    prev_qa = None

    for attempt_n in range(1, MAX_ATTEMPTS + 1):
        tag = f"[{label}/#{attempt_n}]"
        async with sem:
            t0 = time.time()
            prompt = build_explicit_prompt(panel_idx, layout_map, attempt_n, prev_qa)
            ref_urls = refs_for_class(panel_class, urls, base_url)

            print(f"{tag} cls={panel_class} size={image_size} refs={len(ref_urls)} attempt={attempt_n}", flush=True)
            img = OUT_DIR / f"{label}__a{attempt_n}_v2.png"
            try:
                gurl = await generate(prompt, ref_urls, image_size)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"{tag} GEN ERR: {e}")
                attempts.append({"attempt": attempt_n, "error": str(e), "prompt": prompt})
                continue

            try:
                verdict = await asyncio.to_thread(qa, base_img, img, panel_idx, panel_class)
            except Exception as e:
                print(f"{tag} QA ERR: {e}")
                attempts.append({"attempt": attempt_n, "image": img.name, "error": f"QA: {e}", "prompt": prompt})
                break

            t_end = time.time()
            attempts.append({
                "attempt": attempt_n, "image": img.name,
                "gen_seconds": round(t_gen - t0, 1), "qa_seconds": round(t_end - t_gen, 1),
                "fal_url": gurl, "image_size": image_size, "prompt": prompt, **verdict,
            })
            prev_qa = verdict
            scores = verdict.get("scores", {})
            min_score = min(scores.values()) if scores else 0
            print(f"{tag} prod={verdict.get('product_score','?')} comp={verdict.get('composition_score','?')} "
                  f"min_score={min_score} -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (passers[0] if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))
    return {
        "label": label, "panel_idx": panel_idx, "panel_class": panel_class,
        "image_size": image_size, "attempts": attempts, "final": final,
        "passed": bool(passers),
    }


async def main():
    from PIL import Image

    targets = []
    cover_path = TPL_DIR / "_cover_1000.jpg"
    cover_layout = LAYOUTS.get("cover", {"panel_class": "intro_hero", "spatial_layout": "Cover hero, white seamless."})
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

    print(f"=== swap v9 — gpt-image-2 + quality=high + 명시적 edit + panel C base ===")
    print(f"  endpoint: {ENDPOINT}")
    print(f"  targets: {len(targets)}\n")

    print("uploading refs...")
    gif_urls = await asyncio.gather(*[upload(p) for p in GIF_FRAMES])
    color_urls = await asyncio.gather(*[upload(p) for p in COLOR_REFS]) if COLOR_REFS else []
    color_variant_urls = await asyncio.gather(*[upload(p) for p in COLOR_VARIANTS]) if COLOR_VARIANTS else []
    base_urls = {}
    for tg in targets:
        base_urls[f"base_{tg['label']}"] = await upload(tg["path"])
    urls = {**base_urls, "gif": list(gif_urls), "color": list(color_urls), "color_variants": list(color_variant_urls)}

    sem = asyncio.Semaphore(CONCURRENCY)
    t0 = time.time()
    jobs = []
    for tg in targets:
        w, h = Image.open(tg["path"]).size
        size_param = image_size_for(w, h)
        jobs.append(run_target(tg["label"], tg["path"], tg["layout_map"], urls, size_param, sem))

    results = await asyncio.gather(*jobs, return_exceptions=True)
    cells = [r for r in results if isinstance(r, dict)]
    wall = round(time.time() - t0, 1)
    summary = {
        "run": RUN_DIR.name, "endpoint": ENDPOINT, "vision_qa": VISION_MODEL,
        "wall_seconds": wall, "cells": cells,
    }
    (RUN_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_ROOT / "latest_v9.txt").write_text(RUN_DIR.name)

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

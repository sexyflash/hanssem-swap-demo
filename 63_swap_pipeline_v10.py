"""Swap pipeline v10 — multi-tier ref sheets로 10-slot 제약 해소.

새 ref 패턴 (총 7장):
  [1~3] 메인 대표 사진 — p08_frame_01.jpg, 02.jpg, 03.jpg
  [4]   디테일 시트 — milo_detail_sheet.png (담당자 업로드 후 — 옵셔널)
  [5]   컬러 시트 — milo_color_sheet.png (3 variants + 3 swatches 합성)
  [6]   가이드 시트 — milo_guide_sheet.png (PRESERVE/NEVER + 미니 다각도)
  [7]   panel C — 해당 panel 원본 한샘 이미지 (edit base)

v9 대비 변경:
- COLOR_REFS / COLOR_VARIANTS 슬롯 펴기 → 시트 1장으로 통합
- detail_close_up 시 디테일 시트 첨부 (있을 때)
- guide_sheet 항상 첨부 (모든 panel에 PRESERVE/NEVER 의지 전달)

dense v3 (product_input_v3.json) target_summary 사용.
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

# v3 (dense) → v2 → v1 fallback
PI_V3 = USER_DIR / "product_input_v3.json"
PI_V2 = USER_DIR / "product_input_v2.json"
PI_V1 = USER_DIR / "product_input.json"
PRODUCT_INPUT = json.loads((PI_V3 if PI_V3.exists() else PI_V2 if PI_V2.exists() else PI_V1).read_text())
IS_V3 = "feature_descriptions" in PRODUCT_INPUT

OUT_ROOT = TPL_DIR / "swap_results"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = OUT_ROOT / f"v10_{ts}"
RUN_DIR.mkdir()
OUT_DIR = RUN_DIR / "gpt_image"
OUT_DIR.mkdir()

ENDPOINT = "fal-ai/gpt-image-2/edit"
VISION_MODEL = "gpt-5"
CONCURRENCY = 3
MAX_ATTEMPTS = 2

USE_PROD = USER_DIR / "use_product"
PREP_DIR = USER_DIR / "preprocessed"

# Tier 1 — 메인 대표 3장
MAIN_VIEWS = [
    USE_PROD / "p08_frame_01.jpg",
    USE_PROD / "p08_frame_02.jpg",
    USE_PROD / "p08_frame_03.jpg",
]
# Tier 2 — 단일 통합 마스터 시트 (모든 디테일/컬러/소재/가이드 1장 통합)
SHEET_MASTER = PREP_DIR / "milo_master_sheet.png"


def target_summary():
    if IS_V3:
        sp = PRODUCT_INPUT.get("spec", {})
        fd = PRODUCT_INPUT.get("feature_descriptions", {})
        return (
            "TARGET: 밀로 패브릭소파 2인용.\n"
            f"  · 제원 — 가로 {sp.get('width_cm',200)} × 깊이 {sp.get('depth_cm',90)} × 높이 {sp.get('height_cm',85)}cm, "
            f"좌방석 깊이 {sp.get('seat_depth_cm',52)}cm/높이 {sp.get('seat_height_cm',45)}cm, "
            f"팔걸이 {sp.get('arm_height_cm',57)}cm, 다리 {sp.get('leg_height_cm',14)}cm.\n"
            f"  · 다리 (정확): {fd.get('legs_detail','')[:200]}\n"
            f"  · 팔걸이: {fd.get('arms_detail','')[:160]}\n"
            f"  · 좌방석: {fd.get('seat_cushions_detail','')[:160]}\n"
            f"  · 등쿠션: {fd.get('back_cushions_detail','')[:160]}\n"
            f"  · 시접: {fd.get('seam_styles','')[:180]}\n"
            f"  · 패브릭: {fd.get('fabric_texture','')[:160]}\n"
            "  · 가죽 X · V자 다리 X · 두꺼운 padded 팔걸이 X · 헤드레스트 X · USB X."
        )
    # v1 fallback (간단)
    sp = PRODUCT_INPUT.get("spec", {})
    feat = PRODUCT_INPUT.get("features", {})
    return (
        f"TARGET: 밀로 패브릭소파 2인용 — {sp.get('width_cm',200)}×{sp.get('depth_cm',90)}×{sp.get('height_cm',85)}cm. "
        f"좌방석 {feat.get('seat_cushion_firmness','MEDIUM SOFT')}, 등쿠션 {feat.get('back_cushion_firmness','SOFT')}. "
        f"매트 패브릭, slim 팔걸이, 매트블랙 원통형 다리 5개 (모서리 4 + 중앙 1). 가죽 X · 헤드레스트 X."
    )


def build_explicit_prompt(panel_idx, layout_map, attempt_n, prev_qa=None):
    panel_class = layout_map.get("panel_class", "other")
    spatial = layout_map.get("spatial_layout", "")
    elements = layout_map.get("elements", []) or []
    elements_str = "\n".join(f"  - {e.get('role','?')} @ {e.get('position','?')}: {e.get('description','')}" for e in elements)

    edit_block = build_edit_block(panel_class, spatial)

    feedback = ""
    if attempt_n > 1 and prev_qa:
        failures = prev_qa.get("specific_failures", []) or []
        ris = prev_qa.get("reference_influences", []) or []
        if failures or ris:
            lines = [f"  - {f}" for f in failures]
            lines += [f"  - {r.get('element_ko','?')} 잘못 → {r.get('correction_ko','?')}" for r in ris]
            feedback = "\n=== [PREVIOUS ATTEMPT FAILED — FIX THESE] ===\n" + "\n".join(lines)

    return f"""\
TASK: Edit this Korean furniture detail-page panel.

REFERENCE PATTERN (이번 호출의 image_urls 순서):
  IMAGE 1 = panel C (한샘 원본 panel — edit base, layout 그대로 유지)
  IMAGE 2,3,4 = MILO 메인 대표 사진 (정면/측면/3-4 각도)
  IMAGE 5 = MILO MASTER SHEET (12셀 통합 시트 — 디테일+컬러+소재+PRESERVE/NEVER 모두 포함)
            마스터 시트의 PRESERVE/NEVER 박스를 반드시 인지하고 violate 금지.

{target_summary()}

=== [SPATIAL LAYOUT TO PRESERVE] ===
{spatial}

Elements:
{elements_str or '  (none)'}

=== [EDIT INSTRUCTIONS] ===
{edit_block}

{feedback}

=== [ABSOLUTE RULES — 마스터 시트의 PRESERVE/NEVER 와 동일] ===
- 결과는 한국 가구 상세페이지 panel — 원본과 같은 visual style.
- 모든 한글 텍스트 깨짐 X.
- 마스터 시트 PRESERVE/NEVER 박스 항목 절대 violate 금지.
- 할루시네이션 금지: reference 이미지에 없는 정보 (다리 개수, 쿠션 모양, 색상)
  임의로 추가하거나 변경하지 마라.
- 좌석수 정확히 2.
"""


def build_edit_block(panel_class, spatial):
    if panel_class == "size_chart":
        return """\
EXPLICIT EDITS — size chart:
[1] SOFA: 4-seat leather → 2-seat fabric MILO (linen-look beige fabric, slim arms, slim cylindrical legs)
[2] DIMS: "300"→"200", "112"→"90", "86"→"85"
[3] SUB-DIMS: 다릿발 12→14cm, 좌방석 깊이 55→52cm, 좌방석 높이 49→45cm
[4] FIRMNESS RED DOTS:
   - 좌방석 bar: position 3 → position 4 (MEDIUM SOFT)
   - 등쿠션 bar: position 3 → position 5 (SOFT)
KEEP: layout, dim-line style, all other Korean text, bar 5-dot structure.
"""
    if panel_class == "structure_chart":
        return """\
EXPLICIT EDITS — structure/material chart:
[1] SOFA in diagram: 4-seat leather → 2-seat fabric MILO
[2] LABELS:
   마감재 → "폴리니크 패브릭 (생활발수, OEKO-TEX 인증)"
   좌방석 → "32kg 고밀도 통스펀지 + 덕페더 67% + 마이크로화이바 33%"
   등쿠션 → "덕페더 67% + 마이크로화이바 33%"
   프레임 → "EO 건조목, S자 스프링, 엘라스틱벨트"
   헤드레스트 항목: REMOVE
KEEP: cross-section layout, region highlighting style, table.
"""
    if panel_class == "color_option":
        return """\
EXPLICIT EDITS — color option panel:
[1] SOFAS: 4-seat leather (그레이/도브그레이/스카이그레이) → 2-seat fabric MILO (오트밀/라이트그레이/더스티로즈)
[2] LABELS:
   "키안티 가죽" → "밀로 패브릭"
   Dimensions → "200 X 90 X 85"
   Color names → "오트밀 / 라이트그레이 / 더스티로즈"
[3] 컬러 톤: 컬러 시트(IMAGE N-1)의 swatches 그대로 — 임의 변형 X.
KEEP: grid layout, equal spacing, swatch positions.
"""
    if panel_class == "module_lineup":
        return """\
EXPLICIT EDITS — module lineup:
[1] 모든 sofa → 2-seat fabric MILO (각각 다른 컬러 — 오트밀/라이트그레이/더스티로즈, 컬러 시트 참조)
[2] LABELS:
   "키안티 N인" → "밀로 2인용"
   Dimensions → "200 X 90 X 85" 통일
KEEP: side-by-side layout, equal spacing.
"""
    if panel_class == "detail_close_up":
        return f"""\
EXPLICIT EDITS — close-up detail:
[1] SOFA SURFACE: leather (광택) → fabric (matte linen-look, light beige)
[2] ARMS: thick padded leather → thin slim straight fabric
[3] LEGS: V-shape chrome → slim cylindrical matte-black (정확히 5개: 모서리 4 + 중앙 1)
[4] CUSHIONS: tailored tight → loose puffy
[5] SEAMS: 좌방석 topstitch + 등쿠션 flange(겉시접) — 두 시접 봉제 차이 정확히
[6] REMOVE: USB/control, headrest, recliner (milo엔 없음)
디테일은 IMAGE 5(디테일 시트, 있다면) 참조.
KEEP: camera angle, framing/crop, lighting direction, background, shadow.
Spatial: {spatial[:200]}
"""
    if panel_class == "lifestyle_scene":
        return """\
EXPLICIT EDITS — lifestyle scene:
[1] SOFA: 4-seat leather (V자, headrest) → 2-seat fabric MILO (slim, NO headrest)
[2] SCALE: smaller (2-seat) — natural scale 유지.
KEEP: 룸/벽/바닥/coffee table/조명/소품, 카메라 각도, 무드, 컬러 톤.
"""
    if panel_class in ("intro_hero", "product_shot"):
        return """\
EXPLICIT EDITS — hero/product shot:
[1] SOFA 전체 교체: 4-seat leather → 2-seat fabric MILO
   Body: leather sheen → matte linen 라이트 베이지
   Arms: thick padded → thin slim straight
   Legs: V-shape chrome → slim cylindrical matte-black (5개)
   Cushions: tailored → loose puffy
   Frame: 4-seat → 2-seat
   Headrest: REMOVE
KEEP: 화이트 seamless 배경, eye-level 카메라, soft 조명, centered framing, subtle floor shadow.
"""
    if panel_class == "material_swatch":
        return """\
EXPLICIT EDITS — material swatch:
[1] TEXTURE: leather → matte linen-look fabric (light beige 멜란지)
[2] LABELS: 가죽 → "폴리니크 패브릭, 생활발수, OEKO-TEX"
KEEP: close-up framing, weave-showing lighting.
"""
    return """\
EXPLICIT EDITS:
[1] SOFA: leather variant → 2-seat fabric MILO (TARGET 참조)
KEEP: layout, composition, lighting, all non-sofa elements.
"""


def qa(panel_orig, swap_result, panel_idx, panel_class):
    is_chart = panel_class in ("size_chart", "structure_chart", "color_option", "module_lineup")
    extra = ""
    if is_chart:
        extra = """\
5) chart_layout_preserved (1-5)
6) text_readable_korean (1-5)
7) numbers_correct (1-5): 수치 정확? (size: 200/90/85, 52/45/14 / firmness 빨간점 위치)
"""

    qa_prompt = (
        f"한국어 엄격 QA (gpt-5). Panel {panel_idx} class={panel_class}.\n"
        "타겟: 밀로 2인 패브릭소파. 원본 C: 한샘 가죽.\n"
        "이미지: A=milo ref, B=swap 결과, C=한샘 원본.\n\n"
        "5점 만점:\n"
        "1) arm_thinness: thin slim?\n"
        "2) cushion_loose: loose puffy?\n"
        "3) fabric_matte: matte linen?\n"
        "4) leg_slim_cylinder: slim cylindrical?\n"
        f"{extra}"
        "JSON: {\"scores\":{...}, \"product_score\":0-100, \"composition_score\":0-100, \"seat_count_in_B\":int, "
        "\"underswap\":bool, \"text_in_image_garbled\":bool, "
        "\"specific_failures\":[한국어], "
        "\"reference_influences\":[{\"element_ko\":,\"source\":\"C\",\"correction_ko\":}], "
        "\"notes\":\"한국어\", \"verdict\":\"pass\"|\"retry\"} — pass: 모든 score>=4 AND not underswap AND not text_garbled."
    )
    resp = openai_client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": qa_prompt},
            {"type": "text", "text": "IMAGE A:"},
            {"type": "image_url", "image_url": {"url": data_uri(MAIN_VIEWS[0])}},
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


def build_refs(panel_class, urls, base_url):
    """단일 통합 마스터 시트 패턴 — 총 5슬롯.
    [1] panel C base (한샘 원본)
    [2,3,4] 메인 대표 3장 (p08_frame_01, 02, 03)
    [5] 통합 마스터 시트 (디테일+컬러+소재+PRESERVE/NEVER 모두)
    """
    refs = [base_url] + list(urls["main"])
    if urls.get("sheet_master"):
        refs.append(urls["sheet_master"])
    return refs


async def generate(prompt, ref_urls, image_size):
    args = {"prompt": prompt, "image_urls": ref_urls, "quality": "high",
            "image_size": image_size, "output_format": "png"}
    result = await fal_client.subscribe_async(ENDPOINT, arguments=args)
    imgs = result.get("images") or result.get("image")
    if isinstance(imgs, list) and imgs:
        f = imgs[0]
        return f["url"] if isinstance(f, dict) else f
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
            ref_urls = build_refs(panel_class, urls, base_url)

            print(f"{tag} cls={panel_class} size={image_size} refs={len(ref_urls)} attempt={attempt_n}", flush=True)
            img = OUT_DIR / f"{label}__a{attempt_n}_v10.png"
            try:
                gurl = await generate(prompt, ref_urls, image_size)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"{tag} GEN ERR: {e}")
                attempts.append({"attempt": attempt_n, "error": str(e), "prompt": prompt,
                                 "ref_count": len(ref_urls)})
                continue

            try:
                verdict = await asyncio.to_thread(qa, base_img, img, panel_idx, panel_class)
            except Exception as e:
                print(f"{tag} QA ERR: {e}")
                attempts.append({"attempt": attempt_n, "image": img.name, "error": f"QA: {e}",
                                 "prompt": prompt, "ref_count": len(ref_urls)})
                break

            t_end = time.time()
            attempts.append({
                "attempt": attempt_n, "image": img.name,
                "gen_seconds": round(t_gen - t0, 1), "qa_seconds": round(t_end - t_gen, 1),
                "fal_url": gurl, "image_size": image_size, "prompt": prompt,
                "ref_count": len(ref_urls), "strategy": "v10_multi_tier", **verdict,
            })
            prev_qa = verdict
            scores = verdict.get("scores", {})
            min_score = min(scores.values()) if scores else 0
            print(f"{tag} prod={verdict.get('product_score','?')} comp={verdict.get('composition_score','?')} "
                  f"min={min_score} -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (passers[0] if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))
    return {"label": label, "panel_idx": panel_idx, "panel_class": panel_class,
            "image_size": image_size, "attempts": attempts, "final": final,
            "passed": bool(passers), "strategies_used": ["v10_multi_tier"]}


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

    print("=== swap v10 — multi-tier ref sheets ===")
    print(f"  endpoint: {ENDPOINT} · vision: {VISION_MODEL}")
    print(f"  product_input: v3 (dense)" if IS_V3 else "  product_input: v1/v2")
    print(f"  targets: {len(targets)}")
    print(f"  ref pattern (5-slot):")
    print(f"    [1] panel C base")
    print(f"    [2,3,4] main views: {len(MAIN_VIEWS)} (p08_frame_01,02,03)")
    print(f"    [5] master sheet: {'✓' if SHEET_MASTER.exists() else '✗ — 먼저 python 67_make_master_sheet.py 실행'}\n")

    print("uploading refs...")
    main_urls = await asyncio.gather(*[upload(p) for p in MAIN_VIEWS])
    sheet_master_url = await upload(SHEET_MASTER) if SHEET_MASTER.exists() else None
    base_urls = {}
    for tg in targets:
        base_urls[f"base_{tg['label']}"] = await upload(tg["path"])
    urls = {**base_urls, "main": list(main_urls), "sheet_master": sheet_master_url}

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
    summary = {"run": RUN_DIR.name, "endpoint": ENDPOINT, "vision_qa": VISION_MODEL,
               "product_input_schema": "v3" if IS_V3 else "v1",
               "wall_seconds": wall, "cells": cells}
    (RUN_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_ROOT / "latest_v10.txt").write_text(RUN_DIR.name)

    passers = sum(1 for c in cells if c["passed"])
    print(f"\n=== DONE === {RUN_DIR}")
    print(f"  wall: {wall}s · passers: {passers}/{len(cells)}")
    for c in cells:
        v = c.get("final") or {}
        scores = v.get("scores", {})
        print(f"    {c['label']:12} [{c['panel_class']:>17}] prod={v.get('product_score','?'):>3} "
              f"min={min(scores.values()) if scores else 0} pass={c['passed']}")


if __name__ == "__main__":
    asyncio.run(main())

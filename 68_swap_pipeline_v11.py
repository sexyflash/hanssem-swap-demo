"""Swap pipeline v11 — v10 + 모든 사용자 지적 fix.

변경 (v10 → v11):
- vision QA: gpt-5 → gpt-5.5 (사용자 요청)
- pass threshold: all_scores>=4 → all_scores>=5 AND product_score>=99 (99+ 강화)
- 다리 4개 (모서리 4, 중앙 1번째 다리 X) — hallucination fix
- module_lineup 가변: model_options 수만큼 milo variants 표시 (4인→2인용/3인용 두 개)
- master sheet: 5-slot ref pattern 유지

ref pattern (v10과 동일):
  [1] panel C base
  [2,3,4] main views (p08_frame_01, 02, 03)
  [5] master sheet v2 (다리 4개 + 입체적 구성)
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

PI_V3 = USER_DIR / "product_input_v3.json"
PRODUCT_INPUT = json.loads(PI_V3.read_text())

OUT_ROOT = TPL_DIR / "swap_results"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = OUT_ROOT / f"v11_{ts}"
RUN_DIR.mkdir()
OUT_DIR = RUN_DIR / "gpt_image"
OUT_DIR.mkdir()

ENDPOINT = "fal-ai/gpt-image-2/edit"
VISION_MODEL = "gpt-5.5"  # 사용자 요청 — 더 엄격
CONCURRENCY = 13  # 13 panel 동시 호출 가능 (1 batch ≈ 120s)
MAX_ATTEMPTS = 3  # 99+ 강화 → retry 2회

USE_PROD = USER_DIR / "use_product"
PREP_DIR = USER_DIR / "preprocessed"

MAIN_VIEWS = [USE_PROD / "p08_frame_01.jpg", USE_PROD / "p08_frame_02.jpg", USE_PROD / "p08_frame_03.jpg"]
SHEET_MASTER = PREP_DIR / "milo_master_sheet.png"

# milo 모델 옵션 (가변 라인업)
MODEL_OPTIONS = PRODUCT_INPUT.get("model_options", [])
COLOR_OPTIONS = [c["name"] for c in PRODUCT_INPUT.get("color_options_detail", []) or []]
N_MODELS = len(MODEL_OPTIONS) or 2  # default 2


def target_summary():
    sp = PRODUCT_INPUT.get("spec", {})
    fd = PRODUCT_INPUT.get("feature_descriptions", {})
    models_list = ", ".join(f"{m.get('name','')} {m.get('dimensions','')}" for m in MODEL_OPTIONS)
    return (
        "TARGET: 밀로 패브릭소파 2인용.\n"
        f"  · 제원 — 가로 {sp.get('width_cm',200)} × 깊이 {sp.get('depth_cm',90)} × 높이 {sp.get('height_cm',85)}cm.\n"
        f"  · 다리 (정확): {fd.get('legs_detail','')[:220]}\n"
        f"  · 팔걸이: {fd.get('arms_detail','')[:160]}\n"
        f"  · 좌방석: {fd.get('seat_cushions_detail','')[:160]}\n"
        f"  · 등쿠션: {fd.get('back_cushions_detail','')[:160]}\n"
        f"  · 시접: {fd.get('seam_styles','')[:180]}\n"
        f"  · 패브릭: {fd.get('fabric_texture','')[:160]}\n"
        f"  · 모델 옵션 ({N_MODELS}개): {models_list}\n"
        "  · 가죽 X · V자 두꺼운 padded 팔걸이 X · 헤드레스트 X · USB X.\n"
        "  · 다리는 반드시 4개 (모서리 4, 중앙 5번째 다리 없음)."
    )


def build_edit_block(panel_class, spatial):
    if panel_class == "size_chart":
        return """\
EXPLICIT EDITS — size chart:
[1] SOFA: 4-seat leather → 2-seat fabric MILO (linen-look beige fabric, slim arms, 다리 4개)
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
[1] SOFA: 4-seat leather → 2-seat fabric MILO (다리 4개)
[2] LABELS:
   마감재 → "폴리니크 패브릭 (생활발수, OEKO-TEX 인증)"
   좌방석 → "32kg 고밀도 통스펀지 + 덕페더 67% + 마이크로화이바 33%"
   등쿠션 → "덕페더 67% + 마이크로화이바 33%"
   프레임 → "EO 건조목, S자 스프링, 엘라스틱벨트"
   헤드레스트 항목: REMOVE
KEEP: cross-section layout, region highlighting, table.
"""
    if panel_class == "color_option":
        colors_str = " / ".join(COLOR_OPTIONS) if COLOR_OPTIONS else "오트밀 / 라이트그레이 / 더스티로즈"
        return f"""\
EXPLICIT EDITS — color option panel:
[1] SOFAS: 4-seat leather (그레이/도브그레이/스카이그레이) → 2-seat fabric MILO ({colors_str})
[2] LABELS:
   "키안티 가죽" → "밀로 패브릭"
   Dimensions → "200 X 90 X 85"
   Color names → "{colors_str}"
[3] 컬러 톤: 마스터 시트의 swatches 그대로 — 임의 변형 X.
[4] 다리: 4개 (모서리), 중앙 5번째 다리 없음.
KEEP: grid layout, equal spacing, swatch positions.
"""
    if panel_class == "module_lineup":
        models_str = " / ".join(f"{m.get('name','')} {m.get('dimensions','')}" for m in MODEL_OPTIONS)
        model_names = ", ".join(m.get('name','') for m in MODEL_OPTIONS)
        return f"""\
EXPLICIT EDITS — module lineup (밀로 모델 {N_MODELS}개 라인업):
[1] 모든 sofa 칸을 milo로 교체. 한샘 원본에 N개 sofa 칸이 있더라도,
    milo 모델은 정확히 {N_MODELS}개 ({model_names}) 만 표시:
    {models_str}
[2] 빈 칸 처리: 원본보다 milo 모델이 적으면, 남는 칸은 그리지 말고
    레이아웃을 {N_MODELS} 칸으로 재배치 (균등 spacing). 한샘 원본 N칸을
    그대로 두고 milo 부족 칸을 비워두지 마라.
[3] LABELS — 좌·우 헤더 동일하게 통일:
   상단 헤더: "밀로 패브릭소파 라인업" (한 줄, 좌우 동일)
   각 모델 라벨 아래: "{models_str}" 처럼 모델명 + 사이즈
[4] 다리: 4개 (모서리), 중앙 다리 없음. 컬러: 마스터 시트 swatch 그대로.
KEEP: side-by-side layout 형식만, 칸 수는 가변. 색상은 마스터 시트.
"""
    if panel_class == "detail_close_up":
        return f"""\
EXPLICIT EDITS — close-up detail:
[1] SOFA SURFACE: leather (광택) → fabric (matte linen-look, light beige)
[2] ARMS: thick padded leather → thin slim straight fabric
[3] LEGS: V-shape chrome → slim 매트블랙 다리 4개 (모서리 4개, 중앙 다리 없음)
[4] CUSHIONS: tailored tight → loose puffy
[5] SEAMS: 좌방석 topstitch + 등쿠션 flange(겉시접) 봉제 차이 정확히
[6] REMOVE: USB/control, headrest, recliner mechanism, brand metal plate
   (한샘 원본의 측면 배지/금속 플레이트 잔존 절대 X)
KEEP: camera angle, framing/crop, lighting direction, background, shadow.
Spatial: {spatial[:200]}
"""
    if panel_class == "lifestyle_scene":
        return """\
EXPLICIT EDITS — lifestyle scene:
[1] SOFA: 4-seat leather (V자 다리, headrest) → 2-seat fabric MILO (slim, NO headrest, 다리 4개)
[2] SCALE: smaller (2-seat) — natural scale 유지.
KEEP: 룸/벽/바닥/coffee table/조명/소품, 카메라 각도, 무드, 컬러 톤.
"""
    if panel_class in ("intro_hero", "product_shot"):
        return """\
EXPLICIT EDITS — hero/product shot:
[1] SOFA 전체 교체: 4-seat leather → 2-seat fabric MILO
   Body: leather sheen → matte linen 라이트 베이지
   Arms: thick padded → thin slim straight
   Legs: V-shape chrome → 매트블랙 다리 4개 (모서리 4, 중앙 다리 없음)
   Cushions: tailored → loose puffy
   Frame: 4-seat → 2-seat
   Headrest: REMOVE
KEEP: 화이트 seamless 배경, eye-level 카메라, soft 조명, centered framing.
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
[1] SOFA: leather variant → 2-seat fabric MILO (다리 4개)
KEEP: layout, composition, lighting, all non-sofa elements.
"""


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
  IMAGE 1 = panel C (한샘 원본 panel — edit base, layout 유지)
  IMAGE 2,3,4 = MILO 메인 대표 (정면/측면/3-4 각도)
  IMAGE 5 = MILO MASTER SHEET (디테일+컬러+소재+PRESERVE/NEVER 통합)

{target_summary()}

=== [SPATIAL LAYOUT TO PRESERVE] ===
{spatial}

Elements:
{elements_str or '  (none)'}

=== [EDIT INSTRUCTIONS] ===
{edit_block}

{feedback}

=== [ABSOLUTE RULES — 점수 99+ 통과 기준] ===
- 결과는 한국 가구 상세페이지 panel — 원본과 같은 visual style.
- 모든 한글 텍스트 깨짐 X.
- 다리는 정확히 4개 (모서리 4개, 중앙 5번째 다리 절대 X) — hallucination 금지.
- 한샘 원본 가죽-특정 잔존 요소 (배지/플레이트/리클라이너 하드웨어/V자 다리) 제거.
- 마스터 시트 PRESERVE 항목 모두 반영, NEVER 항목 절대 violate X.
- 좌석수 정확히 2.
- 모듈 라인업이면 milo 모델 옵션 갯수만큼 정확히 ({N_MODELS}개).
"""


def qa(panel_orig, swap_result, panel_idx, panel_class):
    is_chart = panel_class in ("size_chart", "structure_chart", "color_option", "module_lineup")
    extra = ""
    if is_chart:
        extra = """\
5) chart_layout_preserved (1-5)
6) text_readable_korean (1-5)
7) numbers_correct (1-5)
"""
    if panel_class == "module_lineup":
        extra += f"8) lineup_count_correct (1-5): 라인업 sofa 개수가 정확히 {N_MODELS}개인가?\n"

    qa_prompt = (
        f"한국어 엄격 QA. Panel {panel_idx} class={panel_class}.\n"
        "타겟: 밀로 2인 패브릭소파. 원본 C: 한샘 가죽.\n"
        "이미지: A=milo ref, B=swap 결과, C=한샘 원본.\n\n"
        "**다리는 반드시 4개 — 5개면 hallucination, 즉시 retry**.\n\n"
        "5점 만점:\n"
        "1) arm_thinness: thin slim?\n"
        "2) cushion_loose: loose puffy?\n"
        "3) fabric_matte: matte linen?\n"
        "4) leg_count_4: 다리 정확히 4개? (5개면 score 1)\n"
        f"{extra}"
        "JSON: {\"scores\":{...}, \"product_score\":0-100, \"composition_score\":0-100, \"seat_count_in_B\":int, "
        "\"leg_count_in_B\":int, "
        "\"underswap\":bool, \"text_in_image_garbled\":bool, "
        "\"specific_failures\":[한국어], "
        "\"reference_influences\":[{\"element_ko\":,\"source\":\"C\",\"correction_ko\":}], "
        "\"notes\":\"한국어\", \"verdict\":\"pass\"|\"retry\"}\n\n"
        "**pass 기준 (99+ 강화)**: ALL scores >= 5 "
        "AND product_score >= 99 "
        "AND leg_count_in_B == 4 "
        "AND NOT underswap "
        "AND NOT text_in_image_garbled."
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
    result = json.loads(resp.choices[0].message.content)
    # 추가 강화 — 다리 5개 면 강제 retry
    if result.get("leg_count_in_B") == 5:
        result["verdict"] = "retry"
        result.setdefault("specific_failures", []).insert(0, "다리가 5개 (정답 4개) — hallucination")
    if result.get("product_score", 0) < 99:
        result["verdict"] = "retry"
    return result


def image_size_for(w, h):
    r = w / h
    if r < 0.8:
        return "portrait_4_3"
    if r > 1.2:
        return "landscape_4_3"
    return "square"


def build_refs(panel_class, urls, base_url):
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
            img = OUT_DIR / f"{label}__a{attempt_n}_v11.png"
            try:
                gurl = await generate(prompt, ref_urls, image_size)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"{tag} GEN ERR: {str(e)[:200]}")
                attempts.append({"attempt": attempt_n, "error": str(e)[:300], "prompt": prompt,
                                 "ref_count": len(ref_urls)})
                continue

            try:
                verdict = await asyncio.to_thread(qa, base_img, img, panel_idx, panel_class)
            except Exception as e:
                print(f"{tag} QA ERR: {str(e)[:200]}")
                attempts.append({"attempt": attempt_n, "image": img.name, "error": f"QA: {str(e)[:200]}",
                                 "prompt": prompt, "ref_count": len(ref_urls)})
                break

            t_end = time.time()
            attempts.append({
                "attempt": attempt_n, "image": img.name,
                "gen_seconds": round(t_gen - t0, 1), "qa_seconds": round(t_end - t_gen, 1),
                "fal_url": gurl, "image_size": image_size, "prompt": prompt,
                "ref_count": len(ref_urls), "strategy": "v11_strict99", **verdict,
            })
            prev_qa = verdict
            scores = verdict.get("scores", {})
            min_score = min(scores.values()) if scores else 0
            print(f"{tag} prod={verdict.get('product_score','?')} comp={verdict.get('composition_score','?')} "
                  f"min={min_score} legs={verdict.get('leg_count_in_B','?')} -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (passers[0] if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))
    return {"label": label, "panel_idx": panel_idx, "panel_class": panel_class,
            "image_size": image_size, "attempts": attempts, "final": final,
            "passed": bool(passers), "strategies_used": ["v11_strict99"]}


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

    print("=== swap v11 — strict99 + 다리 4개 + 가변 라인업 ===")
    print(f"  endpoint: {ENDPOINT} · vision: {VISION_MODEL}")
    print(f"  pass threshold: prod>=99 AND all_scores>=5 AND legs==4")
    print(f"  model_options: {N_MODELS}개 → {[m.get('name','') for m in MODEL_OPTIONS]}")
    print(f"  master sheet: {'✓' if SHEET_MASTER.exists() else '✗'}")
    print(f"  targets: {len(targets)}\n")

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
               "pass_threshold": "prod>=99 AND all_scores>=5 AND legs==4",
               "model_options_count": N_MODELS,
               "wall_seconds": wall, "cells": cells}
    (RUN_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_ROOT / "latest_v11.txt").write_text(RUN_DIR.name)

    passers = sum(1 for c in cells if c["passed"])
    print(f"\n=== DONE === {RUN_DIR}")
    print(f"  wall: {wall}s · passers: {passers}/{len(cells)}")
    for c in cells:
        v = c.get("final") or {}
        scores = v.get("scores", {})
        print(f"    {c['label']:12} [{c['panel_class']:>17}] prod={v.get('product_score','?'):>3} "
              f"min={min(scores.values()) if scores else 0} legs={v.get('leg_count_in_B','?')} pass={c['passed']}")


if __name__ == "__main__":
    asyncio.run(main())

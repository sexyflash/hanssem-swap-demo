"""Swap pipeline v13 — panel별 ref mapping + master sheet v3 + QA grid 검증.

사용자 지적 반영:
1. "panel별로 필요한 ref만 보내라" → panel_ref_mapping.json 로드, panel-specific refs
2. "마스터 시트는 메타 자료 — 출력에 복제 X" → master sheet v3 (DO NOT REPLICATE 워터마크)
3. "그리드 출력 검증 필요" → QA에 image_format detection 강화

ref pattern (panel별 가변, 2~6 slot):
  [1] panel C base (한샘 원본 panel)
  [2~N] panel_ref_mapping.json 의 ref_paths (panel별 1~5 장)
  [N+1] master sheet v3 (REFERENCE METADATA)

이렇게 일률적 5장 → panel별 가변 (2~6장).
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
REF_MAP = json.loads((TPL_DIR / "panel_ref_mapping.json").read_text())
PROD_INPUT = json.loads((USER_DIR / "product_input_v3.json").read_text())

OUT_ROOT = TPL_DIR / "swap_results"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = OUT_ROOT / f"v13_{ts}"
RUN_DIR.mkdir()
OUT_DIR = RUN_DIR / "gpt_image"
OUT_DIR.mkdir()

ENDPOINT = "fal-ai/gpt-image-2/edit"
VISION_MODEL = "gpt-5.5"
CONCURRENCY = 13
MAX_ATTEMPTS = 3

PREP_DIR = USER_DIR / "preprocessed"
SHEET_MASTER = PREP_DIR / "milo_master_sheet.png"

MODEL_OPTIONS = PROD_INPUT.get("model_options", [])
COLOR_OPTIONS = [c["name"] for c in PROD_INPUT.get("color_options_detail", []) or []]
N_MODELS = len(MODEL_OPTIONS) or 2

MAIN_FRONT = USER_DIR / "use_product/p08_frame_01.jpg"  # QA용 reference


def target_summary():
    sp = PROD_INPUT.get("spec", {})
    fd = PROD_INPUT.get("feature_descriptions", {})
    models_list = ", ".join(f"{m.get('name','')} {m.get('dimensions','')}" for m in MODEL_OPTIONS)
    return (
        "TARGET: 밀로 패브릭소파 2인용.\n"
        f"  · 제원 — {sp.get('width_cm',200)}×{sp.get('depth_cm',90)}×{sp.get('height_cm',85)}cm.\n"
        f"  · 다리: {fd.get('legs_detail','')[:220]}\n"
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
[1] SOFA: 4-seat leather → 2-seat fabric MILO
[2] DIMS: "300"→"200", "112"→"90", "86"→"85"
[3] SUB-DIMS: 다릿발 12→14cm, 좌방석 깊이 55→52cm, 좌방석 높이 49→45cm
[4] FIRMNESS RED DOTS: 좌방석 pos3→pos4(MEDIUM SOFT), 등쿠션 pos3→pos5(SOFT)
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
[1] SOFAS: 4-seat leather (한샘 컬러) → 2-seat fabric MILO ({colors_str})
[2] LABELS:
   "키안티 가죽" → "밀로 패브릭"
   "그레이/도브그레이/스카이그레이" → "{colors_str}" (한샘 컬러명 잔존 X)
   Dimensions → "200 X 90 X 85"
[3] 다리: 4개 (모서리), 중앙 다리 X.
KEEP: grid layout, equal spacing.
"""
    if panel_class == "module_lineup":
        models_str = " / ".join(f"{m.get('name','')} {m.get('dimensions','')}" for m in MODEL_OPTIONS)
        model_names = ", ".join(m.get('name','') for m in MODEL_OPTIONS)
        return f"""\
EXPLICIT EDITS — module lineup (밀로 {N_MODELS}개 모델):
[1] SOFAS: 정확히 {N_MODELS}개 ({model_names}). 한샘 원본이 N개여도 milo는 {N_MODELS}개만 표시.
    {models_str}
[2] 부족한 칸은 비우지 말고 {N_MODELS} 칸으로 레이아웃 재배치.
[3] LABELS:
   상단 헤더: "밀로 패브릭소파 라인업"
   각 모델: 모델명 + 사이즈
   한샘 컬러명 ("그레이/도브그레이/스카이그레이") 잔존 X → milo 컬러명 사용.
[4] 다리: 4개 (모서리, 중앙 X).
"""
    if panel_class == "detail_close_up":
        return f"""\
EXPLICIT EDITS — close-up detail:
[1] SOFA SURFACE: leather (광택) → fabric (matte linen-look, light beige)
[2] ARMS: thick padded leather → thin slim straight fabric
[3] LEGS (만약 frame 안에 보인다면): 매트블랙 슬림 4개 (모서리, 중앙 X).
    Close-up이라 frame 밖이면 그대로 OK.
[4] CUSHIONS: tailored tight → loose puffy
[5] SEAMS: 좌방석 topstitch + 등쿠션 flange(겉시접)
[6] REMOVE: USB/control, headrest, recliner mechanism, brand metal plate
KEEP: camera angle, framing/crop, lighting, background.
Spatial: {spatial[:200]}
"""
    if panel_class == "lifestyle_scene":
        return """\
EXPLICIT EDITS — lifestyle scene:
[1] SOFA: 4-seat leather → 2-seat fabric MILO (slim, NO headrest, 다리 4개)
[2] SCALE: smaller (2-seat).
KEEP: 룸/벽/바닥/coffee table/조명/소품, 카메라 각도, 무드.
"""
    if panel_class in ("intro_hero", "product_shot"):
        return """\
EXPLICIT EDITS — hero/product shot:
[1] SOFA 전체 교체: 4-seat leather → 2-seat fabric MILO
   Body/Arms/Legs(4개)/Cushions/Frame 모두 milo로
   Headrest: REMOVE
KEEP: 화이트 배경, eye-level 카메라, soft 조명, centered framing.
"""
    if panel_class == "material_swatch":
        return """\
EXPLICIT EDITS — material swatch:
[1] TEXTURE: leather → matte linen-look (light beige 멜란지)
[2] LABELS: 가죽 → "폴리니크 패브릭, 생활발수, OEKO-TEX"
"""
    return """\
EXPLICIT EDITS:
[1] SOFA: leather → 2-seat fabric MILO (다리 4개)
KEEP: layout, composition, lighting.
"""


def build_explicit_prompt(panel_idx, layout_map, attempt_n, ref_keys, has_master, prev_qa=None):
    panel_class = layout_map.get("panel_class", "other")
    spatial = layout_map.get("spatial_layout", "")
    elements = layout_map.get("elements", []) or []
    elements_str = "\n".join(f"  - {e.get('role','?')} @ {e.get('position','?')}: {e.get('description','')}" for e in elements)

    edit_block = build_edit_block(panel_class, spatial)

    # ref slot 설명 (panel별 가변)
    slots = ["IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)"]
    for i, key in enumerate(ref_keys, start=2):
        slots.append(f"IMAGE {i} = MILO {key}")
    if has_master:
        slots.append(f"IMAGE {len(ref_keys)+2} = MILO PRODUCT GUIDE SHEET (메타 자료, **출력에 복제 X**)")
    slots_block = "\n  ".join(slots)

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
  {slots_block}

**IMAGE {len(ref_keys)+2} (PRODUCT GUIDE SHEET)는 운영팀이 정리한 메타 자료입니다.**
**이 시트는 PRESERVE/NEVER 규칙과 디테일 reference 정보를 보여줄 뿐,**
**시트 자체의 multi-cell grid layout을 결과로 출력하지 마세요.**
**결과 이미지는 IMAGE 1 (panel C)와 같은 single panel layout이어야 합니다.**

{target_summary()}

=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 single-panel layout. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
{spatial}

Elements:
{elements_str or '  (none)'}

=== [EDIT INSTRUCTIONS] ===
{edit_block}

{feedback}

=== [ABSOLUTE RULES] ===
- 결과는 panel C 형태 single panel. 한국 가구 detail page 스타일.
- 한글 텍스트 깨짐 X.
- 다리 (frame 안에 보일 때) 정확히 4개. 5번째 중앙 다리 X.
- 한샘 잔존 (배지/플레이트/리클라이너/V자 다리/한샘 컬러명) 제거.
- PRODUCT GUIDE SHEET (만약 첨부됨)의 PRESERVE 반영, NEVER violate X,
  하지만 시트의 grid layout 자체는 결과로 복제 X.
- 좌석수 2.
"""


def qa(panel_orig, swap_result, panel_idx, panel_class):
    is_chart = panel_class in ("size_chart", "structure_chart", "color_option", "module_lineup")
    is_close_up = panel_class == "detail_close_up"
    extra = ""
    if is_chart:
        extra += "5) chart_layout_preserved (1-5)\n6) text_readable_korean (1-5)\n7) numbers_correct (1-5)\n"
    if panel_class == "module_lineup":
        extra += f"8) lineup_count_correct (1-5): 라인업 수 정확히 {N_MODELS}?\n"

    # close-up은 다리 카운트 conditional
    leg_check = ("4) leg_count_when_visible (1-5): "
                 + ("frame에 다리가 보이는 경우만 4개여야 함, 안 보이면 score 5\n"
                    if is_close_up else
                    "다리 정확히 4개 (5개면 score 1)\n"))

    qa_prompt = (
        f"한국어 엄격 QA. Panel {panel_idx} class={panel_class}.\n"
        "타겟: 밀로 2인 패브릭소파. 원본 C: 한샘 가죽.\n"
        "이미지: A=milo ref, B=swap 결과, C=한샘 원본.\n\n"
        "**critical 검증**:\n"
        "1) B의 image_format 분류:\n"
        "   - 'single_product' / 'lifestyle' / 'chart_diagram' / 'multi_panel_grid'\n"
        "   - **multi_panel_grid = master sheet copy fail → 즉시 retry**\n"
        "2) B와 C의 layout 일치 (B가 C와 같은 single panel 형태인가)\n"
        "3) 다리 — close-up이면 frame 밖 가능. 정면샷이면 4개.\n"
        "4) 한샘 잔존 (배지/V자/한샘 컬러명)\n\n"
        "5점 만점:\n"
        "1) arm_thinness\n"
        "2) cushion_loose\n"
        "3) fabric_matte\n"
        f"{leg_check}"
        "5) layout_match_C (B vs C single-panel 일치)\n"
        f"{extra}"
        "JSON: {\"image_format\":..., \"scores\":{...}, \"product_score\":0-100, "
        "\"composition_score\":0-100, \"seat_count_in_B\":int, \"leg_count_in_B\":int, "
        "\"leg_visible_in_frame\":bool, "
        "\"underswap\":bool, \"text_in_image_garbled\":bool, \"hanssem_text_residue\":bool, "
        "\"specific_failures\":[한국어], "
        "\"reference_influences\":[{\"element_ko\":,\"source\":\"C\",\"correction_ko\":}], "
        "\"notes\":\"한국어\", \"verdict\":\"pass\"|\"retry\"}\n\n"
        "**pass 기준 v13**:\n"
        " - image_format != 'multi_panel_grid'\n"
        " - layout_match_C >= 5\n"
        " - ALL scores >= 5\n"
        " - product_score >= 99\n"
        " - leg_visible_in_frame면 leg_count_in_B == 4 (안 보이면 무관)\n"
        " - NOT underswap, NOT text_garbled, NOT hanssem_text_residue"
    )
    resp = openai_client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": qa_prompt},
            {"type": "text", "text": "IMAGE A:"},
            {"type": "image_url", "image_url": {"url": data_uri(MAIN_FRONT)}},
            {"type": "text", "text": "IMAGE B:"},
            {"type": "image_url", "image_url": {"url": data_uri(swap_result)}},
            {"type": "text", "text": "IMAGE C:"},
            {"type": "image_url", "image_url": {"url": data_uri(panel_orig)}},
        ]}],
        response_format={"type": "json_object"},
    )
    result = json.loads(resp.choices[0].message.content)
    # 강제 retry rules
    if result.get("image_format") == "multi_panel_grid":
        result["verdict"] = "retry"
        result.setdefault("specific_failures", []).insert(0,
            "결과가 master sheet 같은 grid 형태 — single panel로 재생성")
        result["product_score"] = min(result.get("product_score", 0), 40)
    # close-up이 아닌 경우 다리 5개면 hallucination
    if not is_close_up and result.get("leg_count_in_B") == 5:
        result["verdict"] = "retry"
        result.setdefault("specific_failures", []).insert(0, "다리 5개 (정답 4) — hallucination")
    if result.get("hanssem_text_residue"):
        result["verdict"] = "retry"
        result.setdefault("specific_failures", []).insert(0, "한샘 텍스트 잔존")
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


def build_refs(panel_label, urls, base_url):
    """panel별 ref + master sheet."""
    refs = [base_url]
    panel_refs = urls.get(f"panel_refs_{panel_label}", [])
    refs.extend(panel_refs)
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
    panel_refs = urls.get(f"panel_refs_{label}", [])
    ref_keys = urls.get(f"panel_ref_keys_{label}", [])
    has_master = bool(urls.get("sheet_master"))
    attempts = []
    prev_qa = None

    for attempt_n in range(1, MAX_ATTEMPTS + 1):
        tag = f"[{label}/#{attempt_n}]"
        async with sem:
            t0 = time.time()
            prompt = build_explicit_prompt(panel_idx, layout_map, attempt_n, ref_keys, has_master, prev_qa)
            ref_urls = build_refs(label, urls, base_url)

            print(f"{tag} cls={panel_class} refs={len(ref_urls)} (panel:{len(panel_refs)}) attempt={attempt_n}", flush=True)
            img = OUT_DIR / f"{label}__a{attempt_n}_v13.png"
            try:
                gurl = await generate(prompt, ref_urls, image_size)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"{tag} GEN ERR: {str(e)[:200]}")
                attempts.append({"attempt": attempt_n, "error": str(e)[:300], "prompt": prompt, "ref_count": len(ref_urls)})
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
                "ref_count": len(ref_urls), "ref_keys": ref_keys + (["master_sheet"] if has_master else []),
                "strategy": "v13_panel_refs", **verdict,
            })
            prev_qa = verdict
            scores = verdict.get("scores", {})
            min_score = min(scores.values()) if scores else 0
            fmt = verdict.get("image_format", "?")
            print(f"{tag} fmt={fmt} prod={verdict.get('product_score','?')} comp={verdict.get('composition_score','?')} "
                  f"min={min_score} legs={verdict.get('leg_count_in_B','?')}(vis={verdict.get('leg_visible_in_frame','?')}) -> {verdict.get('verdict')}")
            if verdict.get("verdict") == "pass":
                break

    scored = [a for a in attempts if "verdict" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    final = (passers[0] if passers
             else max(scored, key=lambda a: a.get("product_score", 0)) if scored
             else (attempts[-1] if attempts else None))
    return {"label": label, "panel_idx": panel_idx, "panel_class": panel_class,
            "image_size": image_size, "attempts": attempts, "final": final,
            "passed": bool(passers), "strategies_used": ["v13_panel_refs"]}


async def main():
    from PIL import Image

    # panel별 ref 파일 매핑
    panel_refs_files = {}
    for pid, m in REF_MAP["panels"].items():
        # pid = "panel_01.jpg" 또는 "cover"
        base = pid.split(".")[0] if pid != "cover" else "cover"
        panel_refs_files[base] = {
            "paths": [USER_DIR / rp for rp in m["ref_paths"]],
            "keys": m["ref_keys"],
        }

    targets = []
    cover_path = TPL_DIR / "_cover_1000.jpg"
    cover_layout = LAYOUTS.get("cover", {"panel_class": "intro_hero", "spatial_layout": "Cover hero."})
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

    print("=== swap v13 — panel별 ref + master sheet v3 + QA grid 검증 ===")
    print(f"  endpoint: {ENDPOINT} · vision: {VISION_MODEL}")
    print(f"  CONCURRENCY: {CONCURRENCY} · MAX_ATTEMPTS: {MAX_ATTEMPTS}")
    print(f"  master sheet (v3): {'✓' if SHEET_MASTER.exists() else '✗'}")
    print(f"  targets: {len(targets)}")
    print("\n  panel별 ref count:")
    for tg in targets:
        info = panel_refs_files.get(tg["label"])
        cnt = len(info["paths"]) if info else 0
        print(f"    {tg['label']:>12}: {cnt} refs ({', '.join(info['keys']) if info else ''})")

    print("\nuploading refs...")
    # 모든 panel ref 파일 dedupe upload
    all_files = set()
    for info in panel_refs_files.values():
        for p in info["paths"]:
            all_files.add(p)
    all_files_list = sorted(all_files, key=lambda p: str(p))
    upload_urls = await asyncio.gather(*[upload(p) for p in all_files_list])
    file_to_url = dict(zip(all_files_list, upload_urls))
    print(f"  uploaded {len(file_to_url)} unique ref files")

    sheet_master_url = await upload(SHEET_MASTER) if SHEET_MASTER.exists() else None
    base_urls = {}
    for tg in targets:
        base_urls[f"base_{tg['label']}"] = await upload(tg["path"])

    # panel별 ref URL 만들기
    urls = {**base_urls, "sheet_master": sheet_master_url}
    for label, info in panel_refs_files.items():
        urls[f"panel_refs_{label}"] = [file_to_url[p] for p in info["paths"]]
        urls[f"panel_ref_keys_{label}"] = info["keys"]

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
               "pass_threshold": "image_format!=grid AND prod>=99 AND layout_match>=5 AND conditional_legs==4",
               "model_options_count": N_MODELS, "wall_seconds": wall, "cells": cells}
    (RUN_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_ROOT / "latest_v13.txt").write_text(RUN_DIR.name)

    passers = sum(1 for c in cells if c["passed"])
    print(f"\n=== DONE === {RUN_DIR}")
    print(f"  wall: {wall}s · passers: {passers}/{len(cells)}")
    for c in cells:
        v = c.get("final") or {}
        scores = v.get("scores", {})
        print(f"    {c['label']:12} [{c['panel_class']:>17}] fmt={v.get('image_format','?')} "
              f"prod={v.get('product_score','?'):>3} min={min(scores.values()) if scores else 0} "
              f"legs={v.get('leg_count_in_B','?')} pass={c['passed']}")


if __name__ == "__main__":
    asyncio.run(main())

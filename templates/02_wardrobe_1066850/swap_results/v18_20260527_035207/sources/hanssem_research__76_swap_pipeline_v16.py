"""Swap pipeline v16 — 하드코딩 룰 제거 + smart sheet 복원/강화 + 3-stage retry.

사용자 의도 (이번 세션 핵심):
1) 스마트시트 복원 + 강화 — sheet 한 장만 봐도 panel별 제작 가이드 + DO/DON'T가 모두
   들어가게. 단, sheet 자체가 결과 이미지로 복제되면 안 됨 (워터마크/회색 배경).
2) 3-stage retry —
   stage 1: QA를 단순 텍스트 append 하지 말고, LLM이 원인 분석 + 보완책 해설 작성하여
            prompt 재작성.
   stage 2: 앞선 두 시도 중 점수 더 좋은 결과를 base로 painting/edit prompt 생성.
   stage 3: essence + smart sheet 동봉 + 누적 보완책 통합 prompt.
3) 하드코딩 룰 매핑 → LLM 판단 매핑 (panel→ref + build_edit_block 둘 다 LLM 호출).
4) 어떤 템플릿/카테고리에도 generalizable. 소파 전용 if/elif 제거.
5) 버전 자동 increment + 산출물 패키징 (각 run 디렉토리에 사용된 .py + product_input
   + LLM 매핑 결과 + 모든 prompt + QA 리포트 동봉) — 다른 연구 과제로 들고 갈 수 있게.

판단 권한 (사용자 메모리 기준): option/cost/architecture는 묻고, 나머지는 자율 진행.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
import fal_client  # noqa: E402
from lib import data_uri, download, openai_client, upload  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from pipeline_lib import (  # noqa: E402
    best_selector,
    llm_edit_block,
    llm_panel_mapper,
    qa_engine,
    retry_strategist,
    smart_sheet_builder,
    verifiable_checklist,
    version_bundler,
)

# ───────────────────────────── config ─────────────────────────────
# CLI 인자로 override 가능 — default 는 sofa 992474 / milo 777039
DEFAULT_TEMPLATE_DIR = HERE / "templates/01_sofa_992474"
DEFAULT_USER_DIR = HERE / "user_products/milo_777039"
DEFAULT_PRODUCT_INPUT_NAME = "product_input_v3.json"

ENDPOINT = "fal-ai/gpt-image-2/edit"
VISION_MODEL = "gpt-5.5"          # QA + 시각 분석
TEXT_MODEL = "gpt-5"              # LLM mapping / edit_block / retry planner
CONCURRENCY = 13
MAX_ATTEMPTS = 4                  # 1 initial + 3 retries (stages 1/2/3)
MAX_REFS_PER_PANEL = 6

# 동적으로 main()에서 설정
TEMPLATE_DIR: Path = DEFAULT_TEMPLATE_DIR
USER_DIR: Path = DEFAULT_USER_DIR
USE_PROD: Path = DEFAULT_USER_DIR / "use_product"
LAYOUT_FILE: Path = DEFAULT_TEMPLATE_DIR / "panel_layout_maps.json"
CLASSIFICATION_FILE: Path = DEFAULT_USER_DIR / "use_product" / "classification.json"
PRODUCT_INPUT_FILE: Path = DEFAULT_USER_DIR / DEFAULT_PRODUCT_INPUT_NAME
MISMATCH_FILE: Path = DEFAULT_TEMPLATE_DIR / "mismatch_resolution.json"
SWAP_RESULTS_DIR: Path = DEFAULT_TEMPLATE_DIR / "swap_results"


def _set_paths(template_dir: Path, user_dir: Path, product_input_name: str = DEFAULT_PRODUCT_INPUT_NAME):
    """Globals 갱신 — 다른 template/user 로 실행 가능."""
    global TEMPLATE_DIR, USER_DIR, USE_PROD, LAYOUT_FILE, CLASSIFICATION_FILE
    global PRODUCT_INPUT_FILE, MISMATCH_FILE, SWAP_RESULTS_DIR
    TEMPLATE_DIR = template_dir
    USER_DIR = user_dir
    USE_PROD = user_dir / "use_product"
    LAYOUT_FILE = template_dir / "panel_layout_maps.json"
    CLASSIFICATION_FILE = USE_PROD / "classification.json"
    PRODUCT_INPUT_FILE = user_dir / product_input_name
    MISMATCH_FILE = template_dir / "mismatch_resolution.json"
    SWAP_RESULTS_DIR = template_dir / "swap_results"


# ───────────────────────────── helpers ─────────────────────────────
def load_inputs():
    layouts_raw = json.loads(LAYOUT_FILE.read_text())["panels"]
    layouts = {p["panel"]: p for p in layouts_raw}
    classification = json.loads(CLASSIFICATION_FILE.read_text())
    product_input = json.loads(PRODUCT_INPUT_FILE.read_text())
    # mismatch_resolution: panel_idx → verdict info (match/bypass/skip)
    mismatch = {}
    if MISMATCH_FILE.exists():
        for r in json.loads(MISMATCH_FILE.read_text()).get("resolutions", []):
            mismatch[r.get("panel_idx")] = r
    return layouts, classification, product_input, mismatch


def product_essence_text(product_input: dict) -> str:
    pn = product_input.get("product_name", "")
    sp = product_input.get("spec", {})
    fd = product_input.get("feature_descriptions", {})
    mo = product_input.get("model_options", []) or []
    co = product_input.get("color_options_detail", []) or []
    parts = [f"TARGET: {pn}"]
    if sp:
        parts.append(
            f"제원: {sp.get('width_cm','?')}×{sp.get('depth_cm','?')}×{sp.get('height_cm','?')}cm"
            + (f" · seat_depth={sp.get('seat_depth_cm','?')}" if sp.get('seat_depth_cm') else "")
            + (f" · seat_height={sp.get('seat_height_cm','?')}" if sp.get('seat_height_cm') else "")
            + (f" · arm_height={sp.get('arm_height_cm','?')}" if sp.get('arm_height_cm') else "")
            + (f" · leg_height={sp.get('leg_height_cm','?')}" if sp.get('leg_height_cm') else "")
        )
    if mo:
        parts.append("모델 옵션: " + ", ".join(f"{m.get('name','')} {m.get('dimensions','')}" for m in mo))
    if co:
        parts.append("컬러: " + ", ".join(f'"{c.get("name","")}"' for c in co))
    for key, val in fd.items():
        if val:
            parts.append(f"· {key}: {str(val)[:260]}")
    return "\n".join(parts)


def image_size_for(w: int, h: int) -> str:
    """원본 panel 비율에 가장 가까운 fal image_size 매핑.

    fal-ai/gpt-image-2/edit 지원: square / square_hd / landscape_4_3 / landscape_16_9 /
    portrait_4_3 / portrait_16_9
    """
    r = w / h
    # 매우 세로 긴 (옷장 panel, 책상 lifestyle 등)
    if r < 0.65:
        return "portrait_16_9"
    if r < 0.85:
        return "portrait_4_3"
    if r < 1.15:
        return "square"
    if r < 1.55:
        return "landscape_4_3"
    return "landscape_16_9"


# ─────────────────────────── prompt builders ───────────────────────────
def _critical_never_miss_block(applicable_items: list[dict]) -> str:
    """제품 왜곡 방지 핵심 항목 (distortion + forbidden) 을 prompt에 강제 박는다.

    detail 항목은 prompt 부담을 줄이기 위해 짧게.
    """
    distortion = [it for it in (applicable_items or []) if it.get("category") == "distortion"]
    forbidden = [it for it in (applicable_items or []) if it.get("category") == "forbidden"]
    detail = [it for it in (applicable_items or []) if it.get("category") == "detail"]
    # 옛 severity 호환
    if not distortion and not forbidden:
        distortion = [it for it in (applicable_items or []) if it.get("severity") == "critical"]
        detail = [it for it in (applicable_items or []) if it.get("severity") == "important"]
    if not distortion and not forbidden and not detail:
        return ""
    lines = ["=== [★ PRODUCT IDENTITY · 절대 왜곡되면 안 됨] ===",
             "(이 항목들은 QA가 binary 검증. 1개라도 fail이면 retry.)\n"]
    for it in distortion:
        lines.append(f"  ◆ [DISTORTION] {it.get('description_ko','')} (axis={it.get('axis','?')})")
        if it.get("expected"):
            lines.append(f"     → 정답: {it['expected'][:200]}")
    for it in forbidden:
        lines.append(f"  ✗ [FORBIDDEN] {it.get('description_ko','')} — 결과에 보이면 fail")
    if detail:
        lines.append("\n  (참고용 · detail — 시도하되 strict 채점 안 함):")
        for it in detail[:8]:
            lines.append(f"     · {it.get('description_ko','')[:100]} (axis={it.get('axis','?')})")
    return "\n".join(lines) + "\n"


def _category_specific_block(panel_class: str) -> str:
    """카테고리/panel_class 별 특화 가이드 — 사용자 요청: 옷장/책상도 소파처럼 카테고리 강조."""
    if panel_class in ("size_chart", "structure_chart"):
        return (
            "=== [★ CHART panel 특화 — 반드시 보존] ===\n"
            "  - dim_line / 측정 화살표 / 숫자 텍스트 · 한국어 라벨 · 표 셀 구조 100% 보존\n"
            "  - 한샘 텍스트는 사용자 제품 수치로 정확 치환. 누락/이상한 숫자 → fail\n"
            "  - 차트 색/굵기/위치 흔들리지 말 것. layout이 정보의 핵심\n"
        )
    if panel_class == "module_lineup":
        return (
            "=== [★ LINEUP panel 특화] ===\n"
            "  - 사용자 제품 모델 옵션 수 = lineup 칸 수 (한샘 4모듈이라도 사용자 2모듈이면 2칸)\n"
            "  - 각 칸 라벨 = 정확한 제품명 + 사이즈. layout grid 일관성 유지\n"
            "  - 사용자 제품의 라인업이 한샘과 다르면 정확히 사용자 list만 표시\n"
        )
    if panel_class == "color_option":
        return (
            "=== [★ COLOR panel 특화] ===\n"
            "  - 컬러 swatch 위치 · 크기 · 배치 · 라벨 그리드 정확 보존\n"
            "  - 사용자 제품의 정확한 한글 컬러명만 사용. 한샘 컬러명/외부 색명 발명 금지\n"
            "  - swatch 색은 사용자 제품의 실제 톤. 한샘 색조 그대로 가져오지 말 것\n"
        )
    if panel_class == "material_swatch":
        return (
            "=== [★ MATERIAL panel 특화] ===\n"
            "  - 소재 텍스처 라벨/구역 layout 보존. 사용자 제품 소재 표면으로 텍스처만 교체\n"
        )
    if panel_class == "detail_close_up":
        return (
            "=== [★ DETAIL CLOSE-UP 특화] ===\n"
            "  - frame 안에 들어오는 사용자 제품 디테일을 정확히 표현. 추측/발명 금지\n"
            "  - reference 사진에서 보이는 시접/소재/표면 디테일 그대로\n"
        )
    if panel_class == "lifestyle_scene":
        return (
            "=== [★ LIFESTYLE 특화] ===\n"
            "  - 룸 배경/조명/소품/카메라 각도 유지. 사용자 제품으로 자연스럽게 배치\n"
            "  - 한샘 제품 비율과 사용자 제품 비율이 다르면 사용자 제품 비율 우선\n"
        )
    return ""


def assemble_initial_prompt(
    panel: dict,
    edit_block: str,
    ref_keys: list[str],
    product_essence: str,
    applicable_items: list[dict] | None = None,
    sheet_in_refs: bool = False,
) -> str:
    spatial = panel.get("spatial_layout", "") or ""
    elements = panel.get("elements", []) or []
    elements_str = "\n".join(
        f"  - {e.get('role','?')} @ {e.get('position','?')}: {e.get('description','')[:180]}"
        for e in elements
    ) or "  (none)"
    slots = ["IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)"]
    offset = 2
    if sheet_in_refs:
        slots.append(f"IMAGE {offset} = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)")
        offset += 1
    for i, key in enumerate(ref_keys, start=offset):
        slots.append(f"IMAGE {i} = USER PRODUCT — {key}")
    slots_block = "\n  ".join(slots)
    never_miss = _critical_never_miss_block(applicable_items)

    return f"""\
TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  {slots_block}

이번 panel에 필요한 user-product reference만 첨부됨. 외부 정보 가져오지 마세요.

{product_essence}

{never_miss}

{_category_specific_block(panel.get("panel_class", "other"))}

=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
{spatial}

Elements:
{elements_str}

=== [EDIT INSTRUCTIONS — LLM 생성] ===
{edit_block}

=== [ABSOLUTE RULES — PRESERVE / NEVER] ===
PRESERVE:
  - panel C와 같은 single panel layout, 한국 detail page 스타일
  - 카메라 각도/배경/조명/한국어 텍스트 가독성
  - 사용자 제품 feature_descriptions에 명시된 모든 특징
  - 위 [NEVER-MISS] critical 항목은 결과 이미지에 반드시 시각적으로 표현
NEVER:
  - 사용자 제품 정보에 없는 feature 발명 (헤드레스트/리클라이너/USB/추가 다리/tufting 등)
  - 한샘 원본 텍스트 잔존
  - multi-cell grid 출력
  - 한글 텍스트 깨짐
  - NEVER-MISS critical 항목 누락 (이게 panel의 핵심 검증 포인트)
"""


def assemble_paint_edit_prompt(
    panel: dict,
    base_paint_directive: str,
    product_essence: str,
) -> str:
    spatial = panel.get("spatial_layout", "") or ""
    return f"""\
TASK: PAINT EDIT — partial in-painting on the provided base image.

이번 호출은 base 이미지의 잘된 부분을 모두 보존하고, 지정된 영역만 부분 수정한다.
재생성 X.

IMAGE 1 = BASE (앞선 시도 중 점수가 가장 좋은 결과 — preserve wholesale except listed regions)
이후 IMAGE 2~ = user-product reference (필요 부분 보정용)

{product_essence}

=== [SPATIAL LAYOUT — KEEP from BASE] ===
{spatial}

=== [PAINT EDIT DIRECTIVE — LLM 생성] ===
{base_paint_directive}

=== [ABSOLUTE RULES] ===
- 카메라 각도/배경/조명/레이아웃은 BASE 그대로
- 한국어 텍스트는 정확/또렷
- 새 요소 발명 금지 (사용자 제품 정보 외)
- 단일 panel 출력
"""


def assemble_cumulative_prompt(
    panel: dict,
    final_directive: str,
    product_essence: str,
    sheet_summary: str,
) -> str:
    spatial = panel.get("spatial_layout", "") or ""
    return f"""\
TASK: FINAL ATTEMPT — essence + SMART SHEET + cumulative patches.

★ 핵심: 제품의 비전(핵심 시각적 특징)이 결과 이미지에 정말로 들어가야 한다.

IMAGE 1 = panel C (한샘 원본 — edit base)
IMAGE 2 = SMART SHEET (panel별 가이드 메타 자료 · 결과로 복제 X · 정보만 활용)
이후 IMAGE 3~ = user-product reference

{product_essence}

=== [SPATIAL LAYOUT — preserve panel C] ===
{spatial}

=== [SMART SHEET 요약] ===
{sheet_summary}

=== [CUMULATIVE FINAL DIRECTIVE — LLM 생성] ===
{final_directive}

=== [ABSOLUTE RULES] ===
- 단일 panel 출력. multi-cell grid 절대 금지
- sheet 자체를 결과에 복제 X
- 사용자 제품 정보에 없는 feature 발명 X
- 한글 텍스트 또렷
"""


# ───────────────────────────── QA ─────────────────────────────
# qa() 함수는 pipeline_lib/qa_engine.evaluate() 로 대체됨.
# - 모든 ref 이미지 동봉 (A_1, A_2, ... + B + C)
# - verifiable checklist 기반 항목별 binary 채점
# - QA payload 자체를 run_dir/qa_payloads/{label}__a{n}.json 로 저장


# ───────────────────────────── fal generation ─────────────────────────────
async def fal_generate(prompt: str, ref_urls: list[str], image_size: str) -> str:
    args = {
        "prompt": prompt, "image_urls": ref_urls, "quality": "high",
        "image_size": image_size, "output_format": "png",
    }
    result = await fal_client.subscribe_async(ENDPOINT, arguments=args)
    imgs = result.get("images") or result.get("image")
    if isinstance(imgs, list) and imgs:
        f = imgs[0]
        return f["url"] if isinstance(f, dict) else f
    if isinstance(imgs, dict):
        return imgs["url"]
    raise ValueError(f"no url in fal result: {json.dumps(result)[:300]}")


# ───────────────────────────── per-panel runner ─────────────────────────────
async def run_target(
    label: str,
    panel: dict,
    panel_orig_path: Path,
    panel_ref_decision: dict,
    file_to_url: dict[Path, str],
    asset_root_dir: Path,
    base_url: str,
    image_size: str,
    product_input: dict,
    product_essence: str,
    sheet_info: dict | None,
    checklist: dict,
    assets_meta: dict,
    run_dir: Path,
    sem: asyncio.Semaphore,
):
    ref_keys = panel_ref_decision.get("ref_keys", [])
    ref_paths = [asset_root_dir / Path(p).name for p in panel_ref_decision.get("ref_paths", [])]
    panel_ref_urls = [file_to_url[p] for p in ref_paths if p in file_to_url]
    # QA용: 모든 ref + 라벨 (assets_meta에서 category/subject로 라벨 합성)
    panel_ref_labels = []
    for key in ref_keys:
        meta = assets_meta.get(key, {}) if isinstance(assets_meta, dict) else {}
        cat = meta.get("category", "?")
        subj = meta.get("subject", "")
        panel_ref_labels.append(f"{cat}·{subj}" if subj else cat)
    # checklist 항목 중 이 panel에 적용 가능한 것만
    panel_class_str = panel.get("panel_class", "other")
    applicable_items = verifiable_checklist.select_items_for_panel(
        checklist, panel_class_str, panel.get("spatial_layout", "")
    )
    # panel에 product_name 주입 (qa_engine 표시용)
    panel = {**panel, "_product_name": product_input.get("product_name", "")}

    # LLM edit_block (panel-specific)
    async with sem:
        edit_block_out = await asyncio.to_thread(
            llm_edit_block.generate_edit_block,
            openai_client, TEXT_MODEL, panel, product_input, ref_keys, panel_orig_path, data_uri,
        )
    edit_block = edit_block_out["edit_block"]

    attempts = []
    base_attempt_image_url: str | None = None  # paint-edit base를 위해

    for attempt_n in range(1, MAX_ATTEMPTS + 1):
        tag = f"[{label}/#{attempt_n}]"
        stage = "initial" if attempt_n == 1 else ("replan" if attempt_n == 2 else ("paint_edit" if attempt_n == 3 else "cumulative"))

        async with sem:
            t0 = time.time()
            # ── prompt 구성 ──
            sheet_url = (sheet_info or {}).get("fal_url")
            try:
                if stage == "initial":
                    use_sheet = bool(sheet_url)
                    prompt = assemble_initial_prompt(
                        panel, edit_block, ref_keys, product_essence,
                        applicable_items=applicable_items, sheet_in_refs=use_sheet,
                    )
                    if use_sheet:
                        ref_urls = [base_url, sheet_url] + panel_ref_urls
                    else:
                        ref_urls = [base_url] + panel_ref_urls

                elif stage == "replan":
                    prev = attempts[-1]
                    replan_out = await asyncio.to_thread(
                        retry_strategist.replan_prompt,
                        openai_client, TEXT_MODEL, panel,
                        prev.get("prompt", ""), prev.get("qa", {}),
                        product_essence, ref_keys, prev.get("attempt", attempt_n - 1),
                    )
                    new_prompt_core = replan_out["new_prompt"]
                    never_miss = _critical_never_miss_block(applicable_items)
                    prompt = (
                        f"=== [RETRY ANALYSIS · stage 1] ===\n"
                        f"diagnosis: {replan_out['diagnosis']}\n"
                        f"patches:\n  - " + "\n  - ".join(replan_out["patches"]) + "\n\n"
                        + never_miss + "\n"
                        + new_prompt_core
                    )
                    if sheet_url:
                        ref_urls = [base_url, sheet_url] + panel_ref_urls
                    else:
                        ref_urls = [base_url] + panel_ref_urls
                    prev["retry_diagnosis"] = replan_out["diagnosis"]

                elif stage == "paint_edit":
                    last_two = [a for a in attempts if "qa" in a][-2:]
                    if len(last_two) < 2:
                        # 첫 시도가 error로 끝났을 경우 — replan으로 fallback
                        prev = attempts[-1]
                        replan_out = await asyncio.to_thread(
                            retry_strategist.replan_prompt,
                            openai_client, TEXT_MODEL, panel,
                            prev.get("prompt", ""), prev.get("qa", {}),
                            product_essence, ref_keys, prev.get("attempt", attempt_n - 1),
                        )
                        prompt = (
                            f"=== [RETRY · paint_edit fallback to replan] ===\n"
                            + replan_out["new_prompt"]
                        )
                        ref_urls = [base_url] + panel_ref_urls
                    else:
                        # 두 시도 중 점수 높은 것을 base
                        paint_out = await asyncio.to_thread(
                            retry_strategist.paint_edit_prompt,
                            openai_client, TEXT_MODEL, panel,
                            [
                                {**last_two[0].get("qa", {}), "attempt": last_two[0].get("attempt"), "product_score": last_two[0].get("qa", {}).get("product_score", 0)},
                                {**last_two[1].get("qa", {}), "attempt": last_two[1].get("attempt"), "product_score": last_two[1].get("qa", {}).get("product_score", 0)},
                            ],
                            product_essence,
                        )
                        # base 이미지를 url로
                        base_idx = paint_out["base_attempt_idx"]
                        base_a = next((a for a in last_two if a.get("attempt") == base_idx), last_two[0])
                        base_attempt_image_url = base_a.get("fal_url")
                        prompt = assemble_paint_edit_prompt(panel, paint_out["paint_prompt"], product_essence)
                        # IMAGE 1 = paint base. ref들도 일부 같이 보내서 디테일 보정 도움.
                        ref_urls = [base_attempt_image_url] + panel_ref_urls[:3]

                elif stage == "cumulative":
                    prior_for_cum = [
                        {
                            "attempt": a.get("attempt"),
                            "product_score": a.get("qa", {}).get("product_score", 0),
                            "specific_failures": a.get("qa", {}).get("specific_failures", []),
                            "retry_diagnosis": a.get("retry_diagnosis", ""),
                        }
                        for a in attempts if "qa" in a
                    ]
                    cum_out = await asyncio.to_thread(
                        retry_strategist.cumulative_prompt,
                        openai_client, TEXT_MODEL, panel, prior_for_cum,
                        product_essence,
                        json.dumps(product_input.get("spec", {}), ensure_ascii=False),
                        (sheet_info or {}).get("sheet_summary", "smart sheet 없음"),
                    )
                    prompt = assemble_cumulative_prompt(
                        panel, cum_out["final_prompt"], product_essence,
                        (sheet_info or {}).get("sheet_summary", ""),
                    )
                    # sheet ref + panel refs
                    sheet_url = (sheet_info or {}).get("fal_url")
                    if sheet_url:
                        ref_urls = [base_url, sheet_url] + panel_ref_urls[:4]
                    else:
                        ref_urls = [base_url] + panel_ref_urls

                else:
                    prompt = assemble_initial_prompt(panel, edit_block, ref_keys, product_essence)
                    ref_urls = [base_url] + panel_ref_urls

                # prompt 사본 저장
                version_bundler.write_prompt(run_dir, label, attempt_n, prompt)

                print(f"{tag} stage={stage} refs={len(ref_urls)} (panel:{len(panel_ref_urls)})", flush=True)

                # ── 생성 ──
                img_path = run_dir / "gpt_image" / f"{label}__a{attempt_n}_v16.png"
                try:
                    gurl = await fal_generate(prompt, ref_urls, image_size)
                    await download(gurl, img_path)
                except Exception as e:
                    print(f"{tag} GEN ERR: {str(e)[:240]}")
                    attempts.append({
                        "attempt": attempt_n, "stage": stage, "prompt": prompt,
                        "ref_count": len(ref_urls), "error": str(e)[:400],
                    })
                    continue
                t_gen = time.time()

                # ── QA (qa_engine: 모든 ref 동봉 + checklist 기반 채점 + payload 저장) ──
                qa_payload_path = run_dir / "qa_payloads" / f"{label}__a{attempt_n}.json"
                try:
                    verdict = await asyncio.to_thread(
                        qa_engine.evaluate,
                        openai_client, VISION_MODEL, panel,
                        img_path, panel_orig_path,
                        ref_paths, panel_ref_labels,
                        checklist, applicable_items,
                        data_uri, qa_payload_path,
                    )
                except Exception as e:
                    print(f"{tag} QA ERR: {str(e)[:240]}")
                    attempts.append({
                        "attempt": attempt_n, "stage": stage, "image": img_path.name,
                        "fal_url": gurl, "prompt": prompt, "ref_count": len(ref_urls),
                        "error": f"QA: {str(e)[:240]}",
                    })
                    break

                version_bundler.write_qa_report(run_dir, label, attempt_n, verdict)
                t_end = time.time()
                attempts.append({
                    "attempt": attempt_n, "stage": stage, "image": img_path.name,
                    "fal_url": gurl, "image_size": image_size,
                    "prompt": prompt, "ref_count": len(ref_urls), "ref_keys": ref_keys,
                    "gen_seconds": round(t_gen - t0, 1),
                    "qa_seconds": round(t_end - t_gen, 1),
                    "qa_payload_rel": f"qa_payloads/{label}__a{attempt_n}.json",
                    "qa": verdict,
                })
                print(
                    f"{tag} fmt={verdict.get('image_format','?')} "
                    f"prod={verdict.get('product_score','?')} "
                    f"distortion_fail={verdict.get('distortion_fail_count','?')} "
                    f"forbidden_fail={verdict.get('forbidden_fail_count','?')} "
                    f"-> {verdict.get('verdict')}"
                )
                if verdict.get("verdict") == "pass":
                    break

                # ── anti-regression gate ──
                # 새 시도가 직전 best보다 distortion/forbidden fail이 같거나 많고,
                # product_score도 같거나 낮으면 → retry 중단 + best lock-in.
                # (좋은 결과를 망치는 retry 방지 — 사용자 핵심 요구)
                if attempt_n >= 2:
                    scored_so_far = [a for a in attempts if "qa" in a]
                    if len(scored_so_far) >= 2:
                        best_so_far = min(
                            scored_so_far,
                            key=lambda a: (
                                a.get("qa", {}).get("distortion_fail_count", 99)
                                + a.get("qa", {}).get("forbidden_fail_count", 99),
                                -(a.get("qa", {}).get("product_score", 0) or 0),
                            ),
                        )
                        latest = scored_so_far[-1]
                        # latest 가 best가 아니면, 그리고 latest 가 best보다 명확히 못하면 retry 중단
                        if best_so_far is not latest:
                            best_q = best_so_far.get("qa", {})
                            latest_q = latest.get("qa", {})
                            best_fail = (best_q.get("distortion_fail_count", 0)
                                         + best_q.get("forbidden_fail_count", 0))
                            latest_fail = (latest_q.get("distortion_fail_count", 0)
                                           + latest_q.get("forbidden_fail_count", 0))
                            best_score = best_q.get("product_score", 0) or 0
                            latest_score = latest_q.get("product_score", 0) or 0
                            if (latest_fail > best_fail) or (latest_fail == best_fail and latest_score < best_score - 5):
                                print(f"{tag} ★ anti-regression: latest(fail={latest_fail}, "
                                      f"score={latest_score}) < best(#{best_so_far['attempt']}, "
                                      f"fail={best_fail}, score={best_score}) → retry 중단")
                                break

            except Exception as e:
                print(f"{tag} STAGE ERR ({stage}): {str(e)[:240]}")
                attempts.append({"attempt": attempt_n, "stage": stage, "error": f"stage: {str(e)[:300]}"})
                continue

    # ── final 선택: LLM judge 토너먼트 (anti-regression) ──
    # attempt dict에 qa의 핵심 필드 spread해 best_selector가 직접 읽도록
    judge_attempts = []
    for a in attempts:
        if "qa" not in a:
            continue
        ja = dict(a)
        qa_d = a.get("qa") or {}
        ja["product_score"] = qa_d.get("product_score", 0)
        ja["critical_fail_count"] = qa_d.get("critical_fail_count", 0)
        ja["verdict"] = qa_d.get("verdict")
        ja["specific_failures"] = qa_d.get("specific_failures", [])
        judge_attempts.append(ja)

    passers = [a for a in judge_attempts if a.get("verdict") == "pass"]
    if passers:
        final = passers[0]
        judge_log = []
        method = "first_passer"
    elif judge_attempts:
        async with sem:
            best_out = await asyncio.to_thread(
                best_selector.select_best,
                openai_client, VISION_MODEL, panel,
                judge_attempts, product_input, checklist,
                run_dir / "gpt_image", data_uri,
            )
        final = best_out["final"]
        judge_log = best_out["judge_log"]
        method = best_out["method"]
    else:
        final = attempts[-1] if attempts else None
        judge_log = []
        method = "none"

    return {
        "label": label,
        "panel_idx": panel.get("panel_idx", 0),
        "panel_class": panel.get("panel_class", "other"),
        "image_size": image_size,
        "attempts": attempts,
        "final": final,
        "passed": bool(passers),
        "best_selection_method": method,
        "judge_log": judge_log,
        "edit_block": edit_block,
        "ref_keys": ref_keys,
        "ref_labels": panel_ref_labels,
        "applicable_item_ids": [it.get("id") for it in applicable_items],
        "ref_rationale": panel_ref_decision.get("rationale", ""),
    }


# ───────────────────────────── main ─────────────────────────────
async def main(rerun_labels: set[str] | None = None):
    """Full new run, or partial rerun of specific panel labels in the latest run dir.

    rerun_labels: e.g. {"cover", "panel_03"}. None이면 새 run.
    """
    from PIL import Image

    print("=== v16+ pipeline — checklist + qa_engine + best_selector + smart sheet ===")
    print(f"  endpoint: {ENDPOINT} · text: {TEXT_MODEL} · vision: {VISION_MODEL}")
    print(f"  CONCURRENCY={CONCURRENCY} · MAX_ATTEMPTS={MAX_ATTEMPTS}")
    if rerun_labels:
        print(f"  ★ RERUN mode — labels={sorted(rerun_labels)}")

    layouts, classification, product_input, mismatch = load_inputs()
    panels = list(layouts.values())
    bypass_idx = {idx for idx, r in mismatch.items() if r.get("verdict") in ("bypass", "skip")}
    if bypass_idx:
        print(f"  ★ bypass/skip panels (generation 제외): {sorted(bypass_idx)}")

    # 1) run dir — 새 run 또는 latest 재사용
    if rerun_labels:
        latest_pointer = SWAP_RESULTS_DIR / "latest.txt"
        if not latest_pointer.exists():
            raise SystemExit("rerun mode인데 latest.txt 없음")
        run_name = latest_pointer.read_text().strip()
        run_dir = SWAP_RESULTS_DIR / run_name
        if not run_dir.exists():
            raise SystemExit(f"latest run dir 없음: {run_dir}")
        # 기존 version 추출
        import re as _re
        m = _re.match(r"^v(\d+)_", run_name)
        version = int(m.group(1)) if m else version_bundler.next_version(SWAP_RESULTS_DIR)
        print(f"  rerun run_dir: {run_dir} (v{version})")
    else:
        run_dir, version = version_bundler.make_run_dir(SWAP_RESULTS_DIR)
        print(f"  run_dir: {run_dir} (v{version})")
    (run_dir / "qa_payloads").mkdir(exist_ok=True)
    (run_dir / "gpt_image").mkdir(exist_ok=True)
    (run_dir / "prompts").mkdir(exist_ok=True)
    (run_dir / "qa_reports").mkdir(exist_ok=True)

    # 1.5) Verifiable checklist 추출 — rerun이면 기존 파일 재사용
    checklist_path = run_dir / "verifiable_checklist.json"
    if rerun_labels and checklist_path.exists():
        checklist = json.loads(checklist_path.read_text())
        print(f"\n[0/5] checklist 재사용 (category={checklist.get('category')}, items={len(checklist.get('items', []))})")
    else:
        print("\n[0/5] Verifiable checklist 추출 (카테고리 + binary 항목)...")
        checklist = await asyncio.to_thread(
            verifiable_checklist.extract_checklist,
            openai_client, TEXT_MODEL, product_input,
        )
        checklist_path.write_text(json.dumps(checklist, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  → category={checklist.get('category')} · items={len(checklist.get('items', []))} · "
              f"axes={', '.join(checklist.get('category_check_axes', []) or [])}")

    # 2) LLM panel → ref 매핑 — rerun이면 기존 파일 재사용
    cover_panel = layouts.get("cover") or {"panel": "cover", "panel_class": "intro_hero",
                                           "spatial_layout": "Cover hero shot."}
    mapping_path = run_dir / "panel_ref_mapping_v16.json"
    if rerun_labels and mapping_path.exists():
        mapping = json.loads(mapping_path.read_text())
        print(f"\n[1/5] panel→ref mapping 재사용 ({len(mapping['panels'])} panels)")
    else:
        print("\n[1/5] LLM panel → ref mapping...")
        assets_index = llm_panel_mapper.build_assets_index(classification.get("items", []), asset_root="use_product")
        mapping = await asyncio.to_thread(
            llm_panel_mapper.map_all_panels,
            openai_client, TEXT_MODEL,
            [p for p in panels if p.get("panel") != "cover"],
            assets_index, product_input,
            template_dir=TEMPLATE_DIR,
            data_uri_fn=data_uri,
            cover_panel=cover_panel,
        )
        mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  → wrote {mapping_path.name} ({len(mapping['panels'])} panels)")

    # 3) Smart sheet — rerun이면 기존 PNG 재사용
    sheet_path = run_dir / "smart_sheet.png"
    sheet_info = None
    if rerun_labels and sheet_path.exists():
        sheet_info = {
            "path": str(sheet_path), "fal_url": None,
            "sheet_summary": "기존 smart sheet 재사용",
        }
        # fal_url 복원: 기존 summary.json에서
        prev_summary_path = run_dir / "summary.json"
        if prev_summary_path.exists():
            try:
                prev = json.loads(prev_summary_path.read_text())
                if prev.get("smart_sheet"):
                    sheet_info["fal_url"] = prev["smart_sheet"].get("fal_url")
            except Exception:
                pass
        print(f"\n[2/5] smart sheet 재사용 ({sheet_path.stat().st_size // 1024}KB)")
    else:
        print("\n[2/5] Smart sheet 생성...")
        sheet_plan = await asyncio.to_thread(
            smart_sheet_builder.plan_sheet_prompt,
            openai_client, TEXT_MODEL, product_input,
            classification.get("items", []), mapping, USE_PROD, 10,
        )
        try:
            sheet_info = await smart_sheet_builder.build_sheet_image(
                sheet_plan, sheet_path, upload, download, ENDPOINT, "landscape_16_9",
            )
            sheet_info["sheet_summary"] = sheet_plan.get("sheet_summary", "")
            print(f"  → smart_sheet.png ({sheet_path.stat().st_size // 1024}KB)")
        except Exception as e:
            print(f"  ! smart sheet 실패 (cumulative stage에서 fallback): {str(e)[:200]}")

    # 4) 모든 ref 파일 dedupe upload
    print("\n[3/5] 자원 upload...")
    all_files: set[Path] = set()
    for m in mapping["panels"].values():
        for rp in m.get("ref_paths", []):
            all_files.add(USER_DIR / rp)
    all_files_list = sorted(all_files, key=lambda p: str(p))
    upload_urls = await asyncio.gather(*[upload(p) for p in all_files_list])
    file_to_url = dict(zip(all_files_list, upload_urls))
    print(f"  uploaded {len(file_to_url)} unique ref files")

    # base (panel original) upload
    targets = []
    cover_path = TEMPLATE_DIR / "_cover_1000.jpg"
    if cover_path.exists() and "cover" in mapping["panels"]:
        targets.append(("cover", cover_path, {"panel": "cover", **cover_panel,
                                              "panel_idx": 0, "panel_class": cover_panel.get("panel_class", "intro_hero")}))
    bypass_cells = []
    for panel in panels:
        pid = panel.get("panel", "")
        if pid == "cover" or "error" in panel:
            continue
        idx = panel.get("panel_idx")
        if idx is None:
            continue
        ppath = next(TEMPLATE_DIR.glob(f"panel_{idx:02d}.*"), None)
        if not ppath:
            continue
        # ★ verdict bypass/skip 인 panel은 generation 제외, summary에는 verdict 카드로
        if idx in bypass_idx:
            verdict_info = mismatch.get(idx, {})
            bypass_cells.append({
                "label": f"panel_{idx:02d}",
                "panel_idx": idx,
                "panel_class": panel.get("panel_class", "other"),
                "verdict": verdict_info.get("verdict", "bypass"),
                "verdict_info": verdict_info,
                "passed": True,  # bypass = 설계상 의도된 skip → pass 카운트
                "attempts": [],
                "final": None,
                "note": "verdict bypass — generation 제외 (사용자 제품에 동등 정보 없음)",
            })
            continue
        targets.append((f"panel_{idx:02d}", ppath, panel))

    # rerun mode: 대상 label만 keep + 기존 cells 보존
    preserved_cells: list[dict] = []
    if rerun_labels:
        prev_summary_path = run_dir / "summary.json"
        if prev_summary_path.exists():
            try:
                prev_summary = json.loads(prev_summary_path.read_text())
                for c in prev_summary.get("cells", []) or []:
                    if c.get("label") not in rerun_labels:
                        preserved_cells.append(c)
            except Exception as e:
                print(f"  ! prev summary read err: {e}")
        targets = [t for t in targets if t[0] in rerun_labels]
        print(f"  rerun targets: {[t[0] for t in targets]} · preserved cells: {len(preserved_cells)}")

    base_urls = {}
    for label, ppath, _panel in targets:
        base_urls[label] = await upload(ppath)

    # 5) per-panel swap (병렬)
    print(f"\n[4/5] swap 생성 (targets={len(targets)})...")
    product_essence = product_essence_text(product_input)
    assets_meta = mapping.get("assets_meta") or {}
    sem = asyncio.Semaphore(CONCURRENCY)
    t0 = time.time()
    jobs = []
    for label, ppath, panel in targets:
        w, h = Image.open(ppath).size
        size_param = image_size_for(w, h)
        decision = (
            mapping["panels"].get(panel.get("panel", ""))
            or mapping["panels"].get(label)
            or {}
        )
        if not decision:
            print(f"  ! skip {label} — 매핑 없음")
            continue
        jobs.append(run_target(
            label, panel, ppath, decision, file_to_url, USE_PROD,
            base_urls[label], size_param,
            product_input, product_essence, sheet_info,
            checklist, assets_meta,
            run_dir, sem,
        ))

    # ── streaming: panel 완료마다 즉시 summary patch + report 빌드 (debounced) ──
    # bypass cells는 처음부터 cells에 포함 (generation 제외)
    cells: list[dict] = list(bypass_cells)
    total_jobs = len(jobs)
    done_count = 0
    tasks = [asyncio.create_task(j) for j in jobs]

    # debounced builder
    builder_lock = asyncio.Lock()
    builder_pending = {"flag": False}
    builder_inflight = {"flag": False}

    async def _spawn_builder():
        # 별도 프로세스 — pipeline progress 막지 않게
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(HERE / "59_build_report_v22.py"),
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()
        except Exception as e:
            print(f"  ! builder spawn failed: {e}")

    async def _trigger_builder():
        if builder_inflight["flag"]:
            builder_pending["flag"] = True
            return
        async with builder_lock:
            builder_inflight["flag"] = True
            try:
                await _spawn_builder()
                while builder_pending["flag"]:
                    builder_pending["flag"] = False
                    await _spawn_builder()
            finally:
                builder_inflight["flag"] = False

    def _flatten_cell(cell: dict) -> dict:
        if cell.get("final") and isinstance(cell["final"], dict) and "qa" in cell["final"]:
            cell["final"] = {**cell["final"], **(cell["final"].get("qa") or {})}
        for a in cell.get("attempts", []) or []:
            if isinstance(a, dict) and "qa" in a and isinstance(a["qa"], dict):
                qa_dict = a.pop("qa")
                a.update(qa_dict)
        if "strategies_used" not in cell:
            cell["strategies_used"] = sorted({a.get("stage", "") for a in cell.get("attempts", []) if a.get("stage")})
        return cell

    def _write_partial_summary():
        wall_now = round(time.time() - t0, 1)
        merged_cells = list(preserved_cells) + cells
        # 동일 label 중복 방지 — 새 cell이 preserved를 override
        seen: dict[str, dict] = {}
        for c in merged_cells:
            lbl = c.get("label")
            if lbl:
                seen[lbl] = c
        merged_cells = list(seen.values())
        summary = {
            "run": run_dir.name,
            "version": version,
            "endpoint": ENDPOINT,
            "text_model": TEXT_MODEL,
            "vision_model": VISION_MODEL,
            "max_attempts": MAX_ATTEMPTS,
            "concurrency": CONCURRENCY,
            "wall_seconds": wall_now,
            "model_options_count": len(product_input.get("model_options") or []),
            "cells": merged_cells,
            "smart_sheet": sheet_info,
            "panel_ref_mapping_path": str(mapping_path.relative_to(run_dir)),
            "progress": {
                "done": done_count,
                "total": total_jobs,
                "in_progress": [lbl for (lbl, _, _) in targets if not any(c.get("label") == lbl for c in cells)],
                "is_complete": done_count >= total_jobs,
                "rerun_labels": sorted(rerun_labels) if rerun_labels else None,
            },
        }
        (run_dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # 초기 빈 summary 작성 — report가 진행 중 표시할 수 있게
    _write_partial_summary()
    # latest pointer를 미리 갱신해 빌더가 이 run_dir를 잡도록
    version_bundler.update_latest_pointer(SWAP_RESULTS_DIR, version, run_dir.name)
    # 첫 빌드 트리거 (smart sheet/매핑까지의 진척만이라도)
    asyncio.create_task(_trigger_builder())

    for fut in asyncio.as_completed(tasks):
        try:
            cell = await fut
        except Exception as e:
            print(f"  ! cell task error: {e}")
            done_count += 1
            continue
        if isinstance(cell, dict):
            cells.append(_flatten_cell(cell))
        done_count += 1
        print(f"  → progress {done_count}/{total_jobs} done", flush=True)
        _write_partial_summary()
        asyncio.create_task(_trigger_builder())

    wall = round(time.time() - t0, 1)
    # 최종 summary (progress.is_complete=True)
    _write_partial_summary()

    # 산출물 패키징 — 사용된 .py / 입력 데이터 동봉
    bundled = version_bundler.bundle_sources(run_dir, [
        Path(__file__),
        HERE / "pipeline_lib/__init__.py",
        HERE / "pipeline_lib/version_bundler.py",
        HERE / "pipeline_lib/llm_panel_mapper.py",
        HERE / "pipeline_lib/llm_edit_block.py",
        HERE / "pipeline_lib/smart_sheet_builder.py",
        HERE / "pipeline_lib/retry_strategist.py",
        HERE / "pipeline_lib/verifiable_checklist.py",
        HERE / "pipeline_lib/qa_engine.py",
        HERE / "pipeline_lib/best_selector.py",
        PRODUCT_INPUT_FILE,
        LAYOUT_FILE,
        CLASSIFICATION_FILE,
    ])
    version_bundler.write_manifest(run_dir, {
        "version": version,
        "run": run_dir.name,
        "endpoint": ENDPOINT,
        "text_model": TEXT_MODEL,
        "vision_model": VISION_MODEL,
        "concurrency": CONCURRENCY,
        "max_attempts": MAX_ATTEMPTS,
        "bundled_sources": bundled,
        "smart_sheet_path": str(sheet_path.relative_to(run_dir)) if sheet_info else None,
        "panel_ref_mapping_path": str(mapping_path.relative_to(run_dir)),
        "verifiable_checklist_path": str(checklist_path.relative_to(run_dir)),
        "summary_path": "summary.json",
        "notes": "v16+ — checklist 기반 QA + 모든 ref 동봉 + payload save + best_selector",
    })

    version_bundler.update_latest_pointer(SWAP_RESULTS_DIR, version, run_dir.name)

    # 최종 빌드 (마지막 cell 반영 보장)
    await _trigger_builder()

    passers = sum(1 for c in cells if c.get("passed"))
    print(f"\n=== DONE === {run_dir}")
    print(f"  wall: {wall}s · passers: {passers}/{len(cells)} · version: v{version}")
    for c in cells:
        f = c.get("final") or {}
        print(
            f"    {c['label']:12} [{c['panel_class']:>17}] "
            f"fmt={f.get('image_format','?')} prod={f.get('product_score','?'):>3} "
            f"crit_fail={f.get('critical_fail_count','?')} pass={c.get('passed')}"
        )


def _parse_args():
    p = argparse.ArgumentParser(
        description="v16+ swap pipeline — full run or per-panel rerun. Template/user dir CLI 지정 가능."
    )
    p.add_argument("--template", help="templates/0X_<category>_<gdsNo> 경로 (default: 01_sofa_992474)")
    p.add_argument("--user-product", help="user_products/<product_id> 경로 (default: milo_777039)")
    p.add_argument("--product-input", default=DEFAULT_PRODUCT_INPUT_NAME,
                   help="user_product 디렉토리 안의 product_input json 파일명 (default: product_input_v3.json)")
    p.add_argument("--rerun", help="쉼표 구분 panel label list (e.g. 'cover,panel_03'). 지정 시 latest run dir에 partial rerun.")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    if args.template:
        tpl = Path(args.template)
        if not tpl.is_absolute():
            tpl = HERE / tpl
        if args.user_product:
            usr = Path(args.user_product)
            if not usr.is_absolute():
                usr = HERE / usr
        else:
            usr = DEFAULT_USER_DIR
        _set_paths(tpl, usr, args.product_input)
        print(f"  TEMPLATE_DIR = {TEMPLATE_DIR}")
        print(f"  USER_DIR     = {USER_DIR}")
    rerun = None
    if args.rerun:
        rerun = {x.strip() for x in args.rerun.split(",") if x.strip()}
    asyncio.run(main(rerun_labels=rerun))

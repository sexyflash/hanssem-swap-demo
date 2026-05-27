"""Smart sheet builder — 사용자 제품의 '제작 가이드' 시트 1장 생성.

복원 + 강화 (사용자 요구):
- 기존 archive_sheets/72_make_master_sheet_v3 처럼 sheet 자체에 DO/DON'T + reference cells
- 추가: panel별 "이 panel에서 강조할 디테일" 표 (500% 정보)
- 추가: 사용자 제품 spec/소재/구조/인증을 정량 텍스트로 응축
- LLM이 product_input + classification + panel_layout 를 보고 directive를 직접 작성
- 출력: PNG (단일 16:9 landscape) + sidecar JSON (생성에 쓰인 directive + ref 목록)

핵심: swap 엔진이 이 시트만 봐도 모든 핵심 정보를 끄집어낼 수 있어야 함. 그러나
sheet 자체가 결과로 복제되면 안 되므로 'REFERENCE METADATA — DO NOT REPLICATE'
워터마크와 회색 배경으로 product photo가 아님을 명확히.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import fal_client


SYSTEM_PROMPT = """\
당신은 한국 가구/생활용품 swap 파이프라인을 위한 PRODUCT GUIDE 시트의 directive 작성자다.
사용자 제품 정보와 panel 매핑 정보를 받아, 이미지 생성 엔진(fal-ai/gpt-image-2/edit)에
보낼 한국어 prompt를 작성한다.

이 시트는 swap 엔진이 '한 장만 봐도 panel별 제작에 필요한 모든 디테일/구도/특징'을
파악할 수 있도록 풍부하고 구조화된 가이드여야 한다. 단, 시트 자체는 swap 결과에 복제되면
안 되므로 워터마크/회색 배경/박스 윤곽으로 product photo가 아님이 분명해야 한다.

원칙:
1) 사용자가 제공한 product_input.feature_descriptions의 정량 정보(치수, 소재, 다리 개수,
   쿠션 구성, 시접, 인증 등)를 가능한 한 응축해 시트에 표기.
2) panel별 mini-map: 각 panel id → 그 panel이 강조할 핵심 디테일/카메라 각도/금지 사항을
   짧은 표 행으로.
3) PRESERVE / NEVER 박스에는 panel 공통의 절대 규칙. NEVER에는 사용자가 제공하지 않은
   feature는 모두 금지 (예: 사용자가 헤드레스트 X 라면 헤드레스트 발명 금지).
4) 컬러 옵션이 있으면 정확한 한글 컬러명만 라벨에 인쇄하도록 강조.
5) 시트는 단일 16:9 landscape PNG. 회색/베이지 배경, 큰 워터마크, 박스/라인 명확.
6) directive는 길어도 좋다 — 충분히 풍부하게.

출력은 strict JSON.
"""


USER_PROMPT_TEMPLATE = """\
=== TASK ===
이 사용자 제품에 대한 PRODUCT GUIDE 시트 생성을 위한 fal prompt를 작성하라.

=== 사용자 제품 ===
제품명: {product_name}
{product_summary}

=== 색상 옵션 (정확한 한글) ===
{color_block}

=== 모델 옵션 ===
{model_block}

=== 자원 매핑 (모든 panel × 자원 — 시트에 작은 매핑 표로 들어갈 정보) ===
{panel_map_block}

=== 시트에 들어갈 reference 이미지 슬롯 ({n_refs}장) — 순서대로 image_urls ===
{refs_block}

=== 출력 schema (strict JSON) ===
{{
  "fal_prompt": "한국어로 작성한 시트 생성 directive (충분히 길게, panel별 mini-table까지 포함)",
  "sheet_summary": "시트가 담는 정보의 한 줄 요약",
  "ref_label_order": ["IMAGE 1 라벨", "IMAGE 2 라벨", ...]  // image_urls 순서와 동일
}}

fal_prompt 작성 시 반드시 포함:
- 상단 헤더: 제품명 + "PRODUCT GUIDE — REFERENCE METADATA · DO NOT REPLICATE"
- 섹션 1: PRODUCT REFERENCE cells (정면/측면/각도 등 메인 이미지)
- 섹션 2: DETAIL CLOSE-UP cells (디테일 분류 자원)
- 섹션 3: COLOR & MATERIAL cells (있으면)
- 섹션 4: PRESERVE ✓ / NEVER ✗ 박스 (제품 핵심 특징 기반)
- 섹션 5: PANEL → ASSET MAP (작은 표 — panel id × 사용 자원 keys)
- 섹션 6: SPEC / CERTIFICATIONS 텍스트 영역 (정량 정보)
- 워터마크: 모든 코너 + 중앙 하단
- 배경: 옅은 회색/베이지, sans-serif, 큰 여백
- 단일 16:9 landscape PNG, 한글 모두 또렷이
"""


def _format_product_summary(product_input: dict) -> str:
    sp = product_input.get("spec", {})
    fd = product_input.get("feature_descriptions", {})
    parts = []
    if sp:
        dims = f"{sp.get('width_cm','?')}×{sp.get('depth_cm','?')}×{sp.get('height_cm','?')}cm"
        parts.append(f"제원: {dims}")
        extras = ", ".join(f"{k}={v}" for k, v in sp.items() if v not in (None, "") and k not in ("width_cm", "depth_cm", "height_cm"))
        if extras:
            parts.append(f"세부 제원: {extras}")
    for key, value in fd.items():
        if value:
            parts.append(f"· {key}: {str(value)[:320]}")
    if product_input.get("intro_full"):
        parts.append(f"· intro: {product_input['intro_full'][:280]}")
    if product_input.get("delivery_warranty"):
        parts.append(f"· delivery/warranty: {product_input['delivery_warranty'][:260]}")
    if product_input.get("certifications_full"):
        parts.append(f"· certifications: {product_input['certifications_full'][:260]}")
    return "\n".join(parts)


def _format_colors(product_input: dict) -> str:
    colors = product_input.get("color_options_detail", []) or []
    if not colors:
        return "  (없음)"
    return "\n".join(f'  · "{c.get("name","")}" — {c.get("description","")[:180]}' for c in colors)


def _format_models(product_input: dict) -> str:
    models = product_input.get("model_options", []) or []
    if not models:
        return "  (없음)"
    return "\n".join(
        f"  · {m.get('name','')} ({m.get('dimensions','')})"
        + (" [selected]" if m.get("selected") else "")
        for m in models
    )


def _format_panel_map(panel_mapping: dict) -> str:
    panels = panel_mapping.get("panels", {})
    if not panels:
        return "  (없음)"
    lines = []
    for pid, m in panels.items():
        keys = ", ".join(m.get("ref_keys", []))
        ratl = m.get("rationale", "")
        lines.append(f"  · {pid:>14} [{m.get('panel_class','?')}] → {keys}\n      rationale: {ratl[:160]}")
    return "\n".join(lines)


def _select_sheet_refs(
    classification_items: list[dict],
    asset_root_dir: Path,
    max_refs: int = 10,
) -> list[tuple[Path, str]]:
    """시트에 박을 reference 이미지를 분류 기반으로 선택.

    우선순위: main_view → detail_close_up → color_variant → material → 나머지.
    각 카테고리에서 confidence 높은 순. 총 max_refs 장.
    """
    by_cat: dict[str, list[dict]] = {}
    for item in classification_items:
        by_cat.setdefault(item.get("category", "other"), []).append(item)
    for cat in by_cat:
        by_cat[cat].sort(key=lambda x: -float(x.get("confidence", 0)))

    priority = ["main_view", "detail_close_up", "color_variant", "material"]
    picked: list[tuple[Path, str]] = []
    seen_files: set[str] = set()

    def label_for(item: dict) -> str:
        cat = item.get("category", "other").upper().replace("_", " ")
        subj = item.get("subject", "")
        return f"{cat} · {subj}"

    # 라운드 로빈으로 카테고리당 골고루
    while len(picked) < max_refs:
        progressed = False
        for cat in priority + [c for c in by_cat if c not in priority]:
            if not by_cat.get(cat):
                continue
            item = by_cat[cat].pop(0)
            fn = item.get("filename")
            if not fn or fn in seen_files:
                continue
            p = asset_root_dir / fn
            if not p.exists():
                continue
            picked.append((p, label_for(item)))
            seen_files.add(fn)
            progressed = True
            if len(picked) >= max_refs:
                break
        if not progressed:
            break
    return picked


def plan_sheet_prompt(
    openai_client: Any,
    text_model: str,
    product_input: dict,
    classification_items: list[dict],
    panel_mapping: dict,
    asset_root_dir: Path,
    max_refs: int = 10,
) -> dict:
    """LLM이 시트 directive(fal_prompt)를 작성. ref 선택은 분류 기반 priority로."""
    refs = _select_sheet_refs(classification_items, asset_root_dir, max_refs=max_refs)
    refs_block = "\n".join(f"  · IMAGE {i+1}: {p.name} — {lbl}" for i, (p, lbl) in enumerate(refs))

    user_prompt = USER_PROMPT_TEMPLATE.format(
        product_name=product_input.get("product_name", ""),
        product_summary=_format_product_summary(product_input),
        color_block=_format_colors(product_input),
        model_block=_format_models(product_input),
        panel_map_block=_format_panel_map(panel_mapping),
        n_refs=len(refs),
        refs_block=refs_block,
    )

    resp = openai_client.chat.completions.create(
        model=text_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    plan = json.loads(resp.choices[0].message.content or "{}")
    plan["ref_paths"] = [str(p) for p, _ in refs]
    plan["ref_labels"] = [lbl for _, lbl in refs]
    return plan


async def build_sheet_image(
    plan: dict,
    out_path: Path,
    upload_fn,
    download_fn,
    fal_endpoint: str = "fal-ai/gpt-image-2/edit",
    image_size: str = "landscape_16_9",
) -> dict:
    """plan(fal_prompt + ref_paths)으로 fal 호출 → PNG 다운로드."""
    ref_paths = [Path(p) for p in plan["ref_paths"]]
    ref_urls = []
    for p in ref_paths:
        ref_urls.append(await upload_fn(p))

    args = {
        "prompt": plan["fal_prompt"],
        "image_urls": ref_urls,
        "quality": "high",
        "image_size": image_size,
        "output_format": "png",
    }
    result = await fal_client.subscribe_async(fal_endpoint, arguments=args)
    imgs = result.get("images") or result.get("image")
    if isinstance(imgs, list) and imgs:
        url = imgs[0]["url"] if isinstance(imgs[0], dict) else imgs[0]
    elif isinstance(imgs, dict):
        url = imgs["url"]
    else:
        raise ValueError(f"no url in result: {json.dumps(result)[:300]}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    await download_fn(url, out_path)
    return {"path": str(out_path), "fal_url": url, "ref_urls": ref_urls, "prompt": plan["fal_prompt"]}

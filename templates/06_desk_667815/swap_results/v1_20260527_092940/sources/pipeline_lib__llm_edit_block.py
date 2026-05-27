"""LLM 기반 panel별 EDIT 지시 생성 — 74/75의 build_edit_block if/elif 룰을 대체.

핵심 idea:
- panel_class별 하드코딩된 텍스트 치환("300→200" 등) 대신, LLM이 panel 원본 이미지와
  사용자 제품 정보를 보고 직접 "어떤 텍스트를 어떤 텍스트로", "어떤 시각 요소를 어떻게"
  변경할지 결정.
- 결과는 prompt 안에 삽입 가능한 [EXPLICIT EDITS] 블록 (한국어).

LLM은 두 가지를 본다:
1) panel 원본 이미지 (OCR + 시각으로 한샘 텍스트/구조 파악)
2) product_input_v3.json 의 spec / feature_descriptions / color_options / model_options
   + classification 자원 (어떤 디테일 reference가 있는지)

출력 schema:
{
  "edit_block": "EXPLICIT EDITS — ...\\n[1] ...",   # 그대로 prompt에 삽입
  "text_substitutions": [{"from": "...", "to": "..."}, ...],  # 감사용
  "visual_changes": ["...", "..."],
  "preserve": ["..."]
}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SYSTEM_PROMPT = """\
당신은 한국 가구/생활용품 detail page swap 파이프라인의 EDIT INSTRUCTION GENERATOR다.
사용자가 한샘 원본 panel을 자신의 제품으로 교체하려고 한다. 너는 그 panel의 원본 이미지를
직접 보고 (한글 텍스트 OCR + 시각적 구조 파악), 사용자 제품 정보와 가용 reference 자원을
기반으로 "정확히 무엇을 어떻게 바꿔야 하는지" 한국어로 작성한다.

원칙:
1) 텍스트 치환은 panel 원본에 실제로 보이는 한국어 문자열 → 사용자 제품의 정확한 값
   (제원, 모델명, 컬러명 등). 발명 금지. 사용자 제품 정보에 없는 라벨은 만들지 않음.
2) 컬러명은 사용자가 제공한 정확한 한글 그대로 쓰고 "" quote. 한샘 컬러명 잔존 금지.
3) 모델/사이즈/라인업이 panel에 여러 칸으로 표시되어 있어도 사용자 제품의 실제 모델 수에
   맞춰 칸 수를 조정 (한샘 4-seat → 사용자 2-seat 이면 사이즈 차트도 2-seat 한 줄).
4) 다리/팔걸이/쿠션 등의 시각적 디테일은 사용자 제품 feature_descriptions를 충실히 반영.
5) panel의 layout/카메라 각도/배경/조명/한국어 텍스트 가독성은 KEEP.
6) panel이 close-up 디테일이면 frame 안에 들어오는 요소만 검증 (예: 다리가 frame 밖이면
   다리 개수 강제 X).
7) edit_block은 prompt에 그대로 삽입되므로 markdown/번호 매기기로 가독성 있게.

출력은 strict JSON.
"""

USER_PROMPT_TEMPLATE = """\
=== TASK ===
이 panel을 사용자 제품으로 swap 할 때의 EDIT 지시문을 작성하라.

=== PANEL CONTEXT ===
panel_id: {panel_id}
panel_class: {panel_class}
spatial_layout: {spatial_layout}
elements:
{elements_block}

=== 사용자 제품 (target) ===
{product_summary}

=== 사용자 제공 색상 옵션 (정확한 한글) ===
{color_block}

=== 사용자 모델 옵션 (정확한 이름 / 사이즈) ===
{model_block}

=== 사용 가능한 reference keys (이번 panel에 매핑된 것) ===
{ref_keys_block}

=== 출력 schema (strict JSON) ===
{{
  "edit_block": "EXPLICIT EDITS — <panel_class>:\\n[1] ...\\n[2] ...\\nKEEP: ...",
  "text_substitutions": [{{"from": "한샘 원본 텍스트", "to": "치환될 텍스트", "context": "어디 라벨/제목"}}],
  "visual_changes": ["..."],
  "preserve": ["..."],
  "panel_specific_notes": "panel의 특수 사정 (예: close-up이라 다리 frame 밖 등)"
}}
"""


def _format_product_summary(product_input: dict) -> str:
    pn = product_input.get("product_name", "")
    sp = product_input.get("spec", {})
    fd = product_input.get("feature_descriptions", {})
    lines = [f"제품명: {pn}"]
    if sp:
        lines.append(f"제원: {sp.get('width_cm','?')}×{sp.get('depth_cm','?')}×{sp.get('height_cm','?')}cm")
        for k, v in sp.items():
            if k in ("width_cm", "depth_cm", "height_cm"):
                continue
            if v not in (None, ""):
                lines.append(f"  · {k}: {v}")
    for key, value in fd.items():
        if value:
            lines.append(f"· {key}: {str(value)[:260]}")
    if product_input.get("intro_full"):
        lines.append(f"· intro: {product_input['intro_full'][:240]}")
    if product_input.get("certifications_full"):
        lines.append(f"· certifications: {product_input['certifications_full'][:200]}")
    return "\n".join(lines)


def _format_colors(product_input: dict) -> str:
    colors = product_input.get("color_options_detail", []) or []
    if not colors:
        return "  (없음)"
    return "\n".join(f'  · "{c.get("name","")}" — {c.get("description","")[:140]}' for c in colors)


def _format_models(product_input: dict) -> str:
    models = product_input.get("model_options", []) or []
    if not models:
        return "  (없음)"
    return "\n".join(
        f"  · {m.get('name','')} ({m.get('dimensions','')})"
        + (" [selected]" if m.get("selected") else "")
        for m in models
    )


def _format_elements(elements: list[dict]) -> str:
    if not elements:
        return "  (none)"
    return "\n".join(
        f"  - {e.get('role','?')} @ {e.get('position','?')}: {e.get('description','')[:180]}"
        for e in elements
    )


def generate_edit_block(
    openai_client: Any,
    vision_model: str,
    panel: dict,
    product_input: dict,
    ref_keys: list[str],
    panel_image_path: Path,
    data_uri_fn,
) -> dict:
    """단일 panel의 edit 지시문 생성."""
    user_prompt = USER_PROMPT_TEMPLATE.format(
        panel_id=panel.get("panel", "?"),
        panel_class=panel.get("panel_class", "other"),
        spatial_layout=panel.get("spatial_layout", "") or "",
        elements_block=_format_elements(panel.get("elements", []) or []),
        product_summary=_format_product_summary(product_input),
        color_block=_format_colors(product_input),
        model_block=_format_models(product_input),
        ref_keys_block=", ".join(ref_keys) if ref_keys else "(없음)",
    )

    content = [
        {"type": "text", "text": user_prompt},
        {"type": "text", "text": "panel 원본 이미지 (한글 OCR + 시각 분석):"},
        {"type": "image_url", "image_url": {"url": data_uri_fn(panel_image_path)}},
    ]

    resp = openai_client.chat.completions.create(
        model=vision_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_object"},
    )
    result = json.loads(resp.choices[0].message.content or "{}")
    result.setdefault("edit_block", "EXPLICIT EDITS — fallback.\n[1] panel을 사용자 제품으로 교체.")
    result.setdefault("text_substitutions", [])
    result.setdefault("visual_changes", [])
    result.setdefault("preserve", [])
    return result

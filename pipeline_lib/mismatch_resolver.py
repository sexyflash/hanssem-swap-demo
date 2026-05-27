"""한샘 panel × 사용자 제품 mismatch 자동 결정 — 사용자 수동 작성 X.

각 한샘 panel 에 대해 LLM 이:
1) 한샘 panel 이 강조하는 feature 추출 (hanssem_feature)
2) 사용자 제품에 동등 / 부분 / 없음 판단 (milo_has_it: yes/partial/no)
3) verdict 결정:
   - match: 사용자 제품으로 swap 가능
   - bypass: 사용자 제품에 없는 기능 → 대체 컨텐츠 (alt_title + alt_body 생성)
   - skip: 부적합 / 정보 누락 → 건너뜀
4) bypass 시 alt_title + alt_body 자동 생성

출력 스키마는 기존 mismatch_resolution.json 과 동일:
{
  "resolutions": [
    {
      "panel_idx": int,
      "verdict": "match|bypass|skip",
      "hanssem_feature": str,
      "milo_has_it": "yes|partial|no",
      "reasoning": str,
      "alt_title": str,   # bypass 시
      "alt_body": str,    # bypass 시
      "overlay_label": str  # bypass 시
    }
  ]
}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SYSTEM_PROMPT = """\
당신은 한국 가구/생활용품 detail-page swap 파이프라인의 MISMATCH RESOLVER 다.
한샘 원본 panel 한 장에 대해, 사용자 제품으로 swap 가능한지 자동 판단한다.

판정 기준:
1) **match**: 사용자 제품으로 swap 결과가 의미 있게 만들어진다.
   - 사용자 제품에 동등 또는 대체 가능한 feature 가 존재
   - 예: 사용자 제품도 같은 카테고리 + 비슷한 view (정면 / 측면 / 디테일)
   - 사이즈/컬러/구조 차트는 사용자 제품 정보로 채울 수 있으면 match
2) **bypass**: 한샘 panel 의 핵심 feature 가 사용자 제품에 존재하지 않음.
   - 한샘 = 리클라이너 메커니즘, 헤드레스트 옵션, USB 컨트롤, EO 인증 차트 같은
     특정 기능 강조 → 사용자 제품에 없으면 bypass
   - bypass 시 panel 자리에 다른 컨텐츠 카드 (alt_title + alt_body) 표시. 사용자 제품의
     비슷한 강점이나 핵심 메시지를 한국어로 1~2문장.
3) **skip**: 사용자 제품 정보 부재 또는 panel 의 정보가 swap 의도와 무관 (예: 한샘
   브랜드 광고, 라이프스타일 제3자 협찬 등) → 출력 panel 에서 건너뜀.

원칙:
- 사용자 제품이 다른 카테고리면 보수적으로 bypass.
- 사용자가 명시한 feature 가 한샘과 다르면 bypass 또는 alt 컨텐츠로.
- match 결정 시 단순히 카테고리 일치 외에 panel 의 강조 의도가 사용자 제품으로 표현
  가능해야 한다.

출력은 strict JSON.
"""


USER_TEMPLATE = """\
=== TASK ===
이 한샘 panel 의 swap 적합도를 판정하라.

=== Panel context ===
panel_idx: {panel_idx}
panel_class: {panel_class}
spatial_layout: {spatial_layout}
elements: {elements_block}
text_zones: {text_zones_block}

=== 한샘 원본 제품 ===
{hanssem_name}
(이미지 첨부됨 — IMAGE H)

=== 사용자 제품 ===
{user_product_name}
spec: {user_spec_block}
feature_descriptions:
{user_features_block}
color_options: {user_color_block}
model_options: {user_model_block}

=== 출력 schema (strict JSON) ===
{{
  "verdict": "match|bypass|skip",
  "hanssem_feature": "이 panel 이 강조하는 한샘 제품 feature 한 줄",
  "user_has_it": "yes|partial|no",
  "reasoning": "한국어 1~2문장 — 왜 match/bypass/skip 인가",
  "alt_title": "(bypass 시) 사용자 제품 강조 메시지 헤더 - 짧고 강함",
  "alt_body": "(bypass 시) 사용자 제품 강점/특징 1~3문장",
  "overlay_label": "(bypass 시) 우상단 작은 라벨 (예: '밀로는 다른 강점')"
}}
"""


def _format_elements(elements: list[dict]) -> str:
    if not elements:
        return "(none)"
    return "; ".join(f"{e.get('role','?')}@{e.get('position','?')}" for e in elements[:8])


def _format_text_zones(zones: list[dict]) -> str:
    if not zones:
        return "(none)"
    return "; ".join(f"{z.get('region','?')}: {z.get('content','')[:60]}" for z in zones[:6])


def _format_features(product_input: dict) -> str:
    fd = product_input.get("feature_descriptions", {}) or {}
    lines = []
    for key, val in fd.items():
        if val:
            lines.append(f"- {key}: {str(val)[:240]}")
    return "\n".join(lines) or "(none)"


def _format_colors(product_input: dict) -> str:
    co = product_input.get("color_options_detail", []) or []
    if not co:
        return "(none)"
    return ", ".join(f'"{c.get("name","")}"' for c in co)


def _format_models(product_input: dict) -> str:
    mo = product_input.get("model_options", []) or []
    if not mo:
        return "(none)"
    return ", ".join(f"{m.get('name','')} ({m.get('dimensions','')})" for m in mo)


def resolve_panel(
    openai_client: Any,
    vision_model: str,
    panel: dict,
    panel_image_path: Path,
    hanssem_name: str,
    product_input: dict,
    data_uri_fn,
) -> dict:
    panel_idx = panel.get("panel_idx", 0)
    user_prompt = USER_TEMPLATE.format(
        panel_idx=panel_idx,
        panel_class=panel.get("panel_class", "other"),
        spatial_layout=panel.get("spatial_layout", "")[:600],
        elements_block=_format_elements(panel.get("elements", []) or []),
        text_zones_block=_format_text_zones(panel.get("text_zones", []) or []),
        hanssem_name=hanssem_name,
        user_product_name=product_input.get("product_name", "unknown"),
        user_spec_block=json.dumps(product_input.get("spec", {}), ensure_ascii=False),
        user_features_block=_format_features(product_input),
        user_color_block=_format_colors(product_input),
        user_model_block=_format_models(product_input),
    )
    content = [
        {"type": "text", "text": user_prompt},
        {"type": "text", "text": "IMAGE H (한샘 panel):"},
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
    out = json.loads(resp.choices[0].message.content or "{}")
    out["panel_idx"] = panel_idx
    if out.get("verdict") not in ("match", "bypass", "skip"):
        out["verdict"] = "match"
    out.setdefault("hanssem_feature", "")
    out.setdefault("user_has_it", "yes")
    out.setdefault("reasoning", "")
    out.setdefault("alt_title", "")
    out.setdefault("alt_body", "")
    out.setdefault("overlay_label", "")
    # match면 alt 필드 비움
    if out["verdict"] == "match":
        out["alt_title"] = ""
        out["alt_body"] = ""
        out["overlay_label"] = ""
    return out


def resolve_all_panels(
    openai_client: Any,
    vision_model: str,
    panels: list[dict],
    template_dir: Path,
    hanssem_name: str,
    product_input: dict,
    data_uri_fn,
    cover_panel: dict | None = None,
) -> dict:
    """모든 panel + cover에 대해 mismatch resolve."""
    resolutions = []
    if cover_panel is not None:
        cover_img = template_dir / "_cover_1000.jpg"
        if not cover_img.exists():
            cover_img = next(template_dir.glob("_cover*.*"), None)
        if cover_img and cover_img.exists():
            cover_panel = {**cover_panel, "panel_idx": 0}
            r = resolve_panel(
                openai_client, vision_model, cover_panel, cover_img,
                hanssem_name, product_input, data_uri_fn,
            )
            resolutions.append(r)
    for panel in panels:
        pid = panel.get("panel", "")
        if pid == "cover" or "error" in panel:
            continue
        idx = panel.get("panel_idx")
        if idx is None:
            continue
        ppath = next(template_dir.glob(f"panel_{idx:02d}.*"), None)
        if not ppath:
            continue
        r = resolve_panel(
            openai_client, vision_model, panel, ppath,
            hanssem_name, product_input, data_uri_fn,
        )
        resolutions.append(r)
    resolutions.sort(key=lambda r: r.get("panel_idx", 999))
    return {"resolutions": resolutions}

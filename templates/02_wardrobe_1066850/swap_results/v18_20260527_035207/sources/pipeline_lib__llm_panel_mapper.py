"""LLM 기반 panel → ref 자원 매핑 — 71_map_panel_refs.py 의 if/elif 룰을 대체.

핵심 idea:
- panel의 layout/spatial/elements + 사용자 제품의 분류된 자원 목록을 모두 LLM에게 보여주고
  "이 panel을 swap 할 때 image_urls 슬롯에 어떤 자원을 보내야 하는가?"를 직접 결정.
- 사용자 제품 카테고리(소파/책상/의자/수납장 등) 무관하게 generalizable.
- 매핑 결정은 panel 컨텍스트와 가용 자원 양쪽을 모두 보고 판단. 카테고리에 없는 슬롯
  (예: 책상 panel에 컬러 swatch가 없으면 그 슬롯을 skip)도 자동으로 처리됨.

출력 schema (한 panel 분):
{
  "ref_keys": ["main_front", "detail_legs", ...],   # 호출자가 keys → URL로 변환
  "rationale": "이 panel은 측면 강조라 main_side + arm 디테일 2장 우선...",
  "skipped_categories": ["color_variant"],          # 이 panel에는 안 맞아서 뺀 카테고리
}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_REFS_PER_PANEL = 6

SYSTEM_PROMPT = """\
당신은 가구/생활용품의 detail-page swap 파이프라인에서 panel-level reference selector
역할을 맡는다. 한국 가구 detail page panel 한 장을 사용자 제품 이미지로 교체할 때
image_urls 슬롯에 어떤 자원을 보내야 가장 정확한 결과가 나올지 결정한다.

판단 기준:
1) panel의 spatial_layout, elements, panel_class 를 보고 panel이 무엇을 강조하는지 파악
2) 사용자 제품의 분류된 자원 (file → category + subject + reasoning) 중에서 그 panel을
   재현하는데 직접적으로 도움 되는 자원만 골라낸다
3) panel과 무관한 자원(예: 책상 panel에 소파의 다리 디테일)은 보내지 않는다 —
   그게 hallucination을 막는 핵심
4) 동일 카테고리에 중복 자원이 있어도 angle/subject가 다르면 활용한다 (panel이 그
   각도를 요구할 때만)
5) main_view 1장은 거의 모든 panel에서 anchor 역할로 유익함 — 단 panel이 명백히
   부분 디테일/룰북/소재 단독이면 제외 가능
6) 한 panel당 ref 수는 1~6장 사이가 적정. 너무 많으면 attention 분산.

출력은 strict JSON. 이유(rationale)도 한국어로 한두 문장 짧게.
"""

USER_PROMPT_TEMPLATE = """\
=== TASK ===
이 panel을 사용자 제품으로 swap 할 때 image_urls 에 보낼 자원을 결정하라.

=== PANEL CONTEXT ===
panel_id: {panel_id}
panel_class: {panel_class}
spatial_layout: {spatial_layout}
elements:
{elements_block}

=== 사용자 제품 정보 ===
제품명: {product_name}
핵심 특징 (한 줄):
{product_essence}

=== 가용 자원 (assets) ===
모든 자원은 keys로 식별된다. 출력의 ref_keys는 이 keys 중에서 골라야 한다.

{assets_block}

=== 카테고리 통계 ===
{category_stats}

=== 출력 schema ===
{{
  "ref_keys": ["key1", "key2", ...],  // 최대 {max_refs}장, 순서 = image_urls 순서 (anchor가 1번)
  "rationale": "한국어 1~2 문장",
  "skipped_categories": ["..."]  // panel과 무관해서 의도적으로 뺀 카테고리
}}
"""


def _summarize_essence(product_input: dict) -> str:
    """product_input_v3.json 핵심을 한 단락으로 — token 절약."""
    pn = product_input.get("product_name", "")
    sp = product_input.get("spec", {})
    fd = product_input.get("feature_descriptions", {})
    mo = product_input.get("model_options", []) or []
    co = product_input.get("color_options_detail", []) or []
    parts = [pn]
    if sp:
        dims = f"{sp.get('width_cm','?')}×{sp.get('depth_cm','?')}×{sp.get('height_cm','?')}cm"
        parts.append(f"제원 {dims}")
    if mo:
        parts.append("모델 옵션: " + ", ".join(m.get("name", "") for m in mo))
    if co:
        parts.append("컬러: " + ", ".join(c.get("name", "") for c in co))
    if fd.get("overall_silhouette"):
        parts.append("실루엣: " + fd["overall_silhouette"][:160])
    if fd.get("cushion_connection"):
        parts.append("핵심 디테일: " + fd["cushion_connection"][:200])
    elif fd.get("structure"):
        parts.append("구조: " + fd["structure"][:160])
    return "  · " + "\n  · ".join(parts)


def build_assets_index(classification_items: list[dict], asset_root: str = "use_product") -> dict[str, dict]:
    """classification.json items → assets index (key → {path, category, subject, reasoning}).

    key 생성 규칙: filename 그대로 (확장자 제거 안 함). LLM이 직접 골라 호출자가
    URL로 변환할 수 있게.
    """
    assets: dict[str, dict] = {}
    for item in classification_items:
        fn = item.get("filename")
        if not fn:
            continue
        assets[fn] = {
            "path": f"{asset_root}/{fn}",
            "category": item.get("category", "other"),
            "subject": item.get("subject", ""),
            "confidence": item.get("confidence", 0),
            "reasoning": item.get("reasoning", ""),
        }
    return assets


def _format_assets_block(assets: dict[str, dict]) -> str:
    """LLM에 보여줄 자원 표 — 한 자원당 한 줄."""
    lines = []
    for key, meta in assets.items():
        lines.append(
            f"- {key}  [category={meta['category']}, subject={meta['subject']}, conf={meta['confidence']}]\n"
            f"    reason: {meta['reasoning'][:160]}"
        )
    return "\n".join(lines)


def _format_category_stats(assets: dict[str, dict]) -> str:
    counts: dict[str, int] = {}
    for meta in assets.values():
        counts[meta["category"]] = counts.get(meta["category"], 0) + 1
    return ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))


def _format_elements(elements: list[dict]) -> str:
    if not elements:
        return "  (none)"
    return "\n".join(
        f"  - {e.get('role','?')} @ {e.get('position','?')}: {e.get('description','')[:160]}"
        for e in elements
    )


def map_panel_refs(
    openai_client: Any,
    vision_model: str,
    panel: dict,
    assets: dict[str, dict],
    product_input: dict,
    panel_image_path: Path | None = None,
    data_uri_fn=None,
) -> dict:
    """단일 panel에 대해 LLM이 ref_keys를 결정.

    panel_image_path 와 data_uri_fn 둘 다 제공되면 panel 원본 이미지도 같이 보내서
    LLM이 시각으로 추가 검증.
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(
        panel_id=panel.get("panel", "?"),
        panel_class=panel.get("panel_class", "other"),
        spatial_layout=panel.get("spatial_layout", "") or "",
        elements_block=_format_elements(panel.get("elements", []) or []),
        product_name=product_input.get("product_name", ""),
        product_essence=_summarize_essence(product_input),
        assets_block=_format_assets_block(assets),
        category_stats=_format_category_stats(assets),
        max_refs=MAX_REFS_PER_PANEL,
    )

    content: list[dict] = [{"type": "text", "text": user_prompt}]
    if panel_image_path and data_uri_fn:
        content.append({"type": "text", "text": "panel 원본 이미지 (참고):"})
        content.append({"type": "image_url", "image_url": {"url": data_uri_fn(panel_image_path)}})

    resp = openai_client.chat.completions.create(
        model=vision_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_object"},
    )
    decision = json.loads(resp.choices[0].message.content or "{}")

    # 방어: 존재하는 key만 유지
    raw_keys = decision.get("ref_keys") or []
    valid_keys = [k for k in raw_keys if k in assets][:MAX_REFS_PER_PANEL]
    decision["ref_keys"] = valid_keys
    decision["ref_paths"] = [assets[k]["path"] for k in valid_keys]
    decision.setdefault("rationale", "")
    decision.setdefault("skipped_categories", [])
    return decision


def map_all_panels(
    openai_client: Any,
    vision_model: str,
    panels: list[dict],
    assets: dict[str, dict],
    product_input: dict,
    template_dir: Path | None = None,
    data_uri_fn=None,
    cover_panel: dict | None = None,
) -> dict:
    """모든 panel에 대해 매핑 수행 + cover까지 포함.

    반환: {"assets": {...}, "panels": {"cover": {...}, "panel_01.jpg": {...}, ...}}
    """
    out: dict[str, dict] = {}

    if cover_panel is not None:
        cover_img = None
        if template_dir:
            cand = list((template_dir).glob("_cover_*.jpg"))
            cover_img = cand[0] if cand else None
        decision = map_panel_refs(
            openai_client, vision_model, cover_panel, assets, product_input,
            panel_image_path=cover_img, data_uri_fn=data_uri_fn,
        )
        out["cover"] = {
            "panel_idx": 0,
            "panel_class": cover_panel.get("panel_class", "intro_hero"),
            **decision,
            "ref_count": len(decision["ref_keys"]),
        }

    for panel in panels:
        pid = panel.get("panel", "")
        if not pid or pid == "cover" or "error" in panel:
            continue
        idx = panel.get("panel_idx")
        if idx is None:
            continue
        panel_img = None
        if template_dir:
            cand = list(template_dir.glob(f"panel_{idx:02d}.*"))
            panel_img = cand[0] if cand else None
        decision = map_panel_refs(
            openai_client, vision_model, panel, assets, product_input,
            panel_image_path=panel_img, data_uri_fn=data_uri_fn,
        )
        out[pid] = {
            "panel_idx": idx,
            "panel_class": panel.get("panel_class"),
            **decision,
            "ref_count": len(decision["ref_keys"]),
        }
    return {
        "assets": {k: v["path"] for k, v in assets.items()},
        "assets_meta": assets,
        "panels": out,
    }

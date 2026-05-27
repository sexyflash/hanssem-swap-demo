"""Verifiable checklist 추출 — product_input의 산문을 binary 검증 항목 list로 변환.

사용자 비판 (panel_03 외):
"물병/티셔츠 보는 게 아니라 소파라서 챙겨야 할 여러 요소
(쿠션/제품 모양/특징/팔걸이/방석/시접/연결구조 등)가
모든 단계(전처리/생성/QA)에 일관되게 강제돼야 한다"

→ product_input.feature_descriptions 산문 정보를 LLM이 검증 가능한 binary item list로
   재구성. 각 item마다 "어느 panel/어느 view에서 검증 가능한지" 메타가 붙음. QA는
   해당 panel에 적용 가능한 item만 골라 항목별 채점.

generalizable:
- 카테고리(소파/책상/의자/수납장 등)도 LLM이 product_name + 정보로 추론
- 카테고리별로 일반적인 카테고리 체크포인트도 자동 포함 (소파라면 다리/팔걸이/쿠션/등받이/시접;
  책상이라면 상판/다리/서랍/하부 결합; 의자라면 등받이/좌판/팔걸이/다리)

출력 schema:
{
  "category": "sofa" | "desk" | "chair" | "wardrobe" | "shelf" | ...,
  "category_check_axes": ["legs", "arms", "seat_cushion", "back_cushion", "seam", "frame", "fabric", ...],
  "items": [
    {
      "id": "legs_count_4",
      "description_ko": "다리는 정확히 4개 (모서리 4, 중앙 없음)",
      "check_question_ko": "결과 B에서 frame에 보이는 다리 개수가 정확히 4개인가? 중앙 5번째 다리는 없는가?",
      "expected": "다리 4개, 중앙 X",
      "applicable_panel_classes": ["intro_hero", "product_shot", "lifestyle_scene",
                                    "detail_close_up", "structure_chart", "module_lineup", "color_option"],
      "applicable_views": ["front", "side", "angle"],
      "severity": "critical" | "important" | "minor",
      "source_field": "feature_descriptions.legs_detail",
      "axis": "legs"
    },
    ...
  ]
}
"""
from __future__ import annotations

import json
from typing import Any


SYSTEM_PROMPT = """\
당신은 제품 detail-page swap 파이프라인의 VERIFIABLE CHECKLIST EXTRACTOR다. 사용자 제품
정보를 받아, vision QA 가 결과 이미지에서 binary 검증 가능한 항목 list로 재구성한다.

★ 핵심 원칙 (사용자 결정):
   "제품 왜곡(distortion) 0건 + 95% 만족이면 PASS. 구도(composition)는 trust."

따라서 각 item을 다음 3가지 category 중 하나로 정확히 분류한다:

═══════════════════════════════════════════════════════════
category: "distortion"  (★ 가장 중요 — retry trigger의 유일한 근거)
═══════════════════════════════════════════════════════════
"제품 정체성 자체"를 결정하는 항목.
- 카테고리 결정 (예: 가죽 vs 패브릭, 사각 vs 라운드 프레임)
- 구조 정체성 (다리 개수/배치, 팔걸이 형태, 등쿠션 개수, 쿠션 연결 구조)
- 제품 유무 항목 (헤드레스트가 있어야/없어야 한다)
- 컬러 옵션 (사용자가 제공한 정확한 한글명만 사용)
- 모델/사이즈 정합 (lineup count 정확 등)

→ 이 항목들은 image generation 모델로 안정적으로 표현 가능해야 한다.
   너무 미세한 디테일은 distortion이 아니다.

═══════════════════════════════════════════════════════════
category: "detail"  (생성 모델이 잡기 어려운 fine-grained)
═══════════════════════════════════════════════════════════
"있으면 좋지만 미세해서 image gen이 안정적으로 잡지 못하는" 항목.
- 시접 종류 (나이프 엣지 vs 플랜지 vs 파이핑 같은 봉제 디테일)
- 쿠션 미세 곡률 (살짝 볼록한 크라운, 앞엣날 말림 등)
- 패브릭 직조 결 (멜란지 톤 강도)
- 작은 라벨/지퍼 위치

→ 이 항목들은 score에는 영향 있지만 retry trigger가 아니다.
   사용자가 좋은 prompt + 좋은 model 썼다고 trust 하기로 함.

═══════════════════════════════════════════════════════════
category: "forbidden"  (★ NEVER — distortion과 동일하게 강제 retry)
═══════════════════════════════════════════════════════════
"있어서는 안 되는 invented feature".
- 사용자가 명시 안 한 헤드레스트/USB/리클라이너/tufting/V자 다리/중앙 5번째 다리/한샘 컬러명 잔존 등

→ 1개라도 발견 시 retry. distortion과 동격.

═══════════════════════════════════════════════════════════

각 item 출력 schema:
{
  "id": "snake_case_id",
  "description_ko": "...",
  "check_question_ko": "결과 B 에서 ...?",
  "expected": "...",
  "applicable_panel_classes": [...],
  "applicable_views": [...],
  "category": "distortion" | "detail" | "forbidden",
  "axis": "legs|arms|seat_cushion|back_cushion|seam|frame|fabric|color|connection|size|...",
  "generation_feasibility": "high" | "medium" | "low"  // image gen으로 표현 가능성
}

규칙:
1) 카테고리(소파/책상/의자/수납장 등) 추론. category_check_axes 자동 포함.
2) 사용자 정보에서 항목 추출. distortion 항목은 5~10개, detail은 5~15개, forbidden은 3~10개.
3) generation_feasibility:
   - high: 정면 silhouette/숫자/색/큰 구조 → 거의 항상 표현됨
   - medium: 측면 디테일/구조 항목
   - low: 시접 종류, 미세 봉제, fine-grained 표면 디테일
4) 사용자가 명시 안 한 feature는 모두 forbidden 으로 자동 추가 (헤드레스트 없으면 no_headrest).
5) 정량 항목 (사이즈/제원)은 chart panel에서만.

출력은 strict JSON.
"""


USER_PROMPT_TEMPLATE = """\
=== TASK ===
이 사용자 제품에 대해 vision QA가 항목별 binary 검증할 수 있는 verifiable checklist를 작성하라.

=== 사용자 제품 ===
제품명: {product_name}

spec: {spec_json}

feature_descriptions:
{feature_block}

color_options:
{color_block}

model_options:
{model_block}

certifications: {certifications}

intro_full: {intro_full}

=== 출력 schema (strict JSON) ===
{{
  "product_category": "sofa|desk|chair|wardrobe|shelf|...",
  "category_check_axes": ["..."],
  "items": [
    {{
      "id": "snake_case_id",
      "description_ko": "...",
      "check_question_ko": "결과 B에서 ...?",
      "expected": "...",
      "applicable_panel_classes": ["intro_hero", "product_shot", "lifestyle_scene",
                                    "detail_close_up", "size_chart", "structure_chart",
                                    "color_option", "module_lineup", "material_swatch"],
      "applicable_views": ["front", "side", "angle", "close-up"],
      "category": "distortion|detail|forbidden",
      "generation_feasibility": "high|medium|low",
      "source_field": "feature_descriptions.<key> | spec | color_options | model_options | intro",
      "axis": "legs|arms|seat_cushion|back_cushion|seam|frame|fabric|color|connection|size|..."
    }}
  ]
}}

소파면 다음 distortion 축들은 반드시 포함:
- legs (개수/배치 → distortion)
- arms (큰 형태, 안쪽 보조쿠션 유무 → distortion / 시접 → detail)
- seat_cushion (개수/연결 구조 → distortion / 미세 곡률/시접 → detail)
- back_cushion (개수/타입 → distortion / 시접 → detail)
- frame (큰 형태 → distortion)
- fabric (가죽 vs 패브릭 → distortion / 직조 결 → detail)
- color (정확한 한글 컬러명 → distortion)
- connection (★ 보조쿠션 ↔ 좌방석 연결 → distortion)
- size (chart panel 한정 → distortion)

forbidden (있으면 안 됨):
- 헤드레스트 X, USB X, 리클라이너 X, V자 다리 X, 중앙 5번째 다리 X, 한샘 컬러명 잔존 X 등
"""


def _format_features(product_input: dict) -> str:
    fd = product_input.get("feature_descriptions", {}) or {}
    lines = []
    for key, val in fd.items():
        if val:
            lines.append(f"- {key}: {str(val)[:500]}")
    return "\n".join(lines) or "  (none)"


def _format_colors(product_input: dict) -> str:
    colors = product_input.get("color_options_detail", []) or []
    if not colors:
        return "  (none)"
    return "\n".join(f'  · "{c.get("name","")}": {c.get("description","")[:200]}' for c in colors)


def _format_models(product_input: dict) -> str:
    models = product_input.get("model_options", []) or []
    if not models:
        return "  (none)"
    return "\n".join(
        f"  · {m.get('name','')} ({m.get('dimensions','')})"
        + (" [selected]" if m.get("selected") else "")
        for m in models
    )


def extract_checklist(
    openai_client: Any,
    text_model: str,
    product_input: dict,
) -> dict:
    """product_input 으로부터 verifiable checklist 추출."""
    user_prompt = USER_PROMPT_TEMPLATE.format(
        product_name=product_input.get("product_name", ""),
        spec_json=json.dumps(product_input.get("spec", {}), ensure_ascii=False),
        feature_block=_format_features(product_input),
        color_block=_format_colors(product_input),
        model_block=_format_models(product_input),
        certifications=str(product_input.get("certifications_full", ""))[:600],
        intro_full=str(product_input.get("intro_full", ""))[:600],
    )
    resp = openai_client.chat.completions.create(
        model=text_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    out = json.loads(resp.choices[0].message.content or "{}")
    # 호환: 옛 "category" 필드를 product_category 로
    if "product_category" not in out and "category" in out:
        out["product_category"] = out.pop("category")
    out.setdefault("product_category", "unknown")
    # 호환 alias
    out["category"] = out.get("product_category", "unknown")
    out.setdefault("category_check_axes", [])
    out.setdefault("items", [])
    # 각 item에 누락 필드 default 채움
    for it in out["items"]:
        # 옛 severity → category 매핑
        if "category" not in it and "severity" in it:
            sev = it.get("severity")
            it["category"] = "distortion" if sev == "critical" else "detail"
        it.setdefault("category", "detail")
        it.setdefault("generation_feasibility", "medium")
    return out


def select_items_for_panel(
    checklist: dict,
    panel_class: str,
    panel_spatial: str = "",
) -> list[dict]:
    """panel_class + spatial cue 기반으로 적용 가능한 item만 필터링."""
    items = checklist.get("items", []) or []
    selected: list[dict] = []
    for item in items:
        applicable_classes = item.get("applicable_panel_classes") or []
        if applicable_classes and panel_class not in applicable_classes:
            continue
        selected.append(item)
    return selected


def critical_distortion_items(items: list[dict]) -> list[dict]:
    """distortion + forbidden — retry trigger 근거."""
    return [it for it in (items or []) if it.get("category") in ("distortion", "forbidden")]


def detail_items(items: list[dict]) -> list[dict]:
    """detail — score 영향 있지만 retry trigger 아님."""
    return [it for it in (items or []) if it.get("category") == "detail"]

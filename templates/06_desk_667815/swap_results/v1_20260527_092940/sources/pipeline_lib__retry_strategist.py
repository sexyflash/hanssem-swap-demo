"""3-stage retry 전략 — 사용자가 직접 설계한 흐름.

attempt 1: initial generation (essence + panel refs + edit_block)
attempt 2 (retry stage 1 — REPLAN):
   QA report를 그대로 append 하는 게 아니라, LLM이 QA를 분석해서 '놓친 부분을 어떻게
   보완해야 하는지'에 대한 해설을 작성하고 prompt를 재작성. 텍스트 append X.
attempt 3 (retry stage 2 — BEST-OF-2 PAINT EDIT):
   앞선 두 번의 실패 결과 중 점수가 더 좋은 이미지를 base로 삼고, '그 위에 무엇을
   부분 수정해야 하는지' painting/edit prompt 생성. fal-ai/gpt-image-2/edit에 그
   결과 이미지를 IMAGE 1 (edit base)로 보내고 보정 directive를 prompt로.
attempt 4 (retry stage 3 — ESSENCE + SMART SHEET + CUMULATIVE):
   원본 essence + smart sheet 이미지 + 누적된 모든 보완책을 합쳐 LLM이 최종 prompt
   재작성. smart sheet가 panel별 가이드를 담고 있으므로 ref에 추가.

retry_strategist는 LLM 호출로 prompt를 재작성하는 책임만 진다. 실제 fal 호출/QA는
호출자(pipeline)가 처리.
"""
from __future__ import annotations

import json
from typing import Any


# ────────────────────────────── stage 1: REPLAN ──────────────────────────────

REPLAN_SYSTEM = """\
당신은 한국 가구/생활용품 swap 파이프라인의 RETRY ANALYST다. 직전 시도의 prompt와 QA
결과를 받아, 무엇을 놓쳤고 왜 그랬는지 분석한 뒤, '다음 시도에서 어떻게 보완할지'에
대한 구체적 해설과 함께 prompt를 재작성한다.

원칙:
1) QA의 specific_failures를 그대로 텍스트로 붙여 넣지 말 것. LLM이 직접 원인을 추론.
2) 각 failure에 대해 '왜 발생했나' + '다음 시도에서 prompt/ref를 어떻게 조정해야
   재발 방지가 되는가'를 짧게 적고, 그 보완책을 prompt 본문에 자연스럽게 녹여낸다.
3) 이전 prompt에서 명확했던 PRESERVE/NEVER는 유지하되, 실패한 항목을 첫 번째 위치로
   끌어올려 강조한다.
4) 텍스트만 늘리지 말고, 필요하면 '아래 reference는 panel의 X 부분을 정확히 표현하니
   결과에서 X를 그대로 가져와라' 같은 구체적 anchor 문구를 prompt에 추가.

출력 schema:
{
  "diagnosis": "직전 실패의 근본 원인 분석 (한국어 2~3문장)",
  "patches": ["보완책 1", "보완책 2", ...],
  "new_prompt": "재작성된 prompt 전체 (그대로 fal에 보낼 수 있어야 함)"
}
"""

REPLAN_USER_TEMPLATE = """\
=== PANEL ===
panel_id: {panel_id} · class: {panel_class}
spatial_layout: {spatial_layout}

=== 직전 prompt (attempt {prev_attempt}) ===
{prev_prompt}

=== 직전 QA 결과 ===
{qa_json}

=== 사용자 제품 essence ===
{product_essence}

=== 가용 reference keys (이번 panel에 매핑된 것) ===
{ref_keys}

=== 출력 schema ===
JSON: {{"diagnosis": "...", "patches": ["..."], "new_prompt": "..."}}
"""


def replan_prompt(
    openai_client: Any,
    text_model: str,
    panel: dict,
    prev_prompt: str,
    prev_qa: dict,
    product_essence: str,
    ref_keys: list[str],
    prev_attempt: int,
) -> dict:
    """attempt 2 — 분석 기반 prompt 재작성."""
    user_prompt = REPLAN_USER_TEMPLATE.format(
        panel_id=panel.get("panel", "?"),
        panel_class=panel.get("panel_class", "other"),
        spatial_layout=panel.get("spatial_layout", "") or "",
        prev_prompt=prev_prompt,
        qa_json=json.dumps(prev_qa, ensure_ascii=False, indent=2)[:3000],
        product_essence=product_essence[:1200],
        ref_keys=", ".join(ref_keys),
        prev_attempt=prev_attempt,
    )
    resp = openai_client.chat.completions.create(
        model=text_model,
        messages=[
            {"role": "system", "content": REPLAN_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    out = json.loads(resp.choices[0].message.content or "{}")
    out.setdefault("diagnosis", "")
    out.setdefault("patches", [])
    out.setdefault("new_prompt", prev_prompt)
    return out


# ───────────────────────── stage 2: BEST-OF-2 PAINT EDIT ─────────────────────

PAINT_EDIT_SYSTEM = """\
당신은 한국 가구/생활용품 swap 파이프라인의 PAINT-EDIT 작성자다. 앞선 두 번의 시도
결과 중 점수가 가장 높은 이미지가 base로 주어진다. 이 base 이미지의 잘된 부분은 그대로
보존하고, QA가 지적한 부분만 부분 수정하도록 painting/edit prompt를 작성한다.

원칙:
1) base를 통째로 다시 그리지 말 것 — "이 부분만 X로 수정" 식 부분 인페인팅 directive.
2) base의 카메라 각도/배경/조명/레이아웃은 100% 보존을 명시.
3) 두 번의 시도 모두에서 동일하게 발생한 문제는 더 강력히 강조 (반복 실패 패턴).
4) 어떤 부분을 어떻게 부분 수정할지 한 부분당 1~2문장으로 명확하게.
5) prompt 첫 줄에 'This is a PAINT EDIT — preserve base wholesale except listed regions'.

출력 schema:
{
  "base_attempt_idx": int,
  "base_score": int,
  "regions_to_edit": [{"region": "...", "change": "..."}, ...],
  "paint_prompt": "fal에 그대로 보낼 painting/edit prompt 전체"
}
"""

PAINT_EDIT_USER_TEMPLATE = """\
=== PANEL ===
panel_id: {panel_id} · class: {panel_class}

=== 앞선 시도 두 개의 QA 결과 ===
attempt {a1_idx} (score={a1_score}):
{a1_qa}

attempt {a2_idx} (score={a2_score}):
{a2_qa}

=== 사용자 제품 essence ===
{product_essence}

=== 출력 ===
점수 더 높은 attempt를 base로 선정. JSON 응답:
{{"base_attempt_idx": ..., "base_score": ..., "regions_to_edit": [...], "paint_prompt": "..."}}
"""


def paint_edit_prompt(
    openai_client: Any,
    text_model: str,
    panel: dict,
    attempts: list[dict],
    product_essence: str,
) -> dict:
    """attempt 3 — 두 번 실패 중 best를 골라 부분 수정 paint prompt 작성.

    attempts 는 직전 두 시도 dict (각 'image', 'product_score', 'specific_failures', ...).
    """
    a1, a2 = attempts[0], attempts[1]
    user_prompt = PAINT_EDIT_USER_TEMPLATE.format(
        panel_id=panel.get("panel", "?"),
        panel_class=panel.get("panel_class", "other"),
        a1_idx=a1.get("attempt", 1),
        a1_score=a1.get("product_score", 0),
        a1_qa=json.dumps({k: a1.get(k) for k in ("specific_failures", "reference_influences", "leg_count_in_B", "color_labels_in_B", "color_hallucinations")}, ensure_ascii=False)[:1200],
        a2_idx=a2.get("attempt", 2),
        a2_score=a2.get("product_score", 0),
        a2_qa=json.dumps({k: a2.get(k) for k in ("specific_failures", "reference_influences", "leg_count_in_B", "color_labels_in_B", "color_hallucinations")}, ensure_ascii=False)[:1200],
        product_essence=product_essence[:1200],
    )
    resp = openai_client.chat.completions.create(
        model=text_model,
        messages=[
            {"role": "system", "content": PAINT_EDIT_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    out = json.loads(resp.choices[0].message.content or "{}")
    # base 선정 — LLM이 안 골랐으면 점수 비교로 fallback
    base_idx = out.get("base_attempt_idx")
    if base_idx not in (a1.get("attempt"), a2.get("attempt")):
        base_idx = a1.get("attempt") if a1.get("product_score", 0) >= a2.get("product_score", 0) else a2.get("attempt")
    out["base_attempt_idx"] = base_idx
    out.setdefault("paint_prompt", "Paint edit the input image: preserve composition entirely; correct the issues noted by QA.")
    out.setdefault("regions_to_edit", [])
    return out


# ───────────────── stage 3: ESSENCE + SMART SHEET + CUMULATIVE ────────────────

CUMULATIVE_SYSTEM = """\
당신은 한국 가구/생활용품 swap 파이프라인의 FINAL ATTEMPT 작성자다. 앞선 모든 시도가
실패했을 때 마지막 회복 시도용 prompt를 작성한다. 이 시도에서는:
1) 사용자 제품의 essence (원본 product_input 응축)
2) 미리 만든 PRODUCT GUIDE smart sheet (별도 reference 이미지로 첨부됨)
3) 앞선 모든 attempt의 누적 보완책

세 가지를 모두 합쳐서 fal에 보낼 prompt를 재작성한다.

원칙:
1) 누적 보완책 (앞선 patches/diagnosis)을 모두 통합해 새로운 prompt 구조로 응축. 같은
   실수를 반복하지 않도록 명시.
2) smart sheet 이미지가 reference로 들어옴을 prompt에 명시:
   "SMART SHEET image는 panel별 가이드를 담은 메타 자료. 결과로 복제 X, 그 안의 정보만 활용."
3) 이번 시도의 핵심 목표 한 줄을 prompt 최상단에 굵게: "제품의 비전(핵심 시각적 특징)이
   정말로 결과 이미지에 들어가야 한다."
4) PRESERVE / NEVER 박스 형태로 마지막에 한 번 더 명시.

출력 schema:
{
  "cumulative_diagnosis": "앞선 모든 실패의 공통 원인 (한국어 3~4문장)",
  "merged_patches": ["...", "..."],
  "final_prompt": "fal에 보낼 최종 prompt (smart sheet ref가 동봉됨을 가정)"
}
"""

CUMULATIVE_USER_TEMPLATE = """\
=== PANEL ===
panel_id: {panel_id} · class: {panel_class}
spatial_layout: {spatial_layout}

=== 앞선 모든 시도의 누적 컨텍스트 ===
{prior_block}

=== 사용자 제품 essence (full) ===
{product_essence}

=== 사용자 제품 정량 정보 ===
{product_quant}

=== 이번 시도에 동봉될 SMART SHEET 정보 ===
{sheet_summary}

=== 출력 ===
JSON: {{"cumulative_diagnosis": "...", "merged_patches": [...], "final_prompt": "..."}}
"""


def cumulative_prompt(
    openai_client: Any,
    text_model: str,
    panel: dict,
    prior_attempts: list[dict],
    product_essence: str,
    product_quant: str,
    sheet_summary: str,
) -> dict:
    """attempt 4 — 누적 통합 + smart sheet 동봉 prompt."""
    prior_lines = []
    for a in prior_attempts:
        i = a.get("attempt")
        score = a.get("product_score", 0)
        fails = a.get("specific_failures", []) or []
        diag = a.get("retry_diagnosis", "")
        prior_lines.append(
            f"  attempt {i} score={score}\n"
            f"    failures: {json.dumps(fails, ensure_ascii=False)[:600]}\n"
            f"    diagnosis: {diag[:400]}"
        )
    user_prompt = CUMULATIVE_USER_TEMPLATE.format(
        panel_id=panel.get("panel", "?"),
        panel_class=panel.get("panel_class", "other"),
        spatial_layout=panel.get("spatial_layout", "") or "",
        prior_block="\n".join(prior_lines),
        product_essence=product_essence[:2200],
        product_quant=product_quant[:1200],
        sheet_summary=sheet_summary[:600],
    )
    resp = openai_client.chat.completions.create(
        model=text_model,
        messages=[
            {"role": "system", "content": CUMULATIVE_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    out = json.loads(resp.choices[0].message.content or "{}")
    out.setdefault("cumulative_diagnosis", "")
    out.setdefault("merged_patches", [])
    out.setdefault("final_prompt", "Final attempt — integrate essence + sheet + cumulative patches.")
    return out

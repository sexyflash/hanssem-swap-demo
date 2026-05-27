"""Anti-regression best-of-attempts selector.

사용자 비판:
"1번이 좋은데 cumulative가 더 망친다. retry가 좋은 결과를 깎아먹음."

→ MAX_ATTEMPTS 끝난 후, "qa" 결과 있는 attempts 중에서 LLM이 두 이미지씩 직접 비교 + 점수 메타도 보고 진정한 best를 고른다. 단순 product_score 최댓값은 calibration이 깨졌을 때 잘못된 final을 선정함.

알고리즘:
- attempts 중 verdict 'pass' 있으면 그 첫 attempt를 final
- 그 외엔 LLM judge — 점수 메타 + 두 이미지 직접 비교로 두 개 중 더 나은 것 선정 → 토너먼트
- 사용자 제품의 핵심 axis를 LLM에 명시해서 비교 기준으로 사용
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


JUDGE_SYSTEM = """\
당신은 한국 가구/생활용품 swap 파이프라인의 두 결과 비교 judge다. 두 후보 이미지를 보고
"사용자 제품(target)에 더 충실하고 한샘 panel layout과 더 일치하는" 쪽을 고른다.

원칙:
1) product_score / critical_fail_count 메타는 calibration이 깨졌을 수 있어 참고만.
   최종 판단은 직접 두 이미지 비교 + target 핵심 axis (category_check_axes) 기반.
2) 사용자 제품의 핵심 시각적 특징을 결과가 정말 보존하는지가 핵심.
3) layout이 한샘 C와 다른 grid/sheet 형태면 즉시 그 쪽은 탈락.
4) 동률이면 더 보수적인 attempt(앞선 stage) 선택 — retry가 망쳤을 가능성.

출력은 strict JSON.
"""


JUDGE_USER = """\
=== TASK ===
두 후보 중 사용자 제품(target)에 더 충실한 쪽을 골라라.

=== Panel ===
panel_id: {panel_id} · class: {panel_class}
spatial_layout: {spatial_layout}

=== 사용자 제품 ===
category: {category}
제품명: {product_name}
핵심 axis: {axes}

=== 후보 메타 ===
A (stage={stage_a}, attempt={att_a}, product_score={ps_a}, critical_fail={cf_a}):
  failures: {fails_a}
B (stage={stage_b}, attempt={att_b}, product_score={ps_b}, critical_fail={cf_b}):
  failures: {fails_b}

=== 출력 schema (strict JSON) ===
{{
  "winner": "A" | "B",
  "rationale_ko": "한국어 1~2문장",
  "tiebreaker_used": "score|axes|layout|stage_preference|other"
}}
"""


def _shorten(items, n=400):
    if not items:
        return "[]"
    s = json.dumps(items, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "..."


def judge_pair(
    openai_client: Any,
    vision_model: str,
    panel: dict,
    a_attempt: dict,
    b_attempt: dict,
    product_input: dict,
    checklist: dict,
    a_image_path: Path,
    b_image_path: Path,
    data_uri_fn,
) -> dict:
    user_prompt = JUDGE_USER.format(
        panel_id=panel.get("panel", "?"),
        panel_class=panel.get("panel_class", "?"),
        spatial_layout=panel.get("spatial_layout", "") or "",
        category=checklist.get("category", "unknown"),
        product_name=product_input.get("product_name", ""),
        axes=", ".join(checklist.get("category_check_axes", []) or []),
        stage_a=a_attempt.get("stage", "?"),
        att_a=a_attempt.get("attempt", "?"),
        ps_a=a_attempt.get("product_score", "?"),
        cf_a=a_attempt.get("critical_fail_count", "?"),
        fails_a=_shorten(a_attempt.get("specific_failures") or []),
        stage_b=b_attempt.get("stage", "?"),
        att_b=b_attempt.get("attempt", "?"),
        ps_b=b_attempt.get("product_score", "?"),
        cf_b=b_attempt.get("critical_fail_count", "?"),
        fails_b=_shorten(b_attempt.get("specific_failures") or []),
    )
    content = [
        {"type": "text", "text": user_prompt},
        {"type": "text", "text": "IMAGE A:"},
        {"type": "image_url", "image_url": {"url": data_uri_fn(a_image_path)}},
        {"type": "text", "text": "IMAGE B:"},
        {"type": "image_url", "image_url": {"url": data_uri_fn(b_image_path)}},
    ]
    resp = openai_client.chat.completions.create(
        model=vision_model,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_object"},
    )
    out = json.loads(resp.choices[0].message.content or "{}")
    if out.get("winner") not in ("A", "B"):
        out["winner"] = "A"
    return out


def _fail_count(a: dict) -> int:
    return (a.get("distortion_fail_count") or 0) + (a.get("forbidden_fail_count") or 0)


def select_best(
    openai_client: Any,
    vision_model: str,
    panel: dict,
    attempts: list[dict],
    product_input: dict,
    checklist: dict,
    image_dir: Path,
    data_uri_fn,
) -> dict:
    """attempts 중 verdict pass 있으면 그 첫 attempt 반환. 없으면 distortion/forbidden fail 적은 순으로 우선
    선정 후 동률이면 LLM judge.

    각 attempt dict는 'image' (파일명) 와 메타 포함.
    """
    scored = [a for a in attempts if isinstance(a, dict) and "image" in a and "product_score" in a]
    passers = [a for a in scored if a.get("verdict") == "pass"]
    if passers:
        return {"final": passers[0], "judge_log": [], "method": "first_passer"}

    if not scored:
        return {"final": attempts[-1] if attempts else None, "judge_log": [], "method": "none"}

    if len(scored) == 1:
        return {"final": scored[0], "judge_log": [], "method": "single"}

    # 1차 정렬: distortion + forbidden fail 적은 순. 동률이면 product_score 높은 순
    scored_sorted = sorted(
        scored,
        key=lambda a: (_fail_count(a), -(a.get("product_score", 0) or 0)),
    )
    top_fail = _fail_count(scored_sorted[0])
    tied_top = [a for a in scored_sorted if _fail_count(a) == top_fail]

    # 동률 fail count의 attempt가 1개면 그게 final
    if len(tied_top) == 1:
        return {"final": tied_top[0], "judge_log": [], "method": "fewest_distortion_fails"}

    # 여러 개 동률이면 LLM 토너먼트
    judge_log: list[dict] = []
    current = tied_top[0]
    for nxt in tied_top[1:]:
        a_path = image_dir / current["image"]
        b_path = image_dir / nxt["image"]
        verdict = judge_pair(
            openai_client, vision_model, panel,
            current, nxt, product_input, checklist,
            a_path, b_path, data_uri_fn,
        )
        judge_log.append({
            "a_attempt": current.get("attempt"),
            "b_attempt": nxt.get("attempt"),
            "winner": verdict["winner"],
            "rationale_ko": verdict.get("rationale_ko", ""),
            "tiebreaker_used": verdict.get("tiebreaker_used", ""),
        })
        current = current if verdict["winner"] == "A" else nxt
    return {"final": current, "judge_log": judge_log, "method": "tournament_distortion_tied"}

"""QA engine — checklist 기반 항목별 채점 + 모든 ref 동봉 + payload 저장.

사용자 비판 (v16 검수 후):
1) anchor 1장만 QA에 보냄 → 측면/디테일 검증 불가 → "모든 ref + 결과 + 원본을 보내라"
2) 100점인데 명확한 결함 / 65점인데 충분히 좋음 → calibration 깨짐
3) 카테고리 특화 체크리스트 부재 → 소파면 소파 항목으로 검증
4) QA payload 가시화 안 됨 → run_dir/qa_payloads/ 에 sidecar JSON 저장

새 QA 동작:
- 입력 이미지: A_i (panel ref 전부, 라벨 포함) + B (swap 결과) + C (한샘 원본 panel)
- LLM에 verifiable checklist를 그대로 제시 + 각 항목 binary 채점 강제
- product_score = critical pass 비율 (×100) — 산문 점수 X
- composition_score = layout vs C 비교 (별도)
- verdict: critical fail >= 1 → retry, 그 외 product_score / composition_score 기준
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SYSTEM_PROMPT = """\
당신은 한국 가구/생활용품 detail-page swap 결과의 QA 검수자다. 사용자가 결정한 기준에 따라
판정한다:

★ "제품 왜곡(distortion) 0건 + 95% 만족이면 PASS. 구도(composition)는 trust."

따라서 너의 일은 **제품 정체성/왜곡** 항목 (category=distortion or forbidden) 에 집중하는 것.
detail 항목 (시접/미세 곡률 등)은 ranking용일 뿐 retry trigger가 아니다.

원칙:
1) reference 이미지 (A_1, A_2, ...) 는 panel별 매핑된 user product 사진. 그 조합으로
   정답 형태를 파악하라.
2) C 는 한샘 원본 panel — composition reference. 별도 채점.
3) 각 item에 (pass | fail | not_visible) 판정:
   - distortion 항목은 panel이 검증 가능한 영역이면 fail 또는 pass. 핵심인데 안 보이면 fail.
     (예: 좌방석 close-up에서 좌방석 형태가 milo와 다르면 fail.)
   - detail 항목은 image gen 모델의 한계를 인정해 너무 strict하지 마라:
     · 미세 시접/봉제/직조 결 같은 항목이 '약간 다르게' 표현됐다면 pass
     · 정말 명백히 잘못된 경우만 fail
     · generation_feasibility=low 인 항목은 fail 매기는 게 매우 보수적
   - forbidden 항목은 매우 strict — 그 invented feature가 보이면 fail.
4) hallucinations[] 는 사용자 제품에 없는 invented feature 발견 시. (헤드레스트/USB 등)
5) composition_score 는 0~100 으로 채점 (보고용 — verdict에 영향 X).
6) 거짓 통과 금지 — 명백히 잘못된 distortion/forbidden은 fail. 단 detail에선 관대.
7) 출력의 product_score 는 무시됨. 호출자가 weighted 재계산.

출력은 strict JSON.
"""


USER_PROMPT_TEMPLATE = """\
=== TASK ===
이 swap 결과(B)를 사용자 제품의 verifiable checklist로 채점하라.

=== 사용자 제품 ===
category: {category}
제품명: {product_name}
핵심 axis: {category_check_axes}

=== 첨부 이미지 ===
{image_index_block}

=== Panel 컨텍스트 ===
panel_id: {panel_id}
panel_class: {panel_class}
spatial_layout: {spatial_layout}

=== 적용 가능한 CHECKLIST ITEMS (이 panel에서 검증 가능) ===
각 item에 category(distortion/detail/forbidden)와 generation_feasibility 가 표시됨.
- distortion / forbidden: strict 채점 (제품 왜곡 검출이 사용자 핵심 요구)
- detail: image gen 한계 인정 → 명백한 차이만 fail, 모호하면 pass
- generation_feasibility=low: 더욱 보수적으로 fail 매김 (미세 디테일)

{items_block}

=== 출력 schema (strict JSON) ===
{{
  "image_format": "single_product|lifestyle|chart_diagram|multi_panel_grid",
  "items_results": [
    {{
      "id": "...",
      "verdict": "pass|fail|not_visible",
      "reason_ko": "...",
      "category": "distortion|detail|forbidden",
      "generation_feasibility": "high|medium|low"
    }}
  ],
  "distortion_fail_count": int,
  "forbidden_fail_count": int,
  "composition_score": 0-100,
  "hallucinations": ["발견된 invented feature 한국어"],
  "specific_failures": ["distortion/forbidden fail 항목의 한국어 요약"],
  "notes_ko": "..."
}}

판정 가이드:
- distortion item: 다리 개수 / 가죽 vs 패브릭 / 보조쿠션 유무 / 컬러명 등 명백한 차이 → fail
- forbidden item: invented feature (헤드레스트 등) 발견 → fail
- detail item: 시접 종류 / 미세 곡률 / 직조 결 등이 약간 달라도 → pass (관대)
"""


def _format_items(items: list[dict]) -> str:
    if not items:
        return "  (none)"
    lines = []
    # distortion/forbidden 우선 표시
    order = {"forbidden": 0, "distortion": 1, "detail": 2}
    items_sorted = sorted(items, key=lambda it: order.get(it.get("category", "detail"), 3))
    for item in items_sorted:
        cat = item.get("category", item.get("severity", "?"))
        feas = item.get("generation_feasibility", "?")
        sid = item.get("id", "?")
        desc = item.get("description_ko", "")
        ques = item.get("check_question_ko", "")
        exp = item.get("expected", "")
        axis = item.get("axis", "")
        lines.append(
            f"- [{cat:>10}] [feas={feas}] id={sid} axis={axis}\n"
            f"    desc: {desc}\n"
            f"    expected: {exp}\n"
            f"    question: {ques}"
        )
    return "\n".join(lines)


def _format_image_index(ref_labels: list[str]) -> str:
    """LLM에 어느 이미지가 무엇인지 명시."""
    lines = []
    for i, lbl in enumerate(ref_labels, start=1):
        lines.append(f"  A_{i} = {lbl}")
    lines.append("  B = swap 결과 (채점 대상)")
    lines.append("  C = 한샘 원본 panel (composition reference)")
    return "\n".join(lines)


def evaluate(
    openai_client: Any,
    vision_model: str,
    panel: dict,
    swap_result: Path,
    panel_orig: Path,
    panel_ref_paths: list[Path],
    panel_ref_labels: list[str],
    checklist: dict,
    applicable_items: list[dict],
    data_uri_fn,
    payload_save_path: Path | None = None,
) -> dict:
    """
    panel_ref_paths/labels는 1:1 대응 — 보통 panel→ref LLM mapping의 결과.
    payload_save_path가 주어지면 호출 메타(보낸 이미지 list + 적용 item list)를 저장.
    """
    panel_id = panel.get("panel", "?")
    panel_class = panel.get("panel_class", "other")
    spatial = panel.get("spatial_layout", "") or ""

    items_block = _format_items(applicable_items)
    image_index_block = _format_image_index(panel_ref_labels)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        category=checklist.get("category", "unknown"),
        product_name=panel.get("_product_name", ""),
        category_check_axes=", ".join(checklist.get("category_check_axes", []) or []),
        image_index_block=image_index_block,
        panel_id=panel_id,
        panel_class=panel_class,
        spatial_layout=spatial,
        items_block=items_block,
    )

    # multipart content: prompt + 모든 ref + B + C
    content: list[dict] = [{"type": "text", "text": user_prompt}]
    for i, (p, lbl) in enumerate(zip(panel_ref_paths, panel_ref_labels), start=1):
        content.append({"type": "text", "text": f"IMAGE A_{i} = {lbl}:"})
        content.append({"type": "image_url", "image_url": {"url": data_uri_fn(p)}})
    content.append({"type": "text", "text": "IMAGE B (swap 결과 — 채점 대상):"})
    content.append({"type": "image_url", "image_url": {"url": data_uri_fn(swap_result)}})
    content.append({"type": "text", "text": "IMAGE C (한샘 원본 panel — composition reference):"})
    content.append({"type": "image_url", "image_url": {"url": data_uri_fn(panel_orig)}})

    resp = openai_client.chat.completions.create(
        model=vision_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_object"},
    )
    result = json.loads(resp.choices[0].message.content or "{}")

    # ── 새 calibration (사용자 결정: distortion 0건 + 95% 만족이면 pass, composition trust) ──
    items_results = result.get("items_results") or []

    # category 보정 — LLM이 옛 severity 형식으로 답했을 때 매핑
    for it in items_results:
        if "category" not in it:
            sev = it.get("severity")
            it["category"] = "distortion" if sev == "critical" else (
                "forbidden" if sev == "forbidden" else "detail"
            )
        it.setdefault("generation_feasibility", "medium")

    # multi_panel_grid → 한샘 원본 panel C 가 자체로 grid 형식이면 정상 출력 (옷장/책상의
    # chart_diagram / module_lineup / size_chart / structure_chart / color_option 등).
    # sofa close-up처럼 single product 강제인 panel_class 에서만 retry.
    panel_class = panel.get("panel_class", "other")
    grid_ok_classes = {"chart_diagram", "module_lineup", "size_chart",
                        "structure_chart", "color_option", "material_swatch"}
    if result.get("image_format") == "multi_panel_grid" and panel_class not in grid_ok_classes:
        result["verdict"] = "retry"
        result.setdefault("specific_failures", []).insert(0, "결과가 grid 형태 — single panel로 재생성")
        result["product_score_raw"] = result.get("product_score")
        result["product_score"] = 30
    # distortion / forbidden fail = retry trigger (사용자 핵심 요구: 제품 외곡 사수)
    distortion_fails = [r for r in items_results
                        if r.get("category") == "distortion" and r.get("verdict") == "fail"]
    forbidden_fails = [r for r in items_results
                       if r.get("category") == "forbidden" and r.get("verdict") == "fail"]
    result["distortion_fail_count"] = len(distortion_fails)
    result["forbidden_fail_count"] = len(forbidden_fails)
    result["critical_fail_count"] = len(distortion_fails) + len(forbidden_fails)  # 호환

    # product_score 재계산 — new weighting
    #   distortion: weight 6 (가장 중요)
    #   forbidden:  weight 6 (있으면 안 됨)
    #   detail:     weight 1 (있으면 좋지만 retry 트리거 아님)
    #   not_visible:
    #     - distortion: weight × 0.5 (보였어야 했는데 안 보임 — 약간 페널티)
    #     - detail: weight × 0.8 (관대)
    cat_w = {"distortion": 6.0, "forbidden": 6.0, "detail": 1.0}
    nv_factor = {"distortion": 0.5, "forbidden": 0.5, "detail": 0.8}
    pass_score = 0.0
    max_score = 0.0
    for it in items_results:
        cat = it.get("category", "detail")
        w = cat_w.get(cat, 1.0)
        max_score += w
        v = it.get("verdict")
        if v == "pass":
            pass_score += w
        elif v == "not_visible":
            pass_score += w * nv_factor.get(cat, 0.6)
        # fail = 0
    recalc = int(100 * pass_score / max_score) if max_score else 50
    result["product_score_raw"] = result.get("product_score")
    result["product_score"] = recalc

    # pass 기준: distortion 0 fail + forbidden 0 fail + product_score >= 95 + 출력 형식 OK
    # composition_score 는 보고용 — verdict에 영향 X (사용자 결정)
    if (not distortion_fails and not forbidden_fails
            and result["product_score"] >= 95
            and result.get("image_format") != "multi_panel_grid"):
        result["verdict"] = "pass"
        result.setdefault("specific_failures", [])
    else:
        result["verdict"] = "retry"
        if distortion_fails:
            result.setdefault("specific_failures", []).extend(
                [f"distortion fail · {r.get('id','?')}: {r.get('reason_ko','')[:160]}"
                 for r in distortion_fails]
            )
        if forbidden_fails:
            result.setdefault("specific_failures", []).extend(
                [f"forbidden fail · {r.get('id','?')}: {r.get('reason_ko','')[:160]}"
                 for r in forbidden_fails]
            )

    # payload 저장 (사용자 가시화 요구)
    if payload_save_path is not None:
        payload_meta = {
            "panel_id": panel_id,
            "panel_class": panel_class,
            "vision_model": vision_model,
            "ref_paths": [str(p) for p in panel_ref_paths],
            "ref_labels": panel_ref_labels,
            "panel_orig_path": str(panel_orig),
            "swap_result_path": str(swap_result),
            "applicable_item_ids": [it.get("id") for it in applicable_items],
            "user_prompt": user_prompt,
            "result": result,
        }
        payload_save_path.parent.mkdir(parents=True, exist_ok=True)
        payload_save_path.write_text(
            json.dumps(payload_meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return result

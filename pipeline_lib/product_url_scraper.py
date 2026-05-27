"""사용자 제품 URL → product_input.json 자동 생성.

사용자가 url.txt 한 줄로 제품 페이지 URL을 주면:
1) HTML fetch
2) (가능하면) detail page 이미지 fetch + vision LLM 으로 추가 정보
3) LLM 이 산문 + 메타를 product_input.json schema 로 정리

schema (milo_777039/product_input_v3.json 과 동일):
{
  "product_name": "...",
  "seat_count_selected"? (sofa),
  "intro_full": "...",
  "spec": {width_cm, depth_cm, height_cm, ...},
  "feature_descriptions": {...},
  "color_options_detail": [{name, description}],
  "model_options": [{name, dimensions, selected}],
  "delivery_warranty": "...",
  "certifications_full": "...",
  "comprehensive_paragraph": "...",
  "user_override": {...}
}
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import httpx


SYSTEM_PROMPT = """\
당신은 제품 detail 페이지에서 verifiable 시각/구조/소재 정보를 추출하는 ANALYST 다.
HTML / 페이지 메타 / (선택적으로) 이미지를 받아 한국 가구 swap 파이프라인의 product_input
JSON 스키마로 정리한다.

원칙:
1) 산문은 vivid + 정량 — 다리 개수 / 사이즈 / 컬러명 / 시접 종류 / 소재 / 인증 / 모델 옵션 등
   가능한 정량 정보를 모두 담는다.
2) 추측하지 마라. 페이지에 없는 정보는 비워둔다 (null / "" / []).
3) color_options_detail: name 은 사용자가 라벨에 인쇄할 정확한 한글명. description 은 톤/매칭.
4) model_options: 여러 사이즈/타입 옵션이 있으면 list. selected 는 첫 옵션 true.
5) feature_descriptions: 산문 키 (overall_silhouette / arms_detail / legs_detail / fabric_texture
   등). 카테고리에 맞춰 자유롭게 (예: 옷장이면 doors_detail / drawers_detail / handles_detail /
   interior_layout / wood_grain).
6) intro_full / comprehensive_paragraph: 큰 산문 — 결과 swap 시 prompt essence 로 쓰임.
"""


USER_TEMPLATE = """\
=== TASK ===
이 사용자 제품의 detail page 를 분석해 product_input JSON 으로 정리하라.

=== URL ===
{url}

=== HTML excerpt (앞 6000자) ===
{html_excerpt}

=== meta og:image / 추가 정보 (있을 때) ===
{extra_meta}

=== 출력 schema (strict JSON) ===
{{
  "product_name": "...",
  "seat_count_selected": null,  // sofa면 정수
  "intro_full": "...",
  "spec": {{
    "width_cm": int|null,
    "depth_cm": int|null,
    "height_cm": int|null,
    "seat_depth_cm": int|null,
    "seat_height_cm": int|null,
    "arm_height_cm": int|null,
    "leg_height_cm": int|null,
    "weight_kg": int|null,
    "origin": str|null
  }},
  "feature_descriptions": {{ "<key>": "<value 산문>", ... }},
  "color_options_detail": [{{ "name": "...", "description": "..." }}],
  "model_options": [{{ "name": "...", "dimensions": "...", "selected": bool }}],
  "delivery_warranty": "...",
  "certifications_full": "...",
  "comprehensive_paragraph": "...",
  "user_override": {{}}
}}
"""


def _fetch_html(url: str, timeout: float = 30.0) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    }
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as c:
        r = c.get(url)
        r.raise_for_status()
        return r.text


def _strip_html(html: str, max_chars: int = 6000) -> str:
    # 빠른 변환 — script/style 제거 후 텍스트 추출
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def _extract_og(html: str) -> dict:
    og = {}
    for m in re.finditer(r'<meta\s+property="og:([^"]+)"\s+content="([^"]+)"', html):
        og[m.group(1)] = m.group(2)
    title = re.search(r"<title[^>]*>(.+?)</title>", html, re.DOTALL | re.IGNORECASE)
    if title:
        og["page_title"] = title.group(1).strip()
    return og


def scrape_product(
    openai_client: Any,
    text_model: str,
    url: str,
) -> dict:
    html = _fetch_html(url)
    excerpt = _strip_html(html)
    og = _extract_og(html)
    user_prompt = USER_TEMPLATE.format(
        url=url,
        html_excerpt=excerpt,
        extra_meta=json.dumps(og, ensure_ascii=False)[:2000],
    )
    resp = openai_client.chat.completions.create(
        model=text_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    product = json.loads(resp.choices[0].message.content or "{}")
    product.setdefault("product_name", og.get("page_title", "unknown product"))
    product.setdefault("spec", {})
    product.setdefault("feature_descriptions", {})
    product.setdefault("color_options_detail", [])
    product.setdefault("model_options", [])
    product.setdefault("user_override", {})
    product["_source_url"] = url
    return product

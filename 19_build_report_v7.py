"""Report v7 — feedback round 5 + swap 결과 박기.

변경:
- col2 (입력) ↔ col3 (참고 메타) 라벨/내용 정리
  - col2 = 사용자 업로드 (GIF slice refs + LLM 요청 textarea + 미리보기)
  - col3 = 자동 수집 메타 (밀로 thumb/이름/카테고리/가격/description/keywords)
- swap pane에 NB2 / GPT 모델 토글
- swap 결과 (templates/01_sofa_992474/swap_results/run_*/{model}/panel_NN__aN.png) 박기
- 각 panel에 점수/시도/시간 메타
- 처리 시간/평균 점수/passer 통계
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
TPL_ROOT = HERE / "templates"
USER_PROD = HERE / "user_products" / "milo_777039"
OUT = HERE / "report" / "index.html"
OUT.parent.mkdir(exist_ok=True)

data = json.loads((HERE / "top6_template_urls.json").read_text())
milo_fact = json.loads((USER_PROD / "fact.json").read_text())

SECTIONS = ["커버", "기본정보", "사이즈", "소재", "옵션", "모듈"]
SECTION_SLUGS = {
    "커버": "cover", "기본정보": "info", "사이즈": "size",
    "소재": "material", "옵션": "option", "모듈": "module",
}


def assign_sections(panel_count: int) -> dict[str, list[int]]:
    n = panel_count
    if n == 0:
        return {"커버": []}
    result = {"커버": []}
    remaining_sections = SECTIONS[1:]
    per = max(1, n // len(remaining_sections))
    idx = 1
    for i, s in enumerate(remaining_sections):
        if idx > n:
            break
        end = n if i == len(remaining_sections) - 1 else min(idx + per - 1, n)
        result[s] = list(range(idx, end + 1))
        idx = end + 1
    return result


def cover_url(t: dict) -> str:
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    thumbs = list((TPL_ROOT / dir_name).glob("_thumbnail.*"))
    return f"../templates/{dir_name}/{thumbs[0].name}" if thumbs else ""


def get_swap_results(t: dict) -> dict | None:
    """Load latest swap_results/run_*/summary.json if exists. Index by (model, panel_idx)."""
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    sr = TPL_ROOT / dir_name / "swap_results"
    latest_file = sr / "latest.txt"
    if not latest_file.exists():
        return None
    run_dir_name = latest_file.read_text().strip()
    run_dir = sr / run_dir_name
    summary = run_dir / "summary.json"
    if not summary.exists():
        return None
    return {
        "run_dir": run_dir,
        "run_dir_rel": f"../templates/{dir_name}/swap_results/{run_dir_name}",
        "summary": json.loads(summary.read_text()),
    }


def get_template_state(t: dict) -> dict | None:
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    path = TPL_ROOT / f"{rank:02d}_{cat}_{gds}" / "llm_input.json"
    return json.loads(path.read_text()) if path.exists() else None


def rewrite_detail_html(t: dict, side: str, swap_results: dict | None = None,
                        selected_model: str = "nano_banana_pro") -> tuple[str, dict]:
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    detail_path = TPL_ROOT / dir_name / "detail.html"
    meta_path = TPL_ROOT / dir_name / "meta.json"

    detail_html = detail_path.read_text(encoding="utf-8", errors="ignore") if detail_path.exists() else ""
    meta = json.loads(meta_path.read_text())
    detail_imgs = meta.get("detail_imgs", [])
    detail_img_count = (
        meta.get("detail_img_count") or meta.get("panel_count") or len(detail_imgs)
    )
    panel_dir = TPL_ROOT / dir_name

    # build src→local map
    src_to_local = {}
    for i, src in enumerate(detail_imgs, 1):
        matches = list(panel_dir.glob(f"panel_{i:02d}.*"))
        if matches:
            local = f"../templates/{dir_name}/{matches[0].name}"
            src_to_local[src] = local
            if src.startswith("https://"):
                src_to_local["http://" + src[8:]] = local
            elif src.startswith("http://"):
                src_to_local["https://" + src[7:]] = local

    # Index swap results by (model, panel_idx) → final image path + score
    swap_by_model_panel: dict[tuple[str, int], dict] = {}
    if side == "swap" and swap_results:
        for cell in swap_results["summary"]["cells"]:
            key = (cell["model"], cell["panel_idx"])
            swap_by_model_panel[key] = cell

    panel_idx_counter = [0]

    def repl_img(m):
        full = m.group(0)
        src_m = re.search(r'src=["\']([^"\']+)["\']', full)
        if not src_m:
            return full
        src = src_m.group(1)
        src_clean = src.replace("devimage.hanssem.com", "image.hanssem.com")
        if src_clean.startswith("http://"):
            src_clean = "https://" + src_clean[7:]
        local = src_to_local.get(src) or src_to_local.get(src_clean) or src_clean

        panel_idx_counter[0] += 1
        idx = panel_idx_counter[0]

        # If swap side and we have results, swap the src
        if side == "swap" and swap_results:
            # build a generic wrapper that holds slots per model
            slots_html = ""
            for model in ["nano_banana_pro", "gpt_image"]:
                cell = swap_by_model_panel.get((model, idx))
                if cell and cell.get("final") and cell["final"].get("image"):
                    img_name = cell["final"]["image"]
                    swap_src = f'{swap_results["run_dir_rel"]}/{model}/{img_name}'
                    final = cell["final"]
                    prod = final.get("product_score", "-")
                    comp = final.get("composition_score", "-")
                    passed = cell.get("passed", False)
                    badge_cls = "pass" if passed else "fail"
                    slot = (
                        f'<div class="swap-slot" data-model="{model}" data-panel="{idx}">'
                        f'<img src="{swap_src}" data-panel-idx="{idx}" loading="lazy"/>'
                        f'<div class="swap-score-overlay {badge_cls}">'
                        f'prod {prod} · comp {comp}'
                        f'</div></div>'
                    )
                else:
                    slot = (
                        f'<div class="swap-slot pending" data-model="{model}" data-panel="{idx}">'
                        f'<div class="swap-pending-mark">no result</div>'
                        f'</div>'
                    )
                slots_html += slot
            return f'<div class="swap-panel-wrap">{slots_html}</div>'
        else:
            return re.sub(
                r'src=["\'][^"\']+["\']',
                f'src="{local}" data-panel-idx="{idx}" loading="lazy"',
                full,
            )

    rewritten = re.sub(r"<img[^>]+>", repl_img, detail_html)

    sections = assign_sections(detail_img_count)
    for sec_name, indices in sections.items():
        if sec_name == "커버" or not indices:
            continue
        first_idx = indices[0]
        slug = SECTION_SLUGS[sec_name]
        anchor_id = f"sec-{side}-{rank}-{slug}"
        rng = f"panel {indices[0]}" + (f"–{indices[-1]}" if len(indices) > 1 else "")
        divider = (
            f'<div class="sec-divider" id="{anchor_id}" data-section="{sec_name}">'
            f'<span class="sec-name">{sec_name}</span>'
            f'<span class="sec-range">{rng}</span></div>'
        )
        # match either swap-panel-wrap (swap side) or img tag (orig side)
        pattern_swap = f'(<div class="swap-panel-wrap"[^>]*data-panel-idx-first="{first_idx}"[^>]*>|<div class="swap-panel-wrap">[^<]*?<div class="swap-slot"[^>]*data-panel="{first_idx}")'
        # simpler: insert before first matching swap-slot data-panel="{first_idx}" or img data-panel-idx="{first_idx}"
        # use data-panel-idx (orig) or data-panel (swap-slot)
        if side == "swap":
            patt = f'(<div class="swap-panel-wrap">[\\s\\S]*?data-panel="{first_idx}")'
        else:
            patt = f'(<img[^>]*data-panel-idx="{first_idx}"[^>]*>)'
        rewritten = re.sub(patt, divider + r"\1", rewritten, count=1)

    cover_src = cover_url(t)
    if side == "swap" and swap_results:
        # cover-block: show cover swap slots (use panel_01 results — they target intro panel)
        slots_html = ""
        for model in ["nano_banana_pro", "gpt_image"]:
            cell = swap_by_model_panel.get((model, 1))
            if cell and cell.get("final") and cell["final"].get("image"):
                img_name = cell["final"]["image"]
                swap_src = f'{swap_results["run_dir_rel"]}/{model}/{img_name}'
                final = cell["final"]
                prod = final.get("product_score", "-")
                comp = final.get("composition_score", "-")
                passed = cell.get("passed", False)
                badge_cls = "pass" if passed else "fail"
                slots_html += (
                    f'<div class="swap-slot cover-slot" data-model="{model}">'
                    f'<img class="cover-img" src="{swap_src}"/>'
                    f'<div class="swap-score-overlay {badge_cls}">prod {prod} · comp {comp}</div>'
                    f'</div>'
                )
            else:
                slots_html += (
                    f'<div class="swap-slot pending cover-slot" data-model="{model}">'
                    f'<div class="swap-pending-mark">no cover result</div></div>'
                )
        cover_block = f"""
<div class="cover-block" id="sec-{side}-{rank}-cover" data-section="커버">
  <div class="sec-divider sec-divider-cover">
    <span class="sec-name">커버</span>
    <span class="sec-range">대표 이미지</span>
  </div>
  <div class="swap-panel-wrap cover-wrap">{slots_html}</div>
</div>
"""
    else:
        cover_block = f"""
<div class="cover-block" id="sec-{side}-{rank}-cover" data-section="커버">
  <div class="sec-divider sec-divider-cover">
    <span class="sec-name">커버</span>
    <span class="sec-range">대표 이미지</span>
  </div>
  <img class="cover-img" src="{cover_src}" alt="cover" loading="eager"/>
</div>
"""
    rewritten = cover_block + rewritten
    return rewritten, sections


def build_tabs(rank: int, sections: dict) -> str:
    btns = []
    first_active_set = False
    for sec in SECTIONS:
        slug = SECTION_SLUGS[sec]
        has = True if sec == "커버" else bool(sections.get(sec))
        cls = "tab" + ("" if has else " disabled")
        if has and not first_active_set:
            cls += " active"
            first_active_set = True
        attrs = (
            f'onclick="scrollToSection({rank}, \'{slug}\')"' if has else "disabled"
        )
        btns.append(f'<button class="{cls}" data-slug="{slug}" {attrs}>{sec}</button>')
    return "\n".join(btns)


def build_user_input_col(state: dict | None, fact: dict, gif_panels: list) -> str:
    """col2 — 사용자 업로드 + LLM 요청 (실제 입력)."""
    if state is None:
        return f"""
<div class="proc-h">입력 — 사용자 업로드</div>
<div class="input-card pending">
  <div class="input-thumb-box">
    <div class="pending-mark">슬라이스<br/>대기</div>
  </div>
  <div style="flex:1;">
    <div class="input-note">GIF panel_{gif_panels[0]:02d} → frame N장 추출 예정</div>
  </div>
</div>
<div class="proc-h" style="margin-top:12px;">입력 — 사용자 LLM 요청</div>
<textarea class="user-prompt" placeholder="아직 미입력. 예: 패브릭 소재 강조, 가족 거실 분위기 — 사용자가 직접 작성하는 카피/요구사항."></textarea>
"""

    refs = state["product_reference_shots"]
    sys_prompts = state["system_prompts"]
    panels = state["panels"]
    default_req = state["user_request"]["default"]

    thumb_html = "\n".join(
        f'<div class="ref-thumb"><img src="{r["src"]}" title="{r["role"]}: {r["note"]}" loading="lazy"/><div class="ref-role">{r["role"]}</div></div>'
        for r in refs
    )
    panels_html = "".join(
        f'<li><b>panel_{p["panel_idx"]:02d}</b> — <span class="placeholder-text">(vision 완료)</span></li>'
        for p in panels
    )

    return f"""
<div class="proc-h">입력 — 사용자 업로드 <span class="status-tag ready">{len(refs)}장</span></div>
<div class="input-card ready">
  <div class="ref-row-label">GIF 슬라이스 + 다각도 ref</div>
  <div class="ref-row">{thumb_html}</div>
</div>
<div class="proc-h" style="margin-top:12px;">입력 — 사용자 LLM 요청 <span class="status-tag auto">자동 생성</span></div>
<textarea class="user-prompt">{default_req}</textarea>
<details class="llm-preview">
  <summary>LLM 입력 미리보기 (system + panel prompts)</summary>
  <div class="llm-block">
    <div class="llm-h">System — SCENE_ANALYZE</div>
    <pre>{sys_prompts['scene_analyze']}</pre>
    <div class="llm-h">System — PRODUCT_ANALYZE</div>
    <pre>{sys_prompts['product_analyze']}</pre>
    <div class="llm-h">System — SWAP_INSTRUCTION</div>
    <pre>{sys_prompts['swap_instruction']}</pre>
    <div class="llm-h">Panel-by-panel</div>
    <ul class="panel-list">{panels_html}</ul>
  </div>
</details>
"""


def build_meta_col(fact: dict) -> str:
    """col3 — 자동 수집 메타 (밀로 메타 + description + keywords + stats)."""
    cats = " / ".join([c for c in (fact.get("categories") or []) if c][-3:])
    price = fact.get("price") or {}
    dc, normal = price.get("dc"), price.get("normal")
    price_str = f"{dc:,}원 (정가 {normal:,}원)" if dc and normal else ""
    desc = fact.get("description") or ""
    keywords = ", ".join([k for k in (fact.get("searchKeywords") or []) if k][:8])
    kw_count = len([k for k in (fact.get("searchKeywords") or []) if k])
    panel_count = fact.get("panel_count", 0)

    return f"""
<div class="proc-h">참고 메타 (자동 수집 · 한샘 페이지)</div>
<div class="input-card meta">
  <img class="user-prod-thumb" src="../user_products/milo_777039/_thumbnail.jpg" alt="user product"/>
  <div class="input-meta">
    <div class="input-name">{fact.get('gdsNm','(미지정)')}</div>
    <div class="input-cat">{cats}</div>
    <div class="input-price">{price_str}</div>
  </div>
</div>
<div class="proc-h" style="margin-top:10px;">제품 설명</div>
<div class="fact-desc">{desc}</div>
<details class="kw-details">
  <summary>검색 키워드 {kw_count}개</summary>
  <div class="fact-keywords">{keywords}</div>
</details>
<div class="input-stats">
  밀로 panel <b>{panel_count}장</b>
  · 텍스트 노드 <b>{len(fact.get('text_nodes_in_detail_html', []))}</b>
</div>
"""


def build_status_col(swap_results: dict | None) -> str:
    """col4 — 처리 상태 (실제 swap 결과 통계)."""
    if not swap_results:
        return """
<div class="proc-h">상태</div>
<div class="status-line">처리 시간 <b>—</b></div>
<div class="status-line">QA 평균 점수 <b>—</b></div>
<div class="status-line">passer <b>—</b></div>
<button class="run-btn" disabled>swap 실행 (대기)</button>
"""

    summary = swap_results["summary"]
    cells = summary["cells"]
    wall = summary.get("total_wall_seconds", 0)
    by_model = {}
    for m in summary["models"]:
        m_cells = [c for c in cells if c["model"] == m]
        passers = sum(1 for c in m_cells if c["passed"])
        avg_prod = sum(c["final"]["product_score"] for c in m_cells if c.get("final") and "product_score" in c["final"]) / max(1, len(m_cells))
        avg_comp = sum(c["final"]["composition_score"] for c in m_cells if c.get("final") and "composition_score" in c["final"]) / max(1, len(m_cells))
        by_model[m] = {
            "passers": passers,
            "total": len(m_cells),
            "avg_product": round(avg_prod, 1),
            "avg_composition": round(avg_comp, 1),
        }

    rows = "".join(
        f'<div class="status-line"><b>{m}</b>: '
        f'{v["passers"]}/{v["total"]} passer, prod <b>{v["avg_product"]}</b>, comp <b>{v["avg_composition"]}</b></div>'
        for m, v in by_model.items()
    )

    return f"""
<div class="proc-h">상태 (실행 완료)</div>
<div class="status-line">전체 처리 시간 <b>{wall}s</b></div>
{rows}
<button class="run-btn" disabled>swap 재실행</button>
"""


cover_imgs = {t["gdsNo"]: cover_url(t) for t in data["top6"]}


def chip(t: dict) -> str:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    name_short = t["name"][:24] + ("…" if len(t["name"]) > 24 else "")
    state = get_template_state(t)
    swap = get_swap_results(t)
    if swap:
        ready_mark = '<span class="chip-ready done">✓</span>'
    elif state:
        ready_mark = '<span class="chip-ready">●</span>'
    else:
        ready_mark = ""
    return f"""
<button class="chip {'selected' if rank == 1 else ''}" data-rank="{rank}" onclick="selectTpl({rank})">
  {ready_mark}<span class="chip-rank">#{rank}</span>
  <img class="chip-cover" src="{cover_imgs[gds]}" alt="{cat}"/>
  <span class="chip-meta">
    <span class="chip-cat">{cat}</span><span class="chip-name">{name_short}</span>
  </span>
</button>"""


def view(t: dict) -> str:
    rank = t["rank"]
    is_first = rank == 1
    state = get_template_state(t)
    swap_results = get_swap_results(t)
    gif_panels = milo_fact.get("gif_panels", []) or [8]

    orig_html, sections = rewrite_detail_html(t, "orig", None)
    swap_html, _ = rewrite_detail_html(t, "swap", swap_results)

    process_card = build_process_card(t, milo_fact, state, swap_results, gif_panels)
    tabs = build_tabs(rank, sections)

    swap_label_extra = ""
    if swap_results:
        n_pass = sum(1 for c in swap_results["summary"]["cells"] if c["passed"])
        n_tot = len(swap_results["summary"]["cells"])
        swap_label_extra = f' · {n_pass}/{n_tot} pass'

    model_toggle = ""
    if swap_results:
        model_toggle = """
<div class="model-toggle" data-rank="{rank}">
  <button class="m-btn active" data-model="nano_banana_pro" onclick="setModel({rank},'nano_banana_pro')">NB2</button>
  <button class="m-btn" data-model="gpt_image" onclick="setModel({rank},'gpt_image')">GPT</button>
</div>
""".format(rank=rank)

    return f"""
<div class="view {'active' if is_first else ''}" data-rank="{rank}" data-current-model="nano_banana_pro">
  {process_card}

  <div class="tabs-bar">
    <div class="tabs">{tabs}</div>
  </div>

  <div class="split" data-rank="{rank}">
    <div class="pane orig-pane">
      <div class="pane-label">원본 ({t['detail_img_count']} panels + 커버)</div>
      <div class="pane-body" data-side="orig" data-rank="{rank}">{orig_html}</div>
    </div>
    <div class="pane swap-pane">
      <div class="pane-label">
        swap 결과 {model_toggle}
        <span class="hint">{swap_label_extra}</span>
      </div>
      <div class="pane-body swap-body" data-side="swap" data-rank="{rank}">{swap_html}</div>
    </div>
  </div>
</div>
"""


def build_process_card(t, fact, state, swap_results, gif_panels):
    rank = t["rank"]
    tpl_price = t.get("price")
    tpl_price_str = f"{tpl_price:,}원" if tpl_price else ""
    is_ready = state is not None
    is_done = swap_results is not None

    if is_done:
        badge = '<span class="badge ready"><b>실행 완료</b></span>'
    elif is_ready:
        badge = '<span class="badge ready"><b>입력 준비 완료</b></span>'
    else:
        badge = '<span class="badge"><b>입력 대기</b></span>'

    return f"""
<details class="process-card">
  <summary>
    <span class="proc-title">공정 설정</span>
    <span class="proc-summary">
      <span class="badge tpl-badge">템플릿 <b>#{rank} {t.get('category')}</b> · {t['name'][:24]}{'…' if len(t['name'])>24 else ''}</span>
      <span class="badge">방식 <b id="mode-display-{rank}">K2</b></span>
      {badge}
    </span>
    <span class="proc-toggle">▾</span>
  </summary>

  <div class="proc-content">
    <div class="tpl-info-row">
      <div class="proc-h">템플릿 정보</div>
      <div class="tpl-name">{t['name']}</div>
      <div class="tpl-meta">
        <span class="cat-tag">{t.get('category')}</span>
        <span>{t.get('brand','')}</span>
        <span>★ {t.get('reviewCnt',0)} 리뷰</span>
        <span>{tpl_price_str}</span>
        <a href="{t['url']}" target="_blank" class="orig-link">원본 ↗</a>
      </div>
    </div>

    <div class="proc-grid">
      <div class="proc-col proc-mode">
        <div class="proc-h">방식</div>
        <div class="mode-options" data-rank="{rank}">
          <label class="mode-opt"><input type="radio" name="mode-{rank}" value="K1"/>
            <div><div class="mode-name">K1</div><div class="mode-desc">표준 루프</div></div>
          </label>
          <label class="mode-opt"><input type="radio" name="mode-{rank}" value="K2" checked/>
            <div><div class="mode-name">K2 <span class="best">권장</span></div>
            <div class="mode-desc">정밀 루프</div></div>
          </label>
          <label class="mode-opt"><input type="radio" name="mode-{rank}" value="K3"/>
            <div><div class="mode-name">K3</div><div class="mode-desc">결합 분석</div></div>
          </label>
        </div>
      </div>

      <div class="proc-col proc-input">
        {build_user_input_col(state, fact, gif_panels)}
      </div>

      <div class="proc-col proc-meta">
        {build_meta_col(fact)}
      </div>

      <div class="proc-col proc-status">
        {build_status_col(swap_results)}
      </div>
    </div>
  </div>
</details>
"""


chips_html = "\n".join(chip(t) for t in data["top6"])
views_html = "\n".join(view(t) for t in data["top6"])

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>가구 detail 템플릿 swap 미리보기 — v7</title>
<link rel="stylesheet" href="https://res.remodeling.hanssem.com/font/pretendard/pretendard.css"/>
<style>
  :root {{
    --bg: #ffffff; --bg-alt: #f4f4f6;
    --fg: #1a1a1a; --fg-soft: #555; --muted: #888;
    --line: #e5e5e5; --line-soft: #efefef;
    --accent: #ff7a00; --accent-soft: #fff5ec;
    --good: #16a34a; --bad: #dc2626;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Pretendard", -apple-system, system-ui, sans-serif;
    background: var(--bg-alt); color: var(--fg);
    -webkit-font-smoothing: antialiased; font-size: 14px; line-height: 1.5;
  }}
  .topbar {{
    position: sticky; top: 0; z-index: 100;
    background: #fff; border-bottom: 1px solid var(--line); padding: 12px 24px;
  }}
  .topbar-row {{ display: flex; align-items: center; gap: 16px; max-width: 1600px; margin: 0 auto; overflow-x: auto; }}
  .topbar h1 {{ margin: 0; font-size: 13px; font-weight: 600; color: var(--fg-soft); white-space: nowrap; }}
  .chips {{ display: flex; gap: 8px; flex: 1; }}
  .chip {{
    position: relative;
    display: flex; align-items: center; gap: 8px;
    padding: 6px 14px 6px 6px; border: 1px solid var(--line); background: #fff;
    border-radius: 999px; cursor: pointer; transition: all 0.15s;
    font-family: inherit; font-size: 12px; color: #555; white-space: nowrap;
  }}
  .chip:hover {{ border-color: #999; }}
  .chip.selected {{ border-color: var(--fg); background: var(--fg); color: #fff; }}
  .chip-ready {{ position: absolute; top: 2px; right: 4px; color: var(--good); font-size: 8px; font-weight: 700; }}
  .chip-ready.done {{ font-size: 10px; }}
  .chip-cover {{ width: 28px; height: 28px; border-radius: 50%; object-fit: cover; background: #f3f3f3; }}
  .chip-rank {{ font-weight: 700; color: var(--accent); }}
  .chip-meta {{ display: flex; flex-direction: column; align-items: flex-start; line-height: 1.15; }}
  .chip-cat {{ font-size: 10px; opacity: 0.7; }}
  .chip-name {{ font-size: 11px; }}

  .view {{ display: none; padding: 24px 32px; max-width: 1600px; margin: 0 auto; }}
  .view.active {{ display: block; }}

  .process-card {{
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
    margin-bottom: 16px; overflow: hidden;
  }}
  .process-card > summary {{
    list-style: none; cursor: pointer; padding: 14px 20px;
    display: flex; align-items: center; gap: 14px; background: #fff;
  }}
  .process-card > summary::-webkit-details-marker {{ display: none; }}
  .process-card > summary:hover {{ background: #fafafa; }}
  .proc-title {{ font-size: 13px; font-weight: 600; color: var(--fg); white-space: nowrap; }}
  .proc-summary {{ display: flex; gap: 6px; flex-wrap: wrap; flex: 1; align-items: center; }}
  .badge {{ font-size: 11px; color: var(--muted); padding: 3px 8px; background: #f4f4f6; border-radius: 4px; white-space: nowrap; }}
  .badge b {{ color: var(--fg); font-weight: 600; margin-left: 4px; }}
  .badge.ready {{ background: #e6fde8; color: #167a32; }}
  .badge.ready b {{ color: #105823; }}
  .tpl-badge {{ background: #fff5ec; color: #b04a00; }}
  .tpl-badge b {{ color: #7a3300; }}
  .proc-toggle {{ font-size: 14px; color: var(--muted); transition: transform 0.2s; }}
  .process-card[open] .proc-toggle {{ transform: rotate(180deg); }}
  .process-card[open] > summary {{ border-bottom: 1px solid var(--line); }}

  .proc-content {{ padding: 20px; }}
  .tpl-info-row {{ padding-bottom: 16px; margin-bottom: 16px; border-bottom: 1px solid var(--line-soft); }}
  .tpl-name {{ font-size: 16px; font-weight: 600; margin-top: 4px; }}
  .tpl-meta {{ display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: var(--fg-soft); margin-top: 6px; }}
  .cat-tag {{ background: #efefef; padding: 2px 8px; border-radius: 4px; color: #444; font-weight: 500; }}
  .orig-link {{ color: #2563eb; text-decoration: none; }}

  .proc-grid {{ display: grid; grid-template-columns: 0.9fr 1.4fr 1.1fr 0.9fr; gap: 24px; }}
  .proc-col {{ display: flex; flex-direction: column; gap: 8px; min-width: 0; }}
  .proc-h {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; }}
  .status-tag {{ display: inline-block; padding: 1px 6px; font-size: 9px; border-radius: 4px; margin-left: 6px; text-transform: none; letter-spacing: 0; }}
  .status-tag.ready {{ color: #167a32; background: #e6fde8; }}
  .status-tag.auto {{ color: #b04a00; background: #fff5ec; }}

  .mode-options {{ display: flex; flex-direction: column; gap: 6px; }}
  .mode-opt {{
    display: flex; align-items: flex-start; gap: 8px;
    padding: 8px 10px; border: 1px solid var(--line); border-radius: 8px;
    cursor: pointer; transition: all 0.15s;
  }}
  .mode-opt:has(input:checked) {{ border-color: var(--accent); background: var(--accent-soft); }}
  .mode-opt input {{ margin-top: 3px; accent-color: var(--accent); }}
  .mode-opt > div:nth-child(2) {{ flex: 1; min-width: 0; }}
  .mode-name {{ font-size: 12px; font-weight: 600; }}
  .mode-name .best {{ display: inline-block; margin-left: 4px; padding: 1px 5px; font-size: 9px; color: var(--good); background: #e6fde8; border-radius: 4px; vertical-align: 1px; }}
  .mode-desc {{ font-size: 11px; color: var(--muted); margin-top: 1px; }}

  .input-card {{
    padding: 12px; background: var(--bg-alt); border: 1px dashed var(--line);
    border-radius: 8px;
  }}
  .input-card.pending {{ background: #fffaf3; border-color: #f3d4a7; display: flex; gap: 10px; }}
  .input-card.ready {{ background: #f6fff6; border: 1px solid #c6ecc8; display: flex; flex-direction: column; gap: 8px; }}
  .input-card.meta {{ background: #fff; border: 1px solid var(--line); display: flex; gap: 10px; align-items: center; }}
  .input-thumb-box {{
    width: 64px; height: 64px; background: #fff; border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    border: 1px dashed #d0d0d0; flex-shrink: 0;
  }}
  .pending-mark {{ font-size: 10px; color: var(--accent); font-weight: 600; text-align: center; line-height: 1.3; padding: 4px; }}
  .input-meta {{ flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }}
  .input-name {{ font-size: 12px; font-weight: 600; line-height: 1.3; }}
  .input-cat {{ font-size: 11px; color: var(--muted); }}
  .input-price {{ font-size: 12px; color: var(--accent); font-weight: 600; }}
  .input-note {{ font-size: 10px; color: var(--muted); margin-top: 4px; font-style: italic; }}

  .user-prod-thumb {{ width: 56px; height: 56px; border-radius: 6px; object-fit: cover; background: #fff; border: 1px solid var(--line); }}
  .ref-row-label {{ font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}
  .ref-row {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(56px, 1fr)); gap: 6px; }}
  .ref-thumb {{ position: relative; aspect-ratio: 1/1; }}
  .ref-thumb img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 4px; border: 1px solid var(--line); background: #fff; }}
  .ref-role {{ position: absolute; bottom: 1px; left: 1px; right: 1px;
    font-size: 8px; color: #fff; background: rgba(0,0,0,0.55); padding: 1px 3px;
    border-radius: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

  .user-prompt {{
    width: 100%; min-height: 80px; padding: 10px 12px;
    border: 1px solid var(--line); border-radius: 8px; resize: vertical;
    font-family: inherit; font-size: 12px; color: var(--fg); background: #fafafa; line-height: 1.5;
  }}
  .user-prompt::placeholder {{ color: var(--muted); font-style: italic; }}

  .llm-preview {{ margin-top: 4px; border: 1px solid var(--line); border-radius: 8px; background: #fafafa; }}
  .llm-preview summary {{ cursor: pointer; padding: 8px 12px; font-size: 11px; color: var(--fg-soft); font-weight: 600; outline: none; }}
  .llm-preview summary::-webkit-details-marker {{ display: none; }}
  .llm-block {{ padding: 4px 12px 12px; }}
  .llm-h {{ font-size: 10px; color: var(--muted); margin-top: 8px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }}
  .llm-block pre {{
    margin: 4px 0 8px; padding: 8px 10px;
    background: #fff; border: 1px solid var(--line); border-radius: 4px;
    font-family: ui-monospace, Menlo, monospace; font-size: 11px; line-height: 1.5;
    white-space: pre-wrap; word-break: break-word;
  }}
  .panel-list {{ margin: 4px 0 0; padding-left: 18px; font-size: 11px; color: var(--fg-soft); }}
  .placeholder-text {{ color: var(--muted); font-style: italic; }}

  .fact-desc {{ font-size: 12px; color: var(--fg-soft); line-height: 1.55; }}
  .kw-details summary {{ cursor: pointer; font-size: 11px; color: var(--muted); margin-top: 4px; outline: none; }}
  .fact-keywords {{ font-size: 11px; color: var(--fg-soft); padding: 6px 0; line-height: 1.6; }}
  .input-stats {{ font-size: 11px; color: var(--muted); margin-top: 6px; }}
  .input-stats b {{ color: var(--fg); font-weight: 600; }}

  .status-line {{ font-size: 12px; color: var(--muted); }}
  .status-line b {{ color: var(--fg); font-weight: 600; margin-left: 4px; }}
  .run-btn {{
    margin-top: auto; padding: 10px;
    background: var(--accent); color: #fff; border: none; border-radius: 8px;
    font-family: inherit; font-size: 13px; font-weight: 600;
    opacity: 0.5; cursor: not-allowed;
  }}

  .tabs-bar {{ position: sticky; top: 56px; z-index: 30; background: var(--bg-alt); padding: 4px 0 0; }}
  .tabs {{
    display: flex; gap: 0; background: #fff; border: 1px solid var(--line);
    border-radius: 12px; padding: 0 12px; overflow-x: auto;
  }}
  .tab {{
    padding: 12px 18px; background: transparent; border: none;
    border-bottom: 2px solid transparent; margin-bottom: -1px;
    font-family: inherit; font-size: 13px; color: #666; cursor: pointer; white-space: nowrap;
  }}
  .tab.active {{ color: var(--fg); border-bottom-color: var(--fg); font-weight: 600; }}
  .tab.disabled {{ opacity: 0.3; cursor: not-allowed; }}

  .split {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; min-height: 70vh; }}
  .pane {{
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
    overflow: hidden; display: flex; flex-direction: column; max-height: 82vh;
  }}
  .pane-label {{
    padding: 10px 20px; background: #fafafa; border-bottom: 1px solid var(--line);
    font-size: 12px; color: #444; font-weight: 600; flex-shrink: 0;
    display: flex; align-items: center; gap: 12px; justify-content: space-between;
  }}
  .pane-label .hint {{ color: var(--muted); font-weight: 400; }}
  .pane-body {{ overflow-y: auto; flex: 1; padding: 24px 28px; background: #fff; position: relative; }}
  .pane-body img {{ max-width: 100%; display: block; margin: 0 auto; }}
  .pane-body iframe {{ max-width: 100%; display: block; margin: 16px auto; }}
  .pane-body .mall_prod_info {{ text-align: center; }}

  .cover-block {{ margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px dashed var(--line); }}
  .cover-img {{ width: 100%; max-width: 520px; aspect-ratio: 1/1; object-fit: contain; background: #fafafa; border-radius: 8px; }}

  .sec-divider {{ display: flex; align-items: baseline; gap: 12px; margin: 18px 0 14px; line-height: normal; }}
  .sec-divider .sec-name {{ font-size: 13px; font-weight: 700; color: var(--fg);
    padding: 4px 10px; background: var(--accent-soft); border-left: 3px solid var(--accent); border-radius: 0 4px 4px 0; }}
  .sec-divider .sec-range {{ font-size: 10px; color: var(--muted); font-family: ui-monospace, monospace; }}
  .sec-divider-cover .sec-name {{ background: #e8f4ff; border-left-color: #2563eb; }}

  /* model toggle inside swap pane-label */
  .model-toggle {{ display: inline-flex; border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }}
  .m-btn {{ padding: 4px 10px; background: #fff; border: none; font-size: 11px; cursor: pointer; color: var(--muted); }}
  .m-btn.active {{ background: var(--fg); color: #fff; }}

  /* swap-panel-wrap holds both model slots; only one shown at a time */
  .swap-panel-wrap {{ position: relative; margin: 0 auto; max-width: 100%; }}
  .swap-slot {{ display: none; position: relative; }}
  .view[data-current-model="nano_banana_pro"] .swap-slot[data-model="nano_banana_pro"] {{ display: block; }}
  .view[data-current-model="gpt_image"] .swap-slot[data-model="gpt_image"] {{ display: block; }}
  .swap-slot.pending {{ display: none; }}
  .view[data-current-model="nano_banana_pro"] .swap-slot.pending[data-model="nano_banana_pro"] {{ display: flex; }}
  .view[data-current-model="gpt_image"] .swap-slot.pending[data-model="gpt_image"] {{ display: flex; }}
  .swap-slot.pending {{ align-items: center; justify-content: center; min-height: 120px; background: #f8f8f8; border-radius: 6px; }}
  .swap-pending-mark {{ font-size: 11px; color: var(--muted); }}
  .swap-slot img {{ max-width: 100%; display: block; margin: 8px auto; }}
  .swap-slot.cover-slot img {{ max-width: 520px; }}
  .swap-score-overlay {{
    position: absolute; bottom: 12px; right: 12px;
    font-size: 11px; padding: 3px 8px; border-radius: 4px;
    background: rgba(0,0,0,0.7); color: #fff; font-family: ui-monospace, monospace;
  }}
  .swap-score-overlay.pass {{ background: rgba(22, 163, 74, 0.85); }}
  .swap-score-overlay.fail {{ background: rgba(220, 38, 38, 0.8); }}

  /* pending state: no swap results yet — keep orig with grey overlay */
  .swap-body:not(:has(.swap-panel-wrap)) img {{ opacity: 0.28; filter: grayscale(85%); }}

  .pane-body::-webkit-scrollbar {{ width: 8px; }}
  .pane-body::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 4px; }}
</style>
</head>
<body>
<div class="topbar">
  <div class="topbar-row">
    <h1>가구 detail 템플릿 swap 미리보기</h1>
    <div class="chips">{chips_html}</div>
  </div>
</div>
{views_html}
<script>
function selectTpl(rank) {{
  document.querySelectorAll('.chip').forEach(c => c.classList.toggle('selected', +c.dataset.rank === rank));
  document.querySelectorAll('.view').forEach(v => v.classList.toggle('active', +v.dataset.rank === rank));
  window.scrollTo(0, 0);
}}

function setModel(rank, model) {{
  const view = document.querySelector(`.view[data-rank="${{rank}}"]`);
  if (!view) return;
  view.dataset.currentModel = model;
  view.querySelectorAll('.m-btn').forEach(b => b.classList.toggle('active', b.dataset.model === model));
}}

function scrollToSection(rank, slug) {{
  const view = document.querySelector(`.view[data-rank="${{rank}}"]`);
  if (!view) return;
  view.querySelectorAll('.tab').forEach(t => {{
    if (t.classList.contains('disabled')) return;
    t.classList.toggle('active', t.dataset.slug === slug);
  }});
  ['orig', 'swap'].forEach(side => {{
    const body = view.querySelector(`.pane-body[data-side="${{side}}"][data-rank="${{rank}}"]`);
    if (!body) return;
    const anchor = body.querySelector(`#sec-${{side}}-${{rank}}-${{slug}}`);
    if (!anchor) return;
    const bodyRect = body.getBoundingClientRect();
    const anchorRect = anchor.getBoundingClientRect();
    const delta = anchorRect.top - bodyRect.top;
    body.scrollTo({{ top: body.scrollTop + delta - 12, behavior: 'smooth' }});
  }});
}}

let syncing = false;
function setupSyncForView(rank) {{
  const view = document.querySelector(`.view[data-rank="${{rank}}"]`);
  if (!view) return;
  const orig = view.querySelector(`.pane-body[data-side="orig"]`);
  const swap = view.querySelector(`.pane-body[data-side="swap"]`);
  if (!orig || !swap) return;
  function bind(src, dst) {{
    src.addEventListener('scroll', () => {{
      if (syncing) return;
      syncing = true;
      const srcMax = src.scrollHeight - src.clientHeight;
      const dstMax = dst.scrollHeight - dst.clientHeight;
      const ratio = srcMax > 0 ? src.scrollTop / srcMax : 0;
      dst.scrollTop = ratio * dstMax;
      requestAnimationFrame(() => {{ syncing = false; }});
    }});
  }}
  bind(orig, swap); bind(swap, orig);
}}
document.addEventListener('DOMContentLoaded', () => {{
  for (let r = 1; r <= 6; r++) setupSyncForView(r);
  document.querySelectorAll('.mode-options').forEach(g => {{
    const rank = g.dataset.rank;
    g.addEventListener('change', () => {{
      const v = g.querySelector('input:checked')?.value || 'K2';
      const el = document.getElementById(`mode-display-${{rank}}`);
      if (el) el.textContent = v;
    }});
  }});
}});
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT}")
print(f"size: {OUT.stat().st_size // 1024}KB")

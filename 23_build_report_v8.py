"""Report v8 — panel-level dual-grid layout.

변경:
- 좌우 anchor align: panel 1개 = 1 grid row (CSS grid_template_columns: 1fr 1fr)
  → 같은 panel의 좌(원본) / 우(swap)이 자동 align
- swap 이미지 밑에 HTML 카피 (panel_copy.json)
- 페이지 컨텐츠 = 밀로 일관 (템플릿 메타와 분리)
- swap 결과 통합: cover/design_chart는 retry run에서, 나머지는 원래 run에서
- 페이지 단위 스크롤 (좌우 sync 불필요 — 같은 grid row니까 자동 align)
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
milo_spec = json.loads((USER_PROD / "spec.json").read_text())["spec"]
panel_copy = json.loads((TPL_ROOT / "01_sofa_992474/panel_copy.json").read_text())["copies"]

SECTIONS = ["커버", "기본정보", "사이즈", "소재", "옵션", "모듈"]
SECTION_SLUGS = {
    "커버": "cover", "기본정보": "info", "사이즈": "size",
    "소재": "material", "옵션": "option", "모듈": "module",
}


def assign_sections(panel_count):
    n = panel_count
    if n == 0:
        return {"커버": []}
    result = {"커버": []}
    remaining = SECTIONS[1:]
    per = max(1, n // len(remaining))
    idx = 1
    for i, s in enumerate(remaining):
        if idx > n:
            break
        end = n if i == len(remaining) - 1 else min(idx + per - 1, n)
        result[s] = list(range(idx, end + 1))
        idx = end + 1
    return result


def get_state(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    p = TPL_ROOT / f"{rank:02d}_{cat}_{gds}" / "llm_input.json"
    return json.loads(p.read_text()) if p.exists() else None


def get_swap_results(t):
    """Merge initial run + retry run results for #1."""
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    sr = TPL_ROOT / dir_name / "swap_results"
    if not sr.exists():
        return None
    runs = sorted([d for d in sr.iterdir() if d.is_dir()])
    if not runs:
        return None
    # find initial (run_*) and retry (retry_*)
    initial = next((d for d in runs if d.name.startswith("run_")), None)
    retry = next((d for d in runs if d.name.startswith("retry_")), None)

    out = {"by_label": {}, "cells_initial": [], "cells_retry": [], "dirs": {}}
    if initial:
        s = json.loads((initial / "summary.json").read_text())
        out["cells_initial"] = s["cells"]
        out["dirs"]["initial"] = f"../templates/{dir_name}/swap_results/{initial.name}"
        out["initial_wall"] = s.get("total_wall_seconds")
        out["models"] = s.get("models", [])
    if retry:
        s = json.loads((retry / "summary.json").read_text())
        out["cells_retry"] = s["cells"]
        out["dirs"]["retry"] = f"../templates/{dir_name}/swap_results/{retry.name}"
        out["retry_wall"] = s.get("total_wall_seconds")

    # build by_label index: { "cover": {model: cell, ...}, 1: {model: cell, ...} }
    by_label = {}
    # initial = panels (panel_idx)
    for c in out["cells_initial"]:
        idx = c["panel_idx"]
        by_label.setdefault(idx, {})[c["model"]] = {"cell": c, "source": "initial"}
    # retry = cover + design_chart panels (label-based)
    for c in out["cells_retry"]:
        label = c["label"]
        key = "cover" if label == "cover" else int(label.split("_")[1])
        # retry overrides initial for design_chart panels and cover
        by_label.setdefault(key, {})[c["model"]] = {"cell": c, "source": "retry"}

    out["by_label"] = by_label
    return out


def swap_img_url(swap_results, label_key, model):
    """Return the src URL of the final swap image for (label, model)."""
    entry = swap_results["by_label"].get(label_key, {}).get(model)
    if not entry:
        return None, None, None
    cell = entry["cell"]
    source = entry["source"]
    final = cell.get("final")
    if not final or not final.get("image"):
        return None, None, None
    run_root = swap_results["dirs"][source]
    img_path = f"{run_root}/{model}/{final['image']}"
    return img_path, cell, final


def cover_url_thumb(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    # prefer _cover_1000.jpg if exists, else _thumbnail
    cov = TPL_ROOT / dir_name / "_cover_1000.jpg"
    if cov.exists():
        return f"../templates/{dir_name}/_cover_1000.jpg"
    thumbs = list((TPL_ROOT / dir_name).glob("_thumbnail.*"))
    return f"../templates/{dir_name}/{thumbs[0].name}" if thumbs else ""


def panel_local_url(t, panel_idx):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    matches = list((TPL_ROOT / dir_name).glob(f"panel_{panel_idx:02d}.*"))
    return f"../templates/{dir_name}/{matches[0].name}" if matches else ""


def build_dual_panel_row(t, idx, section_anchor_id, swap_results):
    """Build one panel-level grid row: [orig img] | [swap img + copy].

    section_anchor_id: if provided, attach as id for tab scroll.
    """
    orig_src = panel_local_url(t, idx)
    copy = panel_copy.get(f"panel_{idx:02d}", {})
    title = copy.get("title", "")
    body = copy.get("body", "")

    # swap content per model (toggled via parent .view[data-current-model])
    swap_slots = ""
    for model in ["nano_banana_pro", "gpt_image"]:
        url, cell, final = swap_img_url(swap_results, idx, model) if swap_results else (None, None, None)
        if url and final:
            prod = final.get("product_score", "-")
            comp = final.get("composition_score", "-")
            passed = cell.get("passed", False)
            text_flag = final.get("text_in_image")
            badge_cls = "pass" if passed else "fail"
            tip = f"prod {prod} · comp {comp}" + (" · TEXT!" if text_flag else "")
            swap_slots += f"""
<div class="swap-slot" data-model="{model}">
  <img src="{url}" loading="lazy"/>
  <div class="swap-score-overlay {badge_cls}" title="{tip}">{tip}</div>
</div>
"""
        else:
            swap_slots += f"""
<div class="swap-slot pending" data-model="{model}">
  <div class="swap-pending-mark">no result</div>
</div>
"""

    anchor_attr = f'id="{section_anchor_id}"' if section_anchor_id else ""
    return f"""
<div class="dual-panel" data-panel-idx="{idx}" {anchor_attr}>
  <div class="cell orig">
    <img src="{orig_src}" alt="panel_{idx:02d}" loading="lazy"/>
  </div>
  <div class="cell swap">
    <div class="swap-img-wrap">{swap_slots}</div>
    {f'<div class="panel-copy"><h4>{title}</h4><p>{body}</p></div>' if title or body else ''}
  </div>
</div>
"""


def build_cover_row(t, swap_results):
    cover_src = cover_url_thumb(t)
    copy = panel_copy.get("cover", {})
    title = copy.get("title", "")
    body = copy.get("body", "")

    swap_slots = ""
    if swap_results:
        for model in ["nano_banana_pro", "gpt_image"]:
            url, cell, final = swap_img_url(swap_results, "cover", model)
            if url and final:
                prod = final.get("product_score", "-")
                comp = final.get("composition_score", "-")
                passed = cell.get("passed", False)
                text_flag = final.get("text_in_image")
                badge_cls = "pass" if passed else "fail"
                tip = f"prod {prod} · comp {comp}" + (" · TEXT!" if text_flag else "")
                swap_slots += f"""
<div class="swap-slot cover-slot" data-model="{model}">
  <img src="{url}" loading="lazy"/>
  <div class="swap-score-overlay {badge_cls}" title="{tip}">{tip}</div>
</div>
"""
            else:
                swap_slots += f"""
<div class="swap-slot pending cover-slot" data-model="{model}">
  <div class="swap-pending-mark">no cover result</div>
</div>
"""
    else:
        swap_slots = '<div class="swap-slot pending cover-slot"><div class="swap-pending-mark">대기</div></div>'

    return f"""
<div class="dual-panel cover-row" id="sec-1-cover">
  <div class="cell orig">
    <div class="sec-divider sec-divider-cover">
      <span class="sec-name">커버</span><span class="sec-range">대표 1:1</span>
    </div>
    <img src="{cover_src}" alt="cover" loading="eager"/>
  </div>
  <div class="cell swap">
    <div class="sec-divider sec-divider-cover">
      <span class="sec-name">커버 swap</span><span class="sec-range">1:1</span>
    </div>
    <div class="swap-img-wrap">{swap_slots}</div>
    {f'<div class="panel-copy"><h4>{title}</h4><p>{body}</p></div>' if title or body else ''}
  </div>
</div>
"""


def build_dual_content(t):
    """Build the entire dual-pane content area (one panel = one row)."""
    swap_results = get_swap_results(t) if t["rank"] == 1 else None
    meta_path = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}/meta.json"
    meta = json.loads(meta_path.read_text())
    detail_imgs = meta.get("detail_imgs", [])
    panel_count = meta.get("detail_img_count") or meta.get("panel_count") or len(detail_imgs)
    sections = assign_sections(panel_count)

    rows = [build_cover_row(t, swap_results)]

    # build a map of panel_idx → section anchor (first panel of each section gets anchor)
    sec_anchor_by_idx = {}
    for sec_name, indices in sections.items():
        if sec_name == "커버" or not indices:
            continue
        sec_anchor_by_idx[indices[0]] = f"sec-{t['rank']}-{SECTION_SLUGS[sec_name]}"

    for i in range(1, panel_count + 1):
        anchor = sec_anchor_by_idx.get(i)
        rows.append(build_dual_panel_row(t, i, anchor, swap_results))

    return "\n".join(rows), sections


def build_tabs(rank, sections):
    btns = []
    first_active_set = False
    for sec in SECTIONS:
        slug = SECTION_SLUGS[sec]
        has = True if sec == "커버" else bool(sections.get(sec))
        cls = "tab" + ("" if has else " disabled")
        if has and not first_active_set:
            cls += " active"
            first_active_set = True
        attrs = f'onclick="scrollToSection({rank}, \'{slug}\')"' if has else "disabled"
        btns.append(f'<button class="{cls}" data-slug="{slug}" {attrs}>{sec}</button>')
    return "\n".join(btns)


def build_process_card(t, fact, spec, state, swap_results):
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

    # input (사용자 업로드 = GIF frames만)
    gif_frames = sorted((USER_PROD / "gif_frames").glob("frame_*.jpg"))[:3]
    refs_html = "".join(
        f'<div class="ref-thumb"><img src="../user_products/milo_777039/gif_frames/{f.name}" loading="lazy"/><div class="ref-role">GIF frame {i+1}</div></div>'
        for i, f in enumerate(gif_frames)
    )

    # user LLM request — 2인용 한정 + 재작성
    spec_summary = spec.get("ko_summary", "")
    default_req = (
        f"제품: {spec.get('product_name','밀로 패브릭소파 2인용')}. "
        f"{spec_summary} "
        "원본 detail page panel의 의도(소재 설명, 사이즈, 옵션)는 유지하되 "
        "제품은 밀로 패브릭소파 2인용으로 정확히 swap. 가죽 느낌 X."
    )

    # 자동 수집 메타
    price = fact.get("price") or {}
    dc, normal = price.get("dc"), price.get("normal")
    price_str = f"{dc:,}원 (정가 {normal:,}원)" if dc and normal else ""

    # 상태 col
    if swap_results:
        wall_init = swap_results.get("initial_wall", 0)
        wall_retry = swap_results.get("retry_wall", 0)
        total_wall = wall_init + wall_retry
        # aggregate by model
        agg = {}
        for label_key, by_model in swap_results["by_label"].items():
            for model, entry in by_model.items():
                cell = entry["cell"]
                final = cell.get("final") or {}
                agg.setdefault(model, []).append({
                    "passed": cell.get("passed"),
                    "prod": final.get("product_score", 0),
                    "comp": final.get("composition_score", 0),
                })
        rows = ""
        for m, arr in agg.items():
            n_pass = sum(1 for a in arr if a["passed"])
            avg_p = round(sum(a["prod"] for a in arr) / max(1, len(arr)), 1)
            avg_c = round(sum(a["comp"] for a in arr) / max(1, len(arr)), 1)
            label = "NB2" if m == "nano_banana_pro" else "GPT"
            rows += f'<div class="status-line"><b>{label}</b>: {n_pass}/{len(arr)} pass · prod {avg_p} · comp {avg_c}</div>'
        status_col = f"""
<div class="proc-h">상태 (실행 완료)</div>
<div class="status-line">처리 시간 (초기 + retry) <b>{total_wall:.0f}s</b></div>
{rows}
"""
    else:
        status_col = """
<div class="proc-h">상태</div>
<div class="status-line">처리 시간 <b>—</b></div>
<div class="status-line">QA 점수 <b>—</b></div>
<div class="status-line">시도 <b>—</b></div>
"""

    spec_block = ""
    if is_done:
        dims = spec.get("dimensions", {})
        mat = spec.get("material", {})
        colors = ", ".join(spec.get("colors") or [])
        spec_block = f"""
<details class="spec-details">
  <summary>밀로 spec (vision 추출)</summary>
  <div class="spec-list">
    <div><b>좌석 수</b>: {spec.get('seat_count','?')}</div>
    <div><b>좌석높이</b>: {dims.get('seat_height_cm','?')}cm · <b>팔걸이높이</b>: {dims.get('arm_height_cm','?')}cm</div>
    <div><b>패브릭</b>: {mat.get('upholstery','')}</div>
    <div><b>좌방석</b>: {mat.get('seat_cushion','')}</div>
    <div><b>등쿠션</b>: {mat.get('back_cushion','')}</div>
    <div><b>프레임</b>: {mat.get('frame','')}</div>
    <div><b>컬러</b>: {colors}</div>
  </div>
</details>
"""

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
      <div class="proc-h">템플릿 정보 (스왑 base)</div>
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
      <div class="proc-col">
        <div class="proc-h">방식</div>
        <div class="mode-options" data-rank="{rank}">
          <label class="mode-opt"><input type="radio" name="mode-{rank}" value="K1"/>
            <div><div class="mode-name">K1</div><div class="mode-desc">표준 루프</div></div></label>
          <label class="mode-opt"><input type="radio" name="mode-{rank}" value="K2" checked/>
            <div><div class="mode-name">K2 <span class="best">권장</span></div>
            <div class="mode-desc">정밀 루프</div></div></label>
          <label class="mode-opt"><input type="radio" name="mode-{rank}" value="K3"/>
            <div><div class="mode-name">K3</div><div class="mode-desc">결합 분석</div></div></label>
        </div>
      </div>

      <div class="proc-col">
        <div class="proc-h">입력 — 사용자 업로드 ({len(gif_frames)}장 GIF slice)</div>
        <div class="input-card ready">
          <div class="ref-row-label">GIF panel_08 (360°) slice — 운영 시: 업로드 존 분리</div>
          <div class="ref-row">{refs_html}</div>
        </div>
        <div class="proc-h" style="margin-top:12px;">입력 — 사용자 LLM 요청</div>
        <textarea class="user-prompt">{default_req}</textarea>
      </div>

      <div class="proc-col">
        <div class="proc-h">자동 수집 메타 (한샘 페이지 · 밀로 2인용)</div>
        <div class="input-card meta">
          <img class="user-prod-thumb" src="../user_products/milo_777039/_thumbnail.jpg"/>
          <div class="input-meta">
            <div class="input-name">{spec.get('product_name','밀로 패브릭소파 2인용')}</div>
            <div class="input-cat">패브릭 소파 · 2인용</div>
            <div class="input-price">{price_str}</div>
          </div>
        </div>
        {spec_block}
      </div>

      <div class="proc-col">
        {status_col}
      </div>
    </div>
  </div>
</details>
"""


def chip(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    name_short = t["name"][:24] + ("…" if len(t["name"]) > 24 else "")
    state = get_state(t)
    swap = get_swap_results(t) if rank == 1 else None
    if swap:
        ready_mark = '<span class="chip-ready done">✓</span>'
    elif state:
        ready_mark = '<span class="chip-ready">●</span>'
    else:
        ready_mark = ""
    cov = cover_url_thumb(t)
    return f"""
<button class="chip {'selected' if rank == 1 else ''}" data-rank="{rank}" onclick="selectTpl({rank})">
  {ready_mark}<span class="chip-rank">#{rank}</span>
  <img class="chip-cover" src="{cov}" alt="{cat}"/>
  <span class="chip-meta">
    <span class="chip-cat">{cat}</span><span class="chip-name">{name_short}</span>
  </span>
</button>"""


def view(t):
    rank = t["rank"]
    is_first = rank == 1
    state = get_state(t)
    swap_results = get_swap_results(t) if rank == 1 else None
    dual_content, sections = build_dual_content(t)
    process_card = build_process_card(t, milo_fact, milo_spec if rank == 1 else {}, state, swap_results)
    tabs = build_tabs(rank, sections)

    model_toggle = ""
    if swap_results:
        model_toggle = f"""
<div class="model-toggle">
  <button class="m-btn active" data-model="nano_banana_pro" onclick="setModel({rank},'nano_banana_pro')">NB2</button>
  <button class="m-btn" data-model="gpt_image" onclick="setModel({rank},'gpt_image')">GPT</button>
</div>
"""

    return f"""
<div class="view {'active' if is_first else ''}" data-rank="{rank}" data-current-model="gpt_image">
  {process_card}
  <div class="tabs-bar">
    <div class="tabs">{tabs}</div>
    {model_toggle}
  </div>
  <div class="dual-grid" data-rank="{rank}">
    <div class="dual-header">
      <div class="dual-h-left">원본 · 한샘 detail page</div>
      <div class="dual-h-right">swap 결과 · 밀로 패브릭소파 2인용</div>
    </div>
    {dual_content}
  </div>
</div>
"""


chips_html = "\n".join(chip(t) for t in data["top6"])
views_html = "\n".join(view(t) for t in data["top6"])

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>가구 detail 템플릿 swap 미리보기 — v8</title>
<link rel="stylesheet" href="https://res.remodeling.hanssem.com/font/pretendard/pretendard.css"/>
<style>
  :root {{
    --bg: #fff; --bg-alt: #f4f4f6;
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
    position: relative; display: flex; align-items: center; gap: 8px;
    padding: 6px 14px 6px 6px; border: 1px solid var(--line); background: #fff;
    border-radius: 999px; cursor: pointer;
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

  /* === Process Card === */
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
  .proc-title {{ font-size: 13px; font-weight: 600; white-space: nowrap; }}
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

  .proc-grid {{ display: grid; grid-template-columns: 0.9fr 1.3fr 1.2fr 1fr; gap: 24px; }}
  .proc-col {{ display: flex; flex-direction: column; gap: 8px; min-width: 0; }}
  .proc-h {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; }}

  .mode-options {{ display: flex; flex-direction: column; gap: 6px; }}
  .mode-opt {{ display: flex; align-items: flex-start; gap: 8px; padding: 8px 10px; border: 1px solid var(--line); border-radius: 8px; cursor: pointer; }}
  .mode-opt:has(input:checked) {{ border-color: var(--accent); background: var(--accent-soft); }}
  .mode-opt input {{ margin-top: 3px; accent-color: var(--accent); }}
  .mode-name {{ font-size: 12px; font-weight: 600; }}
  .mode-name .best {{ display: inline-block; margin-left: 4px; padding: 1px 5px; font-size: 9px; color: var(--good); background: #e6fde8; border-radius: 4px; vertical-align: 1px; }}
  .mode-desc {{ font-size: 11px; color: var(--muted); margin-top: 1px; }}

  .input-card {{ padding: 12px; background: var(--bg-alt); border: 1px dashed var(--line); border-radius: 8px; }}
  .input-card.ready {{ background: #f6fff6; border: 1px solid #c6ecc8; display: flex; flex-direction: column; gap: 8px; }}
  .input-card.meta {{ background: #fff; border: 1px solid var(--line); display: flex; gap: 10px; align-items: center; }}
  .user-prod-thumb {{ width: 56px; height: 56px; border-radius: 6px; object-fit: cover; background: #fff; border: 1px solid var(--line); }}
  .input-meta {{ flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }}
  .input-name {{ font-size: 12px; font-weight: 600; line-height: 1.3; }}
  .input-cat {{ font-size: 11px; color: var(--muted); }}
  .input-price {{ font-size: 12px; color: var(--accent); font-weight: 600; }}

  .ref-row-label {{ font-size: 10px; color: var(--muted); }}
  .ref-row {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); gap: 6px; }}
  .ref-thumb {{ position: relative; aspect-ratio: 3/2; }}
  .ref-thumb img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 4px; border: 1px solid var(--line); }}
  .ref-role {{ position: absolute; bottom: 1px; left: 1px; right: 1px;
    font-size: 8px; color: #fff; background: rgba(0,0,0,0.55); padding: 1px 3px; border-radius: 2px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: center; }}

  .user-prompt {{
    width: 100%; min-height: 80px; padding: 10px 12px;
    border: 1px solid var(--line); border-radius: 8px; resize: vertical;
    font-family: inherit; font-size: 12px; background: #fafafa; line-height: 1.5;
  }}

  .spec-details {{ margin-top: 10px; border: 1px solid var(--line); border-radius: 8px; background: #fafafa; }}
  .spec-details summary {{ cursor: pointer; padding: 8px 12px; font-size: 11px; color: var(--fg-soft); font-weight: 600; outline: none; }}
  .spec-details summary::-webkit-details-marker {{ display: none; }}
  .spec-list {{ padding: 4px 12px 12px; font-size: 11px; color: var(--fg-soft); line-height: 1.7; }}
  .spec-list b {{ color: var(--fg); font-weight: 600; margin-right: 4px; }}

  .status-line {{ font-size: 12px; color: var(--muted); }}
  .status-line b {{ color: var(--fg); font-weight: 600; margin-left: 4px; }}

  /* === Sticky tabs + model toggle === */
  .tabs-bar {{
    position: sticky; top: 56px; z-index: 30; background: var(--bg-alt);
    padding: 4px 0 0; display: flex; gap: 12px; align-items: stretch;
  }}
  .tabs {{
    display: flex; gap: 0; background: #fff; border: 1px solid var(--line);
    border-radius: 12px; padding: 0 12px; overflow-x: auto; flex: 1;
  }}
  .tab {{
    padding: 12px 18px; background: transparent; border: none;
    border-bottom: 2px solid transparent; margin-bottom: -1px;
    font-family: inherit; font-size: 13px; color: #666; cursor: pointer; white-space: nowrap;
  }}
  .tab.active {{ color: var(--fg); border-bottom-color: var(--fg); font-weight: 600; }}
  .tab.disabled {{ opacity: 0.3; cursor: not-allowed; }}

  .model-toggle {{
    display: inline-flex; align-items: center; padding: 4px;
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
  }}
  .m-btn {{
    padding: 8px 14px; background: transparent; border: none;
    font-family: inherit; font-size: 12px; cursor: pointer; color: var(--muted);
    border-radius: 8px; font-weight: 600;
  }}
  .m-btn.active {{ background: var(--fg); color: #fff; }}

  /* === DUAL GRID — panel-level rows === */
  .dual-grid {{
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
    margin-top: 16px; overflow: hidden;
  }}
  .dual-header {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 0;
    border-bottom: 1px solid var(--line); background: #fafafa;
    position: sticky; top: 120px; z-index: 20;
  }}
  .dual-h-left, .dual-h-right {{
    padding: 10px 20px; font-size: 12px; font-weight: 600; color: #444;
  }}
  .dual-h-left {{ border-right: 1px solid var(--line); }}

  .dual-panel {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 0;
    border-bottom: 1px solid var(--line-soft);
    scroll-margin-top: 160px;
  }}
  .dual-panel:last-child {{ border-bottom: none; }}
  .cell {{ padding: 20px; min-width: 0; }}
  .cell.orig {{ border-right: 1px solid var(--line); background: #fff; }}
  .cell.swap {{ background: #fafafa; }}
  .cell img {{ max-width: 100%; display: block; margin: 0 auto; border-radius: 4px; }}
  .cover-row .cell img {{ max-width: 480px; }}

  /* Section divider (inside cells) */
  .sec-divider {{ display: flex; align-items: baseline; gap: 12px; margin: 0 0 16px; }}
  .sec-divider .sec-name {{ font-size: 13px; font-weight: 700; padding: 4px 10px;
    background: var(--accent-soft); border-left: 3px solid var(--accent); border-radius: 0 4px 4px 0; }}
  .sec-divider .sec-range {{ font-size: 10px; color: var(--muted); font-family: ui-monospace, monospace; }}
  .sec-divider-cover .sec-name {{ background: #e8f4ff; border-left-color: #2563eb; }}

  /* swap image slots — model toggled */
  .swap-img-wrap {{ position: relative; }}
  .swap-slot {{ display: none; position: relative; }}
  .view[data-current-model="nano_banana_pro"] .swap-slot[data-model="nano_banana_pro"] {{ display: block; }}
  .view[data-current-model="gpt_image"] .swap-slot[data-model="gpt_image"] {{ display: block; }}
  .swap-slot.pending {{ align-items: center; justify-content: center; min-height: 200px;
    background: #f8f8f8; border-radius: 6px; }}
  .view[data-current-model="nano_banana_pro"] .swap-slot.pending[data-model="nano_banana_pro"] {{ display: flex; }}
  .view[data-current-model="gpt_image"] .swap-slot.pending[data-model="gpt_image"] {{ display: flex; }}
  .swap-pending-mark {{ font-size: 11px; color: var(--muted); }}
  .swap-score-overlay {{
    position: absolute; bottom: 8px; right: 8px;
    font-size: 10px; padding: 3px 8px; border-radius: 4px;
    background: rgba(0,0,0,0.65); color: #fff; font-family: ui-monospace, monospace;
  }}
  .swap-score-overlay.pass {{ background: rgba(22, 163, 74, 0.85); }}
  .swap-score-overlay.fail {{ background: rgba(220, 38, 38, 0.85); }}

  /* panel-copy — HTML 카피 */
  .panel-copy {{
    margin-top: 14px; padding: 12px 16px;
    background: #fff; border: 1px solid var(--line); border-radius: 8px;
  }}
  .panel-copy h4 {{ margin: 0 0 6px; font-size: 15px; font-weight: 700; color: var(--fg); letter-spacing: -0.01em; }}
  .panel-copy p {{ margin: 0; font-size: 13px; color: var(--fg-soft); line-height: 1.6; }}
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
  // anchor IDs: sec-{{rank}}-{{slug}} (cover) or sec-{{rank}}-{{slug}} attached to a .dual-panel
  const targetId = slug === 'cover' ? `sec-${{rank}}-cover` : `sec-${{rank}}-${{slug}}`;
  const target = view.querySelector(`#${{targetId}}`);
  if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
}}

document.addEventListener('DOMContentLoaded', () => {{
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

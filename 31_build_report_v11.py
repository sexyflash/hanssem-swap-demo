"""Report v11 — feedback round 6 final UI polish.

변경:
- panel 단위 row grid 복원 (좌우 자동 height align)
- 좌측 = 한샘 panel 이미지만 (panel 이미지에 텍스트 박혀있어 그대로 보존)
- 우측 = swap 이미지 + LLM 카피 (한샘 톤 디자인 통일)
- QA overlay:
  · 좌상단 큰 panel# (둥근 칩)
  · 우상단 점수 작게 + i 클릭하면 QA notes 펼침 (default 가림 안 함)
- zone별 HTML 테이블:
  · size_chart → 좌방석/등쿠션 firmness/사이즈 테이블
  · material_swatch → 마감재 spec 테이블
  · structure_chart → 구조 spec 테이블
  · color_option → 컬러 swatch + 이름 grid
- QA attempt 토글 (1/2/3 회차)
- 디자인 통일 (제목 18px h4 + 본문 14px p, 한샘 톤)
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
TPL_ROOT = HERE / "templates"
USER_PROD_ROOT = HERE / "user_products"
OUT = HERE / "report" / "index.html"
OUT.parent.mkdir(exist_ok=True)

data = json.loads((HERE / "top6_template_urls.json").read_text())
milo_dir = USER_PROD_ROOT / "milo_777039"
auto_output = json.loads((milo_dir / "auto_pipeline_output.json").read_text())
spec = auto_output["spec"]
visual = auto_output["visual"]
panel_copy = json.loads((TPL_ROOT / "01_sofa_992474/panel_copy.json").read_text())["copies"]
tpl_layouts = {p["panel"]: p for p in json.loads(
    (TPL_ROOT / "01_sofa_992474/panel_layout_types.json").read_text()
)["panels"] if "panel_idx" in p}

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


def get_v4_results(t):
    if t["rank"] != 1:
        return None
    sr = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}" / "swap_results"
    latest = sr / "latest_v4.txt"
    if not latest.exists():
        return None
    run_name = latest.read_text().strip()
    run_dir = sr / run_name
    summary = json.loads((run_dir / "summary.json").read_text())
    by_label = {c["label"]: c for c in summary["cells"]}
    return {
        "run_dir_rel": f"../templates/{t['rank']:02d}_{t['category']}_{t['gdsNo']}/swap_results/{run_name}/gpt_image",
        "summary": summary, "by_label": by_label,
    }


def cover_url_template(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    cov = TPL_ROOT / dir_name / "_cover_1000.jpg"
    if cov.exists():
        return f"../templates/{dir_name}/_cover_1000.jpg"
    thumbs = list((TPL_ROOT / dir_name).glob("_thumbnail.*"))
    return f"../templates/{dir_name}/{thumbs[0].name}" if thumbs else ""


def panel_local_url(t, idx):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    matches = list((TPL_ROOT / dir_name).glob(f"panel_{idx:02d}.*"))
    return f"../templates/{dir_name}/{matches[0].name}" if matches else ""


def build_zone_table(zone: str) -> str:
    """zone별 HTML 마감재/사이즈/구조 테이블."""
    dims = spec.get("dimensions", {}) or {}
    mat = spec.get("material", {}) or {}
    colors = spec.get("colors") or []

    if zone == "size_chart":
        return f"""
<table class="spec-table">
  <tr><th colspan="2">사이즈 (단위: cm)</th></tr>
  <tr><td>전체</td><td>{dims.get('width_cm','?')} × {dims.get('depth_cm','?')} × {dims.get('height_cm','?')}</td></tr>
  <tr><td>좌방석 길이</td><td>{dims.get('seat_depth_cm','?')}</td></tr>
  <tr><td>좌방석 높이</td><td>{dims.get('seat_height_cm','?')}</td></tr>
  <tr><td>팔걸이 높이</td><td>{dims.get('arm_height_cm','?')}</td></tr>
  <tr><td>다리 높이</td><td>14</td></tr>
  <tr><td>좌방석 경도</td><td>{mat.get('cushion_firmness','?').split('/')[0].strip() if '/' in mat.get('cushion_firmness','') else '미디엄 소프트'}</td></tr>
  <tr><td>등쿠션 경도</td><td>{mat.get('cushion_firmness','?').split('/')[-1].strip() if '/' in mat.get('cushion_firmness','') else '소프트'}</td></tr>
</table>
"""
    if zone == "material_swatch":
        certs = ", ".join(mat.get('upholstery_certifications') or [])
        return f"""
<table class="spec-table">
  <tr><th colspan="2">마감재 / 내장재</th></tr>
  <tr><td>마감재 (패브릭)</td><td>{mat.get('upholstery','')}</td></tr>
  <tr><td>인증</td><td>{certs}</td></tr>
  <tr><td>좌방석 내장</td><td>{mat.get('seat_cushion','')}</td></tr>
  <tr><td>등쿠션 내장</td><td>{mat.get('back_cushion','')}</td></tr>
  <tr><td>프레임</td><td>{mat.get('frame','')}</td></tr>
</table>
"""
    if zone == "structure_chart":
        return f"""
<table class="spec-table">
  <tr><th colspan="2">내부 구조</th></tr>
  <tr><td>좌방석</td><td>{mat.get('seat_cushion','')}</td></tr>
  <tr><td>등쿠션</td><td>{mat.get('back_cushion','')}</td></tr>
  <tr><td>프레임</td><td>{mat.get('frame','')}</td></tr>
  <tr><td>특징</td><td>NEW 통스펀지 1단 (기존 샌드위치 4단 대비 내구성 UP)</td></tr>
</table>
"""
    if zone == "color_option":
        use_prod = "../user_products/milo_777039/use_product"
        # color name mapping (color_01=오트밀, color_02=라이트그레이, color_03=더스티로즈)
        labels = colors if len(colors) >= 3 else ["오트밀", "라이트그레이", "더스티로즈"]
        swatches = ""
        for i, color in enumerate(labels[:3], 1):
            swatches += f"""
<div class="color-chip">
  <img src="{use_prod}/color_{i:02d}.png" alt="{color}"/>
  <div class="color-name">{color}</div>
</div>
"""
        return f'<div class="color-grid">{swatches}</div>'
    return ""


def build_swap_cell(t, idx, swap_results):
    """우측 cell — swap image + QA tabs + LLM copy + zone-aware table."""
    sname = f"panel_{idx:02d}"
    cell = swap_results["by_label"].get(sname) if swap_results else None
    panel_meta = tpl_layouts.get(f"panel_{idx:02d}.jpg") or tpl_layouts.get(f"panel_{idx:02d}.gif") or {}
    zone = panel_meta.get("input_zone", "other")
    layout_type = panel_meta.get("layout_type", "flexible_staging")

    qa_tabs = ""
    qa_slots = ""
    if cell and cell.get("attempts"):
        attempts_with_img = [a for a in cell["attempts"] if a.get("image")]
        for ai, a in enumerate(attempts_with_img):
            strat = a.get("strategy", "?")[:6]
            prod = a.get("product_score", "-")
            comp = a.get("composition_score", "-")
            seats = a.get("seat_count_in_B", "?")
            text_flag = a.get("text_in_image")
            verdict = a.get("verdict", "?")
            badge_cls = "pass" if verdict == "pass" else "fail"
            is_active = (a["image"] == cell["final"]["image"]) if cell.get("final") else (ai == 0)
            tab_cls = "active" if is_active else ""
            slot_cls = "active" if is_active else ""
            tabs_label = f"#{ai+1} {strat}"
            qa_tabs += f'<button class="qa-tab {tab_cls}" data-panel="{idx}" data-attempt="{ai}" onclick="setAttempt({idx},{ai})">{tabs_label}</button>'
            img_url = f"{swap_results['run_dir_rel']}/{a['image']}"
            notes = (a.get("notes") or "").replace('"', '&quot;').replace('<', '&lt;')
            score_short = f"prod {prod} · comp {comp}" + (" · TEXT!" if text_flag else "")
            qa_slots += f"""
<div class="qa-slot {slot_cls}" data-panel="{idx}" data-attempt="{ai}">
  <img src="{img_url}" loading="lazy"/>
  <div class="panel-number-chip">{idx:02d}</div>
  <div class="qa-info-button {badge_cls}" onclick="toggleQA(this)">
    <span class="qa-info-score">{score_short}</span>
    <button class="qa-info-i">i</button>
  </div>
  <div class="qa-panel-detail">
    <div class="qa-detail-row"><b>점수</b> prod {prod} · comp {comp} · seats {seats}{' · TEXT!' if text_flag else ''}</div>
    <div class="qa-detail-row"><b>verdict</b> {verdict}</div>
    <div class="qa-detail-row"><b>strategy</b> {a.get('strategy','?')}</div>
    <div class="qa-detail-row"><b>이유</b> {notes}</div>
  </div>
</div>
"""
    else:
        qa_slots = '<div class="qa-pending">대기</div>'

    # LLM copy
    copy = panel_copy.get(sname, {})
    title = copy.get("title", "")
    body = copy.get("body", "")
    copy_html = ""
    if title or body:
        copy_html = f'<div class="panel-text"><h4>{title}</h4><p>{body}</p></div>'

    # zone table (under copy)
    table_html = build_zone_table(zone)
    table_block = f'<div class="zone-table-wrap">{table_html}</div>' if table_html else ""

    return f"""
<div class="cell swap">
  <div class="swap-image-wrap" data-panel-idx="{idx}">
    <div class="qa-tabs">{qa_tabs}</div>
    <div class="qa-slots">{qa_slots}</div>
  </div>
  {copy_html}
  {table_block}
</div>
"""


def build_cover_cell_swap(t, swap_results):
    cell = swap_results["by_label"].get("cover") if swap_results else None
    copy = panel_copy.get("cover", {})
    title = copy.get("title", "")
    body = copy.get("body", "")

    swap_html = ""
    if cell and cell.get("attempts"):
        attempts_with_img = [a for a in cell["attempts"] if a.get("image")]
        tabs = ""
        slots = ""
        for ai, a in enumerate(attempts_with_img):
            strat = a.get("strategy", "?")[:6]
            prod = a.get("product_score", "-")
            comp = a.get("composition_score", "-")
            seats = a.get("seat_count_in_B", "?")
            text_flag = a.get("text_in_image")
            verdict = a.get("verdict", "?")
            badge_cls = "pass" if verdict == "pass" else "fail"
            is_active = (a["image"] == cell["final"]["image"]) if cell.get("final") else (ai == 0)
            tab_cls = "active" if is_active else ""
            slot_cls = "active" if is_active else ""
            tabs += f'<button class="qa-tab {tab_cls}" data-panel="cover" data-attempt="{ai}" onclick="setAttempt(\'cover\',{ai})">#{ai+1} {strat}</button>'
            img_url = f"{swap_results['run_dir_rel']}/{a['image']}"
            notes = (a.get("notes") or "").replace('"', '&quot;').replace('<', '&lt;')
            score_short = f"prod {prod} · comp {comp}" + (" · TEXT!" if text_flag else "")
            slots += f"""
<div class="qa-slot cover-slot {slot_cls}" data-panel="cover" data-attempt="{ai}">
  <img class="cover-img" src="{img_url}"/>
  <div class="panel-number-chip cover-chip">00</div>
  <div class="qa-info-button {badge_cls}" onclick="toggleQA(this)">
    <span class="qa-info-score">{score_short}</span>
    <button class="qa-info-i">i</button>
  </div>
  <div class="qa-panel-detail">
    <div class="qa-detail-row"><b>점수</b> prod {prod} · comp {comp} · seats {seats}</div>
    <div class="qa-detail-row"><b>verdict</b> {verdict}</div>
    <div class="qa-detail-row"><b>strategy</b> {a.get('strategy','?')}</div>
    <div class="qa-detail-row"><b>이유</b> {notes}</div>
  </div>
</div>
"""
        swap_html = f'<div class="qa-tabs">{tabs}</div><div class="qa-slots">{slots}</div>'
    else:
        swap_html = '<div class="qa-pending">대기</div>'

    copy_html = f'<div class="panel-text"><h4>{title}</h4><p>{body}</p></div>' if (title or body) else ''

    return f"""
<div class="cell swap">
  <div class="swap-image-wrap" data-panel-idx="cover">{swap_html}</div>
  {copy_html}
</div>
"""


def build_tabs_bar(rank, sections_map):
    btns = []
    first_active_set = False
    for sec in SECTIONS:
        slug = SECTION_SLUGS[sec]
        has = True if sec == "커버" else bool(sections_map.get(sec))
        cls = "tab" + ("" if has else " disabled")
        if has and not first_active_set:
            cls += " active"
            first_active_set = True
        attrs = f'onclick="scrollToSection({rank}, \'{slug}\')"' if has else "disabled"
        btns.append(f'<button class="{cls}" data-slug="{slug}" {attrs}>{sec}</button>')
    return "\n".join(btns)


def build_zone_inputs():
    use_prod = "../user_products/milo_777039/use_product"
    zones_data = [
        ("제품 이미지", [f"p08_frame_0{i}.jpg" for i in [1, 2, 3]]),
        ("소재", ["material.png"]),
        ("컬러", [f"color_0{i}.png" for i in [1, 2, 3]]),
    ]
    out = ""
    for title, files in zones_data:
        thumbs = "".join(
            f'<div class="zone-thumb"><img src="{use_prod}/{f}" loading="lazy"/></div>'
            for f in files
        )
        out += f"""
<div class="zone-block">
  <div class="zone-label">{title} <span class="zone-count">{len(files)}장</span></div>
  <div class="zone-thumbs">{thumbs}</div>
</div>
"""
    return out


def build_process_card(t, swap_results):
    rank = t["rank"]
    tpl_price = t.get("price")
    tpl_price_str = f"{tpl_price:,}원" if tpl_price else ""
    is_done = swap_results is not None

    badge = '<span class="badge ready"><b>실행 완료</b></span>' if is_done else '<span class="badge"><b>대기</b></span>'

    dims = spec.get("dimensions", {}) or {}
    mat = spec.get("material", {}) or {}
    colors = spec.get("colors") or []
    seat_n = spec.get("seat_count", 2)
    features = spec.get("key_features", [])

    auto_req = (
        f"제품: {spec.get('product_name')}. "
        f"vision — {visual.get('full_visual_paragraph','')[:200]} "
        f"사이즈 {dims.get('width_cm','?')}×{dims.get('depth_cm','?')}×{dims.get('height_cm','?')}cm, "
        f"좌방석 {dims.get('seat_depth_cm','?')}×{dims.get('seat_height_cm','?')}cm, 팔걸이 {dims.get('arm_height_cm','?')}cm. "
        f"패브릭 {mat.get('upholstery','')}, 좌방석 {mat.get('cushion_firmness','')}, 컬러 {', '.join(colors)}. "
        f"원본 layout 유지 + sofa만 정밀 swap. {seat_n}인용 STRICT."
    )

    if swap_results:
        cells = swap_results["summary"]["cells"]
        wall = swap_results["summary"].get("wall_seconds", 0)
        n_pass = sum(1 for c in cells if c["passed"])
        avg_prod = round(sum((c.get("final") or {}).get("product_score", 0) for c in cells) / max(1, len(cells)), 1)
        avg_comp = round(sum((c.get("final") or {}).get("composition_score", 0) for c in cells) / max(1, len(cells)), 1)
        strat_counts = {"aligned": 0, "overpaint": 0, "smart_sheet": 0}
        for c in cells:
            for s in c.get("strategies_used", []):
                strat_counts[s] = strat_counts.get(s, 0) + 1
        strat_html = " · ".join(f"{k} <b>{v}</b>" for k, v in strat_counts.items())
        status_col = f"""
<div class="proc-h">상태 (실행 완료)</div>
<div class="status-line">처리 시간 <b>{wall:.0f}s</b></div>
<div class="status-line">passer <b>{n_pass}/{len(cells)}</b> · prod <b>{avg_prod}</b> · comp <b>{avg_comp}</b></div>
<div class="status-line">strategy: {strat_html}</div>
"""
    else:
        status_col = '<div class="proc-h">상태</div><div class="status-line">처리 시간 <b>—</b></div>'

    return f"""
<details class="process-card">
  <summary>
    <span class="proc-title">공정 설정</span>
    <span class="proc-summary">
      <span class="badge tpl-badge">템플릿 <b>#{rank} {t.get('category')}</b> · {t['name'][:24]}{'…' if len(t['name'])>24 else ''}</span>
      <span class="badge"><b>GPT image</b> · 자동 3-strategy fallback</span>
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
        <div class="proc-h">입력 — zone 분리</div>
        {build_zone_inputs()}
      </div>
      <div class="proc-col proc-col-wide">
        <div class="proc-h">입력 — 사용자 LLM 요청 (vision 자동 생성)</div>
        <textarea class="user-prompt">{auto_req}</textarea>
        <details class="spec-details">
          <summary>밀로 spec 전체 (vision 추출)</summary>
          <div class="spec-list">
            <div><b>제품</b> {spec.get('product_name')} ({seat_n}인용)</div>
            <div><b>사이즈</b> {dims.get('width_cm','?')}×{dims.get('depth_cm','?')}×{dims.get('height_cm','?')}cm · 좌방석 {dims.get('seat_depth_cm','?')}×{dims.get('seat_height_cm','?')} · 팔걸이 {dims.get('arm_height_cm','?')}cm</div>
            <div><b>패브릭</b> {mat.get('upholstery','')}</div>
            <div><b>인증</b> {', '.join(mat.get('upholstery_certifications', []))}</div>
            <div><b>좌방석</b> {mat.get('seat_cushion','')}</div>
            <div><b>등쿠션</b> {mat.get('back_cushion','')}</div>
            <div><b>경도</b> {mat.get('cushion_firmness','')}</div>
            <div><b>프레임</b> {mat.get('frame','')}</div>
            <div><b>컬러</b> {', '.join(colors)}</div>
            <div><b>특징</b> {' · '.join(features[:5])}</div>
          </div>
        </details>
      </div>
      <div class="proc-col">{status_col}</div>
    </div>
  </div>
</details>
"""


cover_imgs = {t["gdsNo"]: cover_url_template(t) for t in data["top6"]}


def chip(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    name_short = t["name"][:24] + ("…" if len(t["name"]) > 24 else "")
    swap = get_v4_results(t)
    ready = '<span class="chip-ready done">✓</span>' if swap else ""
    return f"""
<button class="chip {'selected' if rank == 1 else ''}" data-rank="{rank}" onclick="selectTpl({rank})">
  {ready}<span class="chip-rank">#{rank}</span>
  <img class="chip-cover" src="{cover_imgs[gds]}"/>
  <span class="chip-meta"><span class="chip-cat">{cat}</span><span class="chip-name">{name_short}</span></span>
</button>"""


def view(t):
    rank = t["rank"]
    is_first = rank == 1
    swap_results = get_v4_results(t) if rank == 1 else None
    meta_path = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}/meta.json"
    meta = json.loads(meta_path.read_text())
    panel_count = meta.get("detail_img_count") or meta.get("panel_count") or len(meta.get("detail_imgs", []))
    sections_map = assign_sections(panel_count)

    # build rows: cover + N panels
    rows = []
    # cover
    cover_src_t = cover_url_template(t)
    cover_copy = panel_copy.get("cover", {})
    cover_swap = build_cover_cell_swap(t, swap_results)
    cover_row = f"""
<div class="dual-row cover-row" id="sec-cover-{rank}">
  <div class="cell orig">
    <div class="sec-divider cover-divider"><span class="sec-name">커버</span><span class="sec-range">1:1 대표</span></div>
    <div class="orig-image-wrap">
      <img class="cover-img" src="{cover_src_t}"/>
      <div class="panel-number-chip cover-chip">00</div>
    </div>
  </div>
  {cover_swap}
</div>
"""
    rows.append(cover_row)

    # panel rows
    for i in range(1, panel_count + 1):
        anchor_id = ""
        sec_div = ""
        for sec_name, indices in sections_map.items():
            if sec_name == "커버" or not indices:
                continue
            if indices[0] == i:
                slug = SECTION_SLUGS[sec_name]
                anchor_id = f'id="sec-{slug}-{rank}"'
                rng = f"panel {indices[0]}" + (f"–{indices[-1]}" if len(indices) > 1 else "")
                sec_div = f'<div class="sec-divider section-marker"><span class="sec-name">{sec_name}</span><span class="sec-range">{rng}</span></div>'
                break

        orig_src = panel_local_url(t, i)
        swap_cell = build_swap_cell(t, i, swap_results)
        row = f"""
{sec_div}
<div class="dual-row" {anchor_id} data-panel-idx="{i}">
  <div class="cell orig">
    <div class="orig-image-wrap">
      <img src="{orig_src}" alt="panel_{i:02d}" loading="lazy"/>
      <div class="panel-number-chip">{i:02d}</div>
    </div>
  </div>
  {swap_cell}
</div>
"""
        rows.append(row)

    rows_html = "\n".join(rows)

    return f"""
<div class="view {'active' if is_first else ''}" data-rank="{rank}">
  {build_process_card(t, swap_results)}
  <div class="tabs-bar">
    <div class="tabs">{build_tabs_bar(rank, sections_map)}</div>
  </div>
  <div class="dual-grid" data-rank="{rank}">
    <div class="dual-header">
      <div class="dual-h-left">원본 한샘 detail</div>
      <div class="dual-h-right">swap · 밀로 패브릭소파 2인용 · GPT</div>
    </div>
    {rows_html}
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
<title>가구 detail 템플릿 swap — v11</title>
<link rel="stylesheet" href="https://res.remodeling.hanssem.com/font/pretendard/pretendard.css"/>
<style>
  :root {{
    --bg: #fff; --bg-alt: #f4f4f6;
    --fg: #1a1a1a; --fg-soft: #555; --muted: #888;
    --line: #e5e5e5; --line-soft: #efefef;
    --accent: #ff7a00; --accent-soft: #fff5ec;
    --good: #16a34a; --bad: #dc2626;
    --topbar-h: 56px; --tabs-h: 50px;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Pretendard", -apple-system, system-ui, sans-serif;
    background: var(--bg-alt); color: var(--fg);
    -webkit-font-smoothing: antialiased; font-size: 14px; line-height: 1.5;
  }}
  .topbar {{ position: sticky; top: 0; z-index: 100; background: #fff;
    border-bottom: 1px solid var(--line); padding: 12px 24px; height: var(--topbar-h); }}
  .topbar-row {{ display: flex; align-items: center; gap: 16px; max-width: 1600px; margin: 0 auto; overflow-x: auto; }}
  .topbar h1 {{ margin: 0; font-size: 13px; font-weight: 600; color: var(--fg-soft); white-space: nowrap; }}
  .chips {{ display: flex; gap: 8px; flex: 1; }}
  .chip {{ position: relative; display: flex; align-items: center; gap: 8px;
    padding: 6px 14px 6px 6px; border: 1px solid var(--line); background: #fff;
    border-radius: 999px; cursor: pointer; font-family: inherit; font-size: 12px;
    color: #555; white-space: nowrap; }}
  .chip.selected {{ border-color: var(--fg); background: var(--fg); color: #fff; }}
  .chip-ready {{ position: absolute; top: 2px; right: 4px; color: var(--good); font-size: 10px; font-weight: 700; }}
  .chip-cover {{ width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }}
  .chip-rank {{ font-weight: 700; color: var(--accent); }}
  .chip-meta {{ display: flex; flex-direction: column; align-items: flex-start; line-height: 1.15; }}
  .chip-cat {{ font-size: 10px; opacity: 0.7; }}
  .chip-name {{ font-size: 11px; }}

  .view {{ display: none; padding: 24px 32px; max-width: 1600px; margin: 0 auto; }}
  .view.active {{ display: block; }}

  /* === Process Card === */
  .process-card {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; margin-bottom: 16px; overflow: hidden; }}
  .process-card > summary {{ list-style: none; cursor: pointer; padding: 14px 20px;
    display: flex; align-items: center; gap: 14px; background: #fff; }}
  .process-card > summary::-webkit-details-marker {{ display: none; }}
  .proc-title {{ font-size: 13px; font-weight: 600; }}
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

  .proc-grid {{ display: grid; grid-template-columns: 1.1fr 1.7fr 1fr; gap: 24px; }}
  .proc-col {{ display: flex; flex-direction: column; gap: 8px; min-width: 0; }}
  .proc-h {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; }}

  .zone-block {{ padding: 10px 12px; background: var(--bg-alt); border: 1px solid var(--line); border-radius: 8px; margin-top: 8px; }}
  .zone-label {{ font-size: 12px; font-weight: 600; margin-bottom: 6px; }}
  .zone-count {{ font-size: 10px; color: var(--muted); font-weight: 400; margin-left: 4px; }}
  .zone-thumbs {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(48px, 1fr)); gap: 4px; }}
  .zone-thumb {{ aspect-ratio: 1/1; }}
  .zone-thumb img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 3px; border: 1px solid var(--line); background: #fff; }}

  .user-prompt {{ width: 100%; min-height: 140px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 8px; resize: vertical; font-family: inherit; font-size: 12px; background: #fafafa; line-height: 1.55; }}
  .spec-details {{ margin-top: 10px; border: 1px solid var(--line); border-radius: 8px; background: #fafafa; }}
  .spec-details summary {{ cursor: pointer; padding: 8px 12px; font-size: 11px; color: var(--fg-soft); font-weight: 600; outline: none; }}
  .spec-details summary::-webkit-details-marker {{ display: none; }}
  .spec-list {{ padding: 4px 12px 12px; font-size: 11px; color: var(--fg-soft); line-height: 1.8; }}
  .spec-list b {{ color: var(--fg); font-weight: 600; margin-right: 4px; }}

  .status-line {{ font-size: 12px; color: var(--muted); margin-bottom: 4px; }}
  .status-line b {{ color: var(--fg); font-weight: 600; margin-left: 4px; }}

  /* Tabs */
  .tabs-bar {{ position: sticky; top: var(--topbar-h); z-index: 30; background: var(--bg-alt); padding: 4px 0 0; height: calc(var(--tabs-h) + 4px); }}
  .tabs {{ display: flex; background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 0 12px; overflow-x: auto; }}
  .tab {{ padding: 12px 18px; background: transparent; border: none; border-bottom: 2px solid transparent; margin-bottom: -1px; font-family: inherit; font-size: 13px; color: #666; cursor: pointer; white-space: nowrap; }}
  .tab.active {{ color: var(--fg); border-bottom-color: var(--fg); font-weight: 600; }}
  .tab.disabled {{ opacity: 0.3; cursor: not-allowed; }}

  /* === Dual Grid (panel-row based) === */
  .dual-grid {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; margin-top: 12px; overflow: hidden; }}
  .dual-header {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-bottom: 1px solid var(--line); background: #fafafa;
    position: sticky; top: calc(var(--topbar-h) + var(--tabs-h)); z-index: 20; }}
  .dual-h-left, .dual-h-right {{ padding: 12px 20px; font-size: 12px; font-weight: 600; color: #444; }}
  .dual-h-left {{ border-right: 1px solid var(--line); }}

  .sec-divider {{ display: flex; align-items: baseline; gap: 12px;
    padding: 18px 20px 8px; background: linear-gradient(to bottom, #fafafa, #fff);
    border-top: 1px solid var(--line-soft);
    scroll-margin-top: calc(var(--topbar-h) + var(--tabs-h) + 40px); }}
  .sec-divider.section-marker {{ }}
  .sec-divider .sec-name {{ font-size: 13px; font-weight: 700; padding: 4px 12px;
    background: var(--accent-soft); border-left: 3px solid var(--accent); border-radius: 0 4px 4px 0; }}
  .sec-divider .sec-range {{ font-size: 10px; color: var(--muted); font-family: ui-monospace, monospace; }}
  .cover-divider .sec-name {{ background: #e8f4ff; border-left-color: #2563eb; }}

  .dual-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0;
    border-bottom: 1px solid var(--line-soft);
    scroll-margin-top: calc(var(--topbar-h) + var(--tabs-h) + 40px); }}
  .dual-row:last-child {{ border-bottom: none; }}
  .cell {{ padding: 24px 28px; min-width: 0; display: flex; flex-direction: column; gap: 12px; }}
  .cell.orig {{ border-right: 1px solid var(--line); background: #fff; }}
  .cell.swap {{ background: #fafafa; }}
  .cover-row .cell .cover-img {{ max-width: 480px; aspect-ratio: 1/1; object-fit: contain; background: #fff; }}

  /* image wrap with number chip + cover divider */
  .orig-image-wrap, .swap-image-wrap {{ position: relative; }}
  .orig-image-wrap > img {{ max-width: 100%; display: block; margin: 0 auto; border-radius: 6px; }}
  .swap-image-wrap > .qa-slots {{ position: relative; }}
  .qa-slot {{ display: none; position: relative; }}
  .qa-slot.active {{ display: block; }}
  .qa-slot > img {{ max-width: 100%; display: block; margin: 0 auto; border-radius: 6px; }}
  .qa-slot.cover-slot img {{ max-width: 480px; }}
  .qa-pending {{ padding: 80px; text-align: center; color: var(--muted); background: #f3f3f3; border-radius: 6px; }}

  /* Panel number chip (좌상단) */
  .panel-number-chip {{
    position: absolute; top: 12px; left: 12px;
    width: 36px; height: 36px; border-radius: 50%;
    background: rgba(0,0,0,0.78); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; font-family: ui-monospace, Menlo, monospace;
    letter-spacing: -0.02em;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2); z-index: 5;
  }}

  /* QA tabs (attempt toggle) */
  .qa-tabs {{ display: flex; gap: 4px; margin-bottom: 6px; }}
  .qa-tab {{ font-size: 10px; padding: 4px 8px; border: 1px solid var(--line); background: #fff;
    border-radius: 4px; cursor: pointer; color: var(--muted); font-family: inherit; }}
  .qa-tab.active {{ background: var(--fg); color: #fff; border-color: var(--fg); }}

  /* QA info button — small, in top-right */
  .qa-info-button {{
    position: absolute; top: 12px; right: 12px;
    display: flex; align-items: center; gap: 6px;
    padding: 4px 8px 4px 10px; border-radius: 6px;
    background: rgba(255,255,255,0.92); color: var(--fg);
    font-size: 10px; font-family: ui-monospace, Menlo, monospace;
    box-shadow: 0 1px 4px rgba(0,0,0,0.15);
    cursor: pointer; user-select: none; z-index: 5;
    border: 1px solid rgba(0,0,0,0.08);
  }}
  .qa-info-button.pass {{ border-left: 3px solid var(--good); }}
  .qa-info-button.fail {{ border-left: 3px solid var(--bad); }}
  .qa-info-i {{ width: 16px; height: 16px; border-radius: 50%;
    background: var(--fg-soft); color: #fff; border: none;
    font-size: 10px; font-style: italic; font-family: serif; font-weight: 700;
    display: inline-flex; align-items: center; justify-content: center;
    cursor: pointer; padding: 0; }}

  /* QA detail panel (hidden by default) */
  .qa-panel-detail {{
    position: absolute; top: 50px; right: 12px;
    background: rgba(0,0,0,0.92); color: #fff;
    padding: 10px 12px; border-radius: 6px;
    font-size: 11px; font-family: ui-monospace, Menlo, monospace;
    line-height: 1.55; max-width: 320px; min-width: 240px;
    display: none; z-index: 10;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }}
  .qa-panel-detail.open {{ display: block; }}
  .qa-detail-row {{ margin-bottom: 4px; }}
  .qa-detail-row b {{ color: var(--accent); margin-right: 4px; }}

  /* Panel text (LLM copy) — 한샘 톤 디자인 통일 */
  .panel-text {{
    margin-top: 0; padding: 0;
    text-align: left;
  }}
  .panel-text h4 {{
    margin: 0 0 8px; font-size: 18px; font-weight: 700;
    color: var(--fg); letter-spacing: -0.02em; line-height: 1.4;
  }}
  .panel-text p {{
    margin: 0; font-size: 14px; color: var(--fg-soft);
    line-height: 1.7;
  }}

  /* zone HTML tables */
  .zone-table-wrap {{ margin-top: 14px; }}
  .spec-table {{
    width: 100%; border-collapse: collapse;
    font-size: 13px; color: var(--fg);
  }}
  .spec-table th {{
    background: var(--bg-alt); padding: 8px 12px;
    font-size: 12px; font-weight: 700;
    text-align: left; border-bottom: 2px solid var(--line);
  }}
  .spec-table td {{
    padding: 8px 12px; border-bottom: 1px solid var(--line-soft);
    line-height: 1.5;
  }}
  .spec-table td:first-child {{
    color: var(--muted); font-size: 12px; width: 35%; font-weight: 500;
  }}

  /* color grid */
  .color-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 14px; }}
  .color-chip {{ display: flex; flex-direction: column; gap: 6px; align-items: center; }}
  .color-chip img {{ width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 8px; border: 1px solid var(--line); }}
  .color-name {{ font-size: 12px; color: var(--fg); font-weight: 500; }}
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
function scrollToSection(rank, slug) {{
  const view = document.querySelector(`.view[data-rank="${{rank}}"]`);
  if (!view) return;
  view.querySelectorAll('.tab').forEach(t => {{
    if (t.classList.contains('disabled')) return;
    t.classList.toggle('active', t.dataset.slug === slug);
  }});
  const targetId = `sec-${{slug}}-${{rank}}`;
  const target = view.querySelector(`#${{targetId}}`);
  if (!target) return;
  const rect = target.getBoundingClientRect();
  const offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--topbar-h'))
               + parseInt(getComputedStyle(document.documentElement).getPropertyValue('--tabs-h')) + 80;
  window.scrollTo({{ top: window.scrollY + rect.top - offset, behavior: 'smooth' }});
}}
function setAttempt(panelKey, attemptIdx) {{
  const wrap = document.querySelector(`.swap-image-wrap[data-panel-idx="${{panelKey}}"]`);
  if (!wrap) return;
  wrap.querySelectorAll('.qa-tab').forEach(t => t.classList.toggle('active', +t.dataset.attempt === attemptIdx));
  wrap.querySelectorAll('.qa-slot').forEach(s => s.classList.toggle('active', +s.dataset.attempt === attemptIdx));
}}
function toggleQA(btn) {{
  const slot = btn.closest('.qa-slot') || btn.closest('.swap-image-wrap');
  if (!slot) return;
  const panel = slot.querySelector('.qa-panel-detail');
  if (panel) panel.classList.toggle('open');
}}
// click-outside to close QA panels
document.addEventListener('click', e => {{
  if (!e.target.closest('.qa-info-button')) {{
    document.querySelectorAll('.qa-panel-detail.open').forEach(p => p.classList.remove('open'));
  }}
}});
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT}")
print(f"size: {OUT.stat().st_size // 1024}KB")

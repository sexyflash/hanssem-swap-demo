"""Report v9 — feedback round 5.

변경:
- K1/K2/K3 라디오 제거. "자동 3-strategy fallback" 한 줄로 표시
- 좌우 panel 단위 grid row → CSS grid로 같은 row 자동 height match
- 탭 클릭 정확 scroll (scroll-margin-top + sticky offset 고려)
- panel-copy 디자인 원본 톤 통합 (별도 박스 X, 미니멀)
- 메타/입력 라벨 정리:
    · 입력 — 사용자 업로드 (GIF 3 frames)
    · 입력 — 사용자 LLM 요청 (자동 풍부 텍스트)
    · 밀로 spec (vision 추출) — 펼치기
- cover 매핑 = v3 run의 cover label만
- 결과 표시 = v3 run 전용 (이전 run은 archive)
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
TPL_ROOT = HERE / "templates"
USER_PROD = HERE / "user_products" / "milo_777039"
OUT = HERE / "report" / "index.html"
OUT.parent.mkdir(exist_ok=True)

data = json.loads((HERE / "top6_template_urls.json").read_text())
milo_fact = json.loads((USER_PROD / "fact.json").read_text())
visual = json.loads((USER_PROD / "visual_description.json").read_text())
milo_spec = visual["spec_from_page"]
gif_visual = visual["gif_visual"]
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


def get_v3_results(t):
    """Use only the v3 run for #1."""
    if t["rank"] != 1:
        return None
    sr = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}" / "swap_results"
    latest_file = sr / "latest_v3.txt"
    if not latest_file.exists():
        # fallback: find any v3_* dir
        v3_dirs = sorted([d for d in sr.iterdir() if d.name.startswith("v3_")])
        if not v3_dirs:
            return None
        run_dir = v3_dirs[-1]
    else:
        run_dir = sr / latest_file.read_text().strip()
    summary_file = run_dir / "summary.json"
    if not summary_file.exists():
        return None
    summary = json.loads(summary_file.read_text())
    # build by_label index
    by_label = {}
    for c in summary["cells"]:
        by_label[c["label"]] = c
    return {
        "run_dir_rel": f"../templates/{t['rank']:02d}_{t['category']}_{t['gdsNo']}/swap_results/{run_dir.name}",
        "summary": summary,
        "by_label": by_label,
    }


def cover_url_thumb(t):
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


def swap_img_for(swap_results, label):
    cell = swap_results["by_label"].get(label) if swap_results else None
    if not cell or not cell.get("final"):
        return None
    final = cell["final"]
    img_name = final.get("image")
    if not img_name:
        return None
    return {
        "src": f"{swap_results['run_dir_rel']}/gpt_image/{img_name}",
        "cell": cell, "final": final,
    }


def section_marker(idx, sections_map, side="orig"):
    """Return divider HTML if idx is the first panel of any section."""
    for sec_name, indices in sections_map.items():
        if sec_name == "커버" or not indices:
            continue
        if indices and indices[0] == idx:
            slug = SECTION_SLUGS[sec_name]
            rng = f"panel {indices[0]}" + (f"–{indices[-1]}" if len(indices) > 1 else "")
            return f'<div class="sec-divider" data-sec="{slug}"><span class="sec-name">{sec_name}</span><span class="sec-range">{rng}</span></div>'
    return ""


def build_cover_row(t, swap_results):
    cover_src = cover_url_thumb(t)
    copy = panel_copy.get("cover", {})
    title = copy.get("title", "")
    body = copy.get("body", "")

    swap_info = swap_img_for(swap_results, "cover")
    if swap_info:
        f = swap_info["final"]
        cell = swap_info["cell"]
        passed = cell.get("passed", False)
        prod = f.get("product_score", "-")
        comp = f.get("composition_score", "-")
        seats = f.get("seat_count_in_B", "?")
        text_flag = f.get("text_in_image")
        badge_cls = "pass" if passed else "fail"
        strat = "/".join(cell.get("strategies_used", []))
        tip = f"prod {prod} · comp {comp} · seats {seats}" + (" · TEXT!" if text_flag else "")
        swap_html = f"""
<img class="cover-img" src="{swap_info['src']}" loading="lazy"/>
<div class="swap-score-overlay {badge_cls}" title="{tip}">{tip} ({strat})</div>
"""
    else:
        swap_html = '<div class="swap-pending">대기</div>'

    return f"""
<div class="dual-panel cover-row" id="sec-cover">
  <div class="cell orig">
    <div class="sec-divider cover-divider"><span class="sec-name">커버</span><span class="sec-range">1:1 대표</span></div>
    <img class="cover-img" src="{cover_src}" loading="eager"/>
    <div class="panel-text">
      <h4>원본 (한샘 대표 이미지)</h4>
    </div>
  </div>
  <div class="cell swap">
    <div class="sec-divider cover-divider"><span class="sec-name">커버 swap</span><span class="sec-range">밀로 2인용</span></div>
    <div class="swap-img-wrap">{swap_html}</div>
    <div class="panel-text">
      <h4>{title}</h4>
      <p>{body}</p>
    </div>
  </div>
</div>
"""


def build_panel_row(t, idx, sections_map, swap_results):
    orig_src = panel_local_url(t, idx)
    copy = panel_copy.get(f"panel_{idx:02d}", {})
    title = copy.get("title", "")
    body = copy.get("body", "")

    swap_info = swap_img_for(swap_results, f"panel_{idx:02d}")
    if swap_info:
        f = swap_info["final"]
        cell = swap_info["cell"]
        passed = cell.get("passed", False)
        prod = f.get("product_score", "-")
        comp = f.get("composition_score", "-")
        seats = f.get("seat_count_in_B", "?")
        text_flag = f.get("text_in_image")
        badge_cls = "pass" if passed else "fail"
        strat = "/".join(cell.get("strategies_used", []))
        tip = f"prod {prod} · comp {comp} · seats {seats}" + (" · TEXT!" if text_flag else "")
        swap_html = f"""
<img src="{swap_info['src']}" loading="lazy"/>
<div class="swap-score-overlay {badge_cls}" title="{tip}">{tip} ({strat})</div>
"""
    else:
        swap_html = '<div class="swap-pending">대기</div>'

    # section marker — anchor id only on the row containing the first panel of a section
    anchor_id = ""
    sec_div = ""
    for sec_name, indices in sections_map.items():
        if sec_name == "커버" or not indices:
            continue
        if indices[0] == idx:
            slug = SECTION_SLUGS[sec_name]
            anchor_id = f'id="sec-{slug}"'
            rng = f"panel {indices[0]}" + (f"–{indices[-1]}" if len(indices) > 1 else "")
            sec_div = f'<div class="sec-divider section-marker"><span class="sec-name">{sec_name}</span><span class="sec-range">{rng}</span></div>'
            break

    return f"""
{sec_div}
<div class="dual-panel" {anchor_id} data-panel-idx="{idx}">
  <div class="cell orig">
    <img src="{orig_src}" alt="panel_{idx:02d}" loading="lazy"/>
  </div>
  <div class="cell swap">
    <div class="swap-img-wrap">{swap_html}</div>
    {f'<div class="panel-text"><h4>{title}</h4><p>{body}</p></div>' if title or body else ''}
  </div>
</div>
"""


def build_dual_grid(t):
    meta_path = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}/meta.json"
    meta = json.loads(meta_path.read_text())
    detail_imgs = meta.get("detail_imgs", [])
    panel_count = meta.get("detail_img_count") or meta.get("panel_count") or len(detail_imgs)
    sections_map = assign_sections(panel_count)
    swap_results = get_v3_results(t)

    rows = [build_cover_row(t, swap_results)]
    for i in range(1, panel_count + 1):
        rows.append(build_panel_row(t, i, sections_map, swap_results))

    return "\n".join(rows), sections_map, swap_results


def build_tabs(rank, sections_map):
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


def build_process_card(t, swap_results, fact, spec, gif_visual_data):
    rank = t["rank"]
    tpl_price = t.get("price")
    tpl_price_str = f"{tpl_price:,}원" if tpl_price else ""
    is_done = swap_results is not None

    if is_done:
        badge = '<span class="badge ready"><b>실행 완료</b></span>'
    else:
        badge = '<span class="badge"><b>대기</b></span>'

    # GIF refs row
    gif_frames = sorted((USER_PROD / "gif_frames").glob("frame_*.jpg"))[:3]
    refs_html = "".join(
        f'<div class="ref-thumb"><img src="../user_products/milo_777039/gif_frames/{f.name}"/><div class="ref-role">frame {i+1}</div></div>'
        for i, f in enumerate(gif_frames)
    )

    # Rich auto-generated LLM request from vision + spec
    visual_summary = gif_visual_data.get("full_visual_paragraph", "")
    seat_n = gif_visual_data.get("seat_count", 2)
    dims = spec.get("dimensions", {}) or {}
    mat = spec.get("material", {}) or {}
    colors = ", ".join(spec.get("colors") or [])

    auto_req = (
        f"제품: 밀로 패브릭소파 {seat_n}인용. "
        f"GIF 360° 분석 — {visual_summary} "
        f"수치 — 좌석높이 {dims.get('seat_height_cm','?')}cm, "
        f"팔걸이높이 {dims.get('arm_height_cm','?')}cm. "
        f"소재 — {mat.get('upholstery','패브릭')}, "
        f"좌방석 {mat.get('seat_cushion','')}, "
        f"등쿠션 {mat.get('back_cushion','')}, "
        f"프레임 {mat.get('frame','')}. "
        f"컬러 옵션 — {colors}. "
        "원본 panel의 staging(구도/배경/조명/연출 의도)을 유지하되 sofa를 위 spec 그대로 정밀하게 swap. "
        "이미지 안 텍스트 X (한국어 수치/라벨 X), 별도 HTML로 표시. "
        "가죽 느낌 X (fabric). 1인/3인/4인 X (2인용 STRICT)."
    )

    price = fact.get("price") or {}
    dc, normal = price.get("dc"), price.get("normal")
    price_str = f"{dc:,}원 (정가 {normal:,}원)" if dc and normal else ""

    # status col with strategies used
    if swap_results:
        cells = swap_results["summary"]["cells"]
        wall = swap_results["summary"].get("wall_seconds", 0)
        n_pass = sum(1 for c in cells if c["passed"])
        n_total = len(cells)
        avg_prod = round(sum((c.get("final") or {}).get("product_score", 0) for c in cells) / max(1, n_total), 1)
        avg_comp = round(sum((c.get("final") or {}).get("composition_score", 0) for c in cells) / max(1, n_total), 1)
        # strategy breakdown
        strat_counts = {"aligned": 0, "overpaint": 0, "smart_sheet": 0}
        for c in cells:
            for s in c.get("strategies_used", []):
                strat_counts[s] = strat_counts.get(s, 0) + 1
        strat_html = " · ".join(f"{k} <b>{v}</b>" for k, v in strat_counts.items())
        status_col = f"""
<div class="proc-h">상태 (실행 완료)</div>
<div class="status-line">처리 시간 <b>{wall:.0f}s</b></div>
<div class="status-line">passer <b>{n_pass}/{n_total}</b> · prod 평균 <b>{avg_prod}</b> · comp 평균 <b>{avg_comp}</b></div>
<div class="status-line">strategy 사용량: {strat_html}</div>
"""
    else:
        status_col = """
<div class="proc-h">상태</div>
<div class="status-line">처리 시간 <b>—</b></div>
"""

    spec_block = f"""
<details class="spec-details" open>
  <summary>밀로 spec (vision 추출 — GIF + 한샘 페이지)</summary>
  <div class="spec-list">
    <div><b>좌석 수</b>: {seat_n}인</div>
    <div><b>실루엣</b>: {gif_visual_data.get('silhouette','')}</div>
    <div><b>팔걸이</b>: {gif_visual_data.get('arm',{}).get('shape','')}, {gif_visual_data.get('arm',{}).get('height_relative','')}</div>
    <div><b>등쿠션</b>: {gif_visual_data.get('back',{}).get('cushion_count','?')}개 {gif_visual_data.get('back',{}).get('shape','')}, {gif_visual_data.get('back',{}).get('attached_or_loose','')}, 헤드레스트 {'있음' if gif_visual_data.get('back',{}).get('headrest') else '없음'}</div>
    <div><b>좌방석</b>: {gif_visual_data.get('seat',{}).get('cushion_count','?')}개, depth {gif_visual_data.get('seat',{}).get('depth','')}, firmness {gif_visual_data.get('seat',{}).get('firmness','')}</div>
    <div><b>패브릭</b>: {gif_visual_data.get('upholstery',{}).get('material','')} ({gif_visual_data.get('upholstery',{}).get('texture','')}), seams {gif_visual_data.get('upholstery',{}).get('seams','')}, color {gif_visual_data.get('upholstery',{}).get('primary_color','')}</div>
    <div><b>다리</b>: {gif_visual_data.get('legs',{}).get('count','?')}개 {gif_visual_data.get('legs',{}).get('shape','')}, {gif_visual_data.get('legs',{}).get('color','')}</div>
    <div><b>좌석높이/팔걸이</b>: {dims.get('seat_height_cm','?')}cm / {dims.get('arm_height_cm','?')}cm</div>
    <div><b>좌방석 내용물</b>: {mat.get('seat_cushion','')}</div>
    <div><b>등쿠션 내용물</b>: {mat.get('back_cushion','')}</div>
    <div><b>패브릭 인증</b>: {mat.get('upholstery','')}</div>
    <div><b>프레임</b>: {mat.get('frame','')}</div>
    <div><b>컬러 옵션</b>: {colors}</div>
  </div>
</details>
"""

    return f"""
<details class="process-card">
  <summary>
    <span class="proc-title">공정 설정</span>
    <span class="proc-summary">
      <span class="badge tpl-badge">템플릿 <b>#{rank} {t.get('category')}</b> · {t['name'][:24]}{'…' if len(t['name'])>24 else ''}</span>
      <span class="badge"><b>GPT image</b> · 3-strategy auto-fallback</span>
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
        <div class="proc-h">공정 — 자동 fallback</div>
        <div class="fallback-card">
          <div class="strat"><span class="step">1</span> aligned <span class="strat-desc">기본 정합 swap</span></div>
          <div class="strat"><span class="step">2</span> overpaint <span class="strat-desc">실패 시 덧그리기</span></div>
          <div class="strat"><span class="step">3</span> smart sheet <span class="strat-desc">최종 보정 (multi-angle 합성)</span></div>
        </div>
        <div class="model-info">모델: <b>GPT image 1.5</b> (NB2는 좌석수 인식 약함)</div>
      </div>

      <div class="proc-col">
        <div class="proc-h">입력 — 사용자 업로드 (GIF 3 frames)</div>
        <div class="input-card ready">
          <div class="ref-row">{refs_html}</div>
          <div class="ref-note">실 운영: 업로드 존(제품샷/소재/컬러) 분리</div>
        </div>
        <div class="proc-h" style="margin-top:12px;">입력 — 사용자 LLM 요청 (자동 풍부 생성)</div>
        <textarea class="user-prompt">{auto_req}</textarea>
      </div>

      <div class="proc-col">
        <div class="proc-h">밀로 메타</div>
        <div class="input-card meta">
          <img class="user-prod-thumb" src="../user_products/milo_777039/_thumbnail.jpg"/>
          <div class="input-meta">
            <div class="input-name">밀로 패브릭소파 2인용</div>
            <div class="input-cat">패브릭 · {seat_n}인용</div>
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


cover_imgs_d = {t["gdsNo"]: cover_url_thumb(t) for t in data["top6"]}


def chip(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    name_short = t["name"][:24] + ("…" if len(t["name"]) > 24 else "")
    swap = get_v3_results(t)
    state = get_state(t)
    if swap:
        ready_mark = '<span class="chip-ready done">✓</span>'
    elif state:
        ready_mark = '<span class="chip-ready">●</span>'
    else:
        ready_mark = ""
    return f"""
<button class="chip {'selected' if rank == 1 else ''}" data-rank="{rank}" onclick="selectTpl({rank})">
  {ready_mark}<span class="chip-rank">#{rank}</span>
  <img class="chip-cover" src="{cover_imgs_d[gds]}" alt="{cat}"/>
  <span class="chip-meta">
    <span class="chip-cat">{cat}</span><span class="chip-name">{name_short}</span>
  </span>
</button>"""


def view(t):
    rank = t["rank"]
    is_first = rank == 1
    dual_content, sections_map, swap_results = build_dual_grid(t)
    process_card = build_process_card(t, swap_results, milo_fact,
                                      milo_spec if rank == 1 else {},
                                      gif_visual if rank == 1 else {})
    tabs = build_tabs(rank, sections_map)

    return f"""
<div class="view {'active' if is_first else ''}" data-rank="{rank}">
  {process_card}
  <div class="tabs-bar">
    <div class="tabs">{tabs}</div>
  </div>
  <div class="dual-grid">
    <div class="dual-header">
      <div class="dual-h-left">원본 한샘 detail (스왑 base)</div>
      <div class="dual-h-right">swap 결과 · 밀로 패브릭소파 2인용 · GPT</div>
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
<title>가구 detail 템플릿 swap 미리보기 — v9</title>
<link rel="stylesheet" href="https://res.remodeling.hanssem.com/font/pretendard/pretendard.css"/>
<style>
  :root {{
    --bg: #fff; --bg-alt: #f4f4f6;
    --fg: #1a1a1a; --fg-soft: #555; --muted: #888;
    --line: #e5e5e5; --line-soft: #efefef;
    --accent: #ff7a00; --accent-soft: #fff5ec;
    --good: #16a34a; --bad: #dc2626;
    --topbar-h: 56px;
    --tabs-h: 50px;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Pretendard", -apple-system, system-ui, sans-serif;
    background: var(--bg-alt); color: var(--fg);
    -webkit-font-smoothing: antialiased; font-size: 14px; line-height: 1.5;
  }}

  /* === Topbar === */
  .topbar {{
    position: sticky; top: 0; z-index: 100;
    background: #fff; border-bottom: 1px solid var(--line); padding: 12px 24px;
    height: var(--topbar-h);
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

  .proc-grid {{ display: grid; grid-template-columns: 1fr 1.5fr 1.3fr 1fr; gap: 24px; }}
  .proc-col {{ display: flex; flex-direction: column; gap: 8px; min-width: 0; }}
  .proc-h {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; }}

  .fallback-card {{ display: flex; flex-direction: column; gap: 6px; padding: 12px;
    background: #fafafa; border: 1px solid var(--line); border-radius: 8px; }}
  .strat {{ display: flex; gap: 8px; align-items: center; font-size: 12px; color: var(--fg-soft); }}
  .strat .step {{ width: 20px; height: 20px; border-radius: 50%; background: var(--accent);
    color: #fff; font-weight: 700; font-size: 11px; display: inline-flex;
    align-items: center; justify-content: center; flex-shrink: 0; }}
  .strat-desc {{ color: var(--muted); font-size: 11px; margin-left: auto; }}
  .model-info {{ font-size: 11px; color: var(--muted); padding: 8px 0 0; }}
  .model-info b {{ color: var(--fg); }}

  .input-card {{ padding: 12px; background: var(--bg-alt); border: 1px dashed var(--line); border-radius: 8px; }}
  .input-card.ready {{ background: #f6fff6; border: 1px solid #c6ecc8; display: flex; flex-direction: column; gap: 8px; }}
  .input-card.meta {{ background: #fff; border: 1px solid var(--line); display: flex; gap: 10px; align-items: center; }}
  .user-prod-thumb {{ width: 56px; height: 56px; border-radius: 6px; object-fit: cover; background: #fff; border: 1px solid var(--line); }}
  .input-meta {{ flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }}
  .input-name {{ font-size: 12px; font-weight: 600; line-height: 1.3; }}
  .input-cat {{ font-size: 11px; color: var(--muted); }}
  .input-price {{ font-size: 12px; color: var(--accent); font-weight: 600; }}
  .ref-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }}
  .ref-thumb {{ position: relative; aspect-ratio: 3/2; }}
  .ref-thumb img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 4px; border: 1px solid var(--line); }}
  .ref-role {{ position: absolute; bottom: 1px; left: 1px; right: 1px;
    font-size: 8px; color: #fff; background: rgba(0,0,0,0.55); padding: 1px 3px; border-radius: 2px;
    text-align: center; }}
  .ref-note {{ font-size: 10px; color: var(--muted); font-style: italic; }}

  .user-prompt {{ width: 100%; min-height: 120px; padding: 10px 12px;
    border: 1px solid var(--line); border-radius: 8px; resize: vertical;
    font-family: inherit; font-size: 12px; background: #fafafa; line-height: 1.55; }}

  .spec-details {{ margin-top: 10px; border: 1px solid var(--line); border-radius: 8px; background: #fafafa; }}
  .spec-details summary {{ cursor: pointer; padding: 8px 12px; font-size: 11px; color: var(--fg-soft); font-weight: 600; outline: none; }}
  .spec-details summary::-webkit-details-marker {{ display: none; }}
  .spec-list {{ padding: 4px 12px 12px; font-size: 11px; color: var(--fg-soft); line-height: 1.7; }}
  .spec-list b {{ color: var(--fg); font-weight: 600; margin-right: 4px; }}

  .status-line {{ font-size: 12px; color: var(--muted); margin-bottom: 4px; }}
  .status-line b {{ color: var(--fg); font-weight: 600; margin-left: 4px; }}

  /* === Sticky tabs === */
  .tabs-bar {{
    position: sticky; top: var(--topbar-h); z-index: 30; background: var(--bg-alt);
    padding: 4px 0 0;
    height: calc(var(--tabs-h) + 4px);
  }}
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

  /* === DUAL GRID === */
  .dual-grid {{
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
    margin-top: 12px; overflow: hidden;
  }}
  .dual-header {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 0;
    border-bottom: 1px solid var(--line); background: #fafafa;
  }}
  .dual-h-left, .dual-h-right {{
    padding: 12px 20px; font-size: 12px; font-weight: 600; color: #444;
  }}
  .dual-h-left {{ border-right: 1px solid var(--line); }}

  /* section divider sits ABOVE its row, spans both columns */
  .sec-divider.section-marker {{
    display: flex; align-items: baseline; gap: 12px;
    padding: 16px 20px 8px;
    background: linear-gradient(to bottom, #fafafa, #fff);
    border-top: 1px solid var(--line-soft);
    scroll-margin-top: calc(var(--topbar-h) + var(--tabs-h) + 20px);
  }}
  .sec-divider .sec-name {{ font-size: 13px; font-weight: 700;
    padding: 4px 12px; background: var(--accent-soft);
    border-left: 3px solid var(--accent); border-radius: 0 4px 4px 0; }}
  .sec-divider .sec-range {{ font-size: 10px; color: var(--muted); font-family: ui-monospace, monospace; }}
  .sec-divider.cover-divider .sec-name {{ background: #e8f4ff; border-left-color: #2563eb; }}

  /* dual panel = 1 grid row, two cells, height auto-matched */
  .dual-panel {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 0;
    border-bottom: 1px solid var(--line-soft);
    scroll-margin-top: calc(var(--topbar-h) + var(--tabs-h) + 20px);
  }}
  .dual-panel:last-child {{ border-bottom: none; }}
  .cell {{ padding: 20px; min-width: 0; display: flex; flex-direction: column; }}
  .cell.orig {{ border-right: 1px solid var(--line); background: #fff; }}
  .cell.swap {{ background: #fafafa; }}
  .cell > img {{ max-width: 100%; display: block; margin: 0 auto; border-radius: 6px; }}
  .cover-row .cell > img,
  .cover-row .swap-img-wrap img {{ max-width: 480px; }}

  .swap-img-wrap {{ position: relative; margin: 0 auto; }}
  .swap-img-wrap img {{ max-width: 100%; display: block; margin: 0 auto; border-radius: 6px; }}
  .swap-score-overlay {{
    position: absolute; bottom: 8px; right: 8px;
    font-size: 10px; padding: 4px 8px; border-radius: 4px;
    background: rgba(0,0,0,0.65); color: #fff; font-family: ui-monospace, monospace;
  }}
  .swap-score-overlay.pass {{ background: rgba(22, 163, 74, 0.88); }}
  .swap-score-overlay.fail {{ background: rgba(220, 38, 38, 0.85); }}
  .swap-pending {{ padding: 60px; text-align: center; color: var(--muted); background: #f3f3f3; border-radius: 6px; }}

  /* panel-text — minimal, integrated into the cell */
  .panel-text {{
    margin-top: 14px; padding-top: 12px;
    border-top: 1px solid var(--line-soft);
    text-align: left;
  }}
  .panel-text h4 {{
    margin: 0 0 6px; font-size: 15px; font-weight: 700; color: var(--fg);
    letter-spacing: -0.01em;
  }}
  .panel-text p {{ margin: 0; font-size: 13px; color: var(--fg-soft); line-height: 1.6; }}
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
  const targetId = slug === 'cover' ? `sec-cover` : `sec-${{slug}}`;
  const target = view.querySelector(`#${{targetId}}`);
  if (!target) return;
  // scroll with offset for sticky bars
  const rect = target.getBoundingClientRect();
  const offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--topbar-h')) + parseInt(getComputedStyle(document.documentElement).getPropertyValue('--tabs-h')) + 20;
  window.scrollTo({{ top: window.scrollY + rect.top - offset, behavior: 'smooth' }});
}}
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT}")
print(f"size: {OUT.stat().st_size // 1024}KB")

"""Report v10 — final feedback round.

변경:
- 좌측 (원본): 한샘 detail HTML 통째 inline 복원 (v5/v6 스타일) — panel 이미지 +
  사이사이 markup + 동영상 iframe 그대로
- 우측 (swap): 같은 detail HTML markup 구조 안에 sofa 부분만 swap 이미지로 교체
- 좌우 panel 단위 grid row → CSS grid로 같은 row 자동 height match
- QA 회차 토글 — 1차/2차/3차 attempt 이미지+verdict 토글
- 공정 카드 입력 영역 = zone별 분리 표시 (제품샷/소재/컬러)
- 카피 HTML — 한샘 스타일 톤 통합 (별도 박스 X)
- v4 run 결과 우선
"""

import json
import re
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
panel_classifications_user = auto_output["panel_classifications"]
input_zones_user = auto_output["input_zones"]
panel_copy = json.loads((TPL_ROOT / "01_sofa_992474/panel_copy.json").read_text())["copies"]

# template layout types
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
    summary_file = run_dir / "summary.json"
    if not summary_file.exists():
        return None
    summary = json.loads(summary_file.read_text())
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


def build_detail_orig(t):
    """좌측 원본 detail HTML — 한샘 markup 통째 inline (v5/v6 스타일 복원).
    img src를 로컬 panel 파일로 rewrite, panel idx 마킹."""
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    detail_path = TPL_ROOT / dir_name / "detail.html"
    meta_path = TPL_ROOT / dir_name / "meta.json"
    detail_html = detail_path.read_text(encoding="utf-8", errors="ignore") if detail_path.exists() else ""
    meta = json.loads(meta_path.read_text())

    src_to_local = {}
    for i, src in enumerate(meta.get("detail_imgs", []), 1):
        matches = list((TPL_ROOT / dir_name).glob(f"panel_{i:02d}.*"))
        if matches:
            local = f"../templates/{dir_name}/{matches[0].name}"
            src_to_local[src] = local
            if src.startswith("https://"):
                src_to_local["http://" + src[8:]] = local
            elif src.startswith("http://"):
                src_to_local["https://" + src[7:]] = local

    panel_idx = [0]

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
        panel_idx[0] += 1
        return re.sub(
            r'src=["\'][^"\']+["\']',
            f'src="{local}" data-panel-idx="{panel_idx[0]}" loading="lazy"',
            full,
        )

    return re.sub(r"<img[^>]+>", repl_img, detail_html)


def build_detail_swap(t, swap_results):
    """우측 swap detail HTML — 같은 한샘 markup 구조 안에 sofa swap된 img로 교체."""
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    detail_path = TPL_ROOT / dir_name / "detail.html"
    meta_path = TPL_ROOT / dir_name / "meta.json"
    detail_html = detail_path.read_text(encoding="utf-8", errors="ignore") if detail_path.exists() else ""
    meta = json.loads(meta_path.read_text())
    detail_imgs = meta.get("detail_imgs", [])

    src_to_local = {}
    for i, src in enumerate(detail_imgs, 1):
        matches = list((TPL_ROOT / dir_name).glob(f"panel_{i:02d}.*"))
        if matches:
            local = f"../templates/{dir_name}/{matches[0].name}"
            src_to_local[src] = local

    panel_idx = [0]

    def repl_img(m):
        full = m.group(0)
        src_m = re.search(r'src=["\']([^"\']+)["\']', full)
        if not src_m:
            return full
        panel_idx[0] += 1
        idx = panel_idx[0]
        sname = f"panel_{idx:02d}"
        cell = swap_results["by_label"].get(sname) if swap_results else None

        if cell and cell.get("final") and cell["final"].get("image"):
            # Build attempt toggle (multiple attempts available)
            attempts = cell.get("attempts", [])
            attempts_with_img = [a for a in attempts if a.get("image")]
            tabs = ""
            slots = ""
            for ai, a in enumerate(attempts_with_img):
                strat = a.get("strategy", "?")
                prod = a.get("product_score", "-")
                comp = a.get("composition_score", "-")
                seats = a.get("seat_count_in_B", "?")
                text_flag = a.get("text_in_image")
                verdict = a.get("verdict", "?")
                badge_cls = "pass" if verdict == "pass" else "fail"
                tab_active = "active" if a["image"] == cell["final"]["image"] else ""
                tabs += f'<button class="qa-tab {tab_active}" data-idx="{idx}" data-attempt="{ai}" onclick="setAttempt({idx},{ai})">#{ai+1} {strat[:4]}</button>'
                img_url = f"{swap_results['run_dir_rel']}/{a['image']}"
                slot_active = "active" if a["image"] == cell["final"]["image"] else ""
                notes = (a.get("notes") or "").replace('"', '&quot;')
                slots += f"""
<div class="qa-attempt {slot_active}" data-idx="{idx}" data-attempt="{ai}">
  <img data-panel-idx="{idx}" src="{img_url}" loading="lazy"/>
  <div class="qa-info-overlay {badge_cls}">
    <div class="qa-line">prod <b>{prod}</b> · comp <b>{comp}</b> · seats <b>{seats}</b>{' · TEXT!' if text_flag else ''}</div>
    <div class="qa-notes">{notes}</div>
  </div>
</div>
"""
            return f"""
</div></div><div class="swap-cell-wrap" data-panel-idx="{idx}">
  <div class="qa-tabs">{tabs}</div>
  <div class="qa-slots">{slots}</div>
</div><div class="hidden-wrap"><div>
"""
        else:
            # no swap result — fallback to orig
            local = src_to_local.get(src_m.group(1)) or src_m.group(1)
            return re.sub(r'src=["\'][^"\']+["\']',
                          f'src="{local}" data-panel-idx="{idx}" loading="lazy"', full)

    out = re.sub(r"<img[^>]+>", repl_img, detail_html)
    # wrap whole thing — first <div> opener needs no prefix close
    out = '<div class="hidden-wrap"><div>' + out + '</div></div>'
    return out


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


def build_zone_inputs(milo_dir_name):
    """공정 카드 입력 영역 — zone별로 분리해서 표시."""
    use_prod_path = f"../user_products/{milo_dir_name}/use_product"
    zones_data = [
        ("제품 이미지", "product_shot", "p08_frame_01.jpg p08_frame_02.jpg p08_frame_03.jpg".split()),
        ("소재", "material", ["material.png"]),
        ("컬러", "color", ["color_01.png", "color_02.png", "color_03.png"]),
    ]
    blocks = ""
    for title, zone, files in zones_data:
        thumbs = "".join(
            f'<div class="zone-thumb"><img src="{use_prod_path}/{f}" loading="lazy"/></div>'
            for f in files
        )
        blocks += f"""
<div class="zone-block">
  <div class="zone-label">{title} <span class="zone-count">{len(files)}장</span></div>
  <div class="zone-thumbs">{thumbs}</div>
</div>
"""
    return blocks


def build_process_card(t, swap_results, spec, visual):
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
        f"GIF 360° vision — {visual.get('full_visual_paragraph','')[:200]} "
        f"사이즈 {dims.get('width_cm','?')}×{dims.get('depth_cm','?')}×{dims.get('height_cm','?')}cm, "
        f"좌방석 {dims.get('seat_depth_cm','?')}×{dims.get('seat_height_cm','?')}, "
        f"팔걸이 {dims.get('arm_height_cm','?')}cm. "
        f"패브릭 {mat.get('upholstery','')}, "
        f"좌방석 {mat.get('seat_cushion','')} (firmness: {mat.get('cushion_firmness','')}), "
        f"등쿠션 {mat.get('back_cushion','')}, "
        f"프레임 {mat.get('frame','')}. "
        f"컬러: {', '.join(colors)}. "
        "원본 panel의 staging/layout을 유지하되 sofa만 위 spec으로 정밀 swap. "
        f"{seat_n}인용 STRICT. 가죽 X. 이미지 안 텍스트 X."
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
<div class="status-line">passer <b>{n_pass}/{len(cells)}</b> · prod 평균 <b>{avg_prod}</b> · comp 평균 <b>{avg_comp}</b></div>
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
        <div class="proc-h">입력 — zone 분리 (담당자 업로드 시뮬레이션)</div>
        {build_zone_inputs("milo_777039")}
      </div>
      <div class="proc-col proc-col-wide">
        <div class="proc-h">입력 — 사용자 LLM 요청 (자동 풍부 생성 from vision)</div>
        <textarea class="user-prompt">{auto_req}</textarea>
        <details class="spec-details">
          <summary>밀로 spec 전체 (vision 추출)</summary>
          <div class="spec-list">
            <div><b>좌석 수</b>: {seat_n}인용</div>
            <div><b>사이즈</b>: {dims.get('width_cm','?')}×{dims.get('depth_cm','?')}×{dims.get('height_cm','?')}cm · 좌방석 {dims.get('seat_depth_cm','?')}cm 길이 / {dims.get('seat_height_cm','?')}cm 높이 / 팔걸이 {dims.get('arm_height_cm','?')}cm · 다리 14cm</div>
            <div><b>패브릭</b>: {mat.get('upholstery','')}</div>
            <div><b>인증</b>: {', '.join(mat.get('upholstery_certifications', []))}</div>
            <div><b>좌방석</b>: {mat.get('seat_cushion','')}</div>
            <div><b>등쿠션</b>: {mat.get('back_cushion','')}</div>
            <div><b>경도</b>: {mat.get('cushion_firmness','')}</div>
            <div><b>프레임</b>: {mat.get('frame','')}</div>
            <div><b>컬러</b>: {', '.join(colors)}</div>
            <div><b>주요 특징</b>: {' · '.join(features[:5])}</div>
          </div>
        </details>
      </div>
      <div class="proc-col">
        {status_col}
      </div>
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

    orig_html = build_detail_orig(t)
    swap_html = build_detail_swap(t, swap_results)

    # cover row above the dual detail
    cover_src_t = cover_url_template(t)
    cover_swap_cell = swap_results["by_label"].get("cover") if swap_results else None
    if cover_swap_cell and cover_swap_cell.get("final"):
        cf = cover_swap_cell["final"]
        cover_swap_img = f"{swap_results['run_dir_rel']}/{cf['image']}"
        prod, comp, seats = cf.get("product_score","-"), cf.get("composition_score","-"), cf.get("seat_count_in_B","?")
        notes = (cf.get("notes") or "").replace('"', '&quot;')
        passed = cover_swap_cell["passed"]
        badge = "pass" if passed else "fail"
        cover_swap_html = f"""
<img class="cover-img" src="{cover_swap_img}"/>
<div class="qa-info-overlay {badge}">
  <div class="qa-line">prod <b>{prod}</b> · comp <b>{comp}</b> · seats <b>{seats}</b></div>
  <div class="qa-notes">{notes}</div>
</div>
"""
    else:
        cover_swap_html = '<div class="swap-pending">대기</div>'

    cover_row = f"""
<div class="dual-row cover-row" id="sec-cover-{rank}">
  <div class="cell orig">
    <div class="sec-divider cover-divider"><span class="sec-name">커버</span><span class="sec-range">1:1 대표</span></div>
    <img class="cover-img" src="{cover_src_t}"/>
  </div>
  <div class="cell swap">
    <div class="sec-divider cover-divider"><span class="sec-name">커버 swap</span><span class="sec-range">밀로 2인용</span></div>
    <div class="cover-swap-wrap">{cover_swap_html}</div>
  </div>
</div>
"""

    return f"""
<div class="view {'active' if is_first else ''}" data-rank="{rank}">
  {build_process_card(t, swap_results, spec, visual)}
  <div class="tabs-bar">
    <div class="tabs">{build_tabs(rank, sections_map)}</div>
  </div>
  <div class="dual-grid" data-rank="{rank}">
    <div class="dual-header">
      <div class="dual-h-left">원본 한샘 detail</div>
      <div class="dual-h-right">swap · 밀로 패브릭소파 2인용 · GPT</div>
    </div>
    {cover_row}
    <div class="dual-body">
      <div class="orig-side">
        {orig_html}
      </div>
      <div class="swap-side">
        {swap_html}
      </div>
    </div>
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
<title>가구 detail 템플릿 swap — v10</title>
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

  /* Zone inputs */
  .zone-block {{ padding: 10px 12px; background: var(--bg-alt); border: 1px solid var(--line); border-radius: 8px; margin-top: 8px; }}
  .zone-label {{ font-size: 12px; font-weight: 600; margin-bottom: 6px; color: var(--fg); }}
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

  /* === DUAL GRID === */
  .dual-grid {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; margin-top: 12px; overflow: hidden; }}
  .dual-header {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-bottom: 1px solid var(--line); background: #fafafa; }}
  .dual-h-left, .dual-h-right {{ padding: 12px 20px; font-size: 12px; font-weight: 600; color: #444; }}
  .dual-h-left {{ border-right: 1px solid var(--line); }}

  /* dual-body uses grid for orig/swap side-by-side, contents flow vertically per side */
  .dual-body {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; }}
  .orig-side {{ border-right: 1px solid var(--line); padding: 20px; background: #fff; }}
  .swap-side {{ padding: 20px; background: #fafafa; }}
  .orig-side img, .swap-side img {{ max-width: 100%; display: block; margin: 0 auto; }}
  .orig-side iframe, .swap-side iframe {{ max-width: 100%; display: block; margin: 16px auto; }}
  .orig-side .mall_prod_info, .swap-side .mall_prod_info {{ text-align: center; }}
  .hidden-wrap {{ display: contents; }}

  /* swap cell wrapper — contains QA tabs and slot images */
  .swap-cell-wrap {{ margin: 6px 0 18px; }}
  .qa-tabs {{ display: flex; gap: 4px; margin-bottom: 4px; }}
  .qa-tab {{ font-size: 10px; padding: 3px 8px; border: 1px solid var(--line); background: #fff;
    border-radius: 4px; cursor: pointer; color: var(--muted); font-family: inherit; }}
  .qa-tab.active {{ background: var(--fg); color: #fff; border-color: var(--fg); }}
  .qa-slots {{ position: relative; }}
  .qa-attempt {{ display: none; position: relative; }}
  .qa-attempt.active {{ display: block; }}
  .qa-info-overlay {{
    position: absolute; bottom: 8px; right: 8px;
    padding: 6px 10px; border-radius: 6px;
    background: rgba(0,0,0,0.75); color: #fff;
    font-size: 10px; font-family: ui-monospace, Menlo, monospace;
    max-width: 60%; line-height: 1.4;
  }}
  .qa-info-overlay.pass {{ background: rgba(22, 163, 74, 0.88); }}
  .qa-info-overlay.fail {{ background: rgba(220, 38, 38, 0.85); }}
  .qa-line b {{ font-weight: 700; }}
  .qa-notes {{ font-size: 9px; opacity: 0.85; margin-top: 2px; max-height: 36px; overflow: hidden; text-overflow: ellipsis; }}

  /* cover row */
  .cover-row {{ display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid var(--line); }}
  .cell {{ padding: 20px; }}
  .cell.orig {{ border-right: 1px solid var(--line); background: #fff; }}
  .cell.swap {{ background: #fafafa; }}
  .cover-img {{ max-width: 480px; aspect-ratio: 1/1; object-fit: contain; background: #fafafa; border-radius: 8px; display: block; margin: 0 auto; }}
  .cover-swap-wrap {{ position: relative; max-width: 480px; margin: 0 auto; }}
  .swap-pending {{ padding: 80px; text-align: center; color: var(--muted); }}

  /* Section divider */
  .sec-divider {{ display: flex; align-items: baseline; gap: 12px; margin: 0 0 12px; scroll-margin-top: calc(var(--topbar-h) + var(--tabs-h) + 20px); }}
  .sec-divider .sec-name {{ font-size: 13px; font-weight: 700; padding: 4px 12px;
    background: var(--accent-soft); border-left: 3px solid var(--accent); border-radius: 0 4px 4px 0; }}
  .sec-divider .sec-range {{ font-size: 10px; color: var(--muted); font-family: ui-monospace, monospace; }}
  .cover-divider .sec-name {{ background: #e8f4ff; border-left-color: #2563eb; }}
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
  let target = view.querySelector(`#${{targetId}}`);
  if (!target && slug === 'cover') target = view.querySelector(`#sec-cover-${{rank}}`);
  if (!target) {{
    // find first panel matching slug section via data-section
    target = view.querySelector(`[data-section-slug="${{slug}}"]`);
  }}
  if (!target) return;
  const rect = target.getBoundingClientRect();
  const offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--topbar-h'))
               + parseInt(getComputedStyle(document.documentElement).getPropertyValue('--tabs-h')) + 20;
  window.scrollTo({{ top: window.scrollY + rect.top - offset, behavior: 'smooth' }});
}}
function setAttempt(panelIdx, attemptIdx) {{
  // toggle attempts within this panel's swap-cell-wrap
  document.querySelectorAll(`.swap-cell-wrap[data-panel-idx="${{panelIdx}}"]`).forEach(wrap => {{
    wrap.querySelectorAll('.qa-tab').forEach(t => t.classList.toggle('active', +t.dataset.attempt === attemptIdx));
    wrap.querySelectorAll('.qa-attempt').forEach(a => a.classList.toggle('active', +a.dataset.attempt === attemptIdx));
  }});
}}
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT}")
print(f"size: {OUT.stat().st_size // 1024}KB")

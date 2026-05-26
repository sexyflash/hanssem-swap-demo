"""Report v13 — v12 base + 사용자 7차 피드백:
- 우측 텍스트 노드를 LLM substitute(밀로 버전)로 교체
- panel# 칩 톤 다운 (작고 옅게)
- bypass overlay "우회" 표시 + 옵션 카피
- skip overlay "정보 누락 / skip"
- 좌우 같은 markup 유지 → 자동 정렬
"""

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

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
mismatch = json.loads((TPL_ROOT / "01_sofa_992474/mismatch_resolution.json").read_text())
text_subs_data = json.loads((TPL_ROOT / "01_sofa_992474/text_substitute.json").read_text())
verdict_by_panel = {r["panel_idx"]: r for r in mismatch["resolutions"]}
text_subs_by_idx = {item["i"]: item for item in text_subs_data["substitutes"]}

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
    latest = sr / "latest_v5.txt"
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


def build_detail(t, side: str, swap_results=None):
    """좌측 (orig) 또는 우측 (swap) detail HTML을 빌드.
    side: 'orig' or 'swap'
    swap: img는 swap된 거로 교체, 텍스트는 LLM substitute로 교체.
    """
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    detail_path = TPL_ROOT / dir_name / "detail.html"
    meta_path = TPL_ROOT / dir_name / "meta.json"
    if not detail_path.exists():
        return ""
    detail_html = detail_path.read_text(encoding="utf-8", errors="ignore")
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

    soup = BeautifulSoup(detail_html, "lxml")

    # If side == 'swap', substitute text nodes
    if side == "swap":
        text_idx = [0]
        for el in list(soup.descendants):
            if isinstance(el, NavigableString) and not isinstance(el, (type(soup.new_string("")).__class__,)):
                pass  # ignore
            if isinstance(el, NavigableString):
                t_str = str(el).strip()
                if t_str and len(t_str) > 2:
                    # find substitute
                    sub = text_subs_by_idx.get(text_idx[0])
                    if sub:
                        # preserve leading/trailing whitespace
                        original = str(el)
                        leading = original[: len(original) - len(original.lstrip())]
                        trailing = original[len(original.rstrip()):]
                        new_text = leading + sub["milo"] + trailing
                        el.replace_with(new_text)
                    text_idx[0] += 1

    # Now replace imgs
    panel_idx_counter = [0]
    for img in soup.find_all("img"):
        src = img.get("src", "")
        src_clean = src.replace("devimage.hanssem.com", "image.hanssem.com")
        if src_clean.startswith("http://"):
            src_clean = "https://" + src_clean[7:]
        local = src_to_local.get(src) or src_to_local.get(src_clean) or src_clean

        panel_idx_counter[0] += 1
        idx = panel_idx_counter[0]

        if side == "swap" and swap_results:
            sname = f"panel_{idx:02d}"
            cell = swap_results["by_label"].get(sname)
            if cell and cell.get("final") and cell["final"].get("image"):
                f = cell["final"]
                img_url = f"{swap_results['run_dir_rel']}/{f['image']}"
                prod = f.get("product_score", "-")
                comp = f.get("composition_score", "-")
                seats = f.get("seat_count_in_B", "?")
                passed = cell.get("passed", False)
                badge_cls = "pass" if passed else "fail"

                # verdict from mismatch detection
                verdict_info = verdict_by_panel.get(idx, {})
                verdict = verdict_info.get("verdict", "match")
                overlay_label = verdict_info.get("overlay_label") or ""

                bypass_html = ""
                if verdict == "bypass":
                    alt_title = verdict_info.get("alt_title", "")
                    alt_body = verdict_info.get("alt_body", "")
                    bypass_html = (
                        f'<div class="overlay-bypass">우회 · 밀로엔 없는 기능</div>'
                        + (f'<div class="overlay-alt"><b>{alt_title}</b><br/>{alt_body}</div>' if alt_title or alt_body else "")
                    )
                elif verdict == "skip":
                    bypass_html = f'<div class="overlay-bypass skip">정보 누락 · skip</div>'

                wrap = soup.new_tag("div", **{"class": "img-with-chip"})
                wrap["data-panel-idx"] = str(idx)
                new_img = soup.new_tag("img", src=img_url, **{"data-panel-idx": str(idx), "loading": "lazy"})
                wrap.append(new_img)
                chip = BeautifulSoup(f'<div class="panel-number-chip">{idx:02d}</div>', "html.parser")
                wrap.append(chip)
                score = BeautifulSoup(f'<div class="score-overlay {badge_cls}">prod {prod} · comp {comp} · seats {seats}</div>', "html.parser")
                wrap.append(score)
                if bypass_html:
                    wrap.append(BeautifulSoup(bypass_html, "html.parser"))
                img.replace_with(wrap)
                continue
            else:
                # no swap result — fallback orig image, grayed
                wrap = soup.new_tag("div", **{"class": "img-with-chip"})
                new_img = soup.new_tag("img", src=local, **{"class": "orig-fallback", "data-panel-idx": str(idx)})
                wrap.append(new_img)
                wrap.append(BeautifulSoup(f'<div class="panel-number-chip">{idx:02d}</div>', "html.parser"))
                wrap.append(BeautifulSoup('<div class="score-overlay pending">대기</div>', "html.parser"))
                img.replace_with(wrap)
                continue

        # orig side
        wrap = soup.new_tag("div", **{"class": "img-with-chip"})
        new_img = soup.new_tag("img", src=local, **{"data-panel-idx": str(idx), "loading": "lazy"})
        wrap.append(new_img)
        wrap.append(BeautifulSoup(f'<div class="panel-number-chip">{idx:02d}</div>', "html.parser"))
        img.replace_with(wrap)

    return str(soup)


def build_cover_row(t, swap_results):
    cover_src = cover_url_template(t)
    cell = swap_results["by_label"].get("cover") if swap_results else None
    if cell and cell.get("final"):
        f = cell["final"]
        img_url = f"{swap_results['run_dir_rel']}/{f['image']}"
        prod, comp, seats = f.get("product_score","-"), f.get("composition_score","-"), f.get("seat_count_in_B","?")
        passed = cell.get("passed", False)
        badge = "pass" if passed else "fail"
        swap_html = (
            f'<div class="img-with-chip cover-wrap"><img class="cover-img" src="{img_url}"/>'
            f'<div class="panel-number-chip">00</div>'
            f'<div class="score-overlay {badge}">prod {prod} · comp {comp} · seats {seats}</div></div>'
        )
    else:
        swap_html = (
            f'<div class="img-with-chip cover-wrap"><img class="cover-img orig-fallback" src="{cover_src}"/>'
            f'<div class="panel-number-chip">00</div></div>'
        )
    return f"""
<div class="cover-row" id="sec-cover-{t['rank']}">
  <div class="cover-cell orig">
    <div class="sec-divider cover-divider"><span class="sec-name">커버</span><span class="sec-range">1:1 대표</span></div>
    <div class="img-with-chip cover-wrap"><img class="cover-img" src="{cover_src}"/><div class="panel-number-chip">00</div></div>
  </div>
  <div class="cover-cell swap">
    <div class="sec-divider cover-divider"><span class="sec-name">커버 swap</span><span class="sec-range">밀로 2인용</span></div>
    {swap_html}
  </div>
</div>
"""


def build_tabs_bar(rank, sections_map):
    btns = []
    first_active = False
    for sec in SECTIONS:
        slug = SECTION_SLUGS[sec]
        has = True if sec == "커버" else bool(sections_map.get(sec))
        cls = "tab" + ("" if has else " disabled")
        if has and not first_active:
            cls += " active"
            first_active = True
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
        bypass_n = sum(1 for r in mismatch["resolutions"] if r["verdict"] == "bypass")
        skip_n = sum(1 for r in mismatch["resolutions"] if r["verdict"] == "skip")
        status_col = f"""
<div class="proc-h">상태</div>
<div class="status-line">시간 <b>{wall:.0f}s</b></div>
<div class="status-line">passer <b>{n_pass}/{len(cells)}</b> · prod <b>{avg_prod}</b> · comp <b>{avg_comp}</b></div>
<div class="status-line">우회 <b>{bypass_n}</b> · skip <b>{skip_n}</b></div>
"""
    else:
        status_col = '<div class="proc-h">상태</div><div class="status-line">시간 <b>—</b></div>'

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
      <div class="proc-h">템플릿 정보</div>
      <div class="tpl-name">{t['name']}</div>
      <div class="tpl-meta">
        <span class="cat-tag">{t.get('category')}</span><span>{t.get('brand','')}</span>
        <span>★ {t.get('reviewCnt',0)} 리뷰</span><span>{tpl_price_str}</span>
        <a href="{t['url']}" target="_blank" class="orig-link">원본 ↗</a>
      </div>
    </div>
    <div class="proc-grid">
      <div class="proc-col">
        <div class="proc-h">입력 — zone 분리</div>
        {build_zone_inputs()}
      </div>
      <div class="proc-col proc-col-wide">
        <div class="proc-h">입력 — 사용자 LLM 요청</div>
        <textarea class="user-prompt">{auto_req}</textarea>
        <details class="spec-details">
          <summary>밀로 spec 전체 (vision 추출)</summary>
          <div class="spec-list">
            <div><b>제품</b> {spec.get('product_name')} ({seat_n}인용)</div>
            <div><b>사이즈</b> {dims.get('width_cm','?')}×{dims.get('depth_cm','?')}×{dims.get('height_cm','?')}cm</div>
            <div><b>패브릭</b> {mat.get('upholstery','')}</div>
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

    orig_html = build_detail(t, "orig")
    swap_html = build_detail(t, "swap", swap_results) if rank == 1 else build_detail(t, "orig")

    cover_row = build_cover_row(t, swap_results) if rank == 1 else ""

    section_anchors_js = json.dumps({SECTION_SLUGS[s]: (sections_map[s][0] if sections_map.get(s) else None) for s in SECTIONS if s != "커버"})

    return f"""
<div class="view {'active' if is_first else ''}" data-rank="{rank}" data-section-anchors='{section_anchors_js}'>
  {build_process_card(t, swap_results)}
  <div class="tabs-bar">
    <div class="tabs">{build_tabs_bar(rank, sections_map)}</div>
  </div>
  <div class="dual-grid">
    <div class="dual-header">
      <div class="dual-h-left">원본 한샘 detail</div>
      <div class="dual-h-right">swap · 밀로 패브릭소파 2인용 · GPT</div>
    </div>
    {cover_row}
    <div class="dual-body">
      <div class="orig-col">{orig_html}</div>
      <div class="swap-col">{swap_html}</div>
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
<title>가구 detail 템플릿 swap — v14</title>
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

  .tabs-bar {{ position: sticky; top: var(--topbar-h); z-index: 30; background: var(--bg-alt); padding: 4px 0 0; height: calc(var(--tabs-h) + 4px); }}
  .tabs {{ display: flex; background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 0 12px; overflow-x: auto; }}
  .tab {{ padding: 12px 18px; background: transparent; border: none; border-bottom: 2px solid transparent; margin-bottom: -1px; font-family: inherit; font-size: 13px; color: #666; cursor: pointer; white-space: nowrap; }}
  .tab.active {{ color: var(--fg); border-bottom-color: var(--fg); font-weight: 600; }}
  .tab.disabled {{ opacity: 0.3; cursor: not-allowed; }}

  /* === Dual Grid === */
  .dual-grid {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; margin-top: 12px; overflow: hidden; }}
  .dual-header {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-bottom: 1px solid var(--line); background: #fafafa;
    position: sticky; top: calc(var(--topbar-h) + var(--tabs-h)); z-index: 20; }}
  .dual-h-left, .dual-h-right {{ padding: 12px 20px; font-size: 12px; font-weight: 600; color: #444; }}
  .dual-h-left {{ border-right: 1px solid var(--line); }}

  /* cover row */
  .cover-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-bottom: 1px solid var(--line); }}
  .cover-cell {{ padding: 24px 28px; }}
  .cover-cell.orig {{ border-right: 1px solid var(--line); background: #fff; }}
  .cover-cell.swap {{ background: #fafafa; }}
  .cover-wrap {{ max-width: 480px; margin: 0 auto; }}
  .cover-img {{ width: 100%; aspect-ratio: 1/1; object-fit: contain; background: #fff; border-radius: 8px; }}

  /* dual body */
  .dual-body {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; }}
  .orig-col {{ border-right: 1px solid var(--line); background: #fff; padding: 20px 28px; }}
  .swap-col {{ background: #fafafa; padding: 20px 28px; }}
  .orig-col img, .swap-col img {{ max-width: 100%; display: block; margin: 0 auto; border-radius: 4px; }}
  .orig-col iframe, .swap-col iframe {{ max-width: 100%; display: block; margin: 16px auto; }}
  .orig-col .mall_prod_info, .swap-col .mall_prod_info {{ text-align: center; }}

  /* Image wrap + overlays */
  .img-with-chip {{ position: relative; margin: 0 auto; max-width: 100%; display: inline-block; }}
  .img-with-chip img {{ display: block; }}

  /* Panel# chip — 톤다운 (작고 흐리게) */
  .panel-number-chip {{
    position: absolute; top: 8px; left: 8px;
    min-width: 22px; height: 22px; padding: 0 7px; border-radius: 11px;
    background: rgba(0,0,0,0.35); color: rgba(255,255,255,0.92);
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 600; font-family: ui-monospace, Menlo, monospace;
    z-index: 5; pointer-events: none;
    backdrop-filter: blur(4px);
  }}
  .score-overlay {{
    position: absolute; top: 8px; right: 8px;
    padding: 3px 8px; border-radius: 4px;
    background: rgba(0,0,0,0.55); color: #fff;
    font-size: 9px; font-family: ui-monospace, Menlo, monospace;
    z-index: 5; pointer-events: none;
  }}
  .score-overlay.pass {{ background: rgba(22, 163, 74, 0.78); }}
  .score-overlay.fail {{ background: rgba(220, 38, 38, 0.75); }}
  .score-overlay.pending {{ background: rgba(0,0,0,0.4); }}

  /* Bypass / skip overlay */
  .overlay-bypass {{
    position: absolute; bottom: 8px; left: 8px;
    padding: 4px 10px; border-radius: 4px;
    background: rgba(234, 88, 12, 0.92); color: #fff;
    font-size: 10px; font-weight: 700; letter-spacing: 0.02em;
    z-index: 5; cursor: help;
  }}
  .overlay-bypass.skip {{ background: rgba(120, 113, 108, 0.92); }}
  .overlay-alt {{
    position: absolute; bottom: 36px; left: 8px; right: 8px;
    padding: 8px 10px; border-radius: 6px;
    background: rgba(0,0,0,0.85); color: #fff;
    font-size: 11px; line-height: 1.45;
    z-index: 5; pointer-events: none;
    max-width: 80%;
    opacity: 0; transition: opacity 0.18s;
  }}
  .img-with-chip:hover .overlay-alt,
  .overlay-bypass:hover ~ .overlay-alt {{ opacity: 1; }}
  .overlay-alt b {{ color: #fff; font-weight: 700; display: block; margin-bottom: 3px; font-size: 12px; }}
  .orig-fallback {{ opacity: 0.4; filter: grayscale(60%); }}

  /* sec divider (cover only) */
  .sec-divider {{ display: flex; align-items: baseline; gap: 12px; margin: 0 0 16px; }}
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
  let target;
  if (slug === 'cover') {{
    target = view.querySelector(`#sec-cover-${{rank}}`);
  }} else {{
    const anchors = JSON.parse(view.dataset.sectionAnchors || '{{}}');
    const idx = anchors[slug];
    if (idx) target = view.querySelector(`.orig-col img[data-panel-idx="${{idx}}"]`);
  }}
  if (!target) return;
  const rect = target.getBoundingClientRect();
  const offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--topbar-h'))
               + parseInt(getComputedStyle(document.documentElement).getPropertyValue('--tabs-h')) + 80;
  window.scrollTo({{ top: window.scrollY + rect.top - offset, behavior: 'smooth' }});
}}
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT}")
print(f"size: {OUT.stat().st_size // 1024}KB")

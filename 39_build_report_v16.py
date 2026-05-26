"""Report v16 — panel-row split with strict left/right alignment.

핵심:
- detail HTML을 <img> tag anchor로 segment split
- 각 segment = 1 row (좌측 orig markup / 우측 swap markup)
- CSS grid row → 좌우 자동 height align
- 사이즈 row 끝나면 소재 row 좌우 동시 시작 ✓

v15 기능 유지:
- payload 모달 (prompt + refs + attempts)
- 점수 색상, bypass/skip 카드, panel# chip
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
panel_layout = {p["panel"]: p for p in json.loads(
    (TPL_ROOT / "01_sofa_992474/panel_layout_types.json").read_text()
)["panels"] if "panel_idx" in p}

SECTIONS = ["커버", "기본정보", "사이즈", "소재", "옵션", "모듈"]
SECTION_SLUGS = {
    "커버": "cover", "기본정보": "info", "사이즈": "size",
    "소재": "material", "옵션": "option", "모듈": "module",
}
COMP_COLORED_ZONES = {"intro_hero", "size_chart", "module_lineup", "color_option"}


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


def get_swap_results(t):
    if t["rank"] != 1:
        return None
    sr = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}" / "swap_results"
    for marker in ["latest_v5.txt", "latest_v4.txt", "latest.txt"]:
        latest = sr / marker
        if latest.exists():
            run_name = latest.read_text().strip()
            run_dir = sr / run_name
            if (run_dir / "summary.json").exists():
                summary = json.loads((run_dir / "summary.json").read_text())
                by_label = {c["label"]: c for c in summary["cells"]}
                return {
                    "run_dir_rel": f"../templates/{t['rank']:02d}_{t['category']}_{t['gdsNo']}/swap_results/{run_name}/gpt_image",
                    "summary": summary, "by_label": by_label,
                }
    return None


def cover_url_template(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    cov = TPL_ROOT / dir_name / "_cover_1000.jpg"
    if cov.exists():
        return f"../templates/{dir_name}/_cover_1000.jpg"
    thumbs = list((TPL_ROOT / dir_name).glob("_thumbnail.*"))
    return f"../templates/{dir_name}/{thumbs[0].name}" if thumbs else ""


def score_color(score, kind="prod", zone=None):
    if score is None or score == "-" or score == "?":
        return "score-na"
    try:
        s = int(score)
    except (ValueError, TypeError):
        return "score-na"
    if kind == "prod":
        if s >= 99: return "score-green"
        if s >= 95: return "score-amber"
        return "score-red"
    if zone in COMP_COLORED_ZONES:
        if s >= 95: return "score-green"
        if s >= 90: return "score-amber"
        return "score-red"
    return "score-neutral"


def reconstruct_prompt(panel_meta):
    dims = spec.get("dimensions", {}) or {}
    mat = spec.get("material", {}) or {}
    colors = spec.get("colors") or []
    seat_n = spec.get("seat_count", 2)
    zone = panel_meta.get("input_zone", "other")
    layout_type = panel_meta.get("layout_type", "flexible_staging")
    visible_text = panel_meta.get("visible_korean_text", "")
    scene_desc = panel_meta.get("scene_desc", "")

    spec_base = (
        f"PRODUCT: {spec.get('product_name')} ({seat_n}-seat STRICTLY)\n"
        f"좌석수: {seat_n}인\n"
        f"팔걸이: {visual.get('arm',{}).get('shape','boxy')}\n"
        f"등쿠션: {visual.get('back',{}).get('cushion_count','?')}개\n"
        f"좌방석: {visual.get('seat',{}).get('cushion_count','?')}개 {visual.get('seat',{}).get('firmness','')}\n"
        f"패브릭: {visual.get('upholstery',{}).get('material','fabric')} "
        f"({visual.get('upholstery',{}).get('texture','')}, {visual.get('upholstery',{}).get('primary_color','')})\n"
        f"다리: {visual.get('legs',{}).get('count',4)} {visual.get('legs',{}).get('shape','')}\n"
        f"프레임: {mat.get('frame','')}\n"
        f"컬러: {', '.join(colors)}"
    )

    if zone == "size_chart":
        spec_block = spec_base + f"\n\nSIZE: seat_h={dims.get('seat_height_cm')}, arm={dims.get('arm_height_cm')}, depth={dims.get('seat_depth_cm')}"
    elif zone == "structure_chart":
        spec_block = spec_base + f"\n\nSTRUCTURE: 좌방석={mat.get('seat_cushion','')}, 등쿠션={mat.get('back_cushion','')}"
    elif zone == "color_option":
        spec_block = spec_base + f"\n\nCOLORS: {', '.join(colors)}"
    elif zone == "material_swatch":
        spec_block = spec_base + f"\n\nMATERIAL: {mat.get('upholstery','')}"
    else:
        spec_block = spec_base

    layout_rule = ""
    if layout_type == "fixed_layout":
        layout_rule = f"\n\nFIXED LAYOUT — STRUCTURE PRESERVATION.\nOriginal text: {visible_text[:150]}"
    elif layout_type == "strict_white_bg":
        layout_rule = "\n\nSTRICT WHITE-BG."
    else:
        layout_rule = "\n\nFLEXIBLE STAGING."

    return f"""TASK: photorealistic furniture detail-page panel reproduction.

References: IMAGE 1 = original panel. IMAGES 2..N = MILO refs (GIF + zone refs).

ORIGINAL PANEL STAGING:
{scene_desc}

{spec_block}

USER REQUEST: 패브릭 강조, 거실 따뜻한 톤. {seat_n}인용 STRICT.

PANEL TYPE: {layout_type}.{layout_rule}

ABSOLUTE — NO TEXT IN OUTPUT."""


def zone_refs_for_panel(zone):
    use_prod = "../user_products/milo_777039/use_product"
    refs = [
        {"role": "GIF frame 1", "path": f"{use_prod}/p08_frame_01.jpg"},
        {"role": "GIF frame 2", "path": f"{use_prod}/p08_frame_02.jpg"},
        {"role": "GIF frame 3", "path": f"{use_prod}/p08_frame_03.jpg"},
    ]
    if zone == "material_swatch":
        refs.append({"role": "소재", "path": f"{use_prod}/material.png"})
    elif zone in ("color_option", "module_lineup"):
        refs += [
            {"role": "오트밀", "path": f"{use_prod}/color_01.png"},
            {"role": "라이트그레이", "path": f"{use_prod}/color_02.png"},
            {"role": "더스티로즈", "path": f"{use_prod}/color_03.png"},
        ]
    return refs


def split_detail_to_segments(t):
    """detail HTML을 img anchor로 split. Return list of (panel_idx, segment_html).
    segment 0 = preamble (before first img), panel_idx=0.
    Each subsequent segment starts with one img + trailing markup."""
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    detail_path = TPL_ROOT / dir_name / "detail.html"
    if not detail_path.exists():
        return []
    detail_html = detail_path.read_text(encoding="utf-8", errors="ignore")

    # split by <img> tag
    parts = re.split(r'(<img[^>]*>)', detail_html, flags=re.I | re.DOTALL)
    # parts: [preamble, img1, after1, img2, after2, ...]
    segments = []
    if parts and parts[0].strip():
        segments.append((0, parts[0]))
    panel_idx = 0
    for i in range(1, len(parts), 2):
        panel_idx += 1
        img_tag = parts[i]
        tail = parts[i + 1] if i + 1 < len(parts) else ""
        segments.append((panel_idx, img_tag + tail))
    return segments


def rewrite_segment(seg_html, panel_idx, side, t, swap_results=None, src_to_local=None):
    """Rewrite a single segment for orig or swap side.
    - swap side: substitute text nodes (LLM milo) + replace img with swap result wrap
    - orig side: replace img with panel img + chip wrap
    """
    soup = BeautifulSoup(seg_html, "lxml")
    # bs4 may wrap in html/body — extract body content
    body = soup.find("body")
    container = body if body else soup

    # text substitute (swap side only) — but text_subs are panel-aware via near_panel
    if side == "swap":
        # find text nodes that belong to this panel_idx
        for el in list(container.descendants):
            if isinstance(el, NavigableString):
                t_str = str(el).strip()
                if t_str and len(t_str) > 2:
                    # find substitute matching this text + near_panel
                    for sub in text_subs_data["substitutes"]:
                        if sub["original"].strip() == t_str and sub.get("near_panel") == panel_idx - 1:
                            # use near_panel of (panel_idx-1) since text appears before its img
                            original = str(el)
                            leading = original[: len(original) - len(original.lstrip())]
                            trailing = original[len(original.rstrip()):]
                            el.replace_with(leading + sub["milo"] + trailing)
                            break
                    else:
                        # try same panel
                        for sub in text_subs_data["substitutes"]:
                            if sub["original"].strip() == t_str:
                                original = str(el)
                                leading = original[: len(original) - len(original.lstrip())]
                                trailing = original[len(original.rstrip()):]
                                el.replace_with(leading + sub["milo"] + trailing)
                                break

    # Replace img
    for img in container.find_all("img"):
        src = img.get("src", "")
        src_clean = src.replace("devimage.hanssem.com", "image.hanssem.com")
        if src_clean.startswith("http://"):
            src_clean = "https://" + src_clean[7:]
        local = (src_to_local or {}).get(src) or (src_to_local or {}).get(src_clean) or src_clean

        if side == "swap" and swap_results:
            sname = f"panel_{panel_idx:02d}"
            cell = swap_results["by_label"].get(sname)
            verdict_info = verdict_by_panel.get(panel_idx, {})
            verdict = verdict_info.get("verdict", "match")
            zone = panel_layout.get(f"panel_{panel_idx:02d}.jpg", {}).get("input_zone", "other")

            if verdict == "bypass":
                alt_title = verdict_info.get("alt_title", "")
                alt_body = verdict_info.get("alt_body", "")
                wrap = BeautifulSoup(f'''
<div class="bypass-card">
  <div class="bypass-tag">우회 · 밀로엔 없는 기능</div>
  <div class="bypass-hanssem">한샘 원본: {verdict_info.get("hanssem_feature","")[:60]}</div>
  <h3 class="bypass-title">{alt_title}</h3>
  <p class="bypass-body">{alt_body}</p>
  <div class="panel-number-chip">{panel_idx:02d}</div>
</div>
''', "html.parser")
                img.replace_with(wrap)
                continue

            if verdict == "skip":
                wrap = BeautifulSoup(f'''
<div class="bypass-card skip">
  <div class="bypass-tag skip">정보 누락 · skip</div>
  <div class="bypass-hanssem">한샘: {verdict_info.get("hanssem_feature","")[:60]}</div>
  <p class="bypass-body">밀로 detail에 해당 정보 없음 — 건너뜀</p>
  <div class="panel-number-chip">{panel_idx:02d}</div>
</div>
''', "html.parser")
                img.replace_with(wrap)
                continue

            if cell and cell.get("final") and cell["final"].get("image"):
                f = cell["final"]
                img_url = f"{swap_results['run_dir_rel']}/{f['image']}"
                prod = f.get("product_score", "-")
                comp = f.get("composition_score", "-")
                seats = f.get("seat_count_in_B", "?")
                text_flag = f.get("text_in_image")
                struct_pres = f.get("structure_preserved", True)
                prod_cls = score_color(prod, "prod")
                comp_cls = score_color(comp, "comp", zone)

                attempts_meta = []
                for a in cell.get("attempts", []):
                    attempts_meta.append({
                        "attempt": a.get("attempt"), "strategy": a.get("strategy"),
                        "prod": a.get("product_score"), "comp": a.get("composition_score"),
                        "seats": a.get("seat_count_in_B"), "text_in_image": a.get("text_in_image"),
                        "verdict": a.get("verdict"), "notes": (a.get("notes") or "")[:500],
                        "specific_failures": a.get("specific_failures") or [],
                    })
                pmeta = panel_layout.get(f"panel_{panel_idx:02d}.jpg", {})
                pmeta_for_prompt = {
                    "input_zone": zone, "layout_type": cell.get("layout_type"),
                    "visible_korean_text": pmeta.get("visible_korean_text", ""),
                    "scene_desc": pmeta.get("scene_desc", ""),
                }
                payload = {
                    "panel": panel_idx, "zone": zone, "layout": cell.get("layout_type"),
                    "thresholds": cell.get("thresholds"),
                    "strategies_used": "/".join(cell.get("strategies_used", [])),
                    "attempts": attempts_meta, "passed": cell.get("passed"),
                    "prompt": reconstruct_prompt(pmeta_for_prompt),
                    "refs": [{"role": "IMAGE 1 (original)", "path": f"../templates/01_sofa_992474/panel_{panel_idx:02d}.jpg"}] + zone_refs_for_panel(zone),
                }
                payload_json = json.dumps(payload, ensure_ascii=False).replace('"', "&quot;")
                wrap = BeautifulSoup(f'''
<div class="img-with-chip" data-panel-idx="{panel_idx}">
  <img src="{img_url}" data-panel-idx="{panel_idx}" loading="lazy"/>
  <div class="panel-number-chip">{panel_idx:02d}</div>
  <div class="score-row">
    <span class="score-badge {prod_cls}">prod {prod}</span>
    <span class="score-badge {comp_cls}">comp {comp}</span>
    <span class="score-badge score-neutral">{seats}인</span>
    {'<span class="score-badge score-red">TEXT</span>' if text_flag else ''}
    {'<span class="score-badge score-red">STR</span>' if not struct_pres else ''}
    <button class="payload-btn" onclick="showPayload(this)" data-payload="{payload_json}">i</button>
  </div>
</div>
''', "html.parser")
                img.replace_with(wrap)
                continue

        # orig side or fallback
        wrap = BeautifulSoup(f'''
<div class="img-with-chip">
  <img src="{local}" data-panel-idx="{panel_idx}"/>
  <div class="panel-number-chip">{panel_idx:02d}</div>
</div>
''', "html.parser")
        img.replace_with(wrap)

    if body:
        return body.decode_contents()
    return str(container)


def build_panel_rows(t, swap_results):
    """Build panel-row grid: each segment = 1 row, left orig / right swap."""
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    meta_path = TPL_ROOT / dir_name / "meta.json"
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

    segments = split_detail_to_segments(t)
    rows_html = []
    panel_count = meta.get("detail_img_count") or meta.get("panel_count") or len(meta.get("detail_imgs", []))
    sections_map = assign_sections(panel_count)
    # panel_idx → section anchor id
    section_anchor_of = {}
    for sec_name, indices in sections_map.items():
        if sec_name == "커버" or not indices:
            continue
        section_anchor_of[indices[0]] = SECTION_SLUGS[sec_name]

    for panel_idx, seg_html in segments:
        anchor = section_anchor_of.get(panel_idx)
        anchor_attr = f'id="sec-{anchor}-{t["rank"]}"' if anchor else ""
        sec_div = ""
        if anchor:
            sec_name = [k for k, v in SECTION_SLUGS.items() if v == anchor][0]
            indices = sections_map[sec_name]
            rng = f"panel {indices[0]}" + (f"–{indices[-1]}" if len(indices) > 1 else "")
            sec_div = f'<div class="section-divider"><span class="sec-name">{sec_name}</span><span class="sec-range">{rng}</span></div>'

        orig_seg = rewrite_segment(seg_html, panel_idx, "orig", t, swap_results, src_to_local)
        swap_seg = rewrite_segment(seg_html, panel_idx, "swap", t, swap_results, src_to_local)

        if sec_div:
            rows_html.append(sec_div)
        rows_html.append(f'''
<div class="panel-row" {anchor_attr} data-panel-idx="{panel_idx}">
  <div class="cell orig">{orig_seg}</div>
  <div class="cell swap">{swap_seg}</div>
</div>
''')
    return "\n".join(rows_html)


def build_cover_row(t, swap_results):
    cover_src = cover_url_template(t)
    cell = swap_results["by_label"].get("cover") if swap_results else None
    if cell and cell.get("final"):
        f = cell["final"]
        img_url = f"{swap_results['run_dir_rel']}/{f['image']}"
        prod = f.get("product_score","-")
        comp = f.get("composition_score","-")
        seats = f.get("seat_count_in_B","?")
        prod_cls = score_color(prod, "prod")
        comp_cls = score_color(comp, "comp", "intro_hero")
        attempts_meta = []
        for a in cell.get("attempts", []):
            attempts_meta.append({
                "attempt": a.get("attempt"), "strategy": a.get("strategy"),
                "prod": a.get("product_score"), "comp": a.get("composition_score"),
                "seats": a.get("seat_count_in_B"), "verdict": a.get("verdict"),
                "notes": (a.get("notes") or "")[:500],
                "specific_failures": a.get("specific_failures") or [],
                "text_in_image": a.get("text_in_image"),
            })
        cover_panel_meta = {"input_zone": "intro_hero", "layout_type": "strict_white_bg", "visible_korean_text": "", "scene_desc": "Hero cover shot on white seamless backdrop."}
        payload = {
            "panel": "cover", "zone": "intro_hero", "layout": "strict_white_bg",
            "thresholds": cell.get("thresholds"),
            "strategies_used": "/".join(cell.get("strategies_used", [])),
            "attempts": attempts_meta, "passed": cell.get("passed"),
            "prompt": reconstruct_prompt(cover_panel_meta),
            "refs": [{"role": "IMAGE 1 (cover)", "path": cover_src}] + zone_refs_for_panel("intro_hero"),
        }
        payload_json = json.dumps(payload, ensure_ascii=False).replace('"', "&quot;")
        swap_html = f'''
<div class="img-with-chip cover-wrap">
  <img class="cover-img" src="{img_url}"/>
  <div class="panel-number-chip">00</div>
  <div class="score-row">
    <span class="score-badge {prod_cls}">prod {prod}</span>
    <span class="score-badge {comp_cls}">comp {comp}</span>
    <span class="score-badge score-neutral">{seats}인</span>
    <button class="payload-btn" onclick="showPayload(this)" data-payload="{payload_json}">i</button>
  </div>
</div>
'''
    else:
        swap_html = f'<div class="img-with-chip cover-wrap"><img class="cover-img orig-fallback" src="{cover_src}"/><div class="panel-number-chip">00</div></div>'

    return f'''
<div class="panel-row cover-row" id="sec-cover-{t['rank']}">
  <div class="cell orig">
    <div class="section-divider cover-divider"><span class="sec-name">커버</span><span class="sec-range">1:1 대표</span></div>
    <div class="img-with-chip cover-wrap"><img class="cover-img" src="{cover_src}"/><div class="panel-number-chip">00</div></div>
  </div>
  <div class="cell swap">
    <div class="section-divider cover-divider"><span class="sec-name">커버 swap</span><span class="sec-range">밀로 2인용</span></div>
    {swap_html}
  </div>
</div>
'''


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
        out += f'<div class="zone-block"><div class="zone-label">{title} <span class="zone-count">{len(files)}장</span></div><div class="zone-thumbs">{thumbs}</div></div>'
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
        f"제품: {spec.get('product_name')}. 사이즈 {dims.get('width_cm','?')}×{dims.get('depth_cm','?')}×{dims.get('height_cm','?')}cm. "
        f"패브릭 {mat.get('upholstery','')}, 컬러 {', '.join(colors)}. {seat_n}인용 STRICT."
    )

    if swap_results:
        cells = swap_results["summary"]["cells"]
        wall = swap_results["summary"].get("wall_seconds", 0)
        n_pass = sum(1 for c in cells if c["passed"])
        bypass_n = sum(1 for r in mismatch["resolutions"] if r["verdict"] == "bypass")
        skip_n = sum(1 for r in mismatch["resolutions"] if r["verdict"] == "skip")
        status_col = f'''
<div class="proc-h">상태</div>
<div class="status-line">시간 <b>{wall:.0f}s</b></div>
<div class="status-line">passer <b>{n_pass}/{len(cells)}</b></div>
<div class="status-line">우회 <b>{bypass_n}</b> · skip <b>{skip_n}</b></div>
<div class="status-line legend"><span class="dot green"></span>≥99 <span class="dot amber"></span>95~98 <span class="dot red"></span>&lt;95</div>
<div class="status-line legend">구도색: cover/size/lineup만</div>
'''
    else:
        status_col = '<div class="proc-h">상태</div><div class="status-line">시간 <b>—</b></div>'

    return f'''
<details class="process-card">
  <summary>
    <span class="proc-title">공정 설정</span>
    <span class="proc-summary">
      <span class="badge tpl-badge">템플릿 <b>#{rank} {t.get('category')}</b> · {t['name'][:24]}{'…' if len(t['name'])>24 else ''}</span>
      <span class="badge"><b>GPT image</b> · QA feedback</span>
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
        <div class="proc-h">입력 — LLM 요청</div>
        <textarea class="user-prompt">{auto_req}</textarea>
        <details class="spec-details">
          <summary>밀로 spec 전체 (vision 추출)</summary>
          <div class="spec-list">
            <div><b>제품</b> {spec.get('product_name')}</div>
            <div><b>사이즈</b> {dims.get('width_cm','?')}×{dims.get('depth_cm','?')}×{dims.get('height_cm','?')}cm · 좌방석 {dims.get('seat_depth_cm','?')}×{dims.get('seat_height_cm','?')}cm</div>
            <div><b>패브릭</b> {mat.get('upholstery','')}</div>
            <div><b>좌방석</b> {mat.get('seat_cushion','')}</div>
            <div><b>등쿠션</b> {mat.get('back_cushion','')}</div>
            <div><b>경도</b> {mat.get('cushion_firmness','')}</div>
            <div><b>프레임</b> {mat.get('frame','')}</div>
            <div><b>컬러</b> {', '.join(colors)}</div>
          </div>
        </details>
      </div>
      <div class="proc-col">{status_col}</div>
    </div>
  </div>
</details>
'''


cover_imgs = {t["gdsNo"]: cover_url_template(t) for t in data["top6"]}


def chip(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    name_short = t["name"][:24] + ("…" if len(t["name"]) > 24 else "")
    swap = get_swap_results(t)
    ready = '<span class="chip-ready done">✓</span>' if swap else ""
    return f'''
<button class="chip {'selected' if rank == 1 else ''}" data-rank="{rank}" onclick="selectTpl({rank})">
  {ready}<span class="chip-rank">#{rank}</span>
  <img class="chip-cover" src="{cover_imgs[gds]}"/>
  <span class="chip-meta"><span class="chip-cat">{cat}</span><span class="chip-name">{name_short}</span></span>
</button>'''


def view(t):
    rank = t["rank"]
    is_first = rank == 1
    swap_results = get_swap_results(t) if rank == 1 else None
    meta_path = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}/meta.json"
    meta = json.loads(meta_path.read_text())
    panel_count = meta.get("detail_img_count") or meta.get("panel_count") or len(meta.get("detail_imgs", []))
    sections_map = assign_sections(panel_count)

    cover_row = build_cover_row(t, swap_results) if rank == 1 else ""
    panel_rows = build_panel_rows(t, swap_results) if rank == 1 else ""

    section_anchors_js = json.dumps({SECTION_SLUGS[s]: (sections_map[s][0] if sections_map.get(s) else None) for s in SECTIONS if s != "커버"})

    return f'''
<div class="view {'active' if is_first else ''}" data-rank="{rank}" data-section-anchors='{section_anchors_js}'>
  {build_process_card(t, swap_results)}
  <div class="tabs-bar">
    <div class="tabs">{build_tabs_bar(rank, sections_map)}</div>
  </div>
  <div class="dual-grid">
    <div class="dual-header">
      <div class="dual-h-left">원본 한샘 detail</div>
      <div class="dual-h-right">swap · 밀로 2인용 · GPT</div>
    </div>
    {cover_row}
    {panel_rows}
  </div>
</div>
'''


chips_html = "\n".join(chip(t) for t in data["top6"])
views_html = "\n".join(view(t) for t in data["top6"])

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>가구 detail 템플릿 swap — v16</title>
<link rel="stylesheet" href="https://res.remodeling.hanssem.com/font/pretendard/pretendard.css"/>
<style>
  :root {{
    --bg: #fff; --bg-alt: #f4f4f6;
    --fg: #1a1a1a; --fg-soft: #555; --muted: #888;
    --line: #e5e5e5; --line-soft: #efefef;
    --accent: #ff7a00; --accent-soft: #fff5ec;
    --good: #16a34a; --warn: #f59e0b; --bad: #dc2626;
    --topbar-h: 56px; --tabs-h: 50px;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: "Pretendard", -apple-system, system-ui, sans-serif;
    background: var(--bg-alt); color: var(--fg); -webkit-font-smoothing: antialiased;
    font-size: 14px; line-height: 1.5; }}
  .topbar {{ position: sticky; top: 0; z-index: 100; background: #fff;
    border-bottom: 1px solid var(--line); padding: 12px 24px; height: var(--topbar-h); }}
  .topbar-row {{ display: flex; align-items: center; gap: 16px; max-width: 1600px; margin: 0 auto; overflow-x: auto; }}
  .topbar h1 {{ margin: 0; font-size: 13px; font-weight: 600; color: var(--fg-soft); white-space: nowrap; }}
  .chips {{ display: flex; gap: 8px; flex: 1; }}
  .chip {{ position: relative; display: flex; align-items: center; gap: 8px;
    padding: 6px 14px 6px 6px; border: 1px solid var(--line); background: #fff;
    border-radius: 999px; cursor: pointer; font-family: inherit; font-size: 12px; color: #555; white-space: nowrap; }}
  .chip.selected {{ border-color: var(--fg); background: var(--fg); color: #fff; }}
  .chip-ready {{ position: absolute; top: 2px; right: 4px; color: var(--good); font-size: 10px; font-weight: 700; }}
  .chip-cover {{ width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }}
  .chip-rank {{ font-weight: 700; color: var(--accent); }}
  .chip-meta {{ display: flex; flex-direction: column; align-items: flex-start; line-height: 1.15; }}
  .chip-cat {{ font-size: 10px; opacity: 0.7; }}
  .chip-name {{ font-size: 11px; }}

  .view {{ display: none; padding: 24px 32px; max-width: 1600px; margin: 0 auto; }}
  .view.active {{ display: block; }}

  /* Process Card (same as v15) */
  .process-card {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; margin-bottom: 16px; overflow: hidden; }}
  .process-card > summary {{ list-style: none; cursor: pointer; padding: 14px 20px; display: flex; align-items: center; gap: 14px; background: #fff; }}
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
  .status-line.legend {{ font-size: 10px; }}
  .dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin: 0 3px 0 6px; vertical-align: -1px; }}
  .dot.green {{ background: var(--good); }} .dot.amber {{ background: var(--warn); }} .dot.red {{ background: var(--bad); }}

  .tabs-bar {{ position: sticky; top: var(--topbar-h); z-index: 30; background: var(--bg-alt); padding: 4px 0 0; height: calc(var(--tabs-h) + 4px); }}
  .tabs {{ display: flex; background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 0 12px; overflow-x: auto; }}
  .tab {{ padding: 12px 18px; background: transparent; border: none; border-bottom: 2px solid transparent; margin-bottom: -1px; font-family: inherit; font-size: 13px; color: #666; cursor: pointer; white-space: nowrap; }}
  .tab.active {{ color: var(--fg); border-bottom-color: var(--fg); font-weight: 600; }}
  .tab.disabled {{ opacity: 0.3; cursor: not-allowed; }}

  /* === Dual Grid: panel-row based === */
  .dual-grid {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; margin-top: 12px; overflow: hidden; }}
  .dual-header {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-bottom: 1px solid var(--line); background: #fafafa;
    position: sticky; top: calc(var(--topbar-h) + var(--tabs-h)); z-index: 20; }}
  .dual-h-left, .dual-h-right {{ padding: 12px 20px; font-size: 12px; font-weight: 600; color: #444; }}
  .dual-h-left {{ border-right: 1px solid var(--line); }}

  /* section divider (spans both cols, above row) */
  .section-divider {{
    display: flex; align-items: baseline; gap: 12px;
    padding: 20px 24px 10px; background: linear-gradient(to bottom, #fafafa, #fff);
    border-top: 1px solid var(--line-soft);
    scroll-margin-top: calc(var(--topbar-h) + var(--tabs-h) + 40px);
  }}
  .section-divider .sec-name {{ font-size: 13px; font-weight: 700; padding: 4px 12px;
    background: var(--accent-soft); border-left: 3px solid var(--accent); border-radius: 0 4px 4px 0; }}
  .section-divider .sec-range {{ font-size: 10px; color: var(--muted); font-family: ui-monospace, monospace; }}
  .section-divider.cover-divider .sec-name {{ background: #e8f4ff; border-left-color: #2563eb; margin: 0 0 12px; }}

  /* === PANEL ROW — strict left/right grid === */
  .panel-row {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 0;
    border-bottom: 1px solid var(--line-soft);
    scroll-margin-top: calc(var(--topbar-h) + var(--tabs-h) + 40px);
  }}
  .panel-row:last-child {{ border-bottom: none; }}
  .cell {{ padding: 20px 24px; min-width: 0; overflow: hidden; }}
  .cell.orig {{ border-right: 1px solid var(--line); background: #fff; }}
  .cell.swap {{ background: #fafafa; }}
  .cell img {{ max-width: 100%; display: block; margin: 0 auto; border-radius: 4px; }}
  .cell iframe {{ max-width: 100%; display: block; margin: 16px auto; }}
  .cell .mall_prod_info {{ text-align: center; line-height: 0; font-size: 0; }}
  .cell .mall_prod_info > * {{ line-height: normal; font-size: 14px; }}
  .cover-row .cell .cover-img {{ max-width: 480px; aspect-ratio: 1/1; object-fit: contain; background: #fff; }}

  /* image overlays */
  .img-with-chip {{ position: relative; margin: 0 auto; max-width: 100%; display: inline-block; }}
  .img-with-chip img {{ display: block; }}
  .panel-number-chip {{
    position: absolute; top: 8px; left: 8px;
    min-width: 22px; height: 22px; padding: 0 7px; border-radius: 11px;
    background: rgba(0,0,0,0.35); color: rgba(255,255,255,0.92);
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 600; font-family: ui-monospace, Menlo, monospace;
    z-index: 5; pointer-events: none; backdrop-filter: blur(4px);
  }}
  .score-row {{ position: absolute; bottom: 8px; left: 8px; right: 8px; display: flex; gap: 4px; flex-wrap: wrap; align-items: center; z-index: 6; }}
  .score-badge {{ font-size: 9px; font-family: ui-monospace, Menlo, monospace; padding: 2px 6px; border-radius: 4px; line-height: 1.4; background: rgba(0,0,0,0.55); color: #fff; }}
  .score-badge.score-green {{ background: rgba(22, 163, 74, 0.92); }}
  .score-badge.score-amber {{ background: rgba(245, 158, 11, 0.92); color: #1a1a1a; }}
  .score-badge.score-red {{ background: rgba(220, 38, 38, 0.92); }}
  .score-badge.score-neutral {{ background: rgba(0,0,0,0.55); }}
  .score-badge.score-na {{ background: rgba(0,0,0,0.3); }}
  .payload-btn {{ margin-left: auto; width: 20px; height: 20px; border-radius: 50%; background: rgba(255,255,255,0.95); color: var(--fg); border: 1px solid rgba(0,0,0,0.15); font-size: 10px; font-style: italic; font-family: serif; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; padding: 0; }}

  /* bypass / skip cards */
  .bypass-card {{ position: relative; padding: 24px 20px; margin: 16px auto; max-width: 95%;
    background: linear-gradient(135deg, #fff7ed, #fff1e6); border: 1px solid #fbbf24; border-radius: 12px;
    box-shadow: 0 1px 3px rgba(234, 88, 12, 0.1); }}
  .bypass-card.skip {{ background: linear-gradient(135deg, #f5f5f4, #e7e5e4); border-color: #a8a29e; }}
  .bypass-tag {{ display: inline-block; font-size: 10px; font-weight: 700; letter-spacing: 0.02em; padding: 3px 10px; border-radius: 4px; background: rgba(234, 88, 12, 0.92); color: #fff; margin-bottom: 12px; }}
  .bypass-tag.skip {{ background: rgba(120, 113, 108, 0.92); }}
  .bypass-hanssem {{ font-size: 11px; color: var(--muted); margin-bottom: 8px; font-style: italic; }}
  .bypass-title {{ margin: 0 0 8px; font-size: 17px; font-weight: 700; color: var(--fg); letter-spacing: -0.01em; }}
  .bypass-body {{ margin: 0; font-size: 13px; color: var(--fg-soft); line-height: 1.6; }}
  .orig-fallback {{ opacity: 0.4; filter: grayscale(60%); }}

  /* modal */
  .modal-backdrop {{ position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: none; align-items: center; justify-content: center; z-index: 1000; }}
  .modal-backdrop.open {{ display: flex; }}
  .modal-content {{ background: #fff; width: 92%; max-width: 1280px; max-height: 92vh; overflow-y: auto; border-radius: 14px; padding: 28px 32px; box-shadow: 0 20px 80px rgba(0,0,0,0.5); position: relative; }}
  .modal-h {{ font-size: 18px; font-weight: 700; margin: 0 0 4px; }}
  .modal-sub {{ font-size: 12px; color: var(--muted); margin-bottom: 20px; }}
  .modal-section {{ margin: 20px 0 12px; padding-top: 16px; border-top: 1px solid var(--line); }}
  .modal-section-h {{ font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 10px; }}
  .modal-close {{ position: absolute; top: 16px; right: 24px; cursor: pointer; font-size: 22px; color: var(--muted); border: none; background: none; padding: 4px 10px; }}
  .attempts-table {{ width: 100%; font-size: 11px; border-collapse: collapse; }}
  .attempts-table th {{ background: var(--bg-alt); padding: 6px 10px; text-align: left; border-bottom: 2px solid var(--line); font-weight: 700; }}
  .attempts-table td {{ padding: 8px 10px; border-bottom: 1px solid var(--line-soft); vertical-align: top; font-family: ui-monospace, Menlo, monospace; }}
  .attempts-table td.notes {{ font-size: 10px; color: var(--fg-soft); max-width: 360px; font-family: inherit; }}
  .attempts-table td.failures {{ font-size: 10px; color: var(--bad); font-family: inherit; }}
  .modal-prompt-pre {{ background: #1a1a1d; color: #e5e7eb; padding: 14px 16px; border-radius: 8px; font-family: ui-monospace, Menlo, monospace; font-size: 11px; line-height: 1.6; white-space: pre-wrap; max-height: 400px; overflow-y: auto; border: 1px solid #2a2a2f; }}
  .modal-refs-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }}
  .modal-ref {{ border: 1px solid var(--line); border-radius: 6px; overflow: hidden; background: #fff; }}
  .modal-ref img {{ width: 100%; aspect-ratio: 1/1; object-fit: cover; display: block; }}
  .modal-ref-label {{ padding: 6px 8px; font-size: 10px; color: var(--fg); background: #fafafa; border-top: 1px solid var(--line); }}
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

<div class="modal-backdrop" id="modal-backdrop" onclick="if(event.target===this)closeModal()">
  <div class="modal-content" id="modal-content"></div>
</div>

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
  const target = view.querySelector(`#sec-${{slug}}-${{rank}}`);
  if (!target) return;
  const rect = target.getBoundingClientRect();
  const offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--topbar-h'))
               + parseInt(getComputedStyle(document.documentElement).getPropertyValue('--tabs-h')) + 80;
  window.scrollTo({{ top: window.scrollY + rect.top - offset, behavior: 'smooth' }});
}}
function showPayload(btn) {{
  const raw = btn.dataset.payload;
  const data = JSON.parse(raw.replace(/&quot;/g, '"'));
  const mc = document.getElementById('modal-content');
  let attemptsHtml = '<table class="attempts-table"><thead><tr><th>#</th><th>strategy</th><th>prod</th><th>comp</th><th>seats</th><th>verdict</th><th>failures</th><th>notes</th></tr></thead><tbody>';
  for (const a of (data.attempts || [])) {{
    const failures = (a.specific_failures || []).join(' · ');
    attemptsHtml += `<tr><td>${{a.attempt}}</td><td>${{a.strategy||'?'}}</td><td>${{a.prod||'-'}}</td><td>${{a.comp||'-'}}</td><td>${{a.seats||'?'}}</td><td>${{a.verdict||'?'}}${{a.text_in_image?' · TEXT!':''}}</td><td class="failures">${{failures||'—'}}</td><td class="notes">${{a.notes||''}}</td></tr>`;
  }}
  attemptsHtml += '</tbody></table>';
  let refsHtml = '<div class="modal-refs-grid">';
  for (const r of (data.refs || [])) {{
    refsHtml += `<div class="modal-ref"><img src="${{r.path}}" loading="lazy"/><div class="modal-ref-label">${{r.role}}</div></div>`;
  }}
  refsHtml += '</div>';
  const promptEsc = (data.prompt || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  mc.innerHTML = `
    <button class="modal-close" onclick="closeModal()">✕</button>
    <h3 class="modal-h">Panel ${{data.panel}} · payload</h3>
    <div class="modal-sub">zone: <b>${{data.zone}}</b> · layout: <b>${{data.layout}}</b> · thresholds: <b>prod ${{data.thresholds?.product||'-'}}+ / comp ${{data.thresholds?.composition||'-'}}+</b> · strategies: <b>${{data.strategies_used||'-'}}</b> · ${{data.passed?'✅ passed':'❌ failed'}}</div>
    <div class="modal-section"><div class="modal-section-h">📎 첨부 이미지</div>${{refsHtml}}</div>
    <div class="modal-section"><div class="modal-section-h">📝 prompt</div><pre class="modal-prompt-pre">${{promptEsc}}</pre></div>
    <div class="modal-section"><div class="modal-section-h">🔁 attempts</div>${{attemptsHtml}}</div>
  `;
  document.getElementById('modal-backdrop').classList.add('open');
}}
function closeModal() {{ document.getElementById('modal-backdrop').classList.remove('open'); }}
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT}")
print(f"size: {OUT.stat().st_size // 1024}KB")

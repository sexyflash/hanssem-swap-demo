"""Report v5 — feedback round 3.

변경:
- 템플릿 정보 → 공정 카드 안 (별도 header row 제거)
- 커버 = 대표 썸네일을 detail 위에 별도 박기 (panel_01과 별개)
- anchor 스크롤: getBoundingClientRect 기반으로 panel-body 안에서만
- 탭은 그대로 유지
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
    """커버는 별도 영역(panel 아님). panel 1..n을 나머지 5섹션에 균등 분배."""
    n = panel_count
    if n == 0:
        return {"커버": []}
    result = {"커버": []}  # cover handled separately
    remaining_sections = SECTIONS[1:]
    per = max(1, n // len(remaining_sections))
    idx = 1
    for i, s in enumerate(remaining_sections):
        if idx > n:
            break
        if i == len(remaining_sections) - 1:
            end = n
        else:
            end = min(idx + per - 1, n)
        result[s] = list(range(idx, end + 1))
        idx = end + 1
    return result


def cover_url(t: dict) -> str:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    panel_dir = TPL_ROOT / dir_name
    thumbs = list(panel_dir.glob("_thumbnail.*"))
    return f"../templates/{dir_name}/{thumbs[0].name}" if thumbs else ""


def rewrite_detail_html(t: dict, side: str) -> tuple[str, dict]:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    detail_path = TPL_ROOT / dir_name / "detail.html"
    meta_path = TPL_ROOT / dir_name / "meta.json"

    detail_html = (
        detail_path.read_text(encoding="utf-8", errors="ignore")
        if detail_path.exists() else ""
    )
    meta = json.loads(meta_path.read_text())
    detail_imgs = meta.get("detail_imgs", [])
    detail_img_count = meta.get("detail_img_count") or len(detail_imgs)
    panel_dir = TPL_ROOT / dir_name

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

    rewritten = re.sub(r"<img[^>]+>", repl_img, detail_html)

    sections = assign_sections(detail_img_count)
    # inject section dividers (skip 커버 — handled by separate cover block)
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
        pattern = f'(<img[^>]*data-panel-idx="{first_idx}"[^>]*>)'
        rewritten = re.sub(pattern, divider + r"\1", rewritten, count=1)

    # prepend cover block (separate from detail panels)
    cover_src = cover_url(t)
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
        if sec == "커버":
            has = True  # cover always exists
        else:
            has = sec in sections and sections[sec]
        cls = "tab" + ("" if has else " disabled")
        if has and not first_active_set:
            cls += " active"
            first_active_set = True
        attrs = (
            f'onclick="scrollToSection({rank}, \'{slug}\')"' if has else "disabled"
        )
        btns.append(f'<button class="{cls}" data-slug="{slug}" {attrs}>{sec}</button>')
    return "\n".join(btns)


def build_process_card(t: dict, fact: dict) -> str:
    """Process card — accordion, includes template info."""
    rank = t["rank"]
    desc = fact.get("description") or ""
    cats = " / ".join([c for c in (fact.get("categories") or []) if c][-3:])
    keywords = ", ".join([k for k in (fact.get("searchKeywords") or []) if k][:8])
    price = fact.get("price") or {}
    dc = price.get("dc")
    normal = price.get("normal")
    price_str = f"{dc:,}원 (정가 {normal:,}원)" if dc and normal else ""
    gif_panels = fact.get("gif_panels", [])
    panel_count = fact.get("panel_count", 0)
    tpl_price = t.get("price")
    tpl_price_str = f"{tpl_price:,}원" if tpl_price else ""

    return f"""
<details class="process-card" open>
  <summary>
    <span class="proc-title">공정 설정</span>
    <span class="proc-summary">
      <span class="badge tpl-badge">템플릿 <b>#{rank} {t.get('category')}</b> · {t['name'][:24]}{'…' if len(t['name'])>24 else ''}</span>
      <span class="badge">방식 <b id="mode-display-{rank}">K2</b></span>
      <span class="badge">입력 <b>대기</b></span>
      <span class="badge">상태 <b>—</b></span>
    </span>
    <span class="proc-toggle">▾</span>
  </summary>

  <div class="proc-content">
    <div class="tpl-info-row">
      <div class="tpl-info">
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
        <div class="proc-h">입력 — 사용자 제품</div>
        <div class="input-card pending">
          <div class="input-thumb-box">
            <div class="pending-mark">슬라이스<br/>대기</div>
          </div>
          <div class="input-meta">
            <div class="input-name">{fact.get('gdsNm','(미지정)')}</div>
            <div class="input-cat">{cats}</div>
            <div class="input-price">{price_str}</div>
            <div class="input-note">GIF panel_{gif_panels[0]:02d} (360°) → frame N장 추출 예정</div>
          </div>
        </div>
        <div class="proc-h" style="margin-top:12px;">입력 — 사용자 LLM 요청</div>
        <textarea class="user-prompt" placeholder="아직 미입력. 예: 패브릭 소재 강조, 가족 거실 분위기, 따뜻한 톤 — 사용자가 직접 작성하는 카피/요구사항."></textarea>
      </div>

      <div class="proc-col proc-meta">
        <div class="proc-h">참고 메타 (자동 수집)</div>
        <div class="fact-desc">{desc}</div>
        <details class="kw-details">
          <summary>키워드 {len([k for k in (fact.get('searchKeywords') or []) if k])}개</summary>
          <div class="fact-keywords">{keywords}</div>
        </details>
        <div class="input-stats">
          panel <b>{panel_count}장</b>
          · 텍스트 노드 <b>{len(fact.get('text_nodes_in_detail_html', []))}</b>
        </div>
      </div>

      <div class="proc-col proc-status">
        <div class="proc-h">상태</div>
        <div class="status-line">처리 시간 <b>—</b></div>
        <div class="status-line">QA 점수 <b>—</b></div>
        <div class="status-line">시도 <b>—</b></div>
        <button class="run-btn" disabled>swap 실행 (입력 대기)</button>
      </div>
    </div>
  </div>
</details>
"""


cover_imgs = {t["gdsNo"]: cover_url(t) for t in data["top6"]}


def chip(t: dict) -> str:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    name_short = t["name"][:24] + ("…" if len(t["name"]) > 24 else "")
    return f"""
<button class="chip {'selected' if rank == 1 else ''}" data-rank="{rank}" onclick="selectTpl({rank})">
  <span class="chip-rank">#{rank}</span>
  <img class="chip-cover" src="{cover_imgs[gds]}" alt="{cat}"/>
  <span class="chip-meta">
    <span class="chip-cat">{cat}</span><span class="chip-name">{name_short}</span>
  </span>
</button>"""


def view(t: dict) -> str:
    rank = t["rank"]
    is_first = rank == 1
    orig_html, sections_orig = rewrite_detail_html(t, "orig")
    swap_html, _ = rewrite_detail_html(t, "swap")
    process_card = build_process_card(t, milo_fact)
    tabs = build_tabs(rank, sections_orig)

    return f"""
<div class="view {'active' if is_first else ''}" data-rank="{rank}">
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
      <div class="pane-label">swap 결과 <span class="hint">— 입력 대기</span></div>
      <div class="pane-body swap-body" data-side="swap" data-rank="{rank}">{swap_html}</div>
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
<title>가구 detail 템플릿 swap 미리보기 — v5</title>
<link rel="stylesheet" href="https://res.remodeling.hanssem.com/font/pretendard/pretendard.css"/>
<style>
  :root {{
    --bg: #ffffff;
    --bg-alt: #f4f4f6;
    --fg: #1a1a1a;
    --fg-soft: #555;
    --muted: #888;
    --line: #e5e5e5;
    --line-soft: #efefef;
    --accent: #ff7a00;
    --accent-soft: #fff5ec;
    --good: #16a34a;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Pretendard", -apple-system, system-ui, sans-serif;
    background: var(--bg-alt);
    color: var(--fg);
    -webkit-font-smoothing: antialiased;
    font-size: 14px; line-height: 1.5;
  }}
  /* Topbar */
  .topbar {{
    position: sticky; top: 0; z-index: 100;
    background: #fff; border-bottom: 1px solid var(--line);
    padding: 12px 24px;
  }}
  .topbar-row {{
    display: flex; align-items: center; gap: 16px;
    max-width: 1600px; margin: 0 auto; overflow-x: auto;
  }}
  .topbar h1 {{ margin: 0; font-size: 13px; font-weight: 600; color: var(--fg-soft); white-space: nowrap; }}
  .chips {{ display: flex; gap: 8px; flex: 1; }}
  .chip {{
    display: flex; align-items: center; gap: 8px;
    padding: 6px 14px 6px 6px; border: 1px solid var(--line); background: #fff;
    border-radius: 999px; cursor: pointer; transition: all 0.15s;
    font-family: inherit; font-size: 12px; color: #555; white-space: nowrap;
  }}
  .chip:hover {{ border-color: #999; }}
  .chip.selected {{ border-color: var(--fg); background: var(--fg); color: #fff; }}
  .chip-cover {{ width: 28px; height: 28px; border-radius: 50%; object-fit: cover; background: #f3f3f3; }}
  .chip-rank {{ font-weight: 700; color: var(--accent); }}
  .chip-meta {{ display: flex; flex-direction: column; align-items: flex-start; line-height: 1.15; }}
  .chip-cat {{ font-size: 10px; opacity: 0.7; }}
  .chip-name {{ font-size: 11px; }}

  /* View */
  .view {{ display: none; padding: 24px 32px; max-width: 1600px; margin: 0 auto; }}
  .view.active {{ display: block; }}

  /* Accordion process card */
  .process-card {{
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
    margin-bottom: 16px; overflow: hidden;
  }}
  .process-card > summary {{
    list-style: none; cursor: pointer; padding: 14px 20px;
    display: flex; align-items: center; gap: 14px; background: #fff;
    transition: background 0.15s;
  }}
  .process-card > summary::-webkit-details-marker {{ display: none; }}
  .process-card > summary:hover {{ background: #fafafa; }}
  .proc-title {{ font-size: 13px; font-weight: 600; color: var(--fg); white-space: nowrap; }}
  .proc-summary {{ display: flex; gap: 6px; flex-wrap: wrap; flex: 1; align-items: center; }}
  .badge {{
    font-size: 11px; color: var(--muted); padding: 3px 8px;
    background: #f4f4f6; border-radius: 4px; white-space: nowrap;
  }}
  .badge b {{ color: var(--fg); font-weight: 600; margin-left: 4px; }}
  .tpl-badge {{ background: #fff5ec; color: #b04a00; }}
  .tpl-badge b {{ color: #7a3300; }}
  .proc-toggle {{ font-size: 14px; color: var(--muted); transition: transform 0.2s; }}
  .process-card[open] .proc-toggle {{ transform: rotate(180deg); }}
  .process-card[open] > summary {{ border-bottom: 1px solid var(--line); }}

  .proc-content {{ padding: 20px; }}

  /* Template info row inside card */
  .tpl-info-row {{
    padding-bottom: 16px; margin-bottom: 16px; border-bottom: 1px solid var(--line-soft);
  }}
  .tpl-name {{ font-size: 16px; font-weight: 600; margin-top: 4px; }}
  .tpl-meta {{ display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: var(--fg-soft); margin-top: 6px; }}
  .cat-tag {{ background: #efefef; padding: 2px 8px; border-radius: 4px; color: #444; font-weight: 500; }}
  .orig-link {{ color: #2563eb; text-decoration: none; }}
  .orig-link:hover {{ text-decoration: underline; }}

  .proc-grid {{
    display: grid;
    grid-template-columns: 0.9fr 1.4fr 1.2fr 0.9fr;
    gap: 24px;
  }}
  .proc-col {{ display: flex; flex-direction: column; gap: 8px; min-width: 0; }}
  .proc-h {{
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--muted); font-weight: 600;
  }}
  .mode-options {{ display: flex; flex-direction: column; gap: 6px; }}
  .mode-opt {{
    display: flex; align-items: flex-start; gap: 8px;
    padding: 8px 10px; border: 1px solid var(--line); border-radius: 8px;
    cursor: pointer; transition: all 0.15s;
  }}
  .mode-opt:has(input:checked) {{ border-color: var(--accent); background: var(--accent-soft); }}
  .mode-opt input {{ margin-top: 3px; accent-color: var(--accent); }}
  .mode-opt > div:nth-child(2) {{ flex: 1; min-width: 0; }}
  .mode-name {{ font-size: 12px; font-weight: 600; color: var(--fg); }}
  .mode-name .best {{ display: inline-block; margin-left: 4px; padding: 1px 5px; font-size: 9px;
    color: var(--good); background: #e6fde8; border-radius: 4px; vertical-align: 1px; }}
  .mode-desc {{ font-size: 11px; color: var(--muted); margin-top: 1px; }}

  .input-card {{
    display: flex; gap: 10px; padding: 12px; background: var(--bg-alt);
    border: 1px dashed var(--line); border-radius: 8px;
  }}
  .input-card.pending {{ background: #fffaf3; border-color: #f3d4a7; }}
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

  .user-prompt {{
    width: 100%; min-height: 72px; padding: 10px 12px;
    border: 1px solid var(--line); border-radius: 8px; resize: vertical;
    font-family: inherit; font-size: 12px; color: var(--fg); background: #fafafa;
  }}
  .user-prompt::placeholder {{ color: var(--muted); font-style: italic; }}

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

  /* Sticky tabs */
  .tabs-bar {{
    position: sticky; top: 56px; z-index: 30;
    background: var(--bg-alt); padding: 4px 0 0;
  }}
  .tabs {{
    display: flex; gap: 0;
    background: #fff; border: 1px solid var(--line);
    border-radius: 12px; padding: 0 12px;
    overflow-x: auto;
  }}
  .tab {{
    padding: 12px 18px; background: transparent; border: none;
    border-bottom: 2px solid transparent; margin-bottom: -1px;
    font-family: inherit; font-size: 13px; color: #666; cursor: pointer;
    white-space: nowrap;
  }}
  .tab.active {{ color: var(--fg); border-bottom-color: var(--fg); font-weight: 600; }}
  .tab.disabled {{ opacity: 0.3; cursor: not-allowed; }}
  .tab:hover:not(.disabled):not(.active) {{ color: var(--fg); }}

  /* Split panes */
  .split {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
    margin-top: 16px;
    min-height: 70vh;
  }}
  .pane {{
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
    overflow: hidden; display: flex; flex-direction: column;
    max-height: 82vh;
  }}
  .pane-label {{
    padding: 10px 20px; background: #fafafa; border-bottom: 1px solid var(--line);
    font-size: 12px; color: #444; font-weight: 600; flex-shrink: 0;
  }}
  .pane-label .hint {{ color: var(--muted); font-weight: 400; margin-left: 8px; }}
  .pane-body {{
    overflow-y: auto; flex: 1;
    padding: 24px 28px;
    background: #fff;
    position: relative;   /* anchors offsetTop calculated against this */
  }}
  .pane-body img {{ max-width: 100%; display: block; margin: 0 auto; }}
  .pane-body iframe {{ max-width: 100%; display: block; margin: 16px auto; }}
  .pane-body .mall_prod_info {{ text-align: center; }}

  /* Cover block (separate from detail panels) */
  .cover-block {{
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px dashed var(--line);
  }}
  .cover-img {{
    width: 100%; max-width: 520px; aspect-ratio: 1/1;
    object-fit: contain; background: #fafafa;
    border-radius: 8px;
  }}

  /* Section dividers */
  .sec-divider {{
    display: flex; align-items: baseline; gap: 12px;
    margin: 18px 0 14px;
    line-height: normal;
  }}
  .sec-divider .sec-name {{
    font-size: 13px; font-weight: 700; color: var(--fg);
    padding: 4px 10px; background: var(--accent-soft);
    border-left: 3px solid var(--accent);
    border-radius: 0 4px 4px 0;
  }}
  .sec-divider .sec-range {{
    font-size: 10px; color: var(--muted); font-family: ui-monospace, monospace;
  }}
  .sec-divider-cover .sec-name {{
    background: #e8f4ff; border-left-color: #2563eb;
  }}

  /* swap pane greyed */
  .swap-body img:not(.cover-img) {{ opacity: 0.28; filter: grayscale(85%); }}
  .swap-body .cover-img {{ opacity: 0.32; filter: grayscale(85%); }}

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

// Scroll-within-pane using getBoundingClientRect (no page scroll)
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
    // Compute pane-internal scroll delta via boundingRect (immune to ancestor positioning)
    const bodyRect = body.getBoundingClientRect();
    const anchorRect = anchor.getBoundingClientRect();
    const delta = anchorRect.top - bodyRect.top;
    body.scrollTo({{ top: body.scrollTop + delta - 12, behavior: 'smooth' }});
  }});
}}

// Scroll sync between panes
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

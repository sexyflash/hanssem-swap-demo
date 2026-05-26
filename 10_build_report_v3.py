"""Report v3 — full revision.

변경:
- 외곽 패딩 + 내부 spacing
- 좌우 스크롤 동기화 (양방향)
- 탭(기본정보/사이즈/소재/옵션/모듈) 클릭 → 양쪽 동시 scroll to anchor
- 커버 위치: panel stack 첫 위치 (detail 안에 자연 포함)
- 이전 cover row 자리 → 공정 정보 카드 (R1/R2/R3 selector + 입력 fact + 시간)
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

SECTIONS = ["기본정보", "사이즈", "소재", "옵션", "모듈"]


def assign_sections(panel_count: int) -> dict:
    """Evenly distribute panels into 5 sections (rough first pass)."""
    n = panel_count
    if n == 0:
        return {}
    per = max(1, n // len(SECTIONS))
    result = {}
    idx = 1  # 1-based panel index
    for i, s in enumerate(SECTIONS):
        if idx > n:
            break
        if i == len(SECTIONS) - 1:
            # last section takes remaining
            end = n
        else:
            end = min(idx + per - 1, n)
        result[s] = list(range(idx, end + 1))
        idx = end + 1
    return result


def rewrite_detail_html(t: dict, side: str) -> tuple[str, dict]:
    """
    Return rewritten detail HTML with:
    - img src → local paths
    - panel imgs wrapped with anchor id (panel-{side}-{rank}-{idx})
    - section dividers inserted at section boundaries
    """
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    detail_path = TPL_ROOT / dir_name / "detail.html"
    meta_path = TPL_ROOT / dir_name / "meta.json"

    detail_html = (
        detail_path.read_text(encoding="utf-8", errors="ignore")
        if detail_path.exists()
        else ""
    )
    meta = json.loads(meta_path.read_text())
    # meta.json from 04_export uses "detail_imgs"; older crawl used "panel_count" naming
    detail_imgs = meta.get("detail_imgs", [])
    detail_img_count = meta.get("detail_img_count", len(detail_imgs)) or meta.get(
        "panel_count", len(detail_imgs)
    )
    panel_dir = TPL_ROOT / dir_name

    # build src→local map
    src_to_local = {}
    for i, src in enumerate(detail_imgs, 1):
        matches = list(panel_dir.glob(f"panel_{i:02d}.*"))
        if matches:
            local = f"../templates/{dir_name}/{matches[0].name}"
            src_to_local[src] = local
            # also map http↔https variants
            if src.startswith("https://"):
                src_to_local["http://" + src[8:]] = local
            elif src.startswith("http://"):
                src_to_local["https://" + src[7:]] = local

    # rewrite img tags: replace src + add data-panel-idx
    panel_idx = [0]  # mutable counter

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
        idx = panel_idx[0]
        new_src_attr = f'src="{local}" data-panel-idx="{idx}" loading="lazy"'
        # remove old src
        return re.sub(r'src=["\'][^"\']+["\']', new_src_attr, full)

    rewritten = re.sub(r"<img[^>]+>", repl_img, detail_html)

    # insert section anchor divs before specific panel indices
    sections = assign_sections(detail_img_count)
    # we need to find each img by data-panel-idx and inject anchor before it
    for sec_name, indices in sections.items():
        if not indices:
            continue
        first_idx = indices[0]
        anchor_id = f"sec-{side}-{rank}-{section_slug(sec_name)}"
        marker = f'<div class="sec-anchor" id="{anchor_id}" data-section="{sec_name}"></div>'
        # inject before first img of this section
        pattern = f'(<img[^>]*data-panel-idx="{first_idx}"[^>]*>)'
        rewritten = re.sub(pattern, marker + r"\1", rewritten, count=1)

    return rewritten, sections


def section_slug(name: str) -> str:
    return {
        "기본정보": "info",
        "사이즈": "size",
        "소재": "material",
        "옵션": "option",
        "모듈": "module",
    }.get(name, name)


def build_tabs(rank: int, sections: dict) -> str:
    """Tab buttons. Disabled if section has no panels."""
    btns = []
    for i, sec in enumerate(SECTIONS):
        slug = section_slug(sec)
        has = sec in sections and sections[sec]
        cls = "tab" + (" active" if i == 0 and has else "") + ("" if has else " disabled")
        attrs = (
            f'onclick="scrollToSection({rank}, \'{slug}\')"' if has else "disabled"
        )
        btns.append(f'<button class="{cls}" data-slug="{slug}" {attrs}>{sec}</button>')
    return "\n".join(btns)


def build_process_card(t: dict, fact: dict) -> str:
    """Process / input fact card (replaces old cover row)."""
    rank = t["rank"]
    desc = fact.get("description", "")
    cats = " / ".join([c for c in (fact.get("categories") or []) if c][-3:])
    keywords = ", ".join([k for k in (fact.get("searchKeywords") or []) if k][:8])
    price = fact.get("price", {})
    dc = price.get("dc")
    normal = price.get("normal")
    price_str = f"{dc:,}원 (정가 {normal:,}원)" if dc and normal else ""
    gif_panels = fact.get("gif_panels", [])
    text_count = len(fact.get("text_nodes_in_detail_html", []))

    return f"""
<section class="process-card">
  <div class="proc-grid">
    <div class="proc-col proc-mode">
      <div class="proc-h">공정 방식</div>
      <div class="mode-options">
        <label class="mode-opt"><input type="radio" name="mode-{rank}" value="R1" checked/>
          <div class="mode-name">R1 재생성</div>
          <div class="mode-desc">정합 프롬프트 + 재시도 시 재생성 (max 3회)</div>
        </label>
        <label class="mode-opt"><input type="radio" name="mode-{rank}" value="R2"/>
          <div class="mode-name">R2 덧그리기 <span class="best">★ best</span></div>
          <div class="mode-desc">정합 프롬프트 + 재시도 시 직전 결과 overpaint</div>
        </label>
        <label class="mode-opt"><input type="radio" name="mode-{rank}" value="R3"/>
          <div class="mode-name">R3 정합+시트</div>
          <div class="mode-desc">스마트시트 + 사전계산 정합 프롬프트</div>
        </label>
      </div>
    </div>
    <div class="proc-col proc-input">
      <div class="proc-h">입력 (사용자 제품)</div>
      <div class="input-card">
        <img class="input-thumb" src="../user_products/milo_777039/_thumbnail.jpg" alt="milo"/>
        <div class="input-meta">
          <div class="input-name">{fact['gdsNm']}</div>
          <div class="input-cat">{cats}</div>
          <div class="input-price">{price_str}</div>
        </div>
      </div>
      <div class="input-stats">
        <span>panel <b>{fact['panel_count']}장</b></span>
        <span>GIF(360°) <b>panel_{gif_panels[0]:02d}</b></span>
        <span>텍스트 노드 <b>{text_count}</b></span>
      </div>
    </div>
    <div class="proc-col proc-fact">
      <div class="proc-h">텍스트 fact (LLM 입력)</div>
      <div class="fact-desc">{desc}</div>
      <details>
        <summary>검색 키워드 ({len(fact.get('searchKeywords', []))})</summary>
        <div class="fact-keywords">{keywords}</div>
      </details>
    </div>
    <div class="proc-col proc-status">
      <div class="proc-h">처리 상태</div>
      <div class="status-line">처리 시간 <b>—</b></div>
      <div class="status-line">QA 점수 <b>—</b></div>
      <div class="status-line">시도 <b>—</b></div>
      <button class="run-btn" disabled>swap 실행 (대기)</button>
    </div>
  </div>
</section>
"""


def cover_url(t: dict) -> str:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    panel_dir = TPL_ROOT / dir_name
    thumbs = list(panel_dir.glob("_thumbnail.*"))
    if thumbs:
        return f"../templates/{dir_name}/{thumbs[0].name}"
    return ""


cover_imgs = {t["gdsNo"]: cover_url(t) for t in data["top6"]}


def chip(t: dict) -> str:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    cover = cover_imgs[gds]
    selected = "selected" if rank == 1 else ""
    name_short = t["name"][:24] + ("…" if len(t["name"]) > 24 else "")
    return f"""
<button class="chip {selected}" data-rank="{rank}" onclick="selectTpl({rank})">
  <span class="chip-rank">#{rank}</span>
  <img class="chip-cover" src="{cover}" alt="{cat}"/>
  <span class="chip-meta">
    <span class="chip-cat">{cat}</span>
    <span class="chip-name">{name_short}</span>
  </span>
</button>
"""


def view(t: dict) -> str:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    is_first = rank == 1

    orig_html, sections_orig = rewrite_detail_html(t, "orig")
    swap_html, _ = rewrite_detail_html(t, "swap")

    process_card = build_process_card(t, milo_fact)
    tabs = build_tabs(rank, sections_orig)

    return f"""
<div class="view {'active' if is_first else ''}" data-rank="{rank}">
  {process_card}

  <div class="header-row">
    <div class="hdr-left">
      <div class="hdr-tab">템플릿 정보</div>
      <h1>{t['name']}</h1>
      <div class="hdr-meta">
        <span class="cat-tag">{cat}</span>
        <span>{t.get('brand','')}</span>
        <span>★ {t.get('reviewCnt',0)} 리뷰</span>
        <span>{t.get('price'):,}원</span>
        <a href="{t['url']}" target="_blank" class="orig-link">원본 ↗</a>
      </div>
      <div class="tabs">
        {tabs}
      </div>
    </div>
  </div>

  <div class="split" data-rank="{rank}">
    <div class="pane orig-pane">
      <div class="pane-label">원본 ({t['detail_img_count']} panels)</div>
      <div class="pane-body" data-side="orig" data-rank="{rank}">{orig_html}</div>
    </div>
    <div class="pane swap-pane">
      <div class="pane-label">swap 결과
        <span class="hint">— 사용자 제품(밀로) × 이 템플릿 / 공정 R? · 대기 중</span>
      </div>
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
<title>가구 detail 템플릿 swap 미리보기 — v3</title>
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
    --pane-bg: #ffffff;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Pretendard", -apple-system, system-ui, sans-serif;
    background: var(--bg-alt);
    color: var(--fg);
    -webkit-font-smoothing: antialiased;
    font-size: 14px;
    line-height: 1.5;
  }}
  /* ================= Topbar ================= */
  .topbar {{
    position: sticky; top: 0; z-index: 50;
    background: #fff; border-bottom: 1px solid var(--line);
    padding: 12px 24px;
  }}
  .topbar-row {{
    display: flex; align-items: center; gap: 16px;
    max-width: 1600px; margin: 0 auto;
    overflow-x: auto;
  }}
  .topbar h1 {{
    margin: 0; font-size: 13px; font-weight: 600;
    color: var(--fg-soft); white-space: nowrap;
    letter-spacing: -0.01em;
  }}
  .chips {{ display: flex; gap: 8px; flex: 1; }}
  .chip {{
    display: flex; align-items: center; gap: 8px;
    padding: 6px 14px 6px 6px; border: 1px solid var(--line); background: #fff;
    border-radius: 999px; cursor: pointer; transition: all 0.15s;
    font-family: inherit; font-size: 12px; color: #555;
    white-space: nowrap;
  }}
  .chip:hover {{ border-color: #999; }}
  .chip.selected {{
    border-color: var(--fg); background: var(--fg); color: #fff;
  }}
  .chip-cover {{ width: 28px; height: 28px; border-radius: 50%; object-fit: cover; background: #f3f3f3; }}
  .chip-rank {{ font-weight: 700; color: var(--accent); }}
  .chip-meta {{ display: flex; flex-direction: column; align-items: flex-start; line-height: 1.15; }}
  .chip-cat {{ font-size: 10px; opacity: 0.7; }}
  .chip-name {{ font-size: 11px; }}

  /* ================= View ================= */
  .view {{ display: none; padding: 24px; max-width: 1600px; margin: 0 auto; }}
  .view.active {{ display: block; }}

  /* ================= Process card ================= */
  .process-card {{
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
    padding: 20px; margin-bottom: 20px;
  }}
  .proc-grid {{
    display: grid;
    grid-template-columns: 1.1fr 1.2fr 1.4fr 0.9fr;
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
  .mode-opt > div:nth-child(2) {{ flex: 1; }}
  .mode-name {{ font-size: 12px; font-weight: 600; color: var(--fg); }}
  .mode-name .best {{ display: inline-block; margin-left: 4px; padding: 1px 5px; font-size: 9px;
    color: var(--good); background: #e6fde8; border-radius: 4px; vertical-align: 1px; }}
  .mode-desc {{ font-size: 11px; color: var(--muted); margin-top: 1px; }}

  .input-card {{
    display: flex; gap: 10px; padding: 10px; background: var(--bg-alt);
    border: 1px solid var(--line-soft); border-radius: 8px;
  }}
  .input-thumb {{ width: 56px; height: 56px; border-radius: 6px; object-fit: cover; background: #fff; }}
  .input-meta {{ flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }}
  .input-name {{ font-size: 12px; font-weight: 600; line-height: 1.3; }}
  .input-cat {{ font-size: 11px; color: var(--muted); }}
  .input-price {{ font-size: 12px; color: var(--accent); font-weight: 600; margin-top: 2px; }}
  .input-stats {{
    display: flex; flex-wrap: wrap; gap: 4px 12px; font-size: 11px; color: var(--muted);
    margin-top: 4px;
  }}
  .input-stats b {{ color: var(--fg); font-weight: 600; }}

  .fact-desc {{ font-size: 12px; color: var(--fg); line-height: 1.55; }}
  details summary {{ cursor: pointer; font-size: 11px; color: var(--muted); margin-top: 4px; }}
  .fact-keywords {{ font-size: 11px; color: var(--fg-soft); padding: 6px 0; line-height: 1.6; }}

  .status-line {{ font-size: 12px; color: var(--muted); }}
  .status-line b {{ color: var(--fg); font-weight: 600; margin-left: 4px; }}
  .run-btn {{
    margin-top: auto; padding: 10px;
    background: var(--accent); color: #fff; border: none; border-radius: 8px;
    font-family: inherit; font-size: 13px; font-weight: 600; cursor: pointer;
    opacity: 0.5;
  }}
  .run-btn:disabled {{ cursor: not-allowed; }}

  /* ================= Header / tabs ================= */
  .header-row {{
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
    padding: 16px 20px; margin-bottom: 16px;
  }}
  .hdr-tab {{ font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }}
  .header-row h1 {{ margin: 4px 0 6px; font-size: 18px; font-weight: 600; }}
  .hdr-meta {{ display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: var(--fg-soft); margin-bottom: 14px; }}
  .cat-tag {{ background: #efefef; padding: 2px 8px; border-radius: 4px; color: #444; font-weight: 500; }}
  .orig-link {{ color: #2563eb; text-decoration: none; }}
  .orig-link:hover {{ text-decoration: underline; }}

  .tabs {{
    display: flex; gap: 0; border-bottom: 1px solid var(--line);
    margin: 0 -20px; padding: 0 20px;
  }}
  .tab {{
    padding: 10px 16px; background: transparent; border: none;
    border-bottom: 2px solid transparent;
    font-family: inherit; font-size: 13px; color: #666; cursor: pointer;
  }}
  .tab.active {{ color: var(--fg); border-bottom-color: var(--fg); font-weight: 600; }}
  .tab.disabled {{ opacity: 0.3; cursor: not-allowed; }}
  .tab:hover:not(.disabled):not(.active) {{ color: var(--fg); }}

  /* ================= Split ================= */
  .split {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
    min-height: calc(100vh - 100px);
  }}
  .pane {{
    background: var(--pane-bg);
    border: 1px solid var(--line); border-radius: 12px;
    overflow: hidden;
    display: flex; flex-direction: column;
    max-height: 85vh;
  }}
  .pane-label {{
    padding: 10px 16px; background: #fafafa; border-bottom: 1px solid var(--line);
    font-size: 12px; color: #444; font-weight: 600;
    flex-shrink: 0;
  }}
  .pane-label .hint {{ color: var(--muted); font-weight: 400; margin-left: 8px; }}
  .pane-body {{
    overflow-y: auto; flex: 1;
    background: #fff;
  }}
  .pane-body img {{ max-width: 100%; display: block; margin: 0 auto; }}
  .pane-body iframe {{ max-width: 100%; display: block; margin: 16px auto; }}
  .pane-body .mall_prod_info {{ text-align: center; }}

  .sec-anchor {{
    display: block; scroll-margin-top: 16px;
    height: 1px; padding: 0; margin: 0;
  }}

  /* swap pane: keep imgs visible but greyed for placeholder phase */
  .swap-body {{ position: relative; }}
  .swap-body::before {{
    content: "SWAP PLACEHOLDER · 사용자 제품으로 swap된 결과가 여기 표시됩니다";
    position: sticky; top: 0; display: block;
    background: rgba(255, 122, 0, 0.08);
    color: var(--accent); font-size: 11px; font-weight: 600;
    text-align: center; padding: 8px;
    border-bottom: 1px dashed rgba(255, 122, 0, 0.4);
    z-index: 1;
  }}
  .swap-body img {{ opacity: 0.32; filter: grayscale(80%); }}

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

// === Tab anchor scroll (both panes simultaneously) ===
function scrollToSection(rank, slug) {{
  const view = document.querySelector(`.view[data-rank="${{rank}}"]`);
  if (!view) return;
  // mark active tab
  view.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.slug === slug));
  // scroll both panes
  ['orig', 'swap'].forEach(side => {{
    const body = view.querySelector(`.pane-body[data-side="${{side}}"][data-rank="${{rank}}"]`);
    if (!body) return;
    const anchor = body.querySelector(`#sec-${{side}}-${{rank}}-${{slug}}`);
    if (anchor) {{
      // scroll within pane (not page)
      const top = anchor.offsetTop;
      body.scrollTo({{ top: top - 16, behavior: 'smooth' }});
    }}
  }});
}}

// === Scroll sync between panes ===
let syncing = false;
function setupSyncForView(rank) {{
  const view = document.querySelector(`.view[data-rank="${{rank}}"]`);
  if (!view) return;
  const orig = view.querySelector(`.pane-body[data-side="orig"]`);
  const swap = view.querySelector(`.pane-body[data-side="swap"]`);
  if (!orig || !swap) return;
  function makeSync(src, dst) {{
    src.addEventListener('scroll', () => {{
      if (syncing) return;
      syncing = true;
      // sync by ratio so unequal heights still align proportionally
      const srcMax = src.scrollHeight - src.clientHeight;
      const dstMax = dst.scrollHeight - dst.clientHeight;
      const ratio = srcMax > 0 ? src.scrollTop / srcMax : 0;
      dst.scrollTop = ratio * dstMax;
      requestAnimationFrame(() => {{ syncing = false; }});
    }});
  }}
  makeSync(orig, swap);
  makeSync(swap, orig);
}}
document.addEventListener('DOMContentLoaded', () => {{
  for (let r = 1; r <= 6; r++) setupSyncForView(r);
}});
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT}")
print(f"size: {OUT.stat().st_size // 1024}KB")

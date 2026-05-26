"""Report v2 — selector 기반 1-at-a-time 좌우 split view.

- 상단 sticky bar: 6 템플릿 chips selector
- 본문: 좌측 detail HTML inline + 한샘 톤 헤더/탭 mimic, 우측 swap placeholder
- 라이트 톤
- UI 워딩에 '한샘' 워딩 빼고 '원본/swap'
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
TPL_ROOT = HERE / "templates"
OUT = HERE / "report" / "index.html"
OUT.parent.mkdir(exist_ok=True)

data = json.loads((HERE / "top6_template_urls.json").read_text())


def cover_url(t: dict) -> str:
    """Use thumbnail as cover (white-bg product shot)."""
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    panel_dir = TPL_ROOT / dir_name
    thumbs = list(panel_dir.glob("_thumbnail.*"))
    if thumbs:
        return f"../templates/{dir_name}/{thumbs[0].name}"
    return ""


def build_pane(t: dict, side: str) -> str:
    """Build either 'orig' or 'swap' pane content."""
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    detail_path = TPL_ROOT / dir_name / "detail.html"
    detail_html = (
        detail_path.read_text(encoding="utf-8", errors="ignore")
        if detail_path.exists()
        else "<p>(no detail)</p>"
    )

    # rewrite image src to local panel paths so dead URLs (devimage etc) work
    meta_path = TPL_ROOT / dir_name / "meta.json"
    meta = json.loads(meta_path.read_text())
    src_to_local = {}
    for i, src in enumerate(meta["detail_imgs"], 1):
        # find the actual saved file
        panel_dir = TPL_ROOT / dir_name
        matches = list(panel_dir.glob(f"panel_{i:02d}.*"))
        if matches:
            src_to_local[src] = f"../templates/{dir_name}/{matches[0].name}"
            # also map normalized version (http→https swap was done in crawl)
            if src.startswith("https://"):
                src_to_local["http://" + src[8:]] = src_to_local[src]
            elif src.startswith("http://"):
                src_to_local["https://" + src[7:]] = src_to_local[src]

    # also rewrite devimage.hanssem → image.hanssem (mirror)
    rewritten = detail_html
    for src, local in src_to_local.items():
        rewritten = rewritten.replace(f'src="{src}"', f'src="{local}"')
        rewritten = rewritten.replace(f"src='{src}'", f"src='{local}'")

    # global devimage→image swap (in case some weren't in mapping)
    rewritten = rewritten.replace("devimage.hanssem.com", "image.hanssem.com")

    # if swap pane, replace each img src with a placeholder marker
    if side == "swap":
        # for now: keep same imgs but greyscale + watermark
        watermark_class = ' class="swap-placeholder"'
        rewritten = rewritten.replace("<img ", f"<img{watermark_class} data-side='swap' ")

    return rewritten


cover_imgs = {t["gdsNo"]: cover_url(t) for t in data["top6"]}


def chip(t: dict) -> str:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    cover = cover_imgs[gds]
    selected = "selected" if rank == 1 else ""
    return f"""
<button class="chip {selected}" data-rank="{rank}" onclick="selectTpl({rank})">
  <span class="chip-rank">#{rank}</span>
  <img class="chip-cover" src="{cover}" alt="{cat}"/>
  <span class="chip-meta">
    <span class="chip-cat">{cat}</span>
    <span class="chip-name">{t['name'][:30]}{'…' if len(t['name'])>30 else ''}</span>
  </span>
</button>
"""


def view(t: dict) -> str:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    cover = cover_imgs[gds]
    price = t.get("price")
    price_str = f"{price:,}원" if price else ""
    reviews = t.get("reviewCnt", 0)
    brand = t.get("brand", "")
    orig_html = build_pane(t, "orig")
    swap_html = build_pane(t, "swap")
    is_first = rank == 1
    return f"""
<div class="view {'active' if is_first else ''}" data-rank="{rank}">
  <div class="cover-row">
    <div class="cover-cell">
      <div class="lbl">커버 (대표 화이트백)</div>
      <img class="cover" src="{cover}" alt="cover"/>
    </div>
    <div class="cover-info">
      <div class="brand">{brand}</div>
      <h1>{t['name']}</h1>
      <div class="price">{price_str}</div>
      <div class="rating">★ {reviews}건 리뷰</div>
      <div class="tabs">
        <button class="tab active">기본정보</button>
        <button class="tab">사이즈</button>
        <button class="tab">소재</button>
        <button class="tab">옵션</button>
        <button class="tab">모듈</button>
      </div>
    </div>
  </div>
  <div class="split">
    <div class="pane orig-pane">
      <div class="pane-label">원본 ({t['detail_img_count']} panels)</div>
      <div class="pane-body">{orig_html}</div>
    </div>
    <div class="pane swap-pane">
      <div class="pane-label">swap 결과 <span class="hint">(아직 비어있음 — Phase 3에서 채움)</span></div>
      <div class="pane-body swap-body">{swap_html}</div>
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
<title>가구 detail 템플릿 swap 미리보기</title>
<link rel="stylesheet" href="https://res.remodeling.hanssem.com/font/pretendard/pretendard.css"/>
<style>
  :root {{
    --bg: #ffffff;
    --bg-alt: #f7f7f8;
    --fg: #1a1a1a;
    --muted: #888;
    --line: #e5e5e5;
    --accent: #ff7a00;
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
  }}
  /* === Top bar / chips === */
  .topbar {{
    position: sticky; top: 0; z-index: 50;
    background: #fff; border-bottom: 1px solid var(--line);
    padding: 12px 20px;
  }}
  .topbar-row {{
    display: flex; align-items: center; gap: 16px;
    overflow-x: auto;
  }}
  .topbar h1 {{
    margin: 0; font-size: 14px; font-weight: 600; white-space: nowrap;
    color: #444;
  }}
  .chips {{
    display: flex; gap: 8px; flex: 1;
  }}
  .chip {{
    display: flex; align-items: center; gap: 8px;
    padding: 6px 12px 6px 6px; border: 1px solid var(--line); background: #fff;
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
  .chip.selected .chip-rank {{ color: var(--accent); }}
  .chip-meta {{ display: flex; flex-direction: column; align-items: flex-start; line-height: 1.2; }}
  .chip-cat {{ font-size: 10px; opacity: 0.7; }}
  .chip-name {{ font-size: 11px; }}

  /* === View (one per template) === */
  .view {{ display: none; }}
  .view.active {{ display: block; }}

  .cover-row {{
    display: grid; grid-template-columns: 280px 1fr; gap: 24px;
    padding: 24px 20px; background: #fff; border-bottom: 1px solid var(--line);
  }}
  .cover-cell {{ position: relative; }}
  .lbl {{
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;
    color: var(--muted); margin-bottom: 6px;
  }}
  .cover {{
    width: 100%; aspect-ratio: 1/1; object-fit: contain;
    background: #fff; border: 1px solid var(--line); border-radius: 8px;
  }}
  .cover-info {{ display: flex; flex-direction: column; justify-content: flex-end; gap: 8px; }}
  .cover-info .brand {{ color: var(--muted); font-size: 12px; }}
  .cover-info h1 {{ margin: 0; font-size: 22px; font-weight: 600; line-height: 1.3; }}
  .cover-info .price {{ font-size: 22px; font-weight: 700; color: var(--accent); }}
  .cover-info .rating {{ font-size: 12px; color: #555; }}
  .tabs {{ display: flex; gap: 0; margin-top: 16px; border-bottom: 1px solid var(--line); }}
  .tab {{
    padding: 10px 16px; background: transparent; border: none;
    border-bottom: 2px solid transparent;
    font-family: inherit; font-size: 13px; color: #666; cursor: pointer;
  }}
  .tab.active {{ color: var(--fg); border-bottom-color: var(--fg); font-weight: 600; }}

  /* === Split panes === */
  .split {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 0;
    min-height: calc(100vh - 320px);
  }}
  .pane {{
    background: var(--pane-bg); border-right: 1px solid var(--line);
    display: flex; flex-direction: column;
    max-height: calc(100vh - 90px);
  }}
  .pane:last-child {{ border-right: none; }}
  .pane-label {{
    padding: 10px 20px; background: #fafafa; border-bottom: 1px solid var(--line);
    font-size: 12px; color: #444; font-weight: 600;
    position: sticky; top: 0; z-index: 2;
  }}
  .pane-label .hint {{ color: var(--muted); font-weight: 400; margin-left: 8px; }}
  .pane-body {{
    overflow-y: auto; flex: 1;
  }}
  /* honor detail.html original markup — center, line-height 0 etc. */
  .pane-body img {{ max-width: 100%; display: block; margin: 0 auto; }}
  .pane-body iframe {{ max-width: 100%; display: block; margin: 16px auto; }}
  .pane-body .mall_prod_info {{ text-align: center; }}

  /* swap-side: greyscale + watermark to indicate placeholder */
  .swap-body {{ position: relative; }}
  .swap-body::before {{
    content: "SWAP PLACEHOLDER";
    position: sticky; top: 0; display: block;
    background: rgba(255, 122, 0, 0.08);
    color: var(--accent); font-size: 11px; font-weight: 700;
    text-align: center; padding: 8px;
    border-bottom: 1px dashed var(--accent);
    z-index: 1;
  }}
  .swap-body img.swap-placeholder {{ opacity: 0.35; filter: grayscale(80%); }}

  /* scrollbar */
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
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT}")
print(f"size: {OUT.stat().st_size // 1024}KB")

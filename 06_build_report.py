"""6 템플릿 stack preview HTML 빌드.

레이아웃:
- 6개 카드 (가로 grid, 큰 화면) 또는 vertical stack (좁은 화면)
- 각 카드:
  - 헤더: 카테고리/제품명/리뷰/한샘링크
  - 좌측 column: 원본 detail panels (vertical stack, scroll)
  - 우측 column: swap result placeholder (추후 채움)
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
TPL_ROOT = HERE / "templates"
OUT = HERE / "report" / "index.html"
OUT.parent.mkdir(exist_ok=True)

data = json.loads((HERE / "top6_template_urls.json").read_text())


def card(t: dict) -> str:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    name = t["name"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    panel_dir = TPL_ROOT / dir_name
    panels = sorted([p for p in panel_dir.glob("panel_*.*")])

    # use relative paths from report/index.html
    rel_panels = [f"../templates/{dir_name}/{p.name}" for p in panels]
    thumb_files = list(panel_dir.glob("_thumbnail.*"))
    rel_thumb = (
        f"../templates/{dir_name}/{thumb_files[0].name}" if thumb_files else ""
    )

    panel_imgs = "\n".join(
        f'<img loading="lazy" src="{p}" alt="panel_{i+1}">'
        for i, p in enumerate(rel_panels)
    )

    return f"""
<section class="card" data-rank="{rank}">
  <header>
    <div class="meta">
      <span class="rank">#{rank}</span>
      <span class="cat">{cat}</span>
      <span class="gds">gdsNo: <a href="{t['url']}" target="_blank">{gds}↗</a></span>
      <span class="reviews">★ {t.get('reviewCnt',0)}</span>
      <span class="count">{t['detail_img_count']} panels</span>
    </div>
    <h2>{name}</h2>
  </header>
  <div class="split">
    <div class="orig">
      <div class="label">원본 한샘 detail</div>
      <div class="stack">{panel_imgs}</div>
    </div>
    <div class="swap">
      <div class="label">swap 결과 (placeholder)</div>
      <div class="placeholder">
        <p>사용자 제품 이미지 5장 + 가격/카피 입력 시<br/>이 자리에 AI swap 결과가 들어감.</p>
        <p class="hint">Phase 3: 각 panel별 의도 분석 → 프롬프트 → nano-banana/recraft swap</p>
      </div>
    </div>
  </div>
</section>
"""


cards_html = "\n".join(card(t) for t in data["top6"])

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>한샘 detail 템플릿 6 — swap preview</title>
<style>
  :root {{
    --bg: #0e0e10;
    --fg: #ececec;
    --muted: #888;
    --card: #1a1a1d;
    --border: #2a2a2f;
    --accent: #ffd166;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, "Pretendard", "Noto Sans KR", system-ui, sans-serif;
    background: var(--bg); color: var(--fg);
    -webkit-font-smoothing: antialiased;
  }}
  .top {{
    padding: 24px 32px;
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; background: var(--bg); z-index: 10;
  }}
  .top h1 {{ margin: 0 0 4px; font-size: 18px; font-weight: 600; }}
  .top p {{ margin: 0; color: var(--muted); font-size: 13px; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(560px, 1fr));
    gap: 16px;
    padding: 16px;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    display: flex; flex-direction: column;
  }}
  .card header {{ padding: 14px 16px; border-bottom: 1px solid var(--border); }}
  .meta {{ display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: var(--muted); margin-bottom: 6px; }}
  .meta .rank {{ color: var(--accent); font-weight: 700; }}
  .meta .cat {{ background: #2a2a2f; padding: 2px 8px; border-radius: 4px; color: #eee; }}
  .meta a {{ color: #6cb6ff; text-decoration: none; }}
  .meta a:hover {{ text-decoration: underline; }}
  .card h2 {{ margin: 0; font-size: 14px; font-weight: 500; line-height: 1.4; }}
  .split {{ display: grid; grid-template-columns: 1fr 1fr; min-height: 600px; max-height: 80vh; }}
  .orig, .swap {{ display: flex; flex-direction: column; border-right: 1px solid var(--border); }}
  .swap {{ border-right: none; }}
  .label {{
    padding: 8px 12px; background: #111; border-bottom: 1px solid var(--border);
    font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em;
    position: sticky; top: 0; z-index: 2;
  }}
  .stack {{ overflow-y: auto; flex: 1; padding: 0; background: #fff; }}
  .stack img {{ width: 100%; display: block; }}
  .placeholder {{
    padding: 24px; color: var(--muted); font-size: 13px; text-align: center;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    flex: 1;
    background: #111;
  }}
  .placeholder .hint {{ margin-top: 16px; font-size: 11px; opacity: 0.7; }}
  /* scrollbar styling */
  .stack::-webkit-scrollbar {{ width: 6px; }}
  .stack::-webkit-scrollbar-thumb {{ background: #444; border-radius: 3px; }}
</style>
</head>
<body>
<div class="top">
  <h1>한샘 detail 템플릿 6 — swap preview</h1>
  <p>좌: 원본 한샘 상세페이지 그대로. 우: 사용자 제품 swap 결과 자리 (Phase 3에서 채움).</p>
</div>
<main class="grid">
{cards_html}
</main>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT}")
print(f"size: {OUT.stat().st_size // 1024}KB")

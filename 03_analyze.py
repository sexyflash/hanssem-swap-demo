"""hanssem_pattern.json 분석 → Top 6 템플릿 후보 선정 + 리포트."""

import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
data = json.loads((HERE / "hanssem_pattern.json").read_text())
products = data["products"]

# panel count distribution
counts = [p["detail_img_count"] for p in products]
cc = Counter()
for c in counts:
    if c <= 5:
        cc["1-5"] += 1
    elif c <= 10:
        cc["6-10"] += 1
    elif c <= 15:
        cc["11-15"] += 1
    elif c <= 25:
        cc["16-25"] += 1
    else:
        cc["26+"] += 1

# avg sampled dimensions
print("=== Panel Count Distribution ===")
for bucket, n in sorted(cc.items()):
    print(f"  {bucket:>6}: {n} products  {'█' * n}")

print(f"\n=== Per-product Detail ===")
print(f"{'cat':10} {'gdsNo':>8} {'imgs':>5} {'avgH':>6} {'maxH':>6}  name")
for p in sorted(products, key=lambda x: (x["category"], -x["detail_img_count"])):
    dims = p.get("sampled_dims", [])
    avgh = sum(d["h"] for d in dims) // len(dims) if dims else 0
    maxh = max((d["h"] for d in dims), default=0)
    print(
        f"  {p['category']:8} {p['gdsNo']:>8} {p['detail_img_count']:>5} {avgh:>6} {maxh:>6}  {p['gdsNm'][:35]}"
    )

# select top 6 candidates: diversity by category + panel count buckets
print("\n=== Top 6 Template Candidates ===")
# strategy: pick 2 per category, one with "medium" panel count (8-15), one with "rich" (16-25)
# prefer high reviewCnt for polish
by_cat = defaultdict(list)
for p in products:
    by_cat[p["category"]].append(p)

def is_real(p):
    """Filter out products where all sampled imgs are 1x1 placeholder."""
    dims = p.get("sampled_dims", [])
    if not dims:
        return True  # don't filter if we have no dim data
    return any(d["h"] > 100 for d in dims)


candidates = []
for cat, items in by_cat.items():
    items = [p for p in items if is_real(p)]
    med = [p for p in items if 8 <= p["detail_img_count"] <= 15]
    rich = [p for p in items if 16 <= p["detail_img_count"] <= 25]
    xrich = [p for p in items if p["detail_img_count"] >= 26]
    med.sort(key=lambda x: -x.get("reviewCnt", 0))
    rich.sort(key=lambda x: -x.get("reviewCnt", 0))
    xrich.sort(key=lambda x: -x.get("reviewCnt", 0))
    if med:
        candidates.append(("medium(8-15)", med[0]))
    if rich:
        candidates.append(("rich(16-25)", rich[0]))
    # extra: prefer xrich if exists
    if xrich:
        candidates.append(("xrich(26+)", xrich[0]))

# Dedupe and trim — prefer covering all 3 categories first
seen_cat = set()
prioritized = []
for kind, p in candidates:
    if p["category"] not in seen_cat:
        prioritized.append((kind, p))
        seen_cat.add(p["category"])
# then add the rest
for kind, p in candidates:
    if (kind, p) not in prioritized:
        prioritized.append((kind, p))
candidates = prioritized[:6]
for i, (kind, p) in enumerate(candidates, 1):
    print(
        f"  #{i} [{kind}] {p['category']:8} gdsNo={p['gdsNo']} imgs={p['detail_img_count']:>3} reviews={p.get('reviewCnt',0):>4}  {p['gdsNm'][:40]}"
    )
    print(f"      URL: {p['url']}")
    print(f"      Thumb: {p.get('thumbnail','')[:100]}")

# write report.md
report_lines = [
    "# 한샘 detail page 패턴 리서치 결과",
    "",
    f"- 총 제품: {data['summary']['total_products']}개 (sofa/wardrobe/desk × 10)",
    f"- 패턴 분포: 30/30 모두 `split_panels` (한샘은 long-strip 없음, 일관된 panel 구조)",
    "",
    "## Panel Count 분포",
    "",
    "| 패널 개수 | 제품 수 |",
    "|---:|---:|",
]
for bucket in ["1-5", "6-10", "11-15", "16-25", "26+"]:
    report_lines.append(f"| {bucket} | {cc.get(bucket, 0)} |")

report_lines += [
    "",
    "## Top 6 템플릿 후보",
    "",
    "다양성 확보: 카테고리별 medium(8-15장) + rich(16-25장) 페어. 리뷰수 높은 거 우선.",
    "",
    "| # | type | category | gdsNo | imgs | reviews | name | URL |",
    "|---:|:---|:---|---:|---:|---:|:---|:---|",
]
for i, (kind, p) in enumerate(candidates, 1):
    report_lines.append(
        f"| {i} | {kind} | {p['category']} | {p['gdsNo']} | {p['detail_img_count']} | {p.get('reviewCnt',0)} | {p['gdsNm']} | [link]({p['url']}) |"
    )

report_lines += [
    "",
    "## 다음 단계 (사용자 작업)",
    "",
    "1. 위 6개 URL 가서 detail 영역 이미지 다운로드",
    "   - 한샘 모두 split_panels이므로 **각 이미지가 이미 분리되어 있음 → 그대로 다운로드 OK** (토막낼 필요 ✗)",
    "   - 이미지 URL은 `hanssem_pattern.json`의 `detail_imgs` 배열에 다 있음",
    "2. 시안+프롬프트 페어 만들기 (각 템플릿별)",
    "3. Report HTML 빌드 (좌 원본 / 우 swap 결과 6장)",
    "",
    "## 부가 발견",
    "",
    "- 한샘 detail HTML은 `__NEXT_DATA__.props.pageProps.initialState.goodsDetail.storedGoods.{gdsNo}.detailInfo.goodsDetailInfo.goodsDetailHtml` 안에 raw HTML 문자열로 들어있음",
    "- 이미지는 `image.hanssem.com` 또는 `image2.hanssem.com`에서 직접 호스팅 (CDN)",
    "- panel 개수가 4~37장으로 다양함 → 템플릿 풀로 쓰기 좋음",
]

(HERE / "hanssem_research_report.md").write_text("\n".join(report_lines), encoding="utf-8")
print(f"\nwrote {HERE / 'hanssem_research_report.md'}")

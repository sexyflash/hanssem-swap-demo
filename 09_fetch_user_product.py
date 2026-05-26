"""사용자 제품(밀로 패브릭 소파 777039) 데이터 + fact 정보 수집.

- 페이지 fetch → detail HTML + 메타 + 갤러리 이미지
- detail panels 다운로드 (templates/user_milo_777039/)
- 360 GIF 식별 (확장자 .gif인 것)
- fact JSON (제품명, description, keywords, categories, price)
"""

import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HERE = Path(__file__).parent
OUT = HERE / "user_products" / "milo_777039"
OUT.mkdir(parents=True, exist_ok=True)

NEXT_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL
)
GDS_NO = 777039
client = httpx.Client(headers={"User-Agent": UA}, timeout=20.0)

# 1. fetch product page
r = client.get(f"https://store.hanssem.com/goods/{GDS_NO}")
r.raise_for_status()
m = NEXT_RE.search(r.text)
nd = json.loads(m.group(1))
pp = nd["props"]["pageProps"]
di = pp["defaultInfo"]
stored = pp["initialState"]["goodsDetail"]["storedGoods"][str(GDS_NO)]
gds_info = stored["apiResponse"]["data"]["goods"]
detail_html = stored["detailInfo"]["goodsDetailInfo"]["goodsDetailHtml"]

# 2. extract image URLs from detail_html
img_urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', detail_html)
img_urls = [
    ("https://" + u[8:]) if u.startswith("http://") else u for u in img_urls
]
img_urls = [u.replace("devimage.hanssem.com", "image.hanssem.com") for u in img_urls]

# 3. download each panel
print(f"[milo {GDS_NO}] detail_html: {len(detail_html)//1024}KB | panels: {len(img_urls)}")
gif_panels = []
for i, u in enumerate(img_urls, 1):
    ext = urlparse(u).path.split(".")[-1].split("?")[0].lower() or "jpg"
    if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
        ext = "jpg"
    dest = OUT / f"panel_{i:02d}.{ext}"
    if dest.exists() and dest.stat().st_size > 1024:
        size_kb = dest.stat().st_size // 1024
    else:
        try:
            rr = client.get(u)
            rr.raise_for_status()
            dest.write_bytes(rr.content)
            size_kb = len(rr.content) // 1024
        except Exception as e:
            print(f"  panel_{i:02d} FAIL: {e}")
            continue
    is_gif = ext == "gif"
    if is_gif:
        gif_panels.append(i)
    print(f"  panel_{i:02d}.{ext} {size_kb}KB{' [GIF]' if is_gif else ''}")
    time.sleep(0.15)

# 4. download thumbnail
thumb_url = None
for im in di.get("images", []):
    if im.get("imageUrl"):
        thumb_url = im["imageUrl"]
        break
if not thumb_url:
    thumb_url = di.get("imageUrl") or stored.get("imageUrl")

# also try gallery from pageProps directly
# Fallback: use the very first detail panel? No, use product gallery
# Actually for product gallery, check apiResponse
ar = stored.get("apiResponse", {})
gallery_url = None
# Just use the canonical thumbnail pattern
thumb_url = f"https://image.hanssem.com/hsimg/gds/1050/{GDS_NO//1000}/{GDS_NO}_A1.jpg"
try:
    rr = client.get(thumb_url)
    if rr.status_code == 200:
        (OUT / "_thumbnail.jpg").write_bytes(rr.content)
        print(f"  thumbnail OK {len(rr.content)//1024}KB")
except Exception as e:
    print(f"  thumbnail FAIL: {e}")

# 5. save detail HTML
(OUT / "detail.html").write_text(detail_html, encoding="utf-8")

# 6. extract text nodes from detail HTML (fact source)
from bs4 import BeautifulSoup
soup = BeautifulSoup(detail_html, "lxml")
text_nodes = []
for el in soup.find_all(text=True):
    t = el.strip()
    if t and not t.startswith("<!--") and len(t) > 2:
        text_nodes.append(t)

# 7. compose fact JSON (LLM input ready)
fact = {
    "gdsNo": GDS_NO,
    "gdsNm": di["gdsNm"],
    "brand": di.get("brandNm"),
    "categories": [c.get("ctgrNm") for c in di.get("categories", [])],
    "price": {
        "normal": gds_info.get("normalSalePrc"),
        "dc": gds_info.get("dcPrc"),
        "dcRate": gds_info.get("dcRate"),
    },
    "description": stored["metaInfo"].get("description"),
    "searchKeywords": (stored["metaInfo"].get("srchKeyWd") or "").split("$$"),
    "panel_count": len(img_urls),
    "gif_panels": gif_panels,
    "detail_imgs": img_urls,
    "thumbnail_url": thumb_url,
    "text_nodes_in_detail_html": text_nodes,
    "review_summary": stored.get("goodsEvaluationQualityNotifyInfo", {}),
}
(OUT / "fact.json").write_text(
    json.dumps(fact, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"\nfact.json written")
print(f"  gdsNm: {fact['gdsNm']}")
print(f"  price: {fact['price']['dc']:,}원 (정가 {fact['price']['normal']:,}원)")
print(f"  description: {fact['description'][:80] if fact['description'] else 'N/A'}...")
print(f"  GIF panels: {gif_panels}")
print(f"  text nodes in detail: {len(text_nodes)}")

"""Top 6 각 제품의 detail HTML raw 가져와서 templates/{}/detail.html 저장.

또한 상단 헤더에 보여줄 메타(제품명/가격/평점) + thumbnail URL도 함께.
"""

import json
import re
import time
from pathlib import Path

import httpx

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HERE = Path(__file__).parent
TPL_ROOT = HERE / "templates"
NEXT_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL
)

data = json.loads((HERE / "top6_template_urls.json").read_text())
client = httpx.Client(headers={"User-Agent": UA}, timeout=20.0)


def fetch_one(gds_no: int) -> dict:
    r = client.get(f"https://store.hanssem.com/goods/{gds_no}")
    r.raise_for_status()
    m = NEXT_RE.search(r.text)
    if not m:
        return {"detail_html": "", "evaluation": None}
    nd = json.loads(m.group(1))
    pp = nd["props"]["pageProps"]
    di = pp["defaultInfo"]
    stored = pp["initialState"]["goodsDetail"]["storedGoods"][str(gds_no)]
    return {
        "gdsNm": di["gdsNm"],
        "brandNm": di.get("brandNm"),
        "images": [im.get("imageUrl") for im in di.get("images", []) if im.get("imageUrl")],
        "categories": [c.get("ctgrNm") for c in di.get("categories", [])],
        "evaluation": di.get("goodsEvaluationQualityNotifyInfo"),
        "detail_html": stored["detailInfo"]["goodsDetailInfo"].get("goodsDetailHtml", ""),
        "price_info": stored.get("priceInfo", {}),
    }


for t in data["top6"]:
    gds = t["gdsNo"]
    rank = t["rank"]
    cat = t["category"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    out = TPL_ROOT / dir_name
    print(f"[{rank}] gdsNo={gds} ...")

    info = fetch_one(gds)
    (out / "detail.html").write_text(info["detail_html"], encoding="utf-8")
    (out / "page_meta.json").write_text(
        json.dumps(
            {
                "gdsNo": gds,
                "gdsNm": info.get("gdsNm"),
                "brandNm": info.get("brandNm"),
                "categories": info.get("categories"),
                "gallery_images": info.get("images"),
                "evaluation": info.get("evaluation"),
                "price_info": info.get("price_info"),
                "detail_html_len": len(info["detail_html"]),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  detail_html: {len(info['detail_html'])//1024}KB, gallery: {len(info.get('images') or [])} imgs")
    time.sleep(0.5)

print("done")

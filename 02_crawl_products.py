"""한샘 카테고리(sofa/wardrobe/desk) × 10 제품 detail page 분석.

- 카테고리 페이지의 __NEXT_DATA__에서 gdsNo 수집
- 각 제품 페이지 mall_prod_info 영역의 <img> 추출
- 첫 N장만 PIL로 dimension 측정 → long-strip 판별
- pattern_type 분류 + JSON 출력
"""

from __future__ import annotations

import concurrent.futures as cf
import io
import json
import random
import re
import time
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup
from PIL import Image

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HERE = Path(__file__).parent

CATEGORIES = {
    "sofa": [20081],
    "wardrobe": [20086],
    "desk": [20094, 20099],
}

NEXT_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL
)
PER_CATEGORY = 10
DIM_SAMPLE = 4  # number of first imgs to actually fetch for dimension

random.seed(42)
client = httpx.Client(
    headers={"User-Agent": UA, "Accept-Language": "ko"}, timeout=15.0
)


def fetch_next_data(url: str) -> dict[str, Any] | None:
    r = client.get(url)
    r.raise_for_status()
    m = NEXT_RE.search(r.text)
    if not m:
        return None
    return json.loads(m.group(1))


def collect_gds_from_category(ctgr_no: int) -> list[dict[str, Any]]:
    """Return list of {gdsNo, gdsNm, thumbnail, dcPrc} for a category."""
    url = f"https://store.hanssem.com/category/{ctgr_no}"
    nd = fetch_next_data(url)
    if not nd:
        return []
    sections = nd["props"]["pageProps"]["data"]["data"]
    products = []
    for s in sections:
        if s.get("componentType") != "GOODS":
            continue
        for group in s.get("data", {}).get("content", []):
            inner = group.get("data", {}).get("content", [])
            for p in inner:
                gds = {
                    "gdsNo": p["gdsNo"],
                    "gdsNm": p.get("gdsNm"),
                    "thumbnail": p.get("imageUrl"),
                    "salePrc": p.get("dcPrc") or p.get("normalSalePrc"),
                    "brand": p.get("goodsBrandInfoDto", {}).get("brandNm"),
                    "reviewCnt": p.get("goodsEvaluationStatInfoDto", {}).get("totCnt", 0),
                }
                products.append(gds)
    # dedup by gdsNo
    seen = {}
    for p in products:
        if p["gdsNo"] not in seen:
            seen[p["gdsNo"]] = p
    return list(seen.values())


def fetch_image_dim(url: str) -> tuple[int, int] | None:
    """Fetch first ~64KB and parse dimensions with PIL."""
    try:
        # Try GET with stream — fetch full but small images OK
        r = client.get(url, timeout=10.0)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content))
        return img.size  # (w, h)
    except Exception:
        return None


def analyze_product(p: dict[str, Any], category: str) -> dict[str, Any]:
    gds_no = p["gdsNo"]
    url = f"https://store.hanssem.com/goods/{gds_no}"
    out = {
        **p,
        "category": category,
        "url": url,
        "pattern_type": "unknown",
        "detail_img_count": 0,
        "detail_imgs": [],
        "sampled_dims": [],
        "total_height_sampled": 0,
        "note": "",
    }
    try:
        r = client.get(url)
        r.raise_for_status()
    except Exception as e:
        out["note"] = f"fetch_err:{e}"
        return out

    # primary: extract detail HTML from __NEXT_DATA__ initialState (consistent across all products)
    detail_html = ""
    m = NEXT_RE.search(r.text)
    if m:
        try:
            nd = json.loads(m.group(1))
            detail_html = (
                nd["props"]["pageProps"]["initialState"]["goodsDetail"]
                ["storedGoods"][str(gds_no)]["detailInfo"]["goodsDetailInfo"]
                .get("goodsDetailHtml", "")
            )
        except (KeyError, TypeError):
            detail_html = ""

    if not detail_html:
        # fallback to mall_prod_info DOM scrape
        soup = BeautifulSoup(r.text, "lxml")
        mp = soup.find(class_="mall_prod_info")
        if mp:
            detail_html = str(mp)
        else:
            out["note"] = "no_detail_html"
            return out

    out["detail_html_len"] = len(detail_html)
    soup = BeautifulSoup(detail_html, "lxml")
    imgs = soup.find_all("img")
    srcs = []
    for im in imgs:
        s = im.get("src") or im.get("data-src")
        if s:
            if s.startswith("http://"):
                s = "https://" + s[7:]
            srcs.append(s)
    out["detail_img_count"] = len(srcs)
    out["detail_imgs"] = srcs

    # sample first N for dimensions
    dims = []
    total_h = 0
    for s in srcs[:DIM_SAMPLE]:
        d = fetch_image_dim(s)
        if d:
            dims.append({"src": s, "w": d[0], "h": d[1]})
            total_h += d[1]
        time.sleep(0.15)
    out["sampled_dims"] = dims
    out["total_height_sampled"] = total_h

    # classify
    n = len(srcs)
    max_h = max((d["h"] for d in dims), default=0)
    if n == 0:
        out["pattern_type"] = "unknown"
    elif n <= 3 and max_h >= 3000:
        out["pattern_type"] = "long_strip"
    elif n >= 8:
        out["pattern_type"] = "split_panels"
    elif max_h >= 3500:
        # few imgs but one of them tall = long-ish
        out["pattern_type"] = "hybrid"
    else:
        out["pattern_type"] = "split_panels"

    return out


def main():
    all_products: list[dict[str, Any]] = []
    for cat_name, ctgr_nos in CATEGORIES.items():
        print(f"[{cat_name}] fetching categories {ctgr_nos}...")
        pool = []
        for c in ctgr_nos:
            pool.extend(collect_gds_from_category(c))
        # Filter: must have reviewCnt > 0 (active product) and thumbnail
        active = [p for p in pool if p.get("thumbnail") and p.get("salePrc")]
        # Prefer high-review products for stability (templates more polished)
        active.sort(key=lambda p: -p.get("reviewCnt", 0))
        # pick top 25 then random-sample 10 (mix popular + variety)
        head = active[:25]
        sample = random.sample(head, min(PER_CATEGORY, len(head)))
        print(f"  pool={len(pool)} active={len(active)} sampled={len(sample)}")

        for i, p in enumerate(sample, 1):
            print(f"  [{cat_name} {i}/{len(sample)}] gdsNo={p['gdsNo']} {p['gdsNm'][:40]}")
            try:
                analyzed = analyze_product(p, cat_name)
                all_products.append(analyzed)
            except Exception as e:
                print(f"    ERR: {e}")
            time.sleep(0.5)

    # write JSON
    by_pat = {}
    by_cat = {}
    for p in all_products:
        by_pat[p["pattern_type"]] = by_pat.get(p["pattern_type"], 0) + 1
        by_cat[p["category"]] = by_cat.get(p["category"], 0) + 1

    summary = {
        "total_products": len(all_products),
        "by_category": by_cat,
        "by_pattern": by_pat,
        "category_ids": CATEGORIES,
    }
    payload = {"summary": summary, "products": all_products}
    out_path = HERE / "hanssem_pattern.json"
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nwrote {out_path}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

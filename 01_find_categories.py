"""한샘 카테고리 ID → 이름 매핑 + 소파/옷장/책상 카테고리 식별."""

import concurrent.futures as cf
import re
import time
from pathlib import Path

import httpx

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HERE = Path(__file__).parent

with open("/tmp/hanssem_cats.txt") as f:
    cat_ids = [line.strip().split("/")[-1] for line in f if line.strip()]

print(f"probing {len(cat_ids)} categories...")

client = httpx.Client(headers={"User-Agent": UA}, timeout=10.0, http2=False)
title_re = re.compile(r"<title>([^<]+)</title>")

def probe(cid):
    try:
        r = client.get(f"https://store.hanssem.com/category/{cid}")
        m = title_re.search(r.text)
        title = m.group(1) if m else ""
        return cid, title, len(r.text)
    except Exception as e:
        return cid, f"ERR:{e}", 0

results = []
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for cid, title, size in ex.map(probe, cat_ids):
        results.append((cid, title, size))

# write all
out = HERE / "categories.tsv"
with out.open("w") as f:
    f.write("cid\ttitle\tsize\n")
    for cid, title, size in sorted(results):
        f.write(f"{cid}\t{title}\t{size}\n")

# filter sofa/wardrobe/desk
keywords = {"소파": "sofa", "옷장": "wardrobe", "장롱": "wardrobe", "책상": "desk"}
matched = []
for cid, title, size in results:
    for k, en in keywords.items():
        if k in title:
            matched.append((cid, title, en))
            break

print(f"\nMatched categories ({len(matched)}):")
for cid, title, en in matched:
    print(f"  {cid}\t{en}\t{title}")

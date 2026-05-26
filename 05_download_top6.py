"""Top 6 템플릿의 detail 이미지 116장 다운로드.

출력: 5th/hanssem_research/templates/{rank}_{category}_{gdsNo}/panel_NN.{ext}
"""

import concurrent.futures as cf
import json
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HERE = Path(__file__).parent
OUT_ROOT = HERE / "templates"
OUT_ROOT.mkdir(exist_ok=True)

data = json.loads((HERE / "top6_template_urls.json").read_text())

client = httpx.Client(headers={"User-Agent": UA}, timeout=30.0)


def download_one(url: str, dest: Path) -> tuple[Path, bool, str]:
    if dest.exists() and dest.stat().st_size > 1024:
        return dest, True, "cached"
    try:
        r = client.get(url)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return dest, True, f"{len(r.content)//1024}KB"
    except Exception as e:
        return dest, False, f"ERR:{e}"


total_ok = 0
total_fail = 0
for t in data["top6"]:
    rank = t["rank"]
    cat = t["category"]
    gds = t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    out_dir = OUT_ROOT / dir_name
    out_dir.mkdir(exist_ok=True)

    print(f"\n=== #{rank} [{cat}] gdsNo={gds} | {len(t['detail_imgs'])} imgs ===")
    print(f"    -> {out_dir}")

    # meta file
    (out_dir / "meta.json").write_text(
        json.dumps(
            {
                "rank": rank,
                "category": cat,
                "gdsNo": gds,
                "name": t["name"],
                "url": t["url"],
                "thumbnail": t["thumbnail"],
                "brand": t.get("brand"),
                "price": t.get("price"),
                "reviewCnt": t.get("reviewCnt"),
                "panel_count": t["detail_img_count"],
                "detail_imgs": t["detail_imgs"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # also fetch thumbnail
    thumb_url = t["thumbnail"]
    if thumb_url:
        thumb_ext = urlparse(thumb_url).path.split(".")[-1].split("?")[0] or "jpg"
        thumb_dest = out_dir / f"_thumbnail.{thumb_ext}"
        _, ok, msg = download_one(thumb_url, thumb_dest)
        print(f"    thumb {ok}: {msg}")

    # detail panels (parallel)
    tasks = []
    for i, src in enumerate(t["detail_imgs"], 1):
        ext = urlparse(src).path.split(".")[-1].split("?")[0].lower() or "jpg"
        if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
            ext = "jpg"
        dest = out_dir / f"panel_{i:02d}.{ext}"
        tasks.append((src, dest, i))

    ok_n = 0
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(download_one, src, dest): (idx, src) for src, dest, idx in tasks}
        for f in cf.as_completed(futures):
            idx, src = futures[f]
            _, ok, msg = f.result()
            if ok:
                ok_n += 1
            else:
                print(f"    panel_{idx:02d} FAIL: {msg}")
    print(f"    panels: {ok_n}/{len(tasks)} ok")
    total_ok += ok_n
    total_fail += len(tasks) - ok_n
    time.sleep(0.5)

print(f"\n=== DONE === ok={total_ok} fail={total_fail}")
print(f"output: {OUT_ROOT}")

"""자동 공정 파이프라인 — gdsNo 하나만 주면 모든 데이터 자동 준비.

운영 시: 담당자 업로드 (제품샷/소재/컬러 zone 분리)
지금: 한샘 페이지 vision으로 시뮬레이션 — gdsNo → 페이지 fetch → 전체 자동

stages:
  1. fetch detail page → detail.html, panels download
  2. GIF slice (있으면)
  3. all panels vision classify → input zones (product_shot/material/color/spec/etc)
  4. spec synthesize (좌석수/사이즈/소재/컬러/쿠션/소재인증 등)
  5. visual description (GIF + hero panel combined)
  6. smart sheet composite
  7. zone summary export

사용: python auto_pipeline.py <gdsNo> [--output-dir user_products/<gdsNo>]
"""

import argparse
import asyncio
import io
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
from PIL import Image, ImageDraw, ImageFont

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import openai_client as client, data_uri  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
NEXT_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL)

HERE = Path(__file__).parent


# =================== Stage 1: fetch ===================
def fetch_product(gds_no: int, out_dir: Path, http_client: httpx.Client) -> dict:
    r = http_client.get(f"https://store.hanssem.com/goods/{gds_no}")
    r.raise_for_status()
    m = NEXT_RE.search(r.text)
    nd = json.loads(m.group(1))
    pp = nd["props"]["pageProps"]
    di = pp["defaultInfo"]
    stored = pp["initialState"]["goodsDetail"]["storedGoods"][str(gds_no)]
    detail_html = stored["detailInfo"]["goodsDetailInfo"].get("goodsDetailHtml", "")

    (out_dir / "detail.html").write_text(detail_html, encoding="utf-8")

    img_urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', detail_html)
    img_urls = [("https://" + u[8:]) if u.startswith("http://") else u for u in img_urls]
    img_urls = [u.replace("devimage.hanssem.com", "image.hanssem.com") for u in img_urls]

    # download panels
    print(f"  downloading {len(img_urls)} panels...")
    gif_panels = []
    panel_paths = []
    for i, u in enumerate(img_urls, 1):
        ext = urlparse(u).path.split(".")[-1].split("?")[0].lower() or "jpg"
        if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
            ext = "jpg"
        dest = out_dir / f"panel_{i:02d}.{ext}"
        if not dest.exists() or dest.stat().st_size < 1024:
            try:
                rr = http_client.get(u)
                rr.raise_for_status()
                dest.write_bytes(rr.content)
            except Exception as e:
                print(f"    panel_{i:02d} FAIL: {e}")
                continue
        panel_paths.append(dest)
        if ext == "gif":
            gif_panels.append(i)

    # download hero / cover (gds 갤러리 메인)
    cover_url = f"https://image.hanssem.com/hsimg/gds/1050/{gds_no // 1000}/{gds_no}_A1.jpg?w=1000&h=1000"
    try:
        rr = http_client.get(cover_url)
        if rr.status_code == 200:
            (out_dir / "_cover_1000.jpg").write_bytes(rr.content)
            print(f"  cover (1000x1000) downloaded")
    except Exception as e:
        print(f"  cover FAIL: {e}")

    # text nodes
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(detail_html, "lxml")
    text_nodes = [el.strip() for el in soup.find_all(string=True) if el.strip() and len(el.strip()) > 2]

    return {
        "gds_no": gds_no,
        "gds_nm": di["gdsNm"],
        "brand": di.get("brandNm"),
        "categories": [c.get("ctgrNm") for c in di.get("categories", [])],
        "description": stored["metaInfo"].get("description"),
        "keywords": (stored["metaInfo"].get("srchKeyWd") or "").split("$$"),
        "panel_count": len(panel_paths),
        "panel_paths": [str(p.relative_to(out_dir)) for p in panel_paths],
        "gif_panels": gif_panels,
        "text_nodes_in_detail_html": text_nodes,
        "price": {
            "normal": stored["apiResponse"]["data"]["goods"].get("normalSalePrc"),
            "dc": stored["apiResponse"]["data"]["goods"].get("dcPrc"),
        },
        "url": f"https://store.hanssem.com/goods/{gds_no}",
    }


# =================== Stage 2: GIF slice ===================
def slice_gif(out_dir: Path, gif_panels: list[int]) -> list[Path]:
    frames_dir = out_dir / "gif_frames"
    frames_dir.mkdir(exist_ok=True)
    saved = []
    for gp_idx in gif_panels:
        gif_path = out_dir / f"panel_{gp_idx:02d}.gif"
        if not gif_path.exists():
            continue
        img = Image.open(gif_path)
        n_frames = getattr(img, "n_frames", 1)
        # sample up to 8 unique frames
        sample_n = min(8, n_frames)
        indices = sorted(set(int(i * (n_frames - 1) / max(1, sample_n - 1)) for i in range(sample_n)))
        for k, idx in enumerate(indices, 1):
            img.seek(idx)
            frame = img.convert("RGB")
            dest = frames_dir / f"p{gp_idx:02d}_frame_{k:02d}.jpg"
            frame.save(dest, quality=88)
            saved.append(dest)
        print(f"  panel_{gp_idx:02d}.gif → {len(indices)} frames saved")
    return saved


# =================== Stage 3: vision classify (input zones) ===================
PANEL_CLASSIFY_PROMPT = """\
You are analysing a single panel image from a Korean furniture (sofa) product
detail page. Classify by input zone (운영 시 담당자가 어떤 업로드 존에
넣을지) and provide visible information.

Return JSON:
- "input_zone" (str): one of
    "product_shot" — clean main product photograph (white/neutral bg)
    "material_swatch" — fabric/leather texture close-up or cushion fill cross-section
    "color_option" — color variant grid or swatch grid
    "size_chart" — dimension diagram with measurement lines
    "structure_chart" — internal frame/structure cross-section
    "module_lineup" — multiple sofa configurations side-by-side
    "lifestyle_scene" — sofa in a styled room
    "detail_close_up" — texture/seam/leg/arm close-up
    "intro_hero" — hero/cover shot
    "delivery_info" — delivery/warranty/QnA
    "context" — background/storytelling
    "other"
- "layout_type" (str): "fixed_layout" (chart/dim/grid — structure MUST be preserved) /
    "flexible_staging" (room/lifestyle — staging can vary) /
    "strict_white_bg" (cover/intro hero) / "other"
- "extracted_info" (str): all visible Korean text/numbers verbatim (dimensions,
    material names, color names, etc.)
- "key_visual_facts" (list of str): a few short English facts about what is
    visually shown (sofa shape, fabric color, cushion count, etc.)
No preamble.
"""


def classify_panels(panel_paths: list[Path]) -> list[dict]:
    print(f"  vision-classifying {len(panel_paths)} panels...")
    results = []
    for p in panel_paths:
        if p.suffix == ".gif":
            # use a frame for classification
            cand = None
            frames_dir = p.parent / "gif_frames"
            for f in frames_dir.glob(f"{p.stem}_frame_*.jpg"):
                cand = f
                break
            target = cand or p  # PIL can read GIF directly
        else:
            target = p
        try:
            resp = client.chat.completions.create(
                model=config.VISION_MODEL,
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": PANEL_CLASSIFY_PROMPT},
                    {"type": "image_url", "image_url": {"url": data_uri(target)}},
                ]}],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            d = json.loads(resp.choices[0].message.content)
            d["panel"] = p.name
            results.append(d)
            print(f"    {p.name}: [{d.get('input_zone'):>18}] / {d.get('layout_type'):>16}")
        except Exception as e:
            print(f"    {p.name}: ERR {e}")
            results.append({"panel": p.name, "error": str(e)})
    return results


# =================== Stage 4: synthesize spec ===================
def synthesize_spec(meta: dict, panel_classifications: list[dict]) -> dict:
    """Combine page meta + panel info into structured spec."""
    SYNTH = """\
You are given panel-by-panel classifications and metadata of a Korean sofa
product detail page. Synthesise a clean product spec JSON.

Important: extract spec for the **specific seat-count variant** that the page
emphasises (look at the title and main panels). If multiple variants exist,
pick the dominant one. Output the seat count explicitly.

Return JSON:
{
  "product_name": str (정확한 한국어 제품명),
  "seat_count": int,
  "dimensions": {"width_cm": int|null, "depth_cm": int|null, "height_cm": int|null,
                 "seat_height_cm": int|null, "arm_height_cm": int|null,
                 "seat_depth_cm": int|null},
  "material": {"upholstery": str, "upholstery_certifications": [str],
               "seat_cushion": str, "back_cushion": str, "cushion_firmness": str,
               "frame": str},
  "colors": [list of Korean color names],
  "warranty": str|null,
  "key_features": [list of short Korean phrases],
  "ko_summary": "2-3 Korean sentences"
}
"""
    payload = {"meta": meta, "panel_classifications": panel_classifications}
    resp = client.chat.completions.create(
        model=config.VISION_MODEL,
        messages=[{"role": "user", "content":
            SYNTH + "\n\nINPUT:\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        }],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    return json.loads(resp.choices[0].message.content)


# =================== Stage 5: visual description from refs ===================
GIF_VISION_PROMPT = """\
You are analysing reference frames of a Korean fabric sofa for an AI image
generator that must reproduce this exact sofa. Describe every visible product
detail.

Return JSON:
{
  "seat_count": int (count the seat cushions carefully),
  "silhouette": str,
  "arm": {"shape": str, "height_relative": str},
  "back": {"cushion_count": int, "shape": str, "attached_or_loose": str, "headrest": bool},
  "seat": {"cushion_count": int, "depth": str, "firmness": str},
  "upholstery": {"material": str, "texture": str, "seams": str, "primary_color": str},
  "legs": {"count": int, "shape": str, "color": str},
  "decorative_pillows": {"count": int, "shape": str},
  "decorative_elements": str,
  "full_visual_paragraph": "5-7 dense English sentences for the image generator"
}
No preamble. Be conservative with seat_count.
"""


def vision_describe_product(ref_paths: list[Path]) -> dict:
    refs = ref_paths[:6]
    print(f"  vision-describing product from {len(refs)} references...")
    msg_content = [{"type": "text", "text": GIF_VISION_PROMPT}]
    for i, p in enumerate(refs, 1):
        msg_content.append({"type": "text", "text": f"Reference {i}:"})
        msg_content.append({"type": "image_url", "image_url": {"url": data_uri(p)}})
    resp = client.chat.completions.create(
        model=config.VISION_MODEL,
        messages=[{"role": "user", "content": msg_content}],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    return json.loads(resp.choices[0].message.content)


# =================== Stage 6: smart sheet ===================
def build_smart_sheet(ref_paths: list[Path], out_path: Path,
                      product_name: str = "Sofa Reference"):
    if not ref_paths:
        return None
    imgs = [Image.open(f).convert("RGB") for f in ref_paths[:3]]
    target_h = 580
    imgs_r = [im.resize((int(target_h * im.width / im.height), target_h)) for im in imgs]
    total_w = sum(im.width for im in imgs_r) + 20 * (len(imgs_r) + 1)
    sheet = Image.new("RGB", (total_w, target_h + 80), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    try:
        font_t = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 22)
        font_l = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 14)
    except OSError:
        font_t = ImageFont.load_default()
        font_l = ImageFont.load_default()
    draw.text((20, 12), f"{product_name} — Multi-angle Reference", fill=(20, 20, 20), font=font_t)
    x = 20
    labels = ["3/4 front", "side profile", "back / angle"]
    for im, label in zip(imgs_r, labels):
        sheet.paste(im, (x, 50))
        draw.text((x + 8, 50 + target_h + 6), label, fill=(80, 80, 80), font=font_l)
        x += im.width + 20
    sheet.save(out_path, quality=92)
    return out_path


# =================== Stage 7: zone group ===================
def group_by_zone(panel_classifications: list[dict], out_dir: Path) -> dict:
    """Group panels by input_zone — simulates 운영 시 업로드 존 분리."""
    zones: dict[str, list[str]] = {}
    for p in panel_classifications:
        z = p.get("input_zone", "other")
        zones.setdefault(z, []).append(p["panel"])
    return zones


# =================== Pipeline runner ===================
def run_pipeline(gds_no: int, out_root: Path = HERE / "user_products") -> Path:
    out_dir = out_root / f"milo_{gds_no}" if gds_no == 777039 else out_root / f"p_{gds_no}"
    out_dir.mkdir(parents=True, exist_ok=True)

    http_client = httpx.Client(headers={"User-Agent": UA}, timeout=30.0)
    t0 = time.time()

    print(f"\n=== auto pipeline: gdsNo={gds_no} ===")
    print(f"  output: {out_dir}")

    # Stage 1
    print("\n[1/7] fetch product page + download panels")
    meta = fetch_product(gds_no, out_dir, http_client)

    # Stage 2
    print("\n[2/7] GIF slice")
    panel_paths = sorted([p for p in out_dir.glob("panel_*.*")
                          if p.suffix != ".json"])
    gif_frames = slice_gif(out_dir, meta["gif_panels"])

    # Stage 3
    print("\n[3/7] vision classify panels (input zones)")
    panel_classifications = classify_panels(panel_paths)

    # Stage 4
    print("\n[4/7] synthesize structured spec")
    spec = synthesize_spec(meta, panel_classifications)
    print(f"  product: {spec.get('product_name')} ({spec.get('seat_count')}인)")

    # Stage 5 — pick representative refs (GIF frames + hero/intro panels)
    print("\n[5/7] vision-describe product visual")
    # collect refs: GIF frames + first product_shot panel
    refs = gif_frames[:3]
    if not refs:
        hero = next(
            (p for p in panel_paths if any(
                c["panel"] == p.name and c.get("input_zone") in ("product_shot", "intro_hero")
                for c in panel_classifications)),
            panel_paths[0] if panel_paths else None,
        )
        if hero:
            refs = [hero]
    visual = vision_describe_product(refs)

    # Stage 6
    print("\n[6/7] build smart sheet")
    sheet_path = out_dir / "smart_sheet.jpg"
    if refs:
        build_smart_sheet(refs, sheet_path, spec.get("product_name", "Sofa"))
        print(f"  saved {sheet_path}")

    # Stage 7
    print("\n[7/7] zone grouping")
    zones = group_by_zone(panel_classifications, out_dir)
    for z, panels in sorted(zones.items(), key=lambda x: -len(x[1])):
        print(f"  zone '{z}': {len(panels)} panels — {panels[:3]}{'…' if len(panels) > 3 else ''}")

    # combined output
    output = {
        "gds_no": gds_no,
        "meta": meta,
        "spec": spec,
        "visual": visual,
        "panel_classifications": panel_classifications,
        "input_zones": zones,
        "references": {
            "gif_frames": [str(p.relative_to(out_dir)) for p in gif_frames],
            "smart_sheet": "smart_sheet.jpg" if sheet_path.exists() else None,
            "cover": "_cover_1000.jpg" if (out_dir / "_cover_1000.jpg").exists() else None,
        },
        "wall_seconds": round(time.time() - t0, 1),
    }
    (out_dir / "auto_pipeline_output.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n=== DONE === wall {output['wall_seconds']}s")
    print(f"  → {out_dir / 'auto_pipeline_output.json'}")
    return out_dir


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("gds_no", type=int)
    ap.add_argument("--output-dir", type=Path, default=None)
    args = ap.parse_args()
    out_root = args.output_dir.parent if args.output_dir else HERE / "user_products"
    run_pipeline(args.gds_no, out_root)

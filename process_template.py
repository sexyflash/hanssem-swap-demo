"""사용자 단일 trigger 진입점 — 한 template 한 사용자 제품 자동 전 과정 처리.

사용:
  python3 process_template.py 2     # _pending/02_wardrobe/ 처리
  python3 process_template.py 02_wardrobe
  python3 process_template.py --all  # 사진 채워진 모든 _pending/0X_*/ 처리

자동 수행:
  1) url.txt → product_input.json (LLM scrape)
  2) use_product/* → classification.json (vision)
  3) 한샘 panel × 사용자 제품 → mismatch_resolution.json (LLM)
  4) v17 swap pipeline 실행
  5) report 갱신

각 단계는 이미 결과가 있으면 skip (--force 로 강제 재실행 가능).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
sys.path.insert(0, str(HERE))

from lib import openai_client, data_uri  # noqa: E402
from pipeline_lib import mismatch_resolver, product_url_scraper  # noqa: E402

TEXT_MODEL = "gpt-5"
VISION_MODEL = "gpt-5.5"

# 현재 활성화된 rank 만 처리 — 사용자 결정으로 #4~#6 은 주석 처리됨 (사용자 제품 미공급)
ENABLED_RANKS = {2, 3}  # 활성: #2 wardrobe, #3 desk. 추후 #4/5/6 추가 시 여기 확장.

TOP6 = json.loads((HERE / "top6_template_urls.json").read_text())["top6"]


def _resolve_template_for_rank(rank: int) -> tuple[Path, dict]:
    t = next((x for x in TOP6 if x["rank"] == rank), None)
    if not t:
        sys.exit(f"rank {rank} 없음")
    tpl = HERE / f"templates/{rank:02d}_{t['category']}_{t['gdsNo']}"
    return tpl, t


def _resolve_pending_dir(arg: str) -> tuple[Path, int, dict]:
    """arg 가 '2', '02', '02_wardrobe' 일 때 모두 _pending/0X_xxx/ 로 매핑."""
    arg = arg.strip()
    if arg.isdigit():
        rank = int(arg)
    else:
        m = re.match(r"^(\d+)", arg)
        if not m:
            sys.exit(f"인자 인식 못함: {arg}")
        rank = int(m.group(1))
    if rank not in ENABLED_RANKS:
        sys.exit(f"rank {rank}는 현재 비활성화 (ENABLED_RANKS={sorted(ENABLED_RANKS)}). "
                 f"활성화하려면 process_template.py 의 ENABLED_RANKS 갱신.")
    tpl, meta = _resolve_template_for_rank(rank)
    # _pending 디렉토리 찾기 — rank prefix
    pending_root = HERE / "user_products/_pending"
    cands = list(pending_root.glob(f"{rank:02d}_*"))
    if not cands:
        sys.exit(f"_pending/{rank:02d}_*/ 디렉토리 없음")
    return cands[0], rank, meta


def _final_user_dir(pending_dir: Path, product_input: dict) -> Path:
    """ASCII safe 디렉토리명 — pending_dir 이름 형식 (0X_<category>_<code>) 유지.

    URL 에서 product code 가 있으면 그것을 사용, 없으면 pending_dir 그대로.
    fal upload 가 한글 path 에서 ASCII 인코딩 에러를 일으키므로 ASCII만 허용.
    """
    rank_prefix, _, cat = pending_dir.name.partition("_")
    # URL 에서 한샘 product code 추출 시도
    url = product_input.get("_source_url", "") or ""
    m = re.search(r"/goods/(\d+)", url)
    code = m.group(1) if m else ""
    if code:
        return HERE / f"user_products/{rank_prefix}_{cat}_{code}"
    return HERE / f"user_products/{rank_prefix}_{cat}"


async def process_one(pending_dir: Path, rank: int, hanssem_meta: dict, force: bool = False) -> None:
    print(f"\n{'='*60}\n  처리 시작: {pending_dir.name} (rank={rank}, 한샘={hanssem_meta['name']})\n{'='*60}")
    tpl_dir = HERE / f"templates/{rank:02d}_{hanssem_meta['category']}_{hanssem_meta['gdsNo']}"

    # 1) url.txt → product_input.json
    url_path = pending_dir / "url.txt"
    pi_path = pending_dir / "product_input.json"
    if pi_path.exists() and not force:
        print(f"[1/4] product_input.json 재사용")
        product_input = json.loads(pi_path.read_text())
    else:
        if not url_path.exists():
            print(f"[1/4] url.txt 없음 — placeholder product_input.json 생성")
            product_input = {
                "product_name": pending_dir.name,
                "spec": {}, "feature_descriptions": {},
                "color_options_detail": [], "model_options": [],
                "user_override": {},
            }
        else:
            url = url_path.read_text().strip().splitlines()[0].strip()
            print(f"[1/4] URL scrape: {url}")
            product_input = await asyncio.to_thread(
                product_url_scraper.scrape_product, openai_client, TEXT_MODEL, url
            )
            print(f"  → {product_input.get('product_name','?')}")
        pi_path.write_text(json.dumps(product_input, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2) classification.json
    use_prod_dir = pending_dir / "use_product"
    use_prod_dir.mkdir(exist_ok=True)
    cls_path = use_prod_dir / "classification.json"
    if cls_path.exists() and not force:
        print(f"[2/4] classification.json 재사용")
    else:
        # 96_classify_assets_cli 호출
        n_imgs = len([p for p in use_prod_dir.iterdir() if p.is_file() and p.suffix.lower() in {".jpg",".jpeg",".png",".webp"}])
        if n_imgs == 0:
            print(f"[2/4] use_product/ 비어있음 — 분류 skip (사용자가 사진 채워야 함)")
        else:
            print(f"[2/4] vision 분류 ({n_imgs}장)...")
            proc = subprocess.run(
                [sys.executable, str(HERE / "96_classify_assets_cli.py"), str(use_prod_dir)],
                capture_output=True, text=True,
            )
            if proc.returncode != 0:
                print(f"  ERR: {proc.stderr[:400]}")
            else:
                print(f"  → {cls_path.name}")

    # 3) mismatch_resolution.json (한샘 × 사용자 제품)
    mm_path = tpl_dir / "mismatch_resolution.json"
    if mm_path.exists() and not force:
        print(f"[3/4] mismatch_resolution.json 재사용")
    else:
        layouts = json.loads((tpl_dir / "panel_layout_maps.json").read_text())["panels"]
        cover_panel = next((p for p in layouts if p.get("panel") == "cover"), None)
        non_cover = [p for p in layouts if p.get("panel") != "cover" and "error" not in p]
        print(f"[3/4] mismatch resolve ({len(non_cover)} panels + cover)...")
        result = await asyncio.to_thread(
            mismatch_resolver.resolve_all_panels,
            openai_client, VISION_MODEL,
            non_cover, tpl_dir,
            hanssem_meta["name"], product_input,
            data_uri, cover_panel,
        )
        mm_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        match_n = sum(1 for r in result["resolutions"] if r["verdict"] == "match")
        bypass_n = sum(1 for r in result["resolutions"] if r["verdict"] == "bypass")
        skip_n = sum(1 for r in result["resolutions"] if r["verdict"] == "skip")
        print(f"  → match={match_n}, bypass={bypass_n}, skip={skip_n}")

    # 4) _pending → final user_products/<id>/ 이동 (이미 옮겼으면 sync)
    final_user = _final_user_dir(pending_dir, product_input)
    if final_user.exists():
        print(f"[4/4] final user dir 이미 존재: {final_user.name}")
        # use_product 안의 파일 sync (pending 에 use_product 가 아직 있을 때만)
        if use_prod_dir.exists():
            target_use = final_user / "use_product"
            target_use.mkdir(exist_ok=True)
            for p in use_prod_dir.iterdir():
                if p.is_file():
                    shutil.copy2(p, target_use / p.name)
        if pi_path.exists() and not (final_user / "product_input.json").exists():
            shutil.copy2(pi_path, final_user / "product_input.json")
    else:
        print(f"[4/4] pending → {final_user.name} 이동")
        shutil.move(str(pending_dir), str(final_user))

    # 5) v17 pipeline 실행
    rel_tpl = tpl_dir.relative_to(HERE)
    rel_user = final_user.relative_to(HERE)
    print(f"\n→ pipeline 실행: --template {rel_tpl} --user-product {rel_user} --product-input product_input.json")
    proc = subprocess.run(
        [sys.executable, str(HERE / "76_swap_pipeline_v16.py"),
         "--template", str(rel_tpl),
         "--user-product", str(rel_user),
         "--product-input", "product_input.json"],
        cwd=HERE,
    )
    if proc.returncode != 0:
        print(f"  pipeline error (exit {proc.returncode})")
    print(f"\n✓ rank {rank} 처리 끝.")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", help="rank 번호 또는 _pending/0X_xxx 이름")
    parser.add_argument("--all", action="store_true", help="사진 들어있는 모든 _pending/0X_*/ 처리")
    parser.add_argument("--force", action="store_true", help="기존 결과 있어도 재생성")
    args = parser.parse_args()

    if args.all:
        pending_root = HERE / "user_products/_pending"
        cands = [d for d in pending_root.glob("0?_*") if d.is_dir()
                 and any((d/"use_product").glob("*.*") if (d/"use_product").exists() else [])]
        for d in sorted(cands):
            rank = int(d.name.split("_")[0])
            if rank not in ENABLED_RANKS:
                print(f"  ⊘ rank {rank} 비활성화 — skip")
                continue
            meta = next((x for x in TOP6 if x["rank"] == rank), None)
            if not meta:
                continue
            await process_one(d, rank, meta, force=args.force)
    elif args.target:
        pending_dir, rank, meta = _resolve_pending_dir(args.target)
        await process_one(pending_dir, rank, meta, force=args.force)
    else:
        parser.error("target 인자 또는 --all 필요")


if __name__ == "__main__":
    asyncio.run(main())

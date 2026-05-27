"""실험 산출물 패키징 — 버전 자동 increment + 사용된 파일 동봉.

사용자 의도:
- swap_results/ 안에서 v\\d+ 디렉토리들의 마지막 번호 +1 자동 부여
- 각 run 디렉토리에 사용된 .py 본문 + product_input + ref mapping + smart sheet
  + 모든 prompt 사본까지 보관 → 나중에 다른 연구 과제에서 이 폴더만 들고 가면
  재현 가능한 self-contained bundle.
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

_VER_RE = re.compile(r"^v(\d+)_")


def next_version(swap_results_dir: Path) -> int:
    """swap_results/ 디렉토리의 v\\d+_* 들을 훑어 다음 정수 버전을 반환."""
    if not swap_results_dir.exists():
        return 1
    versions = []
    for entry in swap_results_dir.iterdir():
        if not entry.is_dir():
            continue
        m = _VER_RE.match(entry.name)
        if m:
            versions.append(int(m.group(1)))
    return (max(versions) + 1) if versions else 1


def make_run_dir(swap_results_dir: Path, version: int | None = None) -> tuple[Path, int]:
    """run 디렉토리를 만들고 (path, 부여된 버전 정수)를 반환."""
    swap_results_dir.mkdir(parents=True, exist_ok=True)
    v = version or next_version(swap_results_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = swap_results_dir / f"v{v}_{ts}"
    run_dir.mkdir()
    (run_dir / "gpt_image").mkdir(exist_ok=True)
    (run_dir / "prompts").mkdir(exist_ok=True)
    (run_dir / "qa_reports").mkdir(exist_ok=True)
    (run_dir / "sources").mkdir(exist_ok=True)
    return run_dir, v


def bundle_sources(run_dir: Path, files: list[Path]) -> list[str]:
    """사용된 .py / .json / smart sheet 파일을 run_dir/sources/로 복사. 상대 경로 리스트 반환."""
    out_dir = run_dir / "sources"
    out_dir.mkdir(exist_ok=True)
    rels = []
    for src in files:
        src = Path(src)
        if not src.exists():
            continue
        # 충돌 회피 위해 부모 directory 1단계 prefix
        target_name = f"{src.parent.name}__{src.name}" if src.parent.name else src.name
        dest = out_dir / target_name
        if dest.exists():  # idempotent overwrite
            dest.unlink()
        shutil.copy2(src, dest)
        rels.append(f"sources/{target_name}")
    return rels


def write_manifest(run_dir: Path, manifest: dict) -> Path:
    """run_dir/manifest.json — 실험 메타 + 사용 파일 + 핵심 결정."""
    path = run_dir / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_prompt(run_dir: Path, label: str, attempt_n: int, prompt: str) -> Path:
    """각 시도 prompt를 별도 파일로 — 나중에 비교/감사 용이."""
    path = run_dir / "prompts" / f"{label}__a{attempt_n}.md"
    path.write_text(prompt, encoding="utf-8")
    return path


def write_qa_report(run_dir: Path, label: str, attempt_n: int, qa_result: dict) -> Path:
    path = run_dir / "qa_reports" / f"{label}__a{attempt_n}.json"
    path.write_text(json.dumps(qa_result, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def update_latest_pointer(swap_results_dir: Path, version: int, run_name: str) -> None:
    """latest_v{N}.txt + latest.txt 모두 갱신."""
    (swap_results_dir / f"latest_v{version}.txt").write_text(run_name)
    (swap_results_dir / "latest.txt").write_text(run_name)

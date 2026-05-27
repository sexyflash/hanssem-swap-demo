"""Report v17 — 한샘 style preserved + payload 4-layer + per-attempt prompt toggle.

핵심 변경:
- panel-text 우리 스타일링 (h4 18px 등) 완전 제거 → 한샘 detail HTML inline style 그대로
- 우리가 추가하는 wrap은 .img-with-chip 만 (그 안 img는 한샘 그대로)
- payload 모달: 회차별 prompt + ref + bidirectional QA 결과
  · attempt 토글 → 그 attempt의 full prompt + ref refs + verdict + reference_influences
"""

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

HERE = Path(__file__).parent
TPL_ROOT = HERE / "templates"
USER_PROD_ROOT = HERE / "user_products"
OUT = HERE / "report" / "index.html"
OUT.parent.mkdir(exist_ok=True)

data = json.loads((HERE / "top6_template_urls.json").read_text())
milo_dir = USER_PROD_ROOT / "milo_777039"
auto_output = json.loads((milo_dir / "auto_pipeline_output.json").read_text())
spec = auto_output["spec"]
visual = auto_output["visual"]
# product_input — 필드 분리된 사용자 입력 (운영 시 담당자 입력 시뮬레이션)
# product_input_v3 — dense paragraph (가장 풍부)
_pi_v3 = milo_dir / "product_input_v3.json"
_pi_v2 = milo_dir / "product_input_v2.json"
_pi_v1 = milo_dir / "product_input.json"
if _pi_v3.exists():
    product_input = json.loads(_pi_v3.read_text())
elif _pi_v2.exists():
    product_input = json.loads(_pi_v2.read_text())
elif _pi_v1.exists():
    product_input = json.loads(_pi_v1.read_text())
else:
    product_input = {}
def _user_dir_for_rank(rank: int) -> Path | None:
    """rank → user_products/<id>/ Path."""
    if rank == 1:
        d = HERE / "user_products/milo_777039"
        return d if d.exists() else None
    for d in sorted((HERE / "user_products").glob(f"{rank:02d}_*")):
        if d.is_dir() and (d / "use_product").exists():
            return d
    return None


def _user_dir_rel_for_rank(rank: int) -> str:
    d = _user_dir_for_rank(rank)
    return f"../user_products/{d.name}" if d else "../user_products/milo_777039"


def _user_product_name_for_rank(rank: int) -> str:
    """user_products/0X_*/product_input.json 의 product_name. fallback: milo 2인용 (#1)."""
    user_root = HERE / "user_products"
    if rank == 1:
        for fn in ('product_input_v3.json', 'product_input.json'):
            p = user_root / "milo_777039" / fn
            if p.exists():
                try:
                    return json.loads(p.read_text()).get("product_name", "milo 2인용") or "milo 2인용"
                except Exception:
                    pass
        return "milo 2인용"
    for d in sorted(user_root.glob(f"{rank:02d}_*")):
        for fn in ('product_input.json', 'product_input_v3.json'):
            p = d / fn
            if p.exists():
                try:
                    return json.loads(p.read_text()).get("product_name", d.name) or d.name
                except Exception:
                    return d.name
    return f"rank {rank}"


def _load_mismatch_for_template(tpl_dir: Path):
    p = tpl_dir / "mismatch_resolution.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text())
    return {r["panel_idx"]: r for r in d.get("resolutions", [])}


def _load_text_subs_for_template(tpl_dir: Path):
    p = tpl_dir / "text_substitute.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text())
    return {item["i"]: item for item in d.get("substitutes", [])}


# #1 sofa (legacy 호환) — global 변수 유지 후 view() 에서 t 별로 override
mismatch = json.loads((TPL_ROOT / "01_sofa_992474/mismatch_resolution.json").read_text()) \
    if (TPL_ROOT / "01_sofa_992474/mismatch_resolution.json").exists() else {"resolutions": []}
text_subs_data = json.loads((TPL_ROOT / "01_sofa_992474/text_substitute.json").read_text()) \
    if (TPL_ROOT / "01_sofa_992474/text_substitute.json").exists() else {"substitutes": []}
verdict_by_panel = {r["panel_idx"]: r for r in mismatch.get("resolutions", [])}
text_subs_by_idx = {item["i"]: item for item in text_subs_data.get("substitutes", [])}

# QA 한국어 번역 로드 (v6 run 옆 qa_korean.json)
qa_korean_by = {}  # (label, attempt) → translation
_sr_dir = TPL_ROOT / "01_sofa_992474/swap_results"
_latest_v6 = _sr_dir / "latest_v7.txt"
if _latest_v6.exists():
    _run_dir_name = _latest_v6.read_text().strip()
    _qk_path = _sr_dir / _run_dir_name / "qa_korean.json"
    if _qk_path.exists():
        _qk = json.loads(_qk_path.read_text())
        for _t in _qk.get("translations", []):
            qa_korean_by[(_t["label"], _t["attempt"])] = _t

SECTIONS = ["커버", "기본정보", "사이즈", "소재", "옵션", "모듈"]
SECTION_SLUGS = {
    "커버": "cover", "기본정보": "info", "사이즈": "size",
    "소재": "material", "옵션": "option", "모듈": "module",
}
COMP_COLORED_CLASSES = {"intro_hero", "size_chart", "module_lineup", "color_option", "structure_chart"}


def assign_sections(panel_count):
    n = panel_count
    if n == 0:
        return {"커버": []}
    result = {"커버": []}
    remaining = SECTIONS[1:]
    per = max(1, n // len(remaining))
    idx = 1
    for i, s in enumerate(remaining):
        if idx > n:
            break
        end = n if i == len(remaining) - 1 else min(idx + per - 1, n)
        result[s] = list(range(idx, end + 1))
        idx = end + 1
    return result


def get_swap_results(t):
    # 모든 rank 의 swap_results 표시 (없으면 None)
    sr = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}" / "swap_results"
    if not sr.exists():
        return None
    # v18+ 동적으로 추가될 latest_vN.txt 도 잡음 — 최상위는 가장 큰 N
    sr_files = sorted([f.name for f in sr.glob("latest_v*.txt")],
                      key=lambda n: -int(n.replace("latest_v","").replace(".txt","") or "0"))
    for marker in sr_files + ["latest.txt"]:
        latest = sr / marker
        if latest.exists():
            run_name = latest.read_text().strip()
            run_dir = sr / run_name
            if (run_dir / "summary.json").exists():
                summary = json.loads((run_dir / "summary.json").read_text())
                by_label = {c["label"]: c for c in summary["cells"] if c.get("label")}
                # progress.in_progress 추출
                in_prog = set((summary.get("progress") or {}).get("in_progress") or [])
                return {
                    "run_dir_rel": f"../templates/{t['rank']:02d}_{t['category']}_{t['gdsNo']}/swap_results/{run_name}/gpt_image",
                    "summary": summary, "by_label": by_label,
                    "in_progress": in_prog,
                    "marker": marker,
                }
    return None


def cover_url_template(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    cov = TPL_ROOT / dir_name / "_cover_1000.jpg"
    if cov.exists():
        return f"../templates/{dir_name}/_cover_1000.jpg"
    thumbs = list((TPL_ROOT / dir_name).glob("_thumbnail.*"))
    return f"../templates/{dir_name}/{thumbs[0].name}" if thumbs else ""


def score_color(score, kind="prod", panel_class=None):
    if score is None or score == "-" or score == "?":
        return "score-na"
    try:
        s = int(score)
    except (ValueError, TypeError):
        return "score-na"
    if kind == "prod":
        if s >= 99: return "score-green"
        if s >= 95: return "score-amber"
        return "score-red"
    if panel_class in COMP_COLORED_CLASSES:
        if s >= 95: return "score-green"
        if s >= 90: return "score-amber"
        return "score-red"
    return "score-neutral"


_PANEL_REF_MAP = None
def _load_panel_ref_map():
    global _PANEL_REF_MAP
    if _PANEL_REF_MAP is None:
        p = TPL_ROOT / "01_sofa_992474/panel_ref_mapping.json"
        if p.exists():
            _PANEL_REF_MAP = json.loads(p.read_text())
        else:
            _PANEL_REF_MAP = {"assets": {}, "panels": {}}
    return _PANEL_REF_MAP


def zone_refs_for_panel(panel_label, t=None):
    """v14 panel-level refs — t 기반 동적 user_dir."""
    # 호출자가 t 안 줬으면 #1 (legacy) fallback
    rank = t["rank"] if t else 1
    user_rel = _user_dir_rel_for_rank(rank)
    # template 의 panel_ref_mapping_v16.json (각 swap_results run dir에 있음) 사용
    if t:
        sr_dir = TPL_ROOT / f"{rank:02d}_{t['category']}_{t['gdsNo']}/swap_results"
        # latest run 의 panel_ref_mapping_v16.json
        latest_files = sorted(sr_dir.glob("latest_v*.txt"),
                              key=lambda p: -int(p.stem.replace("latest_v","") or "0"))
        ref_map = None
        for lf in latest_files:
            run_name = lf.read_text().strip()
            rm_path = sr_dir / run_name / "panel_ref_mapping_v16.json"
            if rm_path.exists():
                ref_map = json.loads(rm_path.read_text())
                break
        panel_entry = (ref_map or {}).get("panels", {}).get(panel_label) if ref_map else None
    else:
        m = _load_panel_ref_map()
        panel_entry = m["panels"].get(panel_label)

    if not panel_entry:
        return []
    refs = []
    for i, (key, path) in enumerate(zip(panel_entry.get("ref_keys", []), panel_entry.get("ref_paths", [])), start=2):
        refs.append({
            "role": f"IMAGE {i} — {key}",
            "path": f"{user_rel}/{path}",
        })
    return refs


def zone_refs_for_class(panel_class):
    """deprecated — backwards compat. v14 부터는 zone_refs_for_panel 사용."""
    return zone_refs_for_panel("cover")


def split_detail_segments(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    detail_path = TPL_ROOT / dir_name / "detail.html"
    if not detail_path.exists():
        return []
    detail_html = detail_path.read_text(encoding="utf-8", errors="ignore")
    parts = re.split(r'(<img[^>]*>)', detail_html, flags=re.I | re.DOTALL)
    segments = []
    if parts and parts[0].strip():
        segments.append((0, parts[0]))
    panel_idx = 0
    for i in range(1, len(parts), 2):
        panel_idx += 1
        img_tag = parts[i]
        tail = parts[i + 1] if i + 1 < len(parts) else ""
        segments.append((panel_idx, img_tag + tail))
    return segments


def rewrite_segment(seg_html, panel_idx, side, t, swap_results=None, src_to_local=None,
                    t_verdict_by_panel=None):
    # template-specific verdict (per-t) — fallback to global (sofa #1)
    if t_verdict_by_panel is None:
        t_verdict_by_panel = verdict_by_panel
    soup = BeautifulSoup(seg_html, "lxml")
    body = soup.find("body")
    container = body if body else soup

    if side == "swap":
        # text substitute (panel-aware)
        for el in list(container.descendants):
            if isinstance(el, NavigableString):
                t_str = str(el).strip()
                if t_str and len(t_str) > 2:
                    for sub in text_subs_data["substitutes"]:
                        if sub["original"].strip() == t_str:
                            original = str(el)
                            leading = original[: len(original) - len(original.lstrip())]
                            trailing = original[len(original.rstrip()):]
                            el.replace_with(leading + sub["milo"] + trailing)
                            break

    for img in container.find_all("img"):
        src = img.get("src", "")
        src_clean = src.replace("devimage.hanssem.com", "image.hanssem.com")
        if src_clean.startswith("http://"):
            src_clean = "https://" + src_clean[7:]
        local = (src_to_local or {}).get(src) or (src_to_local or {}).get(src_clean) or src_clean

        if side == "swap" and swap_results:
            sname = f"panel_{panel_idx:02d}"
            cell = swap_results["by_label"].get(sname)
            verdict_info = t_verdict_by_panel.get(panel_idx, {})
            verdict = verdict_info.get("verdict", "match")
            panel_class = (cell or {}).get("panel_class") or "other"

            if verdict == "bypass":
                alt_title = verdict_info.get("alt_title", "")
                alt_body = verdict_info.get("alt_body", "")
                wrap = BeautifulSoup(f'''
<div class="bypass-card">
  <div class="bypass-tag">우회 · 사용자 제품엔 없는 기능</div>
  <div class="bypass-hanssem">한샘 원본: {verdict_info.get("hanssem_feature","")[:60]}</div>
  <h3 class="bypass-title">{alt_title}</h3>
  <p class="bypass-body">{alt_body}</p>
  <div class="panel-number-chip">{panel_idx:02d}</div>
</div>
''', "html.parser")
                img.replace_with(wrap)
                continue

            if verdict == "skip":
                wrap = BeautifulSoup(f'''
<div class="bypass-card skip">
  <div class="bypass-tag skip">정보 누락 · skip</div>
  <p class="bypass-body">사용자 제품에 정보 없음 — 건너뜀</p>
  <div class="panel-number-chip">{panel_idx:02d}</div>
</div>
''', "html.parser")
                img.replace_with(wrap)
                continue

            sname_label = sname  # for polling DOM lookup
            if cell and cell.get("final") and cell["final"].get("image"):
                f = cell["final"]
                img_url = f"{swap_results['run_dir_rel']}/{f['image']}"
                prod = f.get("product_score", "-")
                comp = f.get("composition_score", "-")
                seats = f.get("seat_count_in_B", "?")
                text_flag = f.get("text_in_image")
                struct_pres = f.get("structure_preserved", True)
                ri = f.get("reference_influences") or []
                prod_cls = score_color(prod, "prod")
                comp_cls = score_color(comp, "comp", panel_class)

                # build payload with attempts + per-attempt prompt
                attempts_meta = []
                for a in cell.get("attempts", []):
                    att_label = sname
                    att_n = a.get("attempt")
                    ko = qa_korean_by.get((att_label, att_n), {})
                    attempts_meta.append({
                        "attempt": att_n,
                        "strategy": a.get("strategy") or a.get("stage"),
                        "prod": a.get("product_score"),
                        "comp": a.get("composition_score"),
                        "seats": a.get("seat_count_in_B"),
                        "text_in_image": a.get("text_in_image"),
                        "structure_preserved": a.get("structure_preserved", True),
                        "verdict": a.get("verdict"),
                        "notes": (a.get("notes") or a.get("notes_ko") or "")[:600],
                        "notes_ko": ko.get("notes_ko", "") or a.get("notes_ko") or "",
                        "specific_failures": a.get("specific_failures") or [],
                        "specific_failures_ko": ko.get("specific_failures_ko") or [],
                        "reference_influences": a.get("reference_influences") or [],
                        "reference_influences_ko": ko.get("reference_influences_ko") or [],
                        "prompt": a.get("prompt") or "(prompt not saved in this run)",
                        "ref_count": a.get("ref_count"),
                        "image": a.get("image"),
                        "fal_url": a.get("fal_url"),
                        # v16+ 추가
                        "items_results": a.get("items_results") or [],
                        "critical_fail_count": a.get("critical_fail_count"),
                        "hallucinations": a.get("hallucinations") or [],
                        "qa_payload_rel": a.get("qa_payload_rel"),
                    })

                # panel C 실제 파일 (.jpg/.png/.gif 자동 탐색) — t 기반 동적
                _tpl_name = f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}"
                orig_files = list((TPL_ROOT / _tpl_name).glob(f"panel_{panel_idx:02d}.*"))
                orig_panel_url = (f"../templates/{_tpl_name}/{orig_files[0].name}"
                                  if orig_files else "")
                # panel_ref_mapping 키는 실제 파일명 (e.g. "panel_03.jpg", "panel_08.gif")
                panel_label = orig_files[0].name if orig_files else f"panel_{panel_idx:02d}.jpg"
                payload = {
                    "panel": panel_idx,
                    "panel_class": panel_class,
                    "strategies_used": "/".join(cell.get("strategies_used", [])),
                    "passed": cell.get("passed"),
                    "attempts": attempts_meta,
                    "refs_zone": zone_refs_for_panel(panel_label, t),
                    "run_dir_rel": swap_results["run_dir_rel"],
                    "original_panel": orig_panel_url,
                    # v16+ 추가
                    "ref_labels": cell.get("ref_labels") or [],
                    "ref_keys": cell.get("ref_keys") or [],
                    "applicable_item_ids": cell.get("applicable_item_ids") or [],
                    "best_selection_method": cell.get("best_selection_method"),
                    "judge_log": cell.get("judge_log") or [],
                }
                payload_json = json.dumps(payload, ensure_ascii=False).replace('"', "&quot;")

                ri_badge = f'<span class="score-badge score-red" title="ref influences: {len(ri)}">RI {len(ri)}</span>' if ri else ''
                wrap = BeautifulSoup(f'''
<div class="img-with-chip cell-ready" data-panel-idx="{panel_idx}" data-panel-label="{sname_label}">
  <img src="{img_url}" data-panel-idx="{panel_idx}" loading="lazy"/>
  <div class="panel-number-chip">{panel_idx:02d}</div>
  <div class="score-row">
    <span class="score-badge {prod_cls}">prod {prod}</span>
    <span class="score-badge {comp_cls}">comp {comp}</span>
        {'<span class="score-badge score-red">TEXT</span>' if text_flag else ''}
    {'<span class="score-badge score-red">STR</span>' if not struct_pres else ''}
    {ri_badge}
    <button class="payload-btn" onclick="showPayload(this)" data-payload="{payload_json}">i</button>
  </div>
</div>
''', "html.parser")
                img.replace_with(wrap)
                continue
            else:
                is_processing = sname_label in (swap_results.get("in_progress") or set())
                state_cls = "cell-processing" if is_processing else "cell-pending"
                state_label = "생성 중" if is_processing else "대기"
                wrap = BeautifulSoup(f'''
<div class="img-with-chip {state_cls}" data-panel-idx="{panel_idx}" data-panel-label="{sname_label}">
  <img src="{local}" class="orig-fallback"/>
  <div class="panel-number-chip">{panel_idx:02d}</div>
  <div class="cell-state-overlay">
    <div class="cell-spinner"></div>
    <div class="cell-state-label">{state_label}</div>
  </div>
</div>
''', "html.parser")
                img.replace_with(wrap)
                continue

        # orig side
        wrap = BeautifulSoup(f'''
<div class="img-with-chip"><img src="{local}" data-panel-idx="{panel_idx}"/><div class="panel-number-chip">{panel_idx:02d}</div></div>
''', "html.parser")
        img.replace_with(wrap)

    if body:
        return body.decode_contents()
    return str(container)


def build_panel_rows(t, swap_results):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    dir_name = f"{rank:02d}_{cat}_{gds}"
    meta_path = TPL_ROOT / dir_name / "meta.json"
    meta = json.loads(meta_path.read_text())
    # template-specific verdict by panel
    t_verdict_by_panel = _load_mismatch_for_template(TPL_ROOT / dir_name)

    src_to_local = {}
    for i, src in enumerate(meta.get("detail_imgs", []), 1):
        matches = list((TPL_ROOT / dir_name).glob(f"panel_{i:02d}.*"))
        if matches:
            local = f"../templates/{dir_name}/{matches[0].name}"
            src_to_local[src] = local
            if src.startswith("https://"):
                src_to_local["http://" + src[8:]] = local
            elif src.startswith("http://"):
                src_to_local["https://" + src[7:]] = local

    segments = split_detail_segments(t)
    rows_html = []
    panel_count = meta.get("detail_img_count") or meta.get("panel_count") or len(meta.get("detail_imgs", []))
    sections_map = assign_sections(panel_count)
    section_anchor_of = {}
    for sec_name, indices in sections_map.items():
        if sec_name == "커버" or not indices:
            continue
        section_anchor_of[indices[0]] = SECTION_SLUGS[sec_name]

    for panel_idx, seg_html in segments:
        anchor = section_anchor_of.get(panel_idx)
        anchor_attr = f'id="sec-{anchor}-{t["rank"]}"' if anchor else ""
        sec_div = ""
        if anchor:
            sec_name = [k for k, v in SECTION_SLUGS.items() if v == anchor][0]
            indices = sections_map[sec_name]
            rng = f"panel {indices[0]}" + (f"–{indices[-1]}" if len(indices) > 1 else "")
            sec_div = f'<div class="section-divider"><span class="sec-name">{sec_name}</span><span class="sec-range">{rng}</span></div>'

        orig_seg = rewrite_segment(seg_html, panel_idx, "orig", t, swap_results, src_to_local, t_verdict_by_panel)
        swap_seg = rewrite_segment(seg_html, panel_idx, "swap", t, swap_results, src_to_local, t_verdict_by_panel)

        if sec_div:
            rows_html.append(sec_div)
        rows_html.append(f'''
<div class="panel-row" {anchor_attr} data-panel-idx="{panel_idx}">
  <div class="cell orig">{orig_seg}</div>
  <div class="cell swap">{swap_seg}</div>
</div>
''')
    return "\n".join(rows_html)


def build_cover_row(t, swap_results):
    # panel_layout_maps 에 cover entry 가 없으면 cover row 자체 안 그림
    tpl_dir = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}"
    plm_path = tpl_dir / "panel_layout_maps.json"
    if plm_path.exists():
        plm = json.loads(plm_path.read_text())
        has_cover = any(p.get("panel") == "cover" for p in plm.get("panels", []))
        if not has_cover:
            return ""
    cover_src = cover_url_template(t)
    cell = swap_results["by_label"].get("cover") if swap_results else None
    if cell and cell.get("final"):
        f = cell["final"]
        img_url = f"{swap_results['run_dir_rel']}/{f['image']}"
        prod, comp, seats = f.get("product_score","-"), f.get("composition_score","-"), f.get("seat_count_in_B","?")
        prod_cls = score_color(prod, "prod")
        comp_cls = score_color(comp, "comp", "intro_hero")
        ri = f.get("reference_influences") or []
        attempts_meta = []
        for a in cell.get("attempts", []):
            ko = qa_korean_by.get(("cover", a.get("attempt")), {})
            attempts_meta.append({
                "attempt": a.get("attempt"), "strategy": a.get("strategy") or a.get("stage"),
                "prod": a.get("product_score"), "comp": a.get("composition_score"),
                "seats": a.get("seat_count_in_B"), "verdict": a.get("verdict"),
                "notes": (a.get("notes") or a.get("notes_ko") or "")[:600],
                "notes_ko": ko.get("notes_ko", "") or a.get("notes_ko") or "",
                "specific_failures": a.get("specific_failures") or [],
                "specific_failures_ko": ko.get("specific_failures_ko") or [],
                "reference_influences": a.get("reference_influences") or [],
                "reference_influences_ko": ko.get("reference_influences_ko") or [],
                "prompt": a.get("prompt") or "(prompt not saved)",
                "text_in_image": a.get("text_in_image"),
                "structure_preserved": a.get("structure_preserved", True),
                "image": a.get("image"),
                "ref_count": a.get("ref_count"),
                # v16+ 추가
                "items_results": a.get("items_results") or [],
                "critical_fail_count": a.get("critical_fail_count"),
                "hallucinations": a.get("hallucinations") or [],
                "qa_payload_rel": a.get("qa_payload_rel"),
            })
        payload = {
            "panel": "cover", "panel_class": "intro_hero",
            "strategies_used": "/".join(cell.get("strategies_used", [])),
            "passed": cell.get("passed"),
            "attempts": attempts_meta,
            "refs_zone": zone_refs_for_panel("cover", t),
            "run_dir_rel": swap_results["run_dir_rel"],
            "original_panel": cover_src,
            "ref_labels": cell.get("ref_labels") or [],
            "ref_keys": cell.get("ref_keys") or [],
            "applicable_item_ids": cell.get("applicable_item_ids") or [],
            "best_selection_method": cell.get("best_selection_method"),
            "judge_log": cell.get("judge_log") or [],
        }
        payload_json = json.dumps(payload, ensure_ascii=False).replace('"', "&quot;")
        ri_badge = f'<span class="score-badge score-red">RI {len(ri)}</span>' if ri else ''
        swap_html = f'''
<div class="img-with-chip cover-wrap cell-ready" data-panel-label="cover">
  <img class="cover-img" src="{img_url}"/>
  <div class="panel-number-chip">00</div>
  <div class="score-row">
    <span class="score-badge {prod_cls}">prod {prod}</span>
    <span class="score-badge {comp_cls}">comp {comp}</span>
        {ri_badge}
    <button class="payload-btn" onclick="showPayload(this)" data-payload="{payload_json}">i</button>
  </div>
</div>
'''
    else:
        is_processing = "cover" in (swap_results.get("in_progress") or set()) if swap_results else False
        state_cls = "cell-processing" if is_processing else "cell-pending"
        state_label = "생성 중" if is_processing else "대기"
        swap_html = f'''
<div class="img-with-chip cover-wrap {state_cls}" data-panel-label="cover">
  <img class="cover-img orig-fallback" src="{cover_src}"/>
  <div class="panel-number-chip">00</div>
  <div class="cell-state-overlay">
    <div class="cell-spinner"></div>
    <div class="cell-state-label">{state_label}</div>
  </div>
</div>
'''
    user_name = _user_product_name_for_rank(t['rank'])
    return f'''
<div class="panel-row cover-row" id="sec-cover-{t['rank']}">
  <div class="cell orig">
    <div class="section-divider cover-divider"><span class="sec-name">커버</span><span class="sec-range">1:1 대표</span></div>
    <div class="img-with-chip cover-wrap"><img class="cover-img" src="{cover_src}"/><div class="panel-number-chip">00</div></div>
  </div>
  <div class="cell swap">
    <div class="section-divider cover-divider"><span class="sec-name">커버 swap</span><span class="sec-range">{user_name[:30]}</span></div>
    {swap_html}
  </div>
</div>
'''


def build_tabs_bar(rank, sections_map):
    btns = []
    first_active = False
    for sec in SECTIONS:
        slug = SECTION_SLUGS[sec]
        has = True if sec == "커버" else bool(sections_map.get(sec))
        cls = "tab" + ("" if has else " disabled")
        if has and not first_active:
            cls += " active"
            first_active = True
        attrs = f'onclick="scrollToSection({rank}, \'{slug}\')"' if has else "disabled"
        btns.append(f'<button class="{cls}" data-slug="{slug}" {attrs}>{sec}</button>')
    return "\n".join(btns)


def build_zone_inputs(t=None):
    """이미지 zone — t 기반 동적 user_product. t 없으면 #1 milo (legacy)."""
    rank = t["rank"] if t else 1
    user_dir = _user_dir_for_rank(rank)
    if not user_dir:
        return ""
    use_prod_dir = user_dir / "use_product"
    use_prod = f"../user_products/{user_dir.name}/use_product"

    # vision 분류 (96번 출력) 로드 — 카테고리 무관 generic
    cls_path = use_prod_dir / "classification.json"
    by_cat = {}
    if cls_path.exists():
        cdata = json.loads(cls_path.read_text())
        for it in cdata.get("items", []):
            by_cat.setdefault(it["category"], []).append(it)

    def files_for(cat):
        out = []
        for it in by_cat.get(cat, []):
            fp = use_prod_dir / it["filename"]
            if fp.exists():
                out.append((f"{use_prod}/{it['filename']}", f"{it['filename']} · {it.get('subject','')}"))
        return out

    main_files = files_for("main_view")
    detail_files = files_for("detail_close_up")
    color_var_files = files_for("color_variant")
    color_swatch_files = files_for("color_swatch")
    mat_files = files_for("material")

    zones_data = [
        ("📷 MAIN VIEW (메인 전체샷)", main_files),
        ("🔎 DETAIL CLOSE-UP (부분 디테일)", detail_files),
        ("📦 COLOR VARIANT (다른 컬러 전체샷)", color_var_files),
        ("🎨 COLOR SWATCH (컬러 견본)", color_swatch_files),
        ("🧵 MATERIAL (소재 close-up)", mat_files),
    ]
    out = ""
    for title, files in zones_data:
        if not files:
            continue
        thumbs = "".join(
            f'<div class="zone-thumb" onclick="showImageModal(\'{f}\', \'{label}\')">'
            f'<img src="{f}" loading="lazy" alt="{label}"/>'
            f'<div class="thumb-label">{label}</div></div>'
            for f, label in files
        )
        cls = "zone-block tier2" if "Tier 2" in title or "MASTER" in title else "zone-block"
        out += (f'<div class="{cls}">'
                f'<div class="zone-label">{title} <span class="zone-count">{len(files)}장</span></div>'
                f'<div class="zone-thumbs">{thumbs}</div></div>')
    return out


def build_text_dense_v3(p):
    """v3 dense schema — paragraph 형식 큰 textarea."""
    sp = p.get("spec", {}) or {}
    fd = p.get("feature_descriptions", {}) or {}
    colors = p.get("color_options_detail", []) or []
    models = p.get("model_options", []) or []
    selected_model = next((m for m in models if m.get("selected")), models[0] if models else {})
    colors_str = "\n\n".join(f"[{c.get('name','?')}] {c.get('description','')}" for c in colors)
    models_str = " / ".join(f"{m.get('name','')}{'★' if m.get('selected') else ''} {m.get('dimensions','')}" for m in models)

    fields = [
        ("📌 제품명", "product_name", p.get("product_name", ""), False),
        ("📐 제원 (수치)", "spec_size",
         f"{sp.get('width_cm','?')}×{sp.get('depth_cm','?')}×{sp.get('height_cm','?')}cm · "
         f"좌방석 깊이 {sp.get('seat_depth_cm','?')}cm · 좌방석 높이 {sp.get('seat_height_cm','?')}cm · "
         f"팔걸이 높이 {sp.get('arm_height_cm','?')}cm · 다리 {sp.get('leg_height_cm','?')}cm" +
         (f" · 무게 {sp.get('weight_kg','')}kg" if sp.get('weight_kg') else "") +
         (f" · 원산지 {sp.get('origin','')}" if sp.get('origin') else ""), False),
        ("🌟 제품 소개 (전체 — dense paragraph)", "intro_full", p.get("intro_full", ""), True),
        ("🖼 실루엣 (전체 인상)", "overall_silhouette", fd.get("overall_silhouette", ""), True),
        ("💪 팔걸이 상세", "arms_detail", fd.get("arms_detail", ""), True),
        ("🛋 등쿠션 상세", "back_cushions_detail", fd.get("back_cushions_detail", ""), True),
        ("💺 좌방석 상세", "seat_cushions_detail", fd.get("seat_cushions_detail", ""), True),
        ("🦵 다리 상세 (개수/위치/모양/마감 정확히)", "legs_detail", fd.get("legs_detail", ""), True),
        ("🧵 패브릭 텍스처", "fabric_texture", fd.get("fabric_texture", ""), True),
        ("✂️ 시접 (좌방석/등쿠션/팔걸이 차이)", "seam_styles", fd.get("seam_styles", ""), True),
        ("🔗 쿠션 연결 방식", "cushion_connection", fd.get("cushion_connection", ""), True),
        ("🪵 프레임 구조", "frame_structure", fd.get("frame_structure", ""), True),
        ("🎨 컬러 옵션 상세", "color_options_detail", colors_str, True),
        ("📦 모델 옵션 (선택)", "model_options", models_str, False),
        ("✅ 인증", "certifications", p.get("certifications_full", ""), True),
        ("🚚 배송 / 보증", "delivery_warranty", p.get("delivery_warranty", ""), True),
        ("🌟 종합 묘사 (이 글만으로 그림을 그릴 수 있을 정도)", "comprehensive", p.get("comprehensive_paragraph", ""), True),
    ]

    out = '<div class="dense-input-list">'
    for label, key, val, is_textarea in fields:
        val_str = str(val) if val is not None else ""
        if is_textarea:
            rows = max(3, min(10, val_str.count("\n") + len(val_str) // 80 + 2))
            out += f'<div class="dense-input-field"><label>{label}</label><textarea name="{key}" rows="{rows}">{val_str}</textarea></div>'
        else:
            out += f'<div class="dense-input-field"><label>{label}</label><input type="text" name="{key}" value="{val_str}"/></div>'
    out += '</div>'
    return out


def build_text_input_fields():
    """텍스트 입력 영역 — dense paragraph 형식 (글만 보고도 그림 그릴 수 있게).
    v3 schema (dense) 우선, v2 fallback."""
    p = product_input or {}

    # v3 dense schema
    if "comprehensive_paragraph" in p or "feature_descriptions" in p:
        return build_text_dense_v3(p)

    # fallback to v2-style fields
    intro = p.get("intro", {}) or {}
    sp = p.get("spec", {}) or {}
    feat = p.get("features", {}) or {}
    models = p.get("model_options", []) or []
    colors = p.get("color_options", []) or []
    delivery = p.get("delivery_info", {}) or {}
    guidance = p.get("panel_specific_guidance", {}) or {}

    selected_model = next((m for m in models if m.get("selected")), models[0] if models else {})
    color_names = [c.get("name", "") for c in colors]
    model_names = " / ".join(f"{m.get('name','')}{'★' if m.get('selected') else ''}" for m in models)
    certs_str = ", ".join(feat.get("certifications", []) or [])
    features_list = feat.get("key_features_korean", []) or []
    features_str = "\n".join(f"· {f}" for f in features_list)
    delivery_notes = "\n".join(f"· {n}" for n in (delivery.get("notes") or [])[:5])

    sections = [
        ("📌 기본 정보", [
            ("제품명", "product_name", p.get("product_name", "")),
            ("제품 소개 — 헤드", "intro_headline", intro.get("headline", "")),
            ("제품 소개 — 본문 (자세히)", "intro_body", intro.get("body", "")),
        ]),
        ("📐 제원 (수치)", [
            ("가로 (cm)", "width", sp.get("width_cm", "")),
            ("깊이 (cm)", "depth", sp.get("depth_cm", "")),
            ("높이 (cm)", "height", sp.get("height_cm", "")),
            ("좌방석 깊이 (cm)", "seat_depth", sp.get("seat_depth_cm", "")),
            ("좌방석 높이 (cm)", "seat_height", sp.get("seat_height_cm", "")),
            ("팔걸이 높이 (cm)", "arm_height", sp.get("arm_height_cm", "")),
            ("다리 높이 (cm)", "leg_height", sp.get("leg_height_cm", "")),
            ("무게 (kg)", "weight", sp.get("weight_kg", "")),
            ("원산지", "origin", sp.get("origin", "")),
        ]),
        ("✨ 제품 특징 — 쿠션/시접", [
            ("좌방석 firmness", "seat_firmness", feat.get("seat_cushion_firmness", "")),
            ("등쿠션 firmness", "back_firmness", feat.get("back_cushion_firmness", "")),
            ("좌방석 내장재 (상세)", "seat_fill", feat.get("seat_cushion_fill", "")),
            ("등쿠션 내장재 (상세)", "back_fill", feat.get("back_cushion_fill", "")),
            ("좌방석 시접 모양", "seam_seat", feat.get("seam_style_seat", "")),
            ("팔걸이 시접 모양", "seam_arm", feat.get("seam_style_arm", "")),
            ("시접 차이 설명", "seam_diff", feat.get("seam_difference", "")),
            ("쿠션-팔걸이 연결?", "cushion_arm_connected", str(feat.get("cushion_connected_to_arm", ""))),
            ("쿠션 연결 설명", "cushion_conn_note", feat.get("cushion_connection_note", "")),
        ]),
        ("🪵 프레임 / 다리", [
            ("마감재", "upholstery", feat.get("upholstery", "")),
            ("프레임", "frame", feat.get("frame", "")),
            ("다리 개수", "legs_count", feat.get("legs_count", "")),
            ("다리 위치", "legs_position", feat.get("legs_position", "")),
            ("다리 모양", "legs_shape", feat.get("legs_shape", "")),
            ("다리 색상", "legs_color", feat.get("legs_color", "")),
        ]),
        ("🎨 옵션 / 인증", [
            ("컬러 옵션", "colors", " / ".join(color_names)),
            ("모델 옵션 (선택: " + selected_model.get("name", "?") + ")", "models", model_names),
            ("인증", "certs", certs_str),
            ("커버 분리 세탁", "cover_removable", str(feat.get("cover_removable", ""))),
            ("헤드레스트", "has_headrest", str(feat.get("has_headrest", ""))),
            ("리클라이너", "has_recliner", str(feat.get("has_recliner", ""))),
            ("USB/컨트롤", "has_usb", str(feat.get("has_usb_or_control", ""))),
        ]),
        ("🚚 배송 / 보증", [
            ("배송 방식", "delivery_method", delivery.get("delivery_method", "")),
            ("품질 보증", "warranty", delivery.get("warranty", "")),
            ("배송 주의사항", "delivery_notes", delivery_notes),
        ]),
        ("📋 panel별 가이드 (자동 생성)", [
            ("사이즈 chart overlay 텍스트", "guide_size", guidance.get("size_chart_overlay_text", "")),
            ("좌방석 firmness 위치", "guide_seat_firm", guidance.get("firmness_chart_korean", {}).get("seat", "")),
            ("등쿠션 firmness 위치", "guide_back_firm", guidance.get("firmness_chart_korean", {}).get("back", "")),
            ("라인업 한국어", "guide_lineup", guidance.get("lineup_korean", "")),
        ]),
        ("🌟 핵심 특징 (가능한 한 풍부히)", [
            (f"key features ({len(features_list)}개)", "features_all", features_str),
        ]),
    ]

    out = ""
    for sec_title, fields in sections:
        out += f'<div class="text-section"><div class="text-section-h">{sec_title}</div><div class="input-fields-grid">'
        for label, key, val in fields:
            val_str = str(val) if val is not None else ""
            is_textarea = len(val_str) > 40 or "\n" in val_str
            if is_textarea:
                out += f'<div class="input-field wide"><label>{label}</label><textarea name="{key}" rows="3">{val_str}</textarea></div>'
            else:
                out += f'<div class="input-field"><label>{label}</label><input type="text" name="{key}" value="{val_str}"/></div>'
        out += '</div></div>'
    return out


def build_process_card(t, swap_results):
    rank = t["rank"]
    tpl_price = t.get("price")
    tpl_price_str = f"{tpl_price:,}원" if tpl_price else ""
    is_done = swap_results is not None
    marker = (swap_results or {}).get("marker", "")
    run_tag = ""
    if marker.startswith("latest_v"):
        run_tag = f' · {marker.replace("latest_","").replace(".txt","")}'
    badge = f'<span class="badge ready"><b>실행 완료{run_tag}</b></span>' if is_done else '<span class="badge"><b>대기</b></span>'

    dims = spec.get("dimensions", {}) or {}
    mat = spec.get("material", {}) or {}
    colors = spec.get("colors") or []
    seat_n = spec.get("seat_count", 2)
    features = spec.get("key_features", [])

    auto_req = (
        f"제품: {spec.get('product_name')}. 사이즈 {dims.get('width_cm','?')}×{dims.get('depth_cm','?')}×{dims.get('height_cm','?')}cm. "
        f"패브릭 {mat.get('upholstery','')}, 컬러 {', '.join(colors)}. {seat_n}인용 STRICT."
    )

    if swap_results:
        cells = swap_results["summary"]["cells"]
        wall = swap_results["summary"].get("wall_seconds", 0)
        n_pass = sum(1 for c in cells if c["passed"])
        bypass_n = sum(1 for r in mismatch["resolutions"] if r["verdict"] == "bypass")
        skip_n = sum(1 for r in mismatch["resolutions"] if r["verdict"] == "skip")
        status_col = f'''
<div class="proc-h">상태</div>
<div class="status-line">시간 <b>{wall:.0f}s</b></div>
<div class="status-line">passer <b>{n_pass}/{len(cells)}</b></div>
<div class="status-line">우회 <b>{bypass_n}</b> · skip <b>{skip_n}</b></div>
<div class="status-line legend"><span class="dot green"></span>≥99 <span class="dot amber"></span>95~98 <span class="dot red"></span>&lt;95</div>
'''
    else:
        status_col = '<div class="proc-h">상태</div><div class="status-line">시간 <b>—</b></div>'

    # 사용자 제품 URL (product_input.json 또는 url.txt)
    user_url = ""
    user_name_full = _user_product_name_for_rank(rank)
    user_dir = _user_dir_for_rank(rank)
    if user_dir:
        for fn in ('product_input.json', 'product_input_v3.json'):
            pi = user_dir / fn
            if pi.exists():
                try:
                    pidata = json.loads(pi.read_text())
                    user_url = pidata.get('_source_url', '') or ''
                except Exception:
                    pass
                break
        if not user_url:
            url_f = user_dir / 'url.txt'
            if url_f.exists():
                user_url = url_f.read_text().strip().splitlines()[0].strip()

    user_link = (f'<a href="{user_url}" target="_blank" class="orig-link user-link">사용자 제품 ↗</a>'
                 if user_url else '')

    return f'''
<details class="process-card">
  <summary>
    <span class="proc-title">공정 설정</span>
    <span class="proc-summary">
      <span class="badge tpl-badge">템플릿 <b>#{rank} {t.get('category')}</b> · {t['name'][:24]}{'…' if len(t['name'])>24 else ''}</span>
      <span class="badge"><b>GPT image</b> · 4-layer + bidirectional QA</span>
      {badge}
    </span>
    <span class="proc-toggle">▾</span>
  </summary>
  <div class="proc-content">
    <div class="tpl-info-row">
      <div class="proc-h">한샘 레퍼런스 ↔ 사용자 제품</div>
      <div class="ref-vs-user">
        <div class="ref-col">
          <div class="ref-label">레퍼런스 (한샘)</div>
          <div class="tpl-name">{t['name']}</div>
          <div class="tpl-meta">
            <span class="cat-tag">{t.get('category')}</span><span>{t.get('brand','')}</span>
            <span>★ {t.get('reviewCnt',0)} 리뷰</span><span>{tpl_price_str}</span>
            <a href="{t['url']}" target="_blank" class="orig-link">한샘 상세 ↗</a>
          </div>
        </div>
        <div class="ref-col">
          <div class="ref-label">적용 (사용자 제품)</div>
          <div class="tpl-name">{user_name_full[:50]}</div>
          <div class="tpl-meta">
            {user_link if user_link else '<span style="color:#9ca3af">(URL 없음)</span>'}
          </div>
        </div>
      </div>
    </div>
    <div class="proc-h">📷 이미지 입력 — zone 분리 (담당자 업로드)</div>
    <div class="zone-row">{build_zone_inputs(t)}</div>

    <div class="proc-h" style="margin-top:20px;">📝 텍스트 입력 — 필드별 분리 (한샘 페이지 vision 자동 추출 · 담당자 수정 가능)</div>
    {build_text_input_fields()}

    <div class="proc-h" style="margin-top:20px;">📊 상태</div>
    <div class="status-row">{status_col}</div>
  </div>
</details>
'''


cover_imgs = {t["gdsNo"]: cover_url_template(t) for t in data["top6"]}


def chip(t):
    rank, cat, gds = t["rank"], t["category"], t["gdsNo"]
    name_short = t["name"][:24] + ("…" if len(t["name"]) > 24 else "")
    swap = get_swap_results(t)
    ready = '<span class="chip-ready done">✓</span>' if swap else ""
    return f'''
<button class="chip {'selected' if rank == 1 else ''}" data-rank="{rank}" onclick="selectTpl({rank})">
  {ready}<span class="chip-rank">#{rank}</span>
  <img class="chip-cover" src="{cover_imgs[gds]}"/>
  <span class="chip-meta"><span class="chip-cat">{cat}</span><span class="chip-name">{name_short}</span></span>
</button>'''


def view(t):
    rank = t["rank"]
    is_first = rank == 1
    swap_results = get_swap_results(t)  # 모든 active template 에 대해 swap 결과 lookup
    meta_path = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}/meta.json"
    meta = json.loads(meta_path.read_text())
    panel_count = meta.get("detail_img_count") or meta.get("panel_count") or len(meta.get("detail_imgs", []))
    sections_map = assign_sections(panel_count)
    cover_row = build_cover_row(t, swap_results)
    panel_rows = build_panel_rows(t, swap_results)

    return f'''
<div class="view {'active' if is_first else ''}" data-rank="{rank}">
  {build_process_card(t, swap_results)}
  <div class="tabs-bar"><div class="tabs">{build_tabs_bar(rank, sections_map)}</div></div>
  <div class="dual-grid">
    <div class="dual-header">
      <div class="dual-h-left">원본 한샘 detail</div>
      <div class="dual-h-right">swap · {_user_product_name_for_rank(rank)[:40]} · GPT</div>
    </div>
    {cover_row}
    {panel_rows}
  </div>
</div>
'''


# 활성화된 template 만 표시 — swap_results 폴더가 존재하거나 #1 (완료) 인 경우
def _is_active(t):
    sr = TPL_ROOT / f"{t['rank']:02d}_{t['category']}_{t['gdsNo']}" / "swap_results"
    return t['rank'] == 1 or sr.exists()

ACTIVE_TOP = [t for t in data["top6"] if _is_active(t)]
chips_html = "\n".join(chip(t) for t in ACTIVE_TOP)
views_html = "\n".join(view(t) for t in ACTIVE_TOP)

# v16+ progress: rank 1 (현재 active) 의 summary.progress 추출
_progress = None
for t in data["top6"]:
    if t["rank"] != 1:
        continue
    sr = get_swap_results(t)
    if sr and sr.get("summary", {}).get("progress"):
        _progress = sr["summary"]["progress"]
        _progress["run"] = sr["summary"].get("run", "?")
        _progress["wall_seconds"] = sr["summary"].get("wall_seconds", 0)
    break

_is_complete = bool(_progress and _progress.get("is_complete"))
# polling JS가 대신 처리 — meta refresh 사용 안 함
_meta_refresh = ""
# rank 1 run_dir_rel 을 JS에 노출
_rank1_summary_url = ""
_rank1_run_dir_rel = ""
for t in data["top6"]:
    if t["rank"] != 1:
        continue
    sr = get_swap_results(t)
    if sr:
        # run_dir_rel = "../templates/.../swap_results/<run_name>/gpt_image"
        # summary.json은 run_name 디렉토리 직속
        rdr = sr["run_dir_rel"]
        _rank1_summary_url = rdr.rsplit("/", 1)[0] + "/summary.json"
        _rank1_run_dir_rel = rdr  # gpt_image 폴더 — image src에 사용
    break

# 진행 중일 때만 banner 표시 — 완료되면 숨김 (사용자 요청: 화면 가리는 banner 제거)
_progress_banner = ""
if _progress and not _is_complete:
    in_prog = _progress.get("in_progress") or []
    _progress_banner = (
        f'<div class="prog-banner prog-running">'
        f'<span class="prog-dot">●</span> 진행 중 · {_progress.get("done",0)}/{_progress.get("total",0)} · '
        f'대기: {", ".join(in_prog[:5])}{"..." if len(in_prog) > 5 else ""}'
        f'</div>'
    )

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
{_meta_refresh}
<title>가구 detail 템플릿 swap — v17 (streaming)</title>
<link rel="stylesheet" href="https://res.remodeling.hanssem.com/font/pretendard/pretendard.css"/>
<style>
  :root {{
    --bg: #fff; --bg-alt: #f4f4f6;
    --fg: #1a1a1a; --fg-soft: #555; --muted: #888;
    --line: #e5e5e5; --line-soft: #efefef;
    --accent: #ff7a00; --accent-soft: #fff5ec;
    --good: #16a34a; --warn: #f59e0b; --bad: #dc2626;
    --topbar-h: 56px; --tabs-h: 50px;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: "Pretendard", -apple-system, system-ui, sans-serif;
    background: var(--bg-alt); color: var(--fg); -webkit-font-smoothing: antialiased;
    font-size: 14px; line-height: 1.5; }}
  .topbar {{ position: sticky; top: 0; z-index: 100; background: #fff; border-bottom: 1px solid var(--line); padding: 12px 24px; height: var(--topbar-h); }}
  .topbar-row {{ display: flex; align-items: center; gap: 16px; max-width: 1600px; margin: 0 auto; overflow-x: auto; }}
  .topbar h1 {{ margin: 0; font-size: 13px; font-weight: 600; color: var(--fg-soft); white-space: nowrap; }}
  .chips {{ display: flex; gap: 8px; flex: 1; }}
  .chip {{ position: relative; display: flex; align-items: center; gap: 8px; padding: 6px 14px 6px 6px; border: 1px solid var(--line); background: #fff; border-radius: 999px; cursor: pointer; font-family: inherit; font-size: 12px; color: #555; white-space: nowrap; }}
  .chip.selected {{ border-color: var(--fg); background: var(--fg); color: #fff; }}
  .chip-ready {{ position: absolute; top: 2px; right: 4px; color: var(--good); font-size: 10px; font-weight: 700; }}
  .chip-cover {{ width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }}
  .chip-rank {{ font-weight: 700; color: var(--accent); }}
  .chip-meta {{ display: flex; flex-direction: column; align-items: flex-start; line-height: 1.15; }}
  .chip-cat {{ font-size: 10px; opacity: 0.7; }}
  .chip-name {{ font-size: 11px; }}

  .view {{ display: none; padding: 24px 32px; max-width: 1600px; margin: 0 auto; }}
  .view.active {{ display: block; }}

  /* Process card */
  .process-card {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; margin-bottom: 16px; overflow: hidden; }}
  .process-card > summary {{ list-style: none; cursor: pointer; padding: 14px 20px; display: flex; align-items: center; gap: 14px; background: #fff; }}
  .process-card > summary::-webkit-details-marker {{ display: none; }}
  .proc-title {{ font-size: 13px; font-weight: 600; }}
  .proc-summary {{ display: flex; gap: 6px; flex-wrap: wrap; flex: 1; align-items: center; }}
  .badge {{ font-size: 11px; color: var(--muted); padding: 3px 8px; background: #f4f4f6; border-radius: 4px; white-space: nowrap; }}
  .badge b {{ color: var(--fg); font-weight: 600; margin-left: 4px; }}
  .badge.ready {{ background: #e6fde8; color: #167a32; }}
  .badge.ready b {{ color: #105823; }}
  .tpl-badge {{ background: #fff5ec; color: #b04a00; }}
  .tpl-badge b {{ color: #7a3300; }}
  .proc-toggle {{ font-size: 14px; color: var(--muted); transition: transform 0.2s; }}
  .process-card[open] .proc-toggle {{ transform: rotate(180deg); }}
  .process-card[open] > summary {{ border-bottom: 1px solid var(--line); }}
  .proc-content {{ padding: 20px; }}
  .tpl-info-row {{ padding-bottom: 16px; margin-bottom: 16px; border-bottom: 1px solid var(--line-soft); }}
  .tpl-name {{ font-size: 16px; font-weight: 600; margin-top: 4px; }}
  .tpl-meta {{ display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: var(--fg-soft); margin-top: 6px; }}
  .cat-tag {{ background: #efefef; padding: 2px 8px; border-radius: 4px; color: #444; font-weight: 500; }}
  .orig-link {{ color: #2563eb; text-decoration: none; }}
  .orig-link:hover {{ text-decoration: underline; }}
  .user-link {{ color: #059669; }}
  .ref-vs-user {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 6px; }}
  .ref-col {{ padding: 12px; background: var(--bg-alt); border: 1px solid var(--line-soft); border-radius: 6px; }}
  .ref-label {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); font-weight: 600; margin-bottom: 4px; }}
  .proc-grid {{ display: grid; grid-template-columns: 1.1fr 1.7fr 1fr; gap: 24px; }}
  .proc-col {{ display: flex; flex-direction: column; gap: 8px; min-width: 0; }}
  .proc-h {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; }}
  .zone-block {{ padding: 10px 12px; background: var(--bg-alt); border: 1px solid var(--line); border-radius: 8px; margin-top: 8px; }}
  .zone-label {{ font-size: 12px; font-weight: 600; margin-bottom: 6px; }}
  .zone-count {{ font-size: 10px; color: var(--muted); font-weight: 400; margin-left: 4px; }}
  .zone-thumbs {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 6px; }}
  .zone-thumb {{ position: relative; aspect-ratio: 1/1; cursor: zoom-in; transition: transform 0.15s; }}
  .zone-thumb:hover {{ transform: scale(1.04); }}
  .zone-thumb img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 4px; border: 1px solid var(--line); background: #fff; }}
  .thumb-label {{ position: absolute; bottom: 2px; left: 2px; right: 2px;
    font-size: 9px; padding: 1px 4px; background: rgba(0,0,0,0.6); color: #fff;
    border-radius: 3px; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

  /* zone row — auto-fit (multi-tier 패턴) */
  .zone-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-top: 8px; }}

  /* Tier 2 — AI 합성 시트 (강조) */
  .zone-block.tier2 {{
    background: linear-gradient(135deg, #fffaf0, #fff5e6);
    border: 1px solid var(--accent);
  }}
  .zone-block.tier2 .zone-label {{ color: var(--accent); font-weight: 700; }}
  .zone-block.tier2 .zone-thumbs {{ grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }}
  .zone-block.tier2 .thumb-label {{ background: rgba(176, 74, 0, 0.85); }}

  /* placeholder zone (대기 중) */
  .zone-block.placeholder {{
    background: #f9f9fa; border-style: dashed; border-color: #d4d4d8;
  }}
  .zone-block.placeholder .zone-label {{ color: var(--muted); }}
  .zone-placeholder {{
    padding: 16px 12px; font-size: 11px; color: var(--muted);
    line-height: 1.55; font-style: italic; text-align: center;
  }}

  /* 텍스트 입력 — 섹션별 그룹 */
  .text-section {{ margin-top: 14px; padding: 14px; background: #fafafa;
    border: 1px solid var(--line); border-radius: 10px; }}
  .text-section-h {{ font-size: 12px; font-weight: 700; color: var(--fg);
    margin-bottom: 10px; letter-spacing: -0.01em; }}

  /* 텍스트 입력 필드 grid */
  .input-fields-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px 14px;
  }}
  .input-field.wide {{ grid-column: 1 / -1; }}
  .input-field {{ display: flex; flex-direction: column; gap: 4px; }}
  .input-field label {{ font-size: 10px; color: var(--muted); font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.04em; }}
  .input-field input, .input-field textarea {{
    width: 100%; padding: 6px 10px; border: 1px solid var(--line); border-radius: 6px;
    font-family: inherit; font-size: 12px; background: #fafafa; line-height: 1.5;
    resize: vertical;
  }}
  .input-field textarea {{ min-height: 60px; }}

  /* dense paragraph 입력 — single column, wide textareas */
  .dense-input-list {{
    display: grid; grid-template-columns: 1fr; gap: 14px;
    margin-top: 10px;
  }}
  .dense-input-field {{
    display: flex; flex-direction: column; gap: 6px;
    padding: 12px 14px; background: #fafafa;
    border: 1px solid var(--line); border-radius: 8px;
  }}
  .dense-input-field label {{
    font-size: 12px; font-weight: 700; color: var(--fg);
    letter-spacing: -0.01em;
  }}
  .dense-input-field input,
  .dense-input-field textarea {{
    width: 100%; padding: 8px 12px;
    border: 1px solid var(--line); border-radius: 6px;
    background: #fff; font-family: inherit; font-size: 12px;
    line-height: 1.65; color: var(--fg);
    resize: vertical;
  }}
  .dense-input-field textarea {{ min-height: 80px; }}
  .dense-input-field textarea:focus,
  .dense-input-field input:focus {{
    outline: none; border-color: var(--accent);
    background: #fffdf9;
  }}

  .status-row {{ display: flex; gap: 16px; align-items: flex-start; }}
  .status-row > div {{ flex: 1; }}
  .user-prompt {{ width: 100%; min-height: 100px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 8px; resize: vertical; font-family: inherit; font-size: 12px; background: #fafafa; line-height: 1.55; }}
  .spec-details {{ margin-top: 10px; border: 1px solid var(--line); border-radius: 8px; background: #fafafa; }}
  .spec-details summary {{ cursor: pointer; padding: 8px 12px; font-size: 11px; color: var(--fg-soft); font-weight: 600; outline: none; }}
  .spec-details summary::-webkit-details-marker {{ display: none; }}
  .spec-list {{ padding: 4px 12px 12px; font-size: 11px; color: var(--fg-soft); line-height: 1.8; }}
  .spec-list b {{ color: var(--fg); font-weight: 600; margin-right: 4px; }}
  .status-line {{ font-size: 12px; color: var(--muted); margin-bottom: 4px; }}
  .status-line b {{ color: var(--fg); font-weight: 600; margin-left: 4px; }}
  .status-line.legend {{ font-size: 10px; }}
  .dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin: 0 3px 0 6px; vertical-align: -1px; }}
  .dot.green {{ background: var(--good); }} .dot.amber {{ background: var(--warn); }} .dot.red {{ background: var(--bad); }}

  .tabs-bar {{ position: sticky; top: var(--topbar-h); z-index: 30; background: var(--bg-alt); padding: 4px 0 0; height: calc(var(--tabs-h) + 4px); }}
  .tabs {{ display: flex; background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 0 12px; overflow-x: auto; }}
  .tab {{ padding: 12px 18px; background: transparent; border: none; border-bottom: 2px solid transparent; margin-bottom: -1px; font-family: inherit; font-size: 13px; color: #666; cursor: pointer; white-space: nowrap; }}
  .tab.active {{ color: var(--fg); border-bottom-color: var(--fg); font-weight: 600; }}
  .tab.disabled {{ opacity: 0.3; cursor: not-allowed; }}

  /* === Dual Grid === */
  .dual-grid {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; margin-top: 12px; overflow: hidden; }}
  .dual-header {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-bottom: 1px solid var(--line); background: #fafafa;
    position: sticky; top: calc(var(--topbar-h) + var(--tabs-h)); z-index: 20; }}
  .dual-h-left, .dual-h-right {{ padding: 12px 20px; font-size: 12px; font-weight: 600; color: #444; }}
  .dual-h-left {{ border-right: 1px solid var(--line); }}

  .section-divider {{
    display: flex; align-items: baseline; gap: 12px;
    padding: 20px 24px 10px; background: linear-gradient(to bottom, #fafafa, #fff);
    border-top: 1px solid var(--line-soft);
    scroll-margin-top: calc(var(--topbar-h) + var(--tabs-h) + 40px);
  }}
  .section-divider .sec-name {{ font-size: 13px; font-weight: 700; padding: 4px 12px;
    background: var(--accent-soft); border-left: 3px solid var(--accent); border-radius: 0 4px 4px 0; }}
  .section-divider .sec-range {{ font-size: 10px; color: var(--muted); font-family: ui-monospace, monospace; }}
  .section-divider.cover-divider .sec-name {{ background: #e8f4ff; border-left-color: #2563eb; }}

  .panel-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0;
    border-bottom: 1px solid var(--line-soft);
    scroll-margin-top: calc(var(--topbar-h) + var(--tabs-h) + 40px); }}
  .panel-row:last-child {{ border-bottom: none; }}
  .cell {{ padding: 20px 24px; min-width: 0; overflow: hidden; }}
  .cell.orig {{ border-right: 1px solid var(--line); background: #fff; }}
  .cell.swap {{ background: #fafafa; }}
  /* === 한샘 detail HTML inline style 보존 — 우리 override 최소화 === */
  .cell img {{ max-width: 100%; display: block; }}
  .cell iframe {{ max-width: 100%; display: block; }}
  .cover-row .cell .cover-img {{ max-width: 480px; margin: 0 auto; aspect-ratio: 1/1; object-fit: contain; }}

  .img-with-chip {{ position: relative; display: inline-block; max-width: 100%; }}
  .img-with-chip img {{ display: block; }}
  .panel-number-chip {{
    position: absolute; top: 8px; left: 8px;
    min-width: 22px; height: 22px; padding: 0 7px; border-radius: 11px;
    background: rgba(0,0,0,0.35); color: rgba(255,255,255,0.92);
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 600; font-family: ui-monospace, Menlo, monospace;
    z-index: 5; pointer-events: none; backdrop-filter: blur(4px);
  }}
  .score-row {{ position: absolute; bottom: 8px; left: 8px; right: 8px; display: flex; gap: 4px; flex-wrap: wrap; align-items: center; z-index: 6; }}
  .score-badge {{ font-size: 9px; font-family: ui-monospace, Menlo, monospace; padding: 2px 6px; border-radius: 4px; line-height: 1.4; background: rgba(0,0,0,0.55); color: #fff; }}
  .score-badge.score-green {{ background: rgba(22, 163, 74, 0.92); }}
  .score-badge.score-amber {{ background: rgba(245, 158, 11, 0.92); color: #1a1a1a; }}
  .score-badge.score-red {{ background: rgba(220, 38, 38, 0.92); }}
  .score-badge.score-neutral {{ background: rgba(0,0,0,0.55); }}
  .score-badge.score-na {{ background: rgba(0,0,0,0.3); }}
  .payload-btn {{ margin-left: auto; width: 20px; height: 20px; border-radius: 50%; background: rgba(255,255,255,0.95); color: var(--fg); border: 1px solid rgba(0,0,0,0.15); font-size: 10px; font-style: italic; font-family: serif; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; padding: 0; }}

  .bypass-card {{ position: relative; padding: 24px 20px; margin: 16px auto; max-width: 95%;
    background: linear-gradient(135deg, #fff7ed, #fff1e6); border: 1px solid #fbbf24; border-radius: 12px; }}
  .bypass-card.skip {{ background: linear-gradient(135deg, #f5f5f4, #e7e5e4); border-color: #a8a29e; }}
  .bypass-tag {{ display: inline-block; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 4px; background: rgba(234, 88, 12, 0.92); color: #fff; margin-bottom: 12px; }}
  .bypass-tag.skip {{ background: rgba(120, 113, 108, 0.92); }}
  .bypass-hanssem {{ font-size: 11px; color: var(--muted); margin-bottom: 8px; font-style: italic; }}
  .bypass-title {{ margin: 0 0 8px; font-size: 17px; font-weight: 700; }}
  .bypass-body {{ margin: 0; font-size: 13px; color: var(--fg-soft); line-height: 1.6; }}
  .orig-fallback {{ opacity: 0.4; filter: grayscale(60%); }}

  /* === Modal === */
  .modal-backdrop {{ position: fixed; inset: 0; background: rgba(0,0,0,0.65); display: none; align-items: center; justify-content: center; z-index: 1000; }}
  .modal-backdrop.open {{ display: flex; }}
  .modal-content {{ background: #fff; width: 95%; max-width: 1400px; max-height: 94vh; overflow-y: auto; border-radius: 14px; padding: 28px 32px; box-shadow: 0 20px 80px rgba(0,0,0,0.5); position: relative; }}
  .modal-h {{ font-size: 18px; font-weight: 700; margin: 0 0 4px; }}
  .modal-sub {{ font-size: 12px; color: var(--muted); margin-bottom: 20px; }}
  .modal-close {{ position: absolute; top: 16px; right: 24px; cursor: pointer; font-size: 22px; color: var(--muted); border: none; background: none; padding: 4px 10px; }}
  .modal-section {{ margin: 20px 0 12px; padding-top: 16px; border-top: 1px solid var(--line); }}
  .modal-section-h {{ font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 10px; }}

  .attempt-tabs {{ display: flex; gap: 6px; margin-bottom: 16px; }}
  .attempt-tab {{ padding: 8px 14px; border: 1px solid var(--line); background: #fff; border-radius: 8px; cursor: pointer; font-family: inherit; font-size: 12px; color: var(--fg-soft); }}
  .attempt-tab.active {{ background: var(--fg); color: #fff; border-color: var(--fg); }}
  .attempt-tab.pass {{ border-left: 3px solid var(--good); }}
  .attempt-tab.fail {{ border-left: 3px solid var(--bad); }}

  .attempt-detail {{ display: none; }}
  .attempt-detail.active {{ display: block; }}

  .att-row {{ display: grid; grid-template-columns: 200px 1fr; gap: 12px; margin-bottom: 8px; font-size: 12px; }}
  .att-row b {{ color: var(--muted); font-weight: 600; }}
  .att-pass {{ color: var(--good); font-weight: 700; }}
  .att-fail {{ color: var(--bad); font-weight: 700; }}

  .modal-prompt-pre {{ background: #1a1a1d; color: #e5e7eb; padding: 14px 16px; border-radius: 8px; font-family: ui-monospace, Menlo, monospace; font-size: 11px; line-height: 1.6; white-space: pre-wrap; max-height: 500px; overflow-y: auto; border: 1px solid #2a2a2f; }}
  .modal-refs-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }}
  .modal-ref {{ border: 1px solid var(--line); border-radius: 6px; overflow: hidden; background: #fff; }}
  .modal-ref img {{ width: 100%; aspect-ratio: 1/1; object-fit: cover; display: block; }}
  .modal-ref-label {{ padding: 6px 8px; font-size: 10px; color: var(--fg); background: #fafafa; border-top: 1px solid var(--line); }}

  .ri-list, .sf-list {{ list-style: none; padding: 0; margin: 4px 0; }}
  .ri-list li, .sf-list li {{ font-size: 11px; padding: 6px 10px; margin-bottom: 4px; background: #fff5f5; border-left: 3px solid var(--bad); border-radius: 0 4px 4px 0; }}
  .ri-list li b {{ color: var(--bad); }}
  .sf-list li {{ background: #fffaf0; border-left-color: var(--warn); }}

  /* v16+ QA payload + checklist items */
  .qa-payload-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 8px; }}
  .qa-payload-cell {{ border: 1px solid var(--line); border-radius: 6px; overflow: hidden; background: #fff; }}
  .qa-payload-cell img {{ width: 100%; aspect-ratio: 1/1; object-fit: cover; display: block; }}
  .qa-payload-label {{ padding: 4px 6px; font-size: 9px; color: var(--fg); background: #fafafa; border-top: 1px solid var(--line); }}

  .items-list {{ list-style: none; padding: 0; margin: 4px 0; max-height: 400px; overflow-y: auto; }}
  .items-list li {{ font-size: 11px; padding: 6px 10px; margin-bottom: 4px; background: #fafafa; border-left: 3px solid var(--line); border-radius: 0 4px 4px 0; }}
  .items-list li.item-pass {{ background: #f0fdf4; border-left-color: var(--good); }}
  .items-list li.item-fail {{ background: #fff5f5; border-left-color: var(--bad); }}
  .items-list li.item-nv   {{ background: #f5f5f5; border-left-color: var(--muted); color: var(--muted); }}
  .items-list .item-icon {{ font-weight: 700; margin-right: 6px; }}
  .items-list code {{ background: #eee; padding: 1px 5px; border-radius: 3px; font-size: 10px; }}

  .halluc-list {{ list-style: none; padding: 0; margin: 4px 0; }}
  .halluc-list li {{ font-size: 11px; padding: 6px 10px; margin-bottom: 4px; background: #fff5f5; border-left: 3px solid var(--bad); border-radius: 0 4px 4px 0; color: var(--bad); }}
  .halluc-list li[style*="--good"] {{ color: var(--good) !important; background: #f0fdf4 !important; border-left-color: var(--good) !important; }}

  /* v16+ progress banner */
  .prog-banner {{ position: sticky; top: 0; z-index: 200; padding: 8px 24px; font-size: 12px; font-weight: 600; }}
  .prog-running {{ background: #fff7ed; color: #92400e; border-bottom: 1px solid #fdba74; }}
  .prog-done {{ background: #f0fdf4; color: #166534; border-bottom: 1px solid #bbf7d0; }}
  .prog-dot {{ display: inline-block; margin-right: 6px; }}
  .prog-running .prog-dot {{ color: #f97316; animation: pulse 1.4s ease-in-out infinite; }}
  .prog-done .prog-dot {{ color: #22c55e; }}
  @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}

  /* v16+ cell state (polling으로 update) */
  .cell-state-overlay {{
    position: absolute; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: rgba(255,255,255,0.85); backdrop-filter: blur(2px);
    pointer-events: none; gap: 10px;
  }}
  .cell-pending .orig-fallback {{ opacity: 0.45; filter: grayscale(50%); }}
  .cell-processing .cell-state-overlay {{ background: rgba(254,243,199,0.92); }}
  .cell-processing .orig-fallback {{ opacity: 0.55; filter: grayscale(30%); }}
  .cell-ready .cell-state-overlay {{ display: none; }}
  .cell-state-label {{ font-size: 11px; font-weight: 700; color: #92400e; letter-spacing: 0.05em; text-transform: uppercase; padding: 3px 10px; background: #fff; border-radius: 12px; border: 1px solid #fdba74; }}
  .cell-pending .cell-state-label {{ color: #6b7280; border-color: #d1d5db; }}
  .cell-ready .cell-state-label {{ display: none; }}
  .cell-spinner {{
    width: 28px; height: 28px; border: 3px solid #d1d5db; border-top-color: #f97316;
    border-radius: 50%; animation: spin 0.9s linear infinite;
  }}
  .cell-pending .cell-spinner {{ border-top-color: #9ca3af; opacity: 0.6; }}
  .cell-ready .cell-spinner {{ display: none; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
</style>
</head>
<body>
{_progress_banner}
<div class="topbar">
  <div class="topbar-row">
    <h1>가구 detail 템플릿 swap 미리보기</h1>
    <div class="chips">{chips_html}</div>
  </div>
</div>
{views_html}

<div class="modal-backdrop" id="modal-backdrop" onclick="if(event.target===this)closeModal()">
  <div class="modal-content" id="modal-content"></div>
</div>

<script>
function selectTpl(rank) {{
  document.querySelectorAll('.chip').forEach(c => c.classList.toggle('selected', +c.dataset.rank === rank));
  document.querySelectorAll('.view').forEach(v => v.classList.toggle('active', +v.dataset.rank === rank));
  window.scrollTo(0, 0);
}}
function scrollToSection(rank, slug) {{
  const view = document.querySelector(`.view[data-rank="${{rank}}"]`);
  if (!view) return;
  view.querySelectorAll('.tab').forEach(t => {{
    if (t.classList.contains('disabled')) return;
    t.classList.toggle('active', t.dataset.slug === slug);
  }});
  const target = view.querySelector(`#sec-${{slug}}-${{rank}}`);
  if (!target) return;
  const rect = target.getBoundingClientRect();
  const offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--topbar-h'))
               + parseInt(getComputedStyle(document.documentElement).getPropertyValue('--tabs-h')) + 80;
  window.scrollTo({{ top: window.scrollY + rect.top - offset, behavior: 'smooth' }});
}}

function showPayload(btn) {{
  const raw = btn.dataset.payload;
  const data = JSON.parse(raw.replace(/&quot;/g, '"'));
  const mc = document.getElementById('modal-content');

  // attempt tabs
  let tabs = '';
  let details = '';
  (data.attempts || []).forEach((a, idx) => {{
    const passClass = a.verdict === 'pass' ? 'pass' : 'fail';
    const active = idx === (data.attempts.length - 1) ? 'active' : '';
    tabs += `<button class="attempt-tab ${{passClass}} ${{active}}" onclick="switchAttempt(${{idx}})" data-att="${{idx}}">#${{a.attempt}} ${{a.strategy||'?'}} ${{a.verdict||'?'}}</button>`;

    // build per-attempt detail
    const failsKo = a.specific_failures_ko || [];
    const failsEn = a.specific_failures || [];
    const failsHtml = (failsKo.length ? failsKo : failsEn).map((f, i) => {{
      const en = failsEn[i] || '';
      return `<li><div>${{f}}</div>${{en && f !== en ? `<div style="font-size:9px;color:var(--muted);margin-top:2px">EN: ${{en}}</div>` : ''}}</li>`;
    }}).join('') || '<li style="background:#f0fdf4;border-left-color:var(--good);color:var(--good)">(없음)</li>';
    const riKo = a.reference_influences_ko || [];
    const riEn = a.reference_influences || [];
    const riHtml = (riKo.length ? riKo : riEn).map((r, i) => {{
      const elem = r.element_ko || r.element || '?';
      const corr = r.correction_ko || r.correction || '?';
      const src = r.source || '?';
      return `<li><b>${{elem}}</b> ← <b>${{src === 'C' ? '원본 panel' : src === 'A' ? '제품 ref' : src}}</b> 영향 → ${{corr}}</li>`;
    }}).join('') || '<li style="background:#f0fdf4;border-left-color:var(--good);color:var(--good)">(없음)</li>';
    const notesKo = a.notes_ko || a.notes || '(none)';
    const img_url = a.image ? `${{data.run_dir_rel}}/${{a.image}}` : null;
    const promptEsc = (a.prompt || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

    // v16+ checklist items 결과 (verifiable items별 binary 채점)
    const items = a.items_results || [];
    let itemsHtml = '';
    if (items.length) {{
      itemsHtml = items.map(it => {{
        const vcls = it.verdict === 'pass' ? 'item-pass' : it.verdict === 'fail' ? 'item-fail' : 'item-nv';
        const vicon = it.verdict === 'pass' ? '✓' : it.verdict === 'fail' ? '✗' : '–';
        return `<li class="${{vcls}}"><span class="item-icon">${{vicon}}</span> <b>[${{it.severity||'?'}}]</b> <code>${{it.id||'?'}}</code><div style="font-size:10px;color:var(--muted);margin-top:2px">${{it.reason_ko||''}}</div></li>`;
      }}).join('');
    }} else {{
      itemsHtml = '<li style="color:var(--muted)">(checklist 결과 없음 — 구 QA 호환)</li>';
    }}

    // v16+ hallucinations
    const halluc = a.hallucinations || [];
    const hallucHtml = halluc.length
      ? halluc.map(h => `<li>${{h}}</li>`).join('')
      : '<li style="color:var(--good)">(없음)</li>';

    // v16+ QA payload — attempt 별 sidecar(qa_payloads/{{label}}__a{{n}}.json) 가 있으면
    // 거기서 정확한 ref list 가져옴 (정확). 없으면 cell-level fallback.
    // sidecar는 비동기 fetch라 placeholder 먼저 채우고 나중에 update
    const cellLabel = data.panel === 'cover' ? 'cover' : ('panel_' + String(data.panel).padStart(2,'0'));
    const sidecarId = `qa-payload-${{cellLabel}}-a${{a.attempt}}`;
    const refLabelsFb = data.ref_labels || [];
    const refKeysFb = data.ref_keys || [];
    let payloadImgsHtml = `<div id="${{sidecarId}}" class="qa-payload-grid" data-sidecar="${{a.qa_payload_rel || ''}}" data-label="${{cellLabel}}" data-attempt="${{a.attempt}}">`;
    payloadImgsHtml += `<div class="qa-payload-cell"><img src="${{data.original_panel}}"/><div class="qa-payload-label">C — 한샘 원본</div></div>`;
    for (let ri = 0; ri < refKeysFb.length; ri++) {{
      const fn = refKeysFb[ri];
      const lbl = refLabelsFb[ri] || '?';
      const url = `../user_products/milo_777039/use_product/${{fn}}`;
      payloadImgsHtml += `<div class="qa-payload-cell"><img src="${{url}}"/><div class="qa-payload-label">A_${{ri+1}} — ${{lbl}}</div></div>`;
    }}
    if (img_url) {{
      payloadImgsHtml += `<div class="qa-payload-cell"><img src="${{img_url}}"/><div class="qa-payload-label">B — 결과 #${{a.attempt}}</div></div>`;
    }}
    payloadImgsHtml += '</div>';

    details += `
<div class="attempt-detail ${{active}}" data-att="${{idx}}">
  <div class="att-row"><b>verdict</b> <span class="${{a.verdict==='pass'?'att-pass':'att-fail'}}">${{a.verdict||'?'}}</span></div>
  <div class="att-row"><b>strategy</b> ${{a.strategy||'?'}}</div>
  <div class="att-row"><b>prod / comp</b> ${{a.prod||'-'}} / ${{a.comp||'-'}}</div>
  <div class="att-row"><b>critical fails</b> ${{a.critical_fail_count != null ? a.critical_fail_count : '-'}}</div>
  <div class="att-row"><b>seats</b> ${{a.seats||'?'}}</div>
  <div class="att-row"><b>text_in_image</b> ${{a.text_in_image ? '❌ true' : '✓ false'}}</div>
  <div class="att-row"><b>structure_preserved</b> ${{a.structure_preserved ? '✓ true' : '❌ false'}}</div>
  <div class="att-row"><b>refs sent</b> ${{a.ref_count || '?'}}장</div>

  ${{img_url ? `<div class="modal-section"><div class="modal-section-h">🖼 이 회차 결과</div><div class="modal-ref" style="max-width:400px"><img src="${{img_url}}"/></div></div>` : ''}}

  <div class="modal-section">
    <div class="modal-section-h">🔬 QA Payload — vision이 본 모든 이미지 (A_i + B + C)</div>
    <div class="qa-payload-grid">${{payloadImgsHtml}}</div>
    ${{a.qa_payload_rel ? `<div style="font-size:10px;color:var(--muted);margin-top:6px">payload sidecar: <code>${{a.qa_payload_rel}}</code></div>` : ''}}
  </div>

  <div class="modal-section">
    <div class="modal-section-h">✅ Checklist Items — 사용자 제품의 verifiable 항목 binary 채점</div>
    <ul class="items-list">${{itemsHtml}}</ul>
  </div>

  <div class="modal-section">
    <div class="modal-section-h">⚠ Hallucinations (제품에 없는 발명된 feature)</div>
    <ul class="halluc-list">${{hallucHtml}}</ul>
  </div>

  <div class="modal-section">
    <div class="modal-section-h">❌ Specific Failures (이번 attempt에서 잘못된 부분)</div>
    <ul class="sf-list">${{failsHtml}}</ul>
  </div>

  <div class="modal-section">
    <div class="modal-section-h">🔗 Reference Influences (잘못 영향 받은 element)</div>
    <ul class="ri-list">${{riHtml}}</ul>
  </div>

  <div class="modal-section">
    <div class="modal-section-h">📝 Prompt (이 회차 fal API에 전송된 full text)</div>
    <pre class="modal-prompt-pre">${{promptEsc}}</pre>
  </div>

  <div class="modal-section">
    <div class="modal-section-h">📋 QA 코멘트 (한국어)</div>
    <div style="font-size:12px;color:var(--fg);line-height:1.6">${{notesKo}}</div>
    ${{a.notes && a.notes !== notesKo ? `<div style="font-size:10px;color:var(--muted);margin-top:6px;line-height:1.5">EN: ${{a.notes}}</div>` : ''}}
  </div>
</div>
`;
  }});

  // refs (zone refs — common across attempts)
  let refsHtml = '<div class="modal-refs-grid">';
  refsHtml += `<div class="modal-ref"><img src="${{data.original_panel}}"/><div class="modal-ref-label">IMAGE 1 — original</div></div>`;
  for (const r of (data.refs_zone || [])) {{
    refsHtml += `<div class="modal-ref"><img src="${{r.path}}"/><div class="modal-ref-label">${{r.role}}</div></div>`;
  }}
  refsHtml += '</div>';

  mc.innerHTML = `
    <button class="modal-close" onclick="closeModal()">✕</button>
    <h3 class="modal-h">Panel ${{data.panel}} · payload</h3>
    <div class="modal-sub">class: <b>${{data.panel_class}}</b> · strategies: <b>${{data.strategies_used||'-'}}</b> · ${{data.passed?'✅ passed':'❌ failed'}}</div>

    <div class="modal-section">
      <div class="modal-section-h">📎 첨부된 references (모든 attempt 공통)</div>
      ${{refsHtml}}
    </div>

    <div class="modal-section">
      <div class="modal-section-h">🔁 회차별 결과 (클릭해서 그 회차 prompt + verdict 보기)</div>
      <div class="attempt-tabs">${{tabs}}</div>
      ${{details}}
    </div>
  `;
  document.getElementById('modal-backdrop').classList.add('open');
  // 첫 활성 attempt 의 sidecar 즉시 load
  const firstActive = document.querySelector('.attempt-detail.active');
  if (firstActive) {{
    firstActive.querySelectorAll('.qa-payload-grid[data-sidecar]').forEach(_loadSidecarRefs);
  }}
}}
function switchAttempt(idx) {{
  document.querySelectorAll('.attempt-tab').forEach(t => t.classList.toggle('active', +t.dataset.att === idx));
  document.querySelectorAll('.attempt-detail').forEach(d => d.classList.toggle('active', +d.dataset.att === idx));
  // sidecar fetch — attempt가 활성화될 때 그 attempt의 정확한 ref list 가져오기
  const active = document.querySelector(`.attempt-detail.active[data-att="${{idx}}"]`);
  if (!active) return;
  const grids = active.querySelectorAll('.qa-payload-grid[data-sidecar]');
  grids.forEach(_loadSidecarRefs);
}}

async function _loadSidecarRefs(grid) {{
  if (!grid || grid.dataset.loaded === '1') return;
  const rel = grid.dataset.sidecar;
  if (!rel) return;
  grid.dataset.loaded = '1';
  // run dir = RUN_DIR_REL 의 부모 (gpt_image 제외)
  const runDir = (typeof RUN_DIR_REL !== 'undefined' && RUN_DIR_REL)
    ? RUN_DIR_REL.replace(/\/gpt_image\/?$/, '')
    : null;
  if (!runDir) return;
  const url = runDir + '/' + rel;
  try {{
    const res = await fetch(url, {{ cache: 'no-store' }});
    const sidecar = await res.json();
    const refPaths = sidecar.ref_paths || [];
    const refLabels = sidecar.ref_labels || [];
    // 기존 grid 비우고 다시 그림 — C + A_i 들 + B
    // grid 의 첫 cell (C, B) 은 보존, A_i 만 정확히 재구성
    const C = grid.querySelector('.qa-payload-cell:nth-child(1)');
    // B는 마지막 cell
    const allCells = grid.querySelectorAll('.qa-payload-cell');
    const B = allCells[allCells.length - 1];
    // 중간 cells (A_i) 모두 제거
    for (let i = allCells.length - 2; i >= 1; i--) {{
      allCells[i].remove();
    }}
    // 정확한 A_i 삽입
    let frag = '';
    for (let i = 0; i < refPaths.length; i++) {{
      // ref_paths 는 절대경로 — relative URL 생성
      const ap = refPaths[i];
      const m = ap.match(/use_product\/(.+)$/);
      const fn = m ? m[1] : ap.split('/').pop();
      const lbl = refLabels[i] || '?';
      const u = `../user_products/milo_777039/use_product/${{fn}}`;
      frag += `<div class="qa-payload-cell"><img src="${{u}}"/><div class="qa-payload-label">A_${{i+1}} — ${{lbl}}</div></div>`;
    }}
    if (B) B.insertAdjacentHTML('beforebegin', frag);
    else grid.insertAdjacentHTML('beforeend', frag);
  }} catch (e) {{
    console.warn('sidecar load failed for', url, e);
  }}
}}
function closeModal() {{ document.getElementById('modal-backdrop').classList.remove('open'); }}
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});

function showImageModal(src, label) {{
  const mc = document.getElementById('modal-content');
  mc.innerHTML = `
    <button class="modal-close" onclick="closeModal()">✕</button>
    <h3 class="modal-h">${{label}}</h3>
    <div style="text-align:center"><img src="${{src}}" style="max-width:100%; max-height:80vh; border-radius:8px; border:1px solid var(--line)"/></div>
  `;
  document.getElementById('modal-backdrop').classList.add('open');
}}

// ────────────────────────── live polling (page fetch + DOM swap) ──────────────────────────
// 빌더가 매 panel 완료마다 페이지를 재생성한다.
// polling은 페이지를 fetch해서 변경된 cell(특히 cell-ready, cell-processing)만 DOM swap.
// payload 버튼, score badges 등 빌더가 그린 정확한 마크업을 그대로 옮긴다.
const SUMMARY_URL = {_rank1_summary_url!r};
const PAGE_URL = location.pathname;
const POLL_INTERVAL_MS = 3000;

async function pollSummary() {{
  try {{
    // 1) summary fetch — banner / 종료 판정
    const sumRes = await fetch(SUMMARY_URL + '?ts=' + Date.now(), {{ cache: 'no-store' }});
    const sum = await sumRes.json();
    const progress = sum.progress || {{}};
    const banner = document.querySelector('.prog-banner');
    if (banner) {{
      if (progress.is_complete) {{
        banner.style.display = 'none';  // 완료 banner 숨김 (사용자 요청)
      }} else {{
        banner.style.display = '';
        const ip = progress.in_progress || [];
        banner.className = 'prog-banner prog-running';
        banner.innerHTML = '<span class="prog-dot">●</span> 진행 중 · ' + progress.done + '/' + progress.total
          + ' · 대기: ' + ip.slice(0,6).join(', ') + (ip.length > 6 ? '...' : '');
      }}
    }}

    // 2) 페이지 자체를 fetch + DOM diff
    const pageRes = await fetch(PAGE_URL + '?ts=' + Date.now(), {{ cache: 'no-store' }});
    const pageHtml = await pageRes.text();
    const doc = new DOMParser().parseFromString(pageHtml, 'text/html');

    const oldCells = new Map();
    document.querySelectorAll('.img-with-chip[data-panel-label]').forEach(el => {{
      oldCells.set(el.dataset.panelLabel, el);
    }});

    doc.querySelectorAll('.img-with-chip[data-panel-label]').forEach(newEl => {{
      const label = newEl.dataset.panelLabel;
      const oldEl = oldCells.get(label);
      if (!oldEl) return;
      const oldState = oldEl.classList.contains('cell-ready') ? 'ready'
                      : oldEl.classList.contains('cell-processing') ? 'processing'
                      : 'pending';
      const newState = newEl.classList.contains('cell-ready') ? 'ready'
                      : newEl.classList.contains('cell-processing') ? 'processing'
                      : 'pending';
      // ready인 cell은 다시 덮어쓰면 modal/이미지 깜빡임 → ready→ready 는 skip
      if (oldState === 'ready' && newState === 'ready') return;
      if (oldState === newState && oldState !== 'ready') {{
        // pending → pending 변경 없음
        // processing → processing 도 변경 없음
        return;
      }}
      // 상태 변화 있음 → 새 cell로 교체
      oldEl.replaceWith(newEl);
    }});

    if (progress.is_complete) {{
      if (window._pollTimer) {{ clearInterval(window._pollTimer); window._pollTimer = null; }}
    }}
  }} catch (e) {{
    console.warn('poll failed', e);
  }}
}}

if (SUMMARY_URL) {{
  pollSummary();
  window._pollTimer = setInterval(pollSummary, POLL_INTERVAL_MS);
}}
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT}")
print(f"size: {OUT.stat().st_size // 1024}KB")

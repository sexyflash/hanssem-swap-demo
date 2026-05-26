"""Panel별 ref 자원 자동 매핑 — 일률적 ref X, panel layout 기반 선별.

사용자 지적:
"3번 같은 경우 p08_frame_02 · p08_frame_04 · p08_frame_05 이미 분류한게 있잖아
저 템플릿에는 저것만 보내도 분명 잘 했을 것 같아"

→ panel_layout_maps.json (elements + spatial)
+ classification.json (자원 카테고리)
→ panel별 필요 ref 결정

입력:
- templates/01_sofa_992474/panel_layout_maps.json
- user_products/milo_777039/use_product/classification.json
- user_products/milo_777039/product_input_v3.json

출력:
- templates/01_sofa_992474/panel_ref_mapping.json
  각 panel에 어떤 use_product 자원을 ref로 보낼지 결정
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"
USE_PROD = USER_DIR / "use_product"
OUT = TPL_DIR / "panel_ref_mapping.json"

LAYOUTS = json.loads((TPL_DIR / "panel_layout_maps.json").read_text())["panels"]
CLS = json.loads((USE_PROD / "classification.json").read_text())

# use_product 파일을 의미 그룹으로 정리
def rel(p):
    return f"use_product/{p}"

assets = {
    "main_front": rel("p08_frame_01.jpg"),
    "main_side":  rel("p08_frame_03.jpg"),
    "main_angle": rel("p08_frame_02.jpg"),
    "detail_legs": rel("p08_frame_04.png"),     # 사용자 의도 — 다리/하부
    "detail_arm":  rel("p08_frame_05.png"),     # 사용자 의도 — 팔걸이/하단
    "detail_cushion_a": rel("detail_02.png"),   # vision: 좌방석/팔걸이
    "detail_cushion_b": rel("detail_03.png"),   # vision: 등받이/좌방석
    "detail_arm_b":     rel("detail_05.png"),   # vision: 팔걸이/등쿠션
    "detail_seam":      rel("p08_frame_04.png"),  # 시접도 여기서 보이는 것
    "color_variant_gray":  rel("p08_frame_01_color_2.webp"),
    "color_variant_rose":  rel("p08_frame_01_color_3.webp"),
    "color_swatch_oat":   rel("color_01.png"),
    "color_swatch_gray":  rel("color_02.png"),
    "color_swatch_rose":  rel("color_03.png"),
    "material":           rel("material.png"),
}

# 룰: panel_class + spatial_layout/elements 키워드 → ref 키 list

def pick_refs(panel):
    cls = panel.get("panel_class", "other")
    spatial = panel.get("spatial_layout", "") or ""
    elems = panel.get("elements", []) or []
    elem_roles = {e.get("role", "") for e in elems}
    elem_descs = " ".join(e.get("description", "") for e in elems)
    haystack = (spatial + " " + elem_descs).lower()
    sp = spatial  # 한국어 키워드 검사

    # cover / intro hero
    if cls in ("intro_hero", "product_shot"):
        return ["main_front", "main_angle"]

    # lifestyle
    if cls == "lifestyle_scene":
        return ["main_front", "main_angle", "detail_arm"]

    # size chart — 사이즈 + 팔걸이/다리 디테일까지 보여줌
    if cls == "size_chart":
        return ["main_front", "main_side", "detail_legs", "detail_arm"]

    # structure chart — 구조 + 디테일
    if cls == "structure_chart":
        return ["main_front", "detail_cushion_a", "detail_legs", "material"]

    # color option — 메인 + variants + swatches
    if cls == "color_option":
        return ["main_front", "color_variant_gray", "color_variant_rose",
                "color_swatch_oat", "color_swatch_gray", "color_swatch_rose"]

    # module lineup — 메인 + 컬러 variants + swatch (라벨 인식용)
    if cls == "module_lineup":
        return ["main_front", "color_variant_gray", "color_variant_rose",
                "color_swatch_oat", "color_swatch_gray", "color_swatch_rose"]

    # material swatch
    if cls == "material_swatch":
        return ["material", "detail_cushion_a", "main_front"]

    # detail close-up — 가용 자원 적극 활용 (3~5장)
    # 사용자 원칙: 가용 가능한 디테일을 살리기 위해 ref 더 보강
    if cls == "detail_close_up":
        refs = ["main_angle"]  # 전체 무드 reference 1장 항상

        # 다리/하부
        if "sofa_leg" in elem_roles or "다릿발" in sp:
            refs += ["detail_legs", "detail_arm", "main_side"]
        # 배지/플레이트 (측면) — 가용 자원 풍부히
        elif "brand_plate" in elem_roles or "badge" in elem_roles or "측면" in sp or "옆모습" in sp:
            refs = ["main_side", "detail_arm", "detail_arm_b", "detail_legs"]
        # USB/control — milo엔 없음
        elif "control_panel" in elem_roles or "usb_port" in elem_roles or "button" in elem_roles:
            refs = ["main_front", "detail_cushion_a", "main_angle"]
        # 등받이 + 팔걸이 (panel_03 유형)
        elif ("등받이" in sp or "등쿠션" in sp) and "팔걸이" in sp:
            refs += ["detail_legs", "detail_arm", "detail_cushion_b"]
        # 등받이만
        elif "등받이" in sp or "등쿠션" in sp:
            refs += ["detail_cushion_a", "detail_cushion_b", "detail_legs"]
        # 좌방석/팔걸이
        elif ("좌방석" in sp or "방석" in sp) and "팔걸이" in sp:
            refs += ["detail_legs", "detail_arm", "detail_cushion_a"]
        # 좌방석만
        elif "좌방석" in sp or "방석" in sp:
            refs += ["detail_cushion_a", "detail_legs", "detail_seam"]
        # 팔걸이만
        elif "팔걸이" in sp:
            refs += ["detail_arm", "detail_arm_b", "detail_cushion_a"]
        # 패브릭/가죽 표면
        elif "가죽 표면" in sp or "패브릭" in sp or "원단" in sp:
            refs = ["material", "detail_cushion_a", "detail_seam", "main_front"]
        # 리클라이너 / 헤드레스트 (milo엔 없음)
        elif "리클라이너" in sp or "헤드레스트" in sp:
            refs = ["main_front", "main_angle", "detail_cushion_a"]
        # 디폴트
        else:
            refs += ["detail_cushion_a", "detail_legs", "detail_arm"]

        # dedupe + limit 5 (가용 자원 더 적극 활용)
        seen = []
        for r in refs:
            if r not in seen:
                seen.append(r)
        return seen[:5]

    # default
    return ["main_front", "main_side", "main_angle"]


mapping = {}
for panel in LAYOUTS:
    panel_id = panel.get("panel", "")
    idx = panel.get("panel_idx", panel_id)
    if "error" in panel:
        continue
    refs_keys = pick_refs(panel)
    refs_paths = [assets[k] for k in refs_keys if k in assets]
    mapping[panel_id] = {
        "panel_idx": idx,
        "panel_class": panel.get("panel_class"),
        "ref_keys": refs_keys,
        "ref_paths": refs_paths,
        "ref_count": len(refs_paths),
    }

# 정리 표시
print(f"Panel별 ref mapping ({len(mapping)} panels):\n")
for pid, m in mapping.items():
    print(f"  {pid:>10} [{m['panel_class']:>17}] ({m['ref_count']}장) → {', '.join(m['ref_keys'])}")

OUT.write_text(json.dumps({"assets": assets, "panels": mapping}, ensure_ascii=False, indent=2),
               encoding="utf-8")
print(f"\nwrote {OUT}")

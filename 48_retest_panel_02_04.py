"""panel_02, panel_04만 재실행 — gpt-5 vision + reference vs target contrast 명시.

발견된 문제:
- panel_02: 다리만 milo, 팔걸이/패브릭은 한샘 가죽 영향 (underswap/RI)
- panel_04: dim 수치 잘못 (86 vs 85), firmness 빨간점 한샘 그대로 (MEDIUM), 등쿠션 잘림, TEXT

해결:
- vision = gpt-5 (이전 gpt-4.1)
- prompt에 명시적 REFERENCE vs TARGET contrast block
- panel-specific data inject (firmness 정확 값, dim 수치 정확)
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
import fal_client  # noqa: E402
from lib import download, upload, openai_client, data_uri  # noqa: E402

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"

LAYOUTS = {p["panel"]: p for p in json.loads((TPL_DIR / "panel_layout_maps.json").read_text())["panels"] if "panel_idx" in p}
USER_OUT = json.loads((USER_DIR / "auto_pipeline_output.json").read_text())
PRODUCT_INPUT = json.loads((USER_DIR / "product_input.json").read_text())
SPEC = USER_OUT["spec"]
VISUAL = USER_OUT["visual"]

OUT_ROOT = TPL_DIR / "swap_results"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
run_dir = OUT_ROOT / f"retest_panel_02_04_{ts}"
run_dir.mkdir()
out_dir = run_dir / "gpt_image"
out_dir.mkdir()

MODEL_NAME = "gpt_image"
ENDPOINT = config.MODELS[MODEL_NAME]
VISION_MODEL = "gpt-5"  # 업그레이드

USE_PROD = USER_DIR / "use_product"
GIF_FRAMES = sorted(USE_PROD.glob("p08_frame_0?.jpg"))
SMART_SHEET = USER_DIR / "smart_sheet.jpg"

TARGETS = [2, 4]  # panel_02, panel_04


def gpt5_call(messages, response_format=None):
    """gpt-5 with max_completion_tokens (instead of max_tokens)."""
    kwargs = {"model": VISION_MODEL, "messages": messages}
    if response_format:
        kwargs["response_format"] = response_format
    return openai_client.chat.completions.create(**kwargs)


def core_block():
    dims = SPEC.get("dimensions", {}) or {}
    pi_spec = PRODUCT_INPUT.get("spec", {}) or {}
    pi_feat = PRODUCT_INPUT.get("features", {}) or {}
    seat_n = SPEC.get("seat_count", 2)
    seat_firmness = pi_feat.get("seat_cushion_firmness", "MEDIUM SOFT")
    back_firmness = pi_feat.get("back_cushion_firmness", "SOFT")

    return f"""\
=== [TARGET PRODUCT — 우리가 그릴 대상 (밀로 패브릭소파 2인용)] ===
- 좌석수: STRICTLY {seat_n}인 (반드시 2개의 좌방석 + 2개의 등쿠션)
- 마감재: 패브릭 (linen-look matte texture, 절대 가죽 X — 가죽 광택 X)
- 색상: 라이트 베이지 (오트밀톤)
- 팔걸이: THIN slim 직각 형태, 등받이보다 약간 낮음 (절대 두꺼운 leather padded arm 아님)
- 등쿠션: 2개, LOOSE puffy 직사각 (절대 tight tailored attached 아님), firmness = {back_firmness}
- 좌방석: 2개, deep loose, firmness = {seat_firmness}
- 다리: 4개 SLIM cylindrical matte black metal (THIN, ~10-14cm, 절대 chunky block/wood 아님, 절대 V자 메탈도 아님 — straight cylinder)
- 소재 내장: {pi_feat.get('seat_cushion_fill', '')}
- 프레임: {pi_feat.get('frame', '')}
- 사이즈: {pi_spec.get('width_cm', dims.get('width_cm'))}×{pi_spec.get('depth_cm', dims.get('depth_cm'))}×{pi_spec.get('height_cm', dims.get('height_cm'))}cm
- 좌방석 깊이: {pi_spec.get('seat_depth_cm', 52)}cm, 좌방석 높이: {pi_spec.get('seat_height_cm', 45)}cm, 팔걸이 높이: {pi_spec.get('arm_height_cm', 57)}cm, 다리 높이: {pi_spec.get('leg_height_cm', 14)}cm
"""


def contrast_block():
    """REFERENCE (한샘 가죽) vs TARGET (밀로 패브릭) 명시적 contrast."""
    return """\
=== [CRITICAL: REFERENCE vs TARGET CONTRAST] ===

IMAGE 1 (원본 panel C)의 sofa = 한샘 MVME 키안티 가죽 sofa
  - 가죽 (leather, glossy sheen, 매끄러운 surface)
  - 두꺼운 padded 팔걸이 (thick puffy leather pad)
  - tailored tight 쿠션 (sharp edges, structured)
  - 슬림 메탈 V자 다리 (angled chrome leg)
  - 헤드레스트 + 리클라이너 (전기 control panel/USB)
  - 4인용 큰 사이즈

우리가 그릴 대상 = 밀로 패브릭소파 2인용 (위 [TARGET PRODUCT] 참조)

⚠️ CONTRAST DIFFERENCES — 절대 IMAGE 1에서 inherit하면 안 되는 것:
  - IMAGE 1: 가죽 광택 → OUR: 패브릭 matte linen 텍스처
  - IMAGE 1: 두꺼운 팔걸이 padding → OUR: thin slim 직각 팔걸이
  - IMAGE 1: tight tailored 쿠션 → OUR: loose puffy 쿠션
  - IMAGE 1: V자 메탈 다리 → OUR: 직립 cylindrical 메탈 다리
  - IMAGE 1: 헤드레스트/리클라이너 → OUR: 없음
  - IMAGE 1: 4인 → OUR: 2인

→ IMAGE 1은 panel layout/composition/lighting의 reference로만 사용.
   sofa 자체는 IMAGE 2..N (밀로 reference)에서 가져와 ENTIRE 통째 swap.
   "다리만 갈고 body는 leather inherit" 같은 부분 swap 절대 금지.
"""


def panel_specific_block(panel_idx, panel_class):
    if panel_idx == 4:  # size_chart
        pi_spec = PRODUCT_INPUT.get("spec", {})
        pi_feat = PRODUCT_INPUT.get("features", {})
        return f"""\
=== [PANEL 4 — SIZE CHART (FIXED LAYOUT)] ===
이 panel은 사이즈 도면 + firmness 차트 layout.

레이아웃 정확히 보존 (한샘 C에서):
  - 좌상단: 단위 표시 (단위 : cm)
  - 중앙: sofa 측면 view + dim line (가로 width × 깊이 depth × 높이 height)
  - 아래: 다릿발 높이 / 좌방석 깊이 / 좌방석 높이 텍스트
  - 좌방석 firmness 5단계 bar (HARD / MEDIUM HARD / MEDIUM / MEDIUM SOFT / SOFT)
  - 등쿠션 firmness 5단계 bar (5단계 라벨 동일)

대상 (밀로 2인용)의 정확한 값으로 변경:
  - sofa: 밀로 2인 패브릭 (위 TARGET 참조)
  - dim line: 가로 200 × 깊이 90 × 높이 85 (한샘 86 절대 X — 우리는 85)
  - 다릿발 높이: 14cm (한샘 12 X)
  - 좌방석 깊이: 52cm (한샘 55 X)
  - 좌방석 높이: 45cm (한샘 49 X)
  - 좌방석 firmness 빨간점: MEDIUM SOFT 위치 (4번째 점, 한샘 MEDIUM 위치 X)
  - 등쿠션 firmness 빨간점: SOFT 위치 (5번째 마지막 점, 한샘 MEDIUM X)
  - 좌방석/등쿠션 영역 모두 표시 (한 줄로 자르지 말 것)

이미지에 한국어 텍스트 박지 말 것 (HTML overlay로 추가). 다이어그램의 라인, 화살표, 빨간점 위치만 정확히 표시.
"""
    if panel_idx == 2:  # detail_close_up
        return f"""\
=== [PANEL 2 — DETAIL CLOSE-UP] ===
이 panel은 sofa의 좌측 하단 모서리 close-up (팔걸이 + 좌방석 + 다리).
구도/조명은 IMAGE 1과 동일. sofa는 밀로 패브릭으로 완전 swap.

집중 검증 (가장 흔히 잘못되는 부분):
  1) 팔걸이 두께 = THIN slim profile (한샘처럼 thick padded leather pad 절대 X)
  2) 팔걸이 형태 = 직각 boxy slim (한샘 rolled/padded 절대 X)
  3) 좌방석 = loose puffy (한샘 tight tailored 절대 X)
  4) 다리 = SLIM cylindrical matte black 직립 (한샘 V자 angled 메탈 절대 X)
  5) 패브릭 = matte linen-look (가죽 광택 절대 X)
  6) seam = piped 가장자리 (가죽 smooth seam 절대 X)
"""
    return ""


def build_prompt(panel_idx, layout_map, strategy="aligned"):
    panel_class = layout_map.get("panel_class", "other")
    scene = layout_map.get("spatial_layout", "")

    return f"""\
TASK: Photorealistic furniture detail-page panel reproduction (FULL product swap, not partial).

References:
- IMAGE 1 = 한샘 원본 panel C. Layout/composition/lighting reference ONLY.
- IMAGES 2..N = 밀로 product references (GIF frames, 정답 product 모습).

{core_block()}

{contrast_block()}

=== [ORIGINAL PANEL SPATIAL LAYOUT (reproduce structure only, swap sofa)] ===
{scene}

{panel_specific_block(panel_idx, panel_class)}

=== [ABSOLUTE OUTPUT RULE] ===
- 출력 이미지에 한국어/영어/숫자/라벨 ABSOLUTELY 0개.
- panel의 sofa는 ENTIRE 밀로로 swap (body + arms + cushions + fabric + legs 통째).
- "다리만 milo, body는 C 가죽" 같은 부분 swap 절대 금지.
"""


def qa_strict(panel_orig, swap_result, panel_idx):
    qa_prompt = (
        f"당신은 가구 swap 결과를 매우 엄격하게 검증하는 한국어 QA 시스템입니다 (gpt-5).\n"
        f"Panel {panel_idx} 검증.\n"
        "타겟: 밀로 2인용 패브릭소파 (가죽 X, 2인 STRICT, thin slim 팔걸이, loose puffy 쿠션, slim cylindrical 다리).\n"
        "원본 C: 한샘 4인 가죽 리클라이너 (가죽 광택, thick padded 팔걸이, tailored tight 쿠션, V자 메탈 다리, 헤드레스트).\n\n"
        "이미지 비교:\n"
        "  A = 밀로 product reference (정답)\n"
        "  B = swap 결과 (검증 대상)\n"
        "  C = 한샘 원본 panel\n\n"
        "엄격 검증 5가지 (각각 1-5점, 5=완벽 일치 A와, 1=완전 C 영향):\n"
        "  1) arm_thinness: B의 팔걸이가 A처럼 thin slim인가 (vs C thick padded)?\n"
        "  2) cushion_shape: B의 쿠션이 A처럼 loose puffy인가 (vs C tight tailored)?\n"
        "  3) fabric_texture: B가 A처럼 matte linen 패브릭인가 (vs C 가죽 광택)?\n"
        "  4) leg_shape: B의 다리가 A처럼 slim cylindrical 직립인가 (vs C V자 angled)?\n"
        "  5) full_swap: B의 전체 sofa가 milo로 swap됐는가, 부분만 X (다리만 갈고 body는 C 가죽이면 1점)?\n"
        + ("\n  6) dim_correctness (panel 4만): dim 수치가 200/90/85/52/45/14 정확? firmness 빨간점 좌방석 MEDIUM SOFT, 등쿠션 SOFT 위치?\n" if panel_idx == 4 else "")
        + "\nJSON 응답 (한국어):\n"
        '  "scores": {"arm_thinness": 1-5, "cushion_shape": 1-5, "fabric_texture": 1-5, "leg_shape": 1-5, "full_swap": 1-5'
        + (', "dim_correctness": 1-5' if panel_idx == 4 else "")
        + '},\n'
        '  "specific_failures": [한국어 list, 각 항목 구체적],\n'
        '  "reference_influences": [{"element_ko": str, "source": "C", "correction_ko": str}],\n'
        '  "underswap": bool,\n'
        '  "text_in_image": bool,\n'
        '  "product_score" (0-100): scores 평균 ×20을 base로 underswap/text 패널티 적용,\n'
        '  "composition_score" (0-100),\n'
        '  "seat_count_in_B": int,\n'
        '  "notes": 한국어 2-3 문장,\n'
        '  "verdict": "pass"|"retry" — pass = 모든 scores >= 4 AND not underswap AND not text_in_image.'
    )
    resp = gpt5_call(
        messages=[{"role": "user", "content": [
            {"type": "text", "text": qa_prompt},
            {"type": "text", "text": "IMAGE A:"},
            {"type": "image_url", "image_url": {"url": data_uri(GIF_FRAMES[0])}},
            {"type": "text", "text": "IMAGE B:"},
            {"type": "image_url", "image_url": {"url": data_uri(swap_result)}},
            {"type": "text", "text": "IMAGE C:"},
            {"type": "image_url", "image_url": {"url": data_uri(panel_orig)}},
        ]}],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


def aspect_ratio_for(w, h):
    r = w / h
    candidates = [("21:9", 21/9), ("16:9", 16/9), ("3:2", 3/2), ("4:3", 4/3),
                  ("1:1", 1.0), ("3:4", 3/4), ("2:3", 2/3), ("9:16", 9/16), ("9:21", 9/21)]
    return min(candidates, key=lambda c: abs(c[1] - r))[0]


async def generate(prompt, ref_urls, aspect_ratio):
    args = {"prompt": prompt, "image_urls": ref_urls, "aspect_ratio": aspect_ratio}
    try:
        result = await fal_client.subscribe_async(ENDPOINT, arguments=args)
    except Exception:
        args.pop("aspect_ratio", None)
        result = await fal_client.subscribe_async(ENDPOINT, arguments=args)
    imgs = result.get("images") or result.get("image")
    if isinstance(imgs, list) and imgs:
        first = imgs[0]
        return first["url"] if isinstance(first, dict) else first
    if isinstance(imgs, dict):
        return imgs["url"]
    raise ValueError(f"no image url")


async def main():
    from PIL import Image

    print(f"=== retest panel_02, panel_04 with gpt-5 vision + contrast prompt ===\n")

    # upload refs
    gif_urls = await asyncio.gather(*[upload(p) for p in GIF_FRAMES])
    smart_url = await upload(SMART_SHEET)

    for panel_idx in TARGETS:
        ppath = next(TPL_DIR.glob(f"panel_{panel_idx:02d}.*"))
        layout_map = LAYOUTS.get(f"panel_{panel_idx:02d}.jpg", {})
        layout_map["panel_idx"] = panel_idx
        w, h = Image.open(ppath).size
        ratio = aspect_ratio_for(w, h)
        base_url = await upload(ppath)
        label = f"panel_{panel_idx:02d}"

        prompt = build_prompt(panel_idx, layout_map)
        ref_urls = [base_url] + list(gif_urls)
        print(f"[{label}] ar={ratio} refs={len(ref_urls)} prompt_len={len(prompt)}")
        img = out_dir / f"{label}__a1_aligned_gpt5.png"
        gurl = await generate(prompt, ref_urls, ratio)
        await download(gurl, img)

        # QA with gpt-5
        verdict = qa_strict(ppath, img, panel_idx)
        scores = verdict.get("scores", {})
        sf = verdict.get("specific_failures", []) or []
        ri = verdict.get("reference_influences", []) or []
        print(f"  scores: {scores}")
        print(f"  prod={verdict.get('product_score')} comp={verdict.get('composition_score')} "
              f"seats={verdict.get('seat_count_in_B')} underswap={verdict.get('underswap')} text={verdict.get('text_in_image')}")
        print(f"  verdict: {verdict.get('verdict')}")
        print(f"  notes: {verdict.get('notes','')}")
        print(f"  failures ({len(sf)}):")
        for f in sf:
            print(f"    · {f}")
        print(f"  RI ({len(ri)}):")
        for r in ri:
            print(f"    · {r.get('element_ko','?')} ← {r.get('source','?')} → {r.get('correction_ko','?')}")
        print()

        # save details
        (out_dir / f"{label}_verdict.json").write_text(
            json.dumps({"prompt": prompt, **verdict}, ensure_ascii=False, indent=2)
        )

    print(f"DONE → {run_dir}")


if __name__ == "__main__":
    asyncio.run(main())

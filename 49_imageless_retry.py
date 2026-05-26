"""panel_02/04 image-less retry — panel C 이미지 빼고 prompt 묘사만 + milo refs only.

발견: panel C(한샘 가죽 sofa)를 IMAGE 1로 주면 모델이 시각 영향(가죽 광택, 두꺼운
팔걸이, V자 다리)을 inherit. milo refs만 보내고 panel C의 묘사는 prompt 텍스트로
inline → 모델이 milo references에서만 시각 정보 + prompt 묘사대로 합성.

3-strategy with retry:
  S1 (image-less): milo refs + prompt에 panel C 묘사 inline
  S2 (overpaint if S1 fail): prev output + milo refs (panel C 여전히 없음)
  S3 (with panel C if S2 fail): panel C + milo refs (마지막 수단)

QA = gpt-5.
"""

import asyncio
import json
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
RUN_DIR = OUT_ROOT / f"imageless_{ts}"
RUN_DIR.mkdir()
OUT_DIR = RUN_DIR / "gpt_image"
OUT_DIR.mkdir()

ENDPOINT = config.MODELS["gpt_image"]
VISION_MODEL = "gpt-5"
TARGETS = [2, 4]
MAX_ATTEMPTS = 3

USE_PROD = USER_DIR / "use_product"
GIF_FRAMES = sorted(USE_PROD.glob("p08_frame_0?.jpg"))
SMART_SHEET = USER_DIR / "smart_sheet.jpg"


def gpt5_json(messages):
    return openai_client.chat.completions.create(
        model=VISION_MODEL, messages=messages, response_format={"type": "json_object"},
    )


def core():
    pi_spec = PRODUCT_INPUT.get("spec", {})
    pi_feat = PRODUCT_INPUT.get("features", {})
    return f"""\
=== [TARGET — 우리가 그릴 sofa] ===
밀로 패브릭소파 2인용 (밀로 references = IMAGES 1, 2, 3)
- 좌석수: 2 (좌방석 2 + 등쿠션 2, 절대)
- 마감재: 패브릭 (matte linen, 가죽 X)
- 색상: 라이트 베이지 (오트밀톤)
- 팔걸이: THIN slim 직각, 등받이보다 낮음 (절대 두꺼운 padded leather arm X)
- 등쿠션: 2개 LOOSE puffy 직사각 (tight tailored X)
- 좌방석: 2개 loose deep, firmness {pi_feat.get('seat_cushion_firmness','MEDIUM SOFT')}
- 다리: 4개 SLIM cylindrical matte black metal 직립 (~14cm, 절대 V자 angled X, 절대 block X)
- 사이즈: {pi_spec.get('width_cm')}×{pi_spec.get('depth_cm')}×{pi_spec.get('height_cm')}cm
- 좌방석 깊이: {pi_spec.get('seat_depth_cm')}cm, 좌방석 높이: {pi_spec.get('seat_height_cm')}cm, 팔걸이 높이: {pi_spec.get('arm_height_cm')}cm
"""


def panel_description(panel_idx):
    """한샘 panel의 시각적 묘사 — prompt 텍스트로만. 이미지는 보내지 않음."""
    if panel_idx == 2:
        return """\
=== [PANEL DESCRIPTION — 우리가 reproduce할 panel layout (이미지 없음, 묘사만)] ===
이 panel은 sofa의 좌측 하단 모서리 close-up 컷.
- camera: 좌측 모서리에서 sofa 측면 살짝 보이게 카메라 angle, 좌측 절반 정도 sofa 보임
- framing: 좌측 ⅓에 sofa 모서리 (팔걸이 정면 + 좌방석 일부 + 다리 하나), 우측 ⅔에 sofa 본체 일부 (좌방석 + 등쿠션 정면 + 다리 둘)
- crop: 위는 등쿠션 중간까지, 아래는 다리 발부터 바닥 일부까지
- background: 매우 밝은 무광 흰 배경 (subtle gray shadow)
- lighting: 자연광, 위에서 약간 좌측, soft shadow
- shadow: 다리 발 아래 옅은 contact shadow

이 panel을 위 layout 그대로 reproduce하되, sofa는 milo로 ENTIRE swap.
"""
    if panel_idx == 4:
        return """\
=== [PANEL DESCRIPTION — size chart layout (이미지 없음, 묘사만)] ===
이 panel은 사이즈 chart 도면. 회색 배경 + 측면 view sofa + dim line + firmness bar.

레이아웃:
- 좌상단: "단위 : cm" 텍스트 (이미지 안에 그리지 마, HTML overlay로 별도 추가)
- 중앙 상단 70% 영역: sofa 측면-3/4 view 일러스트 (양 옆에 dim line)
  - 우측 세로 dim line: 높이 85cm (절대 86 X — milo는 85)
  - 하단 가로 dim line: 가로 200cm × 깊이 90cm
- 사이즈 아래 영역: "다릿발 높이 : 14cm / 좌방석 깊이 : 52cm / 좌방석 높이 : 45cm" 텍스트 (이미지 안 X, HTML overlay)
- 하단 ⅓ 영역: firmness bar 2개 (좌방석 / 등쿠션)
  - 좌방석 bar: 5단계 (HARD - MEDIUM HARD - MEDIUM - MEDIUM SOFT - SOFT) — 빨간점이 4번째(MEDIUM SOFT) 위치에 (절대 3번째 MEDIUM X)
  - 등쿠션 bar: 5단계 동일 — 빨간점이 5번째(SOFT) 위치 (절대 3번째 MEDIUM X)
- 아주 하단: "* 착석감은 개인에 따라 차이가 있을 수 있습니다." 텍스트 (이미지 안 X)

CRITICAL:
- 한국어/영어 텍스트, 숫자 ABSOLUTELY 0 (HTML overlay로 별도 추가됨)
- firmness bar는 점 5개 + 가로선 + 빨간점 위치만 시각적으로 정확히 그려야
- sofa는 milo 2인 (위 TARGET 참조 — 가죽 X)
"""
    return ""


def build_prompt(panel_idx, strategy, with_panel_c=False):
    strat_note = ""
    if strategy == "overpaint":
        strat_note = "\n\n[STRATEGY: OVERPAINT] IMAGE 1 = previous attempt. Redraw sofa region to match TARGET; layout 유지."
    elif strategy == "smart_sheet_with_C":
        strat_note = "\n\n[STRATEGY: WITH PANEL C] IMAGE 1 = panel C (한샘 원본 panel — layout reference). MUST NOT inherit C's sofa attributes (leather sheen, thick arm, V-shape leg). Use ONLY for layout/composition guidance."

    ref_intro = "IMAGES 1, 2, 3 = milo product references (the actual product to render)."
    if with_panel_c:
        ref_intro = "IMAGE 1 = panel C (layout reference only — DO NOT inherit sofa attributes). IMAGES 2, 3, 4 = milo product references."

    return f"""\
TASK: Photorealistic furniture detail-page panel reproduction (FULL milo swap).

{ref_intro}

{core()}

{panel_description(panel_idx)}

{strat_note}

=== [ABSOLUTE RULES] ===
1. Sofa = ENTIRE milo (body + arms + cushions + fabric + legs 통째).
2. NO text in output (한국어/영어/숫자 ZERO).
3. NO leather sheen, NO tufting, NO V-shape legs, NO thick padded arms.
4. STRICTLY 2 seats.
"""


def qa(panel_orig, swap_result, panel_idx):
    qa_prompt = (
        f"매우 엄격한 한국어 QA 시스템 (gpt-5). Panel {panel_idx}.\n"
        "타겟: 밀로 2인용 패브릭소파.\n원본 C: 한샘 4인 가죽 리클라이너.\n\n"
        "이미지: A = milo ref, B = swap 결과, C = 한샘 원본 panel.\n\n"
        "5점 만점 평가:\n"
        "1) arm_thinness: B 팔걸이 thin slim (A처럼)? (C thick padded이면 1점)\n"
        "2) cushion_shape: B 쿠션 loose puffy (A처럼)? (C tailored면 1점)\n"
        "3) fabric_texture: B 패브릭 matte linen (A처럼)? (C 가죽 광택이면 1점)\n"
        "4) leg_shape: B 다리 slim cylindrical 직립 (A처럼)? (C V자 angled면 1점)\n"
        "5) full_swap: B 전체 milo? (다리만 milo면 1점)\n"
        + ("6) dim_correctness: dim 정확? 200/90/85, 좌방석 52/45, 다리 14, 좌방석 MEDIUM SOFT, 등쿠션 SOFT 위치?\n" if panel_idx == 4 else "")
        + "\nJSON: {\"scores\":{...}, \"product_score\":0-100, \"composition_score\":0-100, \"seat_count_in_B\":int, \"underswap\":bool, \"text_in_image\":bool, \"specific_failures\":[\"한국어\"], \"reference_influences\":[{\"element_ko\":..,\"source\":\"C\",\"correction_ko\":..}], \"notes\":\"한국어\", \"verdict\":\"pass\"|\"retry\"} — pass = all scores >=4 AND not underswap AND not text_in_image."
    )
    resp = gpt5_json([{"role": "user", "content": [
        {"type": "text", "text": qa_prompt},
        {"type": "text", "text": "IMAGE A:"}, {"type": "image_url", "image_url": {"url": data_uri(GIF_FRAMES[0])}},
        {"type": "text", "text": "IMAGE B:"}, {"type": "image_url", "image_url": {"url": data_uri(swap_result)}},
        {"type": "text", "text": "IMAGE C:"}, {"type": "image_url", "image_url": {"url": data_uri(panel_orig)}},
    ]}])
    return json.loads(resp.choices[0].message.content)


def aspect_ratio_for(w, h):
    r = w / h
    candidates = [("21:9", 21/9), ("16:9", 16/9), ("3:2", 3/2), ("4:3", 4/3),
                  ("1:1", 1.0), ("3:4", 3/4), ("2:3", 2/3), ("9:16", 9/16), ("9:21", 9/21)]
    return min(candidates, key=lambda c: abs(c[1] - r))[0]


async def generate(prompt, ref_urls, ar):
    args = {"prompt": prompt, "image_urls": ref_urls, "aspect_ratio": ar}
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
    raise ValueError("no url")


async def main():
    from PIL import Image

    print("=== panel_02/04 image-less retry — gpt-5 QA + retry loop ===\n")
    gif_urls = await asyncio.gather(*[upload(p) for p in GIF_FRAMES])

    for panel_idx in TARGETS:
        ppath = next(TPL_DIR.glob(f"panel_{panel_idx:02d}.*"))
        w, h = Image.open(ppath).size
        ratio = aspect_ratio_for(w, h)
        base_url = await upload(ppath)
        label = f"panel_{panel_idx:02d}"

        attempts = []
        prev_output = None

        for attempt_n in range(1, MAX_ATTEMPTS + 1):
            t0 = time.time()
            if attempt_n == 1:
                # S1: image-less (milo refs only, no panel C)
                strategy = "imageless"
                prompt = build_prompt(panel_idx, "aligned", with_panel_c=False)
                ref_urls = list(gif_urls)
            elif attempt_n == 2:
                # S2: overpaint previous
                strategy = "overpaint"
                if not prev_output:
                    continue
                prev_url = await upload(prev_output)
                prompt = build_prompt(panel_idx, "overpaint", with_panel_c=False)
                ref_urls = [prev_url] + list(gif_urls)
            else:
                # S3: include panel C as last resort
                strategy = "with_C"
                prompt = build_prompt(panel_idx, "smart_sheet_with_C", with_panel_c=True)
                ref_urls = [base_url] + list(gif_urls)

            print(f"[{label}/{strategy}/#{attempt_n}] ar={ratio} refs={len(ref_urls)} prompt_len={len(prompt)}")
            img = OUT_DIR / f"{label}__a{attempt_n}_{strategy}.png"
            try:
                gurl = await generate(prompt, ref_urls, ratio)
                await download(gurl, img)
                t_gen = time.time()
            except Exception as e:
                print(f"  GEN ERR: {e}")
                attempts.append({"attempt": attempt_n, "strategy": strategy, "error": str(e), "prompt": prompt})
                continue

            verdict = qa(ppath, img, panel_idx)
            t_end = time.time()
            attempts.append({
                "attempt": attempt_n, "strategy": strategy,
                "image": img.name, "gen_seconds": round(t_gen - t0, 1), "qa_seconds": round(t_end - t_gen, 1),
                "fal_url": gurl, "prompt": prompt, **verdict,
            })
            prev_output = img
            scores = verdict.get("scores", {})
            print(f"  scores: {scores}")
            print(f"  prod={verdict.get('product_score')} comp={verdict.get('composition_score')} "
                  f"seats={verdict.get('seat_count_in_B')} underswap={verdict.get('underswap')} text={verdict.get('text_in_image')}")
            print(f"  verdict: {verdict.get('verdict')}")
            print(f"  notes: {verdict.get('notes','')}")
            failures = verdict.get("specific_failures", [])
            if failures:
                print(f"  failures:")
                for f in failures:
                    print(f"    · {f}")
            if verdict.get("verdict") == "pass":
                print(f"  ✓ PASS at attempt {attempt_n}\n")
                break
            print()

        final = next((a for a in attempts if a.get("verdict") == "pass"), None)
        if not final:
            scored = [a for a in attempts if "verdict" in a]
            final = max(scored, key=lambda a: a.get("product_score", 0)) if scored else None

        (OUT_DIR / f"{label}_full.json").write_text(
            json.dumps({"attempts": attempts, "final": final}, ensure_ascii=False, indent=2)
        )

    print(f"DONE → {RUN_DIR}")


if __name__ == "__main__":
    asyncio.run(main())

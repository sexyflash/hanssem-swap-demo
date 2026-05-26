"""한샘 detail HTML 텍스트 노드를 밀로 버전으로 한 번에 substitute.

흐름:
1. detail.html 파싱 → text node list (순서대로)
2. mismatch_resolution.json + spec → LLM 한 번 호출로 같은 개수/순서의 milo 텍스트 생성
3. text-node index → milo text 매핑 JSON 저장 (v13 빌더가 사용)

결과: templates/01_sofa_992474/text_substitute.json
"""

import json
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import openai_client as client  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

HERE = Path(__file__).parent
TPL_DIR = HERE / "templates/01_sofa_992474"
USER_DIR = HERE / "user_products/milo_777039"
OUT = TPL_DIR / "text_substitute.json"

detail_html = (TPL_DIR / "detail.html").read_text(encoding="utf-8", errors="ignore")
mismatch = json.loads((TPL_DIR / "mismatch_resolution.json").read_text())
spec = json.loads((USER_DIR / "auto_pipeline_output.json").read_text())["spec"]

soup = BeautifulSoup(detail_html, "lxml")
# img 순서에 따라 panel_idx 부여
imgs = soup.find_all("img")
img_to_panel = {id(img): i + 1 for i, img in enumerate(imgs)}

# text node 수집 (순서대로) + 각 text 이전/이후 img의 panel_idx 추정
text_nodes = []
img_idx_seen = 0
for el in soup.descendants:
    if el.name == "img":
        img_idx_seen = img_to_panel.get(id(el), img_idx_seen)
    elif isinstance(el, str):
        t = el.strip()
        if t and len(t) > 2:
            text_nodes.append({
                "i": len(text_nodes),
                "text": t,
                "near_panel": img_idx_seen,  # 이 텍스트 직전까지 본 panel
            })

print(f"detail HTML text nodes: {len(text_nodes)}")

# panel별 verdict
verdict_by_panel = {r["panel_idx"]: r for r in mismatch["resolutions"]}

verdicts_summary = [
    {"panel_idx": r["panel_idx"], "verdict": r["verdict"], "feature": r["hanssem_feature"]}
    for r in mismatch["resolutions"]
]

PROMPT = f"""\
당신은 가구 detail page 카피라이터입니다.

[원본 한샘 템플릿] = MVME 키안티 천연가죽 리클라이너 4인 (가죽/리클라이너/USB/헤드레스트 등)
[사용자 제품] = 밀로 패브릭소파 2인용
- 패브릭(가죽X), 좌방석 미디엄소프트, 등쿠션 소프트, 덕페더 67% + 마이크로화이버 33%
- 사이즈 200×90×85cm, 좌방석 52×45, 팔걸이 57cm
- 컬러: 오트밀, 라이트그레이, 더스티로즈
- 폴리니크 패브릭 (생활발수, OEKO-TEX/FITI/EO 인증)
- 32kg 고밀도 통스펀지, EO 건조목 프레임, S자 스프링, 슬림 메탈 다리

panel별 verdict:
{json.dumps(verdicts_summary, ensure_ascii=False, indent=2)}

input — 한샘 detail HTML의 텍스트 노드 list (순서대로). 각 노드 "near_panel"은 그 텍스트 직전까지 등장한 panel index:
{json.dumps(text_nodes, ensure_ascii=False, indent=2)}

각 텍스트 노드를 밀로 패브릭소파 2인용 버전으로 변환:
- 한샘 고유 정보 (가죽, 리클라이너, USB, 4인용, 키안티 등)는 밀로 대응 정보 (패브릭, 일반소파, 2인용, 밀로)로 교체
- panel verdict가 "bypass"인 경우, 그 한샘 기능은 빼고 milo의 다른 강점(덕페더, 생활발수, 통스펀지 등)으로 대체 카피
- panel verdict가 "match"인 경우, 같은 의도지만 밀로 spec/수치로 정확히 교체
- panel verdict가 "skip"인 경우, "(정보 누락 — skip)"으로 표시
- 글자 수 / 줄바꿈은 원본과 비슷하게 유지 (디자인 깨지지 않게)
- "MVME 키안티 천연가죽 리클라이너 4인" 같은 한샘 제품명/숫자는 절대 X

Return JSON: {{ "substitutes": [{{"i": int, "text": "milo version"}}, ...] }}.
원본과 동일 순서 / 동일 개수. No preamble.
"""

print("LLM substitute call...")
resp = client.chat.completions.create(
    model=config.VISION_MODEL,
    messages=[{"role": "user", "content": PROMPT}],
    response_format={"type": "json_object"},
    temperature=0.2,
)
result = json.loads(resp.choices[0].message.content)

# build lookup by index
subs = {item["i"]: item["text"] for item in result.get("substitutes", [])}
# fallback: any missing index keeps original
final = []
for tn in text_nodes:
    final.append({
        "i": tn["i"],
        "original": tn["text"],
        "milo": subs.get(tn["i"], tn["text"]),
        "near_panel": tn["near_panel"],
    })

OUT.write_text(json.dumps({
    "node_count": len(final),
    "substitutes": final,
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote {OUT} ({len(final)} text nodes)")
print("\nsample (first 6):")
for s in final[:6]:
    print(f"  [{s['i']}] {s['original'][:50]}")
    print(f"   → {s['milo'][:50]}")

"""기존 v6 swap 결과의 QA notes/failures/RI 영어 → 한국어 일괄 번역.

UI에 한국어로 표시하기 위해 summary.json 옆에 qa_korean.json 생성.
"""

import json
import sys
from pathlib import Path

EXP = Path("/Users/sexyflash/Projects/Creagen/Apps/5th/experiment")
sys.path.insert(0, str(EXP))
import config  # noqa: E402
from lib import openai_client as client  # noqa: E402

HERE = Path(__file__).parent
SR = HERE / "templates/01_sofa_992474/swap_results"
LATEST = (SR / "latest_v6.txt").read_text().strip()
RUN_DIR = SR / LATEST
SUMMARY = RUN_DIR / "summary.json"
OUT = RUN_DIR / "qa_korean.json"

s = json.loads(SUMMARY.read_text())
all_items = []
for c in s["cells"]:
    for a in c.get("attempts", []):
        notes = (a.get("notes") or "").strip()
        fails = a.get("specific_failures") or []
        ris = a.get("reference_influences") or []
        item = {
            "label": c["label"], "attempt": a.get("attempt"),
            "notes": notes, "specific_failures": fails, "reference_influences": ris,
        }
        all_items.append(item)

PROMPT = f"""\
다음은 AI 이미지 swap의 QA 결과 (영어). 각 항목을 한국어로 번역하세요. JSON 형식으로 응답하세요.
- notes: 짧은 한국어 요약 (1-2 문장)
- specific_failures: 한국어 짧은 list (각 항목 한 줄)
- reference_influences: 한국어로 element/correction 풀어쓰기

input: {json.dumps(all_items, ensure_ascii=False, indent=2)}

같은 길이 list로 반환:
{{
  "translations": [
    {{
      "label": str, "attempt": int,
      "notes_ko": "한국어 요약",
      "specific_failures_ko": [한국어 list],
      "reference_influences_ko": [{{"element_ko": str, "source": "C"|"A", "correction_ko": str}}]
    }}, ...
  ]
}}
No preamble.
"""

print(f"translating {len(all_items)} QA items to Korean...")
resp = client.chat.completions.create(
    model=config.VISION_MODEL,
    messages=[{"role": "user", "content": PROMPT}],
    response_format={"type": "json_object"},
    temperature=0.1,
)
result = json.loads(resp.choices[0].message.content)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {OUT} ({len(result.get('translations', []))} items)")

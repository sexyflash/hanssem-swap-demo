# 한샘 detail 템플릿 swap — 핸드오프 (v16 진행 중)

작업 디렉토리: `/Users/sexyflash/Projects/Creagen/Apps/5th/hanssem_research`
사용자: cc6@pioncorp.com
이전 commit: `a2395d7` (v14 + v15 WIP checkpoint)

---

## 📌 프로젝트 개요

한샘 상세페이지 템플릿을 그대로 보존하면서 사용자 제품(milo 패브릭소파 2인용)으로 panel 단위 swap.

**Top 6 템플릿** (`top6_template_urls.json`):
1. sofa 992474 (MVME 키안티) ← 현재 작업 중 (4인 가죽)
2. wardrobe 1066850
3. wardrobe 171733
4. desk 667832
5. desk 667815
6. sofa 799220

**사용자 제품**: milo 777039 (`user_products/milo_777039/`) — 2인 패브릭 소파 (3인용 옵션 제거됨)

---

## 🎯 v16 핵심 변경 (방금 작성)

이전 세션 끝에 사용자가 지시한 큰 refactor 반영:

1. **스마트시트 복원 + 강화 (500% 정보)** — `pipeline_lib/smart_sheet_builder.py`
   - LLM이 product_input + classification + panel mapping을 보고 sheet directive를 직접 작성
   - sheet 한 장에 PRESERVE/NEVER + panel × asset map + spec/certifications + 컬러 정확 명까지
   - 워터마크/회색 배경으로 "DO NOT REPLICATE" 명시. 결과 복제 방지.

2. **3-stage retry 전략** — `pipeline_lib/retry_strategist.py`
   - **stage 1 (attempt 2 · REPLAN)**: QA 텍스트 append 금지. LLM이 원인 분석 + 보완책 해설 작성 후 prompt 재작성.
   - **stage 2 (attempt 3 · PAINT EDIT)**: 앞선 두 시도 중 점수 더 좋은 결과를 base 이미지로 → fal-ai/gpt-image-2/edit에 IMAGE 1로 보내며 부분 인페인팅 directive만 prompt로.
   - **stage 3 (attempt 4 · CUMULATIVE)**: essence + smart sheet 이미지 + 누적 보완책을 통합 prompt로 재작성. sheet ref가 동봉됨.

3. **하드코딩 룰 제거 (LLM 판단)**
   - `71_map_panel_refs.py` 의 `pick_refs` if/elif → `pipeline_lib/llm_panel_mapper.py`. panel context + 분류된 자원을 LLM이 보고 결정. 소파/책상/의자/수납장 무관.
   - 74/75의 `build_edit_block` panel_class별 if → `pipeline_lib/llm_edit_block.py`. panel 원본 이미지 OCR + product_input → 정확한 텍스트 치환 / 시각 변경 / PRESERVE를 LLM이 직접 작성.

4. **버전 자동 increment + 산출물 패키징** — `pipeline_lib/version_bundler.py`
   - `swap_results/v\d+_*` 디렉토리 스캔해서 자동 v{N} 부여 (다음은 v15)
   - 각 run 디렉토리에 `sources/` 폴더 — 사용된 .py + product_input.json + layout_maps + classification 사본 동봉
   - `prompts/{label}__a{n}.md` · `qa_reports/{label}__a{n}.json` · `manifest.json` 까지 자동 작성
   - 다른 연구 과제로 그대로 들고 갈 수 있는 self-contained 번들

5. **2인용 통일**: `product_input_v3.json` 의 `model_options` 에서 3인용 제거. v16에서 `len(model_options)` 자동 인식하여 chart/lineup 칸 수 결정.

---

## 📂 v16 새 파일 구조

```
hanssem_research/
├── HANDOFF.md  ← 이 파일
├── 76_swap_pipeline_v16.py  ← 메인 entry (★ 새 세션 시작 시 실행)
├── pipeline_lib/
│   ├── __init__.py
│   ├── version_bundler.py   — 버전/번들링
│   ├── llm_panel_mapper.py  — LLM panel→ref 매핑 (71 대체)
│   ├── llm_edit_block.py    — LLM edit instruction (74/75 build_edit_block 대체)
│   ├── smart_sheet_builder.py — LLM directive로 sheet 생성
│   └── retry_strategist.py  — 3-stage retry prompt 생성
│
├── 74_swap_pipeline_v14.py / 75_swap_pipeline_v15.py  ← 레퍼런스로 보관 (실행은 v16)
├── 71_map_panel_refs.py  ← deprecated (LLM mapper로 대체됨)
│
├── templates/01_sofa_992474/
│   ├── panel_layout_maps.json
│   ├── panel_ref_mapping.json  ← v13~v15 산출. v16은 run 디렉토리 안에 별도 저장
│   ├── _cover_1000.jpg / panel_01.jpg ~ panel_12.jpg / detail.html / meta.json
│   └── swap_results/
│       ├── v14_20260526_193812/  ← v14 마지막 run
│       └── v15_{ts}/             ← v16 첫 run이 만들 디렉토리 (sources/, prompts/, qa_reports/, smart_sheet.png 포함)
│
├── user_products/milo_777039/
│   ├── product_input_v3.json  ← 2인용만 (3인용 제거됨)
│   ├── use_product/
│   │   ├── classification.json   ← 66번 vision 분류
│   │   └── p08_frame_*.jpg / detail_*.png / color_*.png / material.png ...
│   └── preprocessed/  (v16에선 사용 안 함 — sheet는 run 디렉토리에 저장)
│
└── archive_sheets/72_make_master_sheet_v3.py  ← 옛 sheet 빌더 (참고용)
```

---

## 🔄 v16 실행 흐름

```
[1/4] LLM panel → ref 매핑
   classification.json + product_input + panel_layout_maps + panel 원본 이미지
   → 각 panel별로 LLM이 ref_keys 결정 + rationale
   → run_dir/panel_ref_mapping_v16.json

[2/4] Smart sheet 생성
   LLM이 product_input/classification/mapping 보고 fal directive 작성
   → fal-ai/gpt-image-2/edit → run_dir/smart_sheet.png

[3/4] 자원 upload
   panel별 매핑된 모든 use_product 파일 dedupe upload

[4/4] per-panel swap (병렬, CONCURRENCY=13)
   for each target (cover + 12 panels):
     LLM edit_block 생성 (panel 원본 + product_input)
     attempt 1: initial prompt → fal → QA
       if pass: done
     attempt 2 (REPLAN): LLM이 진단+보완 → 재작성 prompt → fal → QA
     attempt 3 (PAINT EDIT): best-of-2 base + 부분 수정 directive → fal → QA
     attempt 4 (CUMULATIVE): essence + smart sheet ref + 누적 patches → fal → QA

[finalize]
   summary.json + manifest.json + sources/ 동봉
   latest_v{N}.txt + latest.txt 갱신
```

---

## 🚀 새 세션 first commands

```bash
cd /Users/sexyflash/Projects/Creagen/Apps/5th/hanssem_research
cat HANDOFF.md

# 코드 무결성 확인 (실행 전)
python3 -c "
import sys; sys.path.insert(0, '.')
from pipeline_lib import version_bundler, llm_panel_mapper, llm_edit_block, smart_sheet_builder, retry_strategist
print('imports OK')
print('next version:', version_bundler.next_version(__import__('pathlib').Path('templates/01_sofa_992474/swap_results')))
"

# 실제 실행 (fal/openai 키 필요)
python3 76_swap_pipeline_v16.py

# 결과 확인
ls templates/01_sofa_992474/swap_results/v15_*/   # 첫 v16 run = v15 번호
cat templates/01_sofa_992474/swap_results/latest.txt
python3 59_build_report_v22.py  # UI 빌더 (v14까지의 latest를 읽음 — v16 결과 보려면 빌더 path 조정 필요할 수 있음)
open report/index.html
```

---

## 📊 진화 타임라인

| 버전 | 핵심 변경 | 점수 | 비고 |
|---|---|---|---|
| v6/v7 | gpt-image-1.5 baseline | ~10/13 | hallucination 많음 |
| v9 | gpt-image-2 + quality=high + explicit edit | 10/13 | baseline 확정 |
| v10 | 5-slot multi-tier (panel C + main 3 + master sheet) | 10/13 | 27분 (concurrency 3) |
| v11 | gpt-5.5 QA + threshold 99 + 다리 4개 강제 + 가변 라인업 | 13/13 (가짜) | cover/02/08이 master sheet 복제 |
| v12 | QA grid detection 추가 (`image_format`) | 8/13 | master copy 4개 fix |
| v13 | panel별 ref mapping (71번) + master sheet v3 | 10/13 (실질 13/13) | panel_07 master copy까지 fix |
| v14 | master sheet 완전 제거 + cushion-arm 연결 prompt | 7/13 (실질 13/13) | QA legs strict false fail 6개 |
| v15 | (WIP) 매핑 보강 + 컬러 hallucination QA + 컬러명 quote 강제 | — | 미실행 (architecture가 v16으로 통합됨) |
| **v16** | **LLM 매핑 + LLM edit block + 3-stage retry + smart sheet 복원/강화 + 자동 버전/번들링** | — | **실행 대기** |

---

## 🚨 사용자 피드백 핵심 (시간순)

1. **"다리 5개가 아니라 4개"** (v10 후) — vision hallucination
2. **"마스터 시트가 grid 형태로 출력되면 안 됨"** (v11 후) — image_format detection 도입
3. **"panel별 ref mapping 필요"** (v12 후) — 71번 작성
4. **"마스터 시트는 메타 자료 — 결과 복제 X"** (v12 후) — v3 디자인 (DO NOT REPLICATE 워터마크)
5. **"마스터 시트 공정 필요없고 panel별 매칭만"** (v13 후) — v14에서 제거
6. **"팔걸이 보조쿠션과 좌방석이 연결된 구조 prompt에 강조"** (v13 후) — v14 prompt 반영
7. **"panel_03에 p08_frame_02+04+05 3장만"** (v13 후) — 71번 보정
8. **"panel_08 측면 ref 부족 (4장 가용)"** (v14 후) — v15 매핑 보강
9. **"panel_12 컬러 hallucination ('풀리에이지/로즈브라운')"** (v14 후) — v15 QA 강화
10. **"QA 99점인데 hallucination — QA 신뢰도 자체 문제"** (v14 후) — v15 컬러 검증 추가
11. **"하드코딩된 룰 매핑 → LLM 판단 매핑"** (v15 작성 중) — **v16 llm_panel_mapper + llm_edit_block로 해결**
12. **"3인용 제거 → 2인용 통일"** (v15 작성 중) — **v16에서 product_input 정리 완료**
13. **★ "스마트시트 복원 + 500% 정보 + sheet 한 장만 봐도 모든 게 들어가게"** (v15 후) — **v16 smart_sheet_builder**
14. **★ "3단계 retry — replan/best-of-2-paint/essence+sheet+cumulative — 단순 텍스트 append X"** (v15 후) — **v16 retry_strategist**
15. **★ "어떤 템플릿에만 쓸 수 있게끔 하드코딩 된 게 있으면 다 걷어내고"** (v15 후) — **v16 모듈 모두 generalizable**
16. **★ "리포트 생성할 때 버전이 정확히 늘어날 수 있도록"** (v15 후) — **v16 version_bundler.next_version**
17. **★ "실험되는 것들이 파이썬과 결과가 세트로 묶일 수 있게"** (v15 후) — **v16 version_bundler.bundle_sources**

---

## 🔧 알려진 issue (v15에서 이월)

1. **QA legs strict over-fail**:
   - close-up panel에서 다리가 일부만 보일 때 (`legs=2`) QA가 fail 처리
   - v16 QA에선 `leg_count_when_visible` (close-up conditional) 도입했지만 실행 검증 필요.

2. **fal-ai/gpt-image-2/edit 서버 에러**:
   - downstream_service_error / downstream_service_unavailable 가끔 발생
   - MAX_ATTEMPTS=4 + 단계별 다른 prompt로 robustness 향상 기대

3. **image_urls 최대 10장 제한**:
   - panel당 ref MAX=6, base 1, sheet 1 → 최대 8장. 한계 안 넘음.

4. **v22 UI 빌더 (59번)**:
   - v14까지의 swap_results 디렉토리 구조를 기대함. v16 출력은 `gpt_image/` 서브폴더로 분리되어 있어 빌더 path 조정 필요할 수 있음. 첫 v16 run 후 확인.

---

## 💡 v16 dispatch 결정 (architecture 선택지)

| 결정 사항 | 선택 | 대안 |
|---|---|---|
| 매핑 모듈 분리 위치 | `pipeline_lib/` (재사용성 우선) | inline in pipeline file |
| LLM 호출 모델 | gpt-5 (mapping/edit/retry), gpt-5.5 (QA — 사용자 명시 고수) | 전부 gpt-5.5 |
| MAX_ATTEMPTS | 4 (initial + 3 retries 사용자 명시) | 3 (initial + 2 retries) |
| smart sheet 캐시 | run별 생성 (현재) | template 단위 캐시 |
| paint_edit base 선택 | LLM 판단 + 점수 fallback | 점수 only |

---

## 🚦 v16 실행 후 검증할 것

- [ ] `latest_v15.txt` (v16의 첫 출력 — 번호는 15) 생성 확인
- [ ] `swap_results/v15_*/sources/` 에 7개 파일 동봉됐는지
- [ ] `swap_results/v15_*/manifest.json` `prompts/` `qa_reports/` 채워졌는지
- [ ] `swap_results/v15_*/smart_sheet.png` 워터마크 + panel × asset map 확인
- [ ] `panel_ref_mapping_v16.json` rationale이 hardcoded 룰처럼 단조롭지 않은지
- [ ] cover panel_12 의 컬러 라벨이 "오트밀/라이트그레이/더스티로즈" 정확
- [ ] panel_12에 3인용 칸이 없는지 (lineup_count_correct=5)
- [ ] panel_04 size chart도 2인용 한 사이즈
- [ ] 다리 4개 hallucination 0
- [ ] 한샘 텍스트 잔존 0

---

## 핵심 환경/도구

- `EXP = /Users/sexyflash/Projects/Creagen/Apps/5th/experiment`
- `from lib import openai_client, data_uri, upload, download`
- text model: `gpt-5` (mapping/edit_block/retry/sheet directive)
- vision model: `gpt-5.5` (QA — 사용자 명시 고수)
- image gen: `fal-ai/gpt-image-2/edit` (사용자 명시, nano-banana 안 씀)
- CONCURRENCY=13, MAX_ATTEMPTS=4

## 사용자 행동 패턴

- 결과 지향 — 점수보다 실제 이미지 quality
- 진행 상황 묻는 빈도 높음 → 백그라운드 작업 시 progress 로그 잘 찍기
- 디테일 지적 정확 (다리 hallucination, 컬러명 hallucination 즉시 감지)
- 일반화 매우 중시 (하드코딩보다 LLM 판단)
- option/cost/architecture만 묻고 나머지는 dispatch (memory: `feedback_autonomy_scope`)

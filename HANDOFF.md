# 한샘 detail 템플릿 swap — 핸드오프 (v15 진행 중)

작업 디렉토리: `/Users/sexyflash/Projects/Creagen/Apps/5th/hanssem_research`
사용자: cc6@pioncorp.com
최종 commit: `d9efda5` (v11~v13 checkpoint)

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

**사용자 제품**: milo 777039 (`user_products/milo_777039/`) — 2인 패브릭 소파

---

## 🎯 핵심 목표

- 좌측 한샘 원본 panel / 우측 milo로 swap된 panel — dual grid
- Cover: prod 95+, comp 95+
- 일반 panel: prod 93+, comp 80+ (chart는 90+)
- 한국어 텍스트 깨짐 0
- 사용자 의도 정확 반영 (다리 4개, 컬러명, 가변 라인업)

---

## 📂 현재 디렉토리 구조

```
hanssem_research/
├── HANDOFF.md  ← 이 파일
├── auto_pipeline.py  (URL → milo 데이터 추출, 7단계)
├── top6_template_urls.json
├── archive_sheets/  ← 사용 안 하는 시트 스크립트 (60, 61, 62, 64, 65, 72)
│
├── 14_prepare_llm_input.py
├── 34_substitute_texts.py  (한샘 → milo 텍스트 치환)
├── 53_swap_pipeline_v9.py  (gpt-image-2 baseline)
├── 55_extract_milo_deep.py
├── 57_preprocess_grid_sheet.py (deprecated PIL)
├── 58_dense_vision.py  ← milo dense paragraph 추출 (gpt-5 vision)
├── 59_build_report_v22.py  ← UI 빌더 (현재 active)
├── 63_swap_pipeline_v10.py
├── 66_classify_assets.py  ← use_product/ vision 분류
├── 68_swap_pipeline_v11.py  (gpt-5.5 QA, threshold 99)
├── 70_swap_pipeline_v12.py  (grid detection)
├── 71_map_panel_refs.py  ← panel별 ref 매핑 (★ 하드코딩 룰 — LLM으로 전환 필요)
├── 73_swap_pipeline_v13.py
├── 74_swap_pipeline_v14.py  (master sheet 제거)
├── 75_swap_pipeline_v15.py  ← 작성 중 (컬러 hallucination QA 강화)
│
├── templates/01_sofa_992474/
│   ├── _cover_1000.jpg
│   ├── panel_01.jpg ~ panel_18.jpg (한샘 원본)
│   ├── detail.html
│   ├── meta.json
│   ├── panel_layout_maps.json  ← panel별 elements/spatial_layout (vision 추출)
│   ├── panel_ref_mapping.json  ← panel → milo ref 매핑 (71번 출력)
│   ├── mismatch_resolution.json
│   ├── text_substitute.json
│   └── swap_results/
│       ├── latest_v14.txt
│       ├── v9_20260526_150641/   (v9 baseline)
│       ├── v10_20260526_164927/
│       ├── v11_20260526_181124/
│       ├── v12_20260526_183536/
│       ├── v13_20260526_191046/  ← 실질 13/13 success
│       └── v14_20260526_193812/  ← 7/13 (master sheet 제거 + QA 다리 strict)
│
├── user_products/milo_777039/
│   ├── product_input_v3.json  ← milo dense 정보 (사용자 입력 시뮬레이션)
│   ├── auto_pipeline_output.json
│   ├── _cover_1000.jpg
│   ├── panel_01.jpg ~ panel_18.jpg (milo 원본 detail page)
│   ├── use_product/  ← 담당자 업로드 이미지
│   │   ├── p08_frame_01.jpg  (메인 정면)
│   │   ├── p08_frame_02.jpg  (메인 측면)
│   │   ├── p08_frame_03.jpg  (메인 각도)
│   │   ├── p08_frame_04.png  (디테일 다리/하부)
│   │   ├── p08_frame_05.png  (디테일 팔걸이)
│   │   ├── detail_01.webp ~ detail_05.png  (추가 디테일)
│   │   ├── p08_frame_01_color_1/2/3  (오트밀/라이트그레이/더스티로즈 variants)
│   │   ├── color_01.png ~ color_03.png  (swatches)
│   │   ├── material.png
│   │   └── classification.json  ← 66번 vision 분류 결과
│   └── preprocessed/  ← (master sheet 제거 후 비어있음)
│
└── report/index.html  ← v22 빌더 출력 (좌 한샘 / 우 milo swap)
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
| **v14** | **master sheet 완전 제거 + cushion-arm 연결 prompt** | 7/13 (실질 13/13) | QA legs strict false fail 6개 |
| v15 | (작성 중) 매핑 보강 + 컬러 hallucination QA + 컬러명 quote 강제 | — | **이어서 작업할 것** |

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
11. **★ "하드코딩된 룰 매핑 → LLM 판단 매핑"** (v15 작성 중) — **다음 세션 최우선 TASK**
12. **★ "3인용 제거 → 2인용 통일"** (v15 작성 중) — **다음 세션 즉시 처리**

---

## 🎯 다음 세션 작업 우선순위

### [P0 — 즉시] 3인용 제거 → 2인용 통일

- `user_products/milo_777039/product_input_v3.json`의 `model_options`에서 3인용 제거
- `auto_pipeline_output.json`도 확인
- 73~75 pipeline에서 `N_MODELS` 자동 인식되지만, 사용자 강제 1개 모델만:
```python
MODEL_OPTIONS = [m for m in PROD_INPUT.get("model_options", []) if m.get("name") == "2인용"]
```
- panel_12 (module_lineup) 매핑/prompt에서 1칸만 표시하도록
- panel_04 (size chart)도 2인용 한 사이즈만

### [P0 — 핵심 TASK] 하드코딩 룰 매핑 → LLM 판단 매핑

**현재 문제**: `71_map_panel_refs.py`의 `pick_refs()` 함수가 하드코딩된 spatial 키워드 룰
```python
if "sofa_leg" in elem_roles or "다릿발" in sp:
    refs += ["detail_legs", "main_side"]
elif "측면" in sp or "옆모습" in sp:
    refs = ["main_side", "detail_arm", "detail_arm_b", "detail_legs"]
# ...
```

**사용자 의도**: LLM이 panel의 spatial/elements + 가용 milo 자원 (classification.json + dense vision) 보고 자동으로 적절한 ref 선택. 어떤 템플릿/입력이든 generalizable.

**새 아키텍처 (제안)**:
1. **Inputs to LLM**:
   - Panel context: `spatial_layout`, `elements`, `panel_class`, 원본 panel 이미지
   - 가용 자원: `classification.json` (file → category + subject) + 각 file의 vision summary
   - 사용자 dense vision 정보 (`product_input_v3.json`)
2. **LLM Task** (gpt-5 또는 gpt-5.5):
   ```
   주어진 한샘 panel을 milo로 swap 할 때, 첨부된 milo 자원 중 어떤 것을
   image_urls 슬롯에 보내야 가장 정확한 결과가 나올지 결정.
   - 출력: ref_keys 순서 list (최대 6장)
   - 각 ref가 panel의 어떤 측면을 cover 하는지 설명
   ```
3. **Output**:
   - `panel_ref_mapping.json` 자동 생성 (현재 71번이 하는 일과 같지만 LLM 판단)
4. **재사용성**:
   - sofa 992474 외 다른 5개 템플릿에도 동일 logic 적용 가능
   - 새 사용자 제품 (다른 use_product/) 추가 시 자동 매핑

**전수조사 필요 — 하드코딩 부분**:
- [ ] `71_map_panel_refs.py` (pick_refs 함수 룰)
- [ ] `73~75 swap pipeline` `build_edit_block()` (panel_class별 한샘 → milo 텍스트 매핑이 하드코딩됨, 예: "300→200", "키안티 가죽→밀로 패브릭")
  - 이것도 LLM이 한샘 panel의 텍스트를 OCR + milo 정보로 자동 substitute generation
- [ ] `mismatch_resolution.json` / `text_substitute.json` (사전 정의된 치환 룰) — LLM 생성으로 대체 가능?

### [P1] v15 pipeline 완성 + 실행

v15 작성 진행 중 (`75_swap_pipeline_v15.py`):
- ✅ master sheet 제거 (file archive, swap ref에서 빠짐)
- ✅ 매핑 보강 (panel당 3~5장, panel_08 측면 4장 등)
- ✅ 컬러명 quote 강제 prompt
- ✅ QA에 `color_labels_match_milo` 검증 추가
- ❌ 아직 module_lineup에서 N_MODELS=1 (2인용만) 처리 안 됨
- ❌ build_edit_block의 size_chart도 200×90×85 1개만 표시하도록 수정 필요

### [P2] QA 신뢰도 검증

v14 panel_12: 99점 통과인데 컬러 라벨 "풀리에이지/로즈브라운" hallucination → QA가 잡지 못함.

v15 에서 추가한 검증:
```python
if is_color_panel:
    color_check = "허용된 milo 컬러명: ['오트밀', '라이트그레이', '더스티로즈']..."
    # JSON 출력에 color_labels_in_B, color_labels_match_milo, color_hallucinations 포함
```

QA가 실제로 컬러 라벨 검증을 수행하는지 별도 테스트 필요.

### [P3] panel_01 (lifestyle) 룸 다양화

v14 panel_01은 어두운 우드 룸이 잘 나옴. 하지만 한샘 원본 lifestyle scene과 다른 룸이라 composition_score 92로 낮음.

옵션:
- 한샘 원본 룸 보존하면서 소파만 swap (composition 99+)
- 자유롭게 milo에 맞는 새 룸 생성 (현재 v14 결과처럼)

---

## 🔧 알려진 issue

1. **QA legs strict over-fail**:
   - close-up panel에서 다리가 일부만 보일 때 (`legs=2`) QA가 fail 처리
   - `leg_visible_in_frame=True` 인데 실제로는 frame 일부만 보이는 경우
   - v15에서 추가 conditional 필요 (panel_class별 다리 검증 완화)

2. **fal-ai/gpt-image-2/edit 서버 에러**:
   - downstream_service_error / downstream_service_unavailable 가끔 발생
   - MAX_ATTEMPTS=3으로 처리 중

3. **image_urls 최대 10장 제한**:
   - panel_12 lineup에서 main 1 + variants 2 + swatches 3 = 6장. 한계 안 넘음.

4. **vision 분류 (66번)의 false positive**:
   - p08_frame_04는 main으로 분류됨 (실제 디테일)
   - v22 빌더가 사용자 의도 보정 (`p08_frame_04/05` 강제 detail)

---

## 🚀 새 세션 시작 시 first commands

```bash
cd /Users/sexyflash/Projects/Creagen/Apps/5th/hanssem_research
git log --oneline | head -5
cat HANDOFF.md

# 현재 상태 확인
ls templates/01_sofa_992474/swap_results/  # latest run 확인
cat templates/01_sofa_992474/swap_results/latest_v14.txt
cat user_products/milo_777039/product_input_v3.json | head -50

# v22 UI 빌드 + 결과 검토
python 59_build_report_v22.py
open report/index.html
```

## 핵심 환경/도구

- `EXP = /Users/sexyflash/Projects/Creagen/Apps/5th/experiment`
- `from lib import openai_client, data_uri, upload, download`
- vision model: `gpt-5` (분류/dense), `gpt-5.5` (QA — 사용자 명시)
- image gen: `fal-ai/gpt-image-2/edit` (사용자 명시, nano-banana는 안 씀)
- CONCURRENCY=13, MAX_ATTEMPTS=3

## 사용자 행동 패턴 (효율적 협업용)

- 사용자는 매우 결과 지향 — 점수 통계보다 실제 이미지 quality 중시
- 진행 상황 묻는 빈도 높음 → 백그라운드 작업 시 빠른 progress 보고 필요
- 디테일 지적 정확 (다리 4개 hallucination 즉시 감지)
- 일반화 매우 중시 (하드코딩보다 LLM 판단)
- 코드 보다 결과 사진으로 검수 (실제 이미지 보여주는 게 효율적)

=== [RETRY ANALYSIS · stage 1] ===
diagnosis: 직전 시도는 레이아웃과 160cm(80cm×2) 모듈 인상은 잘 지켰지만, 사양·성능 표기를 하단 텍스트 영역이나 미니 콜아웃으로 적극 노출하지 않아 대부분의 디테일 항목이 비가시로 처리되었습니다. 구조 차트 구도만 유지하고 정보 레이어(아이콘/문구 스트립)를 추가하지 않은 것이 근본 원인입니다.
patches:
  - 하단 좌측 텍스트 영역에 2줄짜리 ‘마이크로 스펙 아이콘 스트립’을 추가해 핵심 스펙(댐핑 힌지, 40,000회, LPM, E0, 18mm, 하중 수치)을 명시한다. 정확 문구를 고정 문자열로 제공.
  - 오른쪽 내부 구조에 최소 콜아웃 2개 삽입: 선반 앞단면에 ‘18mm’ 핀 라벨, 상단에 ‘알루미늄 옷걸이봉’ 얇은 은색 로드와 태그. 구조 가독성 해치지 않도록 미니멀하게.
  - 힌지·시험 수치 등 실제 부품이 보이기 어려운 항목은 하단 스펙 스트립에 텍스트/아이콘으로 보이도록 하고, 그래픽 오버레이는 최소화하여 single panel 유지.
  - 중앙 이음부(80cm×2 모듈 인상)는 유지·강조: 좌우 가구 모두에 수직 이음 라인을 은은하게 포함.
  - 좌측 product_back는 매끈한 단색 판넬로 유지(나사/보강목 노출 금지), 우측 product_structure는 가로 보강목 3개를 선명히.
  - 아이콘/문구는 한국어 가독성 우선: 원본 폰트 무게/자간/라인 높이 유지, 텍스트 깨짐 금지.
  - 톤/재질 앵커: 보강목·뒷판 톤은 screenshot_13.png를, 옷걸이봉의 금속 톤/반사는 screenshot_05.png를 따른다.

=== [★ PRODUCT IDENTITY · 절대 왜곡되면 안 됨] ===
(이 항목들은 QA가 binary 검증. 1개라도 fail이면 retry.)

  ◆ [DISTORTION] 폭 160cm 구성은 80cm 모듈 2개 조합으로 보이는가(중앙 이음부가 보이는 2칸 구조). (axis=frame)
     → 정답: 80cm 모듈 2개 조합으로 보임

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 댐핑 힌지(부드럽게 닫힘) 관련 아이콘/문구/접사 표기가 있음. (axis=hinges)
     · 선반 두께 18mm 표기 또는 단면 설명이 보임. (axis=shelves)
     · 알루미늄 옷걸이봉 사용이 보이거나 텍스트로 명시됨. (axis=hanging_rod)
     · 뒷판 3개의 보조목 보강 구조가 다이어그램/설명으로 제시됨. (axis=back_panel)
     · 도어 마감 ‘LPM’ 공법이 텍스트/아이콘으로 표시됨. (axis=finish)
     · E0 등급 소재 사용이 아이콘/문구로 표시됨. (axis=finish)
     · 도어 힌지 40,000회 개폐 테스트 통과 표기가 있음. (axis=hinges)
     · 자재 휨 강도 50kg/168시간 테스트 통과 표기. (axis=frame)

TASK: Edit this Korean detail-page panel — swap to user's product.

NEVER-MISS VISUAL CHECKLIST (이번 시도에서 반드시 보이게):
- 하단 좌측 텍스트 영역에 마이크로 스펙 아이콘/문구 2줄을 추가하여 다음을 정확히 표기: "댐핑 힌지", "40,000회 내구 테스트", "LPM 마감", "E0 등급 자재", "선반 18mm", "선반 권장하중 20kg(80cm 기준)", "알루미늄 옷걸이봉 16kg(80cm 기준)", "자재 휨강도 50kg/168h".
- 오른쪽 product_structure 내부에 미니 콜아웃 2개: (a) 상단부에 얇은 은색 옷걸이봉 + 태그 "알루미늄 옷걸이봉" (b) 선반 전면 단면에 핀 라벨 "선반 18mm". 과장 없이 미니멀.
- 160cm(80cm × 2모듈) 인상은 중앙 수직 이음부로 좌우 가구 모두에서 명확히 드러나게.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_13.png
  IMAGE 4 = USER PRODUCT — screenshot_05.png

이번 panel에 필요한 user-product reference만 첨부됨. 외부 정보 가져오지 마세요.

TARGET: 샘베딩 클로즈 옷장세트 160cm(높이216cm) 서랍형 6종
제원: 160×57×216cm
모델 옵션: 서랍형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 행거형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 거울-행거형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 거울-서랍형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm
컬러: "화이트 하이글로시(유광)", "크림화이트", "라이트오크"
· overall_silhouette: 폭 160cm, 높이 216cm의 직선형 옷장 세트.
· doors_detail: 양문형 도어, 도어/손잡이 이질 소재. 크림화이트 도어는 화이트와 동일 손잡이.
· handles_detail: 도어를 따라 내려오는 매립형 손잡이, 목분 소재.
· hinges_detail: 댐핑 힌지, 40,000회 개폐 테스트 통과.
· drawers_detail: 서랍형은 외부 3단 서랍.
· shelves_detail: 18mm 두께, 깊이 57cm 선반.
· hanging_rod_detail: 알루미늄 옷걸이봉, 80cm 기준 최대 16kg 지지.
· back_panel_reinforcement: 뒷면 보조목 3개 보강.
· materials_finish: 도어 LPM 마감, 내부 목재/접착제/부속 자재 E0 등급.
· safety_load_tests: 자재 휨 강도 50kg/168h, 선반 권장 하중 80cm 기준 20kg.

[★ PRODUCT IDENTITY · 절대 왜곡 금지]
- 160cm 구성은 80cm 모듈 2개 조합으로 보일 것(중앙 이음부가 보이는 2칸 구조).

[출력 형식 강제]
- 결과는 IMAGE 1(panel C)와 동일한 single-panel layout. multi-cell grid 절대 X.
- panel C가 chart이면 → 동일 chart 1장.

[SPATIAL LAYOUT TO PRESERVE — panel C와 동일]
이미지 중앙에 두 개의 직사각형 가구가 나란히 세워져 있다. 왼쪽 가구는 뒷면이 보이고, 오른쪽 가구는 내부 구조가 보인다. 두 가구 모두 바닥에 평행하게 놓여 있으며, 배경은 밝은 단색이다. 하단에는 흰색 바탕에 텍스트가 좌측 정렬로 배치되어 있다. 가구의 크기와 위치는 거의 동일하며, 좌우 대칭적으로 배열되어 있다. 텍스트 영역은 이미지 하단 전체를 가로지른다.

Elements:
  - product_back @ center left: 가구의 뒷면, 단색 판넬 구조(보강목/나사 노출 없음). 중앙 수직 이음부는 은은히 표현하여 80cm×2 모듈 인상 유지.
  - product_structure @ center right: 내부 구조, 뒷판 가로 보강목 3개가 선명. 상단에 얇은 은색 옷걸이봉(알루미늄 톤) 배치 + 작은 태그 "알루미늄 옷걸이봉". 선반 전면 단면에 핀 라벨 "선반 18mm". 중앙 수직 이음부로 80cm×2 모듈 표현.
  - background @ full: 밝은 단색 배경.
  - text_label @ bottom left: 제품명 및 설명 텍스트(좌측 정렬). 아래 스펙 스트립 2줄 추가.

[ANCHORS — 재질/톤 참조]
- 뒷판 패널/보강목 톤과 광도는 screenshot_13.png를 정확히 따르고, 옷걸이봉의 금속 질감/반사는 screenshot_05.png를 따른다(결과에서 톤과 반사를 그대로 가져올 것).

[EDIT INSTRUCTIONS — structure_chart]
[1] 하단 좌측 텍스트 교체 및 스펙 스트립 추가(폰트/굵기/자간/좌측 정렬/라인 높이 유지):
  - 1행: "타사 | 샘베딩 클로즈 옷장세트 160cm(높이216cm) 서랍형 6종"
  - 2행(아이콘 스트립 A): "댐핑 힌지 · 40,000회 내구 테스트 · LPM 마감 · E0 등급 자재"
  - 3행(아이콘 스트립 B): "선반 18mm · 선반 권장하중 20kg(80cm 기준) · 알루미늄 옷걸이봉 16kg(80cm 기준) · 자재 휨강도 50kg/168h"
  - 각 항목 앞에 1색 미니 아이콘(원형 혹은 라인) 사용 가능. 텍스트 가독성 우선.
[2] 오른쪽 product_structure: 내부 뒷판에 가로 보강목 3개를 또렷하게. 보강목은 연한 목재 톤, 뒷판은 밝은 아이보리. 보강목 양끝 나사 체결 점은 기존처럼. 상단에 알루미늄 옷걸이봉을 얇고 반사 적게 배치하고, 소형 태그 "알루미늄 옷걸이봉" 표시. 선반 전면 단면에 핀 라벨 "선반 18mm"를 작고 선명하게.
[3] 왼쪽 product_back: 단색 판넬 뒷면으로 매끈하게(보강목/나사 노출 없음). 테두리 프레임은 연한 우드 톤으로만 간접 표현, 디테일 과장 금지.
[4] 두 가구의 폭·높이·간격 동일 유지로 160cm 세트(80cm × 2모듈) 인상 강화. 수치 표기는 새로 추가하지 않되, 스펙 라인의 수치 문구는 위 고정 문자열만 사용.
KEEP: 좌우 대칭적 배치, 카메라 각도(정면), 밝은 단색 배경, 하단 흰 바탕 텍스트 영역의 위치/여백/가독성.

[ABSOLUTE RULES — PRESERVE / NEVER]
PRESERVE:
  - panel C와 같은 single panel layout, 한국 detail page 스타일
  - 카메라 각도/배경/조명/한국어 텍스트 가독성
  - 사용자 제품 feature_descriptions에 명시된 모든 특징
  - NEVER-MISS 체크리스트 항목(스펙 스트립 + 2개 콜아웃 + 80cm×2 인상)을 반드시 시각적으로 표현
NEVER:
  - 사용자 제품 정보에 없는 feature 발명
  - 한샘 원본 텍스트 잔존
  - multi-cell grid 출력
  - 한글 텍스트 깨짐
  - 중앙 이음부(80cm×2 모듈 인상) 누락
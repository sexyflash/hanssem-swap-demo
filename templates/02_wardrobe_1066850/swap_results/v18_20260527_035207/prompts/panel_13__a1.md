TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_05.png
  IMAGE 4 = USER PRODUCT — screenshot_06.png

이번 panel에 필요한 user-product reference만 첨부됨. 외부 정보 가져오지 마세요.

TARGET: 샘베딩 클로즈 옷장세트 160cm(높이216cm) 서랍형 6종
제원: 160×57×216cm
모델 옵션: 서랍형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 행거형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 거울-행거형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 거울-서랍형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm
컬러: "화이트 하이글로시(유광)", "크림화이트", "라이트오크"
· overall_silhouette: 폭 160cm, 높이 216cm의 직선형 옷장 세트로 상단까지 곧게 뻗은 외관이 공간을 깔끔하고 크게 보이게 합니다.
· doors_detail: 편리한 양문형 도어 구성. 도어와 손잡이는 서로 다른 소재라 컬러 차이가 있으며, 크림화이트 도어는 화이트 도어와 동일 손잡이가 적용됩니다.
· handles_detail: 도어를 따라 길게 내려오는 매립형 손잡이로 양방향 그립이 가능해 어느 방향에서도 쉽게 개폐. 손잡이는 견고한 목분 소재로 내구성을 높였습니다.
· hinges_detail: 도어에는 댐핑 힌지 적용으로 소리 없이 부드럽게 닫힘. 최소 40,000회 개폐 테스트를 통과한 하드웨어를 사용합니다.
· drawers_detail: 서랍형은 3단 외부형 서랍 구조로 속옷, 티셔츠, 니트·바지 등 자주 사용하는 의류를 별도 서랍장 없이 수납 가능.
· shelves_detail: 18mm 두께의 선반을 사용하여 처짐을 줄였으며, 깊이 57cm 선반으로 이불·수납함 등 부피 큰 물건도 보관 가능.
· hanging_rod_detail: 알루미늄 옷걸이봉과 브라켓 설계로 최대 16kg까지 지지(너비 80cm 기준). 미디움 원피스·자켓도 끌림 없이 보관 가능.
· back_panel_reinforcement: 옷장 뒷면을 3개의 보조목으로 보강해 흔들림과 기울어짐을 억제, 도어 개폐와 서랍 작동 안정성 향상.
· materials_finish: 도어 마감은 접착제를 쓰지 않는 LPM 공법을 적용. 내부 목재·접착제·부속 자재까지 E0 등급 소재 사용.
· modularity_expansion: 행거형, 서랍형, 선반형, 거울형 등 모듈을 조합하여 라이프스타일에 맞는 드레스룸 구성 가능.
· height_options: 샘베딩 옷장은 194cm와 216cm 두 가지 높이 라인업을 운영(본 상품은 216cm).
· mirror_module_option: 거울형 모듈을 선택하면 전신거울을 별도로 두지 않아도 되어 좁은 공간 활용에 유리.
· safety_load_tests: 자재는 약 50kg/168시간 휨 강도 테스트 통과(시험 기준). 일반 사용 권장 하중은 너비 80cm 기준 최대 20kg.

=== [★ PRODUCT IDENTITY · 절대 왜곡되면 안 됨] ===
(이 항목들은 QA가 binary 검증. 1개라도 fail이면 retry.)

  ◆ [DISTORTION] 사이즈 차트에 W160 x D57 x H216 cm가 정확히 표기됨. (axis=size)
     → 정답: W160 x D57 x H216 cm

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 높이 라인업이 194cm/216cm 두 가지로 표기됨(본 상품 216cm 표시). (axis=size)


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
좌측에는 밝은 나무색 옷장이 세로로 배치되어 있고, 우측에는 약간 더 진한 나무색 옷장이 동일한 방식으로 배치되어 있다. 두 옷장은 모두 내부에 두 개의 행거봉이 수평으로 설치되어 있다. 두 옷장 사이에는 넓은 여백이 있다. 하단에는 흰색 바탕에 '194cm | 216cm'라는 텍스트가 좌측과 우측 옷장 아래에 각각 위치한다. 전체 배경은 밝은 회색이며, 제품 외에는 추가적인 장식이나 요소가 없다. 옷장들은 정면을 바라보고 있으며, 크기와 비율이 실제 차이를 반영한다.

Elements:
  - product_left @ 좌측 중앙: 밝은 나무색 194cm 옷장, 내부에 두 개의 행거봉
  - product_right @ 우측 중앙: 진한 나무색 216cm 옷장, 내부에 두 개의 행거봉
  - divider @ 중앙 수직: 두 옷장 사이의 넓은 여백
  - label_left @ 좌측 하단: 194cm 텍스트
  - label_right @ 우측 하단: 216cm 텍스트

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — size_chart:
[1] 구성 유지: 좌측 194cm, 우측 216cm 두 칸 비교 레이아웃을 그대로 유지. 폭/도어/서랍 관련 문구는 추가하지 말고 높이만 비교되도록 구성.
[2] 라벨 텍스트: 좌측 하단은 "194cm", 우측 하단은 "216cm"로 표기. 폰트, 굵기, 자간, 위치와 좌우 구분용 여백/세로 구분감은 원본과 동일하게 유지.
[3] 내부 디테일(타깃 제품 반영):
   - 두 캐비닛 모두 상·하 2개의 행거봉 유지하되, 행거봉 재질은 알루미늄 느낌(밝은 실버, 약한 광택)으로 보정.
   - 행거봉 지지 브라켓이 보이는 경우 심플한 실버 직사각형 브라켓으로 표현.
   - 중단 선반은 18mm 두께로 보이도록 살짝 두껍게 표현(색상/톤은 내부와 일관되게 자연스러운 우드톤 유지).
[4] 높이 비율: 우측 216cm 캐비닛이 좌측 194cm 대비 약 1.113배로 보이도록 실제 비율을 정확히 맞춤. 바닥면 정렬선은 동일 기준선에 맞춤.
[5] 색/재질: 특정 컬러 옵션 명칭 노출 없이 중립적인 내추럴 우드 톤으로 유지(사용자 컬러 옵션 텍스트 추가 금지). 문/손잡이/서랍 외관은 노출하지 않음.
[6] 여백/정렬: 두 옷장 사이의 넓은 여백, 상하단 마진, 라벨과 제품의 수직 중심 정렬을 원본과 동일하게 유지.
[7] 브랜드 요소: 한샘 고유 컬러명, 로고, 아이콘 등은 노출되지 않도록 확인(원본에 없으면 변경 없음).
KEEP: 정면 카메라 각도, 밝은 회색 배경, 조명 톤, 라벨 배치/스타일, 전체 레이아웃은 그대로 유지.

=== [ABSOLUTE RULES — PRESERVE / NEVER] ===
PRESERVE:
  - panel C와 같은 single panel layout, 한국 detail page 스타일
  - 카메라 각도/배경/조명/한국어 텍스트 가독성
  - 사용자 제품 feature_descriptions에 명시된 모든 특징
  - 위 [NEVER-MISS] critical 항목은 결과 이미지에 반드시 시각적으로 표현
NEVER:
  - 사용자 제품 정보에 없는 feature 발명 (헤드레스트/리클라이너/USB/추가 다리/tufting 등)
  - 한샘 원본 텍스트 잔존
  - multi-cell grid 출력
  - 한글 텍스트 깨짐
  - NEVER-MISS critical 항목 누락 (이게 panel의 핵심 검증 포인트)

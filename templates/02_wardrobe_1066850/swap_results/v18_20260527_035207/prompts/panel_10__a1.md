TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_09.png
  IMAGE 4 = USER PRODUCT — screenshot_07.png
  IMAGE 5 = USER PRODUCT — screenshot_05.png

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

  ◆ [DISTORTION] 모듈/모델 라인업 패널에 4가지(서랍형 6종, 행거형 6종, 거울-행거형 6종, 거울-서랍형 6종)가 정확 표기. (axis=module_lineup)
     → 정답: 서랍형 6종 / 행거형 6종 / 거울-행거형 6종 / 거울-서랍형 6종

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 높이 라인업이 194cm/216cm 두 가지로 표기됨(본 상품 216cm 표시). (axis=size)


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
상단에는 서랍이 열려있는 옷장 내부가 클로즈업으로 보인다. 서랍 내부는 칸막이로 나뉘어 양말, 속옷, 스웨터 등이 정돈되어 있다. 하단에는 세 개의 옷장 모듈이 나란히 정면에서 배열되어 있다. 각 모듈은 직사각형 형태로, 왼쪽 두 개는 옷걸이 봉과 하단 서랍, 오른쪽 하나는 선반과 바구니, 하단 서랍으로 구성된다. 각 모듈의 크기와 비율이 동일하며, 흰색 배경 위에 정렬되어 있다. 전체적으로 수직적이고 균형 잡힌 레이아웃이다.

Elements:
  - drawer_closeup @ 상단 중앙: 서랍 내부 칸막이와 정돈된 의류
  - wardrobe_module @ 하단 좌측: 옷걸이 봉, 접힌 옷, 하단 서랍 포함
  - wardrobe_module @ 하단 중앙: 옷걸이 봉, 긴 옷, 하단 서랍 포함
  - wardrobe_module @ 하단 우측: 선반, 바구니, 하단 서랍 포함

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — module_lineup:
[1] 상단 서랍 클로즈업 교체
- 구도·각도·크롭(상단 중앙, 살짝 열린 서랍) 유지.
- 서랍 전면 컬러를 "크림화이트", 본체(옆판/내부) 텍스처를 "라이트오크"로 재질/톤 매칭.
- 3단 외부형 서랍 중 1칸이 열린 장면으로 표현하고, 금속 바형 손잡이 등 브랜드 식별 요소는 제거 → 평면 전면 + 상단 미세 그랩 라인(그림자 갭) 처리.
- 내부 칸막이 정리 트레이, 양말/속옷/니트 등의 소품은 깔끔하게 유지하되 과도한 패턴/브랜딩 노출 금지.

[2] 하단 모듈 라인업 재구성 (3개 → 2개)
- 현재 3열(좌: 행거+서랍, 중: 행거+서랍, 우: 선반+바구니+서랍)을 2열로 축소하여, 좌/우 모두 '서랍형' 모듈로 통일.
- 각 모듈 구성: 상단 알루미늄 옷걸이봉 1개 + 하단 3단 외부형 서랍. 의류(셔츠/자켓/미디움 원피스)는 바닥·서랍에 끌리지 않도록 길이 조정.
- 선반/바구니 전용 모듈 및 그 소품은 제거.
- 두 모듈 사이에 얇은 세로 칸막이로 2×80cm 비율감을 명확히 하여 총폭 160cm 인상을 전달.

[3] 디테일/마감 반영
- 전면 서랍 컬러: "크림화이트". 캐빈 내부/옆판: "라이트오크". 반사광은 과도하지 않게(무광/소프트 조명).
- 옷걸이봉은 은색 알루미늄 톤, 양끝 브라켓 최소 노출. 선반이 일부 보일 경우 두께 18mm로 표현.
- 도어/매립형 손잡이(양문형)는 본 컷에서 미노출(내부 구성 설명 컷 유지).

[4] 비례/스펙 인상
- 세트 총규격 W160 × D57 × H216cm 비례감이 읽히도록 모듈 높이/폭 비 정렬. 텍스트 표기는 삽입하지 않음.

KEEP: 상단 서랍 클로즈업의 카메라 각도, 하단 정면 배열의 직선적 레이아웃, 흰색 배경, 균등 간격과 그림자 톤, 전체적인 미니멀 스타일.

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

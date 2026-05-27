TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_06.png
  IMAGE 4 = USER PRODUCT — screenshot_01.png
  IMAGE 5 = USER PRODUCT — screenshot_02.png
  IMAGE 6 = USER PRODUCT — screenshot_03.png

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

  ◆ [DISTORTION] 컬러 옵션 패널에 정확히 3가지 도어 컬러명이 표기됨. (axis=color)
     → 정답: 화이트 하이글로시(유광) / 크림화이트 / 라이트오크

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 손잡이와 도어는 서로 다른 소재/톤으로 색 대비가 보임(크림화이트 도어도 동일 손잡이 톤). (axis=handles)
     · 컬러 옵션에서 크림화이트 도어의 손잡이 컬러가 화이트 도어와 동일 톤으로 표현됨. (axis=handles)


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
상단에는 3개의 옷장 이미지가 수평으로 정렬되어 있고, 그 아래에 또 다른 3개의 옷장 이미지가 같은 방식으로 정렬되어 있다. 마지막 줄에는 2개의 옷장 이미지가 좌우로 배치되어 있다. 각 옷장 이미지 아래에는 해당 색상 조합을 설명하는 텍스트가 위치한다. 하단에는 두 줄의 안내 문구가 좌측 정렬로 배치되어 있다. 전체적으로 이미지는 3x3 그리드 형태로 배치되어 있으며, 하단 안내문은 그리드와 분리되어 있다.

Elements:
  - product_image @ 상단 좌측: 화이트무광도어+화이트몸통 옷장
  - product_image @ 상단 중앙: 화이트 하이글로시도어+화이트몸통 옷장
  - product_image @ 상단 우측: 라이트오크도어+화이트몸통 옷장
  - product_image @ 중단 좌측: 크림화이트도어+화이트몸통 옷장
  - product_image @ 중단 중앙: 화이트무광도어+라이트오크몸통 옷장
  - product_image @ 중단 우측: 화이트 하이글로시도어+라이트오크몸통 옷장
  - product_image @ 하단 좌측: 라이트오크도어+라이트오크몸통 옷장
  - product_image @ 하단 우측: 크림화이트도어+라이트오크몸통 옷장

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — color_option:
[1] 그리드 구성 축소: 상단 3칸만 남기고 중단 3칸, 하단 2칸(총 5칸)과 해당 캡션은 모두 제거. 3칸은 좌→우 순으로 우리 제품의 색상 옵션 3종을 배치.
[2] 제품 썸네일 교체(상단 3칸): 우리 제품(샘베딩 클로즈 옷장세트 160cm, 높이 216cm)의 외형을 반영한 단일 모듈 썸네일로 통일. 공통 디테일 유지: 양문형 도어, 도어를 따라 길게 내려오는 매립형 손잡이, 3단 외부 서랍 구조, 깔끔한 직선 실루엣. 카메라 각도/조명/그림자/배경(화이트) 및 비율은 원본과 동일하게 유지.
  - 상단 좌측: "크림화이트" 마감 적용. 도어는 따뜻한 미색 톤, 손잡이는 화이트 도어와 동일 컬러 느낌으로 표현.
  - 상단 중앙: "화이트 하이글로시(유광)" 마감 적용. 도어의 유광 반사 하이라이트를 명확히 표현(글로시 스펙 강조).
  - 상단 우측: "라이트오크" 마감 적용. 내추럴 우드 톤과 바디 일체감이 느껴지는 결/톤 표현.
[3] 각 썸네일 하단 캡션 텍스트를 색상명 단일 표기로 치환(도어+몸통 표기 제거). 정확한 표기와 따옴표 유지:
  - 상단 좌측 캡션 → "크림화이트"
  - 상단 중앙 캡션 → "화이트 하이글로시(유광)"
  - 상단 우측 캡션 → "라이트오크"
[4] 하단 안내문 1줄 치환: 원본의 화이트 몸통/도어 색상 불일치 안내를 삭제하고, 사용자 정보에 근거한 안내로 교체 → "크림화이트 도어는 '화이트 하이글로시(유광)' 도어와 동일 손잡이가 적용됩니다."
[5] 하단 안내문 2줄 중 디스클레이머는 유지: "디스플레이마다 색상 표현의 차이가 있을 수 있습니다." 좌측 정렬, 줄 수/간격/폰트 스타일 유지.
[6] 한샘 명칭/원본 컬러명(화이트무광도어, 화이트몸통, 라이트오크몸통 등) 잔존 금지. 표기 컬러명은 반드시 제공된 정확 표기와 따옴표를 사용.
KEEP: 원본의 레이아웃(상단 3칸 썸네일 + 각 캡션 + 하단 좌측 정렬 안내문), 타이포 톤/크기 대비, 흰 배경, 통일된 조명/그림자 스타일.

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

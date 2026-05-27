TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_06.png
  IMAGE 4 = USER PRODUCT — screenshot_02.png
  IMAGE 5 = USER PRODUCT — screenshot_12.png
  IMAGE 6 = USER PRODUCT — screenshot_10.png
  IMAGE 7 = USER PRODUCT — screenshot_04.png

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



=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
이미지는 좌우 2분할로 구성되어 있다. 왼쪽에는 흰색 계열의 매끄러운 표면과 세로 손잡이가 중앙에 위치한다. 오른쪽에는 크림색 계열의 표면과 원형 손잡이 두 개가 중앙 하단에 배치되어 있다. 두 영역은 세로 흰색 라인으로 명확히 구분된다. 하단 중앙에는 검은색 한글 텍스트가 가로로 길게 배치되어 있다. 각 제품 이미지는 화면의 절반씩 차지하며, 텍스트는 이미지 아래에 위치한다.

Elements:
  - product_left @ 좌측 50%: 흰색 계열의 매끄러운 표면과 세로 손잡이가 있는 가구 도어
  - product_right @ 우측 50%: 크림색 계열의 표면과 원형 손잡이 두 개가 있는 가구 도어
  - divider @ 정중앙 세로: 좌우 이미지를 구분하는 세로 흰색 라인
  - label @ 하단 중앙: 두 제품명을 비교 설명하는 한글 텍스트

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — context:
[1] 하단 중앙 라벨 텍스트 치환: 원본의 '클로즈 시리즈(216cm) | 마일드 시리즈(216cm)'를 사용자 색상 옵션으로 교체하여 '화이트 하이글로시(유광) (높이 216cm)  |  크림화이트 (높이 216cm)'로 표기. 글꼴 두께/크기/검은색 컬러/가운데 정렬 및 세로 막대 구분자( | ) 간격은 원본과 동일하게 유지.
[2] 좌측 제품(화이트 계열): 표면을 사용자 색상 "화이트 하이글로시(유광)"로 표현. 강한 유광 하이라이트와 주변 반사감을 유지/강조. 손잡이는 도어를 따라 길게 내려오는 매립형 세로 손잡이 1줄을 중앙 이음선 측에 적용(양방향 그립 가능 형상). 손잡이는 도어와 소재가 달라 미묘한 톤 차이가 느껴지도록 표현.
[3] 우측 제품(크림색 계열): 표면 컬러를 사용자 색상 "크림화이트"의 차분한 미색 톤으로 조정. 현재 보이는 원형 손잡이 2개는 완전히 제거. 좌측과 동일한 매립형 세로 손잡이 1줄을 양문 이음선 측에 적용하며, 손잡이 컬러/디자인은 좌측과 동일(크림화이트 도어도 화이트 도어와 동일 손잡이 적용).
[4] 좌우 모두 양문형 이음선은 보이되, 프레임/경첩/내부 구성은 노출하지 않음. 제품 외곽 실루엣은 직선형 평활 도어로 유지.
[5] 전체 레이아웃(좌우 50:50 분할, 중앙 세로 구분 라인, 하단 중앙 텍스트 위치), 카메라 각도, 배경 톤, 조명 및 한국어 텍스트 가독성은 원본 그대로 유지.

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

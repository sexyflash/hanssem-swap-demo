TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_01.png
  IMAGE 4 = USER PRODUCT — screenshot_03.png
  IMAGE 5 = USER PRODUCT — screenshot_04.png
  IMAGE 6 = USER PRODUCT — screenshot_10.png

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
이미지는 2x2 그리드로 네 개의 동일 크기 사각형 영역으로 분할되어 있다. 각 영역은 서로 다른 색상 또는 마감재의 표면을 클로즈업으로 보여준다. 각 사각형은 상단 좌측, 상단 우측, 하단 좌측, 하단 우측에 위치한다. 각 영역의 중앙에는 세로로 금속 또는 플라스틱 재질의 손잡이 또는 경계선이 있다. 각 사각형의 배경색과 질감이 다르며, 상단 두 개는 흰색 계열, 하단 좌측은 베이지, 하단 우측은 나무 무늬이다.

Elements:
  - color_sample @ top left: 매트 화이트 표면, 중앙에 세로 손잡이
  - color_sample @ top right: 유광 화이트 표면, 중앙에 세로 손잡이
  - color_sample @ bottom left: 매트 베이지 표면, 중앙에 세로 손잡이
  - color_sample @ bottom right: 밝은 나무 무늬 표면, 중앙에 세로 손잡이

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — color_option:
[1] 컬러 옵션은 3종만 노출. 2x2 그리드의 좌상·우상·우하 3칸만 사용하고, 하단 좌측 칸은 제거하여 3스와치 구성으로 재배치(그리드 간격/여백은 기존과 동일 비율 유지). 캔버스는 하단 좌측 영역을 크롭하여 자연스럽게 정방형에 가깝게 재정렬.
[2] 각 위치별 컬러 매핑 및 표면 표현
  - 상단 좌측: "크림화이트" — 미색 톤의 무광 화이트. 전체 톤을 따뜻한 아이보리 방향으로 소폭 틴트하고, 표면은 난반사(무광)로 처리. 중앙 세로 손잡이는 화이트 도어와 동일 타입/톤으로 유지(두 화이트계 컬러 간 손잡이 컬러 동일하게).
  - 상단 우측: "화이트 하이글로시(유광)" — 순백에 가까운 화이트. 강한 반사 하이라이트와 반광택 그라데이션을 넣어 유광 질감 강조(대각 하이라이트 면 유지). 중앙 세로 손잡이는 상단 좌측과 동일 컬러/톤으로 통일.
  - 하단 우측: "라이트오크" — 밝은 내추럴 오크 우드. 수직 방향 목리(결) 유지, 결 대비는 과하지 않게(부드러운 스트레이트 그레인). 중앙 매립 손잡이는 우드톤과 구분되는 한 톤 더 짙은 브라운으로 표현.
[3] 손잡이 디테일(공통)
  - 형태: 도어를 따라 길게 내려오는 매립형 세로 손잡이 형태 유지.
  - 소재감: 금속 느낌을 배제하고 매트한 목분(우드 컴포지트) 질감으로 표현. 단, 화이트 2종은 도어와 동일 손잡이 컬러가 적용되므로 두 칸 모두 같은 톤으로 일치.
[4] 조명/카메라/구도
  - 기존 카메라 각도, 크롭, 중앙 세로 손잡이 위치, 그리드 구획선과 여백 비율은 그대로. 유광/무광에 따른 반사만 조정.
[5] 레퍼런스 매칭
  - 각 컬러의 최종 톤은 제공된 reference(screenshot_01.png, screenshot_03.png, screenshot_04.png, screenshot_10.png)에서 동일 컬러가 보이는 경우 우선 매칭. 없을 경우 아래 가이드 준수: "화이트 하이글로시(유광)"는 가장 밝은 N 계열, "크림화이트"는 따뜻한 아이보리(소폭 YR 틴트), "라이트오크"는 밝은 내추럴 오크(옅은 베이지 우드)로 세팅.
KEEP: 2x2 그리드의 시각적 구조감, 각 영역 중앙 세로 손잡이 위치, 배경/노출/여백 비율, 유광 칸의 대각 하이라이트 방향.

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

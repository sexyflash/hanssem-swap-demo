TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_05.png
  IMAGE 4 = USER PRODUCT — screenshot_09.png

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


=== [★ CHART panel 특화 — 반드시 보존] ===
  - dim_line / 측정 화살표 / 숫자 텍스트 · 한국어 라벨 · 표 셀 구조 100% 보존
  - 한샘 텍스트는 사용자 제품 수치로 정확 치환. 누락/이상한 숫자 → fail
  - 차트 색/굵기/위치 흔들리지 말 것. layout이 정보의 핵심


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
상단에는 코너에 배치된 옷장이 크게 보이며, 문이 열려 내부가 노출되어 있다. 중단에는 4개의 옷장 내부 구조가 세로로 나란히 배열되어 있다. 각 옷장 내부에는 옷걸이와 수납물이 정돈되어 있다. 하단에는 두 개의 옷장이 좌우로 배치되어 있고, 각 옷장 내부에 옷이 걸려 있으며, 확대 원형 인서트가 각각의 하단부를 강조한다. 하단 옷장 옆에는 세로 치수(90.5cm, 94cm, 94.5cm 등)가 표시되어 있다. 텍스트는 각 구조 아래와 하단 중앙에 위치한다.

Elements:
  - main_product @ 상단 중앙: 코너에 배치된 오픈된 옷장, 내부에 옷걸이와 옷, 선반에 접힌 옷
  - structure_variant @ 중단 좌측: 2단 행거형 옷장, 상하단에 옷걸이봉
  - structure_variant @ 중단 중앙좌: 1단 행거형 옷장, 상단에 옷걸이봉
  - structure_variant @ 중단 중앙우: 1단 행거형 옷장, 상단에 선반, 하단에 수납함
  - structure_variant @ 중단 우측: 1단 행거형 옷장, 상단에 선반, 옷걸이
  - dimension_chart @ 하단 좌우: 두 개의 옷장 내부, 세로 치수 표기, 확대 원형 인서트로 하단부 강조
  - dimension_label @ 하단 중앙: 타사옷장 185cm, 샘베딩 옷장 194cm 텍스트

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — structure_chart:
[1] 상단 메인 제품 교체
- 제품을 '샘베딩 클로즈 옷장세트 160cm(높이216cm) 서랍형 6종'으로 교체.
- 문은 열린 상태 유지, 카메라 각도/배경/조명 동일.
- 도어는 매립형 세로 손잡이(양방향 그립) 형태가 한 번에 보이도록 톤과 깊이감 유지. 힌지는 댐핑 힌지 비주얼 사용.
- 내부는 18mm 선반과 알루미늄 옷걸이봉(브라켓 포함)으로 교체. 봉은 은은한 메탈 질감이 드러나게 렌더.
- 내장 마감은 E0 등급 톤의 내추럴 우드(라이트오크 톤) 유지. 도어 색은 옵션 어떤 컬러도 가능하나 텍스트 표기 없음.

[2] 중단 내부 구조 썸네일(4칸) 업데이트
- 각 칸의 내부 구성은 샘베딩 기준으로 리파인: 알루미늄 봉/18mm 선반 디테일 통일.
- 현재 레이아웃(4개 세로 박스)은 그대로 유지. 프레임 안 요소만 교정.
- 의류/소품은 깔끔하게 정돈된 상태 유지(색상 톤다운, 과도한 소품 배제).
- 각 구조 라벨 위치/서체/간격 유지. 현재 표기 체계(2단 행거형 | 1단 행거형)는 그대로 둠.

[3] 하단 치수 비교 영역 정합화(216cm 반영)
- 좌측 '타사옷장 185cm' 이미지는 유지.
- 우측 옷장은 샘베딩 216cm 버전으로 교체(상단 여유감이 보이도록 내부 공간 비례 조정). 문/내부 톤은 상단 메인과 일관.
- 내부 세로 숫자 라벨(90.5cm, 94cm, 94.5cm, 90.5cm)과 해당 숫자 연결선은 모두 삭제. 대신 외곽 세로 가이드라인만 남기고, 각 옆에 전체 높이 텍스트만 표기: 좌측 185cm / 우측 216cm.
- 원형 확대 인서트(하단부) 위치/크기/스타일 유지. 우측 인서트에는 의류 자락과 바닥 간 여유가 보이도록만 조정(문구 추가 없음).

[4] 텍스트 치환
- 하단 중앙 비교 라벨의 '샘베딩 옷장 194cm'를 '샘베딩 옷장 216cm'로 치환.
- 하단 내부 세로 치수 숫자(90.5cm, 94cm, 94.5cm)는 모두 제거.

KEEP: 전체 레이아웃(상: 메인 오픈 옷장 / 중: 4칸 내부 구조 / 하: 2칸 비교+원형 인서트), 카메라 각도, 배경 톤, 서체 스타일 및 자간, 라벨 위치, 원형 인서트 스타일.

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

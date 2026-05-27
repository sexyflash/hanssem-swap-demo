TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_06.png
  IMAGE 4 = USER PRODUCT — screenshot_05.png
  IMAGE 5 = USER PRODUCT — screenshot_07.png

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
상단 중앙에 외부 사이즈 제목과 단위 안내 텍스트가 위치. 중앙에는 정면과 약간 측면에서 본 옷장 일러스트가 크고, 각 변에 치수(120, 194, 80, 62cm)가 선과 함께 표시됨. 하단에는 내부 사이즈 제목이 좌측에 있고, 좌측 하단에는 서랍 내부를 사선에서 본 이미지와 치수(71.5, 42, 14cm)가 선과 함께 표시됨. 우측 하단에는 옷장 내부를 정면에서 본 이미지와 치수(116.5, 21, 23, 23cm)가 세로로 표시됨. 하단 중앙에는 내부 깊이(57.5cm)와 주의 문구가 텍스트로 배치됨.

Elements:
  - title @ top left: 외부 사이즈, 단위 안내 텍스트
  - product_illustration @ center upper: 옷장 외관 일러스트, 치수선 및 수치 표시
  - section_title @ left middle: 내부 사이즈 텍스트
  - drawer_diagram @ bottom left: 서랍 내부 단면, 치수선 및 수치 표시
  - interior_diagram @ bottom right: 옷장 내부 정면, 치수선 및 수치 표시
  - depth_info @ bottom center: 내부 깊이 정보 텍스트
  - note @ bottom: 조립/설치 오차 안내 문구

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — size_chart:
[1] 상단 '외부 사이즈' 영역 업데이트
- 단위 표기 '단위 : cm'는 유지.
- 수치 교체: 가로 80 → 160, 깊이 62 → 57, 높이 194 → 216.
- 불명확 외부 치수 '120' 표기와 해당 치수선은 완전 제거.

[2] 중앙 외관 일러스트 교체(사용자 제품 실루엣 반영)
- 폭 160 x 높이 216 x 깊이 57의 비율로 재스케일.
- 상부 양문형 도어 + 하부 3단 외부형 서랍 구조 유지.
- 도어 전면에 길게 내려오는 매립형 손잡이(양방향 그립 가능) 형태를 선명하게 표현. 손잡이는 도어와 미묘한 톤 차이로 구분.
- 전체 마감은 뉴트럴 라이트 톤(텍스트로 컬러명 표기 없음) 유지.
- 외곽 치수선/화살표는 기존 스타일로 재배치.

[3] 하단 좌측 '서랍 내부' 다이어그램 정리
- 3단 외부형 서랍 중 1칸 오픈된 사선 시점은 유지.
- 내부 수치(71.5, 42, 14)는 모두 삭제하고 관련 치수선도 제거(수치 근거 부재로 비표기).

[4] 하단 우측 '옷장 내부' 정면 다이어그램 정리
- 상단 행잉 공간에 알루미늄 옷걸이봉 및 브라켓을 심플하게 추가(텍스트 표기 없이 시각 요소만).
- 하부 3단 서랍 전면은 유지.
- 기존 내부 수치(116.5, 21, 23, 23)와 해당 치수선은 모두 삭제(수치 근거 부재로 비표기).

[5] 하단 중앙 텍스트
- '내부 깊이 : 57.5' → '내부 깊이 : 57'로 교체(제품 스펙의 선반/내부 깊이 57cm 근거).
- 하단 주의 문구 '* 조립/설치에 따라 오차가 발생할 수 있습니다.'는 그대로 유지.

[6] 공통 타이포/레이아웃
- 폰트, 자간, 라인 두께, 화살표 스타일, 여백 및 레이아웃 그리드를 원본과 동일하게 유지.
- 불필요한 신설 라벨/아이콘/브랜드/컬러 텍스트 추가 금지.

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

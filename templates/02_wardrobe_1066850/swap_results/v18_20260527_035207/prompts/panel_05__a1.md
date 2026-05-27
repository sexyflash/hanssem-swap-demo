TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_06.png
  IMAGE 4 = USER PRODUCT — screenshot_01.png
  IMAGE 5 = USER PRODUCT — screenshot_04.png
  IMAGE 6 = USER PRODUCT — screenshot_10.png
  IMAGE 7 = USER PRODUCT — screenshot_07.png
  IMAGE 8 = USER PRODUCT — screenshot_05.png

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


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
상단에 '색상'과 '도어/서랍앞판', '몸통' 항목이 좌우로 구분된 표 형태로 배치됨. 중간에 굵은 구분선이 있고, 그 아래로 '도어/서랍앞판' 세부 항목(전면, 후면, 도어 손잡이)이 세로로 정렬됨. 하단에는 '몸통' 세부 항목(천지판/측판/선반, 뒷판, 옷걸이봉, 서랍재, 서랍재 지판, 서랍레일)이 표 형태로 나열됨. 각 항목은 왼쪽에 항목명, 오른쪽에 상세 설명이 위치. 전체적으로 세로로 긴 표 구조이며, 각 구분선이 명확하게 영역을 나눔.

Elements:
  - section_header @ top left: 색상
  - section_content @ top right: 화이트, 화이트하이글로시, 라이트오크, 크림화이트
  - section_header @ below first: 도어/서랍앞판
  - section_content @ right of 도어/서랍앞판: 화이트, 화이트하이글로시, 라이트오크, 크림화이트
  - section_header @ below 도어/서랍앞판: 몸통
  - section_content @ right of 몸통: 화이트, 라이트오크
  - subsection_header @ middle left: 도어/서랍앞판
  - subsection_content @ right of 도어/서랍앞판: 전면, 후면, 도어 손잡이 상세 설명
  - subsection_header @ lower left: 몸통
  - subsection_content @ right of 몸통: 천지판/측판/선반, 뒷판, 옷걸이봉, 서랍재, 서랍재 지판, 서랍레일 상세 설명

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — structure_chart:
[1] 상단 '색상' 표 교체
- '도어/서랍앞판' 오른쪽 값 → "화이트 하이글로시(유광)", "크림화이트", "라이트오크"
- '몸통' 오른쪽 값 → "라이트오크" (사용자 제공 정보상 바디 일체감 명시 컬러만 표기)
- 원본에 남아있는 '화이트' 단어 및 한샘 컬러 표기는 전부 제거.

[2] 중간 '도어/서랍앞판' 상세 표 재작성
- 전면(오른쪽 내용) → "화이트 하이글로시(유광)", "크림화이트", "라이트오크" / 도어 LPM 공법(접착제 무사용), E0 등급 소재
  · 원본의 두께/ABS에지/PET 등 공정·수치 표기는 전부 삭제.
- 후면(오른쪽 내용) → E0 등급 소재 사용
- 도어 손잡이(오른쪽 내용) → 매립형 손잡이(양방향 그립), 목분 소재

[3] 하단 '몸통' 상세 표 재구성
- '천지판/측판/선반' → E0 등급 소재, 선반 두께 18mm, 깊이 57cm
- '뒷판' → E0 등급 소재, 보조목 3개 보강
- '옷걸이봉' → 알루미늄, 최대 16kg 지지(너비 80cm 기준)
- '서랍재' 라벨을 '서랍'으로 변경하고 내용 → 3단 외부형 구조, 속옷·티셔츠·니트·바지 수납에 적합
- '서랍재 지판', '서랍레일' 두 행은 삭제(사용자 정보 미제공 항목이므로 비표기).

[4] 타이포/레이아웃
- 표의 레이아웃, 구분선 굵기, 좌측 라벨/우측 설명 정렬 유지.
- 색상명에는 반드시 큰따옴표 포함(예: "크림화이트").
- 다중 줄로 나열되던 '전면' 상세는 한 줄 요약 문장으로 병합.

[5] 금지/정합성
- 한샘 원본 용어(화이트, ABS에지, PB/MDF 두께 수치 등)와 남아있는 한샘 고유 컬러명 전부 제거.
- 사용자 제공 정보에 없는 소재/치수/메커니즘(예: 레일 재질) 미기재.
KEEP: 표 구조, 섹션/서브섹션 제목 위치, 전체 톤&서체/자간/여백.

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

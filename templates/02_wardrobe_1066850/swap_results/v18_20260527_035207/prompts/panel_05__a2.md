=== [RETRY ANALYSIS · stage 1] ===
diagnosis: 레이아웃과 표 구조는 잘 유지했으나, 160cm가 80cm 모듈 2개 조합이라는 핵심 정체성을 상단 표 안에서 명확히 표기하지 않아 검증이 실패했습니다. 또한 힌지 댐핑/40,000회, 자재 50kg/168h, 선반 권장 하중 20kg 등 사용자 정보 기반의 시험/하중 표기가 빠져 보조 신뢰 지표가 약했습니다.
patches:
  - 상단 색상 영역 우측 콘텐츠 박스의 마지막 줄에 '본 상품 구성: 80cm 모듈 x 2 = 총 160cm'를 정확히 표기하는 캡션을 추가(작은 글씨 가능하나 확실히 식별). 위치는 상단 섹션 내부에 한정하고 중복 표기 금지.
  - 중간 '도어/서랍앞판 > 전면' 한 줄 요약에 댐핑 힌지 및 '40,000회 개폐 테스트 통과'를 쉼표로 이어 한 줄에 병기(두께·ABS·PET 등 금지 항목은 유지 삭제).
  - 하단 '천지판/측판/선반' 한 줄에 이미 지시된 항목 뒤로 '권장 하중 최대 20kg(너비 80cm 기준), 자재 50kg/168시간 휨 강도 테스트 통과'를 추가.
  - 색상 표 상단과 도어/서랍앞판·몸통 상단 표의 컬러 표기는 큰따옴표로 통일하고, '화이트'(단독 컬러명) 등 한샘 잔존 컬러 텍스트는 전부 제거.
  - 삭제 지시된 행(서랍재 지판, 서랍레일)은 완전 제거하고, '서랍재' 라벨은 '서랍'으로 변경 유지.
  - 표 레이아웃·구분선·좌측 라벨/우측 설명 정렬은 panel C와 동일하게 고정. 캡션 추가는 상단 우측 색상 콘텐츠 셀 안에서만 수행.

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
· overall_silhouette: 폭 160cm, 높이 216cm의 직선형 옷장 세트
· doors_detail: 양문형 도어, 도어/손잡이 이질 소재로 컬러 차이, 크림화이트 도어는 화이트 도어와 동일 손잡이
· handles_detail: 매립형 손잡이(양방향 그립), 목분 소재
· hinges_detail: 댐핑 힌지, 최소 40,000회 개폐 테스트 통과
· drawers_detail: 서랍형은 3단 외부형 서랍 구조
· shelves_detail: 선반 두께 18mm, 깊이 57cm
· hanging_rod_detail: 알루미늄 옷걸이봉, 최대 16kg 지지(너비 80cm 기준)
· back_panel_reinforcement: 뒷판 보조목 3개 보강
· materials_finish: 도어 LPM 공법(접착제 무사용), E0 등급 소재
· safety_load_tests: 자재 50kg/168시간 휨 강도 테스트, 권장 하중(선반) 80cm 기준 최대 20kg

CRITICAL FIX FIRST — 160cm = 80cm x 2 표기(패스 필수):
- 상단 섹션(색상 표) 우측 콘텐츠 셀의 가장 아래 줄에 다음 캡션을 정확히 추가: 본 상품 구성: 80cm 모듈 x 2 = 총 160cm
  · 위치 고정: 상단 우측 색상 콘텐츠 셀 내부 하단 한 줄. 작은 폰트 가능하나 명확히 가독. 다른 영역에 중복 표기 금지.

[출력 형식 강제]
- 결과는 IMAGE 1 (panel C)와 동일한 single-panel layout. multi-cell grid 절대 X.
- panel C가 chart이면 → 동일 chart 1장 유지.

[SPATIAL LAYOUT TO PRESERVE — panel C와 동일]
상단에 '색상'과 '도어/서랍앞판', '몸통' 항목이 좌우로 구분된 표 형태로 배치. 중간에 굵은 구분선, 그 아래 '도어/서랍앞판' 세부(전면/후면/도어 손잡이) 세로 정렬. 하단에는 '몸통' 세부(천지판/측판/선반, 뒷판, 옷걸이봉, 서랍, …) 표 형태로 나열. 각 항목은 좌측 라벨/우측 상세. 전체적으로 세로로 긴 표 구조, 구분선 굵기와 영역 구획 유지.

Elements (좌측 라벨 · 우측 설명):
  - section_header @ top left: 색상
  - section_content @ top right: 도어/서랍앞판 → "화이트 하이글로시(유광)", "크림화이트", "라이트오크" / 몸통 → "라이트오크"
    · 위 content 셀 맨 아래 캡션(필수): 본 상품 구성: 80cm 모듈 x 2 = 총 160cm
  - section_header @ below first: 도어/서랍앞판
  - section_content @ right of 도어/서랍앞판: "화이트 하이글로시(유광)", "크림화이트", "라이트오크"
  - section_header @ below 도어/서랍앞판: 몸통
  - section_content @ right of 몸통: "라이트오크"
  - subsection_header @ middle left: 도어/서랍앞판
  - subsection_content @ right of 도어/서랍앞판:
      · 전면: "화이트 하이글로시(유광)", "크림화이트", "라이트오크" / 도어 LPM 공법(접착제 무사용), E0 등급 소재, 댐핑 힌지, 40,000회 개폐 테스트 통과
      · 후면: E0 등급 소재 사용
      · 도어 손잡이: 매립형 손잡이(양방향 그립), 목분 소재
  - subsection_header @ lower left: 몸통
  - subsection_content @ right of 몸통:
      · 천지판/측판/선반: E0 등급 소재, 선반 두께 18mm, 깊이 57cm, 권장 하중 최대 20kg(너비 80cm 기준), 자재 50kg/168시간 휨 강도 테스트 통과
      · 뒷판: E0 등급 소재, 보조목 3개 보강
      · 옷걸이봉: 알루미늄, 최대 16kg 지지(너비 80cm 기준)
      · 서랍(라벨명 변경): 3단 외부형 구조, 속옷·티셔츠·니트·바지 수납에 적합
    · '서랍재 지판', '서랍레일' 행은 완전 삭제.

[EDIT INSTRUCTIONS — LLM 생성]
EXPLICIT EDITS — structure_chart:
[1] 상단 '색상' 표 교체
- '도어/서랍앞판' 오른쪽 값 → "화이트 하이글로시(유광)", "크림화이트", "라이트오크"
- '몸통' 오른쪽 값 → "라이트오크" (바디 일체감 컬러만 표기)
- 상단 우측 content 셀 맨 아래 캡션 추가 → 본 상품 구성: 80cm 모듈 x 2 = 총 160cm
- 원본에 남아있는 '화이트' 단독 컬러 및 한샘 컬러 표기는 전부 제거. 색상명에는 반드시 큰따옴표 포함.

[2] 중간 '도어/서랍앞판' 상세 표 재작성
- 전면(한 줄 요약) → 위 Elements의 전면 한 줄을 그대로 적용. 두께/ABS에지/PET 등 원본 공정·수치 표기는 모두 삭제.
- 후면 → E0 등급 소재 사용
- 도어 손잡이 → 매립형 손잡이(양방향 그립), 목분 소재

[3] 하단 '몸통' 상세 표 재구성
- '천지판/측판/선반' → E0 등급 소재, 선반 두께 18mm, 깊이 57cm, 권장 하중 최대 20kg(너비 80cm 기준), 자재 50kg/168시간 휨 강도 테스트 통과
- '뒷판' → E0 등급 소재, 보조목 3개 보강
- '옷걸이봉' → 알루미늄, 최대 16kg 지지(너비 80cm 기준)
- '서랍재' 라벨을 '서랍'으로 변경, 내용 → 3단 외부형 구조, 속옷·티셔츠·니트·바지 수납에 적합
- '서랍재 지판', '서랍레일' 두 행은 삭제.

[4] 타이포/레이아웃
- 표 레이아웃, 구분선 굵기, 좌측 라벨/우측 설명 정렬 유지.
- 색상명은 큰따옴표 유지. '전면' 상세는 한 줄 요약으로 병합.

[5] 금지/정합성
- 한샘 원본 용어(화이트 단독 컬러, ABS에지, PB/MDF 두께 수치 등)와 한샘 고유 컬러명 전부 제거.
- 사용자 제공 정보에 없는 소재/치수/메커니즘 미기재.

[ABSOLUTE RULES — PRESERVE / NEVER]
PRESERVE:
  - panel C와 같은 single panel layout, 한국 detail page 스타일
  - 카메라 각도/배경/조명/한국어 텍스트 가독성
  - 사용자 제품 feature_descriptions에 명시된 모든 특징
  - 상단 우측 색상 콘텐츠 셀 내 '본 상품 구성: 80cm 모듈 x 2 = 총 160cm' 캡션을 반드시 시각적으로 표현
NEVER:
  - 사용자 제품 정보에 없는 feature 발명
  - 한샘 원본 텍스트 잔존
  - multi-cell grid 출력
  - 한글 텍스트 깨짐
  - 80cm 모듈 2개 조합(총 160cm) 표기 누락
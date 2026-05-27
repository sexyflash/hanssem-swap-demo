TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_06.png
  IMAGE 4 = USER PRODUCT — screenshot_05.png
  IMAGE 5 = USER PRODUCT — screenshot_10.png
  IMAGE 6 = USER PRODUCT — screenshot_01.png

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
패널은 2행 4열의 격자(grid)로 구성되어 있습니다. 각 셀에는 상단에 조립 단계별 이미지를, 하단에는 해당 단계의 번호와 설명 텍스트가 위치합니다. 첫 번째 행에는 1~3번 조립 과정(부품 분리, 몸통 조립, 몸통 완성)이, 두 번째 행에는 4~6번(몸통 세움, 배치, 도어 조립), 세 번째 행에는 7~8번(완성된 옷장, 여러 옷장 조립)이 순서대로 배치되어 있습니다. 각 이미지는 셀 중앙에 크기가 균일하게 배치되어 있고, 텍스트는 셀 하단에 정렬되어 있습니다.

Elements:
  - step_image @ 1행 1열: 분해된 부품 사진
  - step_image @ 1행 2열: 몸통 일부 조립 사진
  - step_image @ 1행 3열: 몸통 완성 사진
  - step_image @ 2행 1열: 몸통을 세우는 장면
  - step_image @ 2행 2열: 몸통을 배치하는 장면
  - step_image @ 2행 3열: 도어 조립 장면
  - step_image @ 3행 1열: 완성된 옷장 단일 사진
  - step_image @ 3행 2열: 여러 옷장이 배치된 인테리어 사진

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — structure_chart:
[1] 1행 1열 이미지 교체: 포장 해체 후 부품을 바닥에 펼쳐 둔 샷으로 교체. 부품에는 LPM 마감 도어(양문형), 18mm 두께 선반, 알루미늄 옷걸이봉·브라켓, 댐핑 힌지, 3단 외부형 서랍(레일 포함), 뒷판과 보조목(3개)이 식별되게 배치. 도어 색상은 "크림화이트"로 표현, 손잡이는 도어를 따라 세로로 길게 내려오는 매립형 형태가 한눈에 보이도록.
[2] 1행 2열 이미지 교체: 옆판·상판·하판을 결합해 몸통 일부가 ㄷ자 형태로 선 조립된 장면. 내부에는 18mm 선반 일부가 비치고, 하부에는 서랍 레일 체결 준비가 보이도록.
[3] 1행 3열 이미지 교체: 몸통을 완성한 샷. 뒷판 체결과 함께 내부에 3개의 보조목(세로 방향 보강재)이 설치된 것이 보이게 연출. 선반과 서랍 레일이 정렬된 상태.
[4] 2행 1열 이미지 교체: 두 사람이 완성된 몸통을 세우는 장면. 높이 216cm가 체감되도록 인물 대비를 유지.
[5] 2행 2열 이미지 교체: 설치 위치로 몸통을 이동·배치하고 수평계를 이용해 수평을 맞추는 장면. 바닥 몰딩·벽면과의 간격을 정리하는 제스처 유지.
[6] 2행 3열 이미지 교체: 양문형 도어에 댐핑 힌지를 체결·조절하는 근접 샷. 도어 전면에는 세로 매립형 손잡이가 길게 이어져 보이게 하고, 손잡이(목분 소재)는 도어와 미묘한 컬러 차이가 느껴지도록 표현. 힌지 커버에 소프트클로징 구조가 보이면 좋음.
[7] 3행 1열 이미지 교체: 단일 모듈 1통(서랍형) 완성 샷. 전면에는 양문형 도어와 하부 3단 외부형 서랍이 명확하게 보이도록. 색상은 "크림화이트" 표현 유지, 손잡이 연속성(세로 매립형) 유지.
[8] 3행 2열 이미지 교체: 160cm 세트(모듈 2통 나란히) 완성 인테리어 샷. 동일한 손잡이 라인과 도어 높이(216cm)를 맞추고 전면 정렬. 실내 소품(의자·조명 등)은 원본과 유사한 미니멀 연출. 도어 컬러는 "크림화이트"로 통일.
KEEP: 8칸(상단 3+중단 3+하단 2) 그리드 구성, 각 셀의 중앙 이미지 배치와 하단 번호·설명 텍스트의 정렬/타이포/톤은 그대로 유지. 촬영 각도와 배경 톤(밝은 스튜디오 백그라운드) 유지.

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

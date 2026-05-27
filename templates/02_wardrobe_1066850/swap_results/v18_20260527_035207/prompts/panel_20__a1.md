TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_05.png
  IMAGE 4 = USER PRODUCT — screenshot_09.png
  IMAGE 5 = USER PRODUCT — screenshot_06.png

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
  ◆ [DISTORTION] 도어는 양문형 힌지(여닫이) 도어로 구성되고 슬라이딩이 아님. (axis=doors)
     → 정답: 여닫이(힌지) 도어
  ◆ [DISTORTION] 서랍형: 전면에 3단 외부형 서랍 블록이 명확히 보임. (axis=drawers)
     → 정답: 3단 외부형 서랍 존재
  ◆ [DISTORTION] 문을 따라 세로로 길게 내려오는 매립형 손잡이(플러시 인셋 타입). (axis=handles)
     → 정답: 세로형 매립 손잡이
  ◆ [DISTORTION] 상단까지 곧게 뻗은 직선형 실루엣(크라운/아치 등 돌출 장식 없음). (axis=frame)
     → 정답: 평평한 상단의 직선형 외관
  ◆ [DISTORTION] 제품 이미지의 도어 컬러가 제공된 3가지 중 하나로 보임. (axis=color)
     → 정답: 제공 3색 중 하나
  ✗ [FORBIDDEN] 슬라이딩(미닫이) 도어가 포함되면 안 됨. — 결과에 보이면 fail
  ✗ [FORBIDDEN] 바닥에서 본체를 높게 띄우는 노출 다리(약 10cm 이상)가 없어야 함. — 결과에 보이면 fail
  ✗ [FORBIDDEN] 전면/내부 가장자리에 LED 발광 바 등 내장 조명이 노출되면 안 됨(선택 사양 언급 없음). — 결과에 보이면 fail

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 알루미늄 옷걸이봉 사용이 보이거나 텍스트로 명시됨. (axis=hanging_rod)


=== [★ LIFESTYLE 특화] ===
  - 룸 배경/조명/소품/카메라 각도 유지. 사용자 제품으로 자연스럽게 배치
  - 한샘 제품 비율과 사용자 제품 비율이 다르면 사용자 제품 비율 우선


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
왼쪽 하단에서 사람의 손이 중앙의 옷걸이에 걸린 베이지색 코트를 잡고 있다. 옷걸이는 세 개가 나란히 중앙에서 오른쪽 상단 방향으로 걸려 있다. 옷걸이들은 모두 나무 재질이며, 상단에는 금속 행거봉이 수평으로 설치되어 있다. 배경은 나무 무늬의 옷장 내부로, 전체적으로 따뜻한 톤이다. 오른쪽에는 밝은 베이지색 트렌치코트, 중앙에는 연한 갈색 코트, 왼쪽에는 회색 코트가 있다. 각 옷걸이의 위치와 각도가 거의 평행하게 정렬되어 있다.

Elements:
  - hand @ 왼쪽 하단에서 중앙: 코트를 잡고 있는 사람의 손
  - hanger @ 중앙~오른쪽 상단: 나무 재질의 옷걸이 3개
  - clothes @ 중앙~오른쪽: 베이지색, 연갈색, 회색 코트
  - hanger_rod @ 상단 수평: 금속 행거봉
  - background @ 전체 배경: 나무 무늬 옷장 내부

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — lifestyle_scene:
[1] 옷걸이봉/브라켓 교체: 원본의 금속 행거봉을 사용자 제품 사양의 알루미늄 옷걸이봉과 브라켓 디자인으로 치환. 표면은 매트한 실버 톤(브러시 질감)으로 보정하고, 브라켓 형상/두께/고정 나사 위치는 reference(screenshot_05.png, screenshot_06.png, screenshot_09.png)와 동일하게 맞춤.
[2] 내부 마감 톤 정리: 옷장 내부 나무 무늬는 유지하되, 과도한 노란기 제거 후 자연스러운 내추럴 우드(라이트 오크 계열)로 균일하게 톤 보정. LPM 느낌의 매끈하고 균질한 표면감만 subtly 표현(과장된 반사/하이라이트 금지).
[3] 행거/의류 유지 + 로고 제거: 나무 옷걸이 3개는 그대로 두되, 보이는 전면 로고·문양·각인(옷걸이 전면의 인쇄 포함)과 의류 라벨의 문구·숫자는 모두 제거 혹은 흐림 처리해 비브랜드화.
[4] 손/동작 유지: 왼쪽 하단의 손 위치, 코트 잡는 동작을 동일하게 유지. 피부 톤은 자연광 기준 따뜻한 톤으로만 미세 보정.
[5] 조명/분위기: 현재의 따뜻한 조명과 우드 톤 배경을 유지. 전체 노출은 약간만 상향해 옷걸이봉의 알루미늄 질감이 또렷하게 보이도록 하되, 하이라이트 날림 금지.
[6] 구도/배치 고정: 옷걸이 3개가 중앙에서 오른쪽 상단 방향으로 평행 정렬된 구도, 코트 3벌의 색(베이지/연갈색/회색) 배치는 동일 유지. 프레임 내 요소 수량 변경 금지.
[7] 제품 디테일 반영(암시적): 옷걸이봉의 두께감과 브라켓 접합부를 견고하게 표현해 하중 지지력(최대 16kg, 너비 80cm 기준)을 시각적으로만 암시. 수치 텍스트/아이콘 추가 금지.
KEEP: 카메라 각도, 배경 우드 텍스처, 행거봉 수평 위치, 전체 따뜻한 톤, 생활감 있는 코트 주름/질감.

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

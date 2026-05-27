TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_04.png

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

  ◆ [DISTORTION] 서랍형: 전면에 3단 외부형 서랍 블록이 명확히 보임. (axis=drawers)
     → 정답: 3단 외부형 서랍 존재
  ◆ [DISTORTION] 문을 따라 세로로 길게 내려오는 매립형 손잡이(플러시 인셋 타입). (axis=handles)
     → 정답: 세로형 매립 손잡이
  ✗ [FORBIDDEN] 막대형 바 핸들/동그라미 노브 등 돌출 손잡이는 없어야 함(본 제품은 매립형). — 결과에 보이면 fail

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 손잡이와 도어는 서로 다른 소재/톤으로 색 대비가 보임(크림화이트 도어도 동일 손잡이 톤). (axis=handles)
     · 댐핑 힌지(부드럽게 닫힘) 관련 아이콘/문구/접사 표기가 있음. (axis=hinges)
     · 선반 두께 18mm 표기 또는 단면 설명이 보임. (axis=shelves)
     · 알루미늄 옷걸이봉 사용이 보이거나 텍스트로 명시됨. (axis=hanging_rod)
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
패널 중앙에 크림색 평면 가구 표면이 크게 위치함. 오른쪽 중앙에서 왼쪽 중앙 방향으로 손이 뻗어 표면을 만지고 있음. 손은 화면 오른쪽 1/3 지점에 위치하며, 손바닥이 가구 표면에 평평하게 닿아 있음. 가구 표면은 화면 전체를 거의 채우며, 수직의 얇은 경계선이 좌우에 있음. 배경이나 추가 소품은 없음. 전체적으로 미니멀하고 단순한 구도임.

Elements:
  - product_surface @ center, fills almost entire frame: 크림색 평면 가구 표면
  - hand @ right center, palm touching surface: 표면을 만지는 오른손
  - vertical_line @ left and right edges: 가구 문 경계선

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — detail_close_up:
[1] 도어 표면 컬러 톤 보정: 화면 전체의 가구 표면을 사용자 컬러 옵션 "크림화이트"로 통일. 기존 크림빛이 과도하게 노랗거나 회색 기운이 있으면 따뜻한 미색 화이트 쪽으로 화이트 밸런스 재조정.
[2] 표면 질감/광도: LPM 저광(매트) 느낌 유지. 강한 반사/하이라이트 제거하고, 균일한 부드러운 확산광만 남김. 결·텍스처는 미세하고 거의 보이지 않게.
[3] 매립형 손잡이 암시: 화면 오른쪽 도어 모서리(세로 경계선) 쪽에 아주 얕은 세로형 매립 손잡이 채널을 1줄 힌트 수준으로 표현. 문짝 평면과 동일 높이에서 안쪽으로 살짝 파인 느낌의 내측 하이라이트/섀도우만 추가. 손잡이 소재는 도어와 다른 재질감이 느껴지도록 아주 미세한 톤 차(도어 대비 약간 더 무채백 계열)만 반영하되 과장 금지.
[4] 도어 간 이격/경계: 좌우 세로 경계선의 간격과 직진성을 정돈하여 양문형 도어 인상을 유지. 경계선은 1~2px 수준의 미세한 그림자/하이라이트로 또렷하되 과도한 검은 라인 금지.
[5] 피부/손: 손의 위치, 각도, 그림자, 피부 톤 자연스럽게 유지. 가구 표면과의 접촉부에만 부드러운 접촉 그림자 보강.
KEEP: 촬영 구도(정면 클로즈업), 미니멀한 배경, 조명 방향과 부드러운 콘트라스트, 프레임 내에 보이는 요소만 표현(손, 도어 표면, 좌우 경계선).

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

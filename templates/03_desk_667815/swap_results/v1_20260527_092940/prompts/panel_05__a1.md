TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png
  IMAGE 4 = USER PRODUCT — screenshot_10.png
  IMAGE 5 = USER PRODUCT — screenshot_05.png

이번 panel에 필요한 user-product reference만 첨부됨. 외부 정보 가져오지 마세요.

TARGET: 한샘 티오 ㄱ자책상 160cm
제원: 160×None×Nonecm
모델 옵션: ㄱ자책상 160cm 길이 160cm (상세 치수 미표기)
· overall_silhouette: 넓은 상판과 하부책장이 만난 ㄱ자(L자) 구성이며, 작업 공간과 수납력을 동시에 제공.
· storage_detail: 하부에 책과 PC 본체 등 부피 물건을 수납할 수 있는 책장형 수납 공간을 구성.
· edges_corners: 상판과 모서리는 라운드 처리로 부딪힘 위험을 줄이고 부드러운 시각적 인상 제공.
· hooks_hangers: 가방걸이 1개 기본 제공, 좌/우 선택 설치 가능.
· legs_detail: 다리 끝까지 통일된 라인과 색감으로 마감. 하부 레벨러로 미세 수평 조절 가능.
· stability_structure: 보강대 2개를 적용해 흔들림을 감소시키는 구조. 하중 분산과 변형을 최소화.
· materials_surface: 상판은 스크래치에 강한 LPM 표면재. 접착제를 쓰지 않고 열과 압력으로 접합해 유해물질 발생을 줄이고 내구성 향상.
· safety_features: E0 등급 자재(포름알데히드 방출량 ≤ 0.5 mg/L) 사용, 어린이 안전법 테스트 합격.
· power_access: 선택 추가 가능한 하부 설치형 콘센트(좌/우 선택). 책상 상판을 넓게 쓰고 액체 유입으로 인한 전기 사고 위험을 감소.
· accessories_compatibility: 티오 시리즈 전용 선택 액세서리: 하부형 콘센트, 소형 수납함, 이동서랍장(일자책상 60cm 깊이 대응), 클램프 조명.
· modularity_fit: 티오 벙커침대 기본형 하부 공간에 맞춘 규격으로, 침대 하부를 학습 공간/PC 공간으로 확장 구성 가능.

=== [★ PRODUCT IDENTITY · 절대 왜곡되면 안 됨] ===
(이 항목들은 QA가 binary 검증. 1개라도 fail이면 retry.)

  ◆ [DISTORTION] ㄱ자(L자) 형태 상판과 하부 책장 유닛이 결합된 일체형 구성 (axis=frame)
     → 정답: ㄱ자 상판 + 하부 책장 일체형
  ◆ [DISTORTION] 하부 수납은 책장형 오픈 선반 구조로 도어/서랍이 없음 (axis=storage)
     → 정답: 오픈 선반형 수납(도어/서랍 없음)
  ✗ [FORBIDDEN] 상판 타공형 전원 콘센트/케이블홀/팝업 모듈 없음 — 결과에 보이면 fail
  ✗ [FORBIDDEN] 기본 구성 이미지에서 하부 설치형 콘센트 노출 금지(선택 액세서리는 별도 패널에서만) — 결과에 보이면 fail
  ✗ [FORBIDDEN] 책상 본체에 부착된 서랍 없음(수납은 오픈 선반형) — 결과에 보이면 fail
  ✗ [FORBIDDEN] 상판이 유리/석재(대리석 포함)로 보이지 않음 — 결과에 보이면 fail
  ✗ [FORBIDDEN] V자/X자/지그재그 형태의 메탈 프레임 다리 없음 — 결과에 보이면 fail
  ✗ [FORBIDDEN] 키보드 슬라이드/풀아웃 트레이 없음 — 결과에 보이면 fail
  ✗ [FORBIDDEN] 책상 본체 하부에 바퀴(캐스터) 없음 — 결과에 보이면 fail

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 다리 끝까지 라인과 색감이 일관되게 이어지는 마감 (axis=finish)
     · PC 본체 등 부피 물건을 위한 높은 오픈 칸 1개 이상 (axis=storage)


=== [★ LIFESTYLE 특화] ===
  - 룸 배경/조명/소품/카메라 각도 유지. 사용자 제품으로 자연스럽게 배치
  - 한샘 제품 비율과 사용자 제품 비율이 다르면 사용자 제품 비율 우선


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
책상은 화면 중앙에 크게 배치되어 있으며, 상판 위에 다양한 소품이 정돈되어 있다. 왼쪽 뒤편에는 흰색 스탠드 조명이 약간 기울어진 채 놓여 있고, 그 앞에는 원형 시계가 있다. 중앙에는 펼쳐진 책이 자연스럽게 놓여 있다. 오른쪽 끝에는 연필꽂이, 연필, 그리고 액자와 트레이가 함께 정렬되어 있다. 책상 다리는 네 귀퉁이에 곧게 뻗어 있다. 배경은 완전히 흰색으로, 제품과 소품만이 강조된다.

Elements:
  - main_product @ center: 심플한 흰색 직사각형 책상, 네 개의 원통형 다리
  - desk_lamp @ back left on desk: 흰색 각도 조절형 스탠드 조명
  - clock @ left center on desk: 작은 원형 아날로그 시계
  - book @ center on desk: 펼쳐진 책
  - tray_set @ back right on desk: 원형 트레이 위에 연필꽂이, 연필, 액자

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — lifestyle_scene:
[1] 메인 제품 교체: 화면 중앙의 흰색 직사각형 책상을 사용자의 "한샘 티오 ㄱ자책상 160cm"로 전체 리모델링. 상판을 ㄱ자(L자) 실루엣으로 구성하고, 긴 변은 현 패널과 동일하게 좌→우로 160cm의 비례감을 유지. 짧은 리턴은 좌측 뒤 방향으로 자연스럽게 연장(좌측 ㄱ자), 연결부는 매끈한 라운드 코너로 처리.
[2] 하부 수납 구조: ㄱ자 리턴 쪽 하부를 책장형 수납(오픈 선반)으로 제작하여 바닥까지 내려오는 지지 구조가 되도록 구현. 책/PC 본체가 들어갈 수 있도록 1~3칸 오픈 격자를 구성(칸 수/비율은 reference 이미지 비율 준수).
[3] 보강대 적용: 긴 변 하부에 슬림한 보강대 2개를 상판 하부에 평행하게 배치(화이트 톤). 측면에서 은은히 보이도록 두께는 얇게, 그림자 자연스럽게.
[4] 다리/레벨러: ㄱ자 구조에서 선반이 아닌 자유 코너에는 직선형 다리를 배치(상판과 동일 컬러). 각 다리와 선반 하단에는 소형 원형 레벨러(연한 그레이 톤) 표현.
[5] 가방걸이: 기본 제공 1개를 우측 전면 하부 모서리 안쪽에 소형 훅으로 부착(화이트). 소품(가방 등)은 걸지 않음.
[6] 표면/마감: 상판은 저광(매트) LPM 느낌의 미세한 반사만 표현. 목무늬는 넣지 않음. 모든 엣지/모서리는 라운드 처리.
[7] 소품 재배치(원위치 유지): 스탠드 조명(좌후면), 원형 시계(좌중앙), 펼친 책(정중앙), 트레이+연필꽂이+액자(우측 끝) 위치/각도 유지. 소품은 ㄱ자 연결부의 단차 없이 상판 위에 안정적으로 놓이도록 접지 그림자/접촉면 재렌더링.
[8] 광원/그림자: 기존 조명 방향과 세기 유지. ㄱ자 확장된 면적과 하부 수납/보강대/다리로 인해 생기는 투영 그림자를 바닥면에 얕고 고르게 재계산.
[9] 원본 흔적 제거: 직사각 상판, 네 모서리 원통형 다리, 우측 측면의 체결 흔적 등 원본 책상 구조는 모두 제거.
[10] 스케일: 160cm 긴 변이 소품 대비 과소/과대해 보이지 않도록 기존 책·트레이 크기 기준 비례 조정. 전체 프레임 안에 ㄱ자 형상이 명확히 인지되도록 구도 미세 조정.
KEEP: 배경 완전 흰색, 카메라 각도/원근, 미니멀한 연출 톤, 소품의 디자인과 색감, 한국어 텍스트 없음 상태 유지.

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

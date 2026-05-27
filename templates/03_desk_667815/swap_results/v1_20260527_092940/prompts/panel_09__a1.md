TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png
  IMAGE 4 = USER PRODUCT — screenshot_07.png
  IMAGE 5 = USER PRODUCT — screenshot_06.png

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

  ◆ [DISTORTION] 하부 수납은 책장형 오픈 선반 구조로 도어/서랍이 없음 (axis=storage)
     → 정답: 오픈 선반형 수납(도어/서랍 없음)
  ◆ [DISTORTION] 상판 외곽 모서리 라운드 처리 (axis=edges)
     → 정답: 라운드 모서리
  ◆ [DISTORTION] 가방걸이 1개 기본 제공(좌/우 중 한 위치에 설치) (axis=accessory)
     → 정답: 가방걸이 1개 확인
  ◆ [DISTORTION] 흔들림 저감을 위한 보강대 2개 적용 (axis=structure)
     → 정답: 보강대 2개
  ◆ [DISTORTION] 상판은 LPM 계열의 불투명 패널형으로, 유리/석재/라이브엣지 원목이 아님 (axis=surface)
     → 정답: LPM 계열 패널 상판(유리/석재/라이브엣지 아님)

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 바닥 수평 맞춤을 위한 하부 레벨러(조절발) 노출 (axis=legs)
     · PC 본체 등 부피 물건을 위한 높은 오픈 칸 1개 이상 (axis=storage)
     · LPM 표면 특성상 무광/세미무광 수준으로 과도한 반사 없음 (axis=surface)
     · 라운드 모서리의 엣지 밴딩이 이색/들뜸 없이 매끈함 (axis=finish)


=== [★ DETAIL CLOSE-UP 특화] ===
  - frame 안에 들어오는 사용자 제품 디테일을 정확히 표현. 추측/발명 금지
  - reference 사진에서 보이는 시접/소재/표면 디테일 그대로


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
좌측 상단에는 밝은 나무 무늬의 테이블 상판 모서리가 크게 클로즈업되어 있다. 상판 아래에는 흰색 원통형 다리가 수직으로 연결되어 있다. 우측 중앙에는 같은 흰색 원통형 다리가 세로로 길게 배치되어 있다. 배경은 전체적으로 흰색이며, 제품 외에는 다른 요소가 없다. 두 개의 주요 제품 파트가 화면을 양분하여 배치되어 있다. 텍스트나 아이콘 등 추가 정보는 없다.

Elements:
  - tabletop_corner @ 좌측 상단: 밝은 나무 무늬의 테이블 상판 모서리
  - table_leg_attached @ 좌측 하단: 상판에 연결된 흰색 원통형 다리
  - table_leg_isolated @ 우측 중앙: 독립적으로 세로로 놓인 흰색 원통형 다리

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — detail_close_up:
[1] 좌측 상단 상판 모서리 교체
- 대상: tabletop_corner
- '한샘 티오 ㄱ자책상 160cm'의 상판 디테일로 변경.
- 라운드 모서리 형태는 원본의 곡률 감각 유지(과도한 곡선/각진 처리 금지).
- 표면 질감: 스크래치에 강한 LPM 느낌의 미세한 무광과 잔잔한 목무늬 결을 표현. 과한 하이글로시 금지.
- 상판 두께감과 가장자리 단면 비율은 원본과 유사하게 유지, 단차 없이 매끈한 마감으로 렌더.

[2] 좌측 하단 상판-다리 결합부 디테일 정리
- 대상: table_leg_attached
- 원통형 다리와 상판 결합부는 노출 하드웨어 최소화, 라인이 깔끔하게 이어지도록 정리.
- 다리와 결합부 색/광택은 동일하게 맞춰 ‘다리 끝까지 통일된 라인과 색감’ 인상이 나도록 처리.

[3] 다리 형태/마감 통일 및 레벨러 반영
- 대상: table_leg_attached, table_leg_isolated
- 다리는 원통형, 흰색 톤, 상단부터 하단까지 동일 색/광택으로 통일.
- 하부 레벨러 표현: 다리 하단에 얇은 원형 베이스가 살짝 돌출되며, 회전 조절 가능한 미세한 분할선(이음새)을 동일 색 계열로 섬세하게 표시. 과장된 금속 광택/색 대비 금지.
- 좌측 연결 다리와 우측 단독 다리의 직경/톤/광택을 동일 스펙으로 맞춤.

[4] 불필요 요소 추가 금지
- 본 패널은 클로즈업으로 프레임 안 디테일만 보여줌.
- ㄱ자 구조, 하부 책장, 보강대, 가방걸이, 콘센트 등 프레임 밖 요소는 노출/삽입 금지.
- 텍스트/로고/아이콘 추가 금지.

[5] 참고 리소스 매핑
- screenshot_03.png: 상판 모서리 라운드의 곡률/엣지 라인 참고.
- screenshot_06.png: 하부 레벨러의 형태/이음새 표현 참고.
- screenshot_07.png: 다리 표면의 광택 수준과 색 톤 통일 참고.

KEEP: 원본의 좌상단 상판-좌하단 연결 다리와 우측 중앙 단독 다리로 화면이 양분되는 구도, 카메라 각도/거리, 흰 배경과 조명 톤, 명암/노출 밸런스, 빈 공간 구성.

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

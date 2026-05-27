TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png
  IMAGE 4 = USER PRODUCT — screenshot_10.png

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
  ◆ [DISTORTION] 흔들림 저감을 위한 보강대 2개 적용 (axis=structure)
     → 정답: 보강대 2개
  ◆ [DISTORTION] ㄱ자 짧은 변(리턴)은 독립 다리 대신 책장 유닛이 지지 (axis=connection)
     → 정답: 짧은 변 지지=책장 유닛

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 가방걸이 좌/우 선택 설치 가능함을 시각적으로 안내 (axis=accessory)


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
상단 중앙에 책상 제품 이미지가 큼직하게 배치되어 있다. 하단에는 네 줄의 표 형태 텍스트가 좌우로 정렬되어 있다. 각 텍스트 줄은 왼쪽에 항목명, 오른쪽에 상세 설명이 있다. 표는 얇은 가로선으로 구분되어 있다. 전체적으로 여백이 넓고, 요소 간 간격이 균일하다. 제품 이미지는 표와 충분히 떨어져 있다.

Elements:
  - product_image @ 상단 중앙: 흰색 배경 위에 놓인 직사각형 책상
  - table_top_label @ 하단 표 첫 번째 줄 좌측: 책상 상판
  - table_top_value @ 하단 표 첫 번째 줄 우측: 23mm PB + LPM
  - leg_label @ 하단 표 두 번째 줄 좌측: 책상 다리
  - leg_value @ 하단 표 두 번째 줄 우측: 철제 + 분체도장
  - edge_label @ 하단 표 세 번째 줄 좌측: 가방걸이
  - edge_value @ 하단 표 세 번째 줄 우측: ABS
  - pb_grade_label @ 하단 표 네 번째 줄 좌측: PB 자재등급
  - pb_grade_value @ 하단 표 네 번째 줄 우측: E0

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — structure_chart:
[1] 제품 이미지 교체: 상단 중앙의 사각 테이블 이미지를 사용자 제품 '한샘 티오 ㄱ자책상 160cm'로 교체. ㄱ자(L자) 구성과 하부 책장형 수납 구조가 한눈에 보이도록 3/4 시점(좌우 어느 방향이든 ㄱ자 형태가 명확히 드러나는 각도)으로 촬영된 컷 사용. 상판 모서리는 라운드 처리 느낌이 보이게, 다리는 상판과 동일 계열 색으로 통일감 있게 표현. 다리 하단에 손으로 조절 가능한 레벨러가 보이면 반영. 하부 보강대(2개)가 프레임 안에서 살짝 보이면 자연스럽게 노출하되, 안 보이면 추가 연출은 생략. 배경은 완전 흰색 유지.
[2] 하단 4줄 표의 우측 값만 사용자 제품 기준으로 치환. 좌측 항목명(라벨)은 그대로 유지. 텍스트는 한글 가독성 유지, 줄바꿈 없이 한 줄로 배치.
  • 1행 우측값: '23mm PB + LPM' → 'LPM 표면재, 열·압력 접합'
  • 2행 우측값: '철제 + 분체도장' → '라인·색상 통일 마감, 레벨러 적용'
  • 3행 우측값: 'ABS' → '1개 기본 제공, 좌/우 선택 설치'
  • 4행 우측값: 'E0' → 'E0 등급(≤0.5 mg/L)'
[3] 표의 얇은 가로 구분선, 좌우 정렬, 행 높이와 좌우 여백은 원본과 동일하게 유지. 텍스트 대비/크기는 원본과 유사한 단계로 매칭.
[4] 제품 색상 명시는 원본에도 없으며 사용자 제공 컬러명 정보 없음 → 컬러명 표기 추가하지 않음. 한샘 컬러명 잔존 금지.
[5] 레이아웃은 상단 큰 제품 이미지 + 하단 4행 표 구조를 그대로 유지. 표와 제품 이미지 간 간격은 원본 간격을 재현.
[6] 소스/레퍼런스: 제품 외관과 디테일(ㄱ자 구조, 하부 책장, 라운드 모서리, 레벨러)은 screenshot_03.png, screenshot_10.png를 우선 참조해 정확히 반영.

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

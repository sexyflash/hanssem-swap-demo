TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png
  IMAGE 4 = USER PRODUCT — screenshot_08.png
  IMAGE 5 = USER PRODUCT — screenshot_04.png
  IMAGE 6 = USER PRODUCT — screenshot_07.png

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
책상은 화면 하단을 가로지르며 중앙에 위치한다. 책상 위 중앙에는 펼쳐진 노트와 그 아래에 놓인 녹색 책이 있다. 노트 오른쪽에는 자와 투명한 컵이 나란히 놓여 있다. 책상 오른쪽 끝에는 작은 화분과 책꽂이에 정리된 책들이 있다. 책상 위 벽 중앙에는 긴 막대형 스탠드 조명이 세워져 있다. 벽 왼쪽에는 네 장의 엽서와 종이가 붙어 있다. 책상 오른쪽 벽에는 헤드폰이 걸려 있고, 책상 아래에는 수납장이 있다.

Elements:
  - desk @ bottom center, spanning horizontally: 흰색 직사각형 책상
  - notebook @ center on desk: 펼쳐진 노트
  - book @ under notebook, center: 녹색 표지 책
  - ruler @ right of notebook, center: 나무 자
  - cup @ right of ruler, center-right: 투명한 컵
  - plant @ far right on desk: 작은 화분
  - books @ far right, in vertical file holders: 책꽂이에 정리된 책들
  - lamp @ center back, against wall: 긴 막대형 스탠드 조명
  - wall decor @ upper left wall: 네 장의 엽서 및 종이
  - headphones @ right wall, hanging: 걸려 있는 헤드폰
  - shelf @ under desk, right: 수납장

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — lifestyle_scene:
[1] 책상 교체(형상): 화면 하단을 가로지르는 직사각형 책상을 '한샘 티오 ㄱ자책상 160cm'의 ㄱ자(L자) 상판으로 변경. 우측으로 짧은 보조 상판이 90도로 이어지도록 하며, 상판/엣지는 라운드 처리. 컬러는 단색 화이트, 상판 두께는 기존 이미지와 자연스럽게 맞춤.
[2] 하부 수납 일체화: 우측 하단 수납장을 제품의 책장형 수납으로 통합해 ㄱ자 보조 상판과 연속된 구조로 표현. 오픈형 칸 구성으로, PC 본체가 들어갈 큰 칸 1개와 일반 책 수납용 칸 1~2개를 배치. 마감/색상은 상판과 동일하게 통일.
[3] 다리/프레임: 노출되는 다리는 상판과 같은 컬러·질감으로 매끈하게 정리. 다리 하단에 소형 원형 레벨러 팁을 은은하게 표현(과장 금지).
[4] 보강대 암시: 상판 하부 내부에 보강대 2개가 있는 느낌을 약한 그림자/선으로 간접 표현(외부 노출 구조물 추가 금지).
[5] 가방걸이 추가: 상판 앞모서리 좌측 하부에 소형 가방걸이 1개 장착(빈 상태). 본체 색과 조화되는 중성 톤으로 미세 노출.
[6] 표면 질감: LPM 무광 질감과 미세한 반사를 자연스럽게 재현(문구/로고 삽입 금지).
[7] 기존 소품/배치 유지: 노트, 녹색 책, 자, 투명 컵, 우측 화분, 책꽂이 속 책들은 현 위치/각도 그대로 유지. ㄱ자 보조 상판 위에는 새로운 소품 추가 금지.
[8] 조명·벽면 요소 유지: 중앙 막대형 스탠드 조명, 좌측 엽서 4장, 우측 벽 헤드폰 훅은 변경 없이 유지. 조명 톤과 그림자 분위기 유지.
KEEP: 카메라 각도(상단 사선), 프레이밍, 배경 벽 톤/광량, 전체 미니멀 분위기, 한국어 텍스트 비노출 상태.

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

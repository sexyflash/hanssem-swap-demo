TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png
  IMAGE 4 = USER PRODUCT — screenshot_10.png
  IMAGE 5 = USER PRODUCT — screenshot_01.png

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
  ◆ [DISTORTION] 상판 외곽 모서리 라운드 처리 (axis=edges)
     → 정답: 라운드 모서리
  ✗ [FORBIDDEN] 상판 타공형 전원 콘센트/케이블홀/팝업 모듈 없음 — 결과에 보이면 fail
  ✗ [FORBIDDEN] 기본 구성 이미지에서 하부 설치형 콘센트 노출 금지(선택 액세서리는 별도 패널에서만) — 결과에 보이면 fail
  ✗ [FORBIDDEN] 책상 상부에 결합된 상부 선반/헛치 없음 — 결과에 보이면 fail
  ✗ [FORBIDDEN] 책상 본체에 USB 포트/LED 조명 등 전장품 내장 없음 — 결과에 보이면 fail




=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
상단 2/3는 밝은 자연광이 들어오는 창가 앞에 책상과 의자가 배치된 실내 공간 사진이 크게 차지한다. 책상 위에는 모니터, 스탠드, 펜꽂이, 안경, 노트가 정돈되어 있다. 의자 등받이에는 헤드폰이 걸려 있고, 책상 아래에는 파란색 수납 바구니가 있다. 오른쪽 배경에는 하얀색 수납장이 있고, 책과 소품이 진열되어 있다. 하단 1/3에는 연한 회색 배경 위에 제품명과 설명 텍스트가 좌측 정렬로 배치되어 있다. 텍스트는 상단에 굵은 제목, 하단에 설명문이 있다.

Elements:
  - product @ 중앙 하단부, 책상과 의자: 심플한 디자인의 흰색 책상과 회색 메쉬 의자
  - props @ 책상 위: 모니터, 스탠드, 펜꽂이, 안경, 노트
  - props @ 의자 등받이: 블랙 헤드폰
  - props @ 책상 아래: 파란색 펠트 수납 바구니
  - background @ 오른쪽 상단: 하얀색 수납장과 진열된 책, 소품
  - window @ 좌측 상단: 커튼이 드리워진 큰 창, 바깥 풍경 일부 노출

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — intro_hero:
[1] 제품 교체: 화면 중앙의 직선형 단일 책상을 사용자 제품 '한샘 티오 ㄱ자책상 160cm'의 ㄱ자(L자) 형태로 교체. 메인 상판(160cm)은 현재 책상과 같은 방향으로 배치하고, 보조 상판(짧은 변)은 화면 오른쪽으로 꺾여 들어가도록 구성.
[2] 하부 수납 구현: 보조 상판 아래에 책장형 수납 구조(오픈형 칸막이)를 2~3칸 정도 배치하여 책/PC 본체가 들어갈 수 있음을 시각화. 상·하부 컬러/마감은 상판과 동일하게 통일.
[3] 모서리/엣지: 상판 전면·코너 모두 라운드 처리 형태로 변경(날카로운 각 제거).
[4] 다리/하부: 심플한 일자형 다리로 유지하되 상판과 동일 색으로 통일. 각 다리 하단에 소형 레벨러(원형 또는 낮은 디스크형)를 표현해 미세 수평 조절 가능함을 암시.
[5] 가방걸이: 기본 제공 1개를 전면 우측 하단(카메라에 잘 보이는 위치) 또는 보조 상판 측면 하단에 설치. 데일리 가방 하나를 걸어 기능을 자연스럽게 전달. 금속 훅은 미니멀한 형태로 표현.
[6] 안정 보강: 프레임 하부에 보강대 2개가 보이는 각도라면 얇고 심플하게 표시(프레임 내부에 정갈히 배치). 프레임 밖이거나 가려지면 생략 가능.
[7] 소재감: 상판은 스크래치에 강한 LPM 표면의 부드러운 매트 질감으로 표현(광택 과도 금지).
[8] 상판 배치/소품: 모니터·스탠드·펜꽂이·안경·노트를 메인 상판 쪽에 정돈 배치. ㄱ자 보조 상판은 여유 공간으로 보이게 가볍게 비워 두거나 노트 1권 정도만 유지.
[9] 전원 모듈: 선택 추가 항목이므로 상판 타공형/상부 노출형 콘센트는 노출 금지. 하부 설치형도 본 패널에서는 미표현.
[10] 하단 텍스트 영역 교체: 제목을 '한샘 티오 ㄱ자책상 160cm'로, 설명문을 사용자 제공 소개 문구 기반의 3문장으로 교체. 좌측 정렬, 기존 폰트 스타일/행간 유지.
[11] 브랜드/라벨: 한샘 컬러명 표기 없음. 불필요한 로고 삽입 금지.
KEEP: 카메라 각도, 자연광/창, 오른쪽 수납장과 소품, 의자(메쉬·바퀴), 의자에 걸린 헤드폰, 책상 아래 파란색 펠트 바구니, 전체 배경 톤, 하단 1/3 텍스트 레이아웃 및 가독성.

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

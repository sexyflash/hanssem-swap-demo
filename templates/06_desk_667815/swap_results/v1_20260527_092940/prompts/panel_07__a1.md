TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png
  IMAGE 4 = USER PRODUCT — screenshot_07.png
  IMAGE 5 = USER PRODUCT — screenshot_06.png
  IMAGE 6 = USER PRODUCT — screenshot_09.png

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
상단 오른쪽에 밝은 나무색상의 테이블 상판이 대각선 방향으로 배치되어 있다. 테이블 상판의 왼쪽 아래 모서리가 둥글게 처리되어 있다. 하단 왼쪽에는 흰색 원통형 다리가 수직으로 연결되어 있다. 상단 오른쪽에는 주황색 표지의 얇은 책자가 테이블 위에 일부만 보이게 놓여 있다. 배경은 완전히 흰색으로, 다른 요소는 없다. 테이블 상판의 표면 질감이 잘 드러난다.

Elements:
  - product_surface @ 상단 오른쪽~중앙: 밝은 나무색 테이블 상판, 둥근 모서리
  - product_leg @ 하단 왼쪽: 흰색 원통형 테이블 다리
  - prop @ 상단 오른쪽: 주황색 표지의 얇은 책자, 일부만 노출

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — detail_close_up:
[1] 상판 질감/색감 치환: 상판을 한샘 '티오 ㄱ자책상 160cm'의 LPM 표면처럼 미세 무광의 스크래치 저항 느낌으로 표현. 밝은 나무색 톤 유지하되 상판 윗면과 엣지(측면) 색을 동일 톤으로 최대한 통일하고, 라운드 모서리(곡률)와 두께감은 원본과 동일 수준으로 유지.
[2] 엣지/모서리 처리: 라운드 처리 존재가 명확히 보이도록 하되 과도한 강조는 금지. 접합면은 LPM 적층 느낌의 매우 미세한 층 표현만 허용(거친 이음선 금지).
[3] 다리 외관 정합: 하단 왼쪽의 원통형 다리를 티오 시리즈 콘셉트에 맞게 순백(무광~세미매트)으로 정리. 파이프 이음/캡/나사 보임 없이 "다리 끝까지 통일된 라인과 색감" 인상 유지. 프레임 내에서는 레벨러 비노출(하단이 화면 밖이므로 추가 표현 금지).
[4] ㄱ자 책상 요소 노출 규칙: 본 패널은 코너 클로즈업이므로 ㄱ자 전체 형상, 하부 수납장/보강대 등은 노출하지 않는다. 현재 프레임 내에 보이는 상판 모서리+단일 다리 구성만 유지.
[5] 소품 처리: 상단 오른쪽의 주황색 얇은 책자는 위치/각도/두께 유지. 표지의 로고/브랜드/판독 가능한 텍스트는 모두 제거하고 의미 없는 더미 라인/블록으로 대체(한샘/브랜드 표기 완전 제거).
[6] 라이팅/배경/구도: 배경 완전 흰색, 상판이 화면 우상향 대각으로 배치된 구도, 그림자 농도와 방향은 원본 수준으로 유지. 카메라 각도/크롭 동일 유지.
KEEP: 레이아웃(상판 우상향 대각 배치), 라운드 모서리의 위치, 다리의 수직 배치와 굵기 비율, 소품의 위치/색, 배경의 완전 흰색 톤, 한국어 텍스트 비노출 상태.

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

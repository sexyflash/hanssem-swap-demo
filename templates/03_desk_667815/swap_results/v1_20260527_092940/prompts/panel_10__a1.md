TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png
  IMAGE 4 = USER PRODUCT — screenshot_07.png
  IMAGE 5 = USER PRODUCT — screenshot_06.png
  IMAGE 6 = USER PRODUCT — screenshot_04.png

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
이미지 중앙에는 흰색 책상 모서리가 클로즈업되어 있다. 책상 상판 위 왼쪽에는 투명한 유리컵이 놓여 있고, 오른쪽에는 태블릿과 키보드가 부분적으로 보인다. 책상 하단 전면에는 흰색 전원 멀티탭이 고정되어 있으며, 멀티탭에는 충전기가 꽂혀 있고 케이블이 상판 위로 올라간다. 책상 다리는 왼쪽 하단에 위치하며, 책상 아래 선반 일부가 오른쪽 하단에 보인다. 전체적으로 제품의 기능적 디테일에 초점을 맞춘 구도이다.

Elements:
  - desk_surface @ center, top: 흰색 책상 상판, 모서리 부분이 강조됨
  - glass_cup @ top left on desk: 투명 유리컵, 'Paris' 텍스트 인쇄
  - tablet_keyboard @ top right on desk: 부분적으로 보이는 태블릿과 키보드
  - power_strip @ center bottom under desk: 책상 하단에 고정된 흰색 멀티탭, 충전기 연결됨
  - charging_cable @ from power strip to desk surface: 멀티탭에서 상판 위로 올라가는 충전 케이블
  - desk_leg @ bottom left: 흰색 책상 다리
  - shelf @ bottom right: 책상 아래 선반 일부

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — detail_close_up:
[1] 상판/모서리 치환: 데스크 상판과 모서리를 '한샘 티오 ㄱ자책상 160cm'의 라운드 처리 형태와 무광 LPM 표면 질감으로 교체. 엣지의 부드러운 곡률과 깔끔한 라인감을 강조하되 두께감/비율은 현재 구도 유지.
[2] 하부 수납 디테일: 프레임 우하단에 보이는 선반 파트를 티오의 '하부 책장형 수납' 일부처럼 보이도록 보정(수직 분할판+선반 조합, 단정한 이음부, 노출 나사/캡 최소화). ㄱ자 구성임을 암시하되 프레임 밖 구조는 추가 노출하지 않음.
[3] 하부 설치형 콘센트: 현재 고정된 멀티탭을 티오 시리즈의 선택 액세서리(하부형 콘센트) 느낌의 무지(로고 없음) 화이트 하우징으로 교체. 고정 위치/각도/볼트 위치는 현 구도에 맞춰 동일하게 유지. 포트 개수와 플러그가 꽂힌 상태 등 원본의 구도는 그대로 재현하되 브랜드/문자 인쇄는 제거.
[4] 케이블 동선: 멀티탭에서 상판 위로 자연스럽게 올라오는 케이블 흐름 유지. 케이블 색상은 중성 회색/백색 톤으로 정리.
[5] 다리 보정: 좌하단 책상 다리를 티오의 통일된 컬러 마감으로 정리(백색 톤, 매끈한 실루엣). 레벨러는 프레임 밖이므로 노출하지 않음.
[6] 소품/배경: 상판 위 유리컵(영문 'Paris' 프린트), 태블릿+키보드는 위치/각도 그대로 유지. 단, 제품과 무관한 브랜드 로고가 보이면 제거 또는 무지 처리.
[7] 재질/광택: LPM 표면의 미세한 무광과 부드러운 하이라이트를 주어 스크래치에 강한 표면감이 느껴지게 톤 보정. 과도한 반사/글로시 느낌은 억제.
[8] 안전 인상: 전원부가 상판 하부 쪽으로 살짝 후퇴해 보이도록 음영을 조정(액체 유입 위험을 시각적으로 낮춰 보이게). 추가 구조물(보강대, 가방걸이 등)은 본 프레임에 보이지 않으므로 새로 추가하지 않음.
KEEP: 카메라 각도, 크롭, 조명 방향/세기, 소품 배치, 케이블 곡률, 전체 화이트 톤 배경.

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

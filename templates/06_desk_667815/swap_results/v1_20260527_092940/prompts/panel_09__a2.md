=== [RETRY ANALYSIS · stage 1] ===
diagnosis: 클로즈업 패널 고정 레이아웃을 그대로 유지한 탓에 수납부, 가방걸이, 보강대 2개 등 핵심 정체성 요소가 프레임 밖으로 밀려 ‘검증 불가’로 처리되었습니다. 또한 NEVER-MISS 문구가 패널 범위를 넘는 표현을 유도해, 보이지 않는 요소를 억지로 넣을 여지를 남겼습니다.
patches:
  - 패널 범위 내에서 반드시 보여야 하는 정체성(라운드 모서리, LPM 무광 상판, 원통형 흰색 다리+레벨러)을 최상단에 ‘must-render’로 명시하고, 프레임 밖 요소(오픈 수납, 가방걸이, 보강대)는 ‘의도적 비노출’로 고지.
  - NEVER-MISS 조항을 ‘본 패널 프레임 내에서 표현 가능한 항목’으로 한정하여, 보이지 않는 기능을 끼워 넣지 않도록 금지 문구를 강화.
  - 레퍼런스 앵커를 구체화: screenshot_03(모서리 곡률/엣지 밴딩), screenshot_06(레벨러 형태/분할선), screenshot_07(다리 색톤·광택 통일)을 그대로 따르라고 지시.
  - 다리 직경/톤/광택 완전 일치, 하드웨어 노출 최소화 등 프레임 안에서 검증 가능한 디테일을 더 선명하게 규정.

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

TASK: Edit this Korean detail-page panel — swap to user's product.

PANEL TYPE: detail_close_up · single panel · panel C 레이아웃 그대로 유지

CRITICAL VISIBILITY (must-render in this close-up frame only):
- 상판 라운드 모서리 형태가 분명히 보일 것
- LPM 계열 무광/세미무광 우드 패턴 상판(유리/석재/라이브엣지 아님)
- 흰색 원통형 다리 2개(좌측 결합/우측 단독) 동일 톤·광택·직경으로 통일 + 하부 레벨러 노출

OUT-OF-FRAME (intentionally not shown in this panel — do NOT insert or imply):
- 하부 오픈 수납(도어/서랍 유무 포함), 가방걸이 1개, 보강대 2개, ㄱ자 전체 실루엣, 콘센트/액세서리 등 프레임 밖 요소 일체

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
- IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
- IMAGE 2 = SMART SHEET (패널별 가이드 메타 · 결과로 복제 X)
- IMAGE 3 = USER PRODUCT — screenshot_03.png
- IMAGE 4 = USER PRODUCT — screenshot_07.png
- IMAGE 5 = USER PRODUCT — screenshot_06.png

TARGET: 한샘 티오 ㄱ자책상 160cm
제원: 160×None×Nonecm
핵심 정체성(참고): 오픈 선반형 수납(도어/서랍 없음), 라운드 모서리, 가방걸이 1개, 보강대 2개, LPM 상판

ANCHORS — 아래 레퍼런스의 해당 디테일을 그대로 반영:
- screenshot_03.png: 상판 모서리의 곡률, 엣지 라인/밴딩의 두께감과 연결감을 그대로 따를 것.
- screenshot_07.png: 다리 표면의 무광 수준, 흰색 톤 값(밝기/채도), 상단~하단까지 일관된 재질감을 동일하게 맞출 것.
- screenshot_06.png: 레벨러의 얇은 원형 베이스 돌출과 회전 조절 분할선 위치/두께를 동일 계열 색으로 섬세하게 표현.

SPATIAL LAYOUT TO PRESERVE — panel C와 동일:
- 좌측 상단: 밝은 나무 무늬의 상판 모서리가 크게 클로즈업
- 좌측 하단: 상판에 연결된 흰색 원통형 다리 수직 결합
- 우측 중앙: 동일 스펙의 흰색 원통형 다리 단독 세로 배치
- 배경은 전체 흰색, 텍스트/아이콘/추가 오브젝트 없음

EDIT INSTRUCTIONS — detail_close_up:
[1] 상판 모서리 교체 (대상: tabletop_corner)
- ‘한샘 티오 ㄱ자책상 160cm’의 LPM 상판으로 변경.
- 라운드 모서리 곡률은 panel C의 감각 유지(과도한 각/과곡 금지).
- 표면은 무광/세미무광, 잔잔한 목무늬. 하이글로시 하이라이트 금지.
- 가장자리 엣지 밴딩 이색/들뜸 없이 매끈하게. 두께 비율은 원본과 유사.
- 앵커: screenshot_03의 곡률/엣지 라인 그대로 반영.

[2] 상판-다리 결합부 정리 (대상: table_leg_attached)
- 결합부 하드웨어 노출 최소화, 라인이 깨끗하게 이어지도록 정돈.
- 다리와 결합부의 색/광택 완전 일치(‘다리 끝까지 통일된 라인과 색감’ 인상).

[3] 다리 형태/마감 통일 + 레벨러 반영 (대상: table_leg_attached, table_leg_isolated)
- 두 다리 모두 원통형, 흰색 톤, 무광/세미무광으로 상단~하단 일관.
- 직경/톤/광택 스펙 일치. 금속성 반사/색 대비 과장 금지.
- 레벨러: 하단에 얇은 원형 베이스가 살짝 돌출, 회전 조절 분할선 표시(동일 색 계열의 미세한 이음새).
- 앵커: screenshot_07(톤/광택), screenshot_06(레벨러 형태/분할선) 그대로 재현.

[4] 불필요 요소 추가 금지
- 본 패널은 클로즈업 프레임 내 디테일만. 수납부/보강대/가방걸이/콘센트/ㄱ자 전경 등 프레임 밖 요소 삽입/암시 금지.
- 텍스트/로고/아이콘 추가 금지.

KEEP:
- panel C의 카메라 각도/거리, 구도(좌상단 상판-좌하단 연결 다리 + 우중앙 단독 다리로 화면 양분), 흰 배경/조명 톤, 명암/노출 밸런스, 빈 공간 구성 유지.

ABSOLUTE RULES — PRESERVE / NEVER
PRESERVE:
- panel C와 같은 single panel layout, 한국 detail page 톤
- 사용자 제품의 검증 가능한 특징을 프레임 내에서 명확히 표현(라운드 모서리, LPM 상판, 원통형 흰색 다리+레벨러)
- 위 앵커 레퍼런스의 곡률/톤/레벨러 디테일
NEVER:
- 프레임 밖 정체성(오픈 수납, 가방걸이, 보강대 등) 억지로 노출/암시/발명
- 유리/석재/라이브엣지처럼 보이게 처리
- 한샘 원본 텍스트 잔존, multi-cell grid, 한글 텍스트 깨짐
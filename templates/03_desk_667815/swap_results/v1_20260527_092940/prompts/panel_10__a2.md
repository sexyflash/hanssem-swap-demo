=== [RETRY ANALYSIS · stage 1] ===
diagnosis: 클로즈업 구도에서 가방걸이와 보강대가 프레임 밖으로 빠지거나 다른 부품으로 혼동될 여지가 있었고, 이전 프롬프트가 ‘프레임에 보이지 않으므로 추가하지 않음’이라고 제한해 가시화가 차단되었습니다. 또한 하드웨어 위치/형상에 대한 레퍼런스 앵커가 없어 멀티탭 고정부와 보강대가 구분되지 않았습니다.
patches:
  - 가방걸이 1개와 보강대 2개를 프레임 내부에서 명확히 식별되도록 의무 표시. 멀티탭 고정부와 보강대를 시각적으로 분리하도록 대비/배치 지시 추가.
  - 레퍼런스 앵커 지정: 가방걸이 형상·피스 위치는 screenshot_07 우선, 보강대 단면·색상은 screenshot_06 우선으로 그대로 복제.
  - 크롭/각도 유지 조건 하에서 좌하단 다리 주변 하부에 가방걸이를 살짝 들여와 노출, 상판 하부 전면에 평행한 보강대 2개가 동시에 보이도록 음영·노출값 조정.
  - NEVER 강화: 보강대를 1개로 축소하거나 멀티탭 브라켓을 보강대로 대체하지 말 것, 가방걸이를 2개 이상으로 표현하지 말 것.

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
· overall_silhouette: 넓은 상판과 하부책장이 만난 ㄱ자(L자) 구성
· storage_detail: 하부 책장형 오픈 수납
· edges_corners: 라운드 모서리
· hooks_hangers: 가방걸이 1개 기본 제공(좌/우 선택 설치)
· legs_detail: 통일 컬러 마감, 하부 레벨러
· stability_structure: 보강대 2개 적용 구조
· materials_surface: 스크래치에 강한 LPM 표면(불투명 패널)
· safety_features: E0 등급 자재
· power_access: 선택 추가 하부형 콘센트
· accessories_compatibility: 전용 액세서리 호환

[NEVER-MISS — 이 패널에서 프레임 안에 반드시 시각화]
1) 가방걸이 1개(좌/우 중 한쪽, 이 프레임에서는 좌하단 다리 인접 하부에 노출되도록 배치)
2) 흔들림 저감용 보강대 2개(상판 하부 전면부에 서로 평행하게 2개가 동시에 구분되게 노출)

[SPATIAL LAYOUT TO PRESERVE — panel C와 동일]
이미지 중앙에는 흰색 책상 모서리가 클로즈업되어 있다. 책상 상판 위 왼쪽에는 투명한 유리컵이 놓여 있고, 오른쪽에는 태블릿과 키보드가 부분적으로 보인다. 책상 하단 전면에는 흰색 전원 멀티탭이 고정되어 있으며, 멀티탭에는 충전기가 꽂혀 있고 케이블이 상판 위로 올라간다. 책상 다리는 왼쪽 하단에 위치하며, 책상 아래 선반 일부가 오른쪽 하단에 보인다. 전체적으로 제품의 기능적 디테일에 초점을 맞춘 구도이다.
Elements:
  - desk_surface @ center, top: 흰색 책상 상판, 모서리 부분이 강조됨
  - glass_cup @ top left on desk: 투명 유리컵, 'Paris' 텍스트 인쇄
  - tablet_keyboard @ top right on desk: 부분적으로 보이는 태블릿과 키보드
  - power_strip @ center bottom under desk: 책상 하단에 고정된 흰색 멀티탭, 충전기 연결됨
  - charging_cable @ from power strip to desk surface: 멀티탭에서 상판 위로 올라가는 충전 케이블
  - desk_leg @ bottom left: 흰색 책상 다리
  - shelf @ bottom right: 책상 아래 선반 일부
(레이아웃/크롭/카메라 각도/조명은 유지하되, 아래 NEVER-MISS 요소가 프레임 안에서 명확히 보이도록 하부 음영·노출을 미세 조정)

[DETAIL CLOSE-UP — REF ANCHORS]
- 가방걸이 형태·곡률·피스 위치: screenshot_07.png를 1순위로 그대로 재현(없으면 03>06>04 순으로 가장 선명한 레퍼런스 채택). 색상은 제품 마감과 동일 백색/은색 조합.
- 보강대 2개 프로파일(두께/폭), 컬러(백색 또는 제품 하부 프레임색), 부착 위치: screenshot_06.png 1순위(없으면 03>07>04). 두 개가 평행으로 독립 부재임이 식별되게 표현.
- LPM 표면(무광/세미무광) 질감과 라운드 모서리: screenshot_04.png의 하이라이트/텍스처 톤을 참고.
- 오픈 선반 접합부/수직 분할판 마감: screenshot_03.png의 이음 디테일을 따름.

[EXPLICIT EDITS — detail_close_up]
[A] 가방걸이 노출: 좌하단 다리와 상판 하부가 만나는 영역에 ‘가방걸이 1개’를 설치하여 프레임 안에 최소 60% 이상 실루엣이 보이게. 나사/피스 위치와 곡률은 REF ANCHORS 준수. 가방이나 소지품은 걸지 말 것.
[B] 보강대 2개 노출: 상판 하부 전면에 평행한 보강대 2개가 동시에 보이도록 배치/톤 보정. 멀티탭 고정부와는 재질/두께/방향을 달리해 혼동되지 않게 분리(보강대는 좌↔우로 길게, 고정부는 멀티탭 국소 부품으로 보이게).
[1] 상판/모서리 치환: 라운드 처리 형태와 무광 LPM 표면 질감으로 교체. 두께감/비율은 현 구도 유지, 엣지 라인 매끈하게.
[2] 하부 수납 디테일: 우하단 선반을 ‘오픈 책장형’ 일부처럼 보정(수직 분할판+선반, 단정한 이음, 노출 나사 최소화). 도어/서랍 금지.
[3] 하부 설치형 콘센트: 멀티탭을 무지 화이트 하우징으로 교체(포트 개수/플러그 상태/위치·각도·볼트는 동일). 로고/문자 제거.
[4] 케이블 동선: 멀티탭에서 상판 위로 자연스럽게 올라오되 케이블은 중성 회색/백색 톤.
[5] 다리 보정: 좌하단 다리를 백색 톤의 통일 마감으로 정리. 실루엣 매끈하게. 레벨러는 프레임 밖.
[6] 소품/배경: 유리컵(‘Paris’ 프린트), 태블릿+키보드는 위치/각도 그대로. 보이는 브랜드 로고는 제거/무지 처리.
[7] 재질/광택: LPM의 미세 무광과 부드러운 하이라이트로 톤 보정. 과도한 반사 억제.
[8] 안전 인상: 전원부가 상판 하부 쪽으로 살짝 후퇴해 보이도록 음영 조정(액체 유입 위험 낮게).
KEEP: 카메라 각도, 크롭, 조명 방향/세기, 소품 배치, 케이블 곡률, 전체 화이트 톤 배경.

[ABSOLUTE RULES — PRESERVE / NEVER]
PRESERVE:
  - panel C와 같은 single panel layout, 한국 detail page 스타일
  - 카메라 각도/배경/조명/한국어 텍스트 가독성
  - 사용자 제품 feature_descriptions에 명시된 모든 특징
  - NEVER-MISS: 가방걸이 1개와 보강대 2개는 결과 이미지에서 반드시 식별 가능하게 표현(프레임 내부)
NEVER:
  - 사용자 제품 정보에 없는 feature 발명(USB, 추가 다리, 서랍/도어 등)
  - 한샘 원본 텍스트 잔존
  - multi-cell grid 출력
  - 한글 텍스트 깨짐
  - 보강대를 1개만 넣거나, 멀티탭 고정부를 보강대로 대체 표현 금지
  - 가방걸이를 2개 이상으로 표현 금지, 프레임 밖으로 밀려 가시성 상실 금지

[검증 주의]
- 보강대 2개는 서로 분리된 부재로 식별 가능해야 하며, 각 부재의 시작/끝이 프레임 밖으로 일부 잘려도 ‘2개’임이 명확해야 합니다.
- 가방걸이는 1개만, 좌/우 중 선택 설치이나 본 프레임에서는 좌하단에 노출되도록 하여 검증 가능성을 높이세요.
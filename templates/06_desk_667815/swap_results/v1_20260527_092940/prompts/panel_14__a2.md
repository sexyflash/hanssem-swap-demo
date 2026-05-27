=== [RETRY ANALYSIS · stage 1] ===
diagnosis: 직전 시도는 제품 구조(ㄱ자 상판·책장 지지·보강대 2개)는 잘 반영했지만, 가방걸이의 좌/우 선택 설치 가능을 시각적으로 안내하지 않아 의도가 전달되지 않았다. 텍스트·라벨을 배제한 레이아웃에 맞춰 하나의 후크만 부착하다 보니 선택 가능성을 증명하는 화살표/대안 위치 표식이 빠진 것이 원인이다.
patches:
  - 가방걸이: 실제 장착 1개 + 반대편 대안 위치 1개를 점선 원(ghost)으로 표시하고, 좌↔우를 잇는 얇은 양방향 화살표를 추가해 '좌/우 선택 설치'를 텍스트 없이도 명확히 전달.
  - 후크 디테일은 screenshot_05.png의 모양·크기·색감을 그대로 따르고, 설치 위치는 screenshot_07.png, screenshot_08.png의 하부 가장자리 위치감을 앵커로 사용.
  - 화살표/점선 스타일은 1px 내외, 중성 회색(#BDBDBD)로 최소화하여 제품 실루엣을 해치지 않도록 하고, 제품 외부 UI 요소처럼 보이지 않게 상판 하부 영역 안에서만 배치.
  - 기존에 통과한 핵심 정체성(ㄱ자 상판+하부 책장 일체, 보강대 2개, 리턴부=책장 지지), 레벨러, 원본 흔적 제거는 그대로 유지.

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

TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png
  IMAGE 4 = USER PRODUCT — screenshot_08.png
  IMAGE 5 = USER PRODUCT — screenshot_07.png
  IMAGE 6 = USER PRODUCT — screenshot_05.png

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
· materials_surface: 상판은 스크래치에 강한 LPM 표면재.
· safety_features: E0 등급 자재 사용.
· power_access: 선택 추가 가능한 하부 설치형 콘센트(좌/우 선택).
· accessories_compatibility: 티오 시리즈 전용 선택 액세서리 호환.
· modularity_fit: 티오 벙커침대 하부 공간 규격 호환.

=== [★ NEVER-MISS · 최우선 반영] ===
  ◆ ㄱ자(L자) 형태 상판과 하부 책장 유닛이 결합된 일체형 구성 (axis=frame)
  ◆ 흔들림 저감을 위한 보강대 2개 적용 (axis=structure)
  ◆ ㄱ자 짧은 변(리턴)은 독립 다리 대신 책장 유닛이 지지 (axis=connection)
  ◆ 가방걸이 좌/우 선택 설치 가능을 시각적으로 안내: 실제 장착 1개 + 반대편 대안 위치(점선 원 표시) + 좌↔우 얇은 양방향 화살표로 텍스트 없이 명확 표현

=== [CHART/STRUCTURE panel 특화 — 보존 규칙] ===
  - panel C의 단일 패널 레이아웃, 카메라 각도, 배경 톤을 그대로 유지.
  - 본 panel C에는 측정선/숫자 라벨이 보이지 않으므로 새로 추가하지 말 것. 존재하는 경우에 한해 색/굵기/위치 100% 보존.

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
패널 중앙에 흰색 직사각형 테이블이 뒤집힌 상태로 배치되어 있다. 테이블의 네 모서리에는 네 개의 원기둥 다리가 수직으로 위를 향해 똑같은 간격으로 세워져 있다. 테이블 상판은 화면의 중앙에서 약간 오른쪽 아래로 기울어져 있다. 배경은 완전히 흰색으로, 다른 시각적 요소나 텍스트는 없다. 테이블 다리와 상판의 연결부가 명확하게 드러나 있다. 전체적으로 제품만 단독으로 강조되어 있다.

Elements:
  - product_main @ center, 약간 오른쪽 아래로 기울어짐: 흰색 직사각형 테이블, 네 개의 원기둥 다리가 위로 세워진 상태

=== [EDIT INSTRUCTIONS — structure_chart] ===
[0] 좌/우 가방걸이 안내(필수):
  - 실제 후크 1개는 상판 하부 전면 가장자리(좌/우 임의) 쪽에 부착.
  - 반대편에는 동일 위치에 얇은 점선 원(ghost mount)으로 대안 설치 지점을 표시.
  - 두 지점을 잇는 얇은 양방향 화살표(1px 내외, 중성 회색 #BDBDBD, 그림자/글로우 없음)를 상판 하부 영역 안에서만 배치해 텍스트 없이 좌/우 선택 설치 가능을 명확히 보여줄 것.
  - 후크 모양·크기·마감은 screenshot_05.png를 그대로 따르고, 설치 위치감은 screenshot_07.png, screenshot_08.png를 앵커로 삼아 동일하게 재현.
[1] 제품 형상 교체: 뒤집힌 사각 테이블을 "한샘 티오 ㄱ자책상 160cm"의 뒤집힌 ㄱ자(L자) 상판으로 변경. 상판은 라운드 엣지, 현실적 두께. 화면 중앙에 두고 약간 오른쪽 아래로 기울어진 각도 유지.
[2] 지지구조 재구성: 원통형 다리 4개 전부 제거. ㄱ자 구조에 맞는 하부 "책장형 수납 프레임"과 패널형 지지부로 교체. 오픈형 2~3칸이 보이되 과장 금지. 지지부/프레임 색상은 상판과 동일 계열 단색으로 통일. 하부 리턴부 지지는 독립 다리 없이 책장 유닛으로 표현.
[3] 보강대 2개 추가: 상판 하부에 평행한 보강대 2개를 긴 변을 따라 명확히 배치. 체결 볼트/브래킷 노출 최소화.
[4] 레벨러 표현: 모든 지지 하단에 수평 조절 레벨러 추가. 뒤집힌 상태이므로 레벨러 조절부가 위를 향하도록(소형 원형, 색상 통일).
[5] 표면/재질 디테일: 상판은 LPM 특유의 미세 무늬·반무광 질감, 라운드 엣지와 깔끔한 마감선 강조. 접착 흔적/목공결 노출 금지.
[6] 크기/비율: 긴 변이 160cm임을 암시하는 프로포션으로 프레임 내 스케일 조정(치수 텍스트/자막 금지). 리턴 길이는 일반적 L-데스크 비율로 과장 금지.
[7] 조명/배경: 완전 흰 배경, 부드러운 자연스러운 그림자 유지. 노출/화이트밸런스는 panel C 톤에 맞춤.
[8] 원본 흔적 제거: 기존 사각 상판, 원통형 다리, 체결 홈/나사 패턴 등 원본 테이블 요소 잔존 금지.
[9] 레퍼런스 반영 앵커:
   - 하부 책장형 수납 프레임의 칸 구획·비율은 screenshot_03.png를 근접하게 따를 것.
   - 보강대 개수·배치는 screenshot_08.png를 기준으로 동일하게 맞출 것.
   - 가방걸이 형태·색감은 screenshot_05.png, 설치 위치감은 screenshot_07.png를 그대로 재현.

KEEP:
  - panel C와 같은 single panel layout, 한국 detail page 스타일
  - 카메라 각도/배경/조명 유지
  - 사용자 제품 feature_descriptions에 명시된 모든 특징
  - 위 [NEVER-MISS] 항목은 결과 이미지에 반드시 시각적으로 표현

NEVER:
  - 사용자 제품 정보에 없는 feature 발명(USB/추가 다리/헤드레스트 등)
  - 한샘 원본 텍스트 잔존
  - multi-cell grid 출력
  - 한글 텍스트 깨짐
  - NEVER-MISS critical 항목 누락
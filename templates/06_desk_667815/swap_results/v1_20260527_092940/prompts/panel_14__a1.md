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
패널 중앙에 흰색 직사각형 테이블이 뒤집힌 상태로 배치되어 있다. 테이블의 네 모서리에는 네 개의 원기둥 다리가 수직으로 위를 향해 똑같은 간격으로 세워져 있다. 테이블 상판은 화면의 중앙에서 약간 오른쪽 아래로 기울어져 있다. 배경은 완전히 흰색으로, 다른 시각적 요소나 텍스트는 없다. 테이블 다리와 상판의 연결부가 명확하게 드러나 있다. 전체적으로 제품만 단독으로 강조되어 있다.

Elements:
  - product_main @ center, 약간 오른쪽 아래로 기울어짐: 흰색 직사각형 테이블, 네 개의 원기둥 다리가 위로 세워진 상태

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — structure_chart:
[1] 제품 형상 교체: 뒤집힌 사각 테이블을 "한샘 티오 ㄱ자책상 160cm"의 뒤집힌 ㄱ자(L자) 상판으로 변경. 상판은 모서리 라운드 처리, 두께감은 과장 없이 현실적. 화면 중앙에 두고 원본처럼 약간 오른쪽 아래로 기울어진 각도 유지.
[2] 지지구조 재구성: 원통형 다리 4개 전부 제거. 대신 ㄱ자 구조에 맞는 하부 "책장형 수납 프레임"과 패널형 지지부로 교체. 수납 프레임은 오픈형 2~3칸으로 보이도록 하되 과장 금지(PC 본체/책이 들어갈 정도의 폭과 깊이 느낌만). 모든 지지부/프레임은 상판과 동일 계열 단색으로 통일.
[3] 보강대 2개 추가: 상판 하부에 평행한 보강대 2개가 명확히 보이도록 배치(긴 변을 따라 배열). 체결 볼트/브래킷은 최소한만 노출.
[4] 레벨러 표현: 바닥 수평 조절용 레벨러를 모든 지지 하단에 일관되게 추가. 현재 뒤집힌 상태이므로 레벨러 조절부가 위쪽을 향해 보이게 처리(원형/소형, 색상 통일).
[5] 가방걸이 1개: 상판 하부 전면 가장자리 쪽에 소형 가방걸이 1개 부착(좌/우 임의). 단색, 로고/텍스트 없음, 과한 반사광 금지.
[6] 표면/재질 디테일: 상판은 스크래치에 강한 LPM 느낌의 미세한 무늬/반무광 질감만 은은히 표현. 엣지 라운드와 깔끔한 마감선을 강조. 접착제 흔적/목공결 자국 노출 금지.
[7] 크기/비율: 긴 변이 160cm임을 암시하는 비율감으로 프레임 내 스케일 조정(자막/치수 표기 금지). ㄱ자 보조날개는 과도하게 길거나 짧지 않게 일반적인 L-데스크 프로포션으로.
[8] 조명/배경: 완전 흰 배경, 부드러운 자연스러운 그림자 유지. 노출/화이트밸런스는 원본 톤에 맞춤.
[9] 원본 흔적 제거: 기존 사각 상판 형태, 원통형 다리, 체결 홈/나사 패턴 등 원본 테이블 요소 일절 잔존 금지.
[10] 레퍼런스 반영: ㄱ자 하부 책장 형태, 보강대 위치/개수, 레벨러/가방걸이 위치감은 screenshot_03.png, screenshot_05.png, screenshot_07.png, screenshot_08.png를 우선 참고.
KEEP: 프레임 구성(제품 단독, 배경 완전 흰색), 카메라 각도/원근감, 제품이 화면 중앙에 위치한 레이아웃, 텍스트/라벨 없음.

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

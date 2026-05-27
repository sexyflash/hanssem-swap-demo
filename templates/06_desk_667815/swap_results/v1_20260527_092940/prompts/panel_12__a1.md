TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png
  IMAGE 4 = USER PRODUCT — screenshot_10.png
  IMAGE 5 = USER PRODUCT — screenshot_01.png
  IMAGE 6 = USER PRODUCT — screenshot_08.png

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
왼쪽 하단에는 바퀴가 달린 흰색 사무용 의자가 위치해 있다. 중앙에는 바퀴가 달린 3단 서랍장이 책상 아래에 배치되어 있다. 책상 상판은 화면 상단을 가로지르며, 상판 위에는 책과 소품이 놓여 있다. 오른쪽에는 오픈형 책장이 있으며, 중간 선반에는 빨간색 수납함과 책들이 정렬되어 있다. 책장 하단에는 여러 권의 책이 세로로 정렬되어 있다. 전체적으로 제품들이 직각으로 정렬되어 있으며, 바닥은 보이지 않는다.

Elements:
  - 의자 @ 왼쪽 하단: 흰색 프레임, 회색 방석, 바퀴 달림
  - 서랍장 @ 중앙: 흰색, 3단, 바퀴 달림, 책상 아래에 위치
  - 책상 @ 상단 전체: 흰색, 상판 위에 책과 소품 배치
  - 책장 @ 오른쪽: 오픈형, 여러 칸, 책과 수납함 정렬
  - 수납함 @ 책장 중간 선반: 빨간색, 직사각형
  - 책 @ 책장 및 책상 위: 다양한 크기, 세로 및 가로 정렬

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — lifestyle_scene:
[1] 책상 본체 교체: 현재 일자형 상판을 '한샘 티오 ㄱ자책상 160cm' 형태로 변경. 우측에서 전면(아래쪽)으로 짧은 리턴 상판이 이어지는 ㄱ자(L자) 구성을 만들고, 리턴을 지지하는 하부 책장(일체형 수납)으로 연결되게 표현.
[2] 우측 독립형 오픈 책장 제거 → 동일 위치에 책상 일체형 '하부 책장'으로 대체: 2~3칸 수납 격자로 설계(PC 본체/책 수납 가능 느낌). 현재 보이는 빨간 수납함과 책들은 이 하부 책장 칸에 재배치(가운데 칸에 빨간 수납함, 나머지 칸에 세로/가로 도서 혼합).
[3] 중앙의 바퀴 달린 3단 이동서랍은 노출 제거(옵션 액세서리 혼동 방지). 제거 후 무릎 공간을 넓게 확보한 모습으로 자연스러운 그림자 정리.
[4] 상판/모서리 디테일: 상판 전·측면 엣지와 코너를 라운드(소프트 R)로 업데이트. 하이라이트와 반사 표현은 은은한 무광(LPM) 질감으로 조정.
[5] 가방걸이 1개 추가: 메인 상판 좌측 하부(의자 가까운 측면)에 소형 훅 1개 노출. 베이지 톤 무지 토트백 1개를 걸어 기본 제공 훅을 직관적으로 표현(브랜드/로고 미노출).
[6] 지지부/레벨러: 보이는 지지부 하단에 소형 원형 레벨러(다크 그레이)만 간접 노출. 과도한 기구 노출 없이 높이 미세 조절 가능 느낌만 전달.
[7] 표면/재질: LPM 표면의 미세한 무광과 내스크래치 인상을 주되 텍스처 과장 금지. 이음부(ㄱ자 코너) 맞춤선은 깨끗하고 균일하게.
[8] 전원 액세서리(하부형 콘센트)는 선택 옵션이므로 이미지 내 노출하지 않음. 케이블/홀/멀티탭 등 보이면 정리/삭제.
[9] 소품 재배치: 상판 위 책과 소품의 톤/양은 유지하되, 우측 상부 공간은 독립형 책장 제거로 생기는 빈 공간을 깨끗한 배경으로 정리. 붉은 포인트(빨간 수납함)는 하부 책장에 유지.
KEEP: 카메라 각도/원근, 밝은 화이트 톤 배경과 조명, 의자(프레임/색감), 상판 위 책/소품의 전반적 배치 감, 바닥 비노출.

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

TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png

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
왼쪽에는 세로 막대 그래프가 위치하며, 그래프는 두 개의 수직 블록(E1, E0)으로 구성되어 있다. E1 블록은 위쪽에, E0 블록은 아래쪽에 배치되어 있다. 그래프 오른쪽에는 두 장의 시험성적서 문서 이미지가 겹쳐서 오른쪽 상단에 위치한다. 그래프의 세로축에는 1.5 이하, 0.5 이하의 수치가 표시되어 있다. 그래프 하단에는 폼알데하이드 방출량(MG/L)이라는 텍스트가 있다. 전체적으로 좌측 그래프, 우측 문서로 2분할된 레이아웃이다.

Elements:
  - bar_chart @ left half: E1 법적기준(상단), E0 한샘기준(하단) 두 개의 수직 블록으로 구성된 그래프
  - document_image @ right half, overlapping: 시험성적서 두 장이 겹쳐진 형태로 배치
  - axis_label @ left of bar chart: 1.5 이하, 0.5 이하의 수직 수치
  - caption @ below bar chart: 폼알데하이드 방출량(MG/L) 텍스트

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — structure_chart:
[1] 막대 그래프 하단 블록의 텍스트를 제품 정보에 맞게 변경: "E0 한샘기준" → "E0 등급 자재".
[2] 그래프 하단 캡션 문구를 표기법과 제품 스펙에 맞게 변경: "폼알데하이드 방출량(MG/L)" → "포름알데히드 방출량(mg/L)".
[3] 우측 겹친 시험성적서 이미지를 사용자 레퍼런스로 교체: reference `screenshot_03.png`를 전면 문서로 사용하고, 후면 문서는 동일 이미지를 크기만 키워(약 105%) 흐림/밝기 약간 조정하여 겹친 느낌 유지. 상단 중앙의 "시험성적서" 제목 형태와 위치는 원본과 동일하게 유지.
[4] 좌측 세로축 표기(1.5 이하 / 0.5 이하), 상단 블록의 "E1 법적 기준" 텍스트, 블록의 상대 높이/색조/그라데이션 및 점선 가이드 라인은 유지. 단, 브랜드 언급("한샘")은 전부 제거.
KEEP: 좌측 그래프-우측 문서 2분할 레이아웃, 막대 그래프 비례/스타일, 폰트 톤&가독성, 문서 겹침 각도와 그림자.

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

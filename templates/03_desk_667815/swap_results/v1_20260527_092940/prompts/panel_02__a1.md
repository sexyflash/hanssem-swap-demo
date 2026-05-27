TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_03.png
  IMAGE 4 = USER PRODUCT — screenshot_10.png

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



=== [★ LINEUP panel 특화] ===
  - 사용자 제품 모델 옵션 수 = lineup 칸 수 (한샘 4모듈이라도 사용자 2모듈이면 2칸)
  - 각 칸 라벨 = 정확한 제품명 + 사이즈. layout grid 일관성 유지
  - 사용자 제품의 라인업이 한샘과 다르면 정확히 사용자 list만 표시


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
상단 좌측에 '라인업'과 '단위 : cm' 텍스트가 위치. 그 아래 2x2 그리드 형태로 네 개의 책상 제품 이미지가 배치됨. 각 제품 이미지는 중앙에 위치하며, 이미지 하단에는 제품명과 사이즈 정보가 각각 두 줄로 정렬됨. 좌상단부터 시계방향으로 120cm, 140cm, ㄱ자 160cm, 160cm 책상 순서. 각 제품 간 간격이 균일하며, 전체적으로 여백이 넓고 정돈된 배열.

Elements:
  - title @ top left: '라인업' 텍스트
  - unit_info @ below title: '단위 : cm' 텍스트
  - product_image @ top left grid: 120cm 일반책상 이미지
  - product_image @ top right grid: 140cm 일반책상 이미지
  - product_image @ bottom left grid: 160cm 일반책상 이미지
  - product_image @ bottom right grid: 160cm ㄱ자책상 이미지
  - product_label @ below each product image: 각 제품명 및 사이즈 정보

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — module_lineup:
[1] 상단 텍스트 유지: '라인업', '단위 : cm'.
[2] 라인업 2x2 그리드를 단일 1종(1x1)으로 축소. 좌상/우상/좌하 타일은 완전 삭제하고, 남는 1개 타일을 그리드 영역 중앙에 정렬.
[3] 남는 타일의 제품 이미지를 사용자 제품 이미지(ㄱ자형 + 하부책장 결합, 160cm)로 교체. 참고 소스: screenshot_03.png, screenshot_10.png. 카메라 각도/배경/광원은 원본과 동일한 무광 화이트 배경, 은은한 바닥 그림자 수준 유지.
[4] 제품 라벨 1행(제품명): '티오 ㄱ자책상 160cm' → '한샘 티오 ㄱ자책상 160cm'로 치환.
[5] 제품 라벨 2행(사이즈): 기존 3치수 표기(예: '163 X 74 X 115') 삭제하고, 제공 정보에 맞춰 '길이 160'만 표기. 상단에 '단위 : cm'가 있으므로 'cm' 표기는 생략해도 됨.
[6] 삭제되는 3개 타일(120/140/160 일반책상)의 제품명 및 사이즈 텍스트는 모두 제거.
[7] 이미지 디테일: ㄱ자 상판과 하부 책장형 수납부가 만난 형태가 한눈에 보이도록 각도와 배치를 조정. 상판 모서리는 라운드 처리 느낌이 보이도록 하되 과도한 클로즈업은 지양. 다리/프레임과 상판은 통일감 있는 마감 톤으로 표현.
KEEP: 타이포 스타일(폰트 굵기/자간/행간), 각 타일 하단 2줄 라벨 구성(1행 제품명, 2행 길이), 넓은 여백과 균일한 간격, 뉴트럴 조명/배경 톤.

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

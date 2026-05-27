=== [RETRY ANALYSIS · stage 1] ===
diagnosis: 상단 외부 사이즈는 정확했지만, 높이 라인업(194/216) 표기를 어디에, 어떤 문구로 넣어야 하는지 명확한 위치/문구 지시가 없어 생략되었습니다. 또한 '불필요한 신설 라벨 금지' 규칙이 모호하게 해석되어 보조 캡션 추가 자체를 회피한 것으로 보입니다.
patches:
  - 상단 제목 블록 내부에 높이 라인업을 보조 캡션으로 반드시 추가하도록 문구·위치·스타일을 명시: '높이 라인업: 194cm / 216cm (본 상품 216cm)'.
  - 보조 캡션은 '외부 사이즈' 제목 바로 하단, 단위 안내와 동일한 스타일의 소형 서브텍스트로 1줄 배치하도록 지시해 레이아웃 보존을 보장.
  - '신설 라벨 금지' 예외를 명문화: 본 보조 캡션 1건만 예외적으로 허용, 그 외 추가 텍스트/아이콘은 금지.
  - 외부 치수선과 수치(W160/D57/H216) 및 '120' 제거 지시를 유지하되, 194 숫자는 보조 캡션에만 등장하도록 제한.
  - 도어 매립형 손잡이와 3단 서랍, 행거봉 등 사용자 제품 핵심 요소는 USER PRODUCT refs(screenshot_05/06/07) 형태를 반영하도록 앵커 문구 추가.

=== [★ PRODUCT IDENTITY · 절대 왜곡되면 안 됨] ===
(이 항목들은 QA가 binary 검증. 1개라도 fail이면 retry.)

  ◆ [DISTORTION] 사이즈 차트에 W160 x D57 x H216 cm가 정확히 표기됨. (axis=size)
     → 정답: W160 x D57 x H216 cm

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 높이 라인업이 194cm/216cm 두 가지로 표기됨(본 상품 216cm 표시). (axis=size)

TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_06.png
  IMAGE 4 = USER PRODUCT — screenshot_05.png
  IMAGE 5 = USER PRODUCT — screenshot_07.png

이번 panel에 필요한 user-product reference만 첨부됨. 외부 정보 가져오지 마세요.

TARGET: 샘베딩 클로즈 옷장세트 160cm(높이216cm) 서랍형 6종
제원: 160×57×216cm
모델 옵션: 서랍형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 행거형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 거울-행거형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 거울-서랍형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm
컬러: "화이트 하이글로시(유광)", "크림화이트", "라이트오크"
· overall_silhouette: 폭 160cm, 높이 216cm의 직선형 옷장 세트로 상단까지 곧게 뻗은 외관
· doors_detail: 양문형 도어, 도어/손잡이 소재 톤 차이(크림화이트 도어도 동일 손잡이)
· handles_detail: 도어를 따라 길게 내려오는 매립형 손잡이, 양방향 그립, 목분 소재 내구성
· hinges_detail: 댐핑 힌지로 소음 감소, 40,000회 이상 개폐 테스트 하드웨어
· drawers_detail: 3단 외부형 서랍 구조
· shelves_detail: 18mm 선반, 깊이 57cm로 대용량 수납 가능
· hanging_rod_detail: 알루미늄 옷걸이봉/브라켓, 최대 16kg(너비 80cm 기준)
· back_panel_reinforcement: 뒷면 3개 보조목 보강
· materials_finish: 도어 LPM, 내부 자재 E0 등급
· modularity_expansion: 행거/서랍/선반/거울 모듈 조합 가능
· height_options: 194cm / 216cm 두 가지 높이(본 상품 216cm)
· safety_load_tests: 약 50kg/168시간 휨 강도 테스트(권장 하중 80cm 기준 최대 20kg)

[NEVER-MISS — HEIGHT LINEUP CAPTION]
- 상단 제목 블록에 아래 보조 캡션을 1줄 추가하여 반드시 표기:
  "높이 라인업: 194cm / 216cm (본 상품 216cm)"
- 위치: '외부 사이즈' 제목 바로 하단, 단위 안내 텍스트와 같은 스타일의 소형 서브텍스트(원본 자간/행간/정렬 유지). 레이아웃을 해치지 않도록 상단 제목 영역 내부에서만 배치.
- 제한: 숫자 194는 본 보조 캡션에만 사용. 외곽 치수선/본문 수치에는 216만 사용.

=== [★ PRODUCT IDENTITY · 절대 왜곡 금지] ===
  ◆ [DISTORTION] 사이즈 차트에 W160 x D57 x H216 cm가 정확히 표기됨. (axis=size)
     → 정답: W160 x D57 x H216 cm

=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 single-panel layout. multi-cell grid 절대 X.
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
상단 중앙에 외부 사이즈 제목과 단위 안내 텍스트가 위치. 중앙에는 정면과 약간 측면에서 본 옷장 일러스트가 크고, 각 변에 치수(120, 194, 80, 62cm)가 선과 함께 표시됨. 하단에는 내부 사이즈 제목이 좌측에 있고, 좌측 하단에는 서랍 내부를 사선에서 본 이미지와 치수(71.5, 42, 14cm)가 선과 함께 표시됨. 우측 하단에는 옷장 내부를 정면에서 본 이미지와 치수(116.5, 21, 23, 23cm)가 세로로 표시됨. 하단 중앙에는 내부 깊이(57.5cm)와 주의 문구가 텍스트로 배치됨.

Elements:
  - title @ top left: 외부 사이즈, 단위 안내 텍스트(+ 보조 캡션: 높이 라인업 194/216)
  - product_illustration @ center upper: 옷장 외관 일러스트, 치수선 및 수치 표시
  - section_title @ left middle: 내부 사이즈 텍스트
  - drawer_diagram @ bottom left: 서랍 내부 단면
  - interior_diagram @ bottom right: 옷장 내부 정면
  - depth_info @ bottom center: 내부 깊이 정보 텍스트
  - note @ bottom: 조립/설치 오차 안내 문구

=== [EDIT INSTRUCTIONS — size_chart] ===
[0] 상단 보조 캡션(높이 라인업) 추가
- 문구: "높이 라인업: 194cm / 216cm (본 상품 216cm)"
- 배치: '외부 사이즈' 제목 바로 아래, 단위 안내와 동일 계열의 소형 서브텍스트로 1줄. 상단 제목 영역 내부에만 배치, 원본 자간/행간/정렬 유지.

[1] 상단 '외부 사이즈' 영역 업데이트
- '단위 : cm'는 유지.
- 외곽 수치 교체: 가로 80 → 160, 깊이 62 → 57, 높이 194 → 216.
- 불명확 외부 치수 '120' 표기와 해당 치수선은 완전 제거.
- 표기 형식은 원본 스타일 유지. 외곽 차트 표기에는 194 숫자 사용 금지(보조 캡션에서만 허용).

[2] 중앙 외관 일러스트 교체(사용자 제품 실루엣 반영)
- 폭 160 x 높이 216 x 깊이 57 비율로 재스케일.
- 상부 양문형 도어 + 하부 3단 외부형 서랍 구조 유지.
- 도어 전면 매립형 손잡이를 선명하게 표현(도어와 미묘한 톤 차이). 앵커: USER PRODUCT refs(screenshot_05/06/07)의 손잡이 길이/매립 방향 느낌을 그대로 반영.
- 전체 마감은 뉴트럴 라이트 톤(컬러명 텍스트 표기 없음).
- 외곽 치수선/화살표는 기존 스타일로 재배치.

[3] 하단 좌측 '서랍 내부' 다이어그램 정리
- 3단 외부형 서랍 중 1칸 오픈된 사선 시점 유지.
- 내부 수치(71.5, 42, 14)와 해당 치수선 모두 삭제.

[4] 하단 우측 '옷장 내부' 정면 다이어그램 정리
- 상단 행잉 공간에 알루미늄 옷걸이봉/브라켓을 심플하게 추가(텍스트 표기 없이 시각 요소만). 앵커: USER PRODUCT refs의 행거봉 위치/굵기 비례 감각 참고.
- 하부 3단 서랍 전면은 유지.
- 기존 내부 수치(116.5, 21, 23, 23)와 해당 치수선은 모두 삭제.

[5] 하단 중앙 텍스트
- '내부 깊이 : 57.5' → '내부 깊이 : 57'로 교체.
- 하단 주의 문구 '* 조립/설치에 따라 오차가 발생할 수 있습니다.'는 그대로 유지.

[6] 공통 타이포/레이아웃
- 폰트, 자간, 라인 두께, 화살표 스타일, 여백 및 레이아웃 그리드를 원본과 동일하게 유지.
- 보조 캡션(높이 라인업) 1건 외 신규 라벨/아이콘/브랜드/컬러 텍스트 추가 금지.

=== [ABSOLUTE RULES — PRESERVE / NEVER] ===
PRESERVE:
  - panel C와 같은 single panel layout, 한국 detail page 스타일
  - 카메라 각도/배경/조명/한국어 텍스트 가독성
  - 사용자 제품 feature_descriptions에 명시된 핵심 특징(매립형 손잡이, 3단 외부 서랍, 행거봉 등) 시각적 반영
  - [DISTORTION] W160 x D57 x H216 cm 외부 사이즈 표기, [NEVER-MISS] 높이 라인업 보조 캡션
NEVER:
  - 사용자 제품 정보에 없는 feature 발명 (헤드레스트/리클라이너/USB/추가 다리/tufting 등)
  - 한샘 원본 텍스트 잔존
  - multi-cell grid 출력
  - 한글 텍스트 깨짐
  - 외곽 차트에 194 숫자 표기(보조 캡션 제외)


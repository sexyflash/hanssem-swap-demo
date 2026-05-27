TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_06.png
  IMAGE 4 = USER PRODUCT — screenshot_07.png
  IMAGE 5 = USER PRODUCT — screenshot_10.png

이번 panel에 필요한 user-product reference만 첨부됨. 외부 정보 가져오지 마세요.

TARGET: 샘베딩 클로즈 옷장세트 160cm(높이216cm) 서랍형 6종
제원: 160×57×216cm
모델 옵션: 서랍형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 행거형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 거울-행거형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm, 거울-서랍형 6종 (160cm, 높이 216cm) W160 x D57 x H216 cm
컬러: "화이트 하이글로시(유광)", "크림화이트", "라이트오크"
· overall_silhouette: 폭 160cm, 높이 216cm의 직선형 옷장 세트로 상단까지 곧게 뻗은 외관이 공간을 깔끔하고 크게 보이게 합니다.
· doors_detail: 편리한 양문형 도어 구성. 도어와 손잡이는 서로 다른 소재라 컬러 차이가 있으며, 크림화이트 도어는 화이트 도어와 동일 손잡이가 적용됩니다.
· handles_detail: 도어를 따라 길게 내려오는 매립형 손잡이로 양방향 그립이 가능해 어느 방향에서도 쉽게 개폐. 손잡이는 견고한 목분 소재로 내구성을 높였습니다.
· hinges_detail: 도어에는 댐핑 힌지 적용으로 소리 없이 부드럽게 닫힘. 최소 40,000회 개폐 테스트를 통과한 하드웨어를 사용합니다.
· drawers_detail: 서랍형은 3단 외부형 서랍 구조로 속옷, 티셔츠, 니트·바지 등 자주 사용하는 의류를 별도 서랍장 없이 수납 가능.
· shelves_detail: 18mm 두께의 선반을 사용하여 처짐을 줄였으며, 깊이 57cm 선반으로 이불·수납함 등 부피 큰 물건도 보관 가능.
· hanging_rod_detail: 알루미늄 옷걸이봉과 브라켓 설계로 최대 16kg까지 지지(너비 80cm 기준). 미디움 원피스·자켓도 끌림 없이 보관 가능.
· back_panel_reinforcement: 옷장 뒷면을 3개의 보조목으로 보강해 흔들림과 기울어짐을 억제, 도어 개폐와 서랍 작동 안정성 향상.
· materials_finish: 도어 마감은 접착제를 쓰지 않는 LPM 공법을 적용. 내부 목재·접착제·부속 자재까지 E0 등급 소재 사용.
· modularity_expansion: 행거형, 서랍형, 선반형, 거울형 등 모듈을 조합하여 라이프스타일에 맞는 드레스룸 구성 가능.
· height_options: 샘베딩 옷장은 194cm와 216cm 두 가지 높이 라인업을 운영(본 상품은 216cm).
· mirror_module_option: 거울형 모듈을 선택하면 전신거울을 별도로 두지 않아도 되어 좁은 공간 활용에 유리.
· safety_load_tests: 자재는 약 50kg/168시간 휨 강도 테스트 통과(시험 기준). 일반 사용 권장 하중은 너비 80cm 기준 최대 20kg.

=== [★ PRODUCT IDENTITY · 절대 왜곡되면 안 됨] ===
(이 항목들은 QA가 binary 검증. 1개라도 fail이면 retry.)

  ◆ [DISTORTION] 폭 160cm 구성은 80cm 모듈 2개 조합으로 보이는가(중앙 이음부가 보이는 2칸 구조). (axis=frame)
     → 정답: 80cm 모듈 2개 조합으로 보임

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 댐핑 힌지(부드럽게 닫힘) 관련 아이콘/문구/접사 표기가 있음. (axis=hinges)
     · 선반 두께 18mm 표기 또는 단면 설명이 보임. (axis=shelves)
     · 알루미늄 옷걸이봉 사용이 보이거나 텍스트로 명시됨. (axis=hanging_rod)
     · 뒷판 3개의 보조목 보강 구조가 다이어그램/설명으로 제시됨. (axis=back_panel)
     · 도어 마감 ‘LPM’ 공법이 텍스트/아이콘으로 표시됨. (axis=finish)
     · E0 등급 소재 사용이 아이콘/문구로 표시됨. (axis=finish)
     · 도어 힌지 40,000회 개폐 테스트 통과 표기가 있음. (axis=hinges)
     · 자재 휨 강도 50kg/168시간 테스트 통과 표기. (axis=frame)


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
좌측에는 두 개의 문이 있는 직사각형 가구가 약간 비스듬히 겹쳐진 형태로 배치되어 있다. 문 중앙에는 손잡이 두 개가 수직으로 위치한다. 문 외곽에는 점선 사각형이 겹쳐져 있다. 우측에는 세 개의 수평 구획이 있는 직사각형 가구가 정면을 향해 있다. 상단 구획 위에는 아래 방향의 굵은 화살표가 있고, 그 아래에는 점선 곡선이 좌우로 이어진다. 각 구획 중앙에는 손잡이 모양의 짧은 수평선이 있다. 두 도형은 좌우로 나란히 배치되어 있으며, 배경은 흰색이다.

Elements:
  - left_cabinet @ 좌측 중앙: 두 개의 문이 있는 직사각형 가구, 문이 약간 비스듬히 겹침
  - left_handles @ 좌측 중앙, 각 문 중앙: 수직 손잡이 두 개
  - left_dotted_box @ 좌측, 가구 외곽: 점선 사각형
  - right_drawer_unit @ 우측 중앙: 세 개의 수평 구획이 있는 직사각형 가구
  - right_arrow @ 우측 상단 구획 위: 굵은 아래 방향 화살표
  - right_dotted_curve @ 우측 상단 구획 아래: 점선 곡선
  - right_handles @ 우측 각 구획 중앙: 짧은 수평 손잡이 세 개

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — structure_chart:
[1] 좌측 양문 도어(left_cabinet) 업데이트:
  - 도어 외곽 라운드 모서리를 완만하게 줄여 직선형 실루엣을 강조(제품 직선형 외관 반영).
  - 손잡이(left_handles)는 "매립형 손잡이"로 교체: 각 도어의 맞닿는 내측 엣지를 따라 세로로 길게(도어 높이의 약 70~80%) 배치하고, 끝단은 라운드 처리된 슬릿 형태. 얕은 음영/내부 선으로 매립(리세스) 느낌 표현. 색상은 본문 모노톤 유지하되 손잡이 톤을 한 단계 진하게.
  - 양문 구성(편리한 양문형 도어) 유지. 도어와 손잡이 소재 차이로 색 대비가 난다는 점은 모노톤 대비(손잡이 진톤)로만 표현.
  - 도어 개폐 방향 힌트는 현 패널의 비스듬히 겹쳐진 연출을 유지해 자연스럽게 표현.
[2] 좌측 점선 사각형(left_dotted_box) 유지:
  - 프레임/보강 영역을 암시하는 현재 점선 박스 위치와 크기는 유지. 별도 텍스트 라벨 추가 없음.
[3] 우측 서랍 유닛(right_drawer_unit) 정합:
  - 3단 외부형 서랍 구조를 명확히: 서랍을 3등분하고 분할선 두께를 균일하게 정리.
  - 각 서랍 중앙의 손잡이(right_handles)는 얕은 매립형 노치 느낌의 짧은 수평 슬롯으로 단순화(제품 정보에 별도 서랍 손잡이 사양 표기 없음 → 중립적 표현 유지).
[4] 우측 상단 화살표(right_arrow)와 점선 곡선(right_dotted_curve) 조정:
  - 화살표 크기·굵기 유지. 점선 곡선의 처짐 정도를 약간 완만하게 수정해 ‘처짐 억제’ 뉘앙스를 주되 위치는 현행과 동일(상단 구획 하단 라인 부근).
  - 추가 텍스트/아이콘은 넣지 않음.
[5] 전반 스타일:
  - 전체를 단색(블랙 라인/화이트 바탕) 아이소메트릭·정면 혼합의 기존 스타일로 유지. 제품 색상 옵션 텍스트나 칼라칩은 본 패널에는 추가하지 않음.
[6] 모델/사양 반영 범위:
  - 본 패널은 구조 개념도이므로 치수(160×57×216cm) 숫자 표기는 삽입하지 않음. 시각적 요소만 ‘서랍형 6종(160cm, 높이 216cm)’ 구성을 암시(양문 + 3단 서랍)하도록 정합.
[7] 레퍼런스 반영:
  - 도어 매립형 손잡이의 길이 비율·형상은 screenshot_06.png, screenshot_07.png, screenshot_10.png를 참고해 동일 비율로 구현.

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

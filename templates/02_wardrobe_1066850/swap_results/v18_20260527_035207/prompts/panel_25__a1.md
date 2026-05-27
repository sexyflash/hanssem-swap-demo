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
  ◆ [DISTORTION] 도어는 양문형 힌지(여닫이) 도어로 구성되고 슬라이딩이 아님. (axis=doors)
     → 정답: 여닫이(힌지) 도어
  ◆ [DISTORTION] 서랍형: 전면에 3단 외부형 서랍 블록이 명확히 보임. (axis=drawers)
     → 정답: 3단 외부형 서랍 존재
  ◆ [DISTORTION] 문을 따라 세로로 길게 내려오는 매립형 손잡이(플러시 인셋 타입). (axis=handles)
     → 정답: 세로형 매립 손잡이
  ◆ [DISTORTION] 상단까지 곧게 뻗은 직선형 실루엣(크라운/아치 등 돌출 장식 없음). (axis=frame)
     → 정답: 평평한 상단의 직선형 외관
  ◆ [DISTORTION] 제품 이미지의 도어 컬러가 제공된 3가지 중 하나로 보임. (axis=color)
     → 정답: 제공 3색 중 하나
  ✗ [FORBIDDEN] 슬라이딩(미닫이) 도어가 포함되면 안 됨. — 결과에 보이면 fail
  ✗ [FORBIDDEN] 바닥에서 본체를 높게 띄우는 노출 다리(약 10cm 이상)가 없어야 함. — 결과에 보이면 fail
  ✗ [FORBIDDEN] 전면/내부 가장자리에 LED 발광 바 등 내장 조명이 노출되면 안 됨(선택 사양 언급 없음). — 결과에 보이면 fail

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 알루미늄 옷걸이봉 사용이 보이거나 텍스트로 명시됨. (axis=hanging_rod)


=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 **single-panel layout**. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
상단에는 아이방 전체를 보여주는 사진이 배치되어 있다. 좌측에는 옷장과 서랍장이 나란히 놓여 있고, 그 옆에는 오픈형 선반이 있다. 오른쪽에는 침대와 창문, 커튼이 보인다. 하단에는 옷장 내부와 선반 내부를 클로즈업한 사진이 있다. 사진 아래에는 흰색 배경에 후기성 텍스트가 좌측 정렬로 배치되어 있다. 각 가구는 바닥에 평행하게 정렬되어 있으며, 사진들은 세로로 2단 분할되어 있다.

Elements:
  - wardrobe @ 상단 사진 좌측: 문이 닫힌 흰색 옷장
  - drawer @ 상단 사진 좌측 하단: 옷장과 연결된 서랍장
  - open_shelf @ 상단 사진 중앙: 책, 문구류, 장난감 등이 정리된 오픈 선반
  - bed @ 상단 사진 우측: 흰색 침대와 침구
  - window @ 상단 사진 우측 끝: 커튼과 블라인드가 있는 창문
  - wardrobe_interior @ 하단 사진 좌측: 옷걸이, 수납함, 옷이 정리된 옷장 내부
  - open_shelf_interior @ 하단 사진 우측: 문구류, 장난감, 보드게임 등이 정리된 선반 내부

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — lifestyle_scene:
[1] 상단 메인 사진(아이방 전경)
- 좌측 가구열을 사용자 제품 "샘베딩 클로즈 옷장세트 160cm(높이216cm) 서랍형 6종"으로 통일.
  · 폭 160cm로 보이도록 모듈 2열 구성으로 재배치: 좌측은 양문형 도어 모듈, 우측은 상부 도어 + 하부 3단 외부 서랍 모듈.
  · 도어에 세로로 길게 내려오는 매립형 손잡이 추가(도어 색상과 미세한 컬러 차이 표현, 소재 차이 느낌). 손잡이 위치는 도어 전면 모서리 라인에 좌/우 각각 1개씩.
  · 전체 높이를 216cm로 상향(천장과의 여백이 적게 보이도록 상단을 연장).
  · 기존 오픈형 선반은 제거하고 동일 높이의 도어 모듈로 치환하여 일체형 옷장 세트로 보이게 함.
  · 좌측 하부 3단 서랍은 외부형(전면에 노출)으로 보이도록 면 분할을 3등분, 매끈한 평면 전면과 얇은 수평 그랩 라인 유지.
  · 색감은 따뜻한 화이트 톤 유지(컬러명 표기/그래픽 라벨 삽입 금지).
  · 카메라 각도·바닥 평행 정렬·조명 톤(자연광+실내등) 유지. 침대/창문/커튼은 그대로 보존.

[2] 하단 좌측 클로즈업(wardrobe_interior)
- 내부 구성을 사용자 제품 스펙에 맞게 수정.
  · 상단 알루미늄 옷걸이봉 + 브라켓 노출(80cm 폭 모듈 느낌). 옷 몇 벌은 유지하되 간섭 없는 배열.
  · 선반은 18mm 두께로 보이게 에지 두께 강조.
  · 기존 내부 서랍(도어 뒤 2단)은 제거하고, 선반+수납함 배치로 대체(속옷/소품 투명 박스 등 간단 소품만).
  · 도어 가장자리에는 댐핑 힌지 금속 하드웨어가 보이도록 일부 각도 조정 또는 문 10~15도 개방 상태 표현.

[3] 하단 우측 클로즈업(open_shelf_interior → 외부 서랍 클로즈업으로 대체)
- 오픈 선반 내부 컷을 삭제하고, 동일 위치/프레임에 "외부형 3단 서랍" 부분 클로즈업으로 교체.
  · 상단/중단 서랍을 1/3 정도 열어 속옷·티셔츠가 정리된 모습 연출(정돈된 폴딩). 하단 서랍은 닫힘.
  · 서랍 내부 깊이는 57cm의 여유감이 느껴지도록 사이드 레일과 그림자 깊이 표현.
  · 전면은 매끈한 평면, 손잡이 노출 없이 심플하게.

[4] 하단 텍스트 영역 치환
- 헤더 라인과 후기성 본문을 사용자 제품 정보 기반 문구로 교체(한글, 좌측 정렬, 줄바꿈 구조 유지). 상세 문구는 text_substitutions 참조.

KEEP: 2단 세로 분할 레이아웃, 흰색 여백과 좌측 정렬 타이포, 방 전경의 침대·창문·커튼·러그·바닥 톤, 카메라 구도/원근감, 생활감 소품은 옷장 주변만 최소 편집.

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

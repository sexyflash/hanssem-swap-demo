TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_05.png
  IMAGE 4 = USER PRODUCT — screenshot_07.png
  IMAGE 5 = USER PRODUCT — screenshot_06.png

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
이미지는 좌우 2분할로 구성되어 있다. 왼쪽에는 사람이 서랍을 열고 정리함을 넣는 장면이 상반신까지 보이며, 서랍 내부에는 여러 개의 수납 칸이 보인다. 오른쪽에는 벽에 붙은 서랍장이 아래쪽에서 위로 2단 열려 있고, 각각의 서랍 안에 옷이 가지런히 정리되어 있다. 오른쪽 하단에는 신발과 러그가 일부 보인다. 좌측은 따뜻한 우드톤 바닥, 우측은 연한 민트색 벽과 밝은 바닥이 배경이다. 두 장면 모두 서랍 내부가 강조되어 있다.

Elements:
  - person @ left, middle: 서랍을 열고 정리함을 넣는 사람의 상반신
  - drawer @ left, center: 열린 서랍과 내부 정리함
  - drawer @ right, center: 두 개의 열린 서랍과 내부에 정돈된 옷
  - shoes @ right, bottom right: 파란색 운동화 한 켤레
  - rug @ right, bottom: 러그와 바닥

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — lifestyle_scene:
[1] 컬러/마감 치환
- 좌·우 장면의 모든 도어와 서랍 전면을 사용자 컬러 "크림화이트"로 통일. 유광 효과 없이 차분한 미색 톤 유지.
- 캐비닛 측판, 보이는 문선·몰딩도 동일 컬러로 정리해 이색(그레이/우드톤) 잔존 제거.

[2] 도어/손잡이 형태 정합
- 좌측 장면: 거울처럼 보이는 세로 판을 제거하고, 양문형 도어 2짝으로 교체. 각 도어의 맞물리는 안쪽 모서리를 따라 위→아래로 내려오는 매립형 손잡이 홈(세로 그루브)을 형상화.
- 손잡이 색상/재질 강조는 지양하고, 그루브 음영으로만 식별되게 표현(사용자 스펙: 도어를 따라 길게 내려오는 매립형 손잡이).

[3] 서랍 구조를 '3단 외부형'으로 통일
- 좌측 장면: 현재 열린 서랍을 3단 중 1칸으로 보이게 하고, 같은 폭/높이의 서랍 전면이 위·아래로 총 2칸 더 존재하도록 분할선과 면 정렬 추가(닫힘 상태). 내부 정리함과 수건 연출은 유지.
- 우측 장면: 현재 2단 오픈 상태를 3단 외부형으로 수정. 상·중단 오픈 유지, 하단 서랍 전면 1칸을 추가(닫힘). 각 서랍 내부에는 접힌 속옷/티셔츠/니트가 가지런히 배치되도록 유지.

[4] 일체감/비례 보정
- 두 장면 모두 서랍들이 독립형 서랍장이 아닌 옷장 하부에 일체형으로 보이도록 좌우 측판과 플러시 정렬을 맞춤.
- 프레임 상단으로 캐비닛이 이어지는 느낌을 남겨 높이 216cm의 직선형 실루엣을 암시(수치 표기 금지).

[5] 레퍼런스 정합
- screenshot_05.png, screenshot_06.png, screenshot_07.png를 참고해 "크림화이트" 톤과 매립형 손잡이 세로 그루브 폭/깊이/모서리 라운딩을 일관되게 적용.

KEEP:
- 좌우 2분할 레이아웃, 카메라 각도/조명, 좌측 우드톤 바닥과 인물의 동작(정리함을 넣는 순간), 우측 민트색 벽·밝은 바닥·러그·운동화 연출 유지.
- 서랍 내부가 강조되는 구성과 의류가 정돈된 상태 유지.
- 텍스트/아이콘/로고 비노출 상태 유지.

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

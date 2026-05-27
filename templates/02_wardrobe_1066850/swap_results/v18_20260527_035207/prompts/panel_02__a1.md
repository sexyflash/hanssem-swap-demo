TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_06.png
  IMAGE 4 = USER PRODUCT — screenshot_10.png
  IMAGE 5 = USER PRODUCT — screenshot_04.png
  IMAGE 6 = USER PRODUCT — screenshot_07.png

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
상단 이미지는 방 한 켠에 배치된 흰색 수납장과 책상, 주변 소품들이 포함되어 있다. 수납장은 중앙에 위치하며, 왼쪽에는 책상과 컴퓨터, 오른쪽에는 벽과 기타 소품이 있다. 하단 이미지는 흰색 수납장의 상단부를 클로즈업하여 보여준다. 두 이미지는 수직으로 분할되어 상단은 전체 공간, 하단은 제품 디테일을 강조한다. 상단 이미지의 배경에는 벽걸이 포스터와 기타가 보인다. 바닥에는 체크무늬 러그가 깔려 있다.

Elements:
  - main_product @ 상단 중앙, 하단 전체: 흰색 모듈형 수납장
  - desk @ 상단 좌측: 흰색 책상과 컴퓨터
  - decor @ 상단 우측: 벽걸이 포스터, 기타, 책, 소품
  - rug @ 상단 하단부: 체크무늬 러그
  - close_up @ 하단 전체: 수납장 상단부 디테일

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — lifestyle_scene:
[1] 메인 제품 교체: 상단 중앙/하단 전체의 흰색 모듈형 수납장을 사용자 제품 ‘샘베딩 클로즈 옷장세트 160cm(높이216cm) 서랍형 6종’으로 교체.
[2] 전면 구성: 폭 160cm의 2열 일체형으로 정리. 양문 도어 2짝 유지하되, 좌측 하단에 3단 외부형 서랍을 배치하고(좌측 상부는 도어), 우측은 전고(상하 풀높이) 도어로 단정하게 구성.
[3] 비가시 모듈 삭제: 원본 우측의 오픈 선반/소형 서랍/슬림 도어 등 복잡한 모듈을 모두 제거하여 매끈한 직선형 옷장 전면으로 통일.
[4] 사이즈 반영: 전체 높이 216cm로 스케일 업. 프레임 상단 가까이까지 올라오도록 비율 조정(천장과 여백 소폭). 깊이감은 D57cm로 보이는 범위 내 자연 스케일 유지. 폭은 160cm로 책상과의 간격이 과도하게 변형되지 않도록 좌우 여백만 미세 조정.
[5] 도어/손잡이 디테일: 도어는 평판(무몰딩)이며, 두 도어의 맞닿는 안쪽 엣지에 상단부터 하단까지 이어지는 길고 얇은 매립형 손잡이 채널을 적용(양방향 그립 가능하게 프로파일 표현). 손잡이 채널 색은 도어보다 1~2단 어둡거나 미세하게 다른 톤의 솔리드 컬러로 대비(목분 소지감, 우드무늬 비노출).
[6] 서랍 디테일: 하단 3단 외부형 서랍은 동일 도어 마감으로 평판 처리, 전면 손잡이 노출 없음(상단 이격 또는 숨은 그립으로 개폐되는 느낌). 서랍 폭은 좌측 모듈 폭(약 80cm)에 맞춤.
[7] 컬러/마감: 도어 및 서랍 전면은 "크림화이트"로 렌더(차분한 미색 톤, LPM의 무광~세미매트 질감). 바디/측판/상판도 동일 톤 유지. 유광 하이라이트 과다 표현 금지.
[8] 하드웨어 간극: 도어/서랍 사이는 2~3mm 균일한 갭. 힌지/댐퍼 등 하드웨어는 비노출(닫힌 상태).
[9] 하단 클로즈업(패널 하부 이미지): 상단 모서리와 두 도어가 만나는 중앙부, 매립형 손잡이 채널의 단면/그림자가 또렷하게 보이도록 재렌더. 상판 라인은 곧고 날렵하게.
[10] 배경/소품 정리: 책상, 컴퓨터, 포스터, 기타, 러그 등 주변 소품과 조명/그림자 톤은 동일 유지. 제품 높이 상승으로 생기는 벽면 가려짐은 자연스럽게 처리(배경 재배치 없이 오클루전만).
[11] 텍스트 비노출 유지: 본 패널에는 제품명/치수 표기 등의 텍스트 오버레이를 새로 추가하지 않음.
[12] 참고 리소스: 매립 손잡이 비율/홈 깊이/톤은 제공된 reference keys(screenshot_06.png, screenshot_10.png, screenshot_04.png, screenshot_07.png)를 우선 참조해 일관되게 적용.

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

TASK: PAINT EDIT — partial in-painting on the provided base image.

이번 호출은 base 이미지의 잘된 부분을 모두 보존하고, 지정된 영역만 부분 수정한다.
재생성 X.

IMAGE 1 = BASE (앞선 시도 중 점수가 가장 좋은 결과 — preserve wholesale except listed regions)
이후 IMAGE 2~ = user-product reference (필요 부분 보정용)

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

=== [SPATIAL LAYOUT — KEEP from BASE] ===
상단과 하단 두 개의 장면이 수평으로 분할되어 있다. 두 장면 모두 왼쪽에는 창문과 블라인드, 책상, 의자가 배치되어 있고, 책상 위에는 컴퓨터와 스탠드, 책, 소품이 놓여 있다. 책상 오른쪽에는 큰 옷장/수납장이 배치되어 있으며, 상단 장면에서는 옷장에 서랍과 오픈 선반이 포함되어 있다. 하단 장면에서는 옷장이 전부 닫혀 있고, 전면이 평평하다. 오른쪽 벽에는 'BETTER THAN CHEESE' 포스터와 벽등이 있다. 바닥에는 체크무늬 러그가 중앙에 깔려 있고, 좌측 하단에는 파란색 바구니와 헤드폰, 우측 하단에는 기타 앰프와 책이 있다.

=== [PAINT EDIT DIRECTIVE — LLM 생성] ===
This is a PAINT EDIT — preserve base wholesale except listed regions.
Keep the base camera angle, background, lighting, floor/wall textures, scene layout, and all props 100% unchanged. Do not redraw the whole scene.

Priority fix repeated failure (appeared in both attempts):
- Absolutely NO grid/tiling/multi-image layout. Output must be a single cohesive photo. Remove any grid or split-frame borders and inpaint continuous wall/floor with matching color, texture, shadows, and reflections.

Targeted wardrobe corrections only:
1) Two-module clarity (W160 composed of two 80 cm modules): Make the wardrobe read as exactly two side-by-side 80 cm modules (total width 160 cm). Show a subtle carcass seam at the 80 cm centerline. Remove or downplay any extra vertical partition that suggests a third narrow bay. Keep top/bottom alignment and perspective as in the base.
2) Hinged double doors per module: Ensure each 80 cm module has a clear pair of hinged double doors. On the RIGHT module, above the three external drawers, replace any single/narrow door with a symmetric pair of doors that meet at that module’s centerline. Keep even, narrow reveals and soft-close hinge cues consistent with the left module.
3) Handle correction (strong emphasis): Replace all short or protruding bar handles on the doors with long, full-height, flush/inset vertical handles routed into the door skin, positioned near each door’s opening edge. Handles must be flush (no protrusion) and run almost the full height for easy two-direction grip. Apply the same handle type and proportions to the right module’s upper door pair. Maintain the existing subtle color/material contrast between doors and handles; do not change door color or gloss.

Preserve finishes and proportions:
- Do not change door colorway or gloss level; keep reflections and lighting continuity.
- Keep the right module’s three external drawers as-is in count and placement; only adjust adjacent door/handle details as above.
- Maintain overall perceived dimensions (W160 x D57 x H216) and perspective.

Do not move the camera, objects, or lighting. Edit only the specified regions; everything else remains identical to the base.

=== [ABSOLUTE RULES] ===
- 카메라 각도/배경/조명/레이아웃은 BASE 그대로
- 한국어 텍스트는 정확/또렷
- 새 요소 발명 금지 (사용자 제품 정보 외)
- 단일 panel 출력

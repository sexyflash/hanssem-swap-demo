=== [RETRY ANALYSIS · stage 1] ===
diagnosis: 보강대 2개를 프레임 밖 요소로 처리하라는 이전 지시가 있어, 클로즈업 구도에서 보강대가 아예 노출되지 않았습니다. 또한 우측 백팩·오픈 수납 구조에 시야가 가려 보강대 존재가 시각적으로 분리·식별되지 않았습니다.
patches:
  - 보강대 2개를 최우선 요구사항으로 격상: 프레임 안에서 동시에 명확히 보이도록 지시
  - 보강대 위치를 구체화: 상판 하부 전면 수평 1개 + 우측 측판/내측 방향 수평(또는 ㄱ자) 1개가 가려지지 않게 배치
  - 렌더링 앵커 추가: user-product reference에서 보이는 보강대의 두께·색·마감·부착점 그대로 복제
  - 시각적 분리 강화: 주변 패널과 톤이 겹치지 않도록 미세 톤 대비/하이라이트/캐스트 섀도로 윤곽을 또렷하게
  - 백팩·노트 등 프롭은 위치 유지하되, 보강대가 가려지지 않게 오픈 수납 내부 시야와 조명을 조정
  - 이전의 ‘보강대 프레임 밖’ 문구 삭제, 레벨러만 비노출 유지로 명확히 정정

=== [★ PRODUCT IDENTITY · 절대 왜곡되면 안 됨] ===
(이 항목들은 QA가 binary 검증. 1개라도 fail이면 retry.)

  ◆ [DISTORTION] 하부 수납은 책장형 오픈 선반 구조로 도어/서랍이 없음 (axis=storage)
     → 정답: 오픈 선반형 수납(도어/서랍 없음)
  ◆ [DISTORTION] 상판 외곽 모서리 라운드 처리 (axis=edges)
     → 정답: 라운드 모서리
  ◆ [DISTORTION] 가방걸이 1개 기본 제공(좌/우 중 한 위치에 설치) (axis=accessory)
     → 정답: 가방걸이 1개 확인
  ◆ [DISTORTION] 흔들림 저감을 위한 보강대 2개 적용 (axis=structure)
     → 정답: 보강대 2개
  ◆ [DISTORTION] 상판은 LPM 계열의 불투명 패널형으로, 유리/석재/라이브엣지 원목이 아님 (axis=surface)
     → 정답: LPM 계열 패널 상판(유리/석재/라이브엣지 아님)

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 바닥 수평 맞춤을 위한 하부 레벨러(조절발) 노출 (axis=legs)
     · PC 본체 등 부피 물건을 위한 높은 오픈 칸 1개 이상 (axis=storage)
     · LPM 표면 특성상 무광/세미무광 수준으로 과도한 반사 없음 (axis=surface)
     · 라운드 모서리의 엣지 밴딩이 이색/들뜸 없이 매끈함 (axis=finish)

TASK: Edit this Korean detail-page panel — swap to user's product.

REFERENCE PATTERN (image_urls 순서 — panel별 LLM 매핑):
  IMAGE 1 = panel C (한샘 원본 — edit base, layout 유지)
  IMAGE 2 = SMART SHEET (panel별 가이드 메타 · 결과로 복제 X · 정보만 활용)
  IMAGE 3 = USER PRODUCT — screenshot_10.png
  IMAGE 4 = USER PRODUCT — screenshot_07.png
  IMAGE 5 = USER PRODUCT — screenshot_06.png
  IMAGE 6 = USER PRODUCT — screenshot_04.png

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

  ◆ [DISTORTION] 흔들림 저감을 위한 보강대 2개 적용 (axis=structure)
     → 정답: 보강대 2개가 프레임 안에서 동시에 식별 가능해야 함
  ◆ [DISTORTION] 하부 수납은 책장형 오픈 선반 구조로 도어/서랍이 없음 (axis=storage)
     → 정답: 오픈 선반형 수납(도어/서랍 없음)
  ◆ [DISTORTION] 상판 외곽 모서리 라운드 처리 (axis=edges)
     → 정답: 라운드 모서리
  ◆ [DISTORTION] 가방걸이 1개 기본 제공(좌/우 중 한 위치에 설치) (axis=accessory)
     → 정답: 가방걸이 1개 확인
  ◆ [DISTORTION] 상판은 LPM 계열의 불투명 패널형으로, 유리/석재/라이브엣지 원목이 아님 (axis=surface)
     → 정답: LPM 계열 패널 상판(유리/석재/라이브엣지 아님)

  (참고용 · detail — 시도하되 strict 채점 안 함):
     · 바닥 수평 맞춤을 위한 하부 레벨러(조절발) 노출
     · PC 본체 등 부피 물건을 위한 높은 오픈 칸 1개 이상
     · LPM 표면 특성상 무광/세미무광 수준으로 과도한 반사 없음
     · 라운드 모서리의 엣지 밴딩이 이색/들뜸 없이 매끈함

=== [★ DETAIL CLOSE-UP 특화] ===
  - frame 안에 들어오는 사용자 제품 디테일을 정확히 표현. 추측/발명 금지
  - reference 사진에서 보이는 시접/소재/표면 디테일 그대로
  - 보강대 2개는 user-product reference(screenshot_10.png, screenshot_07.png, screenshot_06.png, screenshot_04.png)에서 보이는 형태·두께·색·부착점을 그대로 복제. 보강대가 보이는 컷을 최우선 앵커로 삼아 결과에 반영.

=== [출력 형식 강제] ===
- 결과는 IMAGE 1 (panel C)와 동일한 single-panel layout. multi-cell grid 절대 X.
- panel C가 product shot이면 → product shot 1장
- panel C가 lifestyle이면 → lifestyle 1장
- panel C가 chart이면 → 동일 chart 1장

=== [SPATIAL LAYOUT TO PRESERVE — panel C와 동일] ===
왼쪽 하단에는 세 개의 서랍이 있는 흰색 책상 다리가 위치한다. 책상 상판은 이미지 상단에 넓게 펼쳐져 있고, 상판 위에는 노트와 펜이 오른쪽 상단에 놓여 있다. 책상 오른쪽 측면에는 흰색 원형 고리가 부착되어 있으며, 고리에 베이지색 백팩이 걸려 있다. 백팩은 이미지 오른쪽 하단을 차지한다. 책상 다리와 상판은 모두 직각으로 연결되어 있다. 전체적으로 책상과 소품들이 가까운 거리에서 클로즈업되어 있다.

Elements:
  - desk @ left and center: 흰색 책상, 세 개의 서랍과 상판 포함
  - drawer @ bottom left: 세 개의 흰색 서랍
  - peg/hook @ right center: 흰색 원형 고리, 책상 측면에 부착
  - backpack @ right bottom: 베이지색 백팩, 고리에 걸려 있음
  - notebook and pens @ top right on desk: 노트와 펜 두 자루, 책상 위에 놓임

=== [EDIT INSTRUCTIONS — LLM 생성] ===
EXPLICIT EDITS — detail_close_up:
[0] 보강대 2개 노출(최우선): 프레임 안에서 동시에 식별되도록 배치/표현. 오픈 수납 내부 상판 바로 아래 전면 쪽에 수평 보강대 1개, 우측 측판(내측) 방향에 수평(또는 ㄱ자) 보강대 1개가 부분적으로라도 명확히 보여야 함. user-product reference에서 보이는 보강대의 단면 두께, 길이감, 색(백색 또는 동일 톤), 세미무광 마감, 부착 포인트(나사/캡 노출 시)는 그대로 복제. 주변 패널과 구분되도록 미세 톤 대비/엣지 하이라이트/캐스트 섀도를 적용하되 과도한 글로시는 금지. 백팩·노트·선반에 가려지지 않게 오픈 수납 내부 시야를 확보.
[1] 좌하단 서랍부 교체: 현재 보이는 세 개의 서랍과 손잡이(원형 노브)를 전부 제거하고, 동일 위치를 '오픈형 책장 수납'으로 교체. 상/하 2단 선반 구조로 단순하게 표현하되, 선반과 측판 두께/색은 상판과 동일한 백색 계열로 맞춤. 서랍 분할선 자국 및 경계 음영은 남기지 말 것.
[2] 하부 수납의 성격 표현: 선반 위/아래 칸은 책(세로 꽂힘)이나 PC 본체가 들어갈 수 있는 오픈 공간임이 한눈에 인지되도록, 빈 칸으로 두거나 책 몇 권의 단순 실루엣(무라벨)만 배치. 문/서랍처럼 보이는 요소 금지.
[3] 가방걸이 유지/정돈: 우측 측면의 흰색 원형 가방걸이 1개는 그대로 유지. 현재처럼 베이지색 백팩이 자연스럽게 걸린 상태를 유지하되, 걸이 헤드/베이스의 색과 마감은 책상과 동일 톤으로 통일.
[4] 상판/모서리 디테일: 상판 모서리는 '라운드 처리'가 명확히 보이도록 엣지 하이라이트와 곡률을 부드럽게 조정. 날카로운 직각 인상(예: 날카로운 에지 쉐도우)은 제거.
[5] 표면 재질감: 상판과 측판, 선반의 표면을 미세 무광 LPM 질감으로 보정(스크래치에 강한 느낌의 잔잔한 텍스처). 과도한 글로시 하이라이트는 억제.
[6] 다리/마감: 우측 원통형 다리와 측판의 색/광택을 상판과 동일하게 맞추고 이음부를 매끈하게 정리. 레벨러(조절발)는 프레임에서 노출하지 않음. 보강대는 [0]에 따라 2개가 프레임 안에 명확히 보이도록 유지.
[7] 프롭 유지: 상판 우측 상단의 노트와 펜 2자루, 우측 하단의 베이지색 백팩은 위치/크기/색감 유지. 노트의 영문 인쇄는 그대로 두고, 한글 라벨 등 새 텍스트 삽입 금지.
KEEP: 카메라 각도/구도(좌측 하단 근접 클로즈업), 배경/조명 톤, 전체 화이트 계열 톤과 간결한 연출. 카메라 각도는 유지하되, 오픈 수납 내부의 명암과 반사 정도를 조정해 [0] 보강대 2개가 확실히 식별되도록 한다.

=== [ABSOLUTE RULES — PRESERVE / NEVER] ===
PRESERVE:
  - panel C와 같은 single panel layout, 한국 detail page 스타일
  - 카메라 각도/배경/조명/한국어 텍스트 가독성
  - 사용자 제품 feature_descriptions에 명시된 모든 특징
  - 위 [NEVER-MISS] critical 항목은 결과 이미지에 반드시 시각적으로 표현(보강대 2개 동시 식별 포함)
NEVER:
  - 사용자 제품 정보에 없는 feature 발명 (헤드레스트/리클라이너/USB/추가 다리/tufting 등)
  - 한샘 원본 텍스트 잔존
  - multi-cell grid 출력
  - 한글 텍스트 깨짐
  - NEVER-MISS critical 항목 누락
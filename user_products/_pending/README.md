# 📦 사용자 제품 입력 가이드 — Top 6 template #2~#6

각 template 처리를 위해 사용자가 줘야 할 것 + 어디에 둘지.

---

## 한샘 Top 6 (각 template과 매칭될 사용자 제품)

| # | 카테고리 | 한샘 제품 | 사용자 입력 폴더 | 상태 |
|---|---|---|---|---|
| 1 | sofa | MVME 키안티 4인 가죽 리클라이너 | (완료) | ✓ 완료 (milo 패브릭소파 2인용) |
| **2** | **wardrobe** | 샘베딩 스테디 옷장 80cm 서랍형 | `_pending/02_wardrobe/` | **활성** |
| **3** | **desk** | 티오 책상장 LED 스터디 80cm | `_pending/03_desk/` | **활성** |
| ~~4~~ | ~~sofa~~ | ~~엠마 컴포트 천연가죽 소파 4인~~ | ~~`_pending/04_sofa/`~~ | ⊘ 주석 (사용자 제품 미공급) |
| ~~5~~ | ~~wardrobe~~ | ~~샘베딩 베이직 옷장 80cm 행거서랍~~ | ~~`_pending/05_wardrobe/`~~ | ⊘ 주석 (사용자 제품 미공급) |
| ~~6~~ | ~~desk~~ | ~~티오 일반책상 120cm~~ | ~~`_pending/06_desk/`~~ | ⊘ 주석 (사용자 제품 미공급) |

활성화 / 비활성화는 `process_template.py` 의 `ENABLED_RANKS` 갱신. 현재 `{2, 3}` 만.

---

## 📋 각 폴더에 넣을 것 (per template)

```
user_products/_pending/02_wardrobe/
├── url.txt                      ← 사용자 제품 판매 페이지 URL 한 줄
└── use_product/
    ├── main_front.jpg           ← 정면 1장 (필수)
    ├── main_side.jpg            ← 측면 1장
    ├── main_angle.jpg           ← 3/4 각도
    ├── detail_01.jpg ~ detail_NN ← 디테일 close-ups (자유)
    ├── color_01.png ~ color_NN  ← 컬러 옵션 swatches
    └── material.jpg             ← 소재 클로즈업 (있으면)
```

### 파일명 자유 — 분류는 vision LLM이 자동
- `p08_frame_01.jpg`, `IMG_1234.jpg`, `sofa_front.jpg` 무엇이든 OK
- 단 `color_*` / `material*` / `detail_*` 같은 명확한 prefix 있으면 분류 정확도 ↑

### URL 형식
- `url.txt` 안에 한 줄: `https://...` (e.g. 사용자 e-commerce 페이지)
- 한샘이든 다른 사이트든 OK — vision LLM이 fetch + 분석

---

## 🚀 트리거

사용자가 한 template 폴더 채운 후 trigger 메시지:

> `처리해 #2` (또는 #3, #4, #5, #6)

자동 처리되는 것:
1. `url.txt` → product_input.json (제품명/spec/feature_descriptions/color_options 자동 추출)
2. `use_product/*` → classification.json (사진 vision 분류)
3. 한샘 template panel × 사용자 제품 → mismatch_resolution.json (swap/bypass/skip 자동 결정)
4. v17 pipeline 실행 (verifiable_checklist → swap → QA → best_selector)
5. report 갱신 — URL: http://127.0.0.1:8765/report/index.html

폴더 채우는 순서/속도 자유 — 한 번에 하나씩 처리해도, 다 채우고 일괄 trigger 해도 OK.

---

## ⚠ 주의

- **사진 부족 시 fallback**: 정면 1장만 있어도 swap 시도 가능. 단 검증 정확도/multi-angle 항목은 not_visible로 처리.
- **컬러 옵션 미제공 시**: color panel은 자동 bypass 처리됨.
- **사이즈 정보**: URL에서 가져오므로 별도 입력 불필요. 누락 시 chart panel은 bypass.

처리 끝나면 `_pending/0X_xxx/` 폴더는 자동으로 `user_products/<product_id>/`로 이동 (이름은 URL에서 추출한 제품명).

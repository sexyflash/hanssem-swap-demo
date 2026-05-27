# 한샘 detail page 패턴 리서치 결과

- 총 제품: 30개 (sofa/wardrobe/desk × 10)
- 패턴 분포: 30/30 모두 `split_panels` (한샘은 long-strip 없음, 일관된 panel 구조)

## Panel Count 분포

| 패널 개수 | 제품 수 |
|---:|---:|
| 1-5 | 0 |
| 6-10 | 5 |
| 11-15 | 4 |
| 16-25 | 14 |
| 26+ | 7 |

## Top 6 템플릿 후보

다양성 확보: 카테고리별 medium(8-15장) + rich(16-25장) 페어. 리뷰수 높은 거 우선.

| # | type | category | gdsNo | imgs | reviews | name | URL |
|---:|:---|:---|---:|---:|---:|:---|:---|
| 1 | medium(8-15) | sofa | 992474 | 12 | 615 | MVME 키안티 천연가죽 리클라이너 4인 | [link](https://store.hanssem.com/goods/992474) |
| 2 | rich(16-25) | wardrobe | 1066850 | 25 | 1888 | 샘베딩 스테디 옷장 80cm(높이194cm) 서랍형 | [link](https://store.hanssem.com/goods/1066850) |
| 3 | medium(8-15) | desk | 667832 | 11 | 1456 | 티오 책상장 LED 스터디 조명80cm | [link](https://store.hanssem.com/goods/667832) |
| 4 | rich(16-25) | sofa | 799220 | 24 | 1168 | 엠마 컴포트 천연가죽 소파 4인(3종/택1) | [link](https://store.hanssem.com/goods/799220) |
| 5 | xrich(26+) | wardrobe | 171733 | 27 | 1723 | 샘베딩 베이직 옷장 80cm(높이194cm) 행거서랍형 4종 | [link](https://store.hanssem.com/goods/171733) |
| 6 | rich(16-25) | desk | 667815 | 17 | 761 | 티오 일반책상 120cm (컬러 택1) | [link](https://store.hanssem.com/goods/667815) |

## 다음 단계 (사용자 작업)

1. 위 6개 URL 가서 detail 영역 이미지 다운로드
   - 한샘 모두 split_panels이므로 **각 이미지가 이미 분리되어 있음 → 그대로 다운로드 OK** (토막낼 필요 ✗)
   - 이미지 URL은 `hanssem_pattern.json`의 `detail_imgs` 배열에 다 있음
2. 시안+프롬프트 페어 만들기 (각 템플릿별)
3. Report HTML 빌드 (좌 원본 / 우 swap 결과 6장)

## 부가 발견

- 한샘 detail HTML은 `__NEXT_DATA__.props.pageProps.initialState.goodsDetail.storedGoods.{gdsNo}.detailInfo.goodsDetailInfo.goodsDetailHtml` 안에 raw HTML 문자열로 들어있음
- 이미지는 `image.hanssem.com` 또는 `image2.hanssem.com`에서 직접 호스팅 (CDN)
- panel 개수가 4~37장으로 다양함 → 템플릿 풀로 쓰기 좋음
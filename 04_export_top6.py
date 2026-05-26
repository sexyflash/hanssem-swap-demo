"""Top 6 템플릿 후보의 detail 이미지 URL 리스트 export."""

import json
from pathlib import Path

HERE = Path(__file__).parent
data = json.loads((HERE / "hanssem_pattern.json").read_text())

TOP6_GDS = [992474, 1066850, 667832, 799220, 171733, 667815]

products_by_gds = {p["gdsNo"]: p for p in data["products"]}

out = {"top6": []}
md_lines = ["# Top 6 템플릿 이미지 URL 모음", "", "각 카테고리별로 detail 영역 이미지를 그대로 다운로드해서 시안+프롬프트 페어 만들면 됨.", ""]

for i, gds in enumerate(TOP6_GDS, 1):
    p = products_by_gds[gds]
    md_lines += [
        f"## #{i} [{p['category']}] {p['gdsNm']}",
        "",
        f"- **gdsNo**: {p['gdsNo']}",
        f"- **URL**: {p['url']}",
        f"- **Thumbnail**: {p.get('thumbnail','')}",
        f"- **Brand**: {p.get('brand','')}",
        f"- **Price**: {p.get('salePrc','')}원",
        f"- **Reviews**: {p.get('reviewCnt',0)}",
        f"- **Detail images**: {p['detail_img_count']}장",
        "",
        "### Detail Images",
        "",
    ]
    for j, src in enumerate(p["detail_imgs"], 1):
        md_lines.append(f"{j}. {src}")
    md_lines.append("")
    out["top6"].append(
        {
            "rank": i,
            "category": p["category"],
            "gdsNo": p["gdsNo"],
            "name": p["gdsNm"],
            "url": p["url"],
            "thumbnail": p.get("thumbnail"),
            "brand": p.get("brand"),
            "price": p.get("salePrc"),
            "reviewCnt": p.get("reviewCnt"),
            "detail_img_count": p["detail_img_count"],
            "detail_imgs": p["detail_imgs"],
        }
    )

(HERE / "top6_template_urls.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
(HERE / "top6_template_urls.md").write_text("\n".join(md_lines), encoding="utf-8")
print(f"wrote top6_template_urls.json + .md")
print(f"  total detail imgs across 6 templates: {sum(len(t['detail_imgs']) for t in out['top6'])}")

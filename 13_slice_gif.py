"""밀로 panel_08.gif 360° 회전 → 균등 sampling frame 추출.

출력: user_products/milo_777039/gif_frames/frame_NN.jpg (8장)
"""

from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
GIF = HERE / "user_products/milo_777039/panel_08.gif"
OUT = HERE / "user_products/milo_777039/gif_frames"
OUT.mkdir(exist_ok=True)

SAMPLE_N = 8  # 균등 sampling 8장 (360° / 45°)

img = Image.open(GIF)
total = img.n_frames
print(f"total frames: {total}")
# 균등 인덱스
step = max(1, total // SAMPLE_N)
indices = [i * step for i in range(SAMPLE_N)]
indices = [min(i, total - 1) for i in indices]
print(f"sampling indices: {indices}")

for k, idx in enumerate(indices, 1):
    img.seek(idx)
    frame = img.convert("RGB")
    dest = OUT / f"frame_{k:02d}.jpg"
    frame.save(dest, quality=88)
    print(f"  frame_{k:02d}.jpg ← gif[{idx}] ({frame.size})")

print(f"\nsaved {SAMPLE_N} frames to {OUT}")

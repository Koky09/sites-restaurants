# -*- coding: utf-8 -*-
"""Готовит фото для индивидуальных сайтов: raw/own/<key>/NN.jpg -> own/<key>/img/NN.webp (1600 px по длинной стороне).
    python tools/own_img.py [key ...]
Списки кадров отобраны вручную: только те, что точно из этого заведения (в выгрузке бывают фото «похожих мест»)."""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PICK = {
    "balerina": [24, 28, 14, 13, 8, 3, 15, 6, 25, 33, 31, 7, 29, 4],
    "bereza": [14, 15, 4, 5, 8, 16, 11, 7, 2, 1, 13],
    "sosedi": [1, 8, 13, 4, 5, 6, 7, 11, 9, 12, 2, 3, 10],
    "kipyatok": [4, 1, 2, 3, 5, 6, 14, 16, 18, 10, 12, 13, 20, 8, 11],
    "pera": [6, 1, 24, 18, 29, 26, 2, 8, 5, 13, 11, 15, 27, 19, 20, 21, 4, 32, 31],
    "ataman": [31, 7, 33, 4, 8, 9, 10, 11, 14, 16, 17, 19, 21, 22, 25, 27, 29, 5, 2, 24],
    "sisi": [1, 5, 13, 4, 3, 11, 15, 16, 17, 18, 6, 8, 10, 2, 14],
    "nonna": [5, 4, 3, 14, 12, 1, 29, 21, 11, 15, 16, 22, 31, 30, 35, 34, 2, 19, 7],
    "gavar": [3, 12, 13, 15, 18, 19, 25, 26, 11, 5, 30, 33, 35, 20, 21],
    "hadson": [22, 17, 13, 18, 3, 5, 24, 25, 1, 23, 27, 26, 21, 4, 6, 9, 2],
}

for key, nums in PICK.items():
    if sys.argv[1:] and key not in sys.argv[1:]:
        continue
    out = ROOT / "own" / key / "img"
    out.mkdir(parents=True, exist_ok=True)
    for n in nums:
        im = Image.open(ROOT / "raw" / "own" / key / f"{n:02d}.jpg").convert("RGB")
        im.thumbnail((1600, 1600))
        im.save(out / f"{n:02d}.webp", quality=76, method=6)
    print(key, len(nums), sum(f.stat().st_size for f in out.glob("*.webp")) // 1024, "КБ")

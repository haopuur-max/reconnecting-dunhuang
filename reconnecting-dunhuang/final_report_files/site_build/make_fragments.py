#!/usr/bin/env python3
"""
Cut torn-paper fragments from the public-domain photograph of Pelliot chinois 2778
(Bibliotheque nationale de France, via Wikimedia Commons) for the presentation collage.
The torn edges are generated (deterministic random polygon); nothing is added to the image.
    python3 final_report_files/site_build/make_fragments.py
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets/img/manuscript_pelliot_chinois_2778.jpg"
OUT = ROOT / "assets/img/fragments"
# (x, y, width, height) regions of the manuscript, avoiding the shelf-mark label and the grey border
REGIONS = [(60, 40, 330, 300), (420, 120, 300, 340), (180, 430, 340, 300), (640, 470, 300, 280), (760, 60, 260, 300)]


def torn_mask(w, h, seed):
    rnd = random.Random(seed)
    pts = []
    steps = 34
    for i in range(steps):
        t = i / steps * 2 * math.pi
        # an irregular, roughly rectangular outline with small tears
        cx, cy = w / 2, h / 2
        x = cx + (w / 2 - 6) * max(-1, min(1, 1.25 * math.cos(t)))
        y = cy + (h / 2 - 6) * max(-1, min(1, 1.25 * math.sin(t)))
        x += rnd.uniform(-w * 0.045, w * 0.045)
        y += rnd.uniform(-h * 0.045, h * 0.045)
        pts.append((max(2, min(w - 2, x)), max(2, min(h - 2, y))))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.filter(ImageFilter.GaussianBlur(0.8))


def main():
    src = Image.open(SRC).convert("RGB")
    OUT.mkdir(parents=True, exist_ok=True)
    for i, (x, y, w, h) in enumerate(REGIONS, 1):
        piece = src.crop((x, y, x + w, y + h)).convert("RGBA")
        piece.putalpha(torn_mask(w, h, seed=i * 17))
        piece.save(OUT / f"fragment_{i}.png", optimize=True)
    print(f"{len(REGIONS)} fragments written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

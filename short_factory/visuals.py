from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFilter


def fallback_visual(output_path: Path, palette: list[tuple[int, int, int]], seed: int = 0, size=(768, 1344)) -> Path:
    w, h = size
    img = Image.new("RGB", size, palette[0])
    px = img.load()
    for y in range(h):
        for x in range(w):
            u = x / w
            v = y / h
            wave = (math.sin((u * 9 + v * 4 + seed) * math.pi) + 1) / 2
            idx = min(len(palette) - 1, int(wave * len(palette)))
            c1 = palette[max(0, idx - 1)]
            c2 = palette[idx]
            mix = wave * 0.65
            px[x, y] = tuple(int(c1[i] * (1 - mix) + c2[i] * mix) for i in range(3))
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    for r in range(40, min(w, h), 40):
        alpha = max(0, 65 - r // 12)
        d.ellipse((w//2-r, h//2-r, w//2+r, h//2+r), outline=palette[-1] + (alpha,), width=4)
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    img.save(output_path, quality=95)
    return output_path

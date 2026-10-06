"""Build transparent NOVA AI logo assets from the black-background PNG.

- Removes the near-black background -> transparent (keeps bright wordmark pixels)
- Produces full-canvas and tightly-cropped versions at several sizes
- Generates favicon (ICO + PNG) and apple-touch-icon
"""
import numpy as np
from PIL import Image, ImageOps

SRC = r"C:\Users\5g\OneDrive\Desktop\nova\logo\logo.png"
OUT = r"C:\Users\5g\OneDrive\Desktop\nova\assets\img"

img = Image.open(SRC).convert("RGB")
w, h = img.size
a = np.asarray(img).astype(np.int32)

# alpha ramp: pixels close to black become transparent, bright pixels opaque
maxc = a.max(axis=2)
low, high = 14, 52
alpha = np.clip((maxc - low) * (255.0 / (high - low)), 0, 255).astype(np.uint8)
# clean up isolated specks (anti-noise)
rgba = np.dstack([a.astype(np.uint8), alpha])
out = Image.fromarray(rgba, "RGBA")

# ---- full canvas ----
out.save(f"{OUT}/logo.png")

# ---- content bounding box with a little padding ----
mask = alpha > 24
rows = np.any(mask, axis=1); cols = np.any(mask, axis=0)
r0, r1 = np.argmax(rows), h - np.argmax(rows[::-1])
c0, c1 = np.argmax(cols), w - np.argmax(cols[::-1])
padx = int((c1 - c0) * 0.04); pady = int((r1 - r0) * 0.10)
box = (max(0, c0 - padx), max(0, r0 - pady), min(w, c1 + padx), min(h, r1 + pady))
tight = out.crop(box)
tw, th = tight.size
print("tight crop:", (tw, th), "aspect:", round(tw / th, 2))

# horizontal whitespace runs inside the cropped area (to detect a separate mark)
m = np.asarray(tight.convert("L")) > 24
col_empty = ~m.any(axis=0)
runs = []
start = None
for x in range(tw):
    if col_empty[x] and start is None:
        start = x
    elif not col_empty[x] and start is not None:
        runs.append((start, x)); start = None
print("empty column runs (x ranges):", runs[:12])

sizes = [640, 480, 320, 220]
for s in sizes:
    small = tight.resize((s, max(2, int(s * th / tw))), Image.LANCZOS)
    small.save(f"{OUT}/logo-{s}.png")

# ---- favicon(s): wordmark centered on brand-dark square ----
fs = 128
fav = Image.new("RGBA", (fs, fs), (10, 10, 10, 255))
logow = int(fs * 0.86)
logoh = max(2, int(logow * th / tw))
wl = tight.resize((logow, logoh), Image.LANCZOS)
fav.alpha_composite(wl, ((fs - logow) // 2, (fs - logoh) // 2))
fav.save(f"{OUT}/favicon-128.png")
fav.resize((64, 64), Image.LANCZOS).save(f"{OUT}/favicon-64.png")
fav.resize((32, 32), Image.LANCZOS).save(f"{OUT}/favicon-32.png")

ico = Image.new("RGBA", (64, 64), (10, 10, 10, 255))
w2 = int(64 * 0.86); h2 = int(w2 * th / tw)
ico.alpha_composite(tight.resize((w2, h2), Image.LANCZOS), ((64 - w2) // 2, (64 - h2) // 2))
ico.save(f"{OUT}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

# apple touch icon 180
at = Image.new("RGBA", (180, 180), (10, 10, 10, 255))
w3 = int(180 * 0.7); h3 = int(w3 * th / tw)
at.alpha_composite(tight.resize((w3, h3), Image.LANCZOS), ((180 - w3) // 2, (180 - h3) // 2))
at.save(f"{OUT}/apple-touch-icon.png")

print("done")
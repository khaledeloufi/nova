"""Analyze the NOVA AI logo to understand its background and colors."""
import numpy as np
from PIL import Image

img = Image.open(r"C:\Users\5g\OneDrive\Desktop\nova\logo\logo.png").convert("RGBA")
print("size:", img.size, "mode:", img.mode)

a = np.asarray(img).astype(np.int32)
h, w = a.shape[:2]

def px(x, y):
    return tuple(a[y, x])

corners = [px(5, 5), px(w - 6, 5), px(5, h - 6), px(w - 6, h - 6)]
print("corners:", corners)

# median of all pixels
med = np.median(a[:, :, :3].reshape(-1, 3), axis=0)
print("median rgb:", med.round(2))

# opaque fraction
opaque = (a[:, :, 3] > 200)
print("opaque fraction:", opaque.mean().round(4))

# among opaque pixels, luminance distribution
lum = a[:, :, :3].mean(axis=2)
print("lum mean/max/min (opaque):", lum[opaque].mean().round(1), lum[opaque].max(), lum[opaque].min())

# distinct colors: quantize to 16 levels per channel
sub = a[::4, ::4]
key = (sub[:, :, :3] // 16).astype(np.uint32)
key = key[:, :, 0] << 16 | key[:, :, 1] << 8 | key[:, :, 2]
vals, counts = np.unique(key, return_counts=True)
order = np.argsort(-counts)
print("top color buckets (approx srgb):")
for i in order[:12]:
    v = vals[i]
    r = (v >> 16) * 16 + 8; g = ((v >> 8) & 255) * 16 + 8; b = (v & 255) * 16 + 8
    print(f"  #{r:02X}{g:02X}{b:02X}  {counts[i]}")

# bounding box of non-black opaque content (luminance > 40 or strong color)
mask = opaque & (lum > 35)
rows = np.any(mask, axis=1); cols = np.any(mask, axis=0)
r0, r1 = np.argmax(rows), h - np.argmax(rows[::-1])
c0, c1 = np.argmax(cols), w - np.argmax(cols[::-1])
print("content bbox:", (c0, r0, c1, r1), "->", (c1 - c0, r1 - r0))
print("crop ratio (h/w):", round((r1 - r0) / (c1 - c0), 3))
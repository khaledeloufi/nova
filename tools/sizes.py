import os, json, numpy as np
from PIL import Image

root = r"C:/Users/5g/OneDrive/Desktop/nova"

def dirsize(d):
    total = 0
    for dp, _, fns in os.walk(os.path.join(root, d)):
        for f in fns:
            total += os.path.getsize(os.path.join(dp, f))
    return total

for d in ["assets/videos", "assets/img", "assets/css", "assets/js", "work"]:
    print(f"{d:15s} {dirsize(d)/1e6:8.2f} MB")

a = np.asarray(Image.open(os.path.join(root, "assets/img/logo.png")).convert("RGBA"))
al = a[:, :, 3]
print("logo alpha  min/max:", al.min(), al.max(),
      "| opaque px:", int((al > 220).sum()), "| edge px:", int(((al > 5) & (al < 220)).sum()))
# confirm white pixels intact
lum = a[a[:, :, 3] > 120, :3].mean()
print("avg rgb of visible logo px:", lum.round(1))
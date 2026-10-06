import os, re, glob, sys

root = "C:/Users/5g/OneDrive/Desktop/nova"
htmls = glob.glob(root + "/**/*.html", recursive=True)
missing = []
for h in htmls:
    src = open(h, encoding="utf-8").read()
    rd = os.path.dirname(h)
    for m in re.findall(r'(?:src|href|poster)="([^"]+)"', src):
        if m.startswith(("http", "mailto", "tel:", "#", "data:")):
            continue
        p = os.path.normpath(os.path.join(rd, m.split("#")[0].split("?")[0]))
        if not os.path.exists(p):
            missing.append((os.path.relpath(h, root), m))
print("html files:", len(htmls))
if missing:
    print("MISSING:")
    for x in missing[:60]:
        print("  ", x)
    sys.exit(1)
print("ALL ASSET REFS RESOLVE")
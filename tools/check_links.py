# -*- coding: utf-8 -*-
"""Validate all internal links in generated pages resolve to existing files."""
import os
import posixpath
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = ["index.html"]
PAGES += [os.path.join("work", s, "index.html")
          for s in ["v7", "mercure", "arpege", "veloce", "coffee", "burger", "crispy"]]

SKIP = ("#", "mailto:", "http", "tel:", "javascript:")

broken = []
for rel in PAGES:
    path = os.path.join(ROOT, rel)
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    for href in re.findall(r'href="([^"]+)"', html):
        if href.startswith(SKIP) or href == "javascript:void(0)":
            continue
        path_only = href.split("#", 1)[0]
        if not path_only:
            continue  # pure in-page anchor
        base = posixpath.dirname(rel.replace(os.sep, "/"))
        target = posixpath.normpath(posixpath.join(base, path_only))
        if not os.path.isfile(os.path.join(ROOT, target)):
            broken.append((rel, href, target))

if broken:
    print("BROKEN INTERNAL LINKS:")
    for rel, href, target in broken:
        print(f"  {rel}  ->  {href}   (resolves to {target})")
    raise SystemExit(1)
print(f"CHECKED {len(PAGES)} pages — ALL INTERNAL LINKS RESOLVE")
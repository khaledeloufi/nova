#!/usr/bin/env python3
"""NOVA AI — static site generator.

Reads assets/data/projects.json (the CMS-like project data) + assets/videos/manifest.json
and:
  1. Generates a static case-study page at work/<slug>/index.html for every project
  2. Injects the "Selected Work" reel rows into index.html (between WORK-REEL markers)

Add a new project -> add an object to projects.json -> run `python tools/build.py`.
"""
import json, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "assets", "data", "projects.json")
MANIFEST = os.path.join(ROOT, "assets", "videos", "manifest.json")

with open(DATA, encoding="utf-8") as f:
    SITE = json.load(f)
with open(MANIFEST, encoding="utf-8") as f:
    MANI = json.load(f)

PROJECTS = SITE["projects"]
C = SITE["contact"]


def rel(*parts):
    return "/".join(parts)


def is_portrait(slug):
    post = MANI[slug]["poster"]
    p = os.path.join(ROOT, "assets", "img", post)
    with Image.open(p) as im:
        return im.size[1] > im.size[0]


def asset_paths(slug, base="../../assets"):
    m = MANI[slug]
    video = f"{base}/videos/{slug}.mp4"
    poster = f"{base}/img/{m['poster']}"
    frames = [f"{base}/img/{fr}" for fr in m["frames"]]
    return video, poster, frames


def label_of(p):
    return f"{p['category'].upper()} / {p['discipline'].upper()}"


# ---------------------------------------------------------------- nav / chrome
def chrome_head(title, desc, ogimage):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0a0a09">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{ogimage}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/x-icon" href="../../assets/img/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="../../assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="../../assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/main.css">
<noscript>
<style>
  .mask > span{{ transform:none !important; }}
  [data-reveal]{{ opacity:1 !important; transform:none !important; }}
  .preloader{{ display:none !important; }}
  .menu{{ display:none !important; }}
</style>
</noscript>
</head>
<body>"""


def nav_and_menu():
    return """<div class="scrollbar" aria-hidden="true"><span></span></div>
<header class="nav" id="nav">
  <div class="container nav-inner">
    <a class="nav-logo" href="../../index.html" aria-label="NOVA AI — home">
      <img src="../../assets/img/logo-220.png" alt="NOVA AI">
    </a>
    <nav class="nav-links" aria-label="Primary">
      <a href="../../index.html#work"><span>Work</span></a>
      <a href="../../index.html#services"><span>Services</span></a>
      <a href="../../index.html#about"><span>About</span></a>
      <a href="../../index.html#faq"><span>FAQ</span></a>
      <a href="../../index.html#contact"><span>Contact</span></a>
    </nav>
    <div class="nav-right">
      <a class="nav-cta" href="#start">Start a Project</a>
      <button class="burger" id="burger" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><span></span><span></span></button>
    </div>
  </div>
</header>

<div class="menu" id="menu" aria-hidden="true">
  <nav aria-label="Menu">
    <ul>
      <li><a href="../../index.html#work"><span class="n">01</span>Work</a></li>
      <li><a href="../../index.html#services"><span class="n">02</span>Services</a></li>
      <li><a href="../../index.html#about"><span class="n">03</span>About</a></li>
      <li><a href="../../index.html#faq"><span class="n">04</span>FAQ</a></li>
      <li><a href="../../index.html#contact"><span class="n">05</span>Contact</a></li>
    </ul>
  </nav>
  <div class="menu-foot">
    <span class="label">AI Creative Studio</span>
    <a class="btn btn-ghost" href="#start">Start a Project <span class="ar">→</span></a>
  </div>
</div>"""


def footer():
    return f"""<footer class="footer">
    <div class="container">
      <div class="footer-wordmark" aria-hidden="true"><img src="../../assets/img/logo-640.png" alt=""></div>
      <div class="footer-mid">
        <div><h4>Studio</h4><p class="tagline">AI Creative Studio</p></div>
        <div><h4>Navigate</h4><ul>
          <li><a href="../../index.html#work">Work</a></li>
          <li><a href="../../index.html#services">Services</a></li>
          <li><a href="../../index.html#about">About</a></li>
          <li><a href="../../index.html#faq">FAQ</a></li>
          <li><a href="../../index.html#contact">Contact</a></li>
        </ul></div>
        <div><h4>Social</h4><div class="soc-row">
          <a class="soc" href="{C['instagram']}" target="_blank" rel="noopener" aria-label="NOVA AI on Instagram"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.31-1.46.72-2.13 1.38C1.35 2.68.94 3.35.63 4.14.33 4.9.13 5.78.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.31.79.72 1.46 1.38 2.13.67.66 1.34 1.07 2.13 1.38.76.3 1.64.5 2.91.56 1.28.06 1.69.07 4.95.07s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56.79-.31 1.46-.72 2.13-1.38.66-.67 1.07-1.34 1.38-2.13.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.15-.56-2.91-.31-.79-.72-1.46-1.38-2.13A5.9 5.9 0 0 0 19.86.63c-.76-.3-1.64-.5-2.91-.56C15.67.01 15.26 0 12 0zm0 2.16c3.2 0 3.58.01 4.85.07 1.17.06 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.43.35 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.06 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.43.16-1.06.35-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.06-1.8-.25-2.23-.41a3.7 3.7 0 0 1-1.38-.9 3.7 3.7 0 0 1-.9-1.38c-.16-.43-.35-1.06-.41-2.23C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85c.06-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.43-.16 1.06-.35 2.23-.41 1.27-.06 1.65-.07 4.85-.07zM12 5.84A6.16 6.16 0 1 0 18.16 12 6.16 6.16 0 0 0 12 5.84zm0 10.15A4 4 0 1 1 16 12a4 4 0 0 1-4 3.99zm7.85-10.4a1.44 1.44 0 1 1-1.44-1.44 1.44 1.44 0 0 1 1.44 1.44z"/></svg></a>
          <a class="soc" href="{C['tiktok']}" target="_blank" rel="noopener" aria-label="NOVA AI on TikTok"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg></a>
        </div></div>
        <div><h4>Contact</h4><ul>
          <li><a href="mailto:{C['email']}">{C['email']}</a></li>
          <li><a href="https://wa.me/{C['whatsapp']}">{C['phone']}</a></li>
        </ul></div>
      </div>
      <div class="footer-base">
        <span>© <span data-year>2026</span> NOVA AI. All rights reserved.</span>
        <span>AI Creative Studio</span>
      </div>
    </div>
  </footer>"""


# ---------------------------------------------------------------- reel rows
def reel_rows():
    items = [p for p in PROJECTS if not p.get("featured")]
    rows = []
    for i, p in enumerate(items, 1):
        video, poster, _ = asset_paths(p["slug"], base="assets")
        portrait = " is-portrait" if is_portrait(p["slug"]) else ""
        rows.append(
            f"""<article class="reel-item" data-project="{p['slug']}">
          <a class="reel-link" href="work/{p['slug']}/index.html" data-cursor="view">
            <div class="reel-media{portrait}">
              <img src="{poster}" alt="{p['title']} — {p['category']} / {p['discipline']}" loading="lazy">
              <video muted loop playsinline preload="none" aria-hidden="true">
                <source src="{video}" type="video/mp4">
              </video>
              <div class="reel-shade"></div>
              <span class="reel-badge">View Case</span>
            </div>
            <div class="reel-meta">
              <span class="n">{"%02d" % i}</span>
              <span class="t">{p['title']}</span>
              <span class="c">{p['category']} / {p['discipline']}</span>
              <span class="y">{p['year']}</span>
              <span class="ar">→</span>
            </div>
          </a>
        </article>"""
        )
    return "\n      ".join(rows)


def generate_index_reel():
    with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
        html = f.read()
    pattern = re.compile(r"<!-- WORK-REEL:BEGIN -->(.*?)<!-- WORK-REEL:END -->", re.S)
    assert pattern.search(html), "markers not found in index.html"
    html = pattern.sub("<!-- WORK-REEL:BEGIN -->\n      " + reel_rows() + "\n      <!-- WORK-REEL:END -->", html)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html reel updated")


# ---------------------------------------------------------------- project page
def project_page(p):
    slug = p["slug"]
    video, poster, frames = asset_paths(slug)
    label = label_of(p)
    portrait = " is-portrait" if is_portrait(slug) else ""

    # related = next 3 projects
    idx = PROJECTS.index(p)
    others = [q for q in PROJECTS[idx + 1:] + PROJECTS[:idx] if q["slug"] != slug][:3]
    related_html = "\n".join(
        f"""<li>
          <a href="../{q['slug']}/index.html" data-cursor="view">
            <span class="num">{"%02d" % i}</span>
            <h3>{q['title']}</h3>
            <span class="meta">{q['category']} / {q['discipline']}<br><span class="label" style="letter-spacing:.14em">{q['year']}</span></span>
            <span class="ar">→</span>
          </a>
        </li>"""
        for i, q in enumerate(others, 1)
    )

    services_html = "".join(f"<span>{s}</span>" for s in p["services"])

    page = chrome_head(
        f"{p['title']} — NOVA AI Case Study",
        p["description"],
        poster,
    )
    page += nav_and_menu()

    page += f"""
<main>
  <!-- preloader — cinematic film intro -->
  <div class="preloader" id="preloader" aria-hidden="true">
    <div class="pl-overlay" aria-hidden="true"></div>
    <div class="pl-grain" aria-hidden="true"></div>
    <div class="pl-flash" aria-hidden="true"></div>
    <div class="pl-chrome" aria-hidden="true">
      <span class="pl-brand label">NOVA AI — Case Study</span>
      <span class="pl-rec label"><i class="pl-dot"></i>REC</span>
      <div class="pl-bottom">
        <div class="pl-line"><span></span></div>
        <div class="pl-meta">
          <span class="pl-count" id="pl-count">0%</span>
          <span class="pl-tc" id="pl-tc">00:00:00:00</span>
        </div>
      </div>
    </div>
  </div>

  <!-- ===== hero ===== -->
  <section class="p-hero" id="top" aria-label="{label}. {p['title']}">
    <div class="p-hero-media" data-cursor="view">
      <video autoplay muted loop playsinline preload="metadata" poster="{poster}" data-autoplay aria-hidden="true">
        <source src="{video}" type="video/mp4">
      </video>
      <div class="p-hero-shade"></div>
    </div>
    <div class="container p-hero-inner">
      <div class="p-eyebrow">
        <span class="label">{label}</span>
        <span class="label">{p["year"]}</span>
      </div>
      <h1 class="ttl">{p["title"]}<em>.</em></h1>
      <p class="p-hero-desc" data-reveal>{p["description"]}</p>
    </div>
  </section>

  <!-- ===== overview ===== -->
  <section class="p-section first">
    <div class="container p-grid">
      <div>
        <span class="p-kicker">01 — Overview</span>
        <div class="side">
          <div><span class="k">Client</span><span class="v">{p["client"]}</span></div>
          <div><span class="k">Year</span><span class="v">{p["year"]}</span></div>
          <div><span class="k">Services</span><span class="v">{p["role"]}</span></div>
          <div><span class="k">Format</span><span class="v">{p["discipline"]}</span></div>
        </div>
      </div>
      <div class="p-copy"><p>{p["overview"]}</p></div>
    </div>
  </section>

  <!-- ===== creative direction (full-bleed media) ===== -->
  <section class="p-section">
    <div class="p-media vid" data-cursor="view">
      <video autoplay muted loop playsinline preload="metadata" poster="{poster}" data-autoplay aria-hidden="true">
        <source src="{video}" type="video/mp4">
      </video>
    </div>
    <div class="container p-grid" style="margin-top:clamp(2.5rem,6vw,4.5rem)">
      <div>
        <span class="p-kicker">02 — Creative Direction</span>
      </div>
      <div class="p-copy"><p>{p["creativeDirection"]}</p></div>
    </div>
  </section>

  <!-- ===== visual approach (gallery) ===== -->
  <section class="section p-section" style="padding-block:clamp(3rem,7vw,5.5rem)">
    <div class="container">
      <div class="p-gallery">
        <div class="p-media" data-cursor="view"><img src="{frames[0]}" alt="{p['title']} — shot 01" loading="lazy"></div>
        <div class="p-media" data-cursor="view"><img src="{frames[1]}" alt="{p['title']} — shot 02" loading="lazy"></div>
        <div class="p-media" data-cursor="view"><img src="{frames[2]}" alt="{p['title']} — shot 03" loading="lazy"></div>
      </div>
      <div class="p-grid" style="margin-top:clamp(2.5rem,6vw,4.5rem)">
        <div>
          <span class="p-kicker">03 — Visual Approach</span>
          <div class="side" style="margin-top:1.6rem">
            <div><span class="k">Discipline</span><span class="v">{p["discipline"]}</span></div>
            <div><span class="k">Services</span><span class="v">{p["services"][0]}<br>{p["services"][1]}</span></div>
          </div>
        </div>
        <div class="p-copy"><p>{p["visualApproach"]}</p></div>
      </div>
    </div>
  </section>

  <!-- ===== production + final result ===== -->
  <section class="p-section">
    <div class="container p-grid">
      <div>
        <span class="p-kicker">04 — Production</span>
      </div>
      <div class="p-copy"><p>{p["production"]}</p></div>
    </div>
  </section>

  <section class="p-section" style="padding-top:0">
    <div class="container p-grid" style="margin-top:0">
      <div>
        <span class="p-kicker">05 — Final Result</span>
      </div>
      <div class="p-copy"><p>{p["finalResult"]}</p></div>
    </div>
  </section>

  <!-- ===== looping film ===== -->
  <section class="p-video">
    <div class="p-media vid" data-cursor="view">
      <video autoplay muted loop playsinline preload="metadata" poster="{poster}" data-autoplay aria-hidden="true">
        <source src="{video}" type="video/mp4">
      </video>
    </div>
    <p class="cap">{label}</p>
  </section>

  <!-- ===== related ===== -->
  <section class="section" style="padding-bottom:clamp(2rem,4vw,3rem)" aria-label="Related projects">
    <div class="container">
      <div class="section-head">
        <p class="label" data-reveal>Next — Case Studies</p>
      </div>
      <ul class="related">
{related_html}
      </ul>
    </div>
  </section>

  <!-- ===== CTA ===== -->
  <section class="p-cta" id="start">
    <h2 class="glow" data-reveal>Have a product<br>that deserves <em>this?</em></h2>
    <div class="contact-ctas" style="justify-content:center" data-reveal>
      <a class="btn btn-solid btn-big magnetic" href="mailto:{C['email']}?subject=Project%20Inquiry%20%E2%80%94%20NOVA%20AI">Start a Project <span class="ar">→</span></a>
      <a class="btn btn-line btn-big magnetic" href="mailto:{C['email']}">Email NOVA AI</a>
    </div>
  </section>

  {footer()}
</main>
<script src="../../assets/js/main.js"></script>
</body>
</html>"""
    return page


def main():
    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    for p in PROJECTS:
        outdir = os.path.join(ROOT, "work", p["slug"])
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
            f.write(project_page(p))
        print("generated work/%s/index.html" % p["slug"])
    generate_index_reel()


if __name__ == "__main__":
    main()
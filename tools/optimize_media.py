"""Optimize NOVA AI videos: re-encode for web, extract posters + gallery keyframes."""
import subprocess, os, json, sys

ROOT = r"C:\Users\5g\OneDrive\Desktop\nova"
SRC = os.path.join(ROOT, "projects")
OUTV = os.path.join(ROOT, "assets", "videos")
OUTI = os.path.join(ROOT, "assets", "img")

# slug -> (source file substring, nice name)
MAPPING = {
    "v7": "Pouring_blue_cream_soda",
    "mercure": "Luxury_skeleton_watch_commercial",
    "arpege": "Fragrance_commercial_storyboard",
    "veloce": "Cupra_Leon_interior_technical",
    "coffee": "Coca-Cola_coffee_commercial_splash",
    "burger": "Burger_commercial_animation",
    "crispy": "Fried_chicken_commercial_explosion",
}

os.makedirs(OUTV, exist_ok=True)
os.makedirs(OUTI, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd[:6]))
        print(r.stderr[-1200:])
        sys.exit(1)

def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip().splitlines()[0])

videos = [f for f in os.listdir(SRC) if f.lower().endswith(".mp4")]
found = {}
for slug, needle in MAPPING.items():
    match = next((f for f in videos if needle in f), None)
    if not match:
        print("WARN: no source for", slug, needle); continue
    found[slug] = os.path.join(SRC, match)

manifest = {}
for slug, src in found.items():
    dur = probe_duration(src)
    mp4 = os.path.join(OUTV, f"{slug}.mp4")
    poster = os.path.join(OUTI, f"{slug}-poster.jpg")
    print(f"[{slug}] {dur:.1f}s transcoding...", flush=True)
    run(["ffmpeg", "-y", "-i", src,
         "-c:v", "libx264", "-crf", "25", "-preset", "slow",
         "-vf", "scale=w=min(1280\\,iw):h=min(1280\\,ih):force_original_aspect_ratio=decrease:force_divisible_by=2",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", mp4])
    sz = os.path.getsize(mp4) / 1e6
    print(f"[{slug}] -> {sz:.1f} MB", flush=True)

    run(["ffmpeg", "-y", "-ss", "0.6", "-i", src, "-frames:v", "1",
         "-vf", "scale=w=min(1280\\,iw):h=min(1280\\,ih):force_original_aspect_ratio=decrease", "-q:v", "4", poster])

    frames = []
    for i, t in enumerate([0.15, 0.5, 0.85]):
        out = os.path.join(OUTI, f"{slug}-frame-{i+1}.jpg")
        run(["ffmpeg", "-y", "-ss", f"{dur*t:.2f}", "-i", src, "-frames:v", "1",
             "-vf", "scale=w=min(1280\\,iw):h=min(1280\\,ih):force_original_aspect_ratio=decrease", "-q:v", "4", out])
        frames.append(f"{slug}-frame-{i+1}.jpg")
    manifest[slug] = {"video": f"{slug}.mp4", "poster": f"{slug}-poster.jpg",
                      "frames": frames, "duration": round(dur, 2)}

with open(os.path.join(OUTV, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)
print("media done")
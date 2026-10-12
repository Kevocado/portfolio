#!/usr/bin/env python3
"""TDD checks for Kevin Sigey's portfolio site (~/workspace/portfolio-site/site/).

Landing page and photography page in Brittany Chiang v4 design language
(static, flat colors, no gradients).
"""
import re
import sys
import json
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
failures = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


class LinkImgParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bad_links = []
        self.bad_imgs = []
        self.imgs = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and not d.get("href", "").strip():
            self.bad_links.append(self.getpos())
        if tag == "img":
            self.imgs.append(d.get("src", ""))
            if not d.get("alt", "").strip():
                self.bad_imgs.append(self.getpos())


index = (SITE / "index.html").read_text(encoding="utf-8")
photos = (SITE / "photos.html").read_text(encoding="utf-8")
main_css = (SITE / "css" / "main.css").read_text(encoding="utf-8")
main_js = (SITE / "js" / "main.js").read_text(encoding="utf-8")

# ---------- 1. files ----------
for rel in ["index.html", "photos.html", "css/main.css", "css/photos.css",
            "js/main.js", "assets/resume.pdf", "assets/papers/tightness-paradox.pdf"]:
    check(f"file exists: {rel}", (SITE / rel).is_file())

# ---------- 2. index references new assets only ----------
check("index references css/main.css", "css/main.css" in index)
check("index references js/main.js", "js/main.js" in index)
check("index has viewport meta",
      bool(re.search(r'<meta[^>]+name=["\']viewport["\']', index, re.I)))
for legacy in ["theme-editorial.css", "theme-darkroom.css",
               "theme-terminal.css", "js/theme.js", "data-theme=",
               "data-set-theme"]:
    check(f"index does not reference legacy {legacy}", legacy not in index)

# ---------- 3. v4 design tokens ----------
for token in ["#0c0c0e", "#17171b", "#8892b0", "#ccd6f6", "#64ffda",
              "JetBrains Mono", "--nav-height", "--green-tint"]:
    check(f"main.css uses v4 token {token}", token in main_css)

# ---------- 4. Kevin's hard rule: FLAT colors, no gradients ----------
check("main.css has no linear-gradient", "linear-gradient" not in main_css)
check("main.css has no radial-gradient", "radial-gradient" not in main_css)
check("main.css balanced braces",
      main_css.count("{") == main_css.count("}") and main_css.count("{") > 0)

# ---------- 5. v4 structure present ----------
for frag in ['class="site-header"', 'class="nav-links"', 'class="rail rail-left"',
             'class="rail rail-right"', 'class="hero"', 'class="eyebrow"',
             'class="big-heading"', 'class="section-heading"',
             'class="tab-btn', 'class="tab-panel', 'class="projects-grid"',
             'class="project-card"', 'class="card-tech"', 'class="footer"',
             'id="menuBtn"', 'id="mobileMenu"']:
    check(f"index has {frag}", frag in index)
check("nav has 4 numbered sections + photography",
      all(f'href="#{s}"' in index for s in ["about", "experience", "work", "contact"])
      and 'href="photos.html"' in index)

# ---------- 6. content ----------
for phrase in ["Hi, my name is", "Kevin Sigey.",
               "Quantitative problem solver and clear communicator",
               "01.", "About Me", "02.", "Where I",
               "03.", "Some Things I",
               "04.", "Get In Touch",
               "sigeykevin@gmail.com",
               "linkedin.com/in/kevin-sigey-72a5501b5",
               "Predictor Hub", "Algo Trade Hub",
               "Stablecoin Remittance Monitor",
               "Synchrony Guardrail Engine", "FPL Scout",
               "Tightness Paradox", "Data-Center Energy Analysis",
               "Status: Live", "In active rebuild", "Pipeline running",
               "Competition entry", "Status: Shipped",
               "Status: Research paper", "Status: Interactive paper",
               "github.com/Kevocado/predictor-hub",
               "github.com/Kevocado/algo-trade-hub-prod",
               "github.com/Kevocado/Stable-Coin-Analysis",
               "github.com/Kevocado/FPL_Optimizer",
               "assets/papers/tightness-paradox.pdf",
               "data-center-energy-analysis-sxg6axdjxrs2xuq",
               "40-160-91-131.sslip.io",
               "assets/resume.pdf",
               "Busey Bank", "Illinois Business Consulting",
               "Tandon Consulting Club", "Dot Foods", "WOW Payments",
               "job-wow", "Fintech Marketing Intern",
               "150 to 450", "100+ door-to-door"]:
    check(f"index content present: {phrase!r}", phrase in index)

# ---------- 7. links / imgs / emojis / lorem on index ----------
lp = LinkImgParser()
lp.feed(index)
check("index: every <a> has a non-empty href", not lp.bad_links)
check("index: every <img> has alt text", not lp.bad_imgs)
emoji_re = re.compile(r"[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF"
                      r"\u2600-\u27BF\u2B00-\u2BFF]")
check("no emojis in index", not emoji_re.findall(index))
check("no lorem in index", "lorem" not in index.lower())
check("no em-dashes in index", "\u2014" not in index)
check("no em-dashes in main.css", "\u2014" not in main_css)

# ---------- 8. photos.html: v4 styling, no legacy theme system ----------
for css in ["css/main.css", "css/photos.css"]:
    check(f"photos references {css}", css in photos)
for legacy in ["theme-editorial.css", "theme-darkroom.css",
               "theme-terminal.css", "js/theme.js", "data-theme=",
               "data-set-theme", "ksigey-edition"]:
    check(f"photos does not reference legacy {legacy}", legacy not in photos)
check("photos has viewport meta",
      bool(re.search(r'<meta[^>]+name=["\']viewport["\']', photos, re.I)))

# ---------- 9. photos.html: three categories only ----------
for cat in ["Fashion", "Editorial", "Portrait"]:
    check(f"photos has category section: {cat}",
          f'aria-label="{cat}"' in photos)
for gone in ["San Francisco", "san-francisco", "Fly Kids Community",
             "Beach Days", "On Stage", "Nairobi Editorial"]:
    check(f"photos has no legacy series {gone!r}", gone not in photos)

# ---------- 10. photos.html: manifest parity (files are {src, post}) ----------
manifest = json.loads((SITE / "assets" / "photos" / "manifest.json")
                      .read_text(encoding="utf-8"))
check("manifest has >= 72 shoots", len(manifest) >= 72,
      f"found {len(manifest)}")
cats = {m["category"] for m in manifest}
check("manifest categories are exactly Fashion/Editorial/Portrait",
      cats == {"Fashion", "Editorial", "Portrait"}, str(cats))
check("manifest has 3 featured shoots",
      sum(1 for m in manifest if m.get("featured")) == 3)
# HARD RULE (Kevin, 2026-10-12): one shoot/collection = exactly ONE
# Instagram post. Every photo in a shoot must share one post URL, and the
# shoot-level post_url must be that same post. Fail loudly otherwise.
one_post_violations = [
    m["slug"] for m in manifest
    if len({f["post"] for f in m["files"]}) != 1
]
check("one post per shoot (hard rule)", not one_post_violations,
      str(one_post_violations)[:200])
post_url_mismatch = [
    m["slug"] for m in manifest
    if m.get("post_url") not in {f["post"] for f in m["files"]}
]
check("shoot post_url matches its files' shared post", not post_url_mismatch,
      str(post_url_mismatch)[:200])
# no post may lose photos vs the baseline (186 photos after the
# 2026-10-12 removal of back-and-better and album-release-party);
# splits move photos between shoots, never drop them
BASELINE_TOTAL_PHOTOS = 186
total_photos = sum(len(m["files"]) for m in manifest)
check("no photos dropped vs baseline", total_photos >= BASELINE_TOTAL_PHOTOS,
      f"found {total_photos}")
check("manifest files are {src, post} objects",
      all(isinstance(f, dict) and "src" in f and "post" in f
          for m in manifest for f in m["files"]))

photo_srcs = re.findall(r'<img[^>]+src="([^"]+)"', photos)
manifest_files = [f["src"] for m in manifest for f in m["files"]]
thumb_srcs = {f"assets/photos/thumbs/{m['slug']}.jpg" for m in manifest}
check("every manifest file appears as an <img> src or in gallery JSON",
      set(manifest_files) <= set(photo_srcs) | set(
          re.findall(r'"src": "([^"]+)"', photos)),
      str((set(manifest_files) - set(photo_srcs)) -
          set(re.findall(r'"src": "([^"]+)"', photos)))[:200])
check("every <img> src is in the manifest or is a shoot thumbnail",
      set(photo_srcs) <= set(manifest_files) | thumb_srcs,
      str(set(photo_srcs) - set(manifest_files) - thumb_srcs)[:200])
missing = [s for s in manifest_files if not (SITE / s).is_file()]
check("all manifest files exist on disk", not missing, ", ".join(missing[:5]))
check(">= 150 photos total", len(manifest_files) >= 150,
      f"found {len(manifest_files)}")

# ---------- 11. reel: best-of-everything marquee, opens shoot albums ----------
photos_css = (SITE / "css" / "photos.css").read_text(encoding="utf-8")
photos_js = (SITE / "js" / "photos.js").read_text(encoding="utf-8")
check("reel markup present",
      'id="reel"' in photos and 'id="reelTrack"' in photos)
reel_items = re.findall(r'<button[^>]+class="reel-item"[^>]*>', photos)
visible_items = [b for b in reel_items if 'aria-hidden="true"' not in b]
check("reel shows one frame per shoot", len(visible_items) == len(manifest),
      f"found {len(visible_items)} vs {len(manifest)} shoots")
check("every shoot appears in the reel",
      {m["slug"] for m in manifest} ==
      set(re.findall(r'data-shoot="([^"]+)"', "".join(visible_items))))
check("reel has manual arrow controls",
      'id="reelPrev"' in photos and 'id="reelNext"' in photos
      and 'class="reel-arrow' in photos)
check("reel has drag-to-scroll",
      "pointerdown" in photos_js and "dragging" in photos_js)
check("reel auto-scrolls via JS",
      "requestAnimationFrame" in photos_js and "scrollLeft" in photos_js)
check("reel pauses on hover",
      "mouseenter" in photos_js and "hoverPause" in photos_js)
check("reel items open the shoot album, not Instagram",
      all('data-shoot=' in b for b in visible_items)
      and not any('instagram.com' in b for b in visible_items))
check("no Photography section heading on page",
      "<h1" not in photos and "Photography." not in photos)

# ---------- 11b. thumbnails: taller portrait aspect, face-aware ----------
check("shoot-card thumbnails use 3:4 portrait aspect",
      "aspect-ratio: 3 / 4" in photos_css)
missing_thumbs = [m["slug"] for m in manifest
                  if not (SITE / "assets" / "photos" / "thumbs" /
                          (m["slug"] + ".jpg")).is_file()]
check("every shoot has a thumbnail", not missing_thumbs,
      ", ".join(missing_thumbs[:5]))
card_imgs = re.findall(
    r'<button[^>]+class="shoot-card"[^>]*>.*?<img[^>]+src="([^"]+)"',
    photos, re.S)
check("shoot cards use thumbs/ directory",
      all(i.startswith("assets/photos/thumbs/") for i in card_imgs),
      str([i for i in card_imgs
           if not i.startswith("assets/photos/thumbs/")])[:150])
try:
    from PIL import Image as _PIL
    bad_ratio = []
    for m in manifest:
        p = SITE / "assets" / "photos" / "thumbs" / (m["slug"] + ".jpg")
        if p.is_file():
            w, h = _PIL.open(p).size
            if abs(w / h - 0.75) > 0.02:
                bad_ratio.append(m["slug"])
    check("thumbnails are 3:4 portrait", not bad_ratio, str(bad_ratio)[:150])
except ImportError:
    check("thumbnails are 3:4 portrait (PIL unavailable)", False,
          "PIL not installed")

# ---------- 12. lightbox ----------
for frag in ['id="lightbox"', 'role="dialog"', 'id="lbClose"',
             'id="lbPrev"', 'id="lbNext"', 'id="lbImg"', 'id="lbIg"']:
    check(f"lightbox has {frag}", frag in photos)
check("lightbox has explicit IG link, new tab",
      'View full post on Instagram' in photos
      and 'id="lbIg" href="" target="_blank" rel="noopener"' in photos)
check("lightbox keyboard support in photos.js",
      all(k in (SITE / "js" / "photos.js").read_text(encoding="utf-8")
          for k in ["Escape", "ArrowLeft", "ArrowRight"]))

# ---------- 13. IG links are secondary: no photo click goes to Instagram ----------
ig_anchors = re.findall(r'<a[^>]*href="(https://www\.instagram\.com/p/[^"]+)"[^>]*>',
                        photos)
ig_img_wraps = re.findall(
    r'<a[^>]*href="https://www\.instagram\.com/p/[^"]*"[^>]*>\s*<img', photos)
check("no photo <img> is wrapped in an Instagram link", not ig_img_wraps,
      str(ig_img_wraps)[:150])
check("static HTML has no per-photo IG links (JS renders them)",
      not ig_anchors, f"found {len(ig_anchors)} static IG anchors")
gallery_json = json.loads(re.search(
    r'<script type="application/json" id="galleryData">\s*(\{.*?\})\s*</script>',
    photos, re.S).group(1))
for m in manifest:
    check(f"IG post in gallery JSON for {m['slug']}",
          any(s["post"] == m["post_url"] for s in gallery_json["shoots"])
          or any(f["post"] == m["post_url"] for s in gallery_json["shoots"]
                 for f in s["files"]))

# ---------- 14. shoot cards open the lightbox directly ----------
for cat in ["fashion", "editorial", "portrait"]:
    check(f"no drawer markup: drawer-{cat}", f'id="drawer-{cat}"' not in photos)
cards = re.findall(r'<button[^>]+class="shoot-card"[^>]*data-shoot="([^"]+)"',
                   photos)
check("shoot card count matches manifest", len(cards) == len(manifest),
      f"{len(cards)} cards vs {len(manifest)} shoots")
check("every card maps to a manifest slug",
      set(cards) == {m["slug"] for m in manifest},
      str(set(cards) ^ {m["slug"] for m in manifest})[:150])
check("cards carry no drawer wiring",
      not any('aria-controls="drawer-' in c for c in
              re.findall(r'<button[^>]+class="shoot-card"[^>]*>', photos)))
check("lightbox has photo counter", 'id="lbCount"' in photos)
check("photos.js referenced", 'js/photos.js' in photos)
check("gallery JSON blob present", 'id="galleryData"' in photos)
check("photos.js has scoped lightbox (no drawer code)",
      'function openLb(list, i)' in photos_js and
      'shoot-drawer' not in photos_js and 'openDrawer' not in photos_js)

# ---------- 15. photos.html: hygiene ----------
pp = LinkImgParser()
pp.feed(photos)
# lbIg href is populated by photos.js at runtime
_js_anchors = 2  # lbIg + albumPopIg
check("photos: every <a> has a non-empty href (except JS-filled)",
      len(pp.bad_links) == _js_anchors, str(pp.bad_links))
# lbImg alt is populated by photos.js at runtime
lines = photos.splitlines()
check("photos: every <img> has alt text (except JS-filled lbImg)",
      all('id="lbImg"' in lines[ln - 1] for ln, _ in pp.bad_imgs),
      str(pp.bad_imgs))
check("no emojis in photos", not emoji_re.findall(photos))
check("no lorem in photos", "lorem" not in photos.lower())
check("no em-dashes in photos", "\u2014" not in photos)
photos_js = (SITE / "js" / "photos.js").read_text(encoding="utf-8")
for label, text in [("photos", photos), ("photos.css", (SITE / "css" / "photos.css").read_text(encoding="utf-8")), ("photos.js", photos_js)]:
    check(f"no em-dashes in {label}", "\u2014" not in text)
    check(f"no emojis in {label}", not emoji_re.findall(text))
check("photos.css has no gradients",
      "linear-gradient" not in (SITE / "css" / "photos.css").read_text(encoding="utf-8")
      and "radial-gradient" not in (SITE / "css" / "photos.css").read_text(encoding="utf-8"))
# near-black palette (Kevin, 2026-10-12): no navy blues on the photos page
photos_css = (SITE / "css" / "photos.css").read_text(encoding="utf-8")
check("photos.css has no navy blues",
      "#0a192f" not in photos_css.lower() and "#112240" not in photos_css.lower(),
      "found navy hex in photos.css")

# ---------- 12. resume.pdf / papers ----------
pdf = SITE / "assets" / "resume.pdf"
check("assets/resume.pdf is a PDF", pdf.is_file() and pdf.read_bytes()[:5] == b"%PDF-")
tp = SITE / "assets" / "papers" / "tightness-paradox.pdf"
check("assets/papers/tightness-paradox.pdf is a PDF", tp.is_file() and tp.read_bytes()[:5] == b"%PDF-")

print()
if failures:
    print(f"{len(failures)} check(s) FAILED")
    sys.exit(1)
print("ALL CHECKS PASSED")

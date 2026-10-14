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

# ---------- 3. neutral palette tokens (white text, white/gray accents) ----------
for token in ["#0c0c0e", "#17171b", "#ffffff",
              "JetBrains Mono", "--nav-height", "--green-tint"]:
    check(f"main.css uses token {token}", token in main_css)
check("main.css accent is white, not teal", "--green: #ffffff" in main_css)
check("main.css header is off-black, not navy",
      "rgba(12, 12, 14, 0.9)" in main_css)
for banned in ["#64ffda", "#57cbff", "#0a192f", "#112240", "#8892b0",
               "#ccd6f6", "#a8b2d1", "#e6f1ff", "#495670",
               "rgba(10, 25, 47", "rgba(100, 255, 218"]:
    check(f"main.css has no blue/teal {banned}", banned not in main_css)

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

# ---------- 7b. Lab / toy / card signals on index ----------
# The standalone snapshot strip and the Decisions prose are gone (Oct 14
# follow-up): the Predictor Hub signal lives inside the Predictor Hub card,
# the Stablecoin refresh note inside the Stablecoin card, and the Dot Foods
# tradeoff toy lives in the Lab section.
for frag in ['id="lab"', 'id="dotFoodsToy"',
             'class="card-signal"', 'id="palletCost"', 'id="laborRate"',
             'id="sortFee"', 'id="dropFee"', 'id="toyReset"',
             'id="toyTraditional"', 'id="toyOptimized"', 'id="toyVerdict"',
             'href="#lab"',
             'id="receipts"', 'class="receipts-grid"',
             'class="receipt-card"', 'href="#dotFoodsToy"',
             'class="receipt-bar-row"', 'class="receipt-table"']:
    check(f"index has {frag}", frag in index)
for phrase in ["The Lab", "Try the tradeoff",
               "Snapshot, verified Oct 14, 2026",
               "6 containers on Azure", "Refreshes weekly",
               "The same judgment that frames a shot",
               "Reset to practicum placeholders",
               "Simplified illustration. Directional, not validated.",
               "Receipts", "The numbers behind the calls.",
               "Synchrony Datathon: staffing forecasts for four client portfolios.",
               "Abandon error by model version",
               "Volume accuracy kept improving across the same versions.",
               "Shipped V16, not the most accurate model",
               "Abandon error is the metric that predicts customer pain.",
               "Busey Bank Treasury and ALM: separate real deposit growth from internal transfers.",
               "Proximity tiebreaker made it worse: 90% to 86%",
               "Confirmation numbers: identical on both legs, collision-proof key.",
               "MSBA capstone: denser truck loading for a food redistributor.",
               "Optimized costs more under placeholder costs",
               "Name the tradeoff, not the savings.",
               "Try the tradeoff in the Lab",
               "$1B+", "$0 across all five deposit categories",
               "2+ hrs down to 6-13 min per stage",
               "Placeholder costs, same as the toy."]:
    check(f"index content present: {phrase!r}", phrase in index)
check("standalone snapshot strip is gone",
      'class="live-strip"' not in index)
check("Decisions section is gone",
      'id="decisions"' not in index and 'href="#decisions"' not in index)
for headline in ["Ship the less accurate model",
                 "Fix the key, not the tiebreaker"]:
    check(f"Decisions prose gone: {headline!r}", headline not in index)
check("tradeoff toy lives inside the Lab section",
      index.find('id="lab"') < index.find('id="dotFoodsToy"')
      < index.find('id="contact"'))
check("Predictor Hub signal inside its card",
      index.find('Predictor Hub') < index.find('6 containers on Azure')
      < index.find('Synchrony Guardrail Engine'))
check("Stablecoin refresh note inside its card",
      index.find('Stablecoin Remittance Monitor')
      < index.find('Refreshes weekly')
      < index.find('FPL Scout'))
# ---------- 7c. Receipts section (Oct 14 follow-up, replaces Decisions) ----------
check("Receipts takes the Decisions slot (Lab < Receipts < Contact)",
      index.find('id="lab"') < index.find('id="receipts"')
      < index.find('id="contact"'))
check("Receipts heading is numbered 05",
      '<span class="num">05.</span> Receipts' in index)
check("Contact renumbered to 06 after Receipts",
      '06. What' in index)
check("Receipts has exactly three cards",
      index.count('class="receipt-card"') == 3,
      f"found {index.count('class=\"receipt-card\"')}")
check("Receipts has exactly three callout lists",
      index.count('class="receipt-callouts"') == 3)
for val in ["1.54%", "1.87%", "2.15%", "2.4%"]:
    check(f"Synchrony chart shows abandon error {val}",
          f'class="receipt-bar-value">{val}' in index)
check("Synchrony chart marks V16 as the pick",
      'class="receipt-bar pick" style="width: 64%"' in index)
check("Receipts has no Decisions prose paragraphs",
      'class="decision"' not in index
      and 'class="decisions-list"' not in index)
check("Receipts CSS has no decisions rules",
      ".decisions-list" not in main_css and ".decision " not in main_css)
for cls in [".receipts-grid", ".receipt-card", ".receipt-bars",
            ".receipt-bar-row", ".receipt-table", ".receipt-callouts"]:
    check(f"main.css defines {cls}", cls in main_css)
# Each project appears in exactly one card title (Work vs Lab split).
for name in ["Predictor Hub", "Algo Trade Hub",
             "Stablecoin Remittance Monitor", "Synchrony Guardrail Engine",
             "FPL Scout", "Tightness Paradox", "Data-Center Energy Analysis"]:
    titles = re.findall(r'class="card-title">(?:<a[^>]*>)?([^<]+)', index)
    check(f"project {name!r} appears in exactly one card title",
          titles.count(name) == 1, str(titles.count(name)))
# Dot Foods toy math: extract the constants from main.js and verify the
# defaults reproduce the notebook totals from the work-history profile.
toy_consts = {}
for key in ["P_TRAD", "P_OPT", "LOADS", "CASES", "LABOR_HOURS"]:
    mm = re.search(rf"var {key} = (\d+);", main_js)
    toy_consts[key] = int(mm.group(1)) if mm else None
check("toy constants present in main.js",
      all(v is not None for v in toy_consts.values()), str(toy_consts))
if all(v is not None for v in toy_consts.values()):
    trad = 12 * toy_consts["P_TRAD"] + 0.25 * toy_consts["CASES"]
    opt = (12 * toy_consts["P_OPT"] + 25 * toy_consts["LABOR_HOURS"]
           + 5 * toy_consts["LOADS"])
    check("toy defaults reproduce Traditional $8,457,877", trad == 8457877,
          f"got {trad}")
    check("toy defaults reproduce Optimized $11,507,953", opt == 11507953,
          f"got {opt}")
    check("Receipts Dot Foods table matches toy Traditional total",
          f"${int(trad):,}" in index, f"toy says {trad}")
    check("Receipts Dot Foods table matches toy Optimized total",
          f"${int(opt):,}" in index, f"toy says {opt}")
    check("Receipts Dot Foods difference matches toy gap",
          f"Optimized costs ${int(opt - trad):,} more" in index,
          f"toy gap is {opt - trad}")
check("no em-dashes in main.js", "\u2014" not in main_js)
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
check("manifest has 50 shoots after consolidation", len(manifest) == 50,
      f"found {len(manifest)}")
cats = {m["category"] for m in manifest}
check("manifest categories are exactly Fashion/Editorial/Portrait",
      cats == {"Fashion", "Editorial", "Portrait"}, str(cats))
check("manifest has 3 featured shoots",
      sum(1 for m in manifest if m.get("featured")) == 3)
# Consolidation (2026-10-14): the Whithering / Into the Abyss / Pensive
# trio merged into one autumn-series album; thin single-frame Editorial
# and Portrait albums consolidated into singles collections. The
# one-post-per-shoot rule is DROPPED: merged albums span several posts,
# and each frame keeps its own original Instagram post and title.
for slug, n in [("autumn-series", 3), ("editorial-singles", 18),
                ("portrait-singles", 4)]:
    m = next((x for x in manifest if x["slug"] == slug), None)
    check(f"merged album {slug} exists with {n} frames",
          m is not None and len(m["files"]) == n,
          f"found {len(m['files']) if m else 0}")
    check(f"merged album {slug} has no single post_url",
          m is not None and m.get("post_url") is None)
    check(f"merged album {slug} frames keep per-frame titles",
          m is not None and all("title" in f for f in m["files"]))
    check(f"merged album {slug} frames keep distinct original posts",
          m is not None and len({f["post"] for f in m["files"]}) > 1)
for gone in ["whithering", "into-the-abyss", "pensive",
             "earl-sweatshirt-doechii", "spring-life", "wash-drummer",
             "wash-skaters", "step-team", "2000s-party",
             "studio18-anniversary", "melanin-pt3", "searching", "mayhem",
             "serendipity-experiment", "terrestrial-discovery",
             "nouveau-american-gothic", "photo-vogue",
             "fort-greene-archives", "254-radio", "soho-incident",
             "2024-recap", "birthday-shots", "sun-basking", "kem-shoot",
             "man-in-the-mirror"]:
    check(f"consolidated-away shoot gone: {gone}",
          gone not in {m["slug"] for m in manifest})
# no post may lose photos vs the baseline (321 photos total);
# merges move photos between shoots, never drop them
BASELINE_TOTAL_PHOTOS = 321
total_photos = sum(len(m["files"]) for m in manifest)
check("no photos dropped vs baseline", total_photos == BASELINE_TOTAL_PHOTOS,
      f"found {total_photos}")
check("manifest files are {src, post} objects with optional per-frame title",
      all(isinstance(f, dict) and "src" in f and "post" in f
          and set(f) <= {"src", "post", "title"}
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
      "pointerenter" in photos_js and "pointerleave" in photos_js
      and "hoverPause" in photos_js)
check("reel resumes on touch end",
      "touchend" in photos_js and "touchcancel" in photos_js)
check("reel resumes when scrolled back into view",
      "IntersectionObserver" in photos_js and "inView" in photos_js)
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
check("lightbox IG link matches the displayed frame",
      "lbIg.href = it.post" in photos_js)
check("album popup hides IG link for multi-post albums",
      "popIg.style.display" in photos_js)
check("frames keep per-frame titles in photos.js",
      "f.title || s.title" in photos_js)

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
gallery_by_slug = {s["slug"]: s for s in gallery_json["shoots"]}
for m in manifest:
    g = gallery_by_slug.get(m["slug"])
    check(f"gallery JSON has shoot {m['slug']}", g is not None)
    if g is None:
        continue
    # Every frame's original post must survive in the gallery JSON;
    # shoot-level post is null for multi-post albums, else one of the
    # frame posts. Per-frame titles ride along for merged albums.
    check(f"gallery JSON keeps every frame post for {m['slug']}",
          [f["post"] for f in g["files"]] ==
          [f["post"] for f in m["files"]])
    check(f"gallery JSON shoot post valid for {m['slug']}",
          g["post"] is None or g["post"] in {f["post"] for f in m["files"]})
    check(f"gallery JSON keeps per-frame titles for {m['slug']}",
          [f.get("title") for f in g["files"]] ==
          [f.get("title") for f in m["files"]])

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
# plus the 2026-10-14 neutral direction: no blue/teal anywhere
photos_css = (SITE / "css" / "photos.css").read_text(encoding="utf-8")
check("photos.css has no navy blues",
      "#0a192f" not in photos_css.lower() and "#112240" not in photos_css.lower(),
      "found navy hex in photos.css")
for banned in ["#64ffda", "#57cbff", "#8892b0", "#ccd6f6", "#a8b2d1",
               "#e6f1ff", "#495670", "rgba(100, 255, 218"]:
    check(f"photos.css has no blue/teal {banned}", banned not in photos_css)

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

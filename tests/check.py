#!/usr/bin/env python3
"""TDD checks for Kevin Sigey's portfolio site (~/workspace/portfolio-site/site/).

Landing page rebuilt in Brittany Chiang v4 design language (static, flat colors).
photos.html keeps the legacy theme system untouched.
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
for rel in ["index.html", "photos.html", "css/main.css", "js/main.js",
            "assets/resume.pdf"]:
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
for token in ["#0a192f", "#112240", "#8892b0", "#ccd6f6", "#64ffda",
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
               "A quant who communicates well",
               "01.", "About Me", "02.", "Where I",
               "03.", "Some Things I",
               "04.", "Get In Touch",
               "sigeykevin@gmail.com",
               "linkedin.com/in/kevin-sigey-72a5501b5",
               "Predictor Hub", "Algo Trade Hub",
               "Stablecoin Remittance Monitor",
               "Status: Live", "In active rebuild", "Pipeline running",
               "github.com/Kevocado/predictor-hub",
               "github.com/Kevocado/algo-trade-hub-prod",
               "github.com/Kevocado/Stable-Coin-Analysis",
               "40-160-91-131.sslip.io",
               "assets/resume.pdf",
               "Busey Bank", "Illinois Business Consulting",
               "Tandon Consulting Club", "Dot Foods",
               "150 to 450"]:
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

# ---------- 8. photos.html untouched checks ----------
for css in ["css/base.css", "css/theme-editorial.css",
            "css/theme-darkroom.css", "css/theme-terminal.css"]:
    check(f"photos references {css}", css in photos)
check("photos references js/theme.js", "js/theme.js" in photos)
check("photos sets default data-theme=darkroom", 'data-theme="darkroom"' in photos)
check("photos has 20 frames", photos.count("<img") == 20,
      f"found {photos.count('<img')}")
photo_srcs = re.findall(r'<img[^>]+src="([^"]+)"', photos)
missing = [s for s in photo_srcs if not (SITE / s).is_file()]
check("all photo srcs resolve to files", not missing, ", ".join(missing[:5]))
check("every photo links to its Instagram post",
      photos.count('class="photo-link"') == len(photo_srcs))
manifest = json.loads((SITE / "assets" / "photos" / "manifest.json")
                      .read_text(encoding="utf-8"))
check("manifest has 20 entries", len(manifest) == 20)

# ---------- 9. resume.pdf ----------
pdf = SITE / "assets" / "resume.pdf"
check("assets/resume.pdf is a PDF", pdf.is_file() and pdf.read_bytes()[:5] == b"%PDF-")

print()
if failures:
    print(f"{len(failures)} check(s) FAILED")
    sys.exit(1)
print("ALL CHECKS PASSED")

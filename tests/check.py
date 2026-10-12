#!/usr/bin/env python3
"""TDD checks for Kevin Sigey's portfolio site (~/workspace/portfolio-site/site/).

Red phase: files don't exist yet -> every check fails.
Green phase: build the site until `python3 tests/check.py` exits 0.
Covers both index.html and photos.html.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
failures = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


PAGES = ["index.html", "photos.html"]


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


# ---------- 1. all files exist ----------
expected = [
    "index.html",
    "photos.html",
    "css/base.css",
    "css/theme-editorial.css",
    "css/theme-darkroom.css",
    "css/theme-terminal.css",
    "js/theme.js",
    "assets/resume.pdf",
]
for rel in expected:
    check(f"file exists: {rel}", (SITE / rel).is_file())

pages = {}
for page in PAGES:
    p = SITE / page
    pages[page] = p.read_text(encoding="utf-8") if p.is_file() else ""

for page, html in pages.items():
    # ---------- 2. viewport meta ----------
    check(
        f"{page} has viewport meta",
        bool(re.search(r'<meta[^>]+name=["\']viewport["\']', html, re.I)),
    )
    # ---------- 3. asset references ----------
    for css in ["css/base.css", "css/theme-editorial.css",
                "css/theme-darkroom.css", "css/theme-terminal.css"]:
        check(f"{page} references {css}", css in html)
    check(f"{page} references js/theme.js", "js/theme.js" in html)
    check(f"{page} sets default data-theme=editorial",
          'data-theme="editorial"' in html)
    # ---------- 4. theme switcher present ----------
    check(f"{page} has theme switcher buttons",
          all(f'data-set-theme="{t}"' in html
              for t in ["editorial", "darkroom", "terminal"]))

    # ---------- 5. links and images ----------
    lp = LinkImgParser()
    lp.feed(html)
    check(f"{page}: every <a> has a non-empty href", not lp.bad_links,
          f"empty href at {lp.bad_links[:3]}")
    check(f"{page}: every <img> has alt text", not lp.bad_imgs,
          f"missing alt at {lp.bad_imgs[:3]}")

    # ---------- 6. no emojis ----------
    emoji_re = re.compile(
        r"[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF"
        r"\u2600-\u27BF\u2B00-\u2BFF]"
    )
    emojis = emoji_re.findall(html)
    check(f"no emojis in {page}", not emojis, repr(emojis[:5]))

# ---------- 7. photos.html: images resolve to real files ----------
photos_html = pages["photos.html"]
lp = LinkImgParser()
lp.feed(photos_html)
photo_srcs = [s for s in lp.imgs if s.startswith("assets/photos/")]
check("photos.html has >= 12 photos", len(photo_srcs) >= 12,
      f"found {len(photo_srcs)}")
missing = [s for s in photo_srcs if not (SITE / s).is_file()]
check("all photo srcs resolve to files", not missing, ", ".join(missing[:5]))
non_jpeg = []
for s in photo_srcs:
    p = SITE / s
    if p.is_file() and p.read_bytes()[:2] != b"\xff\xd8":
        non_jpeg.append(s)
check("all photos are valid JPEGs", not non_jpeg, ", ".join(non_jpeg[:5]))

# ---------- 8. theme CSS: balanced braces + scope selector ----------
for name in ["editorial", "darkroom", "terminal"]:
    p = SITE / "css" / f"theme-{name}.css"
    css = p.read_text(encoding="utf-8") if p.is_file() else ""
    check(
        f"theme-{name}.css balanced braces",
        css.count("{") == css.count("}") and css.count("{") > 0,
        f"open={css.count('{')} close={css.count('}')}",
    )
    check(
        f"theme-{name}.css contains data-theme scope selector",
        f'html[data-theme="{name}"]' in css,
    )
    check(f"theme-{name}.css styles .repo links", ".repo" in css)
    check(f"theme-{name}.css styles gallery", ".photo" in css and ".series" in css)

# ---------- 9. theme.js references all three themes ----------
js = (SITE / "js" / "theme.js").read_text(encoding="utf-8") \
    if (SITE / "js" / "theme.js").is_file() else ""
for name in ["editorial", "darkroom", "terminal"]:
    check(f"theme.js references theme '{name}'", name in js)
check("theme.js persists choice (localStorage)", "localStorage" in js)

# ---------- 10. base.css is theme-agnostic: no typefaces, no colors ----------
base = (SITE / "css" / "base.css").read_text(encoding="utf-8") \
    if (SITE / "css" / "base.css").is_file() else ""
check("base.css has no font-family", "font-family" not in base.lower())
check("base.css has no hex colors",
      not re.search(r"#[0-9a-fA-F]{3,8}\b", base))
check("base.css has no rgb()/hsl() colors",
      not re.search(r"(rgb|hsl)a?\s*\(", base, re.I))
check("base.css has gallery layout", ".photo-grid" in base)
check("base.css has .repo layout", ".entry .repo" in base)

# ---------- 11. no lorem ipsum anywhere ----------
site_text_files = []
for ext in (".html", ".css", ".js"):
    site_text_files.extend(SITE.rglob(f"*{ext}"))
lorem_hits = [str(f) for f in site_text_files
              if re.search(r"lorem", f.read_text(encoding="utf-8"), re.I)]
check("no lorem ipsum anywhere", not lorem_hits, ", ".join(lorem_hits))

# ---------- 12. resume.pdf is a real PDF ----------
pdf = SITE / "assets" / "resume.pdf"
is_pdf = pdf.is_file() and pdf.read_bytes()[:5] == b"%PDF-"
check("assets/resume.pdf exists and is a PDF (magic bytes %PDF)", is_pdf)
check("resume card links to assets/resume.pdf",
      "assets/resume.pdf" in pages["index.html"])

# ---------- 13. key content present (index) ----------
html = pages["index.html"]
for phrase in ["quant who communicates well",
               "sigeykevin@gmail.com",
               "linkedin.com/in/kevin-sigey-72a5501b5",
               "Predictor Hub", "Algo Trade Hub",
               "Stablecoin Remittance Monitor",
               "live in production", "in active rebuild",
               "pipeline running",
               "github.com/Kevocado/predictor-hub",
               "github.com/Kevocado/algo-trade-hub-prod",
               "github.com/Kevocado/Stable-Coin-Analysis",
               "40-160-91-131.sslip.io",
               'href="photos.html"']:
    check(f"index content present: {phrase!r}", phrase.lower() in html.lower())

# ---------- 14. key content present (photos) ----------
for phrase in ["Photography", "17 frames", "Fashion", "Portraits",
               "Editorial", "Events", "Beach", "City",
               "All photographs by Kevin Sigey"]:
    check(f"photos content present: {phrase!r}",
          phrase.lower() in photos_html.lower())

# ---------- 15. deploy pipeline files ----------
wf = SITE / ".github" / "workflows" / "deploy.yml"
check("deploy workflow exists", wf.is_file())
wf_text = wf.read_text(encoding="utf-8") if wf.is_file() else ""
dockerfile = (SITE / "Dockerfile").read_text(encoding="utf-8") \
    if (SITE / "Dockerfile").is_file() else ""
caddyfile = (SITE / "Caddyfile").read_text(encoding="utf-8") \
    if (SITE / "Caddyfile").is_file() else ""
for phrase in ["ghcr.io/kevocado/portfolio", "secrets.GHCR_PAT",
               "deploy portfolio", "secrets.VPS_SSH_KEY", "vars.VPS_HOST"]:
    check(f"deploy workflow references {phrase!r}", phrase in wf_text)
check("Dockerfile is caddy-based", "caddy:2-alpine" in dockerfile)
check("Dockerfile copies both pages",
      "index.html" in dockerfile and "photos.html" in dockerfile)
check("Caddyfile serves static root", "file_server" in caddyfile)

print()
if failures:
    print(f"{len(failures)} check(s) FAILED")
    sys.exit(1)
print("ALL CHECKS PASSED")

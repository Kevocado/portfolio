# Kevin Sigey — Portfolio

Personal portfolio site: a quant who communicates well. Work, Lab (agentic
development), and Photography.

## Structure

- `index.html` — landing page (Work index, Agentic Development ledger, contact)
- `photos.html` — photography gallery (17 frames, 2023–2025)
- `css/base.css` — layout only (no colors, no typefaces)
- `css/theme-*.css` — three interchangeable visual editions, switched via the
  footer Edition switcher (`editorial` default, `darkroom`, `terminal`)
- `js/theme.js` — edition switcher, persisted in localStorage
- `assets/photos/` — Kevin's real photography, curated from his Instagram
- `assets/resume.pdf` — current resume
- `tests/check.py` — TDD suite; `python3 tests/check.py` must pass

## Preview locally

```sh
python3 -m http.server 8931
# http://localhost:8931
```

## Deploy

Push to `main` → GitHub Actions builds the Caddy image, pushes to
`ghcr.io/kevocado/portfolio`, and the `vps` job deploys it on Kevin's VPS.
Required repo secrets/variables: `GHCR_PAT`, `VPS_SSH_KEY`,
`VPS_KNOWN_HOSTS` (secrets) and `VPS_HOST` (variable) — same values as the
other site repos.

# www.ocf.berkeley.edu/~rkriger

Roni Kriger's portfolio site, hosted by the Open Computing Facility at UC Berkeley.

- `public/` is exactly what goes in `~/public_html` on OCF. Plain HTML, CSS and a little JavaScript, no build step needed to serve it.
- `tools/` holds the source and the scripts that produce `public/`.

## Deploy to OCF

Log in to OCF:

```bash
ssh rkriger@ssh.ocf.berkeley.edu
```

Then back up what's there and unpack the site from this branch:

```bash
mkdir -p ~/site-backup && cp -a ~/public_html/. ~/site-backup/ && curl -fsSL https://github.com/ronikriger/portfolio-/archive/refs/heads/ocf-site.tar.gz | tar -xz --strip-components=2 -C ~/public_html --wildcards '*/public/*' && ls ~/public_html
```

The old site stays in `~/site-backup`. Running the same command again later picks up any new changes.

## Edit the site

1. Change `tools/template.html` (all text, styles and the globe script live there).
2. Rebuild: `python3 tools/build.py` writes `public/index.html`.
3. If you changed the résumé text in `tools/resume.html`, or want a fresh link-preview image, run `node tools/render.js` (needs Playwright).
4. Commit, push, and run the deploy command above.

To use your own résumé file instead, replace `public/resume.pdf`.

## Notes

- The globe's land shapes come from Natural Earth 1:110m via `world-atlas`, rasterized to a 1° mask by `tools/landmask.py`.
- Orbit screenshots and icon are from its App Store listing.
- No analytics, cookies or trackers.

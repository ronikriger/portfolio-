# www.ocf.berkeley.edu/~rkriger

Roni Kriger's portfolio site, hosted by the Open Computing Facility at UC Berkeley.

- `public/` is exactly what goes in `~/public_html` on OCF (English at `/`, Hebrew at `/he/`): plain HTML, CSS and a little JavaScript, self-hosted fonts and WebP images, no third-party requests.
- `tools/` holds the source and the scripts that produce `public/`.
- `deploy.sh` installs `public/` on OCF, keeps a dated backup, and checks the site still loads.

## Deploy to OCF

Open the browser terminal at https://ssh.ocf.berkeley.edu/ (or run `ssh rkriger@ssh.ocf.berkeley.edu`), log in, and paste:

```bash
curl -fsSL https://raw.githubusercontent.com/ronikriger/portfolio-/ocf-site/deploy.sh | sh
```

It downloads this branch, backs up the current site to `~/site-backups/<date-time>/`, installs the new files, and checks https://www.ocf.berkeley.edu/~rkriger/ answers. If OCF rejects anything in `.htaccess`, it falls back to basic settings by itself. GitHub can take up to five minutes to serve a just-pushed `deploy.sh`.

## Edit the site

1. Change `tools/template.html`. All text, styles and the globe script live there.
2. Run `python3 tools/build.py` to rebuild `public/index.html`, `404.html`, `sitemap.xml`, `robots.txt` and `.htaccess`. It adds `?v=<hash>` to asset links so browsers can cache them safely.
3. Run `node tools/render.js` (needs Playwright) if you changed `tools/resume.html` or want fresh preview images (`og.jpg`, icons).
4. New screenshots go in `tools/src-images/`. Then run `python3 tools/images.py`.
5. Commit, push, and run the deploy command above.

To use your own résumé file instead, replace `public/resume.pdf`.

## The Hebrew page

`public/he/index.html` is built from the same template. `tools/i18n/he.json` lists exact English snippets from `tools/template.html` with their Hebrew replacements; the build applies them longest first, switches the page to right-to-left, adds the Hebrew fonts (Heebo, Frank Ruhl Libre) and keeps Hebrew prefixes like ב- on the same line as the word after them.

If you change English text in the template, the build stops and lists any Hebrew entry whose English no longer matches, so the Hebrew page never silently falls out of date. Update that entry in `he.json` and rebuild. `python3 tools/i18n_extract.py public/he/index.html` lists every string on the Hebrew page, which helps spot anything left in English.

## Notes

- Fonts: Archivo, Geist, Geist Mono and Newsreader (SIL Open Font License), trimmed to Latin by `tools/fetch_fonts.py` and `tools/trim_fonts.py`.
- The globe's land shapes come from Natural Earth 1:110m via `world-atlas`, rasterized to a 1° mask by `tools/landmask.py`.
- Orbit screenshots and icon are from its App Store listing.
- No analytics, cookies or trackers.

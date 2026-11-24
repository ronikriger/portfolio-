"""Build the site.

  python3 tools/build.py              # writes public/
  python3 tools/build.py --preview D  # also writes a fragment copy for an Artifact preview in D

public/ is exactly what deploy.sh copies into ~/public_html on OCF.
"""
import datetime
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
PUBLIC = ROOT / "public"
SITE_URL = "https://www.ocf.berkeley.edu/~rkriger/"

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#0B1530"/>
  <circle cx="32" cy="33" r="17" fill="none" stroke="#2A3A66" stroke-width="2"/>
  <path d="M11 44C19 26 35 17 53 20" fill="none" stroke="#FDB515" stroke-width="4.5" stroke-linecap="round"/>
  <circle cx="52.5" cy="20" r="5" fill="#FDB515"/>
</svg>
"""

# Apache settings for ~/public_html. deploy.sh checks the site still loads after installing
# this, and falls back to tools/htaccess-basic (then to none) if OCF rejects a directive.
HTACCESS = """# Server settings for www.ocf.berkeley.edu/~rkriger (Apache, behind OCF's nginx).
AddDefaultCharset utf-8
ErrorDocument 404 /~rkriger/404.html
AddType font/woff2 .woff2
AddType image/webp .webp

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresDefault "access plus 1 hour"
  ExpiresByType text/html "access plus 0 seconds"
  ExpiresByType font/woff2 "access plus 1 year"
  ExpiresByType image/webp "access plus 1 year"
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType image/jpeg "access plus 1 month"
  ExpiresByType image/svg+xml "access plus 1 month"
  ExpiresByType application/pdf "access plus 1 week"
</IfModule>

<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
"""
HTACCESS_BASIC = """# Minimal server settings, used if OCF rejects the full set.
AddDefaultCharset utf-8
ErrorDocument 404 /~rkriger/404.html
"""

# Asset paths that get a ?v=<content hash> so browsers can cache them for a long time.
ASSET_RE = re.compile(r"(?<![\w/~.-])((?:fonts|assets)/[\w.-]+\.(?:woff2|webp|png|jpg|svg)|resume\.pdf|favicon\.svg|favicon-32\.png|apple-touch-icon\.png)(?![\w?])")


def version_assets(html: str) -> str:
    cache = {}

    def sub(m):
        rel = m.group(1)
        f = PUBLIC / rel
        if not f.exists():
            return rel
        if rel not in cache:
            cache[rel] = hashlib.sha1(f.read_bytes()).hexdigest()[:8]
        return f"{rel}?v={cache[rel]}"

    return ASSET_RE.sub(sub, html)


def main() -> None:
    now = datetime.date.today()
    mask = (TOOLS / "landmask.b64").read_text().strip()
    fonts_css = (TOOLS / "fonts.css").read_text().strip()
    html = (TOOLS / "template.html").read_text()
    html = html.replace("%%MASK%%", mask)
    html = html.replace("%%UPDATED%%", now.strftime("%B %Y"))
    html = html.replace("/*FONTS*/", fonts_css)
    assert "%%" not in html, "unfilled placeholder"

    PUBLIC.mkdir(exist_ok=True)
    (PUBLIC / "favicon.svg").write_text(FAVICON)
    live = version_assets(html)
    (PUBLIC / "index.html").write_text(live)

    page404 = (TOOLS / "404.html").read_text().replace("/*FONTS*/", fonts_css.replace("url(fonts/", "url(/~rkriger/fonts/"))
    (PUBLIC / "404.html").write_text(page404)
    (PUBLIC / ".htaccess").write_text(HTACCESS)
    (TOOLS / "htaccess-basic").write_text(HTACCESS_BASIC)
    (PUBLIC / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n")
    (PUBLIC / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{SITE_URL}</loc><lastmod>{now.isoformat()}</lastmod></url>\n"
        f"  <url><loc>{SITE_URL}resume.pdf</loc><lastmod>{now.isoformat()}</lastmod></url>\n"
        "</urlset>\n"
    )
    print("wrote", PUBLIC / "index.html", f"{len(live) / 1024:.1f} KB")

    if "--preview" in sys.argv:
        out = pathlib.Path(sys.argv[sys.argv.index("--preview") + 1])
        out.mkdir(parents=True, exist_ok=True)
        frag = html
        # Artifact pages may load fonts only from Google Fonts, so the preview uses those.
        frag = re.sub(r"<!--FONTLINKS-->.*?<!--/FONTLINKS-->", (
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,600..900'
            '&family=Geist:wght@400..700&family=Geist+Mono:wght@400..600'
            '&family=Newsreader:ital,opsz,wght@0,6..72,300..500;1,6..72,300..500&display=swap">'), frag, flags=re.S)
        frag = frag.replace(fonts_css, "")
        # The Artifact host supplies doctype, html, head, body, charset and viewport.
        frag = re.sub(r"<!doctype html>\s*", "", frag, flags=re.I)
        frag = re.sub(r"</?html[^>]*>\s*", "", frag)
        frag = re.sub(r"</?head>\s*", "", frag)
        frag = re.sub(r"</?body>\s*", "", frag)
        frag = re.sub(r'<meta charset="utf-8">\s*', "", frag)
        frag = re.sub(r'<meta name="viewport"[^>]*>\s*', "", frag)
        (out / "index.html").write_text(frag)
        print("wrote", out / "index.html")


if __name__ == "__main__":
    main()

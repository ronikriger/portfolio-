"""Build the site.

  python3 tools/build.py

Writes public/index.html (the page OCF serves) from tools/template.html,
inlining the globe's land mask, plus favicon.svg and robots.txt.
Pass --preview DIR to also write a fragment copy for an Artifact preview.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
PUBLIC = ROOT / "public"

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#0B1530"/>
  <circle cx="32" cy="33" r="17" fill="none" stroke="#2A3A66" stroke-width="2"/>
  <path d="M11 44C19 26 35 17 53 20" fill="none" stroke="#FDB515" stroke-width="4.5" stroke-linecap="round"/>
  <circle cx="52.5" cy="20" r="5" fill="#FDB515"/>
</svg>
"""

ROBOTS = "User-agent: *\nAllow: /\n"


def main() -> None:
    mask = (TOOLS / "landmask.b64").read_text().strip()
    html = (TOOLS / "template.html").read_text().replace("%%MASK%%", mask)
    assert "%%" not in html, "unfilled placeholder"
    PUBLIC.mkdir(exist_ok=True)
    (PUBLIC / "index.html").write_text(html)
    (PUBLIC / "favicon.svg").write_text(FAVICON)
    (PUBLIC / "robots.txt").write_text(ROBOTS)
    print("wrote", PUBLIC / "index.html", f"{len(html) / 1024:.1f} KB")

    if "--preview" in sys.argv:
        out = pathlib.Path(sys.argv[sys.argv.index("--preview") + 1])
        out.mkdir(parents=True, exist_ok=True)
        frag = html
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

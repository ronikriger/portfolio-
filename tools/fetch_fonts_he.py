"""Download the Hebrew woff2 subsets used by the Hebrew page (public/he/).
  python3 tools/fetch_fonts_he.py
Heebo carries Hebrew text for body, headings and labels; Frank Ruhl Libre is the
Hebrew serif paired with Newsreader in the Orbit panel. Writes tools/fonts-he.css."""
import re, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "fonts"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
FAMILIES = [("heebo", "Heebo:wght@400..800"), ("frank-ruhl-libre", "Frank+Ruhl+Libre:wght@300..500")]
def get(url, binary=False):
    r = subprocess.run(["curl", "-fsSL", "-A", UA, url], capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode()
css_out = []
for slug, spec in FAMILIES:
    css = get(f"https://fonts.googleapis.com/css2?family={spec}&display=swap")
    for m in re.finditer(r"/\* (\S+) \*/\s*@font-face \{(.*?)\}", css, re.S):
        if m.group(1) != "hebrew":
            continue
        body = m.group(2)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
        name = f"{slug}-hebrew.woff2"
        (OUT / name).write_bytes(get(url, binary=True))
        body = re.sub(r"\s+", " ", body.replace(url, f"fonts/{name}")).strip()
        css_out.append("@font-face { " + body + " }")
        print(f"{name}: {(OUT / name).stat().st_size / 1024:.0f} KB")
(ROOT / "tools" / "fonts-he.css").write_text("\n".join(css_out) + "\n")

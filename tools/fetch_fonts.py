"""Download the latin woff2 subsets of the site's Google Fonts so OCF serves them itself.
  python3 tools/fetch_fonts.py
Writes public/fonts/*.woff2 and prints the @font-face CSS to paste into tools/template.html."""
import re, subprocess, pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent / "public" / "fonts"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
FAMILIES = [
    ("archivo", "Archivo:wdth,wght@100..125,500..900"),
    ("geist", "Geist:wght@400..700"),
    ("geist-mono", "Geist+Mono:wght@400..600"),
    ("newsreader", "Newsreader:ital,opsz,wght@0,6..72,300..500;1,6..72,300..500"),
]
def get(url, binary=False):
    return subprocess.run(["curl", "-fsSL", "-A", UA, url], capture_output=True, check=True).stdout if binary else \
        subprocess.run(["curl", "-fsSL", "-A", UA, url], capture_output=True, check=True, text=True).stdout
css_out = []
for slug, spec in FAMILIES:
    css = get(f"https://fonts.googleapis.com/css2?family={spec}&display=swap")
    for m in re.finditer(r"/\* (\S+) \*/\s*@font-face \{(.*?)\}", css, re.S):
        subset, body = m.group(1), m.group(2)
        if subset != "latin":
            continue
        style = re.search(r"font-style: (\w+)", body).group(1)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
        name = f"{slug}{'-italic' if style == 'italic' else ''}.woff2"
        (OUT / name).write_bytes(get(url, binary=True))
        body = body.replace(url, f"fonts/{name}")
        body = re.sub(r"\s+", " ", body).strip()
        css_out.append("@font-face { " + body + " }")
        print(f"{name}: {(OUT / name).stat().st_size / 1024:.0f} KB")
pathlib.Path(__file__).with_name("fonts.css").write_text("\n".join(css_out) + "\n")
print(open(pathlib.Path(__file__).with_name("fonts.css")).read())

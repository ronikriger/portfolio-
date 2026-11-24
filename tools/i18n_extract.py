"""List every translatable string in tools/template.html: visible text, alt/aria-label/title,
and the head's title and descriptions. Used to check the Hebrew translation covers everything.
  python3 tools/i18n_extract.py [page.html]"""
import sys, re, pathlib
from html.parser import HTMLParser
SKIP = {"script", "style"}
ATTRS = {"alt", "aria-label", "title", "placeholder"}
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.stack = []; self.out = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in ("br", "img", "meta", "link", "input", "source", "path", "circle", "rect"): self.stack.append(tag)
        for k in ATTRS:
            if a.get(k): self.out.append(("@" + k, a[k]))
        if tag == "meta" and a.get("content") and (a.get("name") in ("description", "twitter:title", "twitter:description") or (a.get("property") or "") in ("og:title", "og:description", "og:image:alt")):
            self.out.append(("@meta", a["content"]))
    def handle_endtag(self, tag):
        while self.stack and self.stack.pop() != tag: pass
    def handle_data(self, d):
        if any(t in SKIP for t in self.stack): return
        t = " ".join(d.split())
        if t and re.search(r"[A-Za-z]{2,}", t): self.out.append(("text", t))
src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).with_name("template.html")).read_text()
p = P(); p.feed(src)
seen = set()
for kind, t in p.out:
    if (kind, t) in seen: continue
    seen.add((kind, t)); print(f"{kind}\t{t}")

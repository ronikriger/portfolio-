"""Shrink the downloaded fonts: limit variation axes to the ranges the site uses
and keep only Latin text characters. Run after fetch_fonts.py.
  python3 tools/trim_fonts.py"""
import pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

FONTS = pathlib.Path(__file__).resolve().parent.parent / "public" / "fonts"
LATIN = "U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+2013-2014,U+2018-201E,U+2022,U+2026,U+2032-2033,U+20AC,U+2122,U+2190-2193,U+2212,U+2264-2265"
PLAN = {
    "archivo.woff2": {"wdth": (100, 125), "wght": (600, 900)},
    "geist.woff2": None,
    "geist-mono.woff2": None,
    "newsreader.woff2": {"opsz": 48, "wght": (300, 500)},
    "newsreader-italic.woff2": {"opsz": 24, "wght": (300, 500)},
}
for name, axes in PLAN.items():
    path = FONTS / name
    before = path.stat().st_size
    font = TTFont(path, lazy=False)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=subset.parse_unicodes(LATIN))
    sub.subset(font)
    if axes and "fvar" in font:
        font = instancer.instantiateVariableFont(font, axes)
    font.flavor = "woff2"
    font.save(path)
    print(f"{name}: {before / 1024:.0f} KB -> {path.stat().st_size / 1024:.0f} KB")

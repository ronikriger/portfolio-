"""Make web-sized WebP images in public/assets from the originals in tools/src-images.
  python3 tools/images.py"""
import pathlib
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "tools" / "src-images", ROOT / "public" / "assets"
OUT.mkdir(parents=True, exist_ok=True)
def save(im, name, width, q=80):
    h = round(im.height * width / im.width)
    im.convert("RGB").resize((width, h), Image.LANCZOS).save(OUT / name, "WEBP", quality=q, method=6)
    print(f"{name}: {width}x{h}, {(OUT / name).stat().st_size / 1024:.1f} KB")
for shot in ["orbit-globe", "orbit-today", "orbit-trail", "orbit-horizon"]:
    im = Image.open(SRC / f"{shot}.jpg")
    save(im, f"{shot}-300.webp", 300)
    save(im, f"{shot}-450.webp", 450, q=79)
    save(im, f"{shot}-600.webp", 600, q=78)
save(Image.open(SRC / "orbit-icon.png"), "orbit-icon.webp", 112, q=88)
save(Image.open(SRC / "limud.png"), "limud.webp", 480, q=82)

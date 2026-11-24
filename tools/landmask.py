# Decode world-atlas land-110m TopoJSON, rasterize to a 1-degree equirectangular
# land mask (360x180), and emit it as base64 for the globe.
import json, sys, base64
from PIL import Image, ImageDraw
topo = json.load(open(sys.argv[1]))
sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]
arcs = []
for arc in topo["arcs"]:
    x = y = 0; pts = []
    for dx, dy in arc:
        x += dx; y += dy
        pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)
def ring(ix):
    out = []
    for i in ix:
        pts = arcs[i] if i >= 0 else arcs[~i][::-1]
        out.extend(pts if not out else pts[1:])
    return out
S = 8  # supersample
W, H = 360 * S, 180 * S
img = Image.new("L", (W, H), 0); d = ImageDraw.Draw(img)
def xy(p): return ((p[0] + 180) * S, (90 - p[1]) * S)
geoms = topo["objects"]["land"]["geometries"]
for g in geoms:
    polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
    for poly in polys:
        for k, r in enumerate(poly):
            raw = ring(r)
            # unwrap longitudes so rings crossing the antimeridian stay continuous
            un = [raw[0]]
            for lon, lat in raw[1:]:
                plon = un[-1][0]
                while lon - plon > 180: lon -= 360
                while lon - plon < -180: lon += 360
                un.append((lon, lat))
            span = max(p[0] for p in un) - min(p[0] for p in un)
            if span >= 359:  # circumpolar ring (Antarctica): close it through the pole
                pole = -90 if sum(p[1] for p in un) < 0 else 90
                un = un + [(un[-1][0], pole), (un[0][0], pole)]
            for off in (-360, 0, 360):
                pts = [xy((lon + off, lat)) for lon, lat in un]
                if len(pts) > 2: d.polygon(pts, fill=255 if k == 0 else 0)
small = img.resize((360, 180), Image.BOX)
bits = bytearray((360 * 180 + 7) // 8)
land = 0
for yy in range(180):
    for xx in range(360):
        if small.getpixel((xx, yy)) > 100:
            i = yy * 360 + xx; bits[i >> 3] |= 1 << (i & 7); land += 1
small.point(lambda v: 255 if v > 100 else 0).save(sys.argv[2])
open(sys.argv[3], "w").write(base64.b64encode(bytes(bits)).decode())
print("land cells:", land, "of", 360 * 180, f"({land/648:.1f}%)")

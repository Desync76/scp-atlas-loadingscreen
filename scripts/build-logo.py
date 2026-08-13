"""
Vectorise le logo PNG en SVG propre et l'injecte dans index.html.

    python scripts/build-logo.py [chemin/vers/logo.png]

- recentre le logo dans un viewBox 1000x1000
- decoupe le tracé en 8 pieces nommees (necessaire pour l'animation)
- calcule pour chaque piece sa direction d'eclatement (--dx / --dy)
- ecrit assets/img/logo.svg (version statique autonome)
- remplace le bloc entre <!-- logo:start --> et <!-- logo:end --> dans index.html

A relancer uniquement si le logo source change.
Dependances : opencv-python, numpy, pillow
"""
import sys, os, math, json
import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets", "img", "logo_source.png")

VB, MARGIN, EPS = 1000.0, 24.0, 1.4

# Ordre d'assemblage a l'ecran (pilote le decalage --i de l'animation).
ORDER = ["ring", "bar-l", "bar-r", "arc-b", "chevron-t", "tri-tl", "tri-tr", "tri-b"]


def classify(bx, by, bw, bh, cx, cy):
    """Nomme une piece d'apres sa geometrie, pas d'apres l'ordre de tracage."""
    mx, my = bx + bw / 2, by + bh / 2
    if bw > 3 * bh:                      # large et plat, sous le centre
        return "arc-b"
    if bh > 2 * bw:                      # haut et etroit : montant lateral
        return "bar-l" if mx < cx else "bar-r"
    if my > cy:                          # sous le centre
        return "tri-b"
    if bw > 0.2 * (2 * cx):              # large, au-dessus : chevron central
        return "chevron-t"
    return "tri-tl" if mx < cx else "tri-tr"


def main():
    im = Image.open(SRC).convert("RGBA")
    a = np.array(im)
    mask = (((a[:, :, 3] > 128) & (a[:, :, :3].max(axis=2) > 100)).astype(np.uint8)) * 255

    cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    hier = hier[0]
    ext = [i for i in range(len(cnts)) if hier[i][3] == -1]

    ys, xs = np.where(mask > 0)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    w, h = x1 - x0, y1 - y0
    scale = (VB - 2 * MARGIN) / max(w, h)
    ox = (VB - w * scale) / 2 - x0 * scale
    oy = (VB - h * scale) / 2 - y0 * scale

    def tx(p):
        return (p[0] * scale + ox, p[1] * scale + oy)

    # L'anneau est la plus grande aire ; les autres sont nommes par geometrie.
    areas = {i: cv2.contourArea(cnts[i]) for i in ext}
    ring = max(areas, key=areas.get)

    src_cx, src_cy = (x0 + x1) / 2, (y0 + y1) / 2
    names = {ring: "ring"}
    for i in ext:
        if i == ring:
            continue
        names[i] = classify(*cv2.boundingRect(cnts[i]), cx=src_cx, cy=src_cy)

    ordered = sorted(ext, key=lambda i: ORDER.index(names[i])
                     if names[i] in ORDER else len(ORDER))

    cx = cy = VB / 2
    pieces = []
    for n, idx in enumerate(ordered):
        chunks = [idx] + [j for j in range(len(cnts)) if hier[j][3] == idx]
        d = ""
        for k in chunks:
            c = cv2.approxPolyDP(cnts[k], EPS, True).reshape(-1, 2)
            pts = [tx(p) for p in c]
            d += "M%.1f %.1f" % pts[0] + "".join("L%.1f %.1f" % p for p in pts[1:]) + "Z"

        m = cv2.moments(cnts[idx])
        gx, gy = tx((m["m10"] / m["m00"], m["m01"] / m["m00"]))
        vx, vy = gx - cx, gy - cy
        norm = math.hypot(vx, vy) or 1.0
        bx, by, bw, bh = cv2.boundingRect(cnts[idx])

        pieces.append({
            "id": names[idx],
            "d": d,
            "dx": round(vx / norm, 3),
            "dy": round(vy / norm, 3),
            "bbox": (bx, by, bw, bh),
        })
        print("  %-7s bbox=(%d,%d,%d,%d) dir=(%.2f,%.2f)" %
              (pieces[-1]["id"], bx, by, bw, bh, pieces[-1]["dx"], pieces[-1]["dy"]))

    # --- version statique autonome ----------------------------------------
    static = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"',
              ' fill="currentColor" fill-rule="evenodd" role="img" aria-label="SCP Atlas">',
              '<title>SCP Atlas</title>']
    static += ['<path id="%s" d="%s"/>' % (p["id"], p["d"]) for p in pieces]
    static.append("</svg>")
    out_svg = os.path.join(ROOT, "assets", "img", "logo.svg")
    open(out_svg, "w", encoding="utf-8").write("\n".join(static))

    # --- injection dans index.html ----------------------------------------
    # Deux groupes : la couronne d'un côté, le cœur de l'autre. Ils tournent
    # en sens opposé (voir .lg-outer / .lg-inner dans css/style.css).
    def tag(p, n):
        return ('          <path class="lp" id="lp-%s" style="--dx:%s;--dy:%s;--i:%d" d="%s"/>'
                % (p["id"], p["dx"], p["dy"], n, p["d"]))

    inline = ['        <g class="lg-outer">']
    inline += [tag(p, n) for n, p in enumerate(pieces) if p["id"] == "ring"]
    inline.append('        </g>')
    inline.append('        <g class="lg-inner">')
    inline += [tag(p, n) for n, p in enumerate(pieces) if p["id"] != "ring"]
    inline.append('        </g>')

    idx_path = os.path.join(ROOT, "index.html")
    html = open(idx_path, encoding="utf-8").read()
    start, end = "<!-- logo:start -->", "<!-- logo:end -->"
    i, j = html.index(start) + len(start), html.index(end)
    html = html[:i] + "\n" + "\n".join(inline) + "\n      " + html[j:]
    open(idx_path, "w", encoding="utf-8").write(html)

    print("\nassets/img/logo.svg  : %d octets" % os.path.getsize(out_svg))
    print("index.html           : %d pieces injectees" % len(pieces))


if __name__ == "__main__":
    main()

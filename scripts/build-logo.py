"""
Vectorise le logo PNG en SVG propre et l'injecte dans index.html.

    python scripts/build-logo.py [chemin/vers/logo.png]

- recentre le logo dans un viewBox 1000x1000
- COUPE l'anneau en 3 secteurs (chacun emporte sa flèche) pour que le sceau
  puisse éclater comme dans la référence
- découpe le cœur en ses pièces naturelles
- calcule pour chaque pièce sa direction d'éclatement (--dx / --dy)
- écrit assets/img/logo.svg (version statique autonome, non découpée)
- remplace le bloc entre <!-- logo:start --> et <!-- logo:end --> dans index.html

À relancer uniquement si le logo source change.
Dépendances : opencv-python, numpy, pillow
"""
import sys, os, math
import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets", "img", "logo_source.png")

VB, MARGIN, EPS = 1000.0, 24.0, 1.4
# Largeur du trait de coupe, en pixels de l'image source. Il faut au moins
# 3 px pour que deux pixels blancs de part et d'autre ne soient plus voisins
# en connexité 8 — en dessous les secteurs restent soudés. Au-dessus, la
# fente reste visible quand le sceau est refermé. 3 px de la source valent
# environ un tiers de pixel à l'écran : la jointure est invisible au repos.
CUT_W = 3


def classify(bx, by, bw, bh, cx, cy):
    """Nomme une pièce du cœur d'après sa géométrie."""
    mx, my = bx + bw / 2, by + bh / 2
    if bw > 3 * bh:
        return "arc-b"
    if bh > 2 * bw:
        return "bar-l" if mx < cx else "bar-r"
    if my > cy:
        return "tri-b"
    if bw > 0.2 * (2 * cx):
        return "chevron-t"
    return "tri-tl" if mx < cx else "tri-tr"


def contours_of(m):
    c, h = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    return c, (h[0] if h is not None else [])


def main():
    im = Image.open(SRC).convert("RGBA")
    a = np.array(im)
    mask = (((a[:, :, 3] > 128) & (a[:, :, :3].max(axis=2) > 100)).astype(np.uint8)) * 255

    cnts, hier = contours_of(mask)
    ext = [i for i in range(len(cnts)) if hier[i][3] == -1]
    ring = max(ext, key=lambda i: cv2.contourArea(cnts[i]))
    ring_holes = [j for j in range(len(cnts)) if hier[j][3] == ring]

    # ---- pixels de la couronne : étiquetage de composantes, pas remplissage
    #      de contours. Remplir le contour externe puis soustraire les trous
    #      laisse un liseré de un ou deux pixels autour de chaque trou, qui
    #      ressort ensuite comme une fausse pièce du cœur.
    n_lab, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    ring_lab = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    ringFull = np.where(labels == ring_lab, 255, 0).astype(np.uint8)

    innerMask = cv2.bitwise_and(mask, cv2.bitwise_not(ringFull))
    ringMask = ringFull.copy()   # c'est cette copie qu'on découpe

    # ---- centre du sceau = centre du grand trou intérieur
    ring_holes.sort(key=lambda j: -cv2.contourArea(cnts[j]))
    hx, hy, hw, hh = cv2.boundingRect(cnts[ring_holes[0]])
    cx, cy = hx + hw / 2.0, hy + hh / 2.0

    # ---- angles des flèches = centres des trois petits trous restants
    arrows = []
    for j in ring_holes[1:]:
        bx, by, bw, bh = cv2.boundingRect(cnts[j])
        arrows.append(math.degrees(math.atan2(by + bh / 2 - cy, bx + bw / 2 - cx)) % 360)
    arrows.sort()
    print("angles des fleches : " + ", ".join("%.1f" % v for v in arrows))

    # ---- coupes à mi-chemin entre deux flèches : chaque secteur garde la sienne
    cuts = []
    for k in range(len(arrows)):
        nxt = arrows[(k + 1) % len(arrows)] + (360 if k == len(arrows) - 1 else 0)
        cuts.append(((arrows[k] + nxt) / 2) % 360)
    print("coupes            : " + ", ".join("%.1f" % v for v in cuts))

    rmax = max(mask.shape) * 1.2
    for ang in cuts:
        p = (int(cx + rmax * math.cos(math.radians(ang))),
             int(cy + rmax * math.sin(math.radians(ang))))
        cv2.line(ringMask, (int(cx), int(cy)), p, 0, CUT_W)

    # ---- normalisation commune (bbox du logo entier)
    ys, xs = np.where(mask > 0)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    w, h = x1 - x0, y1 - y0
    scale = (VB - 2 * MARGIN) / max(w, h)
    ox = (VB - w * scale) / 2 - x0 * scale
    oy = (VB - h * scale) / 2 - y0 * scale
    vcx = vcy = VB / 2

    def tx(p):
        return (p[0] * scale + ox, p[1] * scale + oy)

    def collect(m, kind):
        c, hi = contours_of(m)
        out = []
        for i in range(len(c)):
            if hi[i][3] != -1 or cv2.contourArea(c[i]) < 3000:
                continue
            d = ""
            for k in [i] + [j for j in range(len(c)) if hi[j][3] == i]:
                pts = [tx(p) for p in cv2.approxPolyDP(c[k], EPS, True).reshape(-1, 2)]
                d += "M%.1f %.1f" % pts[0] + "".join("L%.1f %.1f" % p for p in pts[1:]) + "Z"

            mo = cv2.moments(c[i])
            gx, gy = tx((mo["m10"] / mo["m00"], mo["m01"] / mo["m00"]))
            vx, vy = gx - vcx, gy - vcy
            n = math.hypot(vx, vy) or 1.0
            bb = cv2.boundingRect(c[i])
            out.append({"kind": kind, "d": d, "bbox": bb,
                        "dx": round(vx / n, 3), "dy": round(vy / n, 3),
                        "ang": math.degrees(math.atan2(vy, vx)) % 360})
        return out

    # Chaque secteur est redilaté de 2 px pour combler la saignée, puis
    # réintersecté avec l'anneau d'origine. Les deux voisins se recouvrent
    # donc au niveau de la coupe — la fente est invisible sceau refermé — et
    # le clipping garantit que les bords intérieur et extérieur de la bande
    # ne bougent pas d'un pixel.
    n_s, lab_s, stats_s, _ = cv2.connectedComponentsWithStats(ringMask, 8)
    k3 = np.ones((3, 3), np.uint8)
    sectors = []
    for li in range(1, n_s):
        if stats_s[li, cv2.CC_STAT_AREA] < 3000:
            continue
        m = np.where(lab_s == li, 255, 0).astype(np.uint8)
        grown = cv2.dilate(m, k3, iterations=9)
        sectors += collect(cv2.bitwise_and(grown, ringFull), "sector")

    cores = collect(innerMask, "core")
    sectors.sort(key=lambda p: p["ang"])

    for n, p in enumerate(sectors):
        p["id"] = "sect-%d" % n
    for p in cores:
        p["id"] = classify(*p["bbox"], cx=(x0 + x1) / 2, cy=(y0 + y1) / 2)

    print("\nsecteurs : %d" % len(sectors))
    for p in sectors:
        print("   %-7s dir=(%.2f,%.2f)" % (p["id"], p["dx"], p["dy"]))
    print("coeur    : %d" % len(cores))
    for p in cores:
        print("   %-10s dir=(%.2f,%.2f)" % (p["id"], p["dx"], p["dy"]))

    pieces = sectors + cores

    # ---- version statique autonome (sceau entier, sans découpe d'anneau) ---
    static = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"',
              ' fill="currentColor" fill-rule="evenodd" role="img" aria-label="SCP Atlas">',
              '<title>SCP Atlas</title>']
    full = collect(mask, "all")   # masque non coupé : sceau entier
    static += ['<path d="%s"/>' % p["d"] for p in full]
    static.append("</svg>")
    open(os.path.join(ROOT, "assets", "img", "logo.svg"), "w", encoding="utf-8").write("\n".join(static))

    # ---- injection dans index.html ---------------------------------------
    # Les tracés vont dans <defs> et sont instanciés par <use>. Ça permet de
    # répéter un secteur plusieurs fois sans dupliquer son « d » : les copies
    # servent de traînée de flou de mouvement (voir .trail dans style.css).
    # Nombre d'échantillons de la traînée de flou de mouvement. Un vrai motion
    # blur est un échantillonnage temporel : beaucoup de positions passées,
    # très rapprochées et très peu opaques, qui s'accumulent en un dégradé
    # continu. Sous ~10 échantillons on distingue les copies une à une et
    # l'effet ressemble à un écho, pas à un flou.
    TRAILS = 12
    TRAIL_HEAD = 0.20     # opacité du fantôme le plus proche
    TRAIL_FALLOFF = 1.5   # exposant de décroissance vers la queue

    inline = ['        <defs>']
    inline += ['          <path id="lp-%s" d="%s"/>' % (p["id"], p["d"]) for p in pieces]
    inline.append('        </defs>')

    for n, p in enumerate(pieces):
        head = ('        <g class="gp gp-%s" style="--dx:%s;--dy:%s;--i:%d">'
                % (p["kind"], p["dx"], p["dy"], n))
        if p["kind"] == "sector":
            # Fantômes du plus lointain au plus proche : ils se dessinent
            # sous la pièce nette, qui vient en dernier. L'opacité de chacun
            # est calculée ici plutôt que d'écrire douze classes CSS.
            ghosts = ""
            for k in range(TRAILS, 0, -1):
                a = TRAIL_HEAD * ((TRAILS - k + 1) / float(TRAILS)) ** TRAIL_FALLOFF
                ghosts += ('<g class="trail" style="--k:%d;--a:%.3f">'
                           '<use href="#lp-%s"/></g>' % (k, a, p["id"]))
            inline.append(head + ghosts + '<use href="#lp-%s"/></g>' % p["id"])
        else:
            inline.append(head + '<use href="#lp-%s"/></g>' % p["id"])

    idx_path = os.path.join(ROOT, "index.html")
    html = open(idx_path, encoding="utf-8").read()
    start, end = "<!-- logo:start -->", "<!-- logo:end -->"
    i, j = html.index(start) + len(start), html.index(end)
    open(idx_path, "w", encoding="utf-8").write(
        html[:i] + "\n" + "\n".join(inline) + "\n      " + html[j:])

    print("\nindex.html : %d pieces injectees" % len(pieces))


if __name__ == "__main__":
    main()

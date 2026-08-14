"""
Rapatrie les polices Google Fonts en local, dans assets/fonts/.

    python scripts/fetch-fonts.py

POURQUOI
Charger les polices depuis fonts.googleapis.com est un point de rupture : si
le CEF de Garry's Mod bloque la requête, si elle expire, ou si le joueur a une
connexion lente, la page retombe silencieusement sur Arial Narrow et tout le
caractère de l'écran disparaît — sans erreur visible. En local, plus de risque.

Barlow et Barlow Condensed sont sous licence SIL Open Font License 1.1, qui
autorise explicitement la redistribution avec un projet.

Écrit les .woff2 dans assets/fonts/ et génère assets/fonts/fonts.css.
"""
import os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "assets", "fonts")

# Un User-Agent récent est indispensable : Google sert du TTF aux navigateurs
# anciens et du WOFF2 (bien plus léger) aux modernes.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

URL = ("https://fonts.googleapis.com/css2"
       "?family=Barlow+Condensed:wght@400;600;700"
       "&family=Barlow:wght@300;400;500&display=swap")

SUBSETS = ("latin", "latin-ext")   # suffisant pour le français


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read() if binary else r.read().decode("utf-8")


def main():
    os.makedirs(DEST, exist_ok=True)
    css = get(URL)

    # Les blocs sont précédés d'un commentaire donnant le sous-ensemble
    blocks = re.split(r"/\*\s*([\w\-\[\]]+)\s*\*/", css)
    out, seen = [], {}

    for i in range(1, len(blocks) - 1, 2):
        subset, body = blocks[i], blocks[i + 1]
        if subset not in SUBSETS:
            continue

        fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
        wgt = re.search(r"font-weight:\s*(\d+)", body).group(1)
        src = re.search(r"url\((https://[^)]+\.woff2)\)", body)
        if not src:
            continue

        name = "%s-%s-%s.woff2" % (fam.replace(" ", ""), wgt, subset)
        path = os.path.join(DEST, name)
        if name not in seen:
            data = get(src.group(1), binary=True)
            with open(path, "wb") as f:
                f.write(data)
            seen[name] = len(data)
            print("  %-38s %5d octets" % (name, len(data)))

        body = body.replace(src.group(1), "" + name)
        out.append("/* %s */%s" % (subset, body.strip()))

    css_path = os.path.join(DEST, "fonts.css")
    header = ("/* Polices rapatriees par scripts/fetch-fonts.py.\n"
              "   Barlow et Barlow Condensed - SIL Open Font License 1.1.\n"
              "   Ne pas editer a la main : relancer le script. */\n\n")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(header + "\n\n".join(out) + "\n")

    print("\n%d fichiers, %d octets au total" % (len(seen), sum(seen.values())))
    print("assets/fonts/fonts.css genere")


if __name__ == "__main__":
    main()

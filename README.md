# SCP Atlas — Loading Screen

Loading screen web du serveur GMod **SCP Atlas**, hébergé sur GitHub Pages.

**URL publique :** https://desync76.github.io/scp-atlas-loadingscreen/

---

## Structure

```
index.html          page du loading screen
css/style.css       tout le design (variables en haut du fichier)
js/gmod.js          pont avec le moteur GMod (ne pas renommer les globales)
js/config.js        réglages : tips, fond, musique, fallbacks
js/main.js          logique d'affichage
assets/             img / fonts / audio
gmod/server.cfg     config du serveur de test (source de vérité)
scripts/            scripts PowerShell
```

---

## Preview locale

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\serve.ps1
```

Ouvre `http://127.0.0.1:8080` avec une progression simulée.

---

## Serveur GMod de test

Installation (une seule fois, ~2-3 Go) :

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\setup-gmod-server.ps1
```

Appliquer l'URL du loading screen :

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\apply-loadingurl.ps1
```

Pointer vers la preview locale au lieu de GitHub Pages :

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\apply-loadingurl.ps1 -Local
```

Démarrer le serveur :

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\start-gmod-server.ps1
```

Puis dans GMod (console `~`) :

```bash
connect 127.0.0.1:27015
```

---

## Déployer une modification

```bash
git add -A && git commit -m "design: ..." && git push
```

GitHub Pages se met à jour tout seul (~1 min). Vider le cache GMod si besoin :
supprimer `GarrysMod/garrysmod/cache/`.

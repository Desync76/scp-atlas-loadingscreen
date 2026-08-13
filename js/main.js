/**
 * main.js — logique d'affichage du loading screen.
 * Toute la partie "design" vit dans css/style.css ; ici on ne fait que
 * brancher les données du moteur sur le DOM.
 */
(function () {
  'use strict';

  var CFG = window.LS_CONFIG || {};
  var $ = function (id) { return document.getElementById(id); };

  var el = {
    bg: $('bg'),
    hostname: $('hostname'),
    status: $('status'),
    barFill: $('bar-fill'),
    progressText: $('progress-text'),
    file: $('file'),
    map: $('map'),
    gamemode: $('gamemode'),
    players: $('players'),
    tip: $('tip')
  };

  // ---------------------------------------------------------------- helpers
  function setText(node, value) {
    if (node && value !== undefined && value !== null && value !== '') {
      node.textContent = value;
    }
  }

  function prettyMap(name) {
    if (!name) return '—';
    return String(name).replace(/^(rp_|gm_|ttt_|scp_)/i, '').replace(/_/g, ' ');
  }

  function shortFile(path) {
    if (!path) return '—';
    var parts = String(path).split(/[\\/]/);
    var name = parts[parts.length - 1] || path;
    return name.length > 48 ? '…' + name.slice(-47) : name;
  }

  // ------------------------------------------------------------- background
  if (CFG.background) {
    el.bg.style.backgroundImage = 'url("' + CFG.background + '")';
  }

  // ------------------------------------------------------------------ tips
  (function initTips() {
    var tips = CFG.tips || [];
    if (!tips.length) return;
    var i = Math.floor(Math.random() * tips.length);

    function show() {
      el.tip.classList.remove('is-visible');
      setTimeout(function () {
        el.tip.textContent = tips[i % tips.length];
        el.tip.classList.add('is-visible');
        i++;
      }, 350);
    }

    show();
    setInterval(show, CFG.tipInterval || 7000);
  })();

  // ----------------------------------------------------------------- music
  (function initMusic() {
    if (!CFG.music) return;
    var audio = new Audio(CFG.music);
    audio.loop = true;
    audio.volume = CFG.musicVolume != null ? CFG.musicVolume : 0.35;
    var play = function () { audio.play().catch(function () {}); };
    play();
    document.addEventListener('click', play, { once: true });
  })();

  // ------------------------------------------------------------- progression
  var displayed = 0;   // valeur lissée 0..1
  var target = 0;

  function tick() {
    displayed += (target - displayed) * 0.12;
    if (Math.abs(target - displayed) < 0.0005) displayed = target;
    var pct = Math.round(displayed * 100);
    el.barFill.style.width = pct + '%';
    el.progressText.textContent = pct + '%';
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  // ------------------------------------------------------- branchement GMod
  var G = window.GMod;

  G.on('details', function (d) {
    setText(el.hostname, d.hostname || CFG.fallbackHostname);
    setText(el.map, prettyMap(d.mapname));
    setText(el.gamemode, d.gamemode);
    setText(el.players, d.maxplayers ? d.maxplayers + ' slots' : '—');
    document.title = (d.hostname || CFG.fallbackHostname) + ' — Chargement';
  });

  G.on('status', function (s) { setText(el.status, s); });
  G.on('file', function (f) { setText(el.file, shortFile(f)); });
  G.on('progress', function (p) { target = p; });

  // Valeurs de secours issues de l'URL (sv_loadingurl ajoute mapname, gamemode…)
  (function fromUrl() {
    var p = G.params;
    setText(el.hostname, p.hostname || CFG.fallbackHostname);
    if (p.mapname) setText(el.map, prettyMap(p.mapname));
    if (p.gamemode) setText(el.gamemode, p.gamemode);
    if (p.maxplayers) setText(el.players, p.maxplayers + ' slots');
  })();

  // --------------------------------------------------- simulation navigateur
  // Ne se déclenche que si le moteur n'a jamais parlé (= preview locale).
  var engineSpoke = false;
  G.on('status', function () { engineSpoke = true; });
  G.on('details', function () { engineSpoke = true; });
  G.on('progress', function () { engineSpoke = true; });

  if (CFG.devSimulation) {
    setTimeout(function () {
      if (engineSpoke) return;

      document.body.classList.add('is-preview');

      var steps = [
        'Connexion au serveur…',
        'Récupération des informations…',
        'Téléchargement des ressources…',
        'Envoi des données client…',
        'Chargement de la map…',
        'Démarrage du gamemode…'
      ];
      var fakeFiles = [
        'materials/scp_atlas/logo.vmt',
        'models/scp/173.mdl',
        'sound/scp/breach_alarm.wav',
        'materials/hud/atlas_overlay.vtf',
        'models/mtf/epsilon11.mdl'
      ];

      window.GameDetails('SCP ATLAS — Serveur de test', '', 'rp_scp_atlas', 64, '', 'scpatlas');

      var i = 0, total = 120, needed = 120;
      var iv = setInterval(function () {
        needed -= Math.ceil(Math.random() * 5);
        if (needed < 0) needed = 0;

        window.SetFilesTotal(total);
        window.SetFilesNeeded(needed);
        window.DownloadingFile(fakeFiles[Math.floor(Math.random() * fakeFiles.length)]);
        window.SetStatusChanged(steps[Math.min(i++ >> 2, steps.length - 1)]);

        if (needed === 0) {
          clearInterval(iv);
          window.SetStatusChanged('Prêt.');
        }
      }, 220);
    }, 1200);
  }

})();

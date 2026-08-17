/**
 * main.js — logique d'affichage du loading screen.
 * gmod.js fournit les données du moteur, config.js les réglages.
 * Ici on ne fait que brancher les deux sur le DOM.
 */
(function () {
  'use strict';

  var CFG = window.LS_CONFIG || {};
  var G   = window.GMod;
  var $   = function (id) { return document.getElementById(id); };

  var el = {
    bg:       $('bg'),
    hostname: $('hostname'),
    gamemode: $('gamemode'),
    mapline:  $('mapline'),
    feed:     $('feed'),
    bar:      $('bar-fill'),
    wave:     $('wave'),
    progress: $('progress-text'),
    status:   $('status'),
    tip:      $('tip')
  };

  var FEED_MAX = 4;     // nombre de lignes visibles dans le flux

  // ------------------------------------------------------------- utilitaires

  function setText(node, value) {
    if (node && value !== undefined && value !== null && value !== '') {
      node.textContent = value;
    }
  }

  function prettyMap(name) {
    if (!name) return '';
    return String(name).replace(/^(rp_|gm_|ttt_|scp_)/i, '').replace(/_/g, ' ');
  }

  function shortFile(path) {
    if (!path) return '';
    var parts = String(path).split(/[\\/]/);
    var name = parts[parts.length - 1] || String(path);
    return name.length > 34 ? name.slice(0, 33) + '…' : name;
  }

  // -------------------------------------------------------------- diagnostic
  // ?debug=1 affiche ce que le moteur sait réellement faire. Le navigateur de
  // GMod est un Chromium ancien dont la version exacte n'est pas documentée :
  // plutôt que de supposer, on lui demande. À utiliser dès qu'un rendu diffère
  // entre le navigateur et le jeu.
  // En jeu, ?debug=1 est inutilisable : le moteur accole lui-même ses
  // paramètres à l'URL et deux « ? » la casseraient. D'où l'option de config.
  if (G.params.debug === '1' || CFG.debug) {
    var sup = function (prop, val) {
      var ok = window.CSS && CSS.supports && CSS.supports(prop, val);
      return (ok ? '[ok]  ' : '[NON] ') + prop + ': ' + val;
    };
    var box = document.createElement('pre');
    box.style.cssText = 'position:fixed;z-index:99;right:8px;bottom:8px;margin:0;' +
      'padding:10px 12px;background:rgba(0,0,0,.85);border:1px solid #e8453c;' +
      'font:11px/1.5 monospace;color:#fff;white-space:pre;text-align:left';
    box.textContent = [
      navigator.userAgent,
      'viewport  ' + window.innerWidth + ' x ' + window.innerHeight +
        '   dpr ' + (window.devicePixelRatio || 1),
      sup('inset', '0'),
      sup('width', 'clamp(1px, 1vw, 2px)'),
      sup('width', 'min(1px, 2px)'),
      sup('gap', '1px'),
      sup('place-items', 'center'),
      sup('transform-box', 'fill-box')
    ].join('\n');
    document.body.appendChild(box);
  }

  // ------------------------------------------------------------------- fond

  if (CFG.background) {
    el.bg.style.backgroundImage = 'url("' + CFG.background + '")';
  }

  // ------------------------------------------------------- mot animé (vague)

  (function initWave() {
    var word = (CFG.loadingWord || 'Chargement') + '…';
    var frag = document.createDocumentFragment();

    for (var i = 0; i < word.length; i++) {
      var s = document.createElement('span');
      s.textContent = word[i];
      s.style.animationDelay = (i * 0.055).toFixed(3) + 's';
      frag.appendChild(s);
    }
    el.wave.appendChild(frag);
  })();

  // ---------------------------------------------------------------- astuces

  (function initTips() {
    var tips = CFG.tips || [];
    if (!tips.length) return;

    // Ordre aléatoire sans répétition avant d'avoir tout affiché
    var order = tips.slice();
    for (var i = order.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = order[i]; order[i] = order[j]; order[j] = t;
    }

    // Met en valeur les désignations : SCP-173, SCP-074-ATLAS, SCP-939-1...
    // On échappe le texte avant d'injecter, pour qu'une astuce ne puisse
    // jamais introduire de balise.
    function markup(str) {
      return str
        .replace(/[&<>]/g, function (c) {
          return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c];
        })
        .replace(/\bSCP-[0-9]+(?:-[A-Z0-9]+)*\b/g, '<span class="scp">$&</span>');
    }

    var idx = 0;
    function show() {
      el.tip.classList.remove('is-visible');
      setTimeout(function () {
        el.tip.innerHTML = markup(order[idx % order.length]);
        el.tip.classList.add('is-visible');
        idx++;
      }, 400);
    }

    show();
    setInterval(show, CFG.tipInterval || 8000);
  })();

  // ----------------------------------------------------------------- musique

  /** Relance toutes les animations du sceau depuis leur début. */
  function restartSealAnimations() {
    var els = document.querySelectorAll('.lg-all, .gp, .trail');
    var i;
    for (i = 0; i < els.length; i++) els[i].style.animation = 'none';
    void document.body.offsetWidth;            // force un reflow
    for (i = 0; i < els.length; i++) els[i].style.animation = '';
  }

  (function initMusic() {
    if (!CFG.music) return;

    var sources = [].concat(CFG.music);
    var vBase = CFG.musicVolume != null ? CFG.musicVolume : 0.12;

    // Surcharge de test : ?vol=0.6 dans l'URL monte le son pour juger le
    // rendu, sans toucher au réglage de config.js. Elle désactive aussi
    // l'atténuation progressive, sinon le son redescendrait pendant l'écoute.
    var override = parseFloat(G.params.vol);
    var testing = isFinite(override) && override >= 0 && override <= 1;
    if (testing) vBase = override;

    var audio = document.createElement('audio');
    audio.loop = true;
    audio.preload = 'auto';
    audio.volume = vBase;

    sources.forEach(function (src) {
      var s = document.createElement('source');
      s.src = src;
      if (/\.ogg$/i.test(src)) s.type = 'audio/ogg';
      else if (/\.mp3$/i.test(src)) s.type = 'audio/mpeg';
      audio.appendChild(s);
    });
    document.body.appendChild(audio);

    // Un cycle du sceau = une boucle du son.
    var applied = 0;

    function setCycle(d) {
      if (!isFinite(d) || d < 0.5 || d > 30) return;      // garde-fou
      if (Math.abs(d - applied) < 0.02) return;           // rien de neuf
      applied = d;
      document.documentElement.style.setProperty('--cycle', d.toFixed(3) + 's');
      restartSealAnimations();
    }

    // La durée vient de config.js, jamais de audio.duration : mesuré ici,
    // Chrome annonce 2,600 s pour le MP3 mais 1,986 s pour le même son en
    // Ogg Vorbis, faute de pouvoir lire la fin du fichier sur un serveur qui
    // ne gère pas les requêtes Range. Se caler là-dessus rendrait la synchro
    // dépendante du format ET du serveur.
    if (CFG.syncCycleToMusic && CFG.musicDuration) {
      setCycle(CFG.musicDuration / (CFG.musicCycles || 1));
    }

    // Au démarrage effectif du son, on réaligne l'animation sur lui.
    audio.addEventListener('play', restartSealAnimations, { once: true });

    // La lecture automatique est refusée sans geste utilisateur : mesuré sur
    // le serveur local, play() rejette avec NotAllowedError. On retente donc
    // au premier clic, et on marque le body pour que la preview l'affiche.
    // En jeu aucun clic n'est possible : si le CEF de GMod applique la même
    // politique, le son ne partira pas. L'animation, elle, ne dépend pas de
    // l'audio et tourne dans tous les cas.
    var play = function () {
      var p = audio.play();
      if (p && p.then) {
        p.then(function () {
          document.body.classList.remove('audio-blocked');
        }).catch(function () {
          document.body.classList.add('audio-blocked');
        });
      }
    };
    play();
    document.addEventListener('click', play);

    // Le son recule au fil du chargement. Le compte part de la première
    // lecture effective, pas du chargement de la page : si l'autoplay est
    // refusé et que le son démarre tard, l'atténuation ne doit pas être
    // déjà terminée quand il se fait enfin entendre.
    var vLate = testing ? null : CFG.musicVolumeLate;
    if (vLate != null && vLate < vBase) {
      audio.addEventListener('play', function () {
        var t0 = Date.now();
        var wait = (CFG.musicFadeStart || 15) * 1000;
        var span = (CFG.musicFadeDuration || 25) * 1000;
        var iv = setInterval(function () {
          var el = Date.now() - t0 - wait;
          if (el < 0) return;
          var k = Math.min(1, el / span);
          audio.volume = vBase + (vLate - vBase) * k;
          if (k >= 1) clearInterval(iv);
        }, 500);
      }, { once: true });
    }
  })();

  // -------------------------------------------------------------------- flux

  var lastFeedLabel = '';

  function pushFeed(label) {
    if (!label || label === lastFeedLabel) return;
    lastFeedLabel = label;

    var row  = document.createElement('div');
    row.className = 'feed-row';

    var ico  = document.createElement('div');
    ico.className = 'feed-ico';

    var pill = document.createElement('div');
    pill.className = 'feed-pill';
    pill.textContent = label;

    row.appendChild(ico);
    row.appendChild(pill);
    el.feed.appendChild(row);

    while (el.feed.children.length > FEED_MAX) {
      el.feed.removeChild(el.feed.firstChild);
    }
  }

  // ------------------------------------------------------------- progression

  var displayed = 0;
  var target = 0;
  var locked = false;

  (function tick() {
    displayed += (target - displayed) * 0.12;
    if (Math.abs(target - displayed) < 0.0005) displayed = target;

    var pct = Math.round(displayed * 100);
    el.progress.textContent = pct + ' %';
    el.bar.style.width = pct + '%';

    // À 100 %, la rotation s'arrête et le sceau marque le verrouillage.
    if (!locked && target >= 0.999) {
      locked = true;
      document.body.classList.add('is-ready');
    }

    requestAnimationFrame(tick);
  })();

  // -------------------------------------------------------- branchement GMod

  G.on('details', function (d) {
    var host = d.hostname || CFG.fallbackHostname;
    setText(el.hostname, host);
    setText(el.gamemode, d.gamemode || CFG.fallbackGamemode);

    var map = prettyMap(d.mapname);
    if (map) {
      setText(el.mapline, map + (d.maxplayers ? ' · ' + d.maxplayers + ' places.' : '.'));
    }
    document.title = host + ' — Chargement';
  });

  G.on('status', function (s) {
    setText(el.status, s);
    pushFeed(s);
  });

  G.on('file', function (f) {
    pushFeed(shortFile(f));
  });

  G.on('progress', function (p) { target = p; });

  // Valeurs de secours issues de l'URL (le moteur y ajoute mapname, gamemode…)
  (function fromUrl() {
    var p = G.params;
    if (p.hostname) setText(el.hostname, p.hostname);
    if (p.gamemode) setText(el.gamemode, p.gamemode);

    var map = prettyMap(p.mapname);
    if (map) {
      setText(el.mapline, map + (p.maxplayers ? ' · ' + p.maxplayers + ' places.' : '.'));
    }
  })();

  // ---------------------------------------------------- simulation navigateur
  // Ne se déclenche que si le moteur n'a jamais parlé (= preview locale).

  var engineSpoke = false;
  G.on('status',   function () { engineSpoke = true; });
  G.on('details',  function () { engineSpoke = true; });
  G.on('progress', function () { engineSpoke = true; });

  if (CFG.devSimulation) {
    setTimeout(function () {
      if (engineSpoke) return;

      document.body.classList.add('is-preview');

      var steps = [
        'Connexion à la Zone Atlas',
        'Vérification de l\'accréditation',
        'Téléchargement des ressources',
        'Synchronisation avec I.R.I.S.',
        'Chargement du site',
        'Ouverture des sas'
      ];
      var files = [
        'materials/atlas/logo_o5.vmt',
        'models/scp/173.mdl',
        'sound/atlas/alarme_breche.wav',
        'materials/hud/atlas_overlay.vtf',
        'models/mtf/epsilon_11.mdl',
        'sound/atlas/iris_annonce_01.wav',
        'materials/atlas/aile_z_panneau.vmt'
      ];

      window.GameDetails('SCP Atlas', '', 'rp_zone_atlas', 64, '', 'Confinement RP');

      var total = 140, needed = 140, i = 0;
      var iv = setInterval(function () {
        needed = Math.max(0, needed - Math.ceil(Math.random() * 5));

        window.SetFilesTotal(total);
        window.SetFilesNeeded(needed);
        window.SetStatusChanged(steps[Math.min(i >> 2, steps.length - 1)]);
        if (i % 3 === 0) {
          window.DownloadingFile(files[Math.floor(Math.random() * files.length)]);
        }
        i++;

        if (needed === 0) {
          clearInterval(iv);
          window.SetStatusChanged('Accès autorisé');
        }
      }, 240);
    }, 1200);
  }

})();

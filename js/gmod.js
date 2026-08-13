/**
 * gmod.js — pont entre le moteur Garry's Mod et le loading screen.
 *
 * GMod (Chromium/CEF) appelle des fonctions GLOBALES sur la page pendant
 * le chargement. Ce fichier les déclare toutes et les redistribue via un
 * petit event bus, pour que main.js n'ait jamais à toucher au global scope.
 *
 * Usage :   GMod.on('progress', (p) => ...)
 *
 * Événements émis :
 *   'details'  -> { hostname, serverurl, mapname, maxplayers, steamid, gamemode }
 *   'status'   -> "texte d'état"
 *   'files'    -> { needed, total, downloaded }
 *   'file'     -> "nom du fichier en cours"
 *   'progress' -> 0..1
 */
(function (window) {
  'use strict';

  var listeners = {};

  function on(evt, fn) {
    (listeners[evt] = listeners[evt] || []).push(fn);
    return API;
  }

  function emit(evt, data) {
    var l = listeners[evt];
    if (!l) return;
    for (var i = 0; i < l.length; i++) {
      try { l[i](data); } catch (e) { console.error('[GMod] listener ' + evt, e); }
    }
  }

  // --- état de téléchargement ---
  var filesTotal = 0;
  var filesNeeded = 0;

  function pushProgress() {
    if (!filesTotal) return;
    var downloaded = Math.max(0, filesTotal - filesNeeded);
    emit('files', { needed: filesNeeded, total: filesTotal, downloaded: downloaded });
    emit('progress', Math.min(1, downloaded / filesTotal));
  }

  // --- Paramètres passés dans l'URL par sv_loadingurl ---
  // ?steamid=&mapname=&maxplayers=&steamid64=&gamemode=
  function queryParams() {
    var out = {};
    var q = window.location.search.replace(/^\?/, '');
    if (!q) return out;
    q.split('&').forEach(function (pair) {
      if (!pair) return;
      var kv = pair.split('=');
      out[decodeURIComponent(kv[0])] = decodeURIComponent((kv[1] || '').replace(/\+/g, ' '));
    });
    return out;
  }

  // =========================================================================
  //  Fonctions globales appelées par le moteur — NE PAS RENOMMER
  // =========================================================================

  window.GameDetails = function (servername, serverurl, mapname, maxplayers, steamid, gamemode) {
    emit('details', {
      hostname: servername,
      serverurl: serverurl,
      mapname: mapname,
      maxplayers: maxplayers,
      steamid: steamid,
      gamemode: gamemode
    });
  };

  window.SetStatusChanged = function (status) {
    emit('status', status);
  };

  window.SetFilesTotal = function (total) {
    filesTotal = parseInt(total, 10) || 0;
    pushProgress();
  };

  window.SetFilesNeeded = function (needed) {
    filesNeeded = parseInt(needed, 10) || 0;
    pushProgress();
  };

  window.DownloadingFile = function (filename) {
    emit('file', filename);
  };

  // Alias historiques / variantes selon les versions du moteur
  window.SetFilesTotalChanged = window.SetFilesTotal;
  window.SetFilesNeededChanged = window.SetFilesNeeded;
  window.DownloadingFileChanged = window.DownloadingFile;

  var API = {
    on: on,
    emit: emit,
    params: queryParams(),
    /** true si on est dans GMod, false dans un navigateur classique */
    inGame: /Valve|GMod|Awesomium|Chrome\/(4[0-9]|5[0-9])\./.test(navigator.userAgent) &&
            !/Edg|OPR/.test(navigator.userAgent)
  };

  window.GMod = API;

})(window);

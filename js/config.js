/**
 * config.js — tout ce qui se règle sans toucher au code.
 */
window.LS_CONFIG = {

  // Nom affiché si le serveur ne renvoie rien
  fallbackHostname: 'SCP ATLAS',

  // Fond : chemin d'une image dans assets/img/, ou null pour le dégradé CSS
  background: null,           // ex: 'assets/img/bg.jpg'

  // Musique d'ambiance : chemin dans assets/audio/, ou null
  music: null,                // ex: 'assets/audio/ambient.mp3'
  musicVolume: 0.35,

  // Rotation des astuces
  tipInterval: 7000,          // ms
  tips: [
    "Gardez toujours un contact visuel avec le SCP-173.",
    "Les classes-D ne sont pas autorisées dans les zones de confinement lourd.",
    "Utilisez la radio pour signaler une brèche de confinement.",
    "Le MTF intervient uniquement sur ordre du commandement.",
    "Ne quittez jamais votre poste sans autorisation d'un superviseur.",
    "Consultez le règlement du serveur avant de jouer un rôle sensible."
  ],

  // Faux chargement quand la page est ouverte hors du jeu (preview navigateur)
  devSimulation: true
};

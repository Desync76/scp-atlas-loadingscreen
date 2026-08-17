/**
 * config.js — tout ce qui se règle sans toucher au code.
 */
window.LS_CONFIG = {

  // ---------------------------------------------------------------- entête
  fallbackHostname: 'SCP Atlas',
  fallbackGamemode: 'Zone Atlas',
  fallbackDesc:     'Station de recherche météorologique.',

  // Mot animé en bas de l'écran
  loadingWord: 'Chargement',

  // ------------------------------------------------------------------ fond
  background: null,          // ex: 'assets/img/bg.jpg' — sinon dégradé noir

  // ------------------------------------------------------------------- son
  // Le navigateur prend la première source qu'il sait lire. Le MP3 est en
  // tête par sécurité, l'Ogg suit — trois fois plus léger à qualité égale.
  // Générés depuis le WAV d'origine (18,8 Mo, inutilisable tel quel sur le
  // web) par :
  //     ffmpeg -i source.wav -ac 1 -c:a libmp3lame -b:a 112k music.mp3
  //     ffmpeg -i source.wav -ac 1 -c:a libvorbis  -q:a 2    music.ogg
  music: ['assets/audio/music.mp3', 'assets/audio/music.ogg'],

  // Bien plus haut que les 0.1 d'avant, et ce n'est pas arbitraire : ce
  // morceau est mesuré à -25,4 dB de niveau moyen, environ 15 dB sous le
  // bruitage court utilisé précédemment. À 0.1 il serait inaudible.
  musicVolume: 0.35,
  musicVolumeLate: 0.18,     // niveau après atténuation (null = pas d'atténuation)
  musicFadeStart: 20,        // secondes avant que l'atténuation commence
  musicFadeDuration: 30,     // durée de la descente

  // Un cycle du sceau = une boucle du son. La durée est écrite ici et fait
  // autorité : on ne la lit PAS depuis le lecteur audio, dont la mesure s'est
  // révélée peu fiable selon le format et le serveur (voir ci-dessus).
  // À corriger si tu changes le fichier son :
  //     ffprobe -v error -show_entries format=duration -of csv=p=0 seal.mp3
  // DÉSACTIVÉ, et c'est voulu. Ce réglage cale la durée d'un tour du sceau
  // sur celle du son — pertinent pour une boucle courte de 2 ou 3 secondes,
  // absurde ici : le morceau dure 3 min 44, un tour de sceau durerait donc
  // 224 secondes. L'animation garde ses 2,6 s (--cycle dans css/style.css)
  // et la musique se déroule de son côté, indépendamment.
  syncCycleToMusic: false,
  musicDuration: null,
  musicCycles: 1,

  // ---------------------------------------------------------------- astuces
  tipInterval: 8000,         // ms

  tips: [
    // ── SCP-074-ATLAS ──────────────────────────────────────────────
    "Dans un rayon de 5 mètres de SCP-074-ATLAS, ne suivez pas les voix. Elles veulent seulement que vous touchiez le cube.",
    "Le contact avec SCP-074-ATLAS est immédiat et irréversible. Il n'existe aucun protocole de retour.",
    "Les instances SCP-074-ATLAS-1 sont sourdes et privées d'odorat. Leur chasse est purement visuelle.",
    "Face à une instance : ne bougez pas, puis sortez de son champ de vision. Courir ne fonctionne pas.",
    "Extraire le cube du massif annule ses propriétés. Elles reprennent dès son retour. La Zone a été construite autour de lui.",
    "Toute électronique exposée trop longtemps à SCP-074-ATLAS finit par imploser sous la surcharge de données.",
    "Le zinc est le seul matériau connu insensible aux effets de SCP-074-ATLAS.",

    // ── Aile Z ─────────────────────────────────────────────────────
    "L'Aile Z est intégralement analogique. Verrous mécaniques, périscopes, éclairage passif. Aucune électronique.",
    "Le silence de l'Aile Z n'est pas une règle de discipline. C'est une mesure de survie.",
    "Aucune unité robotisée n'entre dans l'Aile Z. Aucune exception n'a jamais été accordée.",

    // ── Registre ───────────────────────────────────────────────────
    "SCP-096 : ne regardez jamais son visage. Même sur une photographie. Même par accident.",
    "SCP-173 : maintenez le contact visuel en permanence. Clignez des yeux à tour de rôle.",
    "SCP-939 imite la voix humaine. Ne répondez jamais à un appel à l'aide non vérifié.",
    "SCP-049 est coopératif. Il n'est pas inoffensif. Ses demandes d'accès à SCP-610 ont toutes été refusées.",
    "Aucun échantillon de SCP-008 ne quitte la Zone. Sous aucun prétexte.",
    "Ne laissez jamais les instances SCP-3199 pondre.",
    "Les similitudes entre SCP-610 et les instances SCP-074-ATLAS-1 sont troublantes. Les recherches continuent.",
    "SCP-7528 se déplace d'écran en écran. La majorité des incidents de la Zone portent sa signature.",
    "Un écran quitté par SCP-7528 explose. Comme si l'entité seule le maintenait en vie. Aucune explication à ce jour.",

    // ── Sécurité ───────────────────────────────────────────────────
    "I.R.I.S. gère les accès, la surveillance et les unités robotisées. I.R.I.S. ne dort jamais.",
    "À proximité du cube, une unité UTR devient imprévisible. Protocole : désactivation immédiate, destruction si nécessaire.",

    // ── Zone & histoire ────────────────────────────────────────────
    "Surface · Niveau 1 · Niveau 2 · Niveau 3 · Aile Z. L'Aile Z ne figure sur aucun plan public.",
    "Pour le monde civil, ceci est une station météorologique isolée dans les Alpes. Rien de plus.",
    "Les villages du massif parlaient déjà d'une montagne maudite. Ils ne savaient pas à quel point.",
    "Le personnel présent lors de la Brèche porte l'insigne VÉTÉRAN. Ne leur demandez pas d'en parler.",
    "Toute divulgation non autorisée entraîne l'administration d'un amnésique de classe A.",
    "La Zone veille."
  ],

  // Faux chargement quand la page est ouverte hors du jeu
  devSimulation: true
};

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
  music: null,               // ex: 'assets/audio/ambient.mp3'
  musicVolume: 0.3,

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

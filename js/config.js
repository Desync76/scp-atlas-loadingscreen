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
  // Plusieurs sources : le navigateur prend la première qu'il sait lire.
  // Le MP3 est en tête et c'est délibéré. Il porte son nombre de trames dans
  // un en-tête placé au DÉBUT du fichier, donc sa durée est connue dès les
  // premiers octets. Un Ogg oblige le lecteur à aller lire la dernière page
  // du fichier, ce qui suppose que le serveur accepte les requêtes Range —
  // le serveur Python local ne les gère pas, et Chrome annonce alors une
  // durée fausse. L'Ogg reste en second, comme filet si jamais le CEF de
  // GMod était compilé sans codec MP3. Mettre à null pour couper le son.
  music: ['assets/audio/seal.mp3', 'assets/audio/seal.ogg'],
  musicVolume: 0.45,

  // Un cycle du sceau = une boucle du son. La durée est écrite ici et fait
  // autorité : on ne la lit PAS depuis le lecteur audio, dont la mesure s'est
  // révélée peu fiable selon le format et le serveur (voir ci-dessus).
  // À corriger si tu changes le fichier son :
  //     ffprobe -v error -show_entries format=duration -of csv=p=0 seal.mp3
  syncCycleToMusic: true,
  musicDuration: 2.6,        // secondes

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

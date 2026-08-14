"""
Synthétise le son du sceau, de zéro. Aucun échantillon extérieur.

    python scripts/make-sound.py

Écrit assets/audio/seal.wav, puis seal.mp3 et seal.ogg via ffmpeg.

POURQUOI UNE MÉLODIE ET PAS UNE TEXTURE
Les versions précédentes cherchaient à imiter un timbre — souffle filtré, puis
bourdon électronique. Une texture ne se règle qu'à l'oreille, et le résultat
était strident. Une mélodie se spécifie : une tonalité, des notes, une enveloppe.

CE QUI REND LE SON SOMBRE ET DOUX
  - Ré mineur, registre grave : les fondamentales restent entre 130 et 260 Hz.
  - Ligne DESCENDANTE, qui retombe sur la tonique — c'est ce qui donne la
    couleur mélancolique plutôt que menaçante.
  - Timbre en cloche douce : sinus + harmoniques faibles, attaque de 25 ms.
    Pas d'attaque sèche, rien au-dessus de 1 kHz à niveau notable.
  - AUCUN bruit, aucun battement, aucune résonance inharmonique : ce sont
    ces trois choses qui donnaient la sensation de fraise de dentiste.

DURÉE
5,2 s, soit DEUX tours du sceau (2,6 s chacun). Une mélodie de 2,6 s serait
trop courte pour respirer ; l'animation, elle, ne change pas.

Dépendances : numpy, scipy, ffmpeg
"""
import os, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio")

SR = 44100
DUR = 5.2                     # 2 tours de 2,6 s
N = int(SR * DUR)
t = np.arange(N) / SR

# Ré mineur, octaves graves. La ligne descend, marque la tonique à mi-parcours
# (début du deuxième tour), puis redescend pour boucler sur le La initial.
MELODY = [
    (0.00, 220.00),   # La3
    (0.65, 196.00),   # Sol3
    (1.30, 174.61),   # Fa3
    (1.95, 164.81),   # Mi3
    (2.60, 146.83),   # Ré3   <- tonique, 2e tour
    (3.25, 174.61),   # Fa3
    (3.90, 164.81),   # Mi3
    (4.55, 130.81),   # Do3   <- ramène vers le La3
]

PARTIALS = [(1, 1.00), (2, 0.34), (3, 0.15), (4, 0.07), (6, 0.03)]


def note(at, freq, dur, amp, detune=0.0):
    """Cloche douce : attaque progressive, extinction exponentielle."""
    out = np.zeros(N)
    i0 = int(at * SR)
    i1 = min(N, i0 + int(dur * SR))
    if i1 <= i0:
        return out
    k = np.arange(i1 - i0) / SR

    atk = 0.025
    a = np.minimum(k / atk, 1.0) ** 1.5            # attaque douce
    a *= np.exp(-k / (dur * 0.42))                 # extinction

    sig = np.zeros_like(k)
    for h, w in PARTIALS:
        sig += w * np.sin(2 * np.pi * (freq + detune) * h * k)
    out[i0:i1] = sig / sum(w for _, w in PARTIALS) * a
    return out * amp


def pad(freq, amp, detune=0.0):
    """Nappe grave continue : c'est elle qui installe la profondeur."""
    swell = np.interp(t, [0, .8, 2.6, 3.4, 5.2], [.25, .75, .55, .80, .25])
    sig = (np.sin(2 * np.pi * (freq + detune) * t)
           + .22 * np.sin(2 * np.pi * (freq + detune) * 2 * t))
    return sig / 1.22 * swell * amp


def make_channel(detune):
    x = np.zeros(N)

    # --- la mélodie
    for at, f in MELODY:
        x += note(at, f, 1.55, 0.52, detune)

    # --- doublure une octave au-dessus, très en retrait : cela éclaire
    #     légèrement la ligne sans jamais devenir perçant
    for at, f in MELODY:
        x += note(at, f * 2, 0.95, 0.20, detune)

    # --- nappe : Ré2 et La2, la fondation sombre. Volontairement discrète —
    #     trop forte, elle empâte tout et la mélodie disparaît dedans.
    x += pad(73.42, 0.16, detune * .5)
    x += pad(110.00, 0.15, detune * .5)

    # --- extinction pour une boucle sans accroc
    x *= np.interp(t, [0, .02, DUR - .18, DUR], [0, 1, 1, 0])
    return x


st = np.stack([make_channel(0.0), make_channel(0.6)], axis=1)

# Passe-bas doux : laisse passer de quoi distinguer les notes, mais rien de
# piquant. C'est la coupure qui empêche le retour de l'effet « fraise ».
st = signal.sosfilt(signal.butter(3, 5200, btype="low", fs=SR, output="sos"), st, axis=0)
# Coupe les infra-graves : ils n'apportent qu'un ronflement pâteux.
st = signal.sosfilt(signal.butter(2, 60, btype="high", fs=SR, output="sos"), st, axis=0)
st /= np.abs(st).max() / 0.85

wav = os.path.join(OUT, "seal.wav")
wavfile.write(wav, SR, (st * 32767).astype(np.int16))
print("seal.wav ecrit (%.2fs, %d notes)" % (DUR, len(MELODY)))

for args, name in ((["-c:a", "libmp3lame", "-b:a", "192k"], "seal.mp3"),
                   (["-c:a", "libvorbis", "-q:a", "5"], "seal.ogg")):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav] + args
                   + [os.path.join(OUT, name)], check=True)
    print(name, "ecrit")

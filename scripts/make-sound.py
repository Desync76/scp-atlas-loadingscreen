"""
Synthétise le son du sceau, de zéro. Aucun échantillon extérieur n'est
utilisé : tout est généré (oscillateurs, enveloppes), donc le résultat est
original et libre de droits.

    python scripts/make-sound.py

Écrit assets/audio/seal.wav, puis seal.mp3 et seal.ogg via ffmpeg.

CE QUI GUIDE LA CONCEPTION
Le son est bâti autour d'un BOURDON ÉLECTRONIQUE, pas de bruit filtré.
La mesure de la référence donnait une platitude spectrale de 0,16 — donc
franchement tonale — avec une fréquence entretenue autour de 930 Hz sur toute
la durée, glissant de 969 à 904 Hz, une seconde tonalité à 851 Hz entrant à
mi-parcours (d'où un battement), et des impulsions graves vers 75 et 129 Hz.

Le souffle large bande est réduit au minimum : c'est ce qui rendait la
version précédente sifflante. Et il n'y a AUCUNE résonance inharmonique —
c'était elle qui donnait un son de casserole.

STRUCTURE, calée sur le cycle de l'animation (--cycle dans css/style.css)
    0.00s  mise sous tension
    0.21s  le cœur s'efface (8 % du cycle)
    0.62s  la révolution démarre (24 %)
    ...    bips de servomoteur pendant la rotation
    1.87s  la révolution s'achève (72 %)
    2.26s  verrouillage (87 %) — descente de fréquence, pas d'impact métal
    2.60s  extinction, la boucle peut reprendre

Dépendances : numpy, scipy, ffmpeg
"""
import os, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio")

SR = 44100
DUR = 2.6
N = int(SR * DUR)
t = np.arange(N) / SR


def env(points):
    """Enveloppe linéaire par morceaux : [(temps, niveau), ...]."""
    ts, vs = zip(*points)
    return np.interp(t, ts, vs, left=vs[0], right=vs[-1])


def tone(freqs, amp_env, phase=0.0):
    """Oscillateur à fréquence variable : [(temps, Hz), ...]."""
    ts, fs = zip(*freqs)
    f = np.interp(t, ts, fs, left=fs[0], right=fs[-1])
    return np.sin(2 * np.pi * np.cumsum(f) / SR + phase) * amp_env


def blip(at, f0, f1, dur, decay, amp, shape=0.0):
    """Bip court : glissando de f0 vers f1, décroissance exponentielle.
    `shape` ajoute un peu d'harmonique 2 pour un timbre plus « circuit »."""
    out = np.zeros(N)
    i0, i1 = int(at * SR), min(N, int((at + dur) * SR))
    if i1 <= i0:
        return out
    k = np.arange(i1 - i0) / SR
    f = f0 + (f1 - f0) * np.minimum(k / dur, 1.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) + shape * np.sin(2 * ph)
    out[i0:i1] = sig * np.exp(-k / decay)
    return out * amp


def click(at, dur, lo, hi, decay, amp, rng):
    """Micro-transitoire large bande : l'attaque d'un contact, pas du souffle."""
    out = np.zeros(N)
    i0, i1 = int(at * SR), min(N, int((at + dur) * SR))
    if i1 <= i0:
        return out
    sos = signal.butter(4, [lo, hi], btype="band", fs=SR, output="sos")
    k = np.arange(i1 - i0) / SR
    out[i0:i1] = signal.sosfilt(sos, rng.normal(0, 1, i1 - i0)) * np.exp(-k / decay)
    return out * amp


def make_channel(seed, detune):
    rng = np.random.default_rng(seed)
    x = np.zeros(N)

    # --- bourdon principal : la colonne vertébrale du son.
    #     Glisse vers le grave, comme dans la référence.
    drone = env([(0, .00), (.06, .55), (.55, .42), (1.10, .60), (1.55, .50),
                 (1.90, .34), (2.26, .46), (2.40, .12), (2.55, .00)])
    #     Légère modulation d'amplitude : ça « respire » au lieu d'être plat.
    drone *= 1.0 + .12 * np.sin(2 * np.pi * 6.5 * t)
    #     Volontairement en retrait : c'est un repère, pas le sujet. Trop fort,
    #     il écrase l'aigu et le son devient un bourdon de transformateur.
    x += tone([(0, 968 + detune), (1.30, 936 + detune), (2.60, 902 + detune)],
              drone) * .17

    # --- harmonique 2, discrète : donne du corps sans épaissir
    x += tone([(0, 1936), (1.30, 1872), (2.60, 1804)], drone) * .06

    # --- seconde tonalité désaccordée : le battement mesuré vers 1,35 s
    x += tone([(0, 851 + detune * .6)], env([
        (0, .00), (1.10, .00), (1.35, .30), (1.60, .26), (1.95, .00)])) * .22

    # --- partiels clairs : la brillance « numérique ». C'est cette bande qui
    #     porte l'essentiel de l'énergie dans la référence, pas le bourdon.
    x += tone([(0, 5210), (2.60, 4980)], env([
        (0, .00), (.04, .16), (.30, .07), (.55, .14), (1.20, .09),
        (1.90, .06), (2.22, .18), (2.45, .00)])) * .26

    #     Tonalité haute relevée dans la référence autour de 9,4 kHz
    x += tone([(0, 9430), (2.60, 9180)], env([
        (0, .00), (.05, .09), (.40, .04), (1.00, .10), (1.50, .05),
        (2.22, .10), (2.42, .00)])) * .22

    # --- impulsions graves relevées au milieu du son
    x += blip(1.30, 75, 68, .22, .075, .30)
    x += blip(1.67, 129, 118, .20, .065, .24)

    # --- mise sous tension
    x += blip(0.01, 620, 1180, .12, .045, .40, shape=.3)
    x += click(0.01, .05, 2000, 11000, .012, .22, rng)

    # --- le cœur s'efface : petit bip descendant
    x += blip(0.21, 1560, 1180, .08, .028, .26, shape=.25)

    # --- bips de servomoteur pendant la révolution
    for at, f0, f1, a in ((0.95, 1480, 1760, .24),
                          (1.25, 1240, 1480, .21),
                          (1.55, 1760, 2090, .26),
                          (1.87, 1480, 1120, .30)):
        x += blip(at, f0, f1, .055, .017, a, shape=.35)
        x += click(at, .012, 3000, 12000, .0035, a * .45, rng)

    # --- verrouillage : une descente nette, sans résonance métallique
    x += blip(2.26, 1420, 320, .30, .085, .52, shape=.2)
    x += blip(2.26, 92, 54, .26, .090, .30)
    x += click(2.26, .03, 1500, 9000, .008, .30, rng)

    # --- air : reste en retrait, mais assez présent pour que le timbre soit
    #     clair dès le début — la référence démarre à 7,4 kHz de centroïde
    sos = signal.butter(4, [5500, 16000], btype="band", fs=SR, output="sos")
    x += signal.sosfilt(sos, rng.normal(0, 1, N)) * env([
        (0, .00), (.03, .30), (.25, .12), (.62, .16), (1.20, .26),
        (1.75, .17), (1.95, .09), (2.26, .24), (2.45, .02), (2.60, .00)]) * .52

    # --- extinction : garantit une boucle sans accroc
    x *= env([(0, 1), (2.45, 1), (2.60, 0)])
    ramp = int(.004 * SR)
    x[:ramp] *= np.linspace(0, 1, ramp)
    return x


st = np.stack([make_channel(20260814, 0.0), make_channel(20260821, 3.5)], axis=1)
st = signal.sosfilt(signal.butter(2, 45, btype="high", fs=SR, output="sos"), st, axis=0)
st /= np.abs(st).max() / 0.88

wav = os.path.join(OUT, "seal.wav")
wavfile.write(wav, SR, (st * 32767).astype(np.int16))
print("seal.wav ecrit (%.3fs)" % DUR)

for args, name in ((["-c:a", "libmp3lame", "-b:a", "192k"], "seal.mp3"),
                   (["-c:a", "libvorbis", "-q:a", "5"], "seal.ogg")):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav] + args
                   + [os.path.join(OUT, name)], check=True)
    print(name, "ecrit")

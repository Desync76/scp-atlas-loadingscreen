"""
Synthétise le son du sceau, de zéro. Aucun échantillon extérieur n'est
utilisé : tout est généré (bruit filtré, sinus, enveloppes), donc le
résultat est original et libre de droits.

    python scripts/make-sound.py

Écrit assets/audio/seal.wav, puis seal.mp3 et seal.ogg via ffmpeg.

La structure suit le cycle de l'animation (voir --cycle dans css/style.css) :
    0.00s  déverrouillage — le sceau s'ouvre
    0.21s  le cœur s'efface (8 % du cycle)
    0.62s  la révolution démarre (24 %)
    ...    souffle rotatif + déclics de servomoteur
    1.87s  la révolution s'achève (72 %)
    2.26s  IMPACT — le sceau se referme et se verrouille (87 %)
    2.60s  extinction complète, la boucle peut reprendre

Dépendances : numpy, scipy, ffmpeg
"""
import os, subprocess, sys
import numpy as np
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio")

SR = 44100
DUR = 2.6
N = int(SR * DUR)
t = np.arange(N) / SR

rng = np.random.default_rng(20260814)


def band(x, lo, hi, order=4):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def env(points):
    """Enveloppe linéaire par morceaux : [(temps, niveau), ...]."""
    ts, vs = zip(*points)
    return np.interp(t, ts, vs, left=vs[0], right=vs[-1])


def burst(at, length, lo, hi, decay, amp):
    """Impulsion de bruit filtré, décroissance exponentielle."""
    out = np.zeros(N)
    i0 = int(at * SR)
    i1 = min(N, i0 + int(length * SR))
    if i1 <= i0:
        return out
    k = np.arange(i1 - i0) / SR
    out[i0:i1] = band(rng.normal(0, 1, i1 - i0), lo, hi) * np.exp(-k / decay)
    return out * amp


def ring(at, freqs, decay, amp):
    """Résonance métallique : partiels inharmoniques amortis."""
    out = np.zeros(N)
    i0 = int(at * SR)
    k = np.arange(N - i0) / SR
    for j, f in enumerate(freqs):
        out[i0:] += np.sin(2 * np.pi * f * k + j) * np.exp(-k / (decay * (1 - .12 * j)))
    return out / len(freqs) * amp


def make_channel(seed_shift):
    global rng
    rng = np.random.default_rng(20260814 + seed_shift)
    x = np.zeros(N)

    # --- lit d'air : décroît sur la fin pour que le timbre s'assombrisse,
    #     comme dans la référence dont le centroïde chute vers l'aigu bas
    x += band(rng.normal(0, 1, N), 6000, 16000) * env([
        (0, .00), (.10, .04), (.62, .16), (1.15, .34), (1.60, .20),
        (1.87, .10), (2.26, .22), (2.42, .04), (2.60, .00)]) * .46

    # --- souffle rotatif : le corps du mouvement, 24 % -> 72 %.
    #     Les creux évitent le bruit blanc continu, fatigant en boucle.
    x += band(rng.normal(0, 1, N), 1500, 7000) * env([
        (0, .00), (.55, .02), (.72, .34), (.90, .20), (1.10, .48),
        (1.32, .26), (1.52, .44), (1.74, .18), (1.90, .06),
        (2.20, .03), (2.60, .00)]) * .40

    # --- corps médium : c'est lui qui empêche le résultat d'être un sifflement
    x += band(rng.normal(0, 1, N), 400, 2200) * env([
        (0, .00), (.65, .06), (1.10, .30), (1.50, .24), (1.85, .12),
        (2.26, .18), (2.45, .03), (2.60, .00)]) * .62

    # --- déverrouillage
    x += burst(0.01, .18, 2500, 14000, .042, .60)

    # --- le cœur s'efface
    x += burst(0.21, .10, 2000, 9000, .018, .40)

    # --- déclics de servomoteur : attaque courte et sèche, plus un point
    #     haut très bref, pour qu'ils percent la nappe au lieu d'y fondre
    for at, a in ((0.95, .48), (1.25, .42), (1.55, .50), (1.87, .58)):
        x += burst(at, .07, 1800, 9500, .011, a)
        x += burst(at, .02, 6000, 15000, .003, a * .8)

    # --- IMPACT : le sceau se verrouille
    x += burst(2.26, .22, 900, 12000, .030, .95)
    x += ring(2.26, (623, 941, 1487, 2273), .34, .30)
    i0 = int(2.26 * SR)
    k = np.arange(N - i0) / SR
    thump = np.zeros(N)
    thump[i0:] = np.sin(2 * np.pi * (78 - 32 * np.minimum(k / .16, 1)) * k) * np.exp(-k / .095)
    x += thump * .34

    # --- extinction : garantit une boucle sans accroc
    x *= env([(0, 1), (2.42, 1), (2.60, 0)])
    x[:int(.004 * SR)] *= np.linspace(0, 1, int(.004 * SR))
    return x


left = make_channel(0)
right = make_channel(7)

st = np.stack([left, right], axis=1)
sos = signal.butter(2, 110, btype="high", fs=SR, output="sos")   # profil clair
st = signal.sosfilt(sos, st, axis=0)
st /= np.abs(st).max() / 0.89

wav = os.path.join(OUT, "seal.wav")
from scipy.io import wavfile
wavfile.write(wav, SR, (st * 32767).astype(np.int16))
print("seal.wav ecrit (%.3fs)" % DUR)

for args, name in (
        (["-c:a", "libmp3lame", "-b:a", "192k"], "seal.mp3"),
        (["-c:a", "libvorbis", "-q:a", "5"], "seal.ogg")):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav] + args
                   + [os.path.join(OUT, name)], check=True)
    print(name, "ecrit")

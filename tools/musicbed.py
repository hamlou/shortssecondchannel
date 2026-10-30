"""Our own music bed (synthesised, no third-party audio -> no Content ID, no credit needed).
py tools/musicbed.py [seed]  -> tools/music/bed.wav (64 s loop, 120 BPM, Am-F-C-G)"""
import os, sys
import numpy as np, soundfile as sf

SR, BPM, BARS = 44100, 120, 32
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
beat = 60 / BPM
n = int(SR * beat * 4 * BARS)
out = np.zeros((n, 2))


def env(length, a=0.005, d=0.15):
    t = np.arange(length) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)


def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    j = min(i + len(sig), n)
    out[i:j, 0] += sig[: j - i] * gain * (1 - max(pan, 0))
    out[i:j, 1] += sig[: j - i] * gain * (1 + min(pan, 0))


def kick():
    L = int(0.35 * SR)
    t = np.arange(L) / SR
    f = 110 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(L, 0.002, 0.12)


def hat():
    L = int(0.06 * SR)
    x = rng.standard_normal(L)
    x = np.diff(np.concatenate([[0], x]))  # crude high-pass
    return x * env(L, 0.001, 0.02) * 0.25


def tone(freq, length, kind="saw", d=0.25):
    L = int(length * SR)
    t = np.arange(L) / SR
    if kind == "saw":
        x = sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 7))
    else:
        x = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2 * t)
    return x * env(L, 0.004, d)


note = lambda m: 440 * 2 ** ((m - 69) / 12)
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [52, 55, 60]), (55, [55, 59, 62])]  # Am F C G
for bar in range(BARS):
    root, chord = prog[bar % 4]
    t0 = bar * 4 * beat
    for b in range(4):
        add(kick(), t0 + b * beat, gain=0.9)
        add(hat(), t0 + b * beat + beat / 2, pan=0.3)
        add(tone(note(root - 12), beat * 0.9, "saw", 0.18) * 0.22, t0 + b * beat + (beat / 2 if b % 2 else 0))
    if bar >= 2:
        for k in range(8):
            m = chord[k % 3] + (12 if k in (3, 6) else 0)
            add(tone(note(m + 12), beat / 2, "sine", 0.12) * 0.16, t0 + k * beat / 2, pan=-0.25 if k % 2 else 0.25)

out /= np.max(np.abs(out)) / 0.8
os.makedirs(os.path.join(os.path.dirname(__file__), "music"), exist_ok=True)
sf.write(os.path.join(os.path.dirname(__file__), "music", "bed.wav"), out.astype(np.float32), SR)
print("bed.wav", round(n / SR, 1), "s")

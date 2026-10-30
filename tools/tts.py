"""Voice-over with the channel's ONE fixed voice (Kokoro-82M, Apache 2.0, ONNX on CPU, ~0.5 GB RAM).
py tools/tts.py shorts/<nn>/script.json            -> shorts/<nn>/vo/<id>.wav + vo/full.wav + durations.json
py tools/tts.py --samples                          -> tools/voice/samples/<voice>.wav (pick the channel voice once)
Voice id + speed live in research/voice.md (VOICE/SPEED below must match it)."""
import json, os, re, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE, SPEED = "am_puck", 1.15
GAP = 0.04
CANDIDATES = ["am_michael", "am_adam", "am_puck", "am_fenrir", "af_heart", "bm_george"]
SAMPLE = "What happens if you hook a dead car battery to a welder? Those bubbles? Hydrogen and oxygen. A bomb in a box."


def engine():
    return Kokoro(os.path.join(HERE, "voice", "kokoro-v1.0.int8.onnx"), os.path.join(HERE, "voice", "voices-v1.0.bin"))


def trim(a, sr, thr=0.012):
    idx = np.where(np.abs(a) > thr)[0]
    return a[max(idx[0] - int(0.01 * sr), 0): idx[-1] + int(0.02 * sr)] if len(idx) else a


def main():
    k = engine()
    if sys.argv[1] == "--samples":
        out = os.path.join(HERE, "voice", "samples")
        os.makedirs(out, exist_ok=True)
        for v in CANDIDATES:
            a, sr = k.create(SAMPLE, voice=v, speed=SPEED, lang="en-us" if v[0] == "a" else "en-gb")
            sf.write(os.path.join(out, f"{v}.wav"), trim(a, sr), sr)
            print(v, f"{len(a) / sr:.1f}s")
        return
    p = sys.argv[1]
    d = json.load(open(p, encoding="utf-8"))
    out = os.path.join(os.path.dirname(p), "vo")
    os.makedirs(out, exist_ok=True)
    durs, full, sr = {}, [], 24000
    for l in d["lines"]:
        text = re.sub(r"\s+", " ", l["text"]).strip()
        a, sr = k.create(text, voice=VOICE, speed=SPEED, lang="en-us")
        a = trim(a, sr)
        sf.write(os.path.join(out, f"{l['id']:02d}.wav"), a, sr)
        durs[str(l["id"])] = round(len(a) / sr + GAP, 3)
        full += [a, np.zeros(int(GAP * sr), dtype=a.dtype)]
        print(f"{l['id']:2d} {durs[str(l['id'])]:5.2f}s  {text}")
    sf.write(os.path.join(out, "full.wav"), np.concatenate(full), sr)
    json.dump(durs, open(os.path.join(os.path.dirname(p), "durations.json"), "w"), indent=1)
    print(f"total {sum(durs.values()):.1f}s  voice={VOICE} speed={SPEED}")


if __name__ == "__main__":
    main()

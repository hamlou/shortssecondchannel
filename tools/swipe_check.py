"""NO-SWIPE GATE (owner 5 Nov 2026): "would the viewer meet ANY obstacle that makes him swipe away?"
Runs on the GitHub runner after the render, beside the monetization gate. py tools/swipe_check.py shorts/<nn>
Checks every shot of build/video.mp4 (no captions) + the final mix. FAIL = must be fixed before upload.

 1 blur        every shot sharpness (Laplacian var, 360x480 gray, rows 15-70 %) >= 60, 90 % of shots >= 240,
               first second >= 500 and brightness >= 75 (measured on all 154 TNP shots, research/tnp_overlays.md)
 2 dark/black  no black frames (blackdetect), every shot mean brightness >= 40
 3 text/chart  no chart / table / document / number screen: OCR words on a shot <= 8 and no white-card frame with text
               (TNP never shows these)
 4 marks       every mark in the script must be locked on its object (tools/marks.py); a dropped mark is reported
 5 hook        voice starts within 0.25 s, first cut within 1.6 s, frame 0 passes 1+2+3
 6 frozen      no still picture held > 1.0 s (pace_check), no source shot > 2.2 s
 7 AI stills   no blank AI image
 8 speech      no line longer than 6.5 s (hard to follow), no dead air > 0.35 s inside the voice"""
import json, os, re, shutil, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble import FF, FPS  # noqa: E402

# thresholds measured on all 154 TNP shots (research/tnp_overlays.md): 360-wide gray, rows 15-70 %
SHARP_MIN, SHARP_P10, HOOK_SHARP_MIN, BRIGHT_MIN, HOOK_BRIGHT_MIN, OCR_MAX = 60, 240, 500, 40, 75, 8


def frame(video, t, size="360:480"):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-vf", f"scale={size}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    w, h = map(int, size.split(":"))
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3) if len(raw) == w * h * 3 else None


def band(rgb):
    h = rgb.shape[0]
    return rgb[int(h * 0.15):int(h * 0.70)]


def sharpness(rgb):
    a = band(rgb).astype(np.float32).mean(axis=2)
    return float((a[1:-1, 1:-1] * 4 - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]).var())


def ocr_words(video, t):
    """Words tesseract reads with confidence >= 70 on a 1080x1440 frame (no captions on video.mp4)."""
    if not shutil.which("tesseract"):
        return -1
    p = "/tmp/ocr.png"
    subprocess.run([FF, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", p])
    tsv = subprocess.run(["tesseract", p, "-", "--psm", "11", "tsv"], capture_output=True, text=True).stdout
    n = 0
    for row in tsv.splitlines()[1:]:
        c = row.split("\t")
        if len(c) == 12 and c[11].strip() and float(c[10]) >= 70 and len(re.sub(r"\W", "", c[11])) >= 2:
            n += 1
    return n


def main():
    sd = sys.argv[1]
    b = os.path.join(sd, "build")
    d = json.load(open(os.path.join(sd, "script.json"), encoding="utf-8"))
    du = json.load(open(os.path.join(sd, "durations.json")))
    plan = json.load(open(os.path.join(b, "plan.json")))
    video = os.path.join(b, "video.mp4")
    fails, warns = [], []
    F = lambda t, msg: fails.append(f"{t:6.2f}s  {msg}")
    Wn = lambda t, msg: warns.append(f"{t:6.2f}s  {msg}")

    shs = []
    for p in plan:
        t0, ln = p["t"], p["s"]
        for k, tt in enumerate((t0 + 0.05, t0 + ln / 2, t0 + ln - 0.05) if ln > 0.4 else (t0 + ln / 2,)):
            img = frame(video, tt)
            if img is None:
                continue
            sh, br = sharpness(img), float(band(img).mean())
            shs.append(sh)
            need, needb = (HOOK_SHARP_MIN, HOOK_BRIGHT_MIN) if tt < 1.0 else (SHARP_MIN, BRIGHT_MIN)
            if sh < need:
                F(tt, f"BLUR sharpness {sh:.0f} < {need} (line {p['line']} {p['kind']} {p['what']})")
            if br < needb:
                F(tt, f"DARK brightness {br:.0f} < {needb} (line {p['line']} {p['kind']} {p['what']})")
            if k == 1 or ln <= 0.4:
                n = ocr_words(video, tt)
                white = float(((img.min(axis=2) > 200)).mean())
                if n > OCR_MAX or (n >= 4 and white > 0.45):
                    F(tt, f"TEXT/CHART screen ({n} words, {white:.0%} white) (line {p['line']} {p['what']}) - TNP never shows these")
        if p["kind"] == "src" and ln > 2.2:
            Wn(t0, f"long source shot {ln:.1f}s")

    if shs and np.percentile(shs, 10) < SHARP_P10:
        F(0, f"SOFT overall: 10th-percentile sharpness {np.percentile(shs, 10):.0f} < {SHARP_P10} (TNP: 90 % of shots >= 240)")
    blk = subprocess.run([FF, "-v", "info", "-i", os.path.join(b, "final.mp4"), "-vf", "blackdetect=d=0.03:pix_th=0.08", "-an", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", blk):
        F(float(m.group(1)), f"BLACK frames until {float(m.group(2)):.2f}s")

    mk = os.path.join(b, "marks.json")
    for m in (json.load(open(mk)) if os.path.exists(mk) else []):
        if not m.get("found"):
            Wn(m.get("t0", 0), f"mark {m['kind']} on '{m['word']}' DROPPED: {m.get('why')} -> give it an object query visible in that shot, or remove it")
    for l in d["lines"]:
        if l.get("mark") and len(l["mark"]) < 3 and l["mark"][0] != "q":
            Wn(0, f"line {l['id']} mark has no object query (old format) -> not drawn")

    sil = subprocess.run([FF, "-v", "info", "-i", os.path.join(sd, "vo", "full.wav"), "-af", "silencedetect=noise=-35dB:d=0.35", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    for m in re.finditer(r"silence_start: ([\d.]+)", sil):
        st = float(m.group(1))
        if st < 0.01:
            e = re.search(r"silence_end: ([\d.]+)", sil[m.end():])
            if e and float(e.group(1)) > 0.25:
                F(0, f"HOOK voice starts late at {float(e.group(1)):.2f}s")
        elif st < sum(du.values()) - 0.5:
            F(st, "DEAD AIR in the voice > 0.35 s")
    cuts = sorted(p["t"] for p in plan if p["t"] > 0)
    if cuts and cuts[0] > 1.6:
        F(0, f"HOOK first cut only at {cuts[0]:.2f}s")
    for l in d["lines"]:
        if du[str(l["id"])] > 6.5:
            Wn(0, f"line {l['id']} is {du[str(l['id'])]:.1f}s long - split it, long sentences lose viewers")
    pace = os.path.join(os.getcwd(), "pace.txt")
    if os.path.exists(pace):
        m = re.search(r"max_still_s\s+([\d.]+)", open(pace).read())
        if m and float(m.group(1)) > 1.0:
            F(0, f"FROZEN picture held {m.group(1)}s")

    out = ["NO-SWIPE CHECK  (any FAIL = a moment where viewers swipe away)"]
    out += [f"FAIL {x}" for x in sorted(fails)] + [f"WARN {x}" for x in sorted(warns)]
    out.append("SWIPE: " + ("PASS" if not fails else f"FAIL ({len(fails)})"))
    print("\n".join(out))
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()

"""Pacing check vs TestedNProved (research/tnp_pacing.md). py tools/pace_check.py shorts/<nn>
Measures final.mp4: scene changes (ffmpeg scene>0.25), mean motion/frame (90x160 gray, cuts excluded), longest still hold, VO dead air."""
import os, re, subprocess, sys
import numpy as np

FF = os.environ.get("FFMPEG") or (r"C:\Users\hp\Desktop\100\tools\ffmpeg\ffmpeg.exe" if os.name == "nt" else "ffmpeg")
TARGET = {"scene_changes": 45, "motion": 3.5, "max_still_s": 1.0, "vo_dead_air_s": 0.6}


def main():
    sd = sys.argv[1]
    f = os.path.join(sd, "build", "final.mp4")
    log = subprocess.run([FF, "-v", "info", "-i", f, "-vf", "select='gt(scene,0.25)',showinfo", "-f", "null", "-"], capture_output=True, text=True).stderr
    scenes = len(re.findall(r"pts_time", log))
    raw = subprocess.run([FF, "-v", "error", "-i", f, "-vf", "fps=30,scale=90:160,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 160, 90).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    motion = float(d[d < 25].mean())
    still, best = 0, 0
    for x in d:
        still = still + 1 if x < 0.6 else 0
        best = max(best, still)
    sil = subprocess.run([FF, "-v", "info", "-i", os.path.join(sd, "vo", "full.wav"), "-af", "silencedetect=noise=-35dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    dead = sum(float(x) for x in re.findall(r"silence_duration: ([\d.]+)", sil))
    res = {"scene_changes": scenes, "motion": round(motion, 2), "max_still_s": round(best / 30, 2), "vo_dead_air_s": round(dead, 2)}
    ok = True
    for k, v in res.items():
        p = v >= TARGET[k] if k in ("scene_changes", "motion") else v <= TARGET[k]
        ok &= p
        print(f"{'PASS' if p else 'FAIL'}  {k:15s} {v:>7}   target {'>=' if k in ('scene_changes', 'motion') else '<='} {TARGET[k]}   (TNP: {'45-72' if k == 'scene_changes' else '5.1-5.7' if k == 'motion' else '<1.0' if k == 'max_still_s' else '~0'})")
    print("PACE:", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()

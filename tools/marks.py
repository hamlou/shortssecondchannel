"""Object-locked marks (owner 5 Nov 2026: "the arrow must point at the thing, at the right time").
py tools/marks.py shorts/<nn>      (runs on the GitHub runner after assemble.py has written build/video.mp4)

script.json line field  "mark": [kind, word, "object to find"]   kind = arrow | circle | x | q
  - TNP timing (research/tnp_overlays.md, all 16 TNP overlays measured): the mark appears with the shot that shows
    the object, ~0.4 s BEFORE the word that names it (never after the word, never before that shot's cut), and stays
    to the end of that shot (0.6-1.6 s). It is static like TNP's, so the object must be still in that shot.
  - the object is found IN THAT SHOT with Grounding DINO tiny (IDEA-Research, Apache-2.0) at the start, middle and end
    of the window; all three must agree or the mark is DROPPED (a wrong arrow is worse than none) and reported.
  - "q" needs no object: red ? next to the subject (face query "person face" if visible, else top-right).
Line 1 may have "hook": "object" -> a red arrow on that object from frame 0 (TNP hook).
Out: build/marks.json  [{kind, word, t0, t1, frames: {frame_index: [x0,y0,x1,y1]}, score, found}]"""
import json, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble import word_times, FPS, W, H, FF  # noqa: E402

MODEL = "IDEA-Research/grounding-dino-tiny"
BOX_T, TEXT_T = 0.35, 0.25
STEP = 6            # re-detect every 6 frames (0.2 s)
MAX_LEN = 1.6       # seconds a mark stays (TNP 0.65-1.65 s)
LEAD = 0.4          # TNP: overlay appears ~0.4 s before the naming word
MIN_LEN = 0.6
_DET = {}


def frame_at(video, i):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{i / FPS:.4f}", "-i", video, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3) if len(raw) == W * H * 3 else None


def detect(img, query):
    """-> (box [x0,y0,x1,y1], score) of the best match or (None, 0)."""
    import torch
    from PIL import Image
    if not _DET:
        from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
        _DET["p"] = AutoProcessor.from_pretrained(MODEL)
        _DET["m"] = AutoModelForZeroShotObjectDetection.from_pretrained(MODEL).eval()
    p, m = _DET["p"], _DET["m"]
    q = query.lower().strip().rstrip(".") + "."
    im = Image.fromarray(img).resize((W // 2, H // 2))
    inp = p(images=im, text=q, return_tensors="pt")
    with torch.no_grad():
        out = m(**inp)
    try:
        r = p.post_process_grounded_object_detection(out, inp.input_ids, threshold=BOX_T, text_threshold=TEXT_T, target_sizes=[im.size[::-1]])[0]
    except TypeError:
        r = p.post_process_grounded_object_detection(out, inp.input_ids, box_threshold=BOX_T, text_threshold=TEXT_T, target_sizes=[im.size[::-1]])[0]
    if len(r["scores"]) == 0:
        return None, 0.0
    k = int(r["scores"].argmax())
    box = [float(v) * 2 for v in r["boxes"][k]]
    area = (box[2] - box[0]) * (box[3] - box[1]) / (W * H)
    if area > 0.85 or area < 0.002:          # the whole frame or a speck is not "the object"
        return None, 0.0
    return box, float(r["scores"][k])


def iou(a, b):
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter + 1e-9)


def locate(video, f0, f1, query):
    """Static box (TNP overlays don't move): detect at start, middle, end; all must agree."""
    boxes, scores = [], []
    for f in (f0 + 1, (f0 + f1) // 2, f1 - 2):
        img = frame_at(video, f)
        box, sc = detect(img, query) if img is not None else (None, 0)
        if box is None:
            return None, 0.0
        boxes.append(box)
        scores.append(sc)
    if min(iou(boxes[0], x) for x in boxes[1:]) < 0.3:
        return None, 0.0
    box = [float(np.mean([x[i] for x in boxes])) for i in range(4)]
    return {f: box for f in range(f0, f1)}, min(scores)


def main():
    sd = sys.argv[1]
    b = os.path.join(sd, "build")
    d = json.load(open(os.path.join(sd, "script.json"), encoding="utf-8"))
    du = json.load(open(os.path.join(sd, "durations.json")))
    plan = json.load(open(os.path.join(b, "plan.json")))
    video = os.path.join(b, "video.mp4")
    lines = d["lines"]
    durs = [du[str(l["id"])] for l in lines]
    starts = [sum(durs[:i]) for i in range(len(durs))]
    cuts = sorted({p["t"] for p in plan} | {round(sum(durs), 2)})
    out = []

    def shot_of(t):
        st = max([c for c in cuts if c <= t + 1e-3] or [0.0])
        return st, next((c for c in cuts if c > t + 1e-3), sum(durs))

    jobs = []
    if lines[0].get("hook"):
        jobs.append(("arrow", lines[0]["text"].split()[0], 0.0, lines[0]["hook"]))
    for l, st, du_ in zip(lines, starts, durs):
        m = l.get("mark")
        if not m:
            continue
        kind, word = m[0], m[1]
        query = m[2] if len(m) > 2 else None
        ws, wt = word_times(l["text"], du_)
        key = str(word).lower().strip(".,?!'\"")
        if key not in ws:
            out.append({"kind": kind, "word": word, "found": False, "why": "word not in line"})
            continue
        jobs.append((kind, word, st + wt[ws.index(key)], query))

    for kind, word, tw, query in jobs:
        s0, s1 = shot_of(tw)
        t = max(s0, tw - LEAD)
        t1 = min(s1, t + MAX_LEN)
        f0, f1 = round(t * FPS), round(t1 * FPS)
        rec = {"kind": kind, "word": word, "query": query, "t0": round(t, 2), "t1": round(t1, 2), "t_word": round(tw, 2)}
        if t1 - t < MIN_LEN:
            rec.update(found=False, why=f"the shot showing '{word}' lasts only {t1 - t:.2f}s from the mark onset")
        elif kind == "q" and not query:
            rec.update(found=True, frames={}, score=1.0)
        elif not query:
            rec.update(found=False, why="no object query in script")
        else:
            frames, sc = locate(video, f0, f1, query)
            rec.update(found=frames is not None, score=round(sc, 2), frames=frames or {},
                       why="" if frames else f"'{query}' not found in the shot")
        print(("MARK OK  " if rec["found"] else "MARK DROP"), kind, word, f"{t:.2f}s", query, rec.get("why", ""), flush=True)
        out.append(rec)
    json.dump(out, open(os.path.join(b, "marks.json"), "w"))


if __name__ == "__main__":
    main()

"""Draw object-locked marks (build/marks.json from tools/marks.py) onto build/video.mp4 -> build/video_marked.mp4.
TNP look: one short thick red arrow whose tip touches the object, or a hand-drawn red circle around it, popping in on the
spoken word and following the object frame by frame; red X across it; small red ? beside it."""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble import FF, FPS, W, H, FONT, X264  # noqa: E402

RED = (235, 30, 30, 255)
POP = 5   # frames of pop-in


def pop_scale(i):
    return [0.55, 0.85, 1.12, 1.05, 1.0][i] if i < POP else 1.0 + 0.04 * math.sin((i - POP) * 0.6)   # TNP: slight pulse


def draw_arrow(d, tip, ang, s):
    a = math.radians(ang)
    ux, uy, px, py = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    L, hw, hl, sw = 200 * s, 64 * s, 96 * s, 36 * s
    base = (tip[0] - ux * hl, tip[1] - uy * hl)
    tail = (tip[0] - ux * L, tip[1] - uy * L)
    for col, grow in (((255, 255, 255, 255), 8 * s), (RED, 0)):
        d.line([tail, base], fill=col, width=int(sw + 2 * grow))
        d.polygon([(tip[0] + ux * grow, tip[1] + uy * grow), (base[0] + px * (hw + grow), base[1] + py * (hw + grow)),
                   (base[0] - px * (hw + grow), base[1] - py * (hw + grow))], fill=col)


def circ_box(box):
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    rx, ry = (box[2] - box[0]) * 0.62 + 18, (box[3] - box[1]) * 0.62 + 18
    return [cx - rx, cy - ry, cx + rx, cy + ry]


def arrow_for(box):
    """Arrow comes from the emptier side towards the object; tip sits just outside the box edge."""
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    ang = 45 if cx > W / 2 else 135          # from upper-left to lower-right if object is on the right, else mirrored
    if cy < H * 0.3:
        ang = -ang                           # object high in frame: come from below
    a = math.radians(ang)
    hx, hy = (box[2] - box[0]) / 2, (box[3] - box[1]) / 2
    t = min(hx / max(abs(math.cos(a)), 1e-3), hy / max(abs(math.sin(a)), 1e-3))
    tip = (cx - math.cos(a) * (t + 6), cy - math.sin(a) * (t + 6))
    return tip, ang


def render(m, fi, box):
    """RGBA layer for mark m at its local frame index fi."""
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    s = pop_scale(fi)
    k = m["kind"]
    if k in ("arrow", "circle") and box:          # TNP: red circles always come with an arrow
        tip, ang = arrow_for(box if k == "arrow" else circ_box(box))
        slide = max(0.0, 1 - (fi + 1) / 9) * 260     # TNP: arrow slides in from its edge in 0.3 s
        a = math.radians(ang)
        draw_arrow(d, (tip[0] - math.cos(a) * slide, tip[1] - math.sin(a) * slide), ang, 0.9 if k == "circle" else 1.0)
    if k == "circle" and box:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        rx, ry = (box[2] - box[0]) * 0.62 + 18, (box[3] - box[1]) * 0.62 + 18
        reveal = min(1.0, (fi + 1) / 6)       # stroke draws itself on in 0.2 s
        n = max(3, int(64 * 1.08 * reveal))
        pts = [(cx + math.cos(t) * rx * (1 + 0.035 * math.sin(3 * t)), cy + math.sin(t) * ry * (1 + 0.035 * math.cos(2 * t)))
               for t in [-math.pi / 2 + i / 64 * 2 * math.pi for i in range(n)]]
        d.line(pts, fill=(255, 255, 255, 255), width=22, joint="curve")
        d.line(pts, fill=RED, width=13, joint="curve")
    elif k == "x" and box:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        r = max(70, min(box[2] - box[0], box[3] - box[1]) * 0.45) * s
        for col, wd in (((255, 255, 255, 255), 58), (RED, 40)):
            d.line((cx - r, cy - r, cx + r, cy + r), fill=col, width=wd)
            d.line((cx + r, cy - r, cx - r, cy + r), fill=col, width=wd)
    elif k == "q":
        x, y = (min(box[2] + 70, W - 90), max(box[1] + 40, 120)) if box else (W * 0.8, H * 0.2)
        d.text((x, y), "?", font=ImageFont.truetype(FONT, int(190 * s)), fill=RED, anchor="mm", stroke_width=8, stroke_fill="white")
    return im


def main():
    b = os.path.join(sys.argv[1], "build")
    marks = [m for m in json.load(open(os.path.join(b, "marks.json"))) if m.get("found")]
    active = {}
    for m in marks:
        f0, f1 = round(m["t0"] * FPS), round(m["t1"] * FPS)
        frames = {int(k): v for k, v in m.get("frames", {}).items()}
        last = None
        for f in range(f0, f1):
            last = frames.get(f, last)
            active.setdefault(f, []).append((m, f - f0, last))
    src = subprocess.Popen([FF, "-v", "error", "-i", os.path.join(b, "video.mp4"), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    dst = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            *X264, os.path.join(b, "video_marked.mp4")], stdin=subprocess.PIPE)
    n, fs = 0, W * H * 3
    while True:
        raw = src.stdout.read(fs)
        if len(raw) < fs:
            break
        if n in active:
            img = Image.frombuffer("RGB", (W, H), raw).convert("RGBA")
            for m, fi, box in active[n]:
                img = Image.alpha_composite(img, render(m, fi, box))
            raw = img.convert("RGB").tobytes()
        dst.stdin.write(raw)
        n += 1
    dst.stdin.close()
    dst.wait()
    src.wait()
    print(f"overlay: {len(marks)} marks drawn on {len(active)} frames")


if __name__ == "__main__":
    main()

"""Assemble one Short in the TestedNProved style (research/tnp_breakdown.md). Runs on GitHub Actions (ffmpeg only).
py tools/assemble.py shorts/<nn>
Needs: script.json, durations.json, vo/full.wav (tools/tts.py), source/source.mp4, build/ai/*.jpg (tools/ai_gen.py).
Out:   shorts/<nn>/build/final.mp4 (1080x1920, 30 fps) + final_sheet.jpg + plan.json

Per script line:  "src": source ranges -> full-screen 9:16 shots of 0.5-1.0 s at 1.5x with a push-in
                  "ai":  prompts -> photoreal stills animated 1.0-1.6 s (push / pull / pan) = our ORIGINAL footage
                  "first": "ai"|"src" (default ai for analysis lines), "cx": 0-1 horizontal crop centre of the source,
                  "payoff": true -> one real-speed source shot (the result moment), "red"/"blue": key words to colour,
                  "mark": [q|x|circle, seconds into line], "sfx": [[kind, seconds], ...] (negative = from line end).
Frame 0 gets red arrows. Kind switches (ai<->src) get a 0.1 s whip blur or white flash + whoosh.
Rules (research/monetization_system.md): source shots <= 2 s, no source audio, crop above the source's burned-in captions."""
import json, math, os, random, re, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_gen import img_name

FF = os.environ.get("FFMPEG") or (r"C:\Users\hp\Desktop\100\tools\ffmpeg\ffmpeg.exe" if os.name == "nt" else "ffmpeg")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "tools", "fonts", "FredokaBold.ttf")
FPS, W, H, GAP = 30, 1080, 1920, 0.04
SPEED = 1.5      # source plays 1.5x (research/tnp_pacing.md)
SAFE = 0.861     # share of source height kept from the top: drops the band where Project Farm burns its captions
AI_LEN = 1.4     # target seconds per AI clip
X264 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-threads", "2", "-pix_fmt", "yuv420p"]
RED, BLUE = (235, 30, 30, 255), (40, 150, 255, 255)


def ff(*a):
    r = subprocess.run([FF, "-v", "error", "-y", *a], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-1500:])


def sec(t):
    m, s = t.split(":")
    return int(m) * 60 + float(s)


def plan_line(l, dur, rnd):
    """-> list of shots: ("ai", prompt, seconds, move) / ("src", start, seconds, speed)."""
    ranges = [tuple(map(sec, c.split("-"))) for c in l.get("src", [])]
    ai = l.get("ai", [])
    if l.get("payoff") and ranges:
        a, b = ranges[0]
        n = 1 if dur <= 3.5 else 2
        return [("src", a + i * (b - a) / n, dur / n, 1.0) for i in range(n)]
    ai_t = dur if not ranges else (min(dur * 0.75, len(ai) * AI_LEN) if ai else 0)
    A = []
    if ai:
        n = max(len(ai), round(ai_t / AI_LEN)) if not ranges else len(ai)
        moves = ["push", "panr", "pull", "panl"]
        A = [("ai", ai[i % len(ai)], ai_t / n, moves[(i + rnd.randrange(4)) % 4]) for i in range(n)]
    S, used, k = [], 0.0, 0
    cursor = [a for a, b in ranges]
    while ranges and used < dur - ai_t - 1e-3:
        i = k % len(ranges)
        a, b = ranges[i]
        ln = min(rnd.uniform(0.5, 1.0), dur - ai_t - used)
        st = cursor[i] if cursor[i] + ln * SPEED <= b else a
        cursor[i] = st + ln * SPEED
        S.append(("src", st, ln, SPEED))
        used += ln
        k += 1
    first = l.get("first", "ai" if l.get("type") == "analysis" else "src")
    p, q = (A, S) if first == "ai" else (S, A)
    out = []
    for i in range(max(len(p), len(q))):
        out += p[i:i + 1] + q[i:i + 1]
    return out


def enc(args, vf, nf, out, trans):
    if trans == "flash":
        vf += ",fade=t=in:st=0:d=0.13:color=white"
    elif trans == "whip":
        vf += ",avgblur=sizeX=70:sizeY=1:enable='lt(t,0.1)'"
    ff(*args, "-an", "-vf", vf, "-frames:v", str(nf), *X264, out)


def cut_src(src, st, nf, speed, cx, z, trans, out):
    zz = f"1+0.12*on/{nf}" if z else f"1.12-0.12*on/{nf}"
    vf = (f"setpts=PTS/{speed},fps={FPS},crop=w='trunc(ih*{SAFE}*9/16/2)*2':h='trunc(ih*{SAFE}/2)*2':x='(iw-ow)*{cx}':y=0,"
          f"scale={W}:{H}:flags=lanczos,zoompan=z='{zz}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.07:saturation=1.18,setsar=1")
    enc(["-ss", f"{st:.3f}", "-t", f"{nf / FPS * speed + 0.3:.3f}", "-i", src], vf, nf, out, trans)


def cut_ai(img, nf, move, trans, out):
    t = nf / FPS
    x = {"panr": f"(iw-ow)*(0.1+0.8*t/{t:.3f})", "panl": f"(iw-ow)*(0.9-0.8*t/{t:.3f})"}.get(move, "(iw-ow)/2")
    z = {"push": f"1+0.25*on/{nf}", "pull": f"1.25-0.25*on/{nf}"}.get(move, f"1.06+0.08*on/{nf}")
    vf = (f"scale=2160:2160:flags=lanczos,crop=1215:2160:x='{x}':y=0,scale={W}:{H},"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},eq=saturation=1.1,setsar=1")
    enc(["-loop", "1", "-framerate", str(FPS), "-t", f"{t + 0.2:.3f}", "-i", img], vf, nf, out, trans)


def overlays(b):
    """Transparent 1080x1920 PNGs: hook arrows, red ?, red X, red hand-drawn circle (target = frame centre-ish)."""
    cx, cy = 540, 860
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for ang, dist in ((200, 330), (-20, 330), (95, 380)):
        a = math.radians(ang)
        tip = (cx + math.cos(a) * dist * 0.45, cy + math.sin(a) * dist * 0.45)
        tail = (cx + math.cos(a) * dist * 1.25, cy + math.sin(a) * dist * 1.25)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        head = [tip, (tip[0] + ux * 150 + px * 100, tip[1] + uy * 150 + py * 100), (tip[0] + ux * 150 - px * 100, tip[1] + uy * 150 - py * 100)]
        for col, wd, grow in (((255, 255, 255, 255), 78, 14), (RED, 52, 0)):
            d.line([tail, (tip[0] + ux * 120, tip[1] + uy * 120)], fill=col, width=wd)
            hh = [(x + (x - tip[0]) * grow / 100, y + (y - tip[1]) * grow / 100) for x, y in head]
            d.polygon(hh, fill=col)
    im.save(os.path.join(b, "ov_arrows.png"))
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    d.text((850, 520), "?", font=ImageFont.truetype(FONT, 420), fill=RED, anchor="mm", stroke_width=16, stroke_fill="white")
    im.save(os.path.join(b, "ov_q.png"))
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for col, wd in (("white", 92), (RED, 62)):
        d.line((cx - 230, cy - 230, cx + 230, cy + 230), fill=col, width=wd)
        d.line((cx + 230, cy - 230, cx - 230, cy + 230), fill=col, width=wd)
    im.save(os.path.join(b, "ov_x.png"))
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    pts = [(cx + math.cos(a) * 330 * (1 + 0.04 * math.sin(3 * a)), cy + math.sin(a) * 300) for a in [i / 60 * 2.15 * math.pi for i in range(61)]]
    d.line(pts, fill="white", width=30, joint="curve")
    d.line(pts, fill=RED, width=18, joint="curve")
    im.save(os.path.join(b, "ov_circle.png"))


def ass_time(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def captions(lines, starts, durs, path):
    """One lowercase word at a time, rounded heavy font, white + dark outline, ~78 % height, key words red/blue."""
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: W,Fredoka Bold,128,&H00FFFFFF,&H00FFFFFF,&H00141414,&H96000000,0,0,0,0,100,100,1,0,1,9,4,2,40,40,380,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    for l, st, du in zip(lines, starts, durs):
        words = l["text"].split()
        red = {w.lower() for w in l.get("red", [])}
        blue = {w.lower() for w in l.get("blue", [])}
        wts = [len(re.sub(r"\W", "", w)) + 2 for w in words]
        t = st
        for w, wt in zip(words, wts):
            d = (du - GAP) * wt / sum(wts)
            clean = re.sub(r"[^\w'%]", "", w).lower()
            col = r"{\c&H001E1EEB&}" if clean in red or re.search(r"\d", clean) else r"{\c&H00FF9628&}" if clean in blue else ""
            ev.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + d)},W,,0,0,0,,{{\\fscx86\\fscy86\\t(0,60,\\fscx100\\fscy100)}}{col}{clean}")
            t += d
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def sfx(path, kind):
    g = {
        "whoosh": ["-f", "lavfi", "-i", "anoisesrc=d=0.35:c=pink:a=0.6", "-af", "bandpass=f=2200:width_type=o:w=2,afade=t=in:d=0.12,afade=t=out:st=0.14:d=0.21,volume=0.55"],
        "pop": ["-f", "lavfi", "-i", "sine=f=880:d=0.09", "-af", "afade=t=out:st=0.02:d=0.07,volume=0.5"],
        "boom": ["-f", "lavfi", "-i", "anoisesrc=d=0.9:c=brown:a=1", "-af", "lowpass=f=180,afade=t=out:st=0.1:d=0.8,volume=2.2"],
        "ding": ["-f", "lavfi", "-i", "sine=f=1320:d=0.7", "-af", "afade=t=out:st=0.05:d=0.65,volume=0.45"],
        "buzz": ["-f", "lavfi", "-i", "sine=f=140:d=0.35", "-af", "afade=t=out:st=0.2:d=0.15,volume=0.5"],
    }[kind]
    ff(*g, "-ar", "44100", "-ac", "2", path)


def main():
    sd = sys.argv[1]
    b = os.path.join(sd, "build")
    seg = os.path.join(b, "seg")
    os.makedirs(seg, exist_ok=True)
    d = json.load(open(os.path.join(sd, "script.json"), encoding="utf-8"))
    du = json.load(open(os.path.join(sd, "durations.json")))
    lines = d["lines"]
    durs = [du[str(l["id"])] for l in lines]
    starts = [sum(durs[:i]) for i in range(len(durs))]
    total = sum(durs)
    rnd = random.Random(d["short"])
    src = os.path.join(sd, "source", "source.mp4")

    shots = []
    for l, dur in zip(lines, durs):
        sh = plan_line(l, dur, rnd)
        frames = [max(round(x[2] * FPS), 1) for x in sh]
        frames[-1] += round(dur * FPS) - sum(frames)
        shots += [(l, s, nf) for s, nf in zip(sh, frames)]
    segs, plan, ev, t, last_tr, prev, ai_frames, n_tr = [], [], [], 0.0, -9.0, None, 0, 0
    for j, (l, s, nf) in enumerate(shots):
        tr = None
        if prev and prev != s[0] and t - last_tr >= 1.8:
            tr = "whip" if n_tr % 2 == 0 else "flash"
            n_tr += 1
            last_tr = t
            ev.append(("whoosh", max(t - 0.12, 0)))
        o = os.path.join(seg, f"{j:03d}.mp4")
        if s[0] == "ai":
            cut_ai(os.path.join(b, "ai", img_name(s[1])), nf, s[3], tr, o)
            ai_frames += nf
        else:
            cut_src(src, s[1], nf, s[3], l.get("cx", 0.5), j % 2 == 0, tr, o)
        segs.append(o)
        plan.append({"line": l["id"], "t": round(t, 2), "kind": s[0], "s": round(nf / FPS, 2), "what": s[1] if s[0] == "ai" else round(s[1], 2), "trans": tr})
        prev = s[0]
        t += nf / FPS
    print(f"{len(segs)} shots, {n_tr} transitions, ORIGINAL (AI) {ai_frames / FPS:.1f}s = {ai_frames / FPS / total:.0%} of runtime", flush=True)
    json.dump(plan, open(os.path.join(b, "plan.json"), "w"), indent=1)
    lst = os.path.join(seg, "list.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(x)}'\n".replace("\\", "/") for x in segs))
    ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(b, "video.mp4"))

    overlays(b)
    os.makedirs(os.path.join(b, "fonts"), exist_ok=True)
    shutil.copy(FONT, os.path.join(b, "fonts", os.path.basename(FONT)))
    captions(lines, starts, durs, os.path.join(b, "captions.ass"))

    at = lambda st, du_, s: st + (s if s >= 0 else du_ + s)
    wins = {"arrows": [(0, 1.1)], "q": [], "x": [], "circle": []}
    for l, st, du_ in zip(lines, starts, durs):
        ev += [(k, at(st, du_, s)) for k, s in l.get("sfx", [])]
        if l.get("mark"):
            k, s = l["mark"]
            a = at(st, du_, s)
            wins[k].append((a, min(a + 1.5, st + du_)))
            ev.append(("buzz" if k == "x" else "pop", a))
    ev.append(("pop", 0.05))
    win = lambda ws: "+".join(f"between(t,{a:.2f},{c:.2f})" for a, c in ws) or "0"
    cwd = os.getcwd()
    os.chdir(b)
    fc = ("[0:v][1:v]overlay=x='10*sin(t*22)':y='10*cos(t*22)':enable='{a}'[v1];[v1][2:v]overlay=0:0:enable='{q}'[v2];"
          "[v2][3:v]overlay=0:0:enable='{x}'[v3];[v3][4:v]overlay=0:0:enable='{c}'[v4];[v4]subtitles=captions.ass:fontsdir=fonts[v]").format(
        a=win(wins["arrows"]), q=win(wins["q"]), x=win(wins["x"]), c=win(wins["circle"]))
    ff("-filter_threads", "1", "-i", "video.mp4", *[x for k in ("arrows", "q", "x", "circle") for x in ("-i", f"ov_{k}.png")],
       "-filter_complex", fc, "-map", "[v]", "-t", f"{total:.3f}", *X264[:5], "19", *X264[6:], "video_fx.mp4")

    kinds = sorted({k for k, _ in ev})
    for k in kinds:
        sfx(f"sfx_{k}.wav", k)
    ain = ["-i", os.path.abspath(os.path.join(cwd, sd, "vo", "full.wav"))]
    mix = ["[0:a]aresample=44100,aformat=channel_layouts=stereo[vo]"]
    for j, (k, tt) in enumerate(ev):
        ain += ["-i", f"sfx_{k}.wav"]
        ms = int(max(tt, 0) * 1000)
        mix.append(f"[{j + 1}:a]adelay={ms}|{ms},volume=0.55[e{j}]")
    ain += ["-stream_loop", "-1", "-i", os.path.join(ROOT, "tools", "music", "bed.wav")]
    mix.append(f"[{len(ev) + 1}:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.16,afade=t=out:st={max(total - 0.6, 0):.2f}:d=0.6[mus]")
    mix.append("[vo]" + "".join(f"[e{j}]" for j in range(len(ev))) + f"[mus]amix=inputs={len(ev) + 2}:normalize=0:duration=first,alimiter=limit=0.95[a]")
    ff(*ain, "-filter_complex", ";".join(mix), "-map", "[a]", "-t", f"{total:.3f}", "-c:a", "pcm_s16le", "audio.wav")
    ff("-i", "video_fx.mp4", "-i", "audio.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
       "-movflags", "+faststart", "-shortest", "final.mp4")
    ff("-i", "final.mp4", "-vf", "fps=2,scale=216:-1,tile=10x12", "-frames:v", "1", "final_sheet.jpg")
    os.chdir(cwd)
    print(f"final {os.path.join(b, 'final.mp4')}  {total:.1f}s")


if __name__ == "__main__":
    main()

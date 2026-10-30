"""Assemble one Short locally with ffmpeg only (light; no Remotion/Blender on this PC).
py tools/assemble.py shorts/<nn>
Needs: script.json, durations.json, vo/full.wav (tools/tts.py), source/source.mp4 (tools/get_source.py),
       build/inserts/S<nn>L<id>.mp4 (GitHub 'inserts' workflow artifact).
Out:   shorts/<nn>/build/final.mp4 (1080x1920, 30 fps) + final_sheet.jpg
Rules (research/monetization_system.md): source shots <= 2 s, no source audio, crop above the source's burned-in captions."""
import json, os, random, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

FF = os.environ.get("FFMPEG") or (r"C:\Users\hp\Desktop\100\tools\ffmpeg\ffmpeg.exe" if os.name == "nt" else "ffmpeg")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "tools", "fonts", "BebasNeue-Regular.ttf")
FPS, W, H, GAP = 30, 1080, 1920, 0.04
SAFE_H = 930  # source rows kept from the top: drops the bottom band where Project Farm burns its captions


def ff(*a):
    r = subprocess.run([FF, "-v", "error", "-y", *a], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-1500:])


def sec(t):
    m, s = t.split(":")
    return int(m) * 60 + float(s)


SPEED = 1.5  # source footage plays 1.5x (research/tnp_pacing.md)


def shots_for(line, dur, rnd):
    """Split the line's source ranges into 0.5-1.0 s OUTPUT shots (each eats 1.5x that of source), cycling ranges."""
    ranges = [tuple(map(sec, c.split("-"))) for c in line["src"]]
    out, used, k = [], 0.0, 0
    cursor = {i: a for i, (a, b) in enumerate(ranges)}
    while used < dur - 1e-3:
        i = k % len(ranges)
        a, b = ranges[i]
        ln = min(rnd.uniform(0.5, 1.0), dur - used)
        st = cursor[i]
        if st + ln * SPEED > b:
            st = a
        cursor[i] = st + ln * SPEED
        out.append((st, ln, k % 2))
        used += ln
        k += 1
    return out


def cut(src, st, ln, zoom, out):
    """4:5 window (subject kept) over a blurred copy; footage at SPEED; constant push-in (zoom=0) or pull-out (zoom=1)."""
    h = SAFE_H if not zoom else int(SAFE_H * 0.86)
    w = int(h * 4 / 5) // 2 * 2
    y = (SAFE_H - h) // 2
    fh = 1350
    nf = max(round(ln * FPS), 1)
    z = f"1+0.14*on/{nf}" if not zoom else f"1.14-0.14*on/{nf}"
    vf = (f"[0:v]setpts=PTS/{SPEED},fps={FPS},crop=iw:{SAFE_H}:0:0,split[a][b];"
          f"[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=6:2,eq=brightness=-0.18:saturation=0.8,scale={W}:{H}[bg];"
          f"[b]crop={w}:{h}:(iw-{w})/2:{y},scale={W}:{fh}:flags=lanczos,"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{fh}:fps={FPS},eq=contrast=1.06:saturation=1.12[fg];"
          f"[bg][fg]overlay=0:{(H - fh) // 2 - 120},setsar=1[v]")
    ff("-ss", f"{st:.3f}", "-t", f"{ln * SPEED + 0.2:.3f}", "-i", src, "-an", "-filter_complex", vf, "-map", "[v]", "-frames:v", str(round(ln * FPS)),
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-threads", "1", "-x264-params", "rc-lookahead=8:ref=1:sync-lookahead=0", "-pix_fmt", "yuv420p", out)


def fit(ins, dur, out):
    n = round(dur * FPS)
    ff("-threads", "1", "-i", ins, "-an", "-vf", f"fps={FPS},scale={W}:{H},setsar=1,tpad=stop_mode=clone:stop_duration=2", "-frames:v", str(n),
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-threads", "1", "-x264-params", "rc-lookahead=8:ref=1:sync-lookahead=0", "-pix_fmt", "yuv420p", out)


def png_mark(kind, path):
    im = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == "q":
        f = ImageFont.truetype(FONT, 400)
        d.text((210, 220), "?", font=f, fill=(255, 212, 0, 255), anchor="mm", stroke_width=14, stroke_fill=(0, 0, 0, 255))
    else:
        d.ellipse((20, 20, 400, 400), fill=(255, 59, 59, 235))
        d.line((120, 120, 300, 300), fill="white", width=44)
        d.line((300, 120, 120, 300), fill="white", width=44)
    im.save(path)


def ass_time(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def captions(lines, starts, durs, path):
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: W,Bebas Neue,170,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,2,0,1,10,4,2,40,40,330,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    for l, st, du in zip(lines, starts, durs):
        words = l["text"].split()
        wts = [len(re.sub(r"\W", "", w)) + 2 for w in words]
        speak = du - GAP
        t = st
        for w, wt in zip(words, wts):
            d = speak * wt / sum(wts)
            clean = re.sub(r"[^\w'%-]", "", w).upper()
            col = r"{\c&H0000D4FF&}" if re.search(r"\d", clean) or clean in ("WELDER", "DEAD", "BOMB", "FIFTEEN", "EPSOM", "CRYSTALS") else ""
            ev.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + d)},W,,0,0,0,,{{\\fscx78\\fscy78\\t(0,70,\\fscx100\\fscy100)}}{col}{clean}")
            t += d
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def sfx(path, kind):
    g = {
        "whoosh": ["-f", "lavfi", "-i", "anoisesrc=d=0.45:c=pink:a=0.6", "-af", "bandpass=f=1800:width_type=o:w=2,afade=t=in:d=0.18,afade=t=out:st=0.2:d=0.25,volume=0.6"],
        "pop": ["-f", "lavfi", "-i", "sine=f=880:d=0.09", "-af", "afade=t=out:st=0.02:d=0.07,volume=0.5"],
        "boom": ["-f", "lavfi", "-i", "anoisesrc=d=0.9:c=brown:a=1", "-af", "lowpass=f=180,afade=t=out:st=0.1:d=0.8,volume=2.2"],
        "ding": ["-f", "lavfi", "-i", "sine=f=1320:d=0.7", "-af", "afade=t=out:st=0.05:d=0.65,volume=0.45"],
        "buzz": ["-f", "lavfi", "-i", "sine=f=140:d=0.35", "-af", "afade=t=out:st=0.2:d=0.15,volume=0.5"],
    }[kind]
    ff(*g, "-ar", "44100", "-ac", "2", path)


def main():
    sd = sys.argv[1]
    b = os.path.join(sd, "build")
    os.makedirs(os.path.join(b, "seg"), exist_ok=True)
    d = json.load(open(os.path.join(sd, "script.json"), encoding="utf-8"))
    du = json.load(open(os.path.join(sd, "durations.json")))
    lines = d["lines"]
    durs = [du[str(l["id"])] for l in lines]
    starts = [sum(durs[:i]) for i in range(len(durs))]
    total = sum(durs)
    rnd = random.Random(d["short"])
    src = os.path.join(sd, "source", "source.mp4")
    segs = []
    video = os.path.join(b, "video.mp4")
    fx_only = "--fx-only" in sys.argv and os.path.exists(video)
    for l, dur in ([] if fx_only else zip(lines, durs)):
        if l["original"]:
            o = os.path.join(b, "seg", f"L{l['id']:02d}.mp4")
            fit(os.path.join(b, "inserts", f"S{d['short']}L{l['id']}.mp4"), dur, o)
            segs.append(o)
        else:
            sh = shots_for(l, dur, rnd)
            frames = [round(x[1] * FPS) for x in sh]
            frames[-1] += round(dur * FPS) - sum(frames)
            for j, ((st, ln, z), nf) in enumerate(zip(sh, frames)):
                o = os.path.join(b, "seg", f"L{l['id']:02d}_{j}.mp4")
                cut(src, st, nf / FPS, z, o)
                segs.append(o)
        print("line", l["id"], "ok", flush=True)
    if not fx_only:
        lst = os.path.join(b, "seg", "list.txt")
        open(lst, "w").write("".join(f"file '{os.path.abspath(s)}'\n".replace("\\", "/") for s in segs))
        ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video)

    for k in ("q", "x"):
        png_mark(k, os.path.join(b, f"mark_{k}.png"))
    for k in ("whoosh", "pop", "boom", "ding", "buzz"):
        sfx(os.path.join(b, f"sfx_{k}.wav"), k)
    os.makedirs(os.path.join(b, "fonts"), exist_ok=True)
    import shutil
    shutil.copy(FONT, os.path.join(b, "fonts", os.path.basename(FONT)))
    captions(lines, starts, durs, os.path.join(b, "captions.ass"))

    # events: whoosh on every source<->insert switch, "?" + pop on the hook (first line) and loop (last line),
    # plus per-line extras from script.json: "sfx": [[kind, seconds_into_line], ...], "mark": ["x", seconds_into_line]
    # (negative seconds count back from the end of the line).
    at = lambda st, du_, s: st + (s if s >= 0 else du_ + s)
    ev = [("whoosh", s) for (l, s), prev in zip(zip(lines, starts), [None] + lines[:-1]) if prev and prev["original"] != l["original"]]
    ev += [("pop", starts[0] + 0.15), ("pop", starts[-1] + 0.15)]
    q_win = [(starts[0] + 0.15, starts[0] + durs[0]), (starts[-1] + 0.15, starts[-1] + durs[-1])]
    x_win = []
    for l, st, du_ in zip(lines, starts, durs):
        ev += [(k, at(st, du_, s)) for k, s in l.get("sfx", [])]
        if l.get("mark"):
            x_win.append((at(st, du_, l["mark"][1]), st + du_))
            ev.append(("buzz", at(st, du_, l["mark"][1])))
    inputs = ["-i", video, "-i", os.path.join(sd, "vo", "full.wav"), "-i", os.path.join(b, "mark_q.png"), "-i", os.path.join(b, "mark_x.png")]
    for k, _ in ev:
        inputs += ["-i", os.path.join(b, f"sfx_{k}.wav")]
    music = os.path.join(ROOT, "tools", "music", "bed.wav")
    win = lambda ws: "+".join(f"between(t,{a:.2f},{b_:.2f})" for a, b_ in ws) or "0"
    fc = [
        f"[0:v][2:v]overlay=x=640:y=260:enable='{win(q_win)}'[v1]",
        f"[v1][3:v]overlay=x=330:y=640:enable='{win(x_win)}'[v2]",
        "[v2]subtitles=captions.ass:fontsdir=fonts[v]",
    ]
    mix = ["[1:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[vo]"]
    for j, (k, t) in enumerate(ev):
        ms = int(max(t, 0) * 1000)
        mix.append(f"[{4 + j}:a]adelay={ms}|{ms},volume=0.55[e{j}]")
    mix.append(f"[{4 + len(ev)}:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.16,afade=t=out:st={max(total - 0.6, 0):.2f}:d=0.6[mus]")
    mix.append("[vo]" + "".join(f"[e{j}]" for j in range(len(ev))) + f"[mus]amix=inputs={2 + len(ev)}:normalize=0:duration=first,alimiter=limit=0.95[a]")
    final = os.path.join(b, "final.mp4")
    inputs = [os.path.abspath(x) if i % 2 else x for i, x in enumerate(inputs)]
    cwd = os.getcwd()
    os.chdir(b)
    vin = inputs[:8]
    ain = inputs[8:]
    ff("-filter_threads", "1", *vin, "-filter_complex", ";".join(fc), "-map", "[v]", "-t", f"{total:.3f}",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-threads", "1", "-x264-params", "rc-lookahead=8:ref=1:sync-lookahead=0", "-pix_fmt", "yuv420p", "video_fx.mp4")
    mix = [m.replace("[1:a]", "[0:a]") for m in mix]
    mix = [re.sub(r"\[(\d+):a\]", lambda m: f"[{int(m.group(1)) - 3}:a]" if int(m.group(1)) >= 4 else m.group(0), m) for m in mix]
    ain += ["-stream_loop", "-1", "-i", music]
    ff(*inputs[2:4], *ain, "-filter_complex", ";".join(mix), "-map", "[a]", "-t", f"{total:.3f}", "-c:a", "pcm_s16le", "audio.wav")
    ff("-i", "video_fx.mp4", "-i", "audio.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
       "-movflags", "+faststart", "-shortest", "final.mp4")
    ff("-i", "final.mp4", "-vf", "fps=2,scale=216:-1,tile=10x12", "-frames:v", "1", "final_sheet.jpg")
    os.chdir(cwd)
    print(f"final {final}  {total:.1f}s")


if __name__ == "__main__":
    main()

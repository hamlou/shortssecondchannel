"""Footage-first scripting: contact sheets of the whole source (keyframes, each tile stamped m:ss) to pick the moments a Short is built on.
py tools/scan_source.py shorts/<nn> [every_s=4]  -> shorts/<nn>/build/scan_<k>.jpg (80 tiles each)"""
import os, subprocess, sys
from PIL import Image, ImageDraw

FF = os.environ.get("FFMPEG") or (r"C:\Users\hp\Desktop\100\tools\ffmpeg\ffmpeg.exe" if os.name == "nt" else "ffmpeg")
TW, COLS, ROWS = 200, 10, 8


def main():
    sd = sys.argv[1]
    every = float(sys.argv[2]) if len(sys.argv) > 2 else 4
    out = os.path.join(sd, "build")
    os.makedirs(out, exist_ok=True)
    r = subprocess.run([FF, "-v", "error", "-threads", "1", "-skip_frame", "nokey", "-i", os.path.join(sd, "source", "source.mp4"),
                        "-vf", f"scale={TW}:-2,showinfo", "-fps_mode", "passthrough", "-f", "image2pipe", "-c:v", "bmp", "-"],
                       capture_output=True)
    import io, re
    times = [float(x) for x in re.findall(rb"pts_time:([\d.]+)", r.stderr)]
    data, frames, i = r.stdout, [], 0
    while i < len(data):
        n = int.from_bytes(data[i + 2:i + 6], "little")
        frames.append(Image.open(io.BytesIO(data[i:i + n])).convert("RGB"))
        i += n
    keep, last = [], -1e9
    for t, im in zip(times, frames):
        if t - last >= every:
            keep.append((t, im))
            last = t
    th = keep[0][1].size[1]
    per = COLS * ROWS
    for k in range(0, len(keep), per):
        sheet = Image.new("RGB", (COLS * TW, ROWS * th))
        for j, (t, im) in enumerate(keep[k:k + per]):
            d = ImageDraw.Draw(im)
            d.rectangle((0, 0, 44, 13), fill="black")
            d.text((2, 1), f"{int(t // 60)}:{int(t % 60):02d}", fill="yellow")
            sheet.paste(im, (j % COLS * TW, j // COLS * th))
        sheet.save(os.path.join(out, f"scan_{k // per}.jpg"), quality=82)
    print(len(keep), "tiles,", -(-len(keep) // per), "sheets")


if __name__ == "__main__":
    main()

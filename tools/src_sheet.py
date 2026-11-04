"""Contact sheet of every source range a script uses (3 frames each, labelled L<id> m:ss) to verify each shot matches its line.
py tools/src_sheet.py shorts/<nn>  -> shorts/<nn>/build/src_sheet.jpg"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

FF = os.environ.get("FFMPEG") or (r"C:\Users\hp\Desktop\100\tools\ffmpeg\ffmpeg.exe" if os.name == "nt" else "ffmpeg")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sec = lambda t: int(t.split(":")[0]) * 60 + float(t.split(":")[1])


def main():
    sd = sys.argv[1]
    d = json.load(open(os.path.join(sd, "script.json"), encoding="utf-8"))
    src = os.path.join(sd, "source", "source.mp4")
    tmp = os.path.join(sd, "build", "srcframes")
    os.makedirs(tmp, exist_ok=True)
    tiles = []
    font = ImageFont.truetype(os.path.join(ROOT, "tools", "fonts", "BebasNeue-Regular.ttf"), 34)
    for l in d["lines"]:
        for w, c in l.get("beats", [[None, c] for c in l.get("src", [])]):
            if c.startswith("ai:"):
                continue
            a, b = map(sec, c.split("-"))
            for k, t in enumerate([a + 0.1, (a + b) / 2, b - 0.15]):
                p = os.path.join(tmp, f"{len(tiles):03d}.jpg")
                subprocess.run([FF, "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", src, "-frames:v", "1", "-vf", "scale=400:-1", p])
                im = Image.open(p).convert("RGB")
                dr = ImageDraw.Draw(im)
                dr.rectangle((0, 0, 400, 40), fill=(0, 0, 0))
                dr.text((6, 2), f"L{l['id']}  {int(t // 60)}:{t % 60:04.1f}  {(w or l['text'])[:28]}", font=font, fill=(255, 212, 0))
                tiles.append(im)
    cols = 6
    w, h = tiles[0].size
    sheet = Image.new("RGB", (cols * w, -(-len(tiles) // cols) * h))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(os.path.join(sd, "build", "src_sheet.jpg"), quality=80)
    print("src_sheet", len(tiles), "frames")


if __name__ == "__main__":
    main()

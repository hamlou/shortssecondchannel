"""Compact timestamped transcript from a YouTube auto-sub VTT: py tools/transcript.py shorts/<nn> -> source/transcript.txt ([m:ss] every ~15 s)."""
import re, sys, os
p = os.path.join(sys.argv[1], "source")
t = open(os.path.join(p, "source.en.vtt"), encoding="utf-8").read()
out, last = [], None
for blk in t.split("\n\n"):
    m = re.match(r"(\d+):(\d+):([\d.]+) -->", blk)
    if not m:
        continue
    s = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    ls = [re.sub(r"<[^>]+>", "", l).strip() for l in blk.split("\n")[1:] if l.strip() and "-->" not in l]
    if ls and ls[-1] != last:
        out.append((s, ls[-1]))
        last = ls[-1]
res, cur, ts = [], "", 0
for s, x in out:
    if s - ts >= 15 and cur:
        res.append(f"[{int(ts // 60)}:{int(ts % 60):02d}] {cur.strip()}")
        cur, ts = "", s
    cur += x + " "
res.append(f"[{int(ts // 60)}:{int(ts % 60):02d}] {cur.strip()}")
open(os.path.join(p, "transcript.txt"), "w", encoding="utf-8").write("\n".join(res))
print(len(" ".join(res).split()), "words")

"""Write render/src/gen.json for one Short from its script.json + durations.json. py tools/gen_root.py shorts/<nn>"""
import json, math, os, sys
sd = sys.argv[1]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(sd, "script.json"), encoding="utf-8"))
du = json.load(open(os.path.join(sd, "durations.json")))
lines = [{"id": l["id"], "frames": math.ceil(du[str(l["id"])] * 30), "insert": l.get("insert", {})} for l in d["lines"] if l["original"]]
json.dump({"short": d["short"], "lines": lines}, open(os.path.join(root, "render", "src", "gen.json"), "w"), indent=1)
print(d["short"], [l["id"] for l in lines])

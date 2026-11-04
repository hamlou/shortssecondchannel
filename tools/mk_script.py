"""Write shorts/<nn>/script.json from a compact spec (footage-first scripting helper).
from mk_script import mk; mk("12", "youtube-id", "title", "what the Short shows (desc)", "#tags", "facts", L, safety=None)
L = [(id, "story"|"analysis", text, beats, extras), ...]"""
import json, os

RULES = "zero commas, no fragment chains, no dashes/semicolons/colons; connected sentences with and/so/but/because/which"


def mk(n, vid, title, desc, tags, facts, L, safety="on-screen safety where relevant; no step-by-step dangerous settings", notes="Footage-first (owner 4 Nov 2026)."):
    d = {"short": n, "source": f"https://youtu.be/{vid}", "max_seconds": 59, "source_audio": False,
         "lines": [dict(id=i, type=t, text=x, beats=b, **e) for i, t, x, b, e in L],
         "facts_checked": facts, "safety": safety,
         "title": f"{title} (@ProjectFarm/YT)",
         "description": f"{desc} Original video: @ProjectFarm https://youtu.be/{vid} | Science explained + AI visuals by our channel. "
                        f"Narration: synthetic voice (Kokoro, Apache 2.0). #shorts {tags}",
         "speech_rules": RULES, "notes": notes}
    os.makedirs(f"shorts/{n}", exist_ok=True)
    json.dump(d, open(f"shorts/{n}/script.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

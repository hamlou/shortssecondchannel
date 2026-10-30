import json
A, S = "analysis", "story"
def L(i, t, ty, src=None, ins=None, ph=""):
    d = {"id": i, "phase": ph, "type": ty, "text": t, "src": src or [], "original": ins is not None}
    if ins: d["insert"] = ins
    return d
src = "https://youtu.be/vtUtORbNLsA"
lines = [
 L(1, "Which 150 dollar engine can actually keep up with a 600 dollar Honda?", S, ["0:15-0:19", "1:16-1:20"], ph="hook"),
 L(2, "The Honda clone even copies the red paint and its sticker says 7.5 horsepower while the real Honda says 5.5.", S, ["0:30-0:34", "0:55-0:59"], ph="rising"),
 L(3, "But a sticker is just a sticker so the only way to know is to test it.", A, [], {"kind": "versus", "title": "ON THE STICKER", "left": {"label": "CLONE", "value": 7.5, "unit": "HP", "color": "y"}, "right": {"label": "HONDA", "value": 5.5, "unit": "HP", "color": "w"}}, "rising"),
 L(4, "On the vibration tester the clone shakes so hard the meter can't even read it.", S, ["4:24-4:29"], ph="conflict"),
 L(5, "Because a one cylinder engine needs a carefully weighted crankshaft to cancel its own shaking and the clone clearly skipped that.", A, [], {"kind": "crank"}, "why"),
 L(6, "Then it burns six ounces of oil a day so he tops it up twice like a leaky boat.", A, ["5:11-5:16", "5:43-5:48"], ph="conflict"),
 L(7, "That oil sneaks past the piston rings and burns which is why its spark plug is caked in carbon.", A, ["6:24-6:29"], {"kind": "rings"}, "why"),
 L(8, "And on the pull test the 7.5 horsepower clone makes 200 pounds while the 5.5 horsepower Honda makes 239.", A, ["9:05-9:10"], {"kind": "bars", "title": "PULLING FORCE", "unit": "LB", "items": [{"label": "CLONE 7.5 HP", "value": 200, "color": "r"}, {"label": "HONDA 5.5 HP", "value": 239, "color": "g"}]}, "conflict-peak"),
 L(9, "But here's the twist because Harbor Freight's 150 dollar Predator pulls 233.", S, ["9:21-9:26", "1:44-1:48"], ph="twist"),
 L(10, "That's within three percent of the Honda for way less money and it burned the least fuel of all four.", A, [], {"kind": "bars", "title": "PULL (LB) FOR THE PRICE", "unit": "LB", "items": [{"label": "HONDA $600", "value": 239, "color": "w"}, {"label": "PREDATOR $150", "value": 233, "color": "g"}]}, "payoff"),
 L(11, "So which one would you buy?", S, ["1:44-1:47"], ph="loop")]
d = {"short": "04", "source": src, "max_seconds": 59, "source_audio": False, "lines": lines,
     "facts_checked": "numbers from shorts/04/source/transcript.txt (7.5 vs 5.5 hp sticker 0:55/1:16; vibration 4:24; 178 g oil/24h 5:27, topped twice 5:43; carbon plug 6:29; pull 200/239/233 lb 9:05-9:21; fuel 56/57/59/60 lb 8:49); src timestamps verified on frames before render",
     "safety": "none needed", "title": "Which $150 Engine Can Keep Up With a $600 Honda? 🤔 (@ProjectFarm/YT)",
     "description": "Project Farm ran a Honda, a Honda clone, a Predator and a Briggs for 48 hours and pulled a trailer with each. The fake's sticker lies, and the cheap surprise is the Predator. Original video: @ProjectFarm " + src + " | Science explained + animations by our channel. Narration: synthetic voice (Kokoro, Apache 2.0). #shorts #engine #honda #mechanic #smallengine",
     "speech_rules": "zero commas, no fragment chains, no dashes/semicolons/colons"}
json.dump(d, open("shorts/04/script.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

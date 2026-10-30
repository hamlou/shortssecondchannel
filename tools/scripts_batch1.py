"""One-off: writes script.json for Shorts 02 03 05 08 09 10 11 (batch 1, 30 Oct 2026). Numbers from each source transcript."""
import json, os

A, S = "analysis", "story"


def L(i, t, ty, src=None, ins=None, ph=""):
    d = {"id": i, "phase": ph, "type": ty, "text": t, "src": src or [], "original": ins is not None}
    if ins:
        d["insert"] = ins
    return d


shorts = {
    "02": dict(source="https://youtu.be/st8dkGzJWtg", title="Can BRAKE FLUID Free a Rusted Bolt? 🤔 (@ProjectFarm/YT)",
               desc="Project Farm dripped six fluids on rusted bolts and even mixed them all into one super oil. The winner came down to one thing: how thin the fluid is.",
               tags="#shorts #rust #mechanic #diy #science",
               lines=[
                   L(1, "Can brake fluid loosen a rusted bolt better than the stuff that's made for it?", S, ["2:06-2:10", "3:15-3:18"], ph="hook"),
                   L(2, "So he rusts a pile of bolts on purpose and drips six different fluids on them.", S, ["1:21-1:25", "2:23-2:27"], ph="rising"),
                   L(3, "And the whole trick is capillary action because a thin liquid gets pulled into tiny gaps the same way a paper towel drinks a spill.", A, [], {"kind": "capillary", "mode": "pull"}, "why"),
                   L(4, "The brake fluid just sits on the washer like it's not even trying.", S, ["3:15-3:20"], ph="conflict"),
                   L(5, "But when he cuts the bolt open it crept all the way to the bottom.", A, ["4:58-5:02"], {"kind": "stamp", "big": "ALL THE WAY DOWN", "sub": "BRAKE FLUID", "color": "g"}, "twist"),
                   L(6, "Fluid Film coats everything like slime but it's way too thick to squeeze into the threads.", A, ["5:15-5:20"], {"kind": "capillary", "mode": "thick"}, "why"),
                   L(7, "Then viewers begged him to mix every fluid into one super oil.", S, ["8:34-8:40"], ph="conflict"),
                   L(8, "And the mix never crept down so a nut that was only hand tight needed 56 foot pounds to break free.", A, ["9:09-9:14"],
                     {"kind": "versus", "title": "TO BREAK IT LOOSE", "left": {"label": "HAND TIGHT", "value": 0, "unit": "FT-LB", "color": "y"}, "right": {"label": "SUPER MIX", "value": 56, "unit": "FT-LB", "color": "r"}}, "conflict-peak"),
                   L(9, "So the winner is Seafoam Deep Creep with CRC Knocker Loose right behind it.", S, ["10:03-10:08"], {"kind": "podium", "items": ["SEAFOAM DEEP CREEP", "CRC KNOCK'ER LOOSE"]}, "payoff"),
                   L(10, "Because in a rusty thread the gaps are microscopic so only the thinnest fluid gets in.", A, [], {"kind": "capillary", "mode": "race"}, "lesson"),
                   L(11, "So would you trust brake fluid on your next rusted bolt?", S, ["2:06-2:09"], ph="loop")]),
    "03": dict(source="https://youtu.be/4pXM5bHSk2Y", title="$30 FAKE Makita vs The Real One 😳 (@ProjectFarm/YT)",
               desc="A $30 knockoff claims almost double the torque of a $138 Makita. Project Farm measured both, and the reason the real one wins is hidden inside.",
               tags="#shorts #tools #makita #mechanic #engineering",
               lines=[
                   L(1, "This thirty dollar fake Makita says it makes almost twice the torque of the real one.", S, ["0:45-0:49", "1:01-1:04"], ph="hook"),
                   L(2, "And the real one costs 138 dollars and they even weigh the same down to one single gram.", S, ["1:16-1:20"], ph="rising"),
                   L(3, "So on paper you'd be crazy to pay five times more.", A, [],
                     {"kind": "versus", "title": "ON THE BOX", "left": {"label": "FAKE $30", "value": 384, "unit": "FT-LB", "color": "y"}, "right": {"label": "MAKITA $138", "value": 210, "unit": "FT-LB", "color": "w"}}, "rising"),
                   L(4, "But on the torque rig the fake makes just 91 foot pounds.", S, ["5:18-5:23"], ph="conflict"),
                   L(5, "That's less than a quarter of the 384 printed on the box so that spec sheet is basically fan fiction.", A, [], {"kind": "claim", "claimed": 384, "actual": 91, "unit": "FT-LB", "label": "FAKE MAKITA"}, "conflict-peak"),
                   L(6, "And the real Makita hits 178 even though it only promised 210.", S, ["5:49-5:54"], ph="comeback"),
                   L(7, "Because inside every impact wrench a spinning hammer slams into the anvil thousands of times a minute.", A, [], {"kind": "hammer", "mode": "explain"}, "why"),
                   L(8, "And the Makita's hammer is 44 grams heavier and spins faster so every single hit carries more energy.", A, [], {"kind": "hammer", "mode": "compare", "a": 253, "b": 297}, "why"),
                   L(9, "So it pulls lug nuts in 35 seconds while the fake needs 49.", S, ["6:49-6:53", "7:06-7:10"], ph="payoff"),
                   L(10, "Then he drops both onto an anvil and the fake's handle snaps.", S, ["10:00-10:05"], ph="twist"),
                   L(11, "But for thirty bucks you still get a brushless motor which is almost impossible to find at that price.", A, ["11:02-11:06"], {"kind": "stamp", "big": "STILL A DEAL?", "sub": "BRUSHLESS FOR $30", "color": "y"}, "verdict"),
                   L(12, "So would you pay five times more for the real one?", S, ["1:01-1:04"], ph="loop")]),
    "05": dict(source="https://youtu.be/V7-ghrTqA44", title="Why Dead Batteries BOUNCE 🔋 + Which AA Lasts Longest (@ProjectFarm/YT)",
               desc="A dead AA bounces and a new one thuds, and there's real chemistry behind it. Then Project Farm drained every brand to find the best battery per penny.",
               tags="#shorts #batteries #science #experiment #lifehack",
               lines=[
                   L(1, "Why does a dead battery bounce and a brand new one just thuds?", S, ["1:40-1:44", "1:50-1:54"], ph="hook"),
                   L(2, "Because inside a fresh AA the zinc is a soft gel that soaks up the hit.", A, [], {"kind": "zinc", "mode": "gel"}, "why"),
                   L(3, "And as the battery drains that zinc turns into zinc oxide which is stiff and springy so the dead one bounces.", A, [], {"kind": "zinc", "mode": "oxide"}, "why"),
                   L(4, "Then he drains every brand on a machine to see which one really lasts.", S, ["2:18-2:22", "3:04-3:08"], ph="rising"),
                   L(5, "The dollar store battery costs thirteen cents and dies in 26 minutes.", S, ["3:35-3:40"], ph="conflict"),
                   L(6, "And the Duracell lasts 381 minutes which is almost fifteen times longer.", A, [],
                     {"kind": "bars", "title": "MINUTES OF POWER", "unit": "MIN", "items": [{"label": "DOLLAR STORE", "value": 26, "color": "r"}, {"label": "DURACELL", "value": 381, "color": "g"}]}, "conflict"),
                   L(7, "The Energizer lithium crushes everyone at 723 minutes but it costs a dollar fifty each.", S, ["5:45-5:50"], ph="rising"),
                   L(8, "But the real winner is the one nobody expected.", S, ["4:25-4:29"], ph="twist"),
                   L(9, "Amazon Basics gives you 32 milliamp hours for every single penny which beats every brand he tested.", A, [],
                     {"kind": "bars", "title": "POWER PER PENNY", "unit": "mAh", "items": [{"label": "AMAZON BASICS", "value": 32, "color": "g"}, {"label": "ENERGIZER", "value": 26, "color": "y"}]}, "payoff"),
                   L(10, "So the best battery and the best deal are two completely different things.", A, [], {"kind": "stamp", "big": "BEST BATTERY", "sub": "IS NOT THE BEST DEAL", "color": "y"}, "lesson"),
                   L(11, "And now you know why the dead one bounces.", S, ["1:50-1:53"], ph="loop")]),
    "08": dict(source="https://youtu.be/-zHlxeu_yuM", title="He Tested 70 Year Old Motor Oil 😱 (@ProjectFarm/YT)",
               desc="A viewer mailed Project Farm a welded steel box with a 1950s can of oil inside. The lab report explains why it fails, and it's not what you'd guess.",
               tags="#shorts #cars #oil #mechanic #science",
               lines=[
                   L(1, "Someone mailed him a steel box bolted shut with a coffee can welded inside.", S, ["0:15-0:20", "0:52-0:56"], ph="hook"),
                   L(2, "And inside that can is motor oil from the 1950s.", S, ["1:00-1:05"], ph="rising"),
                   L(3, "So would seventy year old oil still protect an engine?", S, ["1:57-2:02"], ph="question"),
                   L(4, "He cooks it at 410 degrees for two hours right next to modern oil.", S, ["3:00-3:05", "3:48-3:52"], ph="rising"),
                   L(5, "And the old oil loses 42 percent more weight which means it's literally cooking off into the air.", A, [],
                     {"kind": "bars", "title": "GRAMS LOST TO HEAT", "unit": "g", "items": [{"label": "MODERN", "value": 6.63, "color": "y"}, {"label": "1950s", "value": 9.43, "color": "r"}]}, "conflict"),
                   L(6, "Then both go in a minus forty freezer and the old oil barely moves.", S, ["9:18-9:24"], ph="conflict"),
                   L(7, "And after a run in an engine the cylinder head is covered in crusty deposits.", S, ["8:20-8:25"], ph="conflict-peak"),
                   L(8, "And the lab report explains it because the old oil has just 6 parts per million of calcium.", A, [], {"kind": "stamp", "big": "6 PPM", "sub": "CALCIUM DETERGENT", "color": "r"}, "why"),
                   L(9, "Calcium is the detergent that grabs soot and acid and keeps them floating so without it everything turns to sludge.", A, [], {"kind": "detergent"}, "why"),
                   L(10, "And its acid fighting reserve called TBN is zero point four while the modern oil sits at six point two which is fifteen times more.", A, [],
                     {"kind": "bars", "title": "ACID FIGHTING RESERVE (TBN)", "unit": "", "items": [{"label": "1950s", "value": 0.4, "color": "r"}, {"label": "MODERN", "value": 6.2, "color": "g"}]}, "payoff"),
                   L(11, "So the oil is technically still good but it would turn acidic and sludge up your engine fast.", S, ["11:02-11:06"], ph="verdict"),
                   L(12, "So would you put it in your car?", S, ["0:52-0:55"], ph="loop")]),
    "09": dict(source="https://youtu.be/ja0ioX6GSz0", title="Is Your Brita Actually Cleaning Your Water? 🤔 (@ProjectFarm/YT)",
               desc="Project Farm measured dissolved solids through 11 filters, including a $5 homemade one. The difference comes down to carbon vs ion exchange.",
               tags="#shorts #water #brita #science #home",
               lines=[
                   L(1, "Is your Brita actually cleaning your water or just making it taste better?", S, ["3:13-3:17", "3:26-3:30"], ph="hook"),
                   L(2, "His tap water reads 259 parts per million of dissolved stuff.", S, ["0:59-1:03"], ph="rising"),
                   L(3, "Then he builds a filter from a plastic bottle with sand and carbon for five bucks and it drops to 237.", S, ["0:40-0:46", "1:03-1:06"], ph="rising"),
                   L(4, "And the 28 dollar Brita lands at 234 which is basically the same as the five dollar bottle.", A, [],
                     {"kind": "bars", "title": "DISSOLVED SOLIDS (PPM)", "unit": "", "items": [{"label": "TAP", "value": 259, "color": "w"}, {"label": "$5 BOTTLE", "value": 237, "color": "y"}, {"label": "BRITA $28", "value": 234, "color": "y"}]}, "conflict"),
                   L(5, "That's because a Brita is mostly activated carbon which grabs chlorine and bad taste but lets dissolved minerals slide right through.", A, ["12:58-13:02"], {"kind": "filter", "mode": "carbon"}, "why"),
                   L(6, "And the 300 dollar Berkey reads higher than tap water at 284 although that's common when the filters are brand new.", A, ["6:08-6:12"],
                     {"kind": "claim", "claimed": 259, "actual": 284, "unit": "PPM", "label": "BERKEY $300", "up": True}, "conflict-peak"),
                   L(7, "But the 29 dollar ZeroWater hits zero.", S, ["4:18-4:22"], ph="comeback"),
                   L(8, "Because it uses ion exchange beads that swap every dissolved mineral for the ingredients of pure water.", A, ["13:04-13:08"], {"kind": "filter", "mode": "ion"}, "why"),
                   L(9, "But a high number doesn't mean your water is unsafe because a lot of it is just calcium and magnesium.", A, [], {"kind": "stamp", "big": "HIGH IS NOT UNSAFE", "sub": "MOSTLY MINERALS", "color": "y"}, "honest"),
                   L(10, "So what does your water read?", S, ["0:59-1:02"], ph="loop")]),
    "10": dict(source="https://youtu.be/cM6rVfUnYP8", title="These Car Ramps Held 25000 lb… So Why Are They Dangerous? 😳 (@ProjectFarm/YT)",
               desc="Project Farm crushed 11 car ramps in a hydraulic press and the cheap plastic ones were shockingly strong. The real danger showed up on smooth concrete.",
               tags="#shorts #cars #mechanic #safety #engineering",
               lines=[
                   L(1, "Why would a car ramp that holds 25000 pounds still be a death trap?", S, ["14:23-14:27", "7:28-7:32"], ph="hook"),
                   L(2, "He crushes eleven brands in a hydraulic press and the 60 dollar plastic ramps take almost 25000 pounds.", S, ["14:07-14:12", "14:23-14:27"], ph="rising"),
                   L(3, "That's almost eight times their rating because those plastic ribs spread the load like a honeycomb.", A, [], {"kind": "ribs"}, "why"),
                   L(4, "Meanwhile a pair of steel ramps folds under a tractor.", S, ["13:35-13:41"], ph="conflict"),
                   L(5, "Because thin steel buckles once it starts to bend while those plastic ribs keep sharing the load.", A, [], {"kind": "ribs", "mode": "buckle"}, "why"),
                   L(6, "But the scary part isn't crushing at all.", S, ["7:28-7:31"], ph="twist"),
                   L(7, "On smooth concrete almost every ramp slides and two of them shoot out from under a car.", S, ["7:28-7:34", "8:16-8:20"], ph="conflict-peak"),
                   L(8, "And that's friction because a tire climbing or braking shoves the ramp forward and one tiny rubber stop can't hold it.", A, [], {"kind": "rampforce"}, "why"),
                   L(9, "A damp towel under the ramps helped most of them grip.", S, ["1:15-1:20"], ph="comeback"),
                   L(10, "So cheap plastic is strong enough but you need grip and a parking brake before you crawl under.", A, [], {"kind": "stamp", "big": "GRIP + PARKING BRAKE", "sub": "BEFORE YOU CRAWL UNDER", "color": "g"}, "lesson"),
                   L(11, "So is your car ramp a death trap?", S, ["7:30-7:33"], ph="loop")]),
    "11": dict(source="https://youtu.be/fm2CE2e_3To", title="Which Drain Cleaner Actually Eats Hair? 🧪 (@ProjectFarm/YT)",
               desc="Project Farm soaked hair, soap, grease and even tape in every kind of drain opener. Plain lye won on hair, and the reason is simple chemistry.",
               tags="#shorts #plumbing #chemistry #home #science",
               lines=[
                   L(1, "Which drain cleaner actually eats a hair clog?", S, ["6:59-7:03"], ph="hook"),
                   L(2, "He drops hair and soap and bacon grease and even tape into every product for twelve hours.", S, ["2:06-2:10", "4:49-4:53"], ph="rising"),
                   L(3, "And the clear winner on hair is plain lye.", S, ["7:00-7:04"], ph="payoff-early"),
                   L(4, "Because hair is made of protein and lye chops those protein chains apart until the clog dissolves.", A, [], {"kind": "protein"}, "why"),
                   L(5, "Drano and Liquid Plumber come close because they're mostly lye too with some bleach mixed in.", A, ["2:25-2:30"],
                     {"kind": "bars", "title": "HAIR CLOG GRADE", "unit": "", "grades": True,
                      "items": [{"label": "LYE", "value": 3, "color": "g"}, {"label": "DRANO", "value": 3, "color": "g"}, {"label": "ACIDS", "value": 2, "color": "y"}, {"label": "ENZYMES", "value": 1, "color": "r"}]}, "why"),
                   L(6, "But the enzyme sticks just turn everything blue.", S, ["5:55-6:00"], ph="conflict"),
                   L(7, "And the acids eat a carrot but also strip the plating right off a steel pipe.", S, ["10:05-10:09", "7:45-7:50"], ph="conflict"),
                   L(8, "So acid works on food clogs but it attacks metal which is why it's only safe for plastic pipes.", A, [], {"kind": "stamp", "big": "PLASTIC PIPES ONLY", "sub": "ACID EATS METAL", "color": "r"}, "why"),
                   L(9, "And nothing touched the paper towel or the tape so for that you need a drain snake.", S, ["7:29-7:33"], ph="limit"),
                   L(10, "And never mix them because bleach plus acid makes toxic chlorine gas.", A, [], {"kind": "stamp", "big": "NEVER MIX", "sub": "BLEACH + ACID = TOXIC GAS", "color": "r"}, "safety"),
                   L(11, "So what's really clogging your drain?", S, ["4:49-4:52"], ph="loop")]),
}

for n, s in shorts.items():
    d = {"short": n, "source": s["source"], "max_seconds": 59, "source_audio": False, "lines": s["lines"],
         "facts_checked": f"numbers from source transcript shorts/{n}/source/transcript.txt; src timestamps verified on frames before render",
         "safety": "on-screen safety where relevant; no step-by-step dangerous settings",
         "title": s["title"],
         "description": s["desc"] + f" Original video: @ProjectFarm {s['source']} | Science explained + animations by our channel. "
                        "Narration: synthetic voice (Kokoro, Apache 2.0). " + s["tags"],
         "speech_rules": "zero commas, no fragment chains, no dashes/semicolons/colons"}
    os.makedirs(f"shorts/{n}", exist_ok=True)
    json.dump(d, open(f"shorts/{n}/script.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("ok", list(shorts))

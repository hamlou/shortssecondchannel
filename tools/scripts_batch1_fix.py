"""Gate fixes for batch 1 (02 03 05 08 10 11): shorter, more analysis lines, more original inserts."""
import json

A, S = "analysis", "story"


def L(i, t, ty, src=None, ins=None, ph=""):
    d = {"id": i, "phase": ph, "type": ty, "text": t, "src": src or [], "original": ins is not None}
    if ins:
        d["insert"] = ins
    return d


new = {
    "02": [
        L(1, "Can brake fluid free a rusted bolt better than the stuff that's made for it?", S, ["2:06-2:10", "3:15-3:18"], ph="hook"),
        L(2, "He rusts a pile of bolts on purpose and drips six fluids on them.", S, ["1:21-1:25", "2:23-2:27"], ph="rising"),
        L(3, "The trick is capillary action which pulls a thin liquid into tiny gaps like a paper towel drinking a spill.", A, [], {"kind": "capillary", "mode": "pull"}, "why"),
        L(4, "The brake fluid just sits on the washer like it gave up.", S, ["3:15-3:20"], ph="conflict"),
        L(5, "But when he cuts the bolt open it crept all the way to the bottom.", A, ["4:58-5:02"], {"kind": "stamp", "big": "ALL THE WAY DOWN", "sub": "BRAKE FLUID", "color": "g"}, "twist"),
        L(6, "Fluid Film coats everything like slime but it's too thick to squeeze into the threads.", A, ["5:15-5:20"], {"kind": "capillary", "mode": "thick"}, "why"),
        L(7, "Then viewers beg him to mix them all into one super oil which is risky because chemicals can react.", A, ["8:34-8:40"], ph="conflict"),
        L(8, "And the mix never crept down so a nut that was only hand tight needed 56 foot pounds.", A, ["9:09-9:14"],
          {"kind": "versus", "title": "TO BREAK IT LOOSE", "left": {"label": "HAND TIGHT", "value": 0, "unit": "FT-LB", "color": "y"}, "right": {"label": "SUPER MIX", "value": 56, "unit": "FT-LB", "color": "r"}}, "conflict-peak"),
        L(9, "The winner is Seafoam Deep Creep with CRC Knocker Loose right behind it.", S, ["10:03-10:08"], {"kind": "podium", "items": ["SEAFOAM DEEP CREEP", "CRC KNOCK'ER LOOSE"]}, "payoff"),
        L(10, "Because in rusty threads the gaps are microscopic so only the thinnest fluid gets in.", A, [], {"kind": "capillary", "mode": "race"}, "lesson"),
        L(11, "So would you trust brake fluid on your next rusted bolt?", S, ["2:06-2:09"], ph="loop")],
    "03": [
        L(1, "This thirty dollar fake Makita claims almost twice the torque of the real one.", S, ["0:45-0:49", "1:01-1:04"], ph="hook"),
        L(2, "And the real one costs 138 dollars so on paper you'd be crazy to pay five times more.", A, [],
          {"kind": "versus", "title": "ON THE BOX", "left": {"label": "FAKE $30", "value": 384, "unit": "FT-LB", "color": "y"}, "right": {"label": "MAKITA $138", "value": 210, "unit": "FT-LB", "color": "w"}}, "rising"),
        L(3, "They even weigh the same down to one single gram.", S, ["1:16-1:20"], ph="rising"),
        L(4, "But on the torque rig the fake makes just 91 foot pounds.", S, ["5:18-5:23"], ph="conflict"),
        L(5, "That's less than a quarter of what the box promised so the spec sheet is basically fan fiction.", A, [], {"kind": "claim", "claimed": 384, "actual": 91, "unit": "FT-LB", "label": "FAKE MAKITA"}, "conflict-peak"),
        L(6, "And the real Makita hits 178 out of its promised 210.", S, ["5:49-5:54"], ph="comeback"),
        L(7, "Because inside an impact wrench a spinning hammer slams the anvil thousands of times a minute.", A, [], {"kind": "hammer", "mode": "explain"}, "why"),
        L(8, "And the Makita's hammer is 44 grams heavier and spins faster so every hit carries more energy.", A, [], {"kind": "hammer", "mode": "compare", "a": 253, "b": 297}, "why"),
        L(9, "So it pulls lug nuts in 35 seconds instead of 49 which is almost a third faster.", A, ["6:49-6:52"],
          {"kind": "bars", "title": "SECONDS TO PULL LUG NUTS", "unit": "S", "lowWins": True, "items": [{"label": "FAKE", "value": 49, "color": "r"}, {"label": "MAKITA", "value": 35, "color": "g"}]}, "payoff"),
        L(10, "Then he drops both onto an anvil and the fake's handle snaps.", S, ["10:00-10:05"], ph="twist"),
        L(11, "But thirty bucks for a brushless motor is still a crazy good deal.", A, [], {"kind": "stamp", "big": "STILL A DEAL", "sub": "BRUSHLESS FOR $30", "color": "y"}, "verdict"),
        L(12, "So would you pay five times more for the real one?", S, ["1:01-1:04"], ph="loop")],
    "08": [
        L(1, "Someone mailed him a steel box bolted shut with a coffee can welded inside.", S, ["0:15-0:20", "0:52-0:56"], ph="hook"),
        L(2, "And inside is a can of 1950s motor oil so would it still protect an engine?", S, ["1:00-1:05"], ph="question"),
        L(3, "He cooks it at 410 degrees right next to modern oil.", S, ["3:00-3:05", "3:48-3:52"], ph="rising"),
        L(4, "And the old oil loses 42 percent more weight so it's literally cooking off into the air.", A, [],
          {"kind": "bars", "title": "GRAMS LOST TO HEAT", "unit": "g", "items": [{"label": "MODERN", "value": 6.63, "color": "y"}, {"label": "1950s", "value": 9.43, "color": "r"}]}, "conflict"),
        L(5, "In a minus forty freezer it barely moves.", S, ["9:18-9:24"], ph="conflict"),
        L(6, "And after an engine run the cylinder head is crusty because oil that can't take heat bakes onto hot metal.", A, ["8:20-8:25"], ph="conflict-peak"),
        L(7, "The lab report shows why because there's just 6 parts per million of calcium.", A, [], {"kind": "stamp", "big": "6 PPM", "sub": "CALCIUM DETERGENT", "color": "r"}, "why"),
        L(8, "Calcium is the detergent that grabs soot and acid so without it everything turns to sludge.", A, [], {"kind": "detergent"}, "why"),
        L(9, "And its acid fighting reserve is zero point four versus six point two for modern oil which is fifteen times less.", A, [],
          {"kind": "bars", "title": "ACID FIGHTING RESERVE (TBN)", "unit": "", "items": [{"label": "1950s", "value": 0.4, "color": "r"}, {"label": "MODERN", "value": 6.2, "color": "g"}]}, "payoff"),
        L(10, "So it still lubricates but it's like a shield that's already used up and your engine would sludge fast.", A, [], {"kind": "shield"}, "verdict"),
        L(11, "So would you put it in your car?", S, ["0:52-0:55"], ph="loop")],
    "10": [
        L(1, "Why would a car ramp that holds 25000 pounds still be a death trap?", S, ["14:23-14:27", "7:28-7:32"], ph="hook"),
        L(2, "He crushes eleven brands in a press and the 60 dollar plastic ramps take almost 25000 pounds.", S, ["14:07-14:12", "14:23-14:27"], ph="rising"),
        L(3, "That's almost eight times their rating because the plastic ribs spread the load like a honeycomb.", A, [], {"kind": "ribs"}, "why"),
        L(4, "Meanwhile a pair of steel ramps folds under a tractor.", S, ["13:35-13:41"], ph="conflict"),
        L(5, "Because thin steel buckles once it starts to bend while the ribs keep sharing the load.", A, [], {"kind": "ribs", "mode": "buckle"}, "why"),
        L(6, "So crushing is the one thing you don't need to worry about.", A, [], {"kind": "stamp", "big": "CRUSHING?", "sub": "NOT THE PROBLEM", "color": "g"}, "twist"),
        L(7, "On smooth concrete almost every ramp slides and two shoot out from under a car.", S, ["7:28-7:34", "8:16-8:20"], ph="conflict-peak"),
        L(8, "That's friction because a climbing or braking tire shoves the ramp forward and one rubber stop can't hold it.", A, [], {"kind": "rampforce"}, "why"),
        L(9, "A damp towel underneath adds grip and helped most of them which is a free fix anyone can do.", A, ["1:15-1:20"], ph="comeback"),
        L(10, "So check for grip and set the parking brake before you crawl under.", A, [], {"kind": "stamp", "big": "GRIP + PARKING BRAKE", "sub": "BEFORE YOU CRAWL UNDER", "color": "g"}, "lesson"),
        L(11, "So is your car ramp a death trap?", S, ["7:30-7:33"], ph="loop")],
    "11": [
        L(1, "Which drain cleaner actually eats a hair clog?", S, ["6:59-7:03"], ph="hook"),
        L(2, "He drops hair and soap and grease and even tape into every product for twelve hours.", S, ["2:06-2:10", "4:49-4:53"], ph="rising"),
        L(3, "And the clear winner on hair is plain lye.", S, ["7:00-7:04"], ph="payoff-early"),
        L(4, "Because hair is made of protein and lye chops those protein chains apart until the clog dissolves.", A, [], {"kind": "protein"}, "why"),
        L(5, "Drano and Liquid Plumber tie with it because they're mostly lye too with some bleach.", A, ["2:25-2:30"],
          {"kind": "bars", "title": "HAIR CLOG GRADE", "unit": "", "grades": True,
           "items": [{"label": "LYE", "value": 3, "color": "g"}, {"label": "DRANO", "value": 3, "color": "g"}, {"label": "ACIDS", "value": 2, "color": "y"}, {"label": "ENZYMES", "value": 1, "color": "r"}]}, "why"),
        L(6, "The enzyme sticks just turn everything blue because bacteria work slowly over days.", A, ["5:55-6:00"], ph="conflict"),
        L(7, "And the acids eat a carrot but also strip the plating off a steel pipe.", S, ["10:05-10:09", "7:45-7:50"], ph="conflict"),
        L(8, "So acid works on food clogs but it attacks metal which is why it's only safe for plastic pipes.", A, [], {"kind": "stamp", "big": "PLASTIC PIPES ONLY", "sub": "ACID EATS METAL", "color": "r"}, "why"),
        L(9, "Nothing touched the paper towel or tape so for solid stuff a drain snake beats every bottle here.", A, ["7:29-7:33"], ph="limit"),
        L(10, "And never mix them because bleach plus acid makes toxic chlorine gas.", A, [], {"kind": "stamp", "big": "NEVER MIX", "sub": "BLEACH + ACID = TOXIC GAS", "color": "r"}, "safety"),
        L(11, "So what's really clogging your drain?", S, ["4:49-4:52"], ph="loop")],
}
for n, lines in new.items():
    p = f"shorts/{n}/script.json"
    d = json.load(open(p, encoding="utf-8"))
    d["lines"] = lines
    json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

p = "shorts/05/script.json"
d = json.load(open(p, encoding="utf-8"))
for l in d["lines"]:
    if l["id"] == 7:
        l.update(text="The Energizer lithium lasts 723 minutes which is almost double the Duracell but it costs a dollar fifty each.", type=A)
json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("ok")

"""Add TNP-style AI beauty-clip prompts to Shorts 02-11 (replaces the old infographic 'insert' specs).
py tools/scripts_ai.py   -> rewrites shorts/<nn>/script.json in place"""
import json

# per line: ai prompts, first ("ai"/"src"), red/blue caption words, mark, payoff
P = {
 "02": {
  1: dict(ai=["a heavily rusted bolt and nut glistening with a drop of golden oil"], first="ai", red=["rusted"]),
  2: dict(ai=["a pile of bright orange rusted bolts on a wooden workbench", "six small bottles of different coloured oils in a row"]),
  3: dict(ai=["macro of thin golden oil creeping up into tiny cracks of rusty metal", "a white paper towel soaking up a spilled blue drink", "macro of a liquid droplet disappearing into a hairline crack"], blue=["liquid"]),
  4: dict(ai=["a single drop of fluid sitting on a rusty washer like a bead"], first="src", mark=["q", -1.2]),
  5: dict(ai=["a steel bolt sliced in half lengthwise showing oil inside the threads macro"], first="ai"),
  6: dict(ai=["thick green slime coating a rusty bolt macro", "thick honey failing to enter a narrow crack macro"], first="ai"),
  7: dict(ai=["six different coloured oils swirling together in a glass beaker", "two chemicals reacting with smoke in a glass flask"], first="src", red=["risky"]),
  8: dict(ai=["a wrench straining on a stuck rusty nut with motion blur"], first="ai", red=["56"]),
  9: dict(ai=["a golden trophy on a podium in a garage spotlight", "a silver trophy next to a gold trophy under spotlights"], first="src"),
  10: dict(ai=["extreme macro of microscopic gaps inside rusty bolt threads", "a thin liquid racing a thick syrup down a crack macro", "macro of oil flowing into a rusted thread"]),
  11: dict(ai=["a heavily rusted bolt and nut glistening with a drop of golden oil"], first="src", mark=["q", 0.2]),
 },
 "03": {
  1: dict(ai=["two teal cordless impact wrenches facing each other on a dark workbench with dramatic light"], first="ai", red=["fake"]),
  2: dict(ai=["a stack of dollar bills next to a cheap cordless impact wrench", "a man holding his head in disbelief silhouette"], red=["138"]),
  3: dict(ai=["two power tools balanced on an old brass scale"], first="src"),
  4: dict(ai=["a cordless impact wrench struggling on a big bolt with sparks"], first="src", mark=["x", -1.0]),
  5: dict(ai=["a glossy product box with a giant exaggerated torque number glowing", "a fantasy book glowing with magic on a workbench"]),
  6: dict(ai=["a teal impact wrench spinning a lug nut with motion blur"], first="src"),
  7: dict(ai=["cutaway inside an impact wrench showing a spinning steel hammer hitting an anvil", "macro of two steel blocks colliding with sparks", "slow motion steel hammer striking metal with a shockwave"]),
  8: dict(ai=["two steel hammer parts side by side on a scale macro", "a heavy steel part spinning fast with motion trails"], red=["heavier"]),
  9: dict(ai=["a lug nut flying off a car wheel in slow motion"], first="ai"),
  10: dict(ai=["a black plastic tool handle shattering into pieces slow motion"], first="src", red=["snaps"]),
  11: dict(ai=["a glowing copper brushless electric motor macro", "a small pile of thirty dollars in cash under a spotlight"], red=["deal"]),
  12: dict(ai=["two teal cordless impact wrenches facing each other on a dark workbench with dramatic light"], first="src", mark=["q", 0.2]),
 },
 "04": {
  1: dict(ai=["two red small gas engines facing off on a garage floor under dramatic light"], first="ai"),
  2: dict(ai=["a shiny red small gas engine with a big horsepower sticker"], first="src"),
  3: dict(ai=["a peeling sticker on a red engine macro", "a stopwatch and a test bench in a workshop"]),
  4: dict(ai=["a small engine shaking violently with motion blur"], first="src", red=["shakes"]),
  5: dict(ai=["a steel crankshaft with heavy counterweights spinning macro", "a washing machine shaking violently on a tiled floor", "cutaway of a single cylinder engine piston and crankshaft"]),
  6: dict(ai=["a leaky wooden boat taking on water", "golden motor oil pouring from a bottle into an engine"], first="ai", blue=["oil"]),
  7: dict(ai=["macro of a spark plug caked in black carbon", "oil sneaking past a piston ring inside an engine cylinder macro"], first="ai", blue=["oil"]),
  8: dict(ai=["a thick rope pulled tight with tension and dust"], first="src"),
  9: dict(ai=["a red small engine under a spotlight with a plot twist mood"], first="src"),
  10: dict(ai=["a stack of cash next to a small red engine", "a fuel can with a few drops left glowing"], red=["least"]),
  11: dict(ai=["two red small gas engines facing off on a garage floor under dramatic light"], first="src", mark=["q", 0.2]),
 },
 "05": {
  1: dict(ai=["an AA battery bouncing high off a table in slow motion"], first="ai", red=["dead"]),
  2: dict(ai=["cutaway of an AA battery showing soft grey gel inside", "a soft gel cube absorbing a falling steel ball slow motion"]),
  3: dict(ai=["white zinc oxide crystals forming inside a battery macro", "a springy rubber ball bouncing off concrete slow motion", "a cutaway AA battery with white crystals inside"]),
  4: dict(ai=["many AA batteries lined up in a row on a workbench"], first="src"),
  5: dict(ai=["a cheap AA battery with a tiny flickering flashlight"], first="src", red=["26"]),
  6: dict(ai=["a glowing AA battery with a bright beam of light", "an hourglass with sand running on a workbench"]),
  7: dict(ai=["a silver lithium AA battery glowing on clouds"], first="ai"),
  8: dict(ai=["a mystery box with light shining out of it"], first="src", mark=["q", 0.2]),
  9: dict(ai=["a single copper penny next to an AA battery macro", "a pile of pennies glowing with blue electric energy"]),
  10: dict(ai=["two AA batteries on a scale balancing with coins", "a gold medal next to a price tag on a table"]),
  11: dict(ai=["an AA battery bouncing high off a table in slow motion"], first="src"),
 },
 "08": {
  1: dict(ai=["a rusty steel box bolted shut on a workbench with dramatic light"], first="ai"),
  2: dict(ai=["an old rusty vintage motor oil can from the 1950s on a shelf"], first="src", mark=["q", -1.2]),
  3: dict(ai=["two glass beakers of motor oil heating on a glowing hot plate"], first="src"),
  4: dict(ai=["golden motor oil steaming and evaporating into the air", "wisps of smoke rising from hot oil in slow motion"], red=["42"]),
  5: dict(ai=["thick frozen motor oil covered in frost"], first="src", blue=["freezer"]),
  6: dict(ai=["a crusty black engine cylinder head macro", "oil baking onto hot metal with smoke"], first="src"),
  7: dict(ai=["a lab report sheet on a clipboard next to test tubes of oil", "a single tiny white grain under a magnifying glass"]),
  8: dict(ai=["tiny particles grabbing black soot inside oil macro", "thick black sludge dripping inside an engine"], red=["sludge"]),
  9: dict(ai=["a nearly empty battery shaped glass of oil", "acid droplets eating a metal surface macro"]),
  10: dict(ai=["a cracked used up metal shield on a dark floor", "black sludge filling an engine macro"], red=["sludge"]),
  11: dict(ai=["an old rusty vintage motor oil can from the 1950s on a shelf"], first="src", mark=["q", 0.2]),
 },
 "09": {
  1: dict(ai=["a water filter pitcher pouring crystal clear water into a glass"], first="ai", blue=["water"]),
  2: dict(ai=["tiny glowing particles floating in a glass of tap water macro"], first="src", red=["259"]),
  3: dict(ai=["a homemade plastic bottle filter with layers of sand and black charcoal"], first="src"),
  4: dict(ai=["a water filter pitcher next to a plastic bottle filter on a kitchen counter", "two glasses of water side by side under a spotlight"]),
  5: dict(ai=["macro of black activated carbon granules with water flowing through", "tiny minerals sliding through charcoal macro"], first="ai"),
  6: dict(ai=["a tall stainless steel water filter tank in a kitchen", "brand new water filter cartridges in a box"], first="ai"),
  7: dict(ai=["a perfectly clear glass of water with a glowing light behind it"], first="src", blue=["zero"]),
  8: dict(ai=["macro of tiny amber resin beads with water flowing over them", "glowing beads swapping particles in water macro"], first="ai"),
  9: dict(ai=["white calcium crystals in a glass of water macro", "a calm glass of mineral water on a stone table"]),
  10: dict(ai=["a water filter pitcher pouring crystal clear water into a glass"], first="src", mark=["q", 0.2], blue=["water"]),
 },
 "10": {
  1: dict(ai=["a car up on black plastic ramps in a dark garage with dramatic light"], first="ai", red=["death"]),
  2: dict(ai=["a hydraulic press crushing a black plastic car ramp"], first="src"),
  3: dict(ai=["macro of a golden honeycomb structure under pressure", "black plastic ribs inside a car ramp cutaway", "a honeycomb holding a heavy steel weight"]),
  4: dict(ai=["a steel car ramp bending under a heavy tractor tire"], first="src", red=["folds"]),
  5: dict(ai=["a thin steel sheet buckling in slow motion", "plastic ribs flexing and holding a heavy load"]),
  6: dict(ai=["a giant hydraulic press resting idle in a dim factory", "a person relaxing next to a car ramp"]),
  7: dict(ai=["a car ramp sliding across smooth concrete with motion blur"], first="src", mark=["x", -1.0]),
  8: dict(ai=["a car tire pushing a plastic ramp forward on concrete", "a small rubber stopper slipping on a floor macro"]),
  9: dict(ai=["a damp towel under a car ramp on concrete"], first="ai", blue=["damp"]),
  10: dict(ai=["a hand pulling up a car parking brake lever", "a mechanic on a creeper next to a car on ramps"], red=["parking"]),
  11: dict(ai=["a car up on black plastic ramps in a dark garage with dramatic light"], first="src", mark=["q", 0.2]),
 },
 "11": {
  1: dict(ai=["a bathroom sink drain clogged with a clump of hair under dramatic light"], first="ai", red=["hair"]),
  2: dict(ai=["clear glass jars with hair and grease and soap inside"], first="src"),
  3: dict(ai=["a jar of white lye crystals on a dark shelf"], first="src", red=["lye"]),
  4: dict(ai=["macro of a single human hair dissolving in liquid", "glowing protein chains snapping apart macro", "hair strands dissolving into bubbles in a glass"]),
  5: dict(ai=["three drain cleaner bottles in a row on a bathroom floor"], first="ai"),
  6: dict(ai=["bright blue liquid swirling in a drain", "tiny bacteria under a microscope glowing"], first="ai", blue=["blue"]),
  7: dict(ai=["a carrot dissolving in a glass of bubbling acid"], first="src"),
  8: dict(ai=["acid eating the shiny plating off a steel pipe macro", "a clean white plastic pipe under a sink"], red=["acid"]),
  9: dict(ai=["a metal drain snake coiled on a bathroom floor"], first="ai"),
  10: dict(ai=["a toxic green cloud of gas rising from a sink", "two cleaning bottles with a red warning glow"], red=["never", "toxic"]),
  11: dict(ai=["a bathroom sink drain clogged with a clump of hair under dramatic light"], first="src", mark=["q", 0.2]),
 },
}

for n, lines in P.items():
    p = f"shorts/{n}/script.json"
    d = json.load(open(p, encoding="utf-8"))
    for l in d["lines"]:
        for k in ("original", "insert", "fx"):
            l.pop(k, None)
        l.update(lines[l["id"]])
    d["description"] = d.get("description", "").replace("animations by our channel", "AI visuals by our channel")
    json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(n, sum(len(set(x.get("ai", []))) for x in lines.values()), "prompts")

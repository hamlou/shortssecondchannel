"""Monetization gate for one Short (research/monetization_system.md §2).
py tools/mono_check.py shorts/<nn>/script.json   -> PASS/FAIL per rule, exit 1 if any FAIL
Pre-render: estimates seconds from words (wpm). Post-render: pass --durations shorts/<nn>/durations.json ({"<id>": seconds}) for exact numbers."""
import json, re, sys

WPM = 175


def secs(t):
    m, s = t.split(":")
    return int(m) * 60 + float(s)


def main():
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    dur = json.load(open(sys.argv[sys.argv.index("--durations") + 1], encoding="utf-8")) if "--durations" in sys.argv else {}
    lines = d["lines"]
    t = {l["id"]: dur.get(str(l["id"]), len(l["text"].split()) / WPM * 60) for l in lines}
    total = sum(t.values())
    res = []
    res.append(("1 length <= 59 s", total <= 59, f"{total:.1f} s"))
    typed = [l for l in lines if l.get("type") in ("analysis", "story")]
    an = sum(1 for l in lines if l.get("type") == "analysis")
    res.append(("2a every line typed analysis/story", len(typed) == len(lines), f"{len(typed)}/{len(lines)}"))
    res.append(("2b analysis >= 50 % of lines", an / len(lines) >= 0.5, f"{an}/{len(lines)} = {an / len(lines):.0%}"))
    # AI clips (tools/assemble.py plan_line): whole line if it has no source, else min(75 %, 1.4 s per prompt); payoff = 0
    ai_t = lambda l: 0 if l.get("payoff") else t[l["id"]] if not l.get("src") else min(0.75 * t[l["id"]], 1.4 * len(l["ai"]))
    orig = sum(ai_t(l) if "ai" in l or l.get("payoff") else t[l["id"]] * bool(l.get("original")) for l in lines)
    res.append(("3 original (AI) visuals >= 50 % runtime", orig / total >= 0.5, f"{orig:.1f}s = {orig / total:.0%}"))
    res.append(("3b frame 0 = AI hero shot", bool(lines[0].get("ai")) and lines[0].get("first") == "ai", "ok" if lines[0].get("ai") else "line 1 needs ai + first=ai"))
    clips = [(c, secs(c.split("-")[1]) - secs(c.split("-")[0])) for l in lines for c in l.get("src", [])]
    long_ = [f"{c} ({s:.0f}s src span; cut to <=2 s pieces)" for c, s in clips if s > 6]
    res.append(("4a source spans short (<= 6 s span, cut into <= 2 s shots)", not long_, "; ".join(long_) or "ok"))
    res.append(("4b no source audio", d.get("source_audio", False) is False, "source_audio=false" if not d.get("source_audio") else "SOURCE AUDIO USED"))
    starts = [secs(l["src"][0].split("-")[0]) for l in lines if l.get("src")]
    reordered = any(b < a for a, b in zip(starts, starts[1:]))
    res.append(("5 our order differs from source", reordered, "re-ordered" if reordered else "follows source order exactly"))
    res.append(("6 facts checked", bool(d.get("facts_checked")), str(d.get("facts_checked", "missing"))))
    res.append(("7 advertiser-friendly / safety note", bool(d.get("safety")), str(d.get("safety", "missing"))))
    res.append(("8 credit + added-value text", all(k in d.get("description", "") for k in ("Original video", "explained")), d.get("description", "missing")[:90]))
    punct = [l["id"] for l in lines if re.search(r"[,;:—–]| - ", l["text"])]
    sents = [s.split() for l in lines for s in re.split(r"[.!?]+", l["text"]) if s.strip()]
    frags = [" ".join(a + b) for a, b in zip(sents, sents[1:]) if len(a) <= 4 and len(b) <= 4]
    res.append(("10 speech: zero commas/dashes/semicolons/colons", not punct, f"lines {punct}" if punct else "ok"))
    res.append(("11 speech: no fragment chains", not frags, "; ".join(frags[:3]) or "ok"))
    ok = True
    for name, p, info in res:
        ok &= p
        print(f"{'PASS' if p else 'FAIL'}  {name:55s} {info}")
    print("\nGATE:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

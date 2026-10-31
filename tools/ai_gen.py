"""AI beauty stills for one Short (TestedNProved style, research/tnp_breakdown.md). Runs on GitHub Actions.
py tools/ai_gen.py shorts/<nn>
Every prompt in a line's "ai" list -> shorts/<nn>/build/ai/<sha1(prompt)[:10]>.jpg (1024x1024), skipped if it already exists (cache).
Model: Cloudflare Workers AI @cf/black-forest-labs/flux-1-schnell (FLUX.1-schnell = Apache 2.0, commercial use OK),
free tier 10k neurons/day (~170 images). Env: CF_ACCOUNT_ID, CF_API_TOKEN."""
import base64, hashlib, json, os, sys, time, urllib.request, urllib.error

MODEL = "@cf/black-forest-labs/flux-1-schnell"
STYLE = (", photorealistic cinematic shot, shallow depth of field, dramatic soft rim light, rich colour, "
         "subject centred and filling the middle of the frame, ultra detailed, 35mm film look, no text, no letters, no logo, no watermark")


def img_name(prompt):
    return hashlib.sha1(prompt.encode()).hexdigest()[:10] + ".jpg"


def gen(prompt, out):
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/{MODEL}"
    body = json.dumps({"prompt": prompt + STYLE, "steps": 4}).encode()
    for a in range(5):
        req = urllib.request.Request(url, body, {"Authorization": f"Bearer {os.environ['CF_API_TOKEN']}", "Content-Type": "application/json"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=120))
            open(out, "wb").write(base64.b64decode(r["result"]["image"]))
            return
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (400, 401, 403):
                sys.exit(f"{e.code} {msg}")
            print("retry", e.code, msg, flush=True)
        except Exception as e:
            print("retry", e, flush=True)
        time.sleep(5 * (a + 1))
    sys.exit(f"failed: {prompt[:60]}")


def main():
    sd = sys.argv[1]
    d = json.load(open(os.path.join(sd, "script.json"), encoding="utf-8"))
    o = os.path.join(sd, "build", "ai")
    os.makedirs(o, exist_ok=True)
    n = 0
    for l in d["lines"]:
        for p in l.get("ai", []):
            f = os.path.join(o, img_name(p))
            if not os.path.exists(f):
                gen(p, f)
                n += 1
                print("made", l["id"], p[:50], flush=True)
    print(f"{n} new images")


if __name__ == "__main__":
    main()

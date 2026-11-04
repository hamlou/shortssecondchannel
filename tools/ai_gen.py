"""AI beauty stills for one Short (TestedNProved style, research/tnp_breakdown.md). Runs on GitHub Actions.
py tools/ai_gen.py shorts/<nn>
Every "ai:<prompt>" beat of a line -> shorts/<nn>/build/ai/<sha1(prompt)[:10]>.jpg (1024x1024), skipped if it already exists (cache).
Backend 1: Cloudflare Workers AI @cf/black-forest-labs/flux-1-schnell (FLUX.1-schnell = Apache 2.0, commercial use OK),
free tier 10k neurons/day (~170 images). Env: CF_ACCOUNT_ID, CF_API_TOKEN.
Backend 2 (automatic once the daily quota is used up, or with --local): our own Stable Diffusion XL base 1.0 + LCM-LoRA
(both CreativeML OpenRAIL++-M, commercial use OK) running on the GitHub runner CPU, 6 steps, 768x1024. Free and unlimited."""
import base64, hashlib, json, os, sys, time, urllib.request, urllib.error

MODEL = "@cf/black-forest-labs/flux-1-schnell"
STYLE = (", photorealistic cinematic shot, shallow depth of field, dramatic soft rim light, rich colour, "
         "subject centred and filling the middle of the frame, ultra detailed, 35mm film look, no text, no letters, no logo, no watermark")


def img_name(prompt):
    return hashlib.sha1(prompt.encode()).hexdigest()[:10] + ".jpg"


class QuotaOver(Exception):
    pass


PIPE = None


def gen_local(prompt, out):
    """Self-hosted SDXL + LCM-LoRA on CPU (~2-3 min/image on a 4-core runner)."""
    global PIPE
    if PIPE is None:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "torch", "--index-url", "https://download.pytorch.org/whl/cpu"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "diffusers", "transformers", "accelerate", "peft", "safetensors"], check=True)
        import torch
        from diffusers import StableDiffusionXLPipeline, LCMScheduler
        torch.set_num_threads(os.cpu_count() or 4)
        PIPE = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float32,
                                                         variant="fp16", use_safetensors=True)
        PIPE.scheduler = LCMScheduler.from_config(PIPE.scheduler.config)
        PIPE.load_lora_weights("latent-consistency/lcm-lora-sdxl")
        PIPE.fuse_lora()
        print("local SDXL+LCM loaded", flush=True)
    import torch
    t = time.time()
    img = PIPE(prompt + STYLE, num_inference_steps=6, guidance_scale=1.0, width=768, height=1024,
               generator=torch.Generator().manual_seed(int(img_name(prompt)[:8], 16))).images[0]
    img.save(out, quality=92)
    print(f"local image {time.time() - t:.0f}s", flush=True)


def gen(prompt, out):
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/{MODEL}"
    body = json.dumps({"prompt": prompt + STYLE, "steps": 4}).encode()
    for a in range(8):
        req = urllib.request.Request(url, body, {"Authorization": f"Bearer {os.environ['CF_API_TOKEN']}", "Content-Type": "application/json"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=120))
            open(out, "wb").write(base64.b64decode(r["result"]["image"]))
            return
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code == 429 and "allocation" in msg:
                raise QuotaOver(msg)
            if e.code in (401, 403) or (e.code == 400 and "NSFW" not in msg):  # the NSFW filter gives random false alarms: retry
                sys.exit(f"{e.code} {msg}")
            print("retry", e.code, msg, flush=True)
        except Exception as e:
            print("retry", e, flush=True)
        time.sleep(5 * (a + 1))
    sys.exit(f"failed: {prompt[:60]}")


LOCAL = [False]


def main():
    LOCAL[0] = "--local" in sys.argv or not os.environ.get("CF_API_TOKEN")
    sd = sys.argv[1]
    d = json.load(open(os.path.join(sd, "script.json"), encoding="utf-8"))
    o = os.path.join(sd, "build", "ai")
    os.makedirs(o, exist_ok=True)
    n = 0
    for l in d["lines"]:
        for p in [b[1][3:] for b in l.get("beats", []) if b[1].startswith("ai:")]:
            f = os.path.join(o, img_name(p))
            if not os.path.exists(f):
                if not LOCAL[0]:
                    try:
                        gen(p, f)
                    except QuotaOver:
                        print("Cloudflare daily quota used up -> switching to self-hosted SDXL+LCM", flush=True)
                        LOCAL[0] = True
                if LOCAL[0]:
                    gen_local(p, f)
                n += 1
                print("made", l["id"], p[:50], flush=True)
    print(f"{n} new images")


if __name__ == "__main__":
    main()

import json, re
from pathlib import Path


def load(p):
    f = Path(p)
    if not f.exists():
        return []
    return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]


NUM = r"-?\d[\d,]*\.?\d*"


def gsm_ok(r):
    text = (r.get("answer") or "").replace("$", "")
    cand = []
    for b in re.findall(r"\*\*(.*?)\*\*", text):
        cand += re.findall(NUM, b)
    if not cand:
        cand = re.findall(NUM, text)
    try:
        return float(cand[-1].replace(",", "")) == float(r["expected"].replace(",", ""))
    except Exception:
        return False


def summarize(rows, name):
    calls = [r for r in rows if r.get("model") not in (None, "none") and not r.get("error")]
    errs = sum(1 for r in rows if r.get("error"))
    gsm = [r for r in rows if r["source"] == "gsm8k"]
    lat = [r.get("latency", 0) for r in calls if r.get("latency")]
    return {
        "সিস্টেম": name,
        "মোট কেস": len(rows),
        "API কল": len(calls),
        "এরর": errs,
        "GSM8K সঠিক": f"{sum(gsm_ok(r) for r in gsm)}/{len(gsm)}",
        "আনুমানিক খরচ (USD)": round(sum(r.get("cost", 0) or 0 for r in rows), 5),
        "গড় দেরি (সে.)": round(sum(lat) / len(lat), 2) if lat else 0,
    }


dev = load("data/results_dev.good.jsonl") or load("data/results_dev.jsonl")
hid = load("data/results_hidden.jsonl")
base = load("data/results_baseline.jsonl")

hidden_inputs = {r["input"] for r in hid}
base_hidden = [r for r in base if r["input"] in hidden_inputs]

for t in [summarize(hid, "Router (হিডেন)"),
          summarize(base_hidden, "সব বড় মডেলে (হিডেন)"),
          summarize(dev, "Router (ডেভ)")]:
    print(t)

if hid:
    print("\nহিডেন রাউটিং সঠিক:", sum(r["match"] for r in hid), "/", len(hid))
    print("ফেল বা এরর কেস:")
    for r in hid:
        if not r["match"] or r.get("error"):
            print(" -", r["tag"], "|", r["input"][:70].replace("\n", " "),
                  "|", r.get("error", "রাউটিং ভুল"))
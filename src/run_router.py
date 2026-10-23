import json, time
from pathlib import Path
from router import route

lines = Path("data/evals.jsonl").read_text(encoding="utf-8").splitlines()
rows = [json.loads(l) for l in lines if l.strip()]
dev = [r for r in rows if r["split"] == "dev"]   # হিডেন ছোঁয়া নিষেধ

out, ok = [], 0
for i, r in enumerate(dev, 1):
    res = route(r["input"])
    tier = res.get("tier", "simple")
    match = tier == r["my_label"]
    ok += match
    print(f"{i:>2} {r['tag']:<10} label={r['my_label']:<7} routed={tier:<7} "
          f"{'OK ' if match else 'MISS'} {res['model']} "
          f"{'(cache)' if res.get('cached') else ''}"
          f"{' (fallback)' if res.get('fallback') else ''}")
    out.append({**r, **res, "match": match})
    if res["model"] != "none" and not res.get("cached"):
        time.sleep(5)

Path("data/results_dev.jsonl").write_text(
    "\n".join(json.dumps(o, ensure_ascii=False) for o in out) + "\n",
    encoding="utf-8")
print(f"\nরাউটিং সঠিক: {ok}/{len(dev)}")
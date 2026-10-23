import json, time, sys
from pathlib import Path
from router import route

OUT = Path("data/results_hidden.jsonl")
if OUT.exists():
    sys.exit("হিডেন রান আগেই হয়েছে। দ্বিতীয়বার চালানো নিষেধ: " + str(OUT))

lines = Path("data/evals.jsonl").read_text(encoding="utf-8").splitlines()
rows = [json.loads(l) for l in lines if l.strip()]
hidden = [r for r in rows if r["split"] == "hidden"]
print("হিডেন কেস:", len(hidden))

out, ok = [], 0
for i, r in enumerate(hidden, 1):
    res = route(r["input"])
    tier = res.get("tier", "simple")
    match = tier == r["my_label"]
    ok += match
    print(f"{i:>2} {r['tag']:<10} label={r['my_label']:<7} routed={tier:<7} "
          f"{'OK ' if match else 'MISS'} {res['model']}"
          f"{' (fallback)' if res.get('fallback') else ''}"
          f"{' ERROR' if res.get('error') else ''}")
    out.append({**r, **res, "match": match})
    if res["model"] != "none" and not res.get("cached"):
        time.sleep(5)

OUT.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in out) + "\n",
               encoding="utf-8")
print(f"\nহিডেন রাউটিং সঠিক: {ok}/{len(hidden)}")
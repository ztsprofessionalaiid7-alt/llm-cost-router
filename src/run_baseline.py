import json, time
from pathlib import Path
from router import PRIMARY, call, cost

client, model = PRIMARY["hard"]
lines = Path("data/evals.jsonl").read_text(encoding="utf-8").splitlines()
rows = [json.loads(l) for l in lines if l.strip()]
rows = [r for r in rows if r["input"].strip()]   # খালি ইনপুট API-তে যায় না

out = []
for i, r in enumerate(rows, 1):
    t0 = time.time()
    resp, err = call(client, model, r["input"][:4000])
    lat = round(time.time() - t0, 2)
    if resp is None:
        out.append({**r, "model": model, "answer": "", "error": err,
                    "tokens_in": 0, "tokens_out": 0, "latency": lat, "cost": 0.0})
        print(f"{i:>2} ERROR {err[:60]}")
    else:
        tin, tout = resp.usage.prompt_tokens, resp.usage.completion_tokens
        out.append({**r, "model": model,
                    "answer": resp.choices[0].message.content or "",
                    "tokens_in": tin, "tokens_out": tout,
                    "latency": lat, "cost": cost(model, tin, tout)})
        print(f"{i:>2} OK {r['tag']:<10} {tin}+{tout} টোকেন")
    time.sleep(5)

Path("data/results_baseline.jsonl").write_text(
    "\n".join(json.dumps(o, ensure_ascii=False) for o in out) + "\n",
    encoding="utf-8")
print("বেসলাইন সংরক্ষিত")
import json, re
from pathlib import Path

rows = [json.loads(l) for l in Path("data/results_dev.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
num = r"-?\d[\d,]*\.?\d*"
ok = n = 0
for r in rows:
    if r["source"] != "gsm8k" or r["class"] == "error":
        continue
    text = r["answer"].replace("$", "")
    bold = re.findall(r"\*\*(.*?)\*\*", text)
    cand = []
    for b in bold:
        cand += re.findall(num, b)
    if not cand:
        cand = re.findall(num, text)
    exp = float(r["expected"].replace(",", ""))
    got = [float(c.replace(",", "")) for c in cand if c.strip(",.")]
    hit = bool(got) and got[-1] == exp
    n += 1; ok += hit
    print("OK " if hit else "MISS", "expected", exp, "got", got[-1] if got else None)
print(f"GSM8K সঠিক: {ok}/{n}")
import json, random, glob
import pandas as pd
from pathlib import Path

random.seed(42)
cases = []

def read(pattern):
    files = [f for f in glob.glob(pattern, recursive=True) if ".cache" not in f]
    assert files, f"ফাইল পাওয়া যায়নি: {pattern}"
    f = files[0]
    if f.endswith(".jsonl"):
        return pd.read_json(f, lines=True).to_dict("records")
    return pd.read_parquet(f).to_dict("records")

def add(rows, n, tag, src, q, a):
    for r in random.sample(rows, n):
        cases.append({"input": q(r), "expected": a(r), "tag": tag,
                      "source": src, "my_label": ""})

# সহজ ১০: Dolly
d = read("data/raw/databricks-dolly-15k/*.jsonl")
d = [r for r in d if r["category"] in ("open_qa", "general_qa")
     and not r["context"] and len(r["instruction"]) < 120]
add(d, 10, "easy", "dolly", lambda r: r["instruction"], lambda r: r["response"])

# কঠিন ৬: GSM8K
g = read("data/raw/gsm8k/main/*.parquet")
add(g, 6, "hard", "gsm8k", lambda r: r["question"],
    lambda r: r["answer"].split("####")[-1].strip())

# উত্তর নেই ৩: SQuAD v2
s = read("data/raw/squad_v2/squad_v2/*.parquet")
s = [r for r in s if len(r["answers"]["text"]) == 0 and len(r["context"]) < 800]
add(s, 3, "no_answer", "squad_v2",
    lambda r: r["context"] + "\n\nপ্রশ্ন: " + r["question"],
    lambda r: "তথ্য নেই")

# আক্রমণ ৩: deepset
p = read("data/raw/prompt-injections/data/*.parquet")
p = [r for r in p if r["label"] == 1]
add(p, 3, "attack", "deepset", lambda r: r["text"], lambda r: "reject")

# ভুল ইনপুট ৩: হাতে লেখা
for t in ["", "asdfghjkl;;;;", "a" * 5000]:
    cases.append({"input": t, "expected": "invalid_input", "tag": "bad_input",
                  "source": "manual", "my_label": ""})

# ডেভ ১৫ / হিডেন ১০
hidden_n = {"easy": 4, "hard": 3, "no_answer": 1, "attack": 1, "bad_input": 1}
seen = {}
for c in cases:
    k = seen.get(c["tag"], 0)
    c["split"] = "hidden" if k < hidden_n[c["tag"]] else "dev"
    seen[c["tag"]] = k + 1

out = Path("data/evals.jsonl")
with out.open("w", encoding="utf-8") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

print(len(cases), "cases saved ->", out)
print("dev:", sum(c["split"] == "dev" for c in cases),
      "hidden:", sum(c["split"] == "hidden" for c in cases))
import json
from pathlib import Path

path = Path("data/evals.jsonl")
Path("data/evals.backup.jsonl").write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

# নিয়ম: সিস্টেম চালানোর আগে ঠিক করা। README-তে এটাই লিখবে।
RULES = {
    "easy":      ("simple", "ছোট সাধারণ প্রশ্ন, ছোট মডেলই পারবে"),
    "hard":      ("hard",   "ধাপে ধাপে গণিতের যুক্তি লাগে"),
    "no_answer": ("hard",   "লম্বা প্রসঙ্গ পড়ে বুঝতে হবে উত্তর নেই, বানিয়ে বলা যাবে না"),
    "attack":    ("simple", "নিয়ম/ফিল্টারে আগেই ধরা পড়ে, বড় মডেল লাগে না"),
    "bad_input": ("simple", "খালি বা অর্থহীন ইনপুট, কোনো মডেলই লাগে না"),
}

def first_sentence(text, limit=200):
    s = text.strip().split(". ")[0].strip()
    return s[:limit]

rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
for r in rows:
    label, why = RULES[r["tag"]]
    r["my_label"] = label
    r["label_reason"] = why
    if r["tag"] == "easy":
        r["expected_short"] = first_sentence(r["expected"])

path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                encoding="utf-8")

print(f"{'#':<3}{'split':<8}{'tag':<11}{'label':<8}input")
for i, r in enumerate(rows, 1):
    print(f"{i:<3}{r['split']:<8}{r['tag']:<11}{r['my_label']:<8}{r['input'][:50]!r}")
print("\nsimple:", sum(r["my_label"] == "simple" for r in rows),
      "hard:", sum(r["my_label"] == "hard" for r in rows))
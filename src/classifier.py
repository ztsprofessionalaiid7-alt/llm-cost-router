import re

ATTACK = ["ignore previous", "ignore all", "forget about all", "new tasks follow",
          "disregard", "system prompt", "jailbreak", "instruktionen", "ignoriere"]
HARD_WORDS = ["how many", "total", "calculate", "step by step", "each", "per ",
              "percent", "more than", "less than", "compare", "explain why"]


def classify(text: str) -> str:
    """ফেরত দেয়: invalid | attack | simple | hard"""
    t = text.strip()
    if not t or len(t) > 4000:
        return "invalid"
    if " " not in t and len(t) > 8:          # স্পেসহীন অর্থহীন স্ট্রিং
        return "invalid"
    low = t.lower()
    if any(p in low for p in ATTACK):
        return "attack"
    digits = len(re.findall(r"\d+", t))
    if len(t) > 400:                          # লম্বা প্রসঙ্গ পড়ে বুঝতে হবে
        return "hard"
    if digits >= 2 and any(w in low for w in HARD_WORDS):
        return "hard"
    if digits >= 3:
        return "hard"
    return "simple"


TIER = {"invalid": "simple", "attack": "simple", "simple": "simple", "hard": "hard"}
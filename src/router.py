import os, json, time, sqlite3, hashlib
from dotenv import load_dotenv
from openai import OpenAI
from classifier import classify, TIER

load_dotenv()
DB = "data/router.db"
# আনুমানিক দাম (USD / ১M টোকেন): প্রকাশিত দাম দেখে নিজে বসাও, README-তে লিখে দাও
PRICE = {"openai/gpt-oss-20b": (0.10, 0.50), "gemini-3.8-flash": (0.30, 2.50)}


def mk(url, key):
    return OpenAI(base_url=url, api_key=os.getenv(key))


PRIMARY = {
    "simple": (mk("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
               os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")),
    "hard": (mk("https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY"),
             os.getenv("GEMINI_MODEL", "gemini-3.8-flash")),
}
FALLBACK = (mk("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
            os.getenv("OPENROUTER_MODEL"))


def db():
    c = sqlite3.connect(DB)
    c.execute("create table if not exists cache(k text primary key, v text)")
    c.execute("""create table if not exists log(ts real, cls text, tier text, model text,
        cached int, fallback int, tin int, tout int, latency real, cost real, err text)""")
    return c


def cost(model, tin, tout):
    p = PRICE.get(model)
    return round((tin * p[0] + tout * p[1]) / 1e6, 6) if p else 0.0


def call(client, model, text, retries=2):
    last = None
    for i in range(retries + 1):
        try:
            r = client.chat.completions.create(
                model=model, max_tokens=1500, timeout=60,
                messages=[{"role": "user", "content": text}])
            if r is not None and r.choices and r.choices[0].message:
                return r, None
            last = "empty response"
        except Exception as e:
            last = str(e)[:200]
        time.sleep(2 ** i * 2)
    return None, last


def log(con, cls, tier, model, cached, fb, tin, tout, lat, c, err):
    con.execute("insert into log values(?,?,?,?,?,?,?,?,?,?,?)",
                (time.time(), cls, tier, model, cached, fb, tin, tout, lat, c, err))
    con.commit()


def route(text):
    cls = classify(text)
    con = db()
    if cls in ("invalid", "attack"):
        log(con, cls, "simple", "none", 0, 0, 0, 0, 0.0, 0.0, None)
        return {"class": cls, "tier": "simple", "model": "none",
                "answer": f"BLOCKED:{cls}", "cached": False}

    tier = TIER[cls]
    key = hashlib.sha256(f"{tier}|{text}".encode()).hexdigest()
    hit = con.execute("select v from cache where k=?", (key,)).fetchone()
    if hit:
        d = json.loads(hit[0])
        d["cached"] = True
        log(con, cls, tier, d["model"], 1, 0, 0, 0, 0.0, 0.0, None)
        return d

    t0 = time.time()
    client, model = PRIMARY[tier]
    r, err = call(client, model, text)
    fb = 0
    if r is None:                      # মূল মডেল ফেল হলে OpenRouter
        client, model = FALLBACK
        r, err2 = call(client, model, text, retries=1)
        fb = 1
        if r is None:
            err = f"{err} | fallback: {err2}"
    lat = round(time.time() - t0, 2)

    if r is None:
        log(con, cls, tier, model, 0, fb, 0, 0, lat, 0.0, err)
        return {"class": cls, "tier": "?", "model": model,
                "answer": "", "cached": False, "error": err}

    tin, tout = r.usage.prompt_tokens, r.usage.completion_tokens
    d = {"class": cls, "tier": tier, "model": model,
         "answer": r.choices[0].message.content or "",
         "tokens_in": tin, "tokens_out": tout, "latency": lat,
         "fallback": bool(fb), "cost": cost(model, tin, tout), "cached": False}
    con.execute("insert or replace into cache values(?,?)",
                (key, json.dumps(d, ensure_ascii=False)))
    log(con, cls, tier, model, 0, fb, tin, tout, lat, d["cost"], err)
    return d
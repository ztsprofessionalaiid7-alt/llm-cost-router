import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
providers = {
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY"),
}
for name, (url, env) in providers.items():
    key = os.getenv(env)
    if not key:
        print(name, "-> key পাওয়া যায়নি"); continue
    try:
        ids = sorted(m.id for m in OpenAI(base_url=url, api_key=key).models.list())
        print(name, "OK,", len(ids), "মডেল")
        print("  ", [i for i in ids if "llama" in i or "flash" in i][:12])
    except Exception as e:
        print(name, "ERROR:", str(e)[:150])
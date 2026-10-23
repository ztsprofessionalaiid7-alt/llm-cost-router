from huggingface_hub import snapshot_download

jobs = [
    ("databricks/databricks-dolly-15k", ["*.jsonl"]),
    ("openai/gsm8k", ["main/test-*.parquet"]),
    ("rajpurkar/squad_v2", ["squad_v2/validation-*.parquet"]),
    ("deepset/prompt-injections", ["data/train-*.parquet"]),
]

for repo, patterns in jobs:
    name = repo.split("/")[1]
    print("downloading", repo)
    snapshot_download(
        repo_id=repo,
        repo_type="dataset",
        allow_patterns=patterns,
        local_dir=f"data/raw/{name}",
    )
print("done")
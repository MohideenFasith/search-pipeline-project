import os
import json
import requests
from retrieve import retrieve

# ─── Configuration ──────────────────────────────────────────────────────────────
EVAL_URL   = "https://mercor-dev--search-eng-interview.modal.run/grade"
AUTH_EMAIL = "mohideenfasiths@gmail.com"  # ← replace with your interview email

# ─── Discover all .yml configs in ./configs ──────────────────────────────────────
CONFIG_DIR = "configs"
config_files = [
    f for f in os.listdir(CONFIG_DIR)
    if f.endswith(".yml") or f.endswith(".yaml")
]
if len(config_files) != 10:
    print(f"⚠️  Found {len(config_files)} configs in '{CONFIG_DIR}'—expected 10.")
    print("Configs:", config_files)

# ─── Build the grade payload ────────────────────────────────────────────────────
def build_payload():
    config_candidates = {}
    for cfg in config_files:
        path = os.path.join(CONFIG_DIR, cfg)
        # pass an empty string as 'query' if your stubs don't include one
        ids = retrieve("", config_path=path)
        if len(ids) < 10:
            raise ValueError(f"Only {len(ids)} candidates for {cfg}; need 10.")
        config_candidates[cfg] = ids[:10]

    return {"config_candidates": config_candidates}

# ─── Submit to /grade ───────────────────────────────────────────────────────────
def submit_grade():
    payload = build_payload()
    headers = {
        "Authorization": AUTH_EMAIL,
        "Content-Type":  "application/json"
    }
    print("Submitting payload:", json.dumps(payload, indent=2))
    resp = requests.post(EVAL_URL, headers=headers, json=payload)
    resp.raise_for_status()
    print("✅ Submission successful!")
    print("Response:", resp.json())

# ─── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    submit_grade()

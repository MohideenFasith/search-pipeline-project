import os
import requests
import yaml
from turbopuffer import Turbopuffer

# ─── Config ──────────────────────────────────────────────────────────────────────
TPUF_API_KEY   = "tpuf_dQHBpZEvl612XAdP0MvrQY5dbS0omPMy"
VOYAGE_API_KEY = "pa-vNEmoJfc5evP_SSvpxIAj3uFzs9dfppEZkpx-3kOFZy"
INDEX_NAME     = "linkedin_candidates"
REGION         = "gcp-us-central1"

# ─── Init Turbopuffer & Namespace ────────────────────────────────────────────────
tpuf      = Turbopuffer(api_key=TPUF_API_KEY, region=REGION)
namespace = tpuf.namespace(INDEX_NAME)

# ─── Embedding Call ─────────────────────────────────────────────────────────────
def get_query_embedding(query: str):
    url = "https://api.voyageai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {VOYAGE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"input": query, "model": "voyage-3"}
    res = requests.post(url, json=payload, headers=headers)
    res.raise_for_status()
    return res.json()["data"][0]["embedding"]

# ─── YAML Loader ────────────────────────────────────────────────────────────────
def load_config(path: str):
    with open(path, "r") as f:
        return yaml.safe_load(f)

# ─── Hard Criteria Filter ──────────────────────────────────────────────────────
def match_hard_criteria(meta: dict, criteria: dict):
    for key, val in criteria.items():
        if key == "minYearsExperience" and meta.get("yearsOfExperience", 0) < val:
            return False
        if key == "requiredEducation" and val.lower() not in meta.get("education", "").lower():
            return False
        if key == "requiredExperience" and val.lower() not in meta.get("experience", "").lower():
            return False
    return True

# ─── Retrieval ──────────────────────────────────────────────────────────────────
def retrieve(query: str, config_path: str = None, top_k: int = 10):
    rows = []

    # 1) Vector search only if query is non-empty
    if query.strip():
        vec = get_query_embedding(query)
        result = namespace.query(
            rank_by=("vector", "ANN", vec),
            top_k=top_k * 2  # get more to allow for filtering
        )
        rows = result.rows
    else:
        print("⚠️ Empty query passed. Falling back to metadata-only filtering.")
        result = namespace.query(rank_by=None, top_k=top_k * 5)
        rows = result.rows

    # 2) Apply hard filtering if config is provided and exists
    if config_path and os.path.isfile(config_path):
        hard = load_config(config_path).get("hard", {})
        filtered = []
        for row in rows:
            meta = getattr(row, "attributes", None) or getattr(row, "metadata", {})
            if match_hard_criteria(meta, hard):
                filtered.append(row)
        rows = filtered
    elif config_path:
        print(f"⚠️ Config file not found at '{config_path}', skipping hard-filtering.")

    # 3) Return top IDs
    return [row.id for row in rows[:top_k]]

# ─── CLI Test ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    q = "corporate lawyer with 3+ years experience from top law school"
    ids = retrieve(q, config_path="configs/tax_lawyer.yml")
    print("🔍 Retrieved IDs:", ids)

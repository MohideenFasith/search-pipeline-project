# init.py

from pymongo import MongoClient
from turbopuffer import Turbopuffer
from tqdm import tqdm
import json

# Configuration
MONGO_URI    = "mongodb+srv://candidate:aQ7hHSLV9QqvQutP@hardfiltering.awwim.mongodb.net/"
TPUF_API_KEY = "tpuf_dQHBpZEvl612XAdP0MvrQY5dbS0omPMy"
INDEX_NAME   = "linkedin_candidates"
BATCH_SIZE   = 100

# 1. Connect to MongoDB
try:
    client     = MongoClient(MONGO_URI)
    db         = client["interview_data"]
    collection = db["linkedin_data_subset"]
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")
    exit(1)

# 2. Initialize Turbopuffer client & namespace
try:
    tpuf      = Turbopuffer(api_key=TPUF_API_KEY, region="gcp-us-central1")
    namespace = tpuf.namespace(INDEX_NAME)
except Exception as e:
    print(f"❌ Error initializing Turbopuffer: {e}")
    exit(1)

# 3. Upsert in batches, skip any bad doc
def batch_upsert():
    cursor = collection.find(
        {},
        {
            "_id":               1,
            "embedding":         1,
            "name":              1,
            "experience":        1,
            "education":         1,
            "yearsOfExperience": 1
        }
    )

    batch = []
    skipped = []

    for doc in tqdm(cursor, desc="Preparing batches"):
        doc_id = str(doc["_id"])

        # 3.1 Validate & cast embedding
        emb = doc.get("embedding")
        if not emb or not isinstance(emb, (list, tuple)):
            skipped.append((doc_id, "bad embedding"))
            continue
        try:
            vec = [float(x) for x in emb]
        except Exception:
            skipped.append((doc_id, "embedding cast fail"))
            continue

        # 3.2 Cast attributes
        try:
            attrs = {
                "name":              str(doc.get("name", "")),
                "education":         str(doc.get("education", "")),
                "experience":        str(doc.get("experience", "")),
                "yearsOfExperience": float(doc.get("yearsOfExperience", 0)),
            }
            # Quick JSON test
            _ = json.dumps(attrs)
        except Exception:
            skipped.append((doc_id, "attributes cast fail"))
            continue

        # 3.3 Build row
        batch.append({
            "id":         doc_id,
            "vector":     vec,
            "attributes": attrs
        })

        # 3.4 Flush batch
        if len(batch) >= BATCH_SIZE:
            try:
                namespace.write(upsert_rows=batch, distance_metric="cosine_distance")
            except Exception as e:
                print(f"❌ Batch upsert error: {e}\n Offending IDs: {[row['id'] for row in batch]}")
            batch.clear()

    # 3.5 Final leftover
    if batch:
        try:
            namespace.write(upsert_rows=batch, distance_metric="cosine_distance")
        except Exception as e:
            print(f"❌ Final batch upsert error: {e}\n Offending IDs: {[row['id'] for row in batch]}")

    print(f"✅ Done. Skipped {len(skipped)} documents.")
    if skipped:
        print("Skipped examples (id, reason):")
        for sid, reason in skipped[:10]:
            print(f" - {sid}: {reason}")
        if len(skipped) > 10:
            print(f" ...and {len(skipped)-10} more.")

if __name__ == "__main__":
    batch_upsert()

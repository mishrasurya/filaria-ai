import json
INPUT_FILE = "output/chunks_with_embeddings.json"
OUTPUT_FILE = "output/vector_db.json"
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

vector_db = []
for item in data:
    vector_db.append({
        "id": item["chunk_id"],
        "embedding": item["embedding"],
        "text": item["text"]
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(vector_db, f, indent=2)


print("✅ Vector database created")

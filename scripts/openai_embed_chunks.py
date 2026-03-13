import json
import requests
import os
from tqdm import tqdm

INPUT_FILE = "output/chunks.json"
OUTPUT_FILE = "output/chunks_with_embeddings.json"

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not set")

URL = "https://openrouter.ai/api/v1/embeddings"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

for item in tqdm(chunks):
    payload = {
        "model": "openai/text-embedding-3-small",
        "input": item["text"]
    }

    res = requests.post(URL, headers=headers, json=payload)

    if res.status_code != 200:
        print("❌ Embedding failed:", res.text)
        break

    item["embedding"] = res.json()["data"][0]["embedding"]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(chunks, f)

print("✅ Embeddings created successfully using OpenRouter")

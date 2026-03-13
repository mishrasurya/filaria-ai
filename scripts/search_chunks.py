import json
import numpy as np
import requests
import os

API_KEY = os.getenv("OPENAI_API_KEY")
URL = "https://openrouter.ai/api/v1/embeddings"
MODEL = "openai/text-embedding-3-small"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Filariasis Project"
}

def embed(text):
    res = requests.post(URL, headers=headers, json={
        "model": MODEL,
        "input": text
    })
    return np.array(res.json()["data"][0]["embedding"])

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

with open("output/vector_db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

query = input("Enter your question: ")
query_vec = embed(query)

results = []
for item in db:
    score = cosine(query_vec, np.array(item["embedding"]))
    results.append((score, item["text"]))

results.sort(reverse=True)
print("\n🔍 Top Relevant Results:\n")
for score, text in results[:2]:
    print(text)
    print("-" * 60)

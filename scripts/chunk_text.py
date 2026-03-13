import json

INPUT_FILE = "output/final_filaria_clean.txt"
OUTPUT_FILE = "output/chunks.json"

MAX_WORDS = 200  # ideal chunk size for semantic search

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

# Step 1: Split into meaningful paragraphs
paragraphs = [
    p.strip()
    for p in text.split("\n\n")
    if len(p.strip()) > 200
    and not p.strip().lower().startswith("chapter")
    and not p.strip().isupper()
]

chunks = []
chunk_id = 0

# Step 2: Further split long paragraphs into smaller chunks
for para in paragraphs:
    words = para.split()

    if len(words) > MAX_WORDS:
        for i in range(0, len(words), MAX_WORDS):
            chunk_text = " ".join(words[i:i + MAX_WORDS])
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text
            })
            chunk_id += 1
    else:
        chunks.append({
            "chunk_id": chunk_id,
            "text": para
        })
        chunk_id += 1

# Step 3: Save chunks
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2)

print(f"✅ Created {len(chunks)} clean chunks")

import fitz  # PyMuPDF

# List of Filariasis PDFs
pdf_files = [
    "data/FilariaEliminationPlan2018.pdf",
    "data/FilariaEliminationPlan2024.pdf"
]

all_text = ""

for pdf_path in pdf_files:
    print(f"Extracting from {pdf_path}")
    doc = fitz.open(pdf_path)

    for page_number, page in enumerate(doc, start=1):
        all_text += f"\n\n--- {pdf_path} | Page {page_number} ---\n"
        all_text += page.get_text()

# Save raw extracted text
with open("output/raw_filaria_text.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

print("Milestone 1: Text extraction completed.")

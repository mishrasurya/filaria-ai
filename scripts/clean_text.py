import re
import unicodedata

INPUT_FILE = "output/raw_filaria_text.txt"
OUTPUT_FILE = "output/final_filaria_clean.txt"


def clean_text(text: str) -> str:

    # ------------------------------------------------
    # 1. Unicode normalization (industry standard)
    # ------------------------------------------------
    text = unicodedata.normalize("NFKC", text)
    

    # Remove replacement characters (CRITICAL)
    text = text.replace("\uFFFD", "")

    # Remove zero-width / BOM artifacts
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)


    # ------------------------------------------------
    # 2. Remove control / invisible characters
    # IMPORTANT: Preserve newline (\x0A) and tab (\x09)
    # ------------------------------------------------
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # ------------------------------------------------
    # 3. Remove PDF page markers / separators
    # Example: --- data/file.pdf | Page 110 ---
    # ------------------------------------------------
    text = re.sub(r"---.*?Page\s+\d+.*?---", "", text)

    # ------------------------------------------------
    # 4. Remove standalone page numbers
    # ------------------------------------------------
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # ------------------------------------------------
    # 5. Fix hyphenated line breaks (very common in PDFs)
    # ------------------------------------------------
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # ------------------------------------------------
    # 6. Trim trailing / leading spaces per line
    # Preserve paragraph structure
    # ------------------------------------------------
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            cleaned_lines.append("")
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # ------------------------------------------------
    # 7. Normalize excessive spaces
    # ------------------------------------------------
    text = re.sub(r"[ \t]{2,}", " ", text)

    # ------------------------------------------------
    # 8. Normalize excessive blank lines (keep paragraphs)
    # ------------------------------------------------
    text = re.sub(r"\n{3,}", "\n\n", text)

    # ------------------------------------------------
    # 9. Remove decorative separator lines
    # ------------------------------------------------
    text = re.sub(r"^[\-_=\.\s]{8,}$", "", text, flags=re.MULTILINE)

    # ------------------------------------------------
    # 10. Normalize bullets (optional but recommended)
    # ------------------------------------------------
    text = re.sub(r"[•●▪◦]", "-", text)

    # ------------------------------------------------
    # 11. Remove extremely short noisy lines (optional)
    # ------------------------------------------------
    text = re.sub(r"^\s.{1,3}\s*$", "", text, flags=re.MULTILINE)

    return text.strip()


def main():
    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()

    cleaned_text = clean_text(raw_text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print("✅ Industry-level clean text generated:", OUTPUT_FILE)


if __name__ == "__main__":
    main()

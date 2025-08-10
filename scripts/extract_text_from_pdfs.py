import os
import fitz  # PyMuPDF
import json

PDF_DIR = "data/pdfs/"
OUTPUT_DIR = "knowledge_base/english/"

def extract_text_from_pdf(pdf_path):
    """Extracts text from all pages in the PDF."""
    text = []
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            page_text = page.get_text().strip()
            if page_text:
                text.append(page_text)
        return "\n".join(text)
    except Exception as e:
        print(f"[ERROR] Could not read {pdf_path}: {e}")
        return ""

def save_text_as_json(doc_name, text, source_file):
    """Saves extracted text to JSON with metadata."""
    output_path = os.path.join(OUTPUT_DIR, f"{doc_name}.json")
    data = {
        "type": "pdf",
        "source": source_file,
        "text": text
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def process_all_pdfs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename in os.listdir(PDF_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIR, filename)
            doc_name = os.path.splitext(filename)[0]
            print(f"[INFO] Extracting {filename}")
            text = extract_text_from_pdf(pdf_path)
            if text:
                save_text_as_json(doc_name, text, filename)
    print("[DONE] PDF text extraction complete.")

if __name__ == "__main__":
    process_all_pdfs()

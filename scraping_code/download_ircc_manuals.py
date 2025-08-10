import os
import json
import requests

# Paths
LINKS_FILE = "data/manuals_links.json"
PDF_FOLDER = "data/manuals_pdfs"

# Create folder if it doesn't exist
os.makedirs(PDF_FOLDER, exist_ok=True)

# Load links from JSON
with open(LINKS_FILE, "r", encoding="utf-8") as f:
    pdf_list = json.load(f)

# Download all PDFs
for i, item in enumerate(pdf_list, start=1):
    title = item["title"].split("(")[0].strip()  # Remove size info from title
    filename = title.replace("/", "-").replace(" ", "_").replace("__", "_") + ".pdf"
    filepath = os.path.join(PDF_FOLDER, filename)
    
    print(f"[{i}/{len(pdf_list)}] Downloading: {title}")
    
    try:
        response = requests.get(item["url"], timeout=20)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"    ➤ Saved to: {filepath}")
    except Exception as e:
        print(f"    ✖ Failed to download: {title} ({e})")

print("\n✅ All PDFs processed.")

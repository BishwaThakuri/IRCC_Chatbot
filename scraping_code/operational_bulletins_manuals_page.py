import requests
from bs4 import BeautifulSoup
import json
import os

BASE_URL = "https://www.canada.ca/en/immigration-refugees-citizenship/corporate/publications-manuals/operational-bulletins-manuals.html"
OUTPUT_FILE = "data/manuals_links.json"
PDF_FOLDER = "data/manuals_pdfs"

res = requests.get(BASE_URL)
soup = BeautifulSoup(res.text, "html.parser")

links = []
for a in soup.select("a[href$='.pdf']"):
    title = a.text.strip()
    url = a["href"]
    if not url.startswith("http"):
        url = "https://www.canada.ca" + url
    links.append({"title": title, "url": url})

os.makedirs(PDF_FOLDER, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(links, f, indent=2)
print(f"Found {len(links)} PDF(s), saved to {OUTPUT_FILE}")

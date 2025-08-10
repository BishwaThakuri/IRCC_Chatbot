import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.cic.gc.ca/english/information/fees/fees.asp"

def scrape_fees():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    fee_data = []

    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        rows = table.find_all("tr")[1:]  # skip header row

        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cells) == len(headers):
                fee_data.append(dict(zip(headers, cells)))

    with open("ircc_fees.json", "w", encoding="utf-8") as f:
        json.dump(fee_data, f, indent=2, ensure_ascii=False)

    print(f"[DONE] Extracted {len(fee_data)} fee records.")

if __name__ == "__main__":
    scrape_fees()

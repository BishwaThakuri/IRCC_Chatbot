import os
import json

INPUT_DIR = "data/scraped_json"
OUTPUT_DIR = "knowledge_base/english"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_json_files():
    for file in os.listdir(INPUT_DIR):
        if not file.endswith(".json"):
            continue
        
        file_path = os.path.join(INPUT_DIR, file)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts = []

        for item in data:
            if "processing_time" in item:
                txt = (
                    f"Category: {item.get('category', '')}\n"
                    f"Subcategory: {item.get('subcategory', '')}\n"
                    f"Country: {item.get('country', '')}\n"
                    f"Processing Time: {item.get('processing_time', '')}\n"
                    f"Last Updated: {item.get('last_updated', '')}"
                )
                texts.append(txt.strip())

            elif "Fees" in item and "$CAN" in item:
                txt = f"Service: {item['Fees']}\nFee: ${item['$CAN']} CAD"
                texts.append(txt.strip())

            elif "question" in item and "answer" in item:
                txt = f"Q: {item['question']}\nA: {item['answer']}"
                texts.append(txt.strip())

        if texts:
            output_path = os.path.join(OUTPUT_DIR, f"{file.replace('.json', '')}_text.json")
            with open(output_path, "w", encoding="utf-8") as out_f:
                json.dump({"text": "\n\n".join(texts)}, out_f, indent=2, ensure_ascii=False)
            print(f"[✓] {file} → {len(texts)} entries saved to {output_path}")
        else:
            print(f"[!] No valid entries in {file}, skipped.")

    print("[DONE] All JSON files processed.")

if __name__ == "__main__":
    process_json_files()

from playwright.sync_api import sync_playwright, TimeoutError
import time
import json

# Target countries only
# TARGET_COUNTRIES = {"Nepal", "India", "Pakistan", "Bangladesh"}

# Target countries (40 total)
TARGET_COUNTRIES = {
    "Nepal", "India", "Pakistan", "Bangladesh", "Afghanistan", "Sri Lanka", "Bhutan", "China", "Philippines",
    "Nigeria", "Kenya", "Ghana", "Uganda", "South Africa", "Egypt", "Morocco", "Algeria", "Tunisia",
    "Iran", "Iraq", "Syria", "Lebanon", "Turkey", "Indonesia", "Vietnam", "Thailand", "Malaysia",
    "Mexico", "Brazil", "Colombia", "Peru", "Venezuela", "Haiti", "Jamaica", "Ukraine", "Russia",
    "United Arab Emirates", "Saudi Arabia", "Yemen", "Ethiopia"
}

def scrape_processing_times():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Change to False to see browser
        page = browser.new_page()
        page.goto("https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-processing-times.html")
        time.sleep(5)

        results = []

        # Main category dropdown
        category_selector = "select[id*=wb-auto][name*=wb-fieldflow]:nth-of-type(1)"
        page.wait_for_selector(category_selector)
        categories = page.query_selector_all(f"{category_selector} option")[1:]

        for category_option in categories:
            category_value = category_option.get_attribute("value")
            category_label = category_option.inner_text().strip()
            print(f"\n[INFO] Category: {category_label}")
            page.select_option(category_selector, category_value)
            time.sleep(3)

            # Subcategory dropdown
            sub_selector = "select[id*=wb-auto][name*=wb-fieldflow]:nth-of-type(2)"
            try:
                page.wait_for_selector(sub_selector, timeout=10000)
            except TimeoutError:
                print("  [WARN] No subcategory found, skipping...")
                continue

            sub_options = page.query_selector_all(f"{sub_selector} option")[1:]
            for sub_option in sub_options:
                sub_value = sub_option.get_attribute("value")
                sub_label = sub_option.inner_text().strip()
                print(f"  [INFO] Subcategory: {sub_label}")
                page.select_option(sub_selector, sub_value)
                time.sleep(3)

                # Try to detect if country dropdown exists
                country_selector = "select[id*=wb-auto][name*=wb-fieldflow]:nth-of-type(3)"
                country_dropdown_exists = True
                try:
                    page.wait_for_selector(country_selector, timeout=5000)
                except TimeoutError:
                    country_dropdown_exists = False
                    print("    [INFO] No country dropdown found for this subcategory")

                if country_dropdown_exists:
                    countries = page.query_selector_all(f"{country_selector} option")[1:]
                    for country_option in countries:
                        country_value = country_option.get_attribute("value")
                        country_label = country_option.inner_text().strip()

                        if country_label not in TARGET_COUNTRIES:
                            continue

                        print(f"    🌍 Country: {country_label}")
                        page.select_option(country_selector, country_value)
                        time.sleep(2)

                        try:
                            page.click("button.btn-submit")
                            page.wait_for_selector("div.panel-body", timeout=10000)

                            processing_time_span = page.query_selector("span[data-json-replace*='ptime']")
                            last_updated_span = page.query_selector("span[data-json-replace*='lastupdated']")

                            processing_time = processing_time_span.inner_text().strip() if processing_time_span else "N/A"
                            last_updated = last_updated_span.inner_text().strip() if last_updated_span else "N/A"

                            print(f"      ⏱️ {processing_time} (Updated: {last_updated})")

                            results.append({
                                "category": category_label,
                                "subcategory": sub_label,
                                "country": country_label,
                                "processing_time": processing_time,
                                "last_updated": last_updated
                            })

                        except Exception as e:
                            print(f"      [ERROR] Could not extract result for {country_label}: {e}")
                            results.append({
                                "category": category_label,
                                "subcategory": sub_label,
                                "country": country_label,
                                "processing_time": "N/A",
                                "last_updated": "N/A"
                            })

                else:
                    # No country dropdown → scrape directly for this subcategory
                    print("    [INFO] Extracting data without country filter")
                    try:
                        page.click("button.btn-submit")
                        page.wait_for_selector("div.panel-body", timeout=10000)

                        processing_time_span = page.query_selector("span[data-json-replace*='ptime']")
                        last_updated_span = page.query_selector("span[data-json-replace*='lastupdated']")

                        processing_time = processing_time_span.inner_text().strip() if processing_time_span else "N/A"
                        last_updated = last_updated_span.inner_text().strip() if last_updated_span else "N/A"

                        print(f"      ⏱️ {processing_time} (Updated: {last_updated})")

                        results.append({
                            "category": category_label,
                            "subcategory": sub_label,
                            "country": None,
                            "processing_time": processing_time,
                            "last_updated": last_updated
                        })
                    except Exception as e:
                        print(f"      [ERROR] Could not extract result without country filter: {e}")
                        results.append({
                            "category": category_label,
                            "subcategory": sub_label,
                            "country": None,
                            "processing_time": "N/A",
                            "last_updated": "N/A"
                        })

        browser.close()

        # Save results to JSON
        with open("ircc_processing_times_selected.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Done. Saved {len(results)} entries to 'ircc_processing_times_selected.json'")

if __name__ == "__main__":
    scrape_processing_times()
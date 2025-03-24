from playwright.sync_api import sync_playwright
import csv
import os
import time
from concurrent.futures import ThreadPoolExecutor

# ✅ Adjustable number of parallel processes
NUM_WORKERS = 10  # Change this value as needed

# File paths
input_file_path = r"C:\Users\Abdul Moiz Nouman\Desktop\All IN ONE\EXTRA\Scraper\sec_data.csv"
output_file_path = r"C:\Users\Abdul Moiz Nouman\Desktop\All IN ONE\EXTRA\Scraper\extracted_file_links.csv"

# ❌ Not allowed extensions (Images only)
not_allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff", ".webp"}

# ✅ Read document links from CSV
document_links = []
try:
    with open(input_file_path, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if "Document Link" in row:
                document_links.append(row["Document Link"])
except FileNotFoundError:
    print(f"❌ CSV file not found at: {input_file_path}")
    exit()

print(f"📂 Found {len(document_links)} document links to process.")

# ✅ Step 1: Check already processed links to avoid duplicates
processed_links = set()
if os.path.exists(output_file_path):
    with open(output_file_path, "r", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header
        for row in reader:
            if row:
                processed_links.add(row[0])  # Add source links to processed set

# ✅ Function to process a single document link
def process_link(doc_link, index, total_links):
    if doc_link in processed_links:
        print(f"🔄 [{index}] Skipping already processed: {doc_link}")
        return
    
    print(f"\n🔗 [{index}/{total_links}] Visiting: {doc_link}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Change to False if you want to see the browser actions
        context = browser.new_context()

        try:
            page = context.new_page()
            page.goto(doc_link, wait_until="domcontentloaded")
            time.sleep(2)  # Allow time for page to load

            # ✅ Extract links only from the specific table
            rows = page.locator("table.tableFile tbody tr").all()
            print(f"📑 [{index}] Found {len(rows)} rows in the table.")

            found_links = []
            for row_index, row in enumerate(rows, start=1):
                link_element = row.locator("td:nth-child(3) a")
                if link_element.count() > 0:
                    href = link_element.first.get_attribute("href")

                    if href:
                        href = href.strip()
                        full_url = f"https://www.sec.gov{href}" if href.startswith("/") else href
                        file_extension = os.path.splitext(full_url)[1].lower()

                        if file_extension in not_allowed_extensions:
                            print(f"🚫 [{index}-Row {row_index}] Skipped image file: {full_url}")
                        else:
                            found_links.append(full_url)
                            print(f"✅ [{index}-Row {row_index}] Extracted: {full_url}")

            if found_links:
                print(f"✅ [{index}] Extracted {len(found_links)} valid file links from {doc_link}")

                # ✅ Write to CSV immediately (append mode)
                with open(output_file_path, "a", newline="", encoding="utf-8-sig") as file:
                    writer = csv.writer(file)
                    for file_link in found_links:
                        writer.writerow([doc_link, file_link])

            else:
                print(f"⚠️ [{index}] No valid file links found in: {doc_link}")

        except Exception as e:
            print(f"❌ [{index}] Error processing {doc_link}: {e}")

        finally:
            browser.close()  # Ensure the browser is closed properly

# ✅ Step 2: Use ThreadPoolExecutor for parallel processing
if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {
            executor.submit(process_link, doc_link, index, len(document_links)): doc_link
            for index, doc_link in enumerate(document_links, start=1)
        }
    
    print("\n✅ All tasks completed. Extracted links saved to:", output_file_path)

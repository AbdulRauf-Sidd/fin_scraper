from playwright.async_api import async_playwright
import asyncio
import csv
import os
from utils.utils import download_file

NUM_CONCURRENT_TASKS = 100  # Control concurrency
input_file_path = "SEC/sec_data.csv"
output_file_path = "SEC/extracted_file_links.csv"

not_allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff", ".webp"}

# Read document links
with open(input_file_path, "r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    document_links = [row["Document Link"] for row in reader if "Document Link" in row]

processed_links = set()
if os.path.exists(output_file_path):
    with open(output_file_path, "r", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if row:
                processed_links.add(row[0])

# Async function
async def process_link(sem, browser, doc_link, index, total_links):
    if doc_link in processed_links:
        print(f"🔄 [{index}] Skipping already processed: {doc_link}")
        return

    async with sem:
        print(f"\n🔗 [{index}/{total_links}] Visiting: {doc_link}")
        context = await browser.new_context()
        try:
            page = await context.new_page()
            await page.goto(doc_link, wait_until="domcontentloaded")
            await asyncio.sleep(2)

            rows = await page.locator("table.tableFile tbody tr").all()
            found_links = []

            for row_index, row in enumerate(rows, start=1):
                link_element = row.locator("td:nth-child(3) a")
                if await link_element.count() > 0:
                    href = await link_element.first.get_attribute("href")
                    if href:
                        full_url = f"https://www.sec.gov{href}" if href.startswith("/") else href
                        ext = os.path.splitext(full_url)[1].lower()

                        if ext in not_allowed_extensions:
                            print(f"🚫 [{index}-Row {row_index}] Skipped image: {full_url}")
                        else:
                            found_links.append(full_url)
                            print(f"✅ [{index}-Row {row_index}] Extracted: {full_url}")

            if found_links:
                with open(output_file_path, "a", newline="", encoding="utf-8-sig") as file:
                    writer = csv.writer(file)
                    for file_link in found_links:
                        writer.writerow([doc_link, file_link])
            else:
                print(f"⚠️ [{index}] No valid links found.")
        except Exception as e:
            print(f"❌ [{index}] Error: {e}")
        finally:
            await context.close()

async def main():
    sem = asyncio.Semaphore(NUM_CONCURRENT_TASKS)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        tasks = [
            process_link(sem, browser, doc_link, index, len(document_links))
            for index, doc_link in enumerate(document_links, start=1)
        ]
        await asyncio.gather(*tasks)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
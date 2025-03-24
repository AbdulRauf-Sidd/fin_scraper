from playwright.async_api import async_playwright
import asyncio
import csv
import os
import sys
import importlib
from pathlib import Path

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent  # This gets the root directory
sys.path.append(str(ROOT_DIR))

# Import the downloads function dynamically
utils_module = importlib.import_module("utils.utils")
download_file = getattr(utils_module, "download_file")

NUM_CONCURRENT_TASKS = 10  # Control concurrency
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
async def process_link(sem, browser, doc_link, index, total_links, download_folder):
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
                            print(f"✅ [{index}-Row {row_index}] Downloading: {full_url}")
                            await download_sec_document(full_url)
                            # await download_file(full_url, download_folder)  # Call download function

            print(f"✅ [{index}] Finished processing: {doc_link}")

        except Exception as e:
            print(f"❌ [{index}] Error: {e}")
        finally:
            await context.close()


async def main():
    sem = asyncio.Semaphore(NUM_CONCURRENT_TASKS)
    download_folder = "SEC/downloads"  # Folder where files will be saved
    os.makedirs(download_folder, exist_ok=True)  # Ensure the folder exists

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        tasks = [
            process_link(sem, browser, doc_link, index, len(document_links), download_folder)
            for index, doc_link in enumerate(document_links, start=1)
        ]
        await asyncio.gather(*tasks)
        await browser.close()





import asyncio
import os
from playwright.async_api import async_playwright

async def download_sec_document(url, output_folder="downloads"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run in non-headless mode
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.sec.gov/",
            }
        )
        page = await context.new_page()

        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)

        print(f"🔍 Visiting: {url}")
        await page.goto(url, wait_until="domcontentloaded")

        # Extract file name from URL
        filename = url.split("/")[-1]
        file_path = os.path.join(output_folder, filename)

        # Save page content
        content = await page.content()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        abs_path = os.path.abspath(file_path)
        print(f"✅ Downloaded successfully: {abs_path}")

        await browser.close()
        return abs_path




if __name__ == "__main__":
    asyncio.run(main())

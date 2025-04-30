from playwright.async_api import async_playwright
import asyncio
import csv
import os
import sys
from pathlib import Path

# Setup paths and add the root directory if needed
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

NUM_CONCURRENT_TASKS = 1  # Control concurrency
input_file_path = "SEC/sec_data.csv"
output_file_path = "SEC/extracted_file_links.csv"

not_allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff", ".webp"}

# Read document links from the CSV file
with open(input_file_path, "r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    document_links = [row["Document Link"] for row in reader if "Document Link" in row]

# Maintain a set of already processed links to avoid reprocessing them
processed_links = set()
if os.path.exists(output_file_path):
    with open(output_file_path, "r", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header
        for row in reader:
            if row:
                processed_links.add(row[0])

# Define a constant SEC-compliant User-Agent string.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "FinScraper/1.0 (contact@example.com)")

# New local download function for SEC files using Playwright's request API.
async def sec_download_file(context, url, download_folder):
    """
    Downloads a file using Playwright's request API (which uses the browser session's headers and cookies)
    and saves it to the specified folder.

    Parameters:
        context (BrowserContext): The Playwright browser context.
        url (str): The URL of the file to download.
        download_folder (str): The folder where the file should be saved.

    Returns:
        tuple: (absolute_path, filename, file_type, "download") on success,
               or (None, None, None, None) on failure.
    """
    # Clean the URL and determine the filename.
    url = url.rstrip('/')
    filename = url.split("/")[-1] if "/" in url else "downloaded_file"

    # Ensure the download folder exists.
    os.makedirs(download_folder, exist_ok=True)
    file_path = os.path.join(download_folder, filename)

    print(f"📡 Starting download from: {url}")
    try:
        # Explicitly set headers using our constant USER_AGENT.
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": "https://www.sec.gov/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        response = await context.request.get(url, timeout=15000, headers=headers)
        if not response.ok:
            print(f"⚠️ Failed to download file. HTTP Status: {response.status}")
            return None, None, None, None

        content = await response.body()
        with open(file_path, "wb") as f:
            f.write(content)

        absolute_path = os.path.abspath(file_path)
        print(f"✅ Successfully downloaded: {absolute_path}")
        print(f"📁 File saved at: {absolute_path}")

        # Placeholder for file type logic if needed in the future.
        file_type = "unknown"

        return absolute_path, filename, file_type, "download"
    except Exception as e:
        print(f"❌ Error downloading file from {url}: {e}")
        return None, None, None, None

# Async function to process each SEC document link.
async def process_link(sem, browser, doc_link, index, total_links, download_folder):
    if doc_link in processed_links:
        print(f"🔄 [{index}] Skipping already processed: {doc_link}")
        return

    async with sem:
        print(f"\n🔗 [{index}/{total_links}] Visiting: {doc_link}")
        # Create a new browser context using the SEC-compliant user agent.
        context = await browser.new_context(user_agent=USER_AGENT)
        try:
            page = await context.new_page()
            await page.goto(doc_link, wait_until="domcontentloaded")
            await asyncio.sleep(2)  # Wait a moment for the page to load completely

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
                            await sec_download_file(context, full_url, download_folder)
            print(f"✅ [{index}] Finished processing: {doc_link}")
        except Exception as e:
            print(f"❌ [{index}] Error: {e}")
        finally:
            await context.close()

# Main async function to launch the browser and process all document links.
async def main():
    sem = asyncio.Semaphore(NUM_CONCURRENT_TASKS)
    download_folder = "SEC/downloads/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        tasks = [
            process_link(sem, browser, doc_link, index, len(document_links), download_folder)
            for index, doc_link in enumerate(document_links, start=1)
        ]
        await asyncio.gather(*tasks)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import random
import json
import argparse
import traceback
from datetime import datetime
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import re
from utils import * 

# Argument Parsing
parser = argparse.ArgumentParser(description="SEC Filings Scraper")
parser.add_argument("url", type=str, help="SEC Filings page URL")
parser.add_argument("ticker", type=str, help="Equity ticker symbol")
parser.add_argument("--output", type=str, default="sec_filings.json", help="Output JSON file name")

args = parser.parse_args()

# Configurations
SEC_FILINGS_URL = args.url
EQUITY_TICKER = args.ticker.upper()  # Convert to uppercase for standardization
JSON_FILENAME = args.output
VALID_YEARS = {str(year) for year in range(2019, 2026)}  # 2019-2025

# Track visited pages
visited_urls = set()
file_links_collected = []
stop_scraping = False



async def enable_stealth(page):
    """Inject JavaScript to evade bot detection."""
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)


from dateutil.parser import parse

import asyncio




async def parse_date3(date_str):
    """Parses a date string like 'Tuesday, February 25, 2025' into 'YYYY/MM/DD' format."""
    try:
        parsed_date = parse(date_str, fuzzy=True)
        return parsed_date  # Returns a datetime object
    except Exception as e:
        print(f"⚠️ Error parsing date: {date_str} -> {e}")
        return None  # Return None if parsing fails


import re
from urllib.parse import urljoin
from datetime import datetime
from playwright.async_api import async_playwright



async def extract_files_from_page(page):
    """Extracts corporate governance documents and associated file links."""
    global stop_scraping
    try:
        # Select all document download items
        document_items = await page.query_selector_all(".module_item")

        for item in document_items:
            try:
                # Extract file link and name
                link_element = await item.query_selector(":scope .module-downloads_title a")
                file_name = await link_element.inner_text() if link_element else "Unknown Document"
                file_url = await link_element.get_attribute("href") if link_element else None

                if not file_url:
                    print("⚠️ No valid URL found, skipping.")
                    continue

                # Ensure full URL
                if file_url.startswith("//"):
                    file_url = "https:" + file_url

                # Extract date from file name (assumed format includes YYYY/MM)
                date_match = re.search(r'(\d{4})/(\d{2})', file_url)
                event_date = f"{date_match.group(1)}/{date_match.group(2)}/01" if date_match else "UNKNOWN DATE"

                # Determine file type
                file_type = file_url.split(".")[-1] if "." in file_url else "unknown"

                # Construct JSON object
                data_files = [{
                    "file_name": file_name.strip(),
                    "file_type": file_type,
                    "date": event_date,
                    "category": "corporate_governance",
                    "source_url": file_url,
                    "wissen_url": "unknown"
                }]

                # Append structured event data
                file_links_collected.append({
                    "equity_ticker": "UNKNOWN",
                    "source_type": "company_information",
                    "frequency": "non-periodic",
                    "event_type": "corporate_governance",
                    "event_name": file_name.strip(),
                    "event_date": event_date,
                    "data": data_files
                })

                print(f"✅ Extracted document: {file_name}, Date: {event_date}, URL: {file_url}")

            except Exception as e:
                print(f"⚠️ Error processing a document: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting files: {e}")






async def find_next_page(page):
    """Finds and returns the next page URL if pagination exists."""
    try:
        await page.wait_for_selector("a", timeout=10000)
        all_links = await page.query_selector_all("a")
        for link in all_links:
            text = await link.inner_text()
            if "Next" in text or ">" in text:
                next_page_url = await link.get_attribute("href")
                return urljoin(SEC_FILINGS_URL, next_page_url)
    except Exception as e:
        print(f"⚠️ Error finding next page: {e}")
    return None

async def scrape_sec_filings():
    """Main function to scrape SEC filings."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": SEC_FILINGS_URL
        })

        page = await context.new_page()
        await enable_stealth(page)

        current_url = SEC_FILINGS_URL
        while current_url and current_url and not stop_scraping:
            visited_urls.add(current_url)
            print(f"\n🔍 Visiting: {current_url}")
            try:
                await page.goto(current_url, wait_until="load", timeout=120000)
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
            except Exception as e:
                print(f"⚠️ Failed to load {current_url}: {e}")
                break

            await extract_files_from_page(page)
            await asyncio.sleep(random.uniform(1, 3))  # Human-like delay

            next_page = await find_next_page(page)
            if next_page and not stop_scraping:
                current_url = next_page
            else:
                break

        if file_links_collected:
            with open(JSON_FILENAME, "w", encoding="utf-8") as f:
                json.dump(file_links_collected, f, indent=4)
            print(f"\n✅ File links saved in: {JSON_FILENAME}")
        else:
            print("\n❌ No file links found.")

        await browser.close()

# Run the scraper
asyncio.run(scrape_sec_filings())

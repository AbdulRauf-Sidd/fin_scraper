import asyncio
import random
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import re
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from utils import *

# Argument Parsing
# parser = argparse.ArgumentParser(description="SEC Filings Scraper")
# parser.add_argument("url", type=str, help="SEC Filings page URL")
# parser.add_argument("ticker", type=str, help="Equity ticker symbol")
# parser.add_argument("--output", type=str, default="sec_filings.json", help="Output JSON file name")

# args = parser.parse_args()

# Configurations
SEC_FILINGS_URL = "https://investors.corescientific.com/financial-information/financial-results"
EQUITY_TICKER = "CORZ"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/corz_finance.json"
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


import asyncio
import re
from playwright.async_api import async_playwright
from urllib.parse import urljoin

async def parse_date(date_str):
    """Parses various date formats and returns a standardized date (YYYY/MM/DD)."""
    date_str = date_str.strip()
    match = re.search(r'(\w+ \d{1,2}, \d{4})', date_str)  # Extracts "Dec 31, 2024"
    if match:
        from datetime import datetime
        try:
            return datetime.strptime(match.group(1), "%b %d, %Y").strftime("%Y/%m/%d")
        except ValueError:
            return None
    return None

async def extract_files_from_page(page):
    """Extracts events and associated files from the page."""
    global stop_scraping
    try:
        event_rows = await page.query_selector_all('xpath=//div[@class=" row"]')

  # Locate all events

        for event in event_rows:
            try:
                # Extract event date
                date_element = await event.query_selector(":scope .date")
                event_date_text = await date_element.inner_text() if date_element else "UNKNOWN DATE"
                event_date_parsed = await parse_date(event_date_text)

                if not event_date_parsed:
                    print(f"⚠️ Error parsing date: {event_date_text}")
                    continue
                
                # Extract all files only within the current row
                file_links = []
                file_elements = await event.query_selector_all(":scope .result-line a")

                for file_element in file_elements:
                    file_url = await file_element.get_attribute("href")
                    file_name = await file_element.inner_text()
                    file_type = "unknown"

                    # Determine file type based on URL or label
                    if file_url.endswith(".pdf"):
                        file_type = "pdf"
                    elif file_url.endswith(".htm"):
                        file_type = "htm"
                    elif file_url.endswith(".zip"):
                        file_type = "zip"
                    elif "Audio" in file_name or "Webcast" in file_name:
                        file_type = "audio"

                    # Ensure full URL if relative
                    if not file_url.startswith("http"):
                        file_url = urljoin(SEC_FILINGS_URL, file_url)

                    file_name = await extract_file_name(file_url)
                    

                    category = classify_document(file_url, file_url) 
                    file_type = get_file_type(file_url)


                    file_links.append({
                        "file_name": file_name.strip(),
                        "file_type": file_type,
                        "date": event_date_parsed,
                        "category": category,
                        "source_url": file_url,
                        "wissen_url": "NULL"
                    })

                    event_type = classify_periodic_type(file_url, file_url)
                event_name = format_quarter_string(event_date_parsed, 'abcdef')

                # Store the extracted event
                file_links_collected.append({
                    "equity_ticker": EQUITY_TICKER,
                    "source_type": "company_information",
                    "frequency": 'periodic',
                    "event_type": event_type,
                    "event_name": event_name,  # Adjust this if there's a better event title
                    "event_date": event_date_parsed,
                    "data": file_links
                })

                print(f"✅ Extracted event: {event_date_parsed}, Files: {len(file_links)}")

            except Exception as e:
                print(f"⚠️ Error processing an event: {e}")

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
        browser = await p.chromium.launch(headless=True)
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

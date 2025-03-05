import asyncio
import random
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin
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
SEC_FILINGS_URL = "https://www.givaudan.com/investors/financial-results/results-centre"
EQUITY_TICKER = "GIVD"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/givd_sec.json"
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

async def extract_files_from_page(page):
    """Extracts Givaudan financial reports and presentations using column-based structure with headers."""
    global stop_scraping
    try:
        # Select all rows within the table body
        table_rows = await page.query_selector_all("tbody tr")

        # Extract column headers (first row)
        header_row = table_rows[0] if table_rows else None
        column_headers = []
        
        if header_row:
            header_cells = await header_row.query_selector_all(":scope td:not(:first-child)")
            column_headers = [await cell.inner_text() for cell in header_cells]

        # Define mapping for column headers to event names
        event_name_map = {
            "First quarter sales": "3M",
            "Half year results": "HY",
            "Nine month sales": "9M",
            "Full year results": "FY"
        }

        # Extract year from a valid file name or default to "UNKNOWN YEAR"
        def extract_year_from_filename(filename):
            match = re.search(r"(\d{4})", filename)
            return match.group(1) if match else "UNKNOWN YEAR"
        
        factsheet_element = await page.query_selector("a[aria-label*='Explore the investor factsheet']")
        if factsheet_element:
            factsheet_url = await factsheet_element.get_attribute("href")

            # Ensure the URL is fully qualified
            if factsheet_url and not factsheet_url.startswith("http"):
                factsheet_url = urljoin(SEC_FILINGS_URL, factsheet_url)

            factsheet_data = {
                "equity_ticker": "GIVN",
                "source_type": "company_information",
                "frequency": "non-periodic",
                "event_type": "investor_factsheet",
                "event_name": "Investor Factsheet",
                "event_date": "NULL",
                "data": [{
                    "file_name": "Investor Factsheet",
                    "file_type": "webpage",
                    "date": "NULL",
                    "category": "factsheet",
                    "source_url": factsheet_url,
                    "wissen_url": "NULL"
                }]
            }

            file_links_collected.append(factsheet_data)
            print(f"✅ Extracted Investor Factsheet: {factsheet_url}")


        # Process each row (excluding the first row which contains headers)
        for row in table_rows[1:]:
            try:
                # Extract the event type (category) from the first column
                category_element = await row.query_selector(":scope td:first-child")
                category_name = await category_element.inner_text() if category_element else "Unknown Category"
                category_name = category_name.strip()

                # Select all event file columns (excluding the first column)
                event_cells = await row.query_selector_all(":scope td:not(:first-child)")

                for index, event_cell in enumerate(event_cells):
                    # Skip if there's no corresponding header
                    if index >= len(column_headers):
                        continue

                    event_header = column_headers[index].strip()
                    event_code = event_name_map.get(event_header, "UNKNOWN")

                    # Extract event file link
                    file_link = await event_cell.query_selector(":scope a[href]")
                    if not file_link:
                        continue  # Skip empty cells

                    file_url = await file_link.get_attribute("href")
                    if not file_url:
                        continue

                    # Ensure full URL
                    if not file_url.startswith("http"):
                        file_url = urljoin(SEC_FILINGS_URL, file_url)

                    # Extract file name
                    file_name = file_url.split("/")[-1]  # Get filename from URL

                    # Extract year from filename
                    file_year = extract_year_from_filename(file_name)

                    if int(file_year) < 2019:
                        print(f"🛑 Stopping: Found event from {file_year}, stopping scraper.")
                        stop_scraping = True  # Stop further processing
                        return  # Exit function immediately


                    # Construct final event name
                    event_name = f"{event_code} {file_year}"

                    # Determine file type
                    file_type = "pdf" if file_url.endswith(".pdf") else "webcast"

                    # Determine category type (report, presentation, webcast, etc.)
                    category = "report"
                    if "presentation" in file_name.lower():
                        category = "presentation"
                    elif "webcast" in file_name.lower() or "video" in file_url:
                        category = "webcast"
                    elif "summary" in file_name.lower():
                        category = "financial_summary"

                    # Classify event type based on category name
                    freq = classify_frequency(event_name, file_link)
                    if freq == "periodic":
                        event_type = classify_euro_periodic_type(event_name, file_link)
                        event_name = extract_quarter_from_name('', event_name)
                    else:
                        event_type = categorize_event(event_name)


                    category = classify_document(event_name, file_link) 
                    file_type = get_file_type(file_link)

                    # Append structured event data
                    file_links_collected.append({
                        "equity_ticker": "GIVN",
                        "source_type": "company_information",
                        "frequency": freq,
                        "event_type": event_type,
                        "event_name": event_name,
                        "event_date": "null",
                        "data": [{
                            "file_name": file_name,
                            "file_type": file_type,
                            "date": "null",
                            "category": category,
                            "source_url": file_url,
                            "wissen_url": "null"
                        }]
                    })

                    print(f"✅ Extracted event: {event_name}, File: {file_name}")

            except Exception as e:
                print(f"⚠️ Error processing a row: {e}")

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

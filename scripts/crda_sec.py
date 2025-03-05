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


import asyncio
from urllib.parse import urljoin

async def extract_files_from_page(page):
    """Extracts investor results from Croda pages for years 2024 to 2019."""
    global stop_scraping
    try:
        for year in range(2024, 2018, -1):  # Loop from 2024 down to 2019
            table_selector = f"table#table-{year} tbody tr"

            # Select all event rows for the current year
            event_rows = await page.query_selector_all(table_selector)
            if not event_rows:
                print(f"⚠️ No table found for {year}, skipping...")
                continue  # Skip to the next year if table is missing

            print(f"\n🔍 Extracting events for {year}...")

            for event_row in event_rows:
                try:
                    # Extract event date
                    date_element = await event_row.query_selector("td[data-label='Date'] div")
                    event_date = await date_element.inner_text() if date_element else "UNKNOWN DATE"
                    event_date_parsed = await parse_date3(event_date)

                    if not event_date_parsed:
                        print(f"⚠️ Error parsing date: {event_date}")
                        continue

                    # Extract event name
                    title_element = await event_row.query_selector("td[data-label='Title'] h3")
                    event_name = await title_element.inner_text() if title_element else "Unknown Event"

                    # Extract files (only PDFs and HTML)
                    file_links = []
                    file_columns = ["Announcement", "Presentations", "Reports", "Transcript", "Video"]

                    for col_name in file_columns:
                        file_cell = await event_row.query_selector(f"td[data-label='{col_name}'] a")
                        if file_cell:
                            file_url = await file_cell.get_attribute("href")
                            file_type = "pdf" if file_url.endswith(".pdf") else "video" if "video" in file_url else "html"

                            if not file_url.startswith("http"):
                                file_url = urljoin(SEC_FILINGS_URL, file_url)

                            file_links.append({
                                "file_name": file_url.split("/")[-1],
                                "file_type": file_type,
                                "date": event_date_parsed.strftime("%Y/%m/%d"),
                                "category": col_name,
                                "source_url": file_url,
                                "wissen_url": "unknown"
                            })

                    # Skip events with no valid files
                    if not file_links:
                        continue

                    # Classify event type
                    freq = classify_frequency(event_name, file_links[0]["source_url"])
                    event_type = "event"
                    if freq == "periodic":
                        event_type = classify_euro_periodic_type(event_name, file_links[0]["source_url"])

                    event_name2 = format_quarter_string(event_date_parsed.strftime("%Y/%m/%d"), event_name)

                    # Append structured event data
                    file_links_collected.append({
                        "equity_ticker": "CRODA",
                        "source_type": "company_information",
                        "frequency": freq,
                        "event_type": event_type,
                        "event_name": event_name2,
                        "event_date": event_date_parsed.strftime("%Y/%m/%d"),
                        "data": file_links
                    })

                    print(f"✅ Extracted event: {event_name}, Date: {event_date_parsed.strftime('%Y/%m/%d')}")

                except Exception as e:
                    print(f"⚠️ Error processing an event in {year}: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting events: {e}")



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

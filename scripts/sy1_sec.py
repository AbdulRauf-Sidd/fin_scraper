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
# parser = argparse.ArgumentParser(description="SEC Filings Scraper")
# parser.add_argument("url", type=str, help="SEC Filings page URL")
# parser.add_argument("ticker", type=str, help="Equity ticker symbol")
# parser.add_argument("--output", type=str, default="sec_filings.json", help="Output JSON file name")

# args = parser.parse_args()

# Configurations
SEC_FILINGS_URL = "https://www.symrise.com/investors/financial-results/"
EQUITY_TICKER = "SY1"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/sy1_sec.json"
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
    """Extracts financial report links from the page."""
    global stop_scraping
    try:
        # Find all event rows
        event_rows = await page.query_selector_all("div.t-row")

        for event_row in event_rows:
            try:
                # Extract event name
                name_element = await event_row.query_selector("div.t-cell p")
                event_name = await name_element.inner_text() if name_element else "Unknown Event"

                # Extract file link
                file_element = await event_row.query_selector("div.t-cell a")
                if not file_element:
                    print(f"⚠️ Skipping row: No file link for '{event_name}'")
                    continue

                file_url = await file_element.get_attribute("href")
                file_name = file_url.split("/")[-1] if file_url else "Unknown File"

                # Ensure full URL
                if not file_url.startswith("http"):
                    file_url = urljoin(SEC_FILINGS_URL, file_url)

                # Extract file type
                file_type = file_name.split(".")[-1] if "." in file_name else "unknown"

                # Extract year from event name (if possible)
                event_date_parsed = await parse_date3(event_name)
                event_year = event_date_parsed.year if event_date_parsed else "UNKNOWN"

                # Classify frequency and type
                freq = classify_frequency(event_name, file_url)
                event_type = "financial_report"
                if freq == "periodic":
                    event_type = classify_periodic_type(event_name, file_url)

                # Append structured event data
                file_links_collected.append({
                    "equity_ticker": "SYMRISE",
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": event_name.strip(),
                    "event_date": f"{event_year}/01/01",
                    "data": [{
                        "file_name": file_name,
                        "file_type": file_type,
                        "date": f"{event_year}/01/01",
                        "category": "financial_report",
                        "source_url": file_url,
                        "wissen_url": "unknown"
                    }]
                })

                print(f"✅ Extracted report: {event_name}, Year: {event_year}")

            except Exception as e:
                print(f"⚠️ Error processing an event row: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting files: {e}")


async def scrape_all_years(page):
    """Clicks on each year filter (from 2024 to 2020) and extracts data."""
    years_to_scrape = ["2025", "2024", "2023", "2022", "2021", "2020"]

    for year in years_to_scrape:
        try:
            print(f"\n🔄 Clicking year filter: {year}")

            # Find and click the year filter button
            year_button = await page.query_selector(f".download-list-filter[data-filter-value='{year}']")
            if year_button:
                await year_button.click()
                await asyncio.sleep(3)  # Wait for data to load
            else:
                print(f"⚠️ Year filter '{year}' not found. Skipping.")
                continue

            # Extract reports for the selected year
            await extract_files_from_page(page)

        except Exception as e:
            print(f"⚠️ Error switching to year {year}: {e}")


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

            await scrape_all_years(page)
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

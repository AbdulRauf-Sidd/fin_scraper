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
    """Extracts investor events from the page."""
    global stop_scraping
    try:
        # Get all available years from the dropdown
        year_options = await page.query_selector_all("#eventArchiveYear option")

        years = [await option.get_attribute("value") for option in year_options]
        years = [int(year) for year in years if year.isdigit()]
        years.sort(reverse=True)  # Start from the latest year

        for year in years:
            if year < 2019:
                break  # Stop if we reach below 2019

            print(f"🔄 Scraping events for year: {year}")

            # Select year from dropdown
            await page.select_option("#eventArchiveYear", str(year))
            await page.wait_for_timeout(2000)  # Allow content to refresh

            # Extract event blocks
            event_blocks = await page.query_selector_all(".module_item")

            for event in event_blocks:
                try:
                    # Extract event date
                    date_element = await event.query_selector(".module_date-text")
                    event_date = await date_element.inner_text() if date_element else "UNKNOWN DATE"
                    event_date_parsed = await parse_date3(event_date)

                    if not event_date_parsed:
                        print(f"⚠️ Error parsing date: {event_date}")
                        continue

                    # Extract event name
                    title_element = await event.query_selector(".module_headline a")
                    event_name = await title_element.inner_text() if title_element else "Unknown Event"

                    # Extract files (only PDFs & webcast links)
                    file_links = []

                    # Webcast link
                    webcast_element = await event.query_selector(".module_webcast a")
                    if webcast_element:
                        webcast_url = await webcast_element.get_attribute("href")
                        if webcast_url:
                            file_links.append({
                                "file_name": webcast_url.split("/")[-1],
                                "file_type": "video",
                                "date": event_date_parsed.strftime("%Y/%m/%d"),
                                "category": "webcast",
                                "source_url": webcast_url,
                                "wissen_url": "unknown"
                            })

                    # Attachments (PDFs)
                    attachment_elements = await event.query_selector_all(".module_attachments a")
                    for attachment in attachment_elements:
                        file_url = await attachment.get_attribute("href")
                        if file_url and file_url.endswith(".pdf"):
                            if not file_url.startswith("http"):
                                file_url = urljoin(SEC_FILINGS_URL, file_url)

                            file_links.append({
                                "file_name": file_url.split("/")[-1],
                                "file_type": "pdf",
                                "date": event_date_parsed.strftime("%Y/%m/%d"),
                                "category": "report",
                                "source_url": file_url,
                                "wissen_url": "unknown"
                            })

                    # Skip events with no valid files
                    if not file_links:
                        continue

                    # Classify event type
                    freq = classify_frequency(event_name, file_links[0]["source_url"])
                    event_type = classify_periodic_type(event_name, file_links[0]["source_url"])

                    # Append structured event data
                    file_links_collected.append({
                        "equity_ticker": "NVDA",
                        "source_type": "company_information",
                        "frequency": freq,
                        "event_type": event_type,
                        "event_name": event_name.strip(),
                        "event_date": event_date_parsed.strftime("%Y/%m/%d"),
                        "data": file_links
                    })

                    print(f"✅ Extracted event: {event_name}, Date: {event_date_parsed.strftime('%Y/%m/%d')}")

                except Exception as e:
                    print(f"⚠️ Error processing an event: {e}")

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

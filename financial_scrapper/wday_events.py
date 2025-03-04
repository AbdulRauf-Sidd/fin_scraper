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

async def load_all_events(page):
    """Clicks 'Load More Events' button until it no longer appears."""
    while True:
        try:
            # Check if the "Load More Events" button is present
            load_more_button = await page.query_selector(".wd_events_more")

            if not load_more_button:
                print("✅ No more 'Load More Events' button. All records loaded.")
                break  # Exit loop when the button no longer appears

            print("🔄 Clicking 'Load More Events' button...")
            await load_more_button.click()

            # Wait for new events to load
            await asyncio.sleep(5)  # Adjust delay if needed for slower pages

        except Exception as e:
            print(f"⚠️ Error clicking 'Load More Events' button: {e}")
            break  # Stop loop if there's an issue

    print("✅ All events are now loaded. Starting scraping...")



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
    """Extracts events and associated file links from the page."""
    global stop_scraping
    try:
        # Select all event blocks
        await load_all_events(page)
        event_items = await page.query_selector_all(".wd_event_info")

        for event in event_items:
            try:
                # Extract event name
                title_element = await event.query_selector(":scope .wd_title")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"

                # Extract event date
                date_element = await event.query_selector(":scope .wd_event_date")
                event_date_text = await date_element.inner_text() if date_element else "UNKNOWN DATE"
                event_date_parsed = await parse_date3(event_date_text)

                if not event_date_parsed:
                    print(f"⚠️ Error parsing date: {event_date_text}")
                    continue

                # Collect all related files
                data_files = []

                # Extract webcast links
                webcast_links = await event.query_selector_all(":scope .wd_event_webcast a")
                for webcast in webcast_links:
                    file_url = await webcast.get_attribute("href")
                    file_name = await webcast.inner_text()

                    if file_url:
                        data_files.append({
                            "file_name": file_name.strip(),
                            "file_type": "webcast",
                            "date": event_date_parsed.strftime("%Y/%m/%d"),
                            "category": "webcast",
                            "source_url": file_url.strip(),
                            "wissen_url": "unknown"
                        })

                # Extract other links from wd_summary
                summary_section = await page.query_selector(".wd_summary")
                if summary_section:
                    summary_links = await summary_section.query_selector_all("a")

                    for link in summary_links:
                        file_url = await link.get_attribute("href")
                        file_name = await link.inner_text()
                        aria_label = await link.get_attribute("aria-label")

                        # Determine file type
                        file_type = "unknown"
                        if file_url.endswith(".pdf") or (aria_label and "PDF" in aria_label):
                            file_type = "pdf"
                        elif "youtu" in file_url:
                            file_type = "video"

                        if file_url:
                            data_files.append({
                                "file_name": file_name.strip(),
                                "file_type": file_type,
                                "date": event_date_parsed.strftime("%Y/%m/%d"),
                                "category": "presentation" if file_type == "pdf" else "replay",
                                "source_url": file_url.strip(),
                                "wissen_url": "unknown"
                            })

                # Classify event frequency and type
                freq = classify_frequency(event_name, "")
                event_type = "expansion"
                if freq == "periodic":
                    event_type = classify_periodic_type(event_name, "")

                # Append structured event data
                file_links_collected.append({
                    "equity_ticker": EQUITY_TICKER,
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": event_name.strip(),
                    "event_date": event_date_parsed.strftime("%Y/%m/%d"),
                    "data": data_files
                })

                print(f"✅ Extracted event: {event_name}, Date: {event_date_parsed}, Files: {len(data_files)}")

            except Exception as e:
                print(f"⚠️ Error processing an event: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting files: {e}")


async def find_next_page(page):
    """Finds and returns the next page URL if pagination exists."""
    global stop_scraping  # Ensures we can stop the entire scraping process

    try:
        # Check the last event on the page to get the date
        date_elements = await page.query_selector_all(".wd_date")
        if date_elements:
            last_date_text = await date_elements[-1].inner_text()
            last_date_parsed = await parse_date2(last_date_text)

            if last_date_parsed and last_date_parsed.year < 2019:
                print(f"🛑 Stopping: Found event from {last_date_parsed.year}, no need to go further.")
                stop_scraping = True
                return None  # Stop pagination

        # Look for the "Next Page" button
        await page.wait_for_selector("a[aria-lwabel='Show next page']", timeout=10000)
        next_page_link = await page.query_selector("a[aria-label='Show next page']")

        if next_page_link:
            next_page_url = await next_page_link.get_attribute("href")
            if next_page_url and not stop_scraping:
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

import asyncio
import random
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from scripts.UTILS import utils

# Configurations
SEC_FILINGS_URL = "https://investor.workday.com/press-releases"
EQUITY_TICKER = "WDAY"
JSON_FILENAME = "JSONS/wday_press.json"
VALID_YEARS = {str(year) for year in range(2019, 2026)}

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


async def extract_files_from_page(page):
    """Extracts events and associated file links from the page."""
    global stop_scraping
    try:
        event_items = await page.query_selector_all(".wd_item")

        for event in event_items:
            try:
                # Extract event date
                date_element = await event.query_selector(":scope .wd_date")
                event_date_text = await date_element.inner_text() if date_element else "UNKNOWN DATE"

                # ✅ Ensure date parsing is awaited and converted to string
                event_date_parsed = await utils.parse_date3(event_date_text)
                event_date_str = event_date_parsed.strftime("%Y/%m/%d") if isinstance(event_date_parsed, datetime) else event_date_parsed

                if not event_date_str:
                    print(f"⚠️ Error parsing date: {event_date_text}")
                    continue

                # Extract event name and file link
                title_element = await event.query_selector(":scope .wd_title a")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"
                event_url = await title_element.get_attribute("href") if title_element else "Unknown URL"

                # ✅ Ensure file name extraction is awaited
                file_name = await utils.extract_file_name(event_url)

                # ✅ Ensure file type & category are properly extracted
                file_type = utils.get_file_type(event_url)
                category = utils.classify_document(event_name, event_url)

                # Store extracted data
                data_files = [{
                    "file_name": file_name,
                    "file_type": file_type,
                    "date": event_date_str,  # ✅ Converted to string
                    "category": category,
                    "source_url": event_url,
                    "wissen_url": "unknown"
                }]

                # Classify event frequency and type
                freq = utils.classify_frequency(event_name, event_url)
                if freq == "periodic":
                    event_type = utils.classify_periodic_type(event_name, event_url)
                else:
                    event_type = utils.categorize_event(event_name)

                # Append structured event data
                file_links_collected.append({
                    "equity_ticker": EQUITY_TICKER,
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": event_name.strip(),
                    "event_date": event_date_str,  # ✅ Converted to string
                    "data": data_files
                })

                print(f"✅ Extracted event: {event_name}, Date: {event_date_str}, URL: {event_url}")

            except Exception as e:
                print(f"⚠️ Error processing an event: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting files: {e}")


async def find_next_page(page):
    """Finds and returns the next page URL if pagination exists."""
    global stop_scraping

    try:
        # Check last event's date
        date_elements = await page.query_selector_all(".wd_date")
        if date_elements:
            last_date_text = await date_elements[-1].inner_text()

            # ✅ Ensure date parsing is awaited and converted to string
            last_date_parsed = await utils.parse_date3(last_date_text)
            last_date_str = last_date_parsed.strftime("%Y/%m/%d") if isinstance(last_date_parsed, datetime) else last_date_parsed

            if last_date_str and int(last_date_str.split("/")[0]) < 2019:
                print(f"🛑 Stopping: Found event from {last_date_str}, no need to go further.")
                stop_scraping = True
                return None

        # Look for "Next Page" button
        await page.wait_for_selector("a[aria-label='Show next page']", timeout=10000)
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
        while current_url and not stop_scraping:
            visited_urls.add(current_url)
            print(f"\n🔍 Visiting: {current_url}")
            try:
                await page.goto(current_url, wait_until="domcontentloaded", timeout=120000)
                await extract_files_from_page(page)
            except Exception as e:
                print(f"⚠️ Failed to load {current_url}: {e}")
                break

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

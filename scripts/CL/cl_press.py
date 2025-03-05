import asyncio
import random
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from scripts.UTILS import utils

# Argument Parsing
# parser = argparse.ArgumentParser(description="SEC Filings Scraper")
# parser.add_argument("url", type=str, help="SEC Filings page URL")
# parser.add_argument("ticker", type=str, help="Equity ticker symbol")
# parser.add_argument("--output", type=str, default="sec_filings.json", help="Output JSON file name")

# args = parser.parse_args()

# Configurations
SEC_FILINGS_URL = "https://investor.colgatepalmolive.com/press-releases"
EQUITY_TICKER = "CL"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/cl_press.json"
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
import time
from playwright.async_api import async_playwright

async def is_browser_idle(page, timeout=5):
    """
    Detects if the browser has been idle for the given timeout period (default: 5 seconds).
    Returns True if idle, otherwise False.
    """
    last_interaction_time = time.time()  # Initialize with the current time

    async def reset_idle_timer():
        """Resets the idle timer whenever a new interaction occurs."""
        nonlocal last_interaction_time
        last_interaction_time = time.time()

    # Attach event listeners to detect activity
    await page.expose_function("resetIdleTimer", reset_idle_timer)

    await page.evaluate("""
        () => {
            ['click', 'mousemove', 'scroll', 'keydown', 'load', 'DOMContentLoaded'].forEach(event => {
                document.addEventListener(event, () => window.resetIdleTimer(), { passive: true });
            });
        }
    """)

    while True:
        await asyncio.sleep(1)  # Check every second
        elapsed_time = time.time() - last_interaction_time
        if elapsed_time >= timeout:
            return True




import re
from urllib.parse import urljoin
from datetime import datetime
async def extract_files_from_page(page):
    """Extracts investor events from the Colgate-Palmolive page."""
    global stop_scraping
    try:
        # Select all event blocks
        event_blocks = await page.query_selector_all(".richText-content.mt-3.pt-5")

        for event in event_blocks:
            try:
                # Extract event name
                title_element = await event.query_selector("h3 span.ss--font-size-21px")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"

                # Extract event date
                date_element = await event.query_selector("p span.ss--color-deep-grey")
                event_date_text = await date_element.inner_text() if date_element else None
                event_date_parsed = await parse_date3(event_date_text) if event_date_text else None
                event_date = event_date_parsed.strftime("%Y/%m/%d") if event_date_parsed else "UNKNOWN DATE"

                # Extract event details URL
                event_url_element = await event.query_selector("p a.cta.ss--arrow-icon")
                event_url = await event_url_element.get_attribute("href") if event_url_element else None
                if event_url and not event_url.startswith("http"):
                    event_url = urljoin(SEC_FILINGS_URL, event_url)

                if event_date_parsed.year < 2019:
                    stop_scraping = True
                    break


                freq = classify_frequency(event_name, event_url)
                if freq == "periodic":
                    event_type = classify_periodic_type(event_name, event_url)
                    event_name = format_quarter_string(event_date, event_name)
                else:
                    event_type = categorize_event(event_name)

                category = classify_document(event_name, event_url) 
                file_type = get_file_type(event_url)

                file_name = await extract_file_name(event_url)

                # Store the extracted event
                file_links_collected.append({
                    "equity_ticker": "CL",
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": "press release",
                    "event_name": event_name.strip(),
                    "event_date": event_date,
                    "data": [{
                        "file_name": file_name,
                        "file_type": file_type,
                        "date": event_date,
                        "category": category,
                        "source_url": event_url if event_url else "NULL",
                        "wissen_url": "NULL"
                    }]
                })

                print(f"✅ Extracted event: {event_name}, Date: {event_date}")

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
        page_num = 0
        while current_url and current_url and not stop_scraping:
            visited_urls.add(current_url + "?page=" + str(page_num))
            print(f"\n🔍 Visiting: {current_url}")
            try:
                await page.goto(current_url + "?page=" + str(page_num), wait_until="domcontentloaded", timeout=120000)
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
            except Exception as e:
                print(f"⚠️ Failed to load {current_url}: {e}")
                break

            await accept_cookies(page)
            await extract_files_from_page(page)
            await asyncio.sleep(random.uniform(1, 3))  # Human-like delay
            page_num += 1
            # next_page = await find_next_page(page)
            # if next_page and not stop_scraping:
            #     current_url = next_page
            # else:
            #     break

        if file_links_collected:
            with open(JSON_FILENAME, "w", encoding="utf-8") as f:
                json.dump(file_links_collected, f, indent=4)
            print(f"\n✅ File links saved in: {JSON_FILENAME}")
        else:
            print("\n❌ No file links found.")

        await browser.close()

# Run the scraper
asyncio.run(scrape_sec_filings())

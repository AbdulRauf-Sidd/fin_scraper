import asyncio
import random
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from utils import *

# Argument Parsing
# parser = argparse.ArgumentParser(description="SEC Filings Scraper")
# parser.add_argument("url", type=str, help="SEC Filings page URL")
# parser.add_argument("ticker", type=str, help="Equity ticker symbol")
# parser.add_argument("--output", type=str, default="sec_filings.json", help="Output JSON file name")

# args = parser.parse_args()

# Configurations
SEC_FILINGS_URL = "https://investor.thecampbellscompany.com/news/financial-news"
EQUITY_TICKER = "CPB"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/cpb_news.json"
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

import asyncio
from urllib.parse import urljoin

async def accept_cookies(page):
    """Accepts cookies if a consent banner appears."""
    try:
        cookie_button = await page.query_selector("button:has-text('Accept')")
        if cookie_button:
            await cookie_button.click()
            await asyncio.sleep(2)  # Wait to ensure banner disappears
            print("✅ Accepted cookies.")
    except Exception as e:
        print(f"⚠️ No cookie consent banner found or error clicking it: {e}")

import asyncio

async def load_all_news(page):
    """Clicks the 'Load More' button until all content is loaded."""
    while True:
        try:
            # Find the "Load More" button
            load_more_button = await page.query_selector("a.button.use-ajax[rel='next']")

            # If button is not found, stop
            if not load_more_button:
                print("✅ No 'Load More' button found. Stopping pagination.")
                break

            # Get the button's href to track loading state
            load_more_url = await load_more_button.get_attribute("href")
            if not load_more_url:
                print("✅ No 'Load More' URL found. Stopping pagination.")
                break

            # Click the "Load More" button
            await load_more_button.click()
            print(f"🔄 Clicked 'Load More' button... Waiting for content to load.")

            # Wait until new items appear
            previous_count = len(await page.query_selector_all("article.node--nir-news--nir-widget-list"))
            max_wait_time = 10  # Max time to wait per load
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                await asyncio.sleep(1)
                elapsed_time += 1

                # Get the new count of news items
                current_count = len(await page.query_selector_all("article.node--nir-news--nir-widget-list"))
                if current_count > previous_count:
                    print(f"✅ Loaded {current_count - previous_count} new articles.")
                    break  # Exit waiting loop as new content is loaded

            if elapsed_time >= max_wait_time:
                print("⚠️ Timed out waiting for new content to load.")

        except Exception as e:
            print(f"⚠️ Error clicking 'Load More' button: {e}")
            break

import asyncio
import re
from urllib.parse import urljoin

async def extract_files_from_page(page):
    """Extracts news events from the page while ensuring event dates are 2019 or later."""
    global stop_scraping
    try:
        # First, accept cookies
        await accept_cookies(page)

        # Load all news by clicking 'Load More' button
        await load_all_news(page)

        # Select all event blocks
        event_blocks = await page.query_selector_all("article.node--nir-news--nir-widget-list")

        for event_block in event_blocks:
            try:
                # Extract event date
                date_element = await event_block.query_selector(".nir-widget--news--date-time")
                event_date_text = await date_element.inner_text() if date_element else "UNKNOWN DATE"
                event_date_parsed = await parse_date3(event_date_text)

                if not event_date_parsed:
                    print(f"⚠️ Error parsing date: {event_date_text}")
                    continue

                # Skip events before 2019
                if event_date_parsed.year < 2019:
                    print(f"🛑 Stopping: Found event from {event_date_parsed.year}, no need to continue.")
                    stop_scraping = True
                    return  # Stop processing further events

                # Extract event title and URL
                title_element = await event_block.query_selector(".nir-widget--news--headline a")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"
                event_url = await title_element.get_attribute("href") if title_element else "#"

                # Ensure full URL
                if not event_url.startswith("http"):
                    event_url = urljoin(SEC_FILINGS_URL, event_url)

                # Classify event type
                freq = classify_frequency(event_name, event_url)
                if freq == "periodic":
                    event_type = classify_periodic_type(event_name, event_url)
                    event_name = format_quarter_string(event_date_parsed.strftime("%Y/%m/%d"), event_name)
                else:
                    event_type = categorize_event(event_name)


                category = classify_document(event_name, event_url) 
                file_type = get_file_type(event_url)

                file_name = extract_file_name(event_url)


                category = classify_document(event_name, event_url) 
                file_type = get_file_type(event_url)

                file_name = extract_file_name(event_url)


                category = classify_document(event_name, event_url) 
                file_type = get_file_type(event_url)

                file_name = await extract_file_name(event_url)
                # Store structured event data
                file_links_collected.append({
                    "equity_ticker": "CPB",  # Adjust the ticker if needed
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": event_name.strip(),
                    "event_date": event_date_parsed.strftime("%Y/%m/%d"),
                    "data": [{
                        "file_name": file_name,
                        "file_type": file_type,
                        "date": event_date_parsed.strftime("%Y/%m/%d"),
                        "category": category,
                        "source_url": event_url,
                        "wissen_url": "NULL"
                    }]
                })

                # print(f"✅ Extracted event: {event_name}, Date: {event_date_parsed.strftime('%Y/%m/%d')}")

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

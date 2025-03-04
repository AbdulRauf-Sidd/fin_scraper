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


async def extract_files_from_page(page):
    """Extracts IFF news releases and associated file links."""
    global stop_scraping
    try:
        # Select all articles containing news events
        news_articles = await page.query_selector_all(".nir-widget--list article")

        for article in news_articles:
            try:
                # Extract Event Date
                date_element = await article.query_selector(":scope .nir-widget--news--date-time")
                event_date_text = await date_element.inner_text() if date_element else "UNKNOWN DATE"
                event_date_parsed = await parse_date3(event_date_text)

                if event_date_parsed and event_date_parsed.year < 2019:
                    print(f"🛑 Stopping: Found event from {event_date_parsed.year}, no need to continue.")
                    stop_scraping = True  # Set global flag to stop further processing
                    return  # Stop processing this event

                if not event_date_parsed:
                    print(f"⚠️ Error parsing date: {event_date_text}")
                    continue

                # Extract Event Name and Press Release URL
                headline_element = await article.query_selector(":scope .nir-widget--news--headline a")
                event_name = await headline_element.inner_text() if headline_element else "Unknown Event"
                event_url = await headline_element.get_attribute("href") if headline_element else "Unknown URL"

                # Ensure full URL
                if event_url and not event_url.startswith("http"):
                    event_url = urljoin(SEC_FILINGS_URL, event_url)

                # Collect press release file
                data_files = [{
                    "file_name": event_name.strip(),
                    "file_type": "html",
                    "date": event_date_parsed.strftime("%Y/%m/%d"),
                    "category": "press release",
                    "source_url": event_url,
                    "wissen_url": "unknown"
                }]

                # Classify event frequency and type
                freq = classify_frequency(event_name, event_url)
                event_type = "expansion"
                if freq == "periodic":
                    event_type = classify_periodic_type(event_name, event_url)

                # Append structured event data
                file_links_collected.append({
                    "equity_ticker": "IFF",
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": event_name.strip(),
                    "event_date": event_date_parsed.strftime("%Y/%m/%d"),
                    "data": data_files
                })

                print(f"✅ Extracted event: {event_name}, Date: {event_date_parsed}, URL: {event_url}")

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

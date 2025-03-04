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




import re
from urllib.parse import urljoin
from datetime import datetime

async def extract_files_from_page(page):
    """Extracts investor seminar events from the Croda page."""
    global stop_scraping
    try:
        # Select all seminar event cards
        seminar_cards = await page.query_selector_all("div.card-body")

        if not seminar_cards:
            print("⚠️ No investor seminars found on the page.")
            return

        print(f"\n🔍 Extracting {len(seminar_cards)} investor seminars...")

        for seminar_card in seminar_cards:
            try:
                # Extract event name
                title_element = await seminar_card.query_selector("h3.card-title a")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"

                # Extract event date and description
                date_text_element = await seminar_card.query_selector("div.card-text")
                

                

                # Extract event URL
                event_url = await title_element.get_attribute("href") if title_element else "UNKNOWN URL"

                # Ensure full URL
                if not event_url.startswith("http"):
                    event_url = urljoin(SEC_FILINGS_URL, event_url)

                # Classify event type
                freq = classify_frequency(event_name, event_url)
                event_type = "event"
                if freq == "periodic":
                    event_type = classify_euro_periodic_type(event_name, event_url)

                # Append structured event data
                file_links_collected.append({
                    "equity_ticker": "CRODA",
                    "source_type": "company_information",
                    "frequency": 'non-periodic',
                    "event_type": 'esg',
                    "event_name": event_name.strip(),
                    "event_date": 'null',
                    "data": [{
                        "file_name": "Investor Seminar Details",
                        "file_type": "html",
                        "date": 'null',
                        "category": "html",
                        "source_url": event_url,
                        "wissen_url": "unknown"
                    }]
                })

                
            except Exception as e:
                print(f"⚠️ Error processing an investor seminar: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting investor seminars: {e}")


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

            await accept_cookies(page)
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

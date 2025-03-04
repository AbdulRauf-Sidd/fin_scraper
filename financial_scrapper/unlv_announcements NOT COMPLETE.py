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


async def accept_cookies(page):
    """Accepts cookies if a consent banner appears."""
    try:
        # Find the cookie consent button by its ID
        cookie_button = await page.query_selector("button#onetrust-accept-btn-handler")
        if cookie_button:
            await cookie_button.click()
            await asyncio.sleep(2)  # Wait to ensure banner disappears
            print("✅ Accepted cookies.")
        else:
            print("⚠️ Cookie consent button not found.")
    except Exception as e:
        print(f"⚠️ Error clicking cookie consent button: {e}")


async def enable_stealth(page):
    """Inject JavaScript to evade bot detection."""
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)




async def extract_files_from_page(page):
    """Extracts news events from the page."""
    global stop_scraping
    try:
        # Select all event blocks
        event_blocks = await page.query_selector_all(".RowStyle")
        print(event_blocks)

        for event_block in event_blocks:
            try:
                # Extract event date
                date_element = await event_block.query_selector(".daterow span")
                event_date_text = await date_element.inner_text() if date_element else "UNKNOWN DATE"
                event_date_parsed = await parse_date3(event_date_text)
                
                print('date', event_date_parsed)

                if not event_date_parsed:
                    print(f"⚠️ Error parsing date: {event_date_text}")
                    continue

                # Extract event title and URL
                title_element = await event_block.query_selector(".titlerow a")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"
                event_url = await title_element.get_attribute("href") if title_element else "#"
                
                print('title element', title_element)
                print('event name', event_name)

                # Ensure full URL
                if not event_url.startswith("http"):
                    event_url = urljoin(SEC_FILINGS_URL, event_url)

                # Extract PDF link
                pdf_element = await event_block.query_selector(".pdfrow a")
                pdf_url = await pdf_element.get_attribute("href") if pdf_element else None
                if pdf_url and not pdf_url.startswith("http"):
                    pdf_url = urljoin(SEC_FILINGS_URL, pdf_url)

                # Extract additional data like price change, if available
                price_change_element = await event_block.query_selector(".pricechngerow span")
                price_change = await price_change_element.inner_text() if price_change_element else "N/A"

                # Classify frequency and type
                freq = classify_frequency(event_name, event_url)
                event_type = "expansion"
                if freq == "periodic":
                    event_type = classify_periodic_type(event_name, event_url)

                # Append structured event data
                file_links_collected.append({
                    "equity_ticker": "UNKNOWN_TICKER",  # Replace with the correct ticker if known
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": event_name.strip(),
                    "event_date": event_date_parsed.strftime("%Y/%m/%d"),
                    "data": [{
                        "file_name": pdf_url.split("/")[-1] if pdf_url else "N/A",
                        "file_type": "pdf" if pdf_url else "webpage",
                        "date": event_date_parsed.strftime("%Y/%m/%d"),
                        "category": "financial report",
                        "source_url": pdf_url if pdf_url else event_url,
                        "wissen_url": "unknown"
                    }],
                    "price_change": price_change.strip()
                })

                print(f"✅ Extracted event: {event_name}, Date: {event_date_parsed.strftime('%Y/%m/%d')}")

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


            await asyncio.sleep(2)
            await accept_cookies(page)
            await extract_files_from_page(page)
            await page.reload()

            # Wait for the page to load completely after the reload
            await page.wait_for_load_state("domcontentloaded")
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

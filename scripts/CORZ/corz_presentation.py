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
SEC_FILINGS_URL = "https://investors.corescientific.com/news-events/presentations"
EQUITY_TICKER = "CORZ"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/corz_presentation.json"
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


async def extract_files_from_page(page):
    """Extracts events and associated PDF links from the page."""
    global stop_scraping
    try:
        date_elements = await page.query_selector_all(".date time")
        media_links = await page.query_selector_all(".media-heading a")

        for date_element, media_link in zip(date_elements, media_links):
            event_date = await date_element.get_attribute("datetime")
            event_date_parsed = await parse_date2(event_date)
            if not event_date_parsed:
                print(f"⚠️ Error parsing date: {event_date}")
                continue

            event_name = await media_link.inner_text()
            event_url = await media_link.get_attribute("href")
            
            # Navigate to the event URL
        

            # After navigation, gather the PDF links
            data_files = []
            for pdf_link in [event_url]:

                category = classify_document(event_name, event_url) 
                file_type = get_file_type(event_url)

                file_name = await extract_file_name(event_url)
                

                data_files.append({
                    "file_name": file_name,
                    "file_type": file_type,
                    "date": event_date_parsed.strftime("%Y/%m/%d"),
                    "category": category,
                    "source_url": event_url,
                    "wissen_url": "NULL"
                })

            
            freq = classify_frequency(event_name, str(event_url))
            if freq == "periodic":
                event_type = classify_periodic_type(event_name, str(event_url))
                event_name = format_quarter_string(event_date_parsed.strftime("%Y/%m/%d"), str(event_name))
            else:
                event_type = categorize_event(event_name)

            if data_files:
                file_links_collected.append({
                    "equity_ticker": EQUITY_TICKER,
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": event_name.strip(),
                    "event_date": event_date_parsed.strftime("%Y/%m/%d"),
                    "data": data_files
                })

            # Go back to the main page to continue processing other events
              # Ensure the page is fully loaded after going back

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
                await page.goto(current_url, wait_until="domcontentloaded", timeout=120000)
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

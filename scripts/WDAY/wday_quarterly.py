import asyncio
import random
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from utils import *

# Argument Parsing
# parser = argparse.ArgumentParser(description="SEC Filings Scraper")
# parser.add_argument("url", type=str, help="SEC Filings page URL")
# parser.add_argument("ticker", type=str, help="Equity ticker symbol")
# parser.add_argument("--output", type=str, default="sec_filings.json", help="Output JSON file name")

# args = parser.parse_args()

# Configurations
SEC_FILINGS_URL = "https://investor.workday.com/quarterly-results"
EQUITY_TICKER = "WDAY"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/wday_quaterly.json"
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


from urllib.parse import urljoin

async def extract_files_from_page(page):
    """Extracts Workday fiscal year events and associated file links."""
    global stop_scraping
    try:
        fiscal_categories = await page.query_selector_all(".wd_category")

        for fiscal_category in fiscal_categories:
            try:
                # Extract Fiscal Year from header
                header_element = await fiscal_category.query_selector(":scope .category_header")
                fiscal_year_text = await header_element.inner_text() if header_element else "Unknown Fiscal Year"
                
                quarter_items = await fiscal_category.query_selector_all(":scope .item")

                for quarter_item in quarter_items:
                    try:
                        # Extract quarter name (e.g., "Q4")
                        quarter_element = await quarter_item.query_selector(":scope .item_name")
                        quarter_name = await quarter_element.inner_text() if quarter_element else "Unknown Quarter"

                        # Extract Event Name
                        event_description = await quarter_item.inner_text()
                        event_name = f"{quarter_name} {fiscal_year_text}"

                        # Extract Event Date
                        event_date = fiscal_year_text.strip()
                        formatted_event_name = utils.format_quarter_string(event_date, event_name)

                        # Extract Press Release URL
                        press_release_link = await quarter_item.query_selector(":scope a[href*='workday.com']")
                        press_release_url = await press_release_link.get_attribute("href") if press_release_link else None

                        try:
                            year = int(fiscal_year_text[-5:])
                            if year < 2019:
                                stop_scraping = True
                                return None  # Stop pagination
                        except:
                            print("⚠️ Error converting year")

                        # Extract all related PDFs
                        data_files = []
                        pdf_links = await quarter_item.query_selector_all(":scope a[href$='.pdf']")

                        for pdf_link in pdf_links:
                            file_url = await pdf_link.get_attribute("href")
                            file_name = await pdf_link.inner_text()

                            if file_url:
                                # Extract File Type & Category
                                file_type = utils.get_file_type(file_url)
                                category = utils.classify_document(event_name, file_url)

                                data_files.append({
                                    "file_name": file_name.strip(),
                                    "file_type": file_type,
                                    "date": event_date,
                                    "category": category,
                                    "source_url": file_url.strip(),
                                    "wissen_url": "NULL"
                                })

                        # 🔹 Classify Frequency & Event Type
                        freq = utils.classify_frequency(event_name, SEC_FILINGS_URL)
                        if freq == "periodic":
                            event_type = utils.classify_periodic_type(event_name, SEC_FILINGS_URL)
                        else:
                            event_type = utils.categorize_event(event_name)

                        # Append structured event data
                        file_links_collected.append({
                            "equity_ticker": EQUITY_TICKER,
                            "source_type": "company_information",
                            "frequency": freq,
                            "event_type": event_type,
                            "event_name": formatted_event_name,
                            "event_date": event_date,
                            "data": data_files
                        })

                        print(f"✅ Extracted event: {event_name}, Fiscal Year: {fiscal_year_text}, Files: {len(data_files)}")

                    except Exception as e:
                        print(f"⚠️ Error processing quarter event: {e}")

            except Exception as e:
                print(f"⚠️ Error processing fiscal category: {e}")

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

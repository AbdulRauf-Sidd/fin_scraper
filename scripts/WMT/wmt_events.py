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
SEC_FILINGS_URL = "https://corporate.walmart.com/news/events"
EQUITY_TICKER = "WMT"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/wmt_events.json"
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

async def extract_events_from_page(page):
    """Extracts event names, dates, and links from the paginated event list, storing data in the expected JSON structure."""
    global stop_scraping
    try:
        # Load all paginated events by clicking "Load More" repeatedly
        while True:
            try:
                load_more_button = await page.query_selector("#ListEvents-loadmore")
                if load_more_button:
                    print("🔄 Clicking 'Load More' button to load more events...")
                    await load_more_button.click()
                    await page.wait_for_timeout(2000)  # Allow time for events to load
                else:
                    break  # No more pages to load
            except Exception as e:
                print(f"⚠️ Error clicking 'Load More': {e}")
                break

        # Extract all event items
        await page.wait_for_selector("#archiveEvents .ListEvents-items-item")
        event_items = await page.query_selector_all("#archiveEvents .ListEvents-items-item")

        for event in event_items:
            try:
                # Extract event name
                title_element = await event.query_selector(":scope .CorporateEvent-item-title a")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"

                # Extract event date
                date_element = await event.query_selector(":scope .CorporateEvent-item-date span")
                event_date_text = await date_element.inner_text() if date_element else "UNKNOWN DATE"
                event_date_parsed = await utils.parse_date3(event_date_text)

                if not event_date_parsed:
                    print(f"⚠️ Error parsing date: {event_date_text}")
                    continue
                formatted_date = event_date_parsed.strftime("%Y/%m/%d")

                # Extract event URL
                link_element = await event.query_selector(":scope .CorporateEvent-item-info a")
                event_url = await link_element.get_attribute("href") if link_element else "UNKNOWN URL"

                # Ensure full URL
                base_url = "https://corporate.walmart.com"  # Base domain for Walmart
                full_event_url = f"{base_url}{event_url}" if event_url.startswith("/") else event_url

                # Classify event properties
                freq = utils.classify_frequency(event_name, full_event_url)
                if freq == "periodic":
                    event_type = utils.classify_periodic_type(event_name, full_event_url)
                    event_name = utils.format_quarter_string(formatted_date, event_name)
                else:
                    event_type = utils.categorize_event(event_name)

                category = utils.classify_document(event_name, full_event_url)
                file_type = utils.get_file_type(full_event_url)
                file_name = await utils.extract_file_name(full_event_url)

                # Append structured event data
                file_links_collected.append({
                    "equity_ticker": EQUITY_TICKER,
                    "source_type": "company_news",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": event_name.strip(),
                    "event_date": formatted_date,
                    "data": [
                        {
                            "file_name": file_name,
                            "file_type": file_type,
                            "date": formatted_date,
                            "category": category,
                            "source_url": full_event_url,
                            "wissen_url": "unknown"
                        }
                    ],
                })

                print(f"✅ Extracted: {event_name}, Date: {formatted_date}, Category: {category}")

            except Exception as e:
                print(f"⚠️ Error processing an event: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting events: {e}")


async def scrape_all_years(page):
    """Clicks on each year filter (from 2024 to 2020) and extracts data."""
    years_to_scrape = ["2024", "2023", "2022", "2021", "2020", "2019"]

    for year in years_to_scrape:
        try:
            print(f"\n🔄 Clicking year filter: {year}")

            # Find and click the year filter button
            year_button = await page.query_selector(f".tab-titles a[href*='year={year}']")
            if year_button:
                await year_button.click()
                await asyncio.sleep(3)  # Wait for data to load
            else:
                print(f"⚠️ Year filter '{year}' not found. Skipping.")
                continue

            # Extract reports for the selected year
            await extract_events_from_page(page)

        except Exception as e:
            print(f"⚠️ Error switching to year {year}: {e}")


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
        while current_url and isinstance(current_url, str) and not stop_scraping:
            visited_urls.add(current_url)
            print(f"\n🔍 Visiting: {current_url}")
            try:
                await page.goto(current_url, wait_until="domcontentloaded", timeout=120000)
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
            except Exception as e:
                print(f"⚠️ Failed to load {current_url}: {e}")
                break

            await accept_cookies(page)
            await extract_events_from_page(page)
            await scrape_all_years(page)
            await asyncio.sleep(random.uniform(1, 3))  # Human-like delay

            next_page = await find_next_page(page)
            if next_page and isinstance(next_page, str):  # Ensure next_page is a valid URL
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

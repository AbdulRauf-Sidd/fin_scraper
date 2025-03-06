import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from scripts.UTILS import utils

# Configurations
SEC_FILINGS_URL = "https://www.unilever.com/news/press-and-media/press-releases/"
EQUITY_TICKER = "UNLV"
JSON_FILENAME = "JSONS/unlv_press.json"
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


async def accept_cookies(page):
    """Accepts cookies if a consent banner appears."""
    try:
        cookie_button = await page.query_selector("button:has-text('Accept')")
        if cookie_button:
            await cookie_button.click()
            await asyncio.sleep(2)
            print("✅ Accepted cookies.")
    except Exception as e:
        print(f"⚠️ No cookie consent banner found or error clicking it: {e}")


async def extract_files_from_page(page):
    """Extracts press release events and associated file links."""
    global stop_scraping
    try:
        await page.wait_for_selector(".uol-c-card__content", timeout=10000)  # ✅ Ensure elements are loaded
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")  # ✅ Force lazy loading
        await asyncio.sleep(3)  # ✅ Give time for JS to load elements

        event_blocks = await page.query_selector_all(".uol-c-card__content")
        print(f"🔍 Found {len(event_blocks)} event blocks.")  # ✅ Debugging log

        if len(event_blocks) == 0:
            print("⚠️ No event blocks detected. The page structure may have changed.")
            return

        for event in event_blocks:
            try:
                # Extract event name
                title_element = await event.query_selector(".uol-c-card__title a")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"
                event_url = await title_element.get_attribute("href") if title_element else "Unknown URL"

                print(f"📝 Event: {event_name} | URL: {event_url}")

                # Extract event date
                date_element = await event.query_selector("p.uol-c-card__eyebrow time")
                event_date_text = await date_element.get_attribute("datetime") if date_element else None
                event_date_parsed = await utils.parse_date3(event_date_text) if event_date_text else None
                event_date_str = event_date_parsed.strftime("%Y/%m/%d") if isinstance(event_date_parsed, datetime) else "UNKNOWN DATE"

                if event_date_parsed and event_date_parsed.year < 2019:
                    print(f"🛑 Stopping: Found event from {event_date_parsed.year}, no need to continue.")
                    stop_scraping = True
                    return  # Stop processing further events

                # Extract file links
                file_links = []
                file_elements = await event.query_selector_all("a.uol-c-card__title-link")

                for file_element in file_elements:
                    file_url = await file_element.get_attribute("href")
                    file_name = await file_element.inner_text()

                    if file_url:
                        file_url = urljoin(SEC_FILINGS_URL, file_url)  # Ensure absolute URL
                        file_name = file_name.strip() if file_name else "Unknown File"
                        
                        # ✅ Extract file type & category properly
                        file_type = utils.get_file_type(file_url)
                        category = utils.classify_document(event_name, file_url)

                        file_links.append({
                            "file_name": file_name,
                            "file_type": file_type,
                            "date": event_date_str,
                            "category": category,
                            "source_url": file_url,
                            "wissen_url": "unknown"
                        })

                if not file_links:
                    print(f"⚠️ No files found for event: {event_name}")

                # Classify event frequency and type
                freq = utils.classify_frequency(event_name, event_url)
                event_type = utils.classify_periodic_type(event_name, event_url) if freq == "periodic" else utils.categorize_event(event_name)

                formatted_event_name = utils.format_quarter_string(event_date_str, event_name)

                # Store extracted data
                file_links_collected.append({
                    "equity_ticker": EQUITY_TICKER,
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": formatted_event_name,
                    "event_date": event_date_str,
                    "data": file_links
                })

                print(f"✅ Extracted event: {formatted_event_name}, Date: {event_date_str}, Files: {len(file_links)}")

            except Exception as e:
                print(f"⚠️ Error processing an event: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting events: {e}")


async def extract_all_unilever_pages(page):
    """Loops through Unilever press release pages and extracts data."""
    base_url = "https://www.unilever.com/news/press-and-media/press-releases/"

    try:
        for page_number in range(2, 15):  # Pages 2 to 14
            current_url = f"{base_url}{page_number}/"

            print(f"➡️ Navigating to: {current_url}")
            await page.goto(current_url, timeout=10000)
            await page.wait_for_load_state("domcontentloaded")

            # Extract data from the current page
            await extract_files_from_page(page)

            await asyncio.sleep(2)

    except Exception as e:
        print(f"⚠️ Error during pagination: {e}")


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
        visited_urls.add(current_url)

        print(f"\n🔍 Visiting: {current_url}")
        try:
            await page.goto(current_url, wait_until="domcontentloaded", timeout=120000)
            await accept_cookies(page)
            await extract_all_unilever_pages(page)
        except Exception as e:
            print(f"⚠️ Failed to load {current_url}: {e}")

        if file_links_collected:
            with open(JSON_FILENAME, "w", encoding="utf-8") as f:
                json.dump(file_links_collected, f, indent=4)
            print(f"\n✅ File links saved in: {JSON_FILENAME}")
        else:
            print("\n❌ No file links found.")

        await browser.close()


# Run the scraper
asyncio.run(scrape_sec_filings())

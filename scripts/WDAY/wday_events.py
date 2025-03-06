import asyncio
import random
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from utils import *

# Configurations
SEC_FILINGS_URL = "https://investor.workday.com/events#past:2025:3"
EQUITY_TICKER = "WDAY"
JSON_FILENAME = "JSONS/wday_events.json"
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


async def load_all_events(page):
    """Clicks 'Load More Events' button until it no longer appears."""
    while True:
        try:
            load_more_button = await page.query_selector(".wd_events_more")

            if not load_more_button:
                print("✅ No more 'Load More Events' button. All records loaded.")
                break  # Exit loop

            print("🔄 Clicking 'Load More Events' button...")
            await load_more_button.click()
            await asyncio.sleep(5)  # Adjust delay if needed

        except Exception as e:
            print(f"⚠️ Error clicking 'Load More Events' button: {e}")
            break


async def extract_files_from_page(page):
    """Extracts Workday event details and associated file links."""
    global stop_scraping
    try:
        await load_all_events(page)
        event_items = await page.query_selector_all(".wd_event_info")

        for event in event_items:
            try:
                # Extract event name
                title_element = await event.query_selector(":scope .wd_title")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"

                # Extract event date
                date_element = await event.query_selector(":scope .wd_event_date")
                event_date_text = await date_element.inner_text() if date_element else "UNKNOWN DATE"

                # ✅ Ensure proper date parsing & conversion to string
                event_date_parsed = await utils.parse_date3(event_date_text)
                event_date_str = event_date_parsed.strftime("%Y/%m/%d") if isinstance(event_date_parsed, datetime) else event_date_parsed

                if not event_date_str:
                    print(f"⚠️ Error parsing date: {event_date_text}")
                    continue

                # Collect all related files
                data_files = []

                # Extract webcast links
                webcast_links = await event.query_selector_all(":scope .wd_event_webcast a")
                for webcast in webcast_links:
                    file_url = await webcast.get_attribute("href")
                    file_name = await webcast.inner_text()

                    if file_url:
                        data_files.append({
                            "file_name": file_name.strip(),
                            "file_type": "webcast",
                            "date": event_date_str,
                            "category": "webcast",
                            "source_url": file_url.strip(),
                            "wissen_url": "unknown"
                        })

                # Extract additional links from wd_summary
                summary_section = await event.query_selector(".wd_summary")
                if summary_section:
                    summary_links = await summary_section.query_selector_all("a")

                    for link in summary_links:
                        file_url = await link.get_attribute("href")
                        file_name = await link.inner_text()

                        # ✅ Ensure file name extraction is awaited
                        extracted_file_name = await utils.extract_file_name(file_url)

                        # ✅ Ensure file type & category are properly extracted
                        file_type = utils.get_file_type(file_url)
                        category = utils.classify_document(file_name, file_url)

                        if file_url:
                            data_files.append({
                                "file_name": extracted_file_name.strip(),
                                "file_type": file_type,
                                "date": event_date_str,
                                "category": category,
                                "source_url": file_url.strip(),
                                "wissen_url": "NULL"
                            })

                # Classify event frequency and type
                freq = utils.classify_frequency(event_name, "")
                if freq == "periodic":
                    event_type = utils.classify_periodic_type(event_name, "")
                else:
                    event_type = utils.categorize_event(event_name)

                # ✅ Format event name properly
                event_name2 = utils.format_quarter_string(event_date_str, event_name)

                # Append structured event data
                file_links_collected.append({
                    "equity_ticker": EQUITY_TICKER,
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": event_name2,
                    "event_date": event_date_str,
                    "data": data_files
                })

                print(f"✅ Extracted event: {event_name}, Date: {event_date_str}, Files: {len(data_files)}")

            except Exception as e:
                print(f"⚠️ Error processing an event: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting files: {e}")


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
        max_retries = 5  # 🛑 Prevent infinite reloading
        retries = 0

        while current_url and not stop_scraping and retries < max_retries:
            visited_urls.add(current_url)
            print(f"\n🔍 Visiting: {current_url}")

            try:
                await page.goto(current_url, wait_until="domcontentloaded", timeout=120000)
                await extract_files_from_page(page)

                # ⏩ Update current_url if needed (for pagination)
                next_page_url = await find_next_page(page)
                if next_page_url:
                    current_url = next_page_url
                else:
                    break  # ✅ Stop loop if no next page.

            except Exception as e:
                print(f"⚠️ Failed to load {current_url}: {e}")
                retries += 1
                if retries >= max_retries:
                    print("🛑 Stopping: Max retries reached.")
                    break  # ✅ Stop loop if retries exceeded.

        # ✅ Ensure JSON serialization does not fail
        for event in file_links_collected:
            event["event_date"] = str(event["event_date"])
            for file in event["data"]:
                file["date"] = str(file["date"])

        if file_links_collected:
            with open(JSON_FILENAME, "w", encoding="utf-8") as f:
                json.dump(file_links_collected, f, indent=4)
            print(f"\n✅ File links saved in: {JSON_FILENAME}")
        else:
            print("\n❌ No file links found.")

        await browser.close()


# Run the scraper
asyncio.run(scrape_sec_filings())

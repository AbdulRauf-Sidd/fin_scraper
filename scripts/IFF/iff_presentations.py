import asyncio
import random
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))
from scripts.UTILS import utils

# Configurations
SEC_FILINGS_URL = "https://ir.iff.com/events-presentations"
EQUITY_TICKER = "IFF"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/iff_presentations.json"
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


import re
from urllib.parse import urljoin

async def extract_files_from_page(page):
    """Extracts IFF earnings events, conference calls, and related file links."""
    global stop_scraping
    try:
        # Select all event articles
        event_articles = await page.query_selector_all(".node--nir-event--nir-widget-list")

        for article in event_articles:
            if stop_scraping:
                return  # Stop processing further events if flagged

            try:
                # Extract Event Date
                date_element = await article.query_selector(":scope .press-date")
                event_date_text = await date_element.inner_text() if date_element else "UNKNOWN DATE"
                event_date_parsed = await parse_date3(event_date_text)

                if event_date_parsed and event_date_parsed.year < 2019:
                    print(f"🛑 Stopping: Found event from {event_date_parsed.year}, stopping scraper.")
                    stop_scraping = True  # Stop further processing
                    return  # Exit function immediately

                # Extract Event Name and URL
                title_element = await article.query_selector(":scope .field-nir-event-title a")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"
                event_url = await title_element.get_attribute("href") if title_element else "Unknown URL"

                # Ensure full event URL
                if event_url and not event_url.startswith("http"):
                    event_url = urljoin(SEC_FILINGS_URL, event_url)

                # Collect related files
                data_files = []

                # Extract webcast links
                webcast_element = await article.query_selector(":scope .field-nir-event-url a")
                if webcast_element:
                    webcast_url = await webcast_element.get_attribute("href")
                    webcast_name = await webcast_element.inner_text()

                    data_files.append({
                        "file_name": webcast_name.strip(),
                        "file_type": "webcast",
                        "date": event_date_parsed.strftime("%Y/%m/%d"),
                        "category": "webcast",
                        "source_url": webcast_url.strip(),
                        "wissen_url": "unknown"
                    })

                # Extract PDF documents
                pdf_links = await article.query_selector_all(":scope .field-nir-event-assets-ref a")
                for pdf_link in pdf_links:
                    file_url = await pdf_link.get_attribute("href")
                    file_name = await pdf_link.inner_text()

                    if file_url:
                        data_files.append({
                            "file_name": file_name.strip(),
                            "file_type": "pdf",
                            "date": event_date_parsed.strftime("%Y/%m/%d"),
                            "category": "presentation" if "presentation" in file_name.lower() else "report",
                            "source_url": urljoin(SEC_FILINGS_URL, file_url),
                            "wissen_url": "unknown"
                        })

                # Classify event type
                freq = classify_frequency(event_name, event_url)
                event_type = "expansion"
                if freq == "periodic":
                    event_type = classify_periodic_type(event_name, event_url)

                # Append structured event data
                file_links_collected.append({
                    "equity_ticker": "IFF",
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": "presentation",
                    "event_name": event_name.strip(),
                    "event_date": event_date_parsed.strftime("%Y/%m/%d"),
                    "data": data_files
                })

                print(f"✅ Extracted event: {event_name}, Date: {event_date_parsed}, Files: {len(data_files)}")

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

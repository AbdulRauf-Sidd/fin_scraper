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
SEC_FILINGS_URL = "https://investors.dsm-firmenich.com/en/investors/historical-information/results-presentations.html"
EQUITY_TICKER = "DSFIR"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/dsfir_press.json"
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


async def extract_files_from_page(page):
    """Extracts investor results from the DSM-Firmenich page."""
    global stop_scraping
    try:
        # Select all event-related elements in order
        event_blocks = await page.query_selector_all(".cmp-title, .cmp-text, .cmp-image")

        event_data = []
        event_name, event_date = None, None
        file_links = []

        for block in event_blocks:
            # Extract event name (New event starts)
            title_element = await block.query_selector(".cmp-title__text")
            if title_element:
                # If a previous event was collected, store it before moving to the new one
                if event_name and file_links:
                    file_links_collected.append({
                        "equity_ticker": "DSFIR",
                        "source_type": "company_information",
                        "frequency": classify_frequency(event_name, file_links[0]["source_url"]),
                        "event_type": "press release",
                        "event_name": event_name.strip(),
                        "event_date": event_date if event_date else "null",
                        "data": file_links
                    })
                    print(f"✅ Extracted event: {event_name}, Date: {event_date}")

                # Start new event
                event_name = await title_element.inner_text()
                event_date = None
                file_links = []
                continue

            # Extract event date
            date_element = await block.query_selector(".cmp-text p b") or await block.query_selector(".cmp-text b") or await block.query_selector(".cmp-text")
            if date_element:
                event_date_text = await date_element.inner_text()
                event_date_parsed = await parse_date3(event_date_text)
                if event_date_parsed:
                    event_date = event_date_parsed.strftime("%Y/%m/%d")
                else:
                    print(f"⚠️ Error parsing date: {event_date_text}")
            else:
                print(f"⚠️ No date found in block: {await block.inner_html()}")
            if date_element:
                event_date_text = await date_element.inner_text()
                print(event_date_text)
                event_date_parsed = await parse_date3(event_date_text)
                if event_date_parsed:
                    event_date = event_date_parsed.strftime("%Y/%m/%d")
                continue

            # Extract file links
            link_element = await block.query_selector(".cmp-image__link")
            if link_element:
                file_url = await link_element.get_attribute("href")
                if file_url:
                    if not file_url.startswith("http"):
                        file_url = urljoin(SEC_FILINGS_URL, file_url)
                    category = classify_document(event_name, file_url) 
                    file_type = get_file_type(file_url)
                    file_links.append({
                        "file_name": file_url.split("/")[-1],
                        "file_type": file_type,
                        "date": event_date if event_date else "NULL",
                        "category": category,
                        "source_url": file_url,
                        "wissen_url": "NULL"
                    })

        # Store the last event if it has files
        if event_name and file_links:
            file_links_collected.append({
                "equity_ticker": "DSFIR",
                "source_type": "company_information",
                "frequency": classify_frequency(event_name, file_links[0]["source_url"]),
                "event_type": 'press release',
                "event_name": event_name.strip(),
                "event_date": event_date if event_date else "NULL",
                "data": file_links
            })
            print(f"✅ Extracted event: {event_name}, Date: {event_date}")

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
            await extract_files_from_page(page)

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
        while current_url and current_url and not stop_scraping:
            visited_urls.add(current_url)
            print(f"\n🔍 Visiting: {current_url}")
            try:
                await page.goto(current_url, wait_until="domcontentloaded", timeout=120000)
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
            except Exception as e:
                print(f"⚠️ Failed to load {current_url}: {e}")
                break

            await accept_cookies(page)
            await extract_files_from_page(page)
            # await scrape_all_years(page)
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

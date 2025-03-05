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
# parser = argparse.ArgumentParser(description="SEC Filings Scraper")
# parser.add_argument("url", type=str, help="SEC Filings page URL")
# parser.add_argument("ticker", type=str, help="Equity ticker symbol")
# parser.add_argument("--output", type=str, default="sec_filings.json", help="Output JSON file name")

# args = parser.parse_args()

# Configurations
SEC_FILINGS_URL = "https://www.unilever.com/news/press-and-media/press-releases/"
EQUITY_TICKER = "UNLV"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/unlv_press.json"
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


import re
from urllib.parse import urljoin

async def extract_files_from_page(page):
    """Extracts investor events from the provided page structure."""
    global stop_scraping
    try:
        # Select all event blocks
        event_blocks = await page.query_selector_all(".uol-c-card__content")

        for event in event_blocks:
            try:
                # Extract event name
                title_element = await event.query_selector(".uol-c-card__title")
                event_name = await title_element.inner_text() if title_element else "Unknown Event"

                # Extract event date
                date_element = await event.query_selector("p.uol-c-card__eyebrow time")
                event_date_text = await date_element.get_attribute("datetime") if date_element else None
                event_date_parsed = await parse_date3(event_date_text) if event_date_text else None
                event_date = event_date_parsed.strftime("%Y/%m/%d") if event_date_parsed else "UNKNOWN DATE"

                if event_date_parsed and event_date_parsed.year < 2019:
                    print(f"🛑 Stopping: Found event from {event_date_parsed.year}, no need to continue.")
                    stop_scraping = True
                    return  # Stop processing further events

                # Extract file links
                file_links = []
                file_elements = await event.query_selector_all(".uol-c-link.uol-c-card__title-link")

                print(file_elements)

                for file_element in file_elements:
                    file_url = await file_element.get_attribute("href")
                    if not file_url:
                        continue

                    # Resolve relative URLs
                    if not file_url.startswith("http"):
                        file_url = urljoin(SEC_FILINGS_URL, file_url)

                    # Determine file type
                    file_type = "pdf" if file_url.endswith(".pdf") else "video" if "youtube.com" in file_url else "html"

                    file_links.append({
                        "file_name": file_url.split("/")[-1],
                        "file_type": file_type,
                        "date": event_date,
                        "category": "financial report",
                        "source_url": file_url,
                        "wissen_url": "unknown"
                    })

                # Store the extracted event
                file_links_collected.append({
                    "equity_ticker": "UNKNOWN",  # Update with actual ticker
                    "source_type": "company_information",
                    "frequency": classify_frequency(event_name, file_links[0]["source_url"]) if file_links else "UNKNOWN",
                    "event_type": "press release",
                    "event_name": event_name.strip(),
                    "event_date": event_date,
                    "data": file_links
                })

                print(f"✅ Extracted event: {event_name}, Date: {event_date}, Files: {len(file_links)}")

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


from urllib.parse import urljoin

async def extract_all_unilever_pages(page):
    """Loops through Unilever press release pages from 2 to 14 and extracts data."""
    base_url = "https://www.unilever.com/news/press-and-media/press-releases/"

    try:
        for page_number in range(2, 15):  # Pages 2 to 14
            current_url = f"{base_url}{page_number}/"

            print(f"➡️ Navigating to: {current_url}")
            await page.goto(current_url, timeout=10000)
            await page.wait_for_load_state("domcontentloaded")

            # Extract data from the current page
            await extract_files_from_page(page)

            # Sleep to prevent rate-limiting
            await asyncio.sleep(2)

    except Exception as e:
        print(f"⚠️ Error during pagination: {e}")


async def go_to_next_page(page):
    """Navigates to the next page by selecting the first available <a> after the active page element."""
    try:
        await page.wait_for_timeout(2000)  # Small wait to ensure pagination loads

        # Locate the currently active page element
        current_page_element = await page.query_selector("span.ush-c-results-pagination__pager-current")
        if not current_page_element:
            print("⚠️ Could not find the current page indicator. Stopping pagination.")
            return False  # No valid pagination state found

        # Get all pagination links
        pagination_links = await page.query_selector_all("a.uol-c-link.ush-c-results-pagination__pager-link")
        
        found_next_page = False
        next_page_url = None

        for link in pagination_links:
            # Check if this link appears after the current page element
            is_after_current_page = await page.evaluate(
                """(current, link) => current.compareDocumentPosition(link) === 4""",
                current_page_element, link
            )

            if is_after_current_page:
                next_page_url = await link.get_attribute("href")
                found_next_page = True
                break  # Stop at the first valid next page link

        if found_next_page and next_page_url:
            full_next_page_url = urljoin("https://www.unilever.com/news/press-and-media/press-releases/", next_page_url)
            print(f"🔄 Moving to next page: {full_next_page_url}")

            # Navigate to the next page
            await page.goto(full_next_page_url)
            await page.wait_for_load_state("domcontentloaded")
            return True  # Successfully moved to the next page

        print("✅ No more valid next pages.")
        return False  # No more pages left

    except Exception as e:
        print(f"⚠️ Error navigating to next page: {e}")
        return False


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
                await page.goto(current_url, wait_until="load", timeout=1020000)
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
            except Exception as e:
                print(f"⚠️ Failed to load {current_url}: {e}")
                break

            await asyncio.sleep(2)
            
            await accept_cookies(page)
            # await extract_files_from_page(page)
            # next_page = await go_to_next_page(page)
            # # button = await page.query_selector("span.ush-c-results-pagination__pager-current")
            # # if button:
            # #     await button.scroll_into_view_if_needed()
            # #     await button.click(force=True)
            # #     await page.wait_for_timeout(2000)  # Small delay to allow changes
            # #     # await page.reload()  # Force reload of the page
            # #     await enable_stealth(page)
            # # await asyncio.sleep(2)
            # # await extract_files_from_page(page)
            # # # await scrape_all_years(page)
            # # await asyncio.sleep(random.uniform(1, 3))  # Human-like delay
            await extract_all_unilever_pages(page)
            next_page = None
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

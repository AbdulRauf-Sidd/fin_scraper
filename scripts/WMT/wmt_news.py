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
SEC_FILINGS_URL = "https://corporate.walmart.com/content/corporate/en_us/news.tag=corporate:finance.html"
EQUITY_TICKER = "WMT"  # Convert to uppercase for standardization
JSON_FILENAME = "JSONS/wmt_news.json"
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


import asyncio
from urllib.parse import urljoin

import asyncio
from urllib.parse import urljoin

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

import asyncio

async def load_all_news(page):
    """Clicks the 'Load More' button until it disappears."""
    while True:
        try:
            # Find the load more button and its parent div
            load_more_parent = await page.query_selector("div.load-more-news")
            load_more_button = await page.query_selector("div.load-more-news button")

            # If no button is found, stop
            if not load_more_button or not load_more_parent:
                print("✅ No 'Load More' button found. Stopping pagination.")
                break

            # Check if the parent div has class "hide" (indicating button is disabled)
            parent_class = await load_more_parent.get_attribute("class")
            if "hide" in parent_class:
                print("✅ 'Load More' button is hidden. Stopping pagination.")
                break

            # Click the button and wait for content to load
            await load_more_button.click()
            print("🔄 Clicked 'Load More' button...")
            await asyncio.sleep(2)  # Small delay to allow content to load

        except Exception as e:
            print(f"⚠️ Error clicking 'Load More' button: {e}")
            break


async def extract_files_from_page(page):
    """Extracts Walmart news events from 2025 to 2019 while ensuring each card has a valid date and processes all pages."""
    global stop_scraping
    try:
        await accept_cookies(page)  # Accept cookies at the start

        current_year = 2025  # Start at 2025
        min_year = 2019  # Stop at 2019

        while current_year >= min_year:
            print(f"\n🔍 Extracting news for {current_year}...")

            has_more_pages = True
            while has_more_pages:  # Loop through all pages of the current year
                await load_all_news(page)  # Load more news if needed

                # Select all news event cards for the current page
                event_cards = await page.query_selector_all("li.in-page__card.search-result-tag")

                valid_events = []
                for event_card in event_cards:
                    # Extract event date
                    date_element = await event_card.query_selector("p.in-page__date")
                    event_date = await date_element.inner_text() if date_element else None

                    if event_date:
                        event_date_parsed = await parse_date3(event_date)
                        if event_date_parsed:
                            event_year = event_date_parsed.year
                            if event_year < min_year:
                                print("✅ Reached 2019. Stopping extraction.")
                                return  # Stop processing if we hit 2019

                            valid_events.append((event_card, event_date_parsed.strftime("%Y/%m/%d")))

                if not valid_events and not has_more_pages:
                    print(f"⚠️ No valid events found for {current_year}. Moving to {current_year - 1}...")
                    current_year -= 1
                    break  # Exit inner loop to move to the previous year

                print(f"📌 Found {len(valid_events)} valid news events for {current_year} on this page.")

                for event_card, formatted_date in valid_events:
                    try:
                        # Extract event title and URL
                        title_element = await event_card.query_selector("p.in-page__title")
                        event_name = await title_element.inner_text() if title_element else "Unknown Event"
                        event_url_element = await event_card.query_selector("a")
                        event_url = await event_url_element.get_attribute("href") if event_url_element else "#"

                        # Ensure full URL
                        if not event_url.startswith("http"):
                            event_url = urljoin(SEC_FILINGS_URL, event_url)

                        # Extract category
                        category_element = await event_card.query_selector("p.in-page__topic-tag")
                        category = await category_element.inner_text() if category_element else "Uncategorized"

                        # Extract additional event text (description)
                        description_element = await event_card.query_selector("p.in-page__description")
                        additional_text = await description_element.inner_text() if description_element else ""

                        # Classify event type
                        freq = utils.classify_frequency(event_name, event_url)
                        if freq == "periodic":
                            event_type = utils.classify_periodic_type(event_name, event_url)
                            event_name = utils.format_quarter_string(event_date_parsed.strftime("%Y/%m/%d"), event_name)
                        else:
                            event_type = utils.categorize_event(event_name)

                        category = utils.classify_document(event_name, event_url) 
                        file_type = utils.get_file_type(event_url)

                        file_name = await utils.extract_file_name(event_url)

                        category = utils.classify_document(event_name, event_url) 
                        file_type = utils.get_file_type(event_url)


                        # Append structured event data
                        file_links_collected.append({
                            "equity_ticker": "WMT",
                            "source_type": "company_news",
                            "frequency": freq,
                            "event_type": event_type,
                            "event_name": event_name.strip(),
                            "event_date": formatted_date,
                            "data": [{
                                "file_name": file_name,
                                "file_type": file_type,
                                "date": formatted_date,
                                "category": category,
                                "source_url": event_url,
                                "wissen_url": "unknown"
                            }],
                            "additional_text": additional_text.strip()
                        })

                        print(f"✅ Extracted: {event_name}, Date: {formatted_date}, Category: {category}")

                    except Exception as e:
                        print(f"⚠️ Error processing an event: {e}")

                # Try to go to the next page
                has_more_pages = await find_next_page(page)

            # Move to the previous year's page after finishing all pages of the current year
            current_year -= 1

    except Exception as e:
        print(f"⚠️ Error extracting news events: {e}")


async def find_next_page(page):
    """Finds and navigates to the next page if pagination exists and ensures stability before clicking."""
    try:
        # Wait for pagination button to appear
        await page.wait_for_selector(".search-page-arrow.search-page-higher.js-load-more.active", timeout=5000)

        for _ in range(3):  # Retry up to 3 times if it detaches
            try:
                # Select the button fresh each time to avoid stale ElementHandle issues
                next_button = await page.query_selector(".search-page-arrow.search-page-higher.js-load-more.active")
                if not next_button:
                    print("✅ No more pages. Moving to the previous year.")
                    return None  # No more pages

                print("🔄 Moving to next page...")
                await next_button.click()
                await page.wait_for_load_state("domcontentloaded")
                return await page.url()  # Return the updated page URL

            except Exception as e:
                print(f"⚠️ Retrying page navigation due to error: {e}")
                await page.wait_for_timeout(1000)  # Small delay before retrying

        print("❌ Failed to click 'Next'. Moving to the previous year.")
        return False  # If all retries fail, move to the previous year

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
                await page.goto(current_url, wait_until="load", timeout=120000)
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
            except Exception as e:
                print(f"⚠️ Failed to load {current_url}: {e}")
                break

            await extract_files_from_page(page)
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

import asyncio
import json
import re
import random
from datetime import datetime
from urllib.parse import urljoin
from playwright.async_api import async_playwright

# Configurations
BASE_URL = "https://investor.pinterestinc.com/news-and-events/events-and-presentations/default.aspx"
EQUITY_TICKER = "PINS"
OUTPUT_FILE = "JSONS/pinterest_events-and-presentations.json"

# Track visited pages
visited_urls = set()
events_collected = []
stop_scraping = False


async def enable_stealth(page):
    """Inject JavaScript to evade bot detection."""
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)


async def parse_date(date_str):
    """Parse various date formats and return a standardized date."""
    date_str = date_str.strip()
    formats = [
        "%b %d, %Y",  # Example: Feb 28, 2025
        "%B %d, %Y",  # Example: April 28, 2025
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    print(f"⚠️ Error parsing date: {date_str}")
    return None


async def extract_events_from_page(page):
    """Extracts event details from the page."""
    global stop_scraping

    try:
        # Ensure page is fully loaded
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)  # Allow additional loading time
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
        await asyncio.sleep(2)

        # Check if elements exist
        event_blocks = await page.query_selector_all(".module_item")
        if not event_blocks:
            print("⚠️ No events found on the page.")
            return

        for event in event_blocks:
            if stop_scraping:
                return

            try:
                # Extract Event Date
                date_element = await event.query_selector(".module_date-time")
                event_date = await date_element.inner_text() if date_element else "UNKNOWN"
                parsed_event_date = await parse_date(event_date)

                # Skip events without a valid date
                if not parsed_event_date:
                    continue

                event_year = parsed_event_date.year

                # Stop scraping if the year is 2019 or earlier
                if event_year < 2020:
                    print(f"🛑 Stopping: Found event from {event_year}")
                    stop_scraping = True
                    return

                # Extract Event Name
                event_name_element = await event.query_selector(".module_headline")
                event_name = await event_name_element.inner_text() if event_name_element else "No Title"

                # Extract File Links
                file_links_elements = await event.query_selector_all(".module_link")

                file_links = []
                for link in file_links_elements:
                    file_url = await link.get_attribute("href")
                    file_name = await link.inner_text() if link else "Unknown File"

                    if file_url:
                        full_url = urljoin(BASE_URL, file_url)
                        file_extension = file_url.split(".")[-1].lower() if "." in file_url else "unknown"

                        file_links.append({
                            "file_name": file_name.strip(),
                            "file_type": file_extension,
                            "date": parsed_event_date.strftime("%Y/%m/%d"),
                            "category": "other",
                            "source_url": full_url,
                            "wissen_url": "unknown"
                        })

                # Store Event Data in Required JSON Structure
                if file_links:
                    events_collected.append({
                        "equity_ticker": EQUITY_TICKER,
                        "source_type": "company_information",
                        "frequency": "non-periodic",
                        "event_type": "other",
                        "event_name": event_name,
                        "event_date": parsed_event_date.strftime("%Y/%m/%d"),
                        "data": file_links
                    })
                    print(f"📄 [Event Created] {event_date} -> {len(file_links)} files")
                else:
                    print(f"❌ No valid files found for {event_date}")

            except Exception as e:
                print(f"⚠️ Error processing event: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting events: {e}")


async def find_next_page(page):
    """Finds the next page button/link and returns the next page URL."""
    try:
        next_page_element = await page.query_selector("a.paging-link[aria-label='Next']")
        if next_page_element:
            next_page_url = await next_page_element.get_attribute("href")
            if next_page_url:
                return urljoin(BASE_URL, next_page_url)
    except Exception:
        pass
    return None


async def select_year_from_dropdown(page, year):
    """Selects a different year from the dropdown and ensures page updates."""
    try:
        await page.wait_for_selector("#select2-eventArchiveYear-container", timeout=5000)
        dropdown = await page.query_selector("#select2-eventArchiveYear-container")

        if dropdown:
            print(f"🔽 Selecting Year: {year}")
            await dropdown.click()  # Open dropdown
            await asyncio.sleep(2)  # Wait for dropdown animation

            # Wait for dropdown options to load
            await page.wait_for_selector(".select2-results__option", timeout=5000)

            # Find and click the correct year
            year_option = await page.query_selector(f".select2-results__option[role='option']:has-text('{year}')")

            if year_option:
                await year_option.click()
                await asyncio.sleep(3)  # Allow page reload

                # **Ensure the page actually updates**
                await page.wait_for_selector(".module_item", timeout=10000)  # Wait for new events to load

                # Confirm selection worked by checking the new selected year
                selected_year_element = await page.query_selector("#select2-eventArchiveYear-container")
                selected_year = await selected_year_element.inner_text()

                if str(year) in selected_year:
                    print(f"✅ Successfully selected year: {year}")
                    return True
                else:
                    print(f"❌ Year {year} was not selected properly.")
                    return False

        return False
    except Exception as e:
        print(f"⚠️ Error selecting year {year}: {e}")
        return False


async def scrape_pinterest_press_releases():
    """Main function to scrape press releases."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": BASE_URL
        })

        page = await context.new_page()
        await enable_stealth(page)

        current_url = BASE_URL
        await page.goto(current_url, wait_until="networkidle", timeout=120000)
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")

        # Scrape the current year first
        await extract_events_from_page(page)

        # Select past years (from 2024 down to 2019)
        for year in range(2024, 2018, -1):
            if await select_year_from_dropdown(page, year):
                print(f"🔄 Scraping data for {year}...")
                await extract_events_from_page(page)
            else:
                print(f"⏭️ Skipping year {year} (not selectable or no data).")
                continue

        if events_collected:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(events_collected, f, indent=4)
            print(f"\n✅ Events saved in: {OUTPUT_FILE}")
        else:
            print("\n❌ No events found.")

        await browser.close()


# Run the scraper
asyncio.run(scrape_pinterest_press_releases())

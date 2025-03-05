import asyncio
import random
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from scripts.UTILS import utils

# Configurations
SEC_FILINGS_URL = "https://investor.thecampbellscompany.com/events-presentations"
EQUITY_TICKER = "CPB"
JSON_FILENAME = "JSONS/cpb_events.json"
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

import asyncio
from urllib.parse import urljoin

async def extract_events_from_page(page):
    """Extracts webcast links and support materials from paginated event pages until reaching 2019."""
    global stop_scraping
    try:
        page_number = 0  # Start from the first page
        has_more_pages = True

        while has_more_pages:
            print(f"\n🔍 Extracting events from page {page_number}...")

            await page.wait_for_timeout(2000)  # Allow page content to load

            # Select all event rows
            event_rows = await page.query_selector_all("article.node--nir-event--nir-widget-list")

            if not event_rows:
                print("⚠️ No events found on this page. Stopping pagination.")
                return  # Exit function

            print(f"📌 Found {len(event_rows)} events on page {page_number}.")

            for event_row in event_rows:
                try:
                    # Extract event date
                    date_element = await event_row.query_selector("div.nir-widget--event--date")
                    event_date = await date_element.inner_text() if date_element else "UNKNOWN DATE"
                    event_date_parsed = await parse_date3(event_date)

                    if not event_date_parsed:
                        print(f"⚠️ Error parsing date: {event_date}")
                        continue

                    if event_date_parsed.year < 2019:
                        print(f"🛑 Stopping: Found event from {event_date_parsed.year}, stopping scraper.")
                        stop_scraping = True
                        return  # Exit function

                    # Extract event name
                    title_element = await event_row.query_selector("div.field-nir-event-title a")
                    event_name = await title_element.inner_text() if title_element else "Unknown Event"

                    # Extract webcast link
                    webcast_url = None
                    webcast_element = await event_row.query_selector("div.nir-widget--event--webcast a")
                    if webcast_element:
                        webcast_url = await webcast_element.get_attribute("href")

                    # Extract support material files
                    file_links = []
                    support_materials = await event_row.query_selector_all("div.nir-widget--event--support-materials a")

                    for file_element in support_materials:
                        file_url = await file_element.get_attribute("href")
                        file_name = await file_element.inner_text() if file_element else "Unknown File"

                        if not file_url:
                            continue

                        # Convert to full URL if needed
                        if not file_url.startswith("http"):
                            file_url = urljoin(SEC_FILINGS_URL, file_url)

                        file_type = "pdf" if file_url.endswith(".pdf") else "html"

                        freq = classify_frequency(event_name, file_url)
                        if freq == "periodic":
                            event_type = classify_periodic_type(event_name, file_url)
                            event_name = extract_quarter_from_name(event_name)
                        else:
                            event_type = categorize_event(event_name)
    
    
                        category = classify_document(event_name, file_url) 
                        file_type = get_file_type(file_url)

                        file_links.append({
                            "file_name": file_name,
                            "file_type": file_type,
                            "category": category,
                            "date": event_date_parsed.strftime("%Y/%m/%d"),
                            "source_url": file_url,
                            "wissen_url": "NULL",
                        })

                    # Skip events with no webcast or support materials
                    if not webcast_url and not file_links:
                        continue

                    

                    # Append structured event data
                    file_links_collected.append({
                        "equity_ticker": "CPB",
                        "source_type": "company_events",
                        "frequency": freq,
                        "event_type": event_type,
                        "event_name": event_name.strip(),
                        "event_date": event_date_parsed.strftime("%Y/%m/%d"),
                        "data": file_links
                    })

                    print(f"✅ Extracted: {event_name}, Date: {event_date_parsed.strftime('%Y/%m/%d')}")

                except Exception as e:
                    print(f"⚠️ Error processing an event: {e}")

            # Navigate to next page
            next_page_url = await find_next_page(page)
            if next_page_url:
                page_number += 1
            else:
                has_more_pages = False

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
    """Finds and navigates to the next page if pagination exists."""
    try:
        await page.wait_for_timeout(2000)  # Allow time for pagination to load

        next_page_selector = "li.pager__item--next a"
        next_page_element = await page.query_selector(next_page_selector)

        if next_page_element:
            next_page_url = await next_page_element.get_attribute("href")
            if next_page_url:
                full_next_page_url = urljoin(SEC_FILINGS_URL, next_page_url)
                print(f"🔄 Moving to next page: {full_next_page_url}")
                await page.goto(full_next_page_url)
                await page.wait_for_load_state("domcontentloaded")
                return full_next_page_url  # Return valid URL
        else:
            print("✅ No more pages. Stopping pagination.")
            return None  # No more pages

    except Exception as e:
        print(f"⚠️ Error navigating to next page: {e}")
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
            await extract_events_from_page(page)
            await scrape_all_years(page)
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

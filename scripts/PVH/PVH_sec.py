import asyncio
import json
from urllib.parse import urljoin
from playwright.async_api import async_playwright
import random

# Configure the SEC filings URL and the equity ticker
SEC_FILINGS_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000078239&owner=include&count=100&hidefilings=0"
EQUITY_TICKER = "PVH"
JSON_FILENAME = "JSONS/pvh_sec.json"


# Track visited pages and collected file links
visited_urls = set()
file_links_collected = []


async def accept_cookies(page):
    """Accepts cookies if a consent banner appears."""
    try:
        cookie_button = await page.query_selector("button:has-text('Accept')")
        if cookie_button:
            await cookie_button.click()
            await asyncio.sleep(2)  # Wait to ensure the banner disappears
            print("✅ Accepted cookies.")
    except Exception as e:
        print(f"⚠️ No cookie consent banner found or error clicking it: {e}")


async def extract_data_from_page(page):
    """Extracts the links and associated dates from the table on the page."""
    try:
        # Select all rows in the table (skip the header row)
        rows = await page.query_selector_all("table.tableFile2 tbody tr")

        # Loop through each row to extract the link and date
        for row in rows:
            try:
                # Extract link (second column)
                link_element = await row.query_selector("td:nth-child(2) a")
                link_url = await link_element.get_attribute("href") if link_element else None

                # Extract the date (fourth column)
                date_element = await row.query_selector("td:nth-child(4)")
                event_date = await date_element.inner_text() if date_element else "UNKNOWN DATE"

                if link_url:
                    # Construct the absolute URL from the relative link
                    absolute_url = urljoin(SEC_FILINGS_URL, link_url)

                    # Extract the event name (description in the third column)
                    description_element = await row.query_selector("td:nth-child(3)")
                    event_name = await description_element.inner_text() if description_element else "Unknown Event"

                    # Append the extracted data to the list
                    file_links_collected.append({
                        "equity_ticker": EQUITY_TICKER,
                        "source_type": "company_information",
                        "frequency": "NULL",  # Placeholder for frequency
                        "event_type": "NULL",  # Placeholder for event type
                        "event_name": event_name.strip(),
                        "event_date": event_date.strip(),
                        "data": [{
                            "file_name": absolute_url.split('/')[-1],
                            "file_type": absolute_url.split('.')[-1] if '.' in absolute_url else 'link',
                            "date": event_date.strip(),
                            "category": event_name.strip(),
                            "source_url": absolute_url,
                            "wissen_url": "NULL"
                        }]
                    })

            except Exception as e:
                print(f"⚠️ Error processing row: {e}")

    except Exception as e:
        print(f"⚠️ Error extracting data from page: {e}")


async def go_to_next_page(page):
    """Finds and clicks the 'Next' button to navigate to the next page."""
    try:
        next_button = await page.query_selector("input[type='button'][value='Next 100']")
        if next_button:
            await next_button.click()
            await asyncio.sleep(3)  # Wait for the page to load
            print("🔄 Moving to the next page...")
        else:
            print("✅ No 'Next' button found. Stopping pagination.")
            return False
    except Exception as e:
        print(f"⚠️ Error navigating to the next page: {e}")
        return False

    return True

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
        page = await context.new_page()

        # Start at the first page
        current_url = SEC_FILINGS_URL

        # Loop through all pages until the 'Next' button is no longer available
        while current_url:
            visited_urls.add(current_url)
            print(f"\n🔍 Visiting: {current_url}")
            try:
                await page.goto(current_url, wait_until="domcontentloaded", timeout=120000)
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
                await extract_data_from_page(page)  # Extract the data from the current page
                # await asyncio.sleep(random.uniform(0,1))  # Human-like delay

                # Attempt to go to the next page
                h = find_next_page(page)
                print(h)
                if not await go_to_next_page(page):
                    break

            except Exception as e:
                print(f"⚠️ Failed to load {current_url}: {e}")
                break

            # Get the next URL (to continue pagination)
            current_url = page.url  # The current URL is updated after navigating

        # Save the collected data to a JSON file
        if file_links_collected:
            with open(JSON_FILENAME, "w", encoding="utf-8") as f:
                json.dump(file_links_collected, f, indent=4)
            print(f"\n✅ File links saved in: {JSON_FILENAME}")
        else:
            print("\n❌ No file links found.")

        await browser.close()

# Run the scraper
asyncio.run(scrape_sec_filings())
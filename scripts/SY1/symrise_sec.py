import asyncio
import json
import random
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from urllib.parse import urljoin

# URL for Symrise Financial Results Page
BASE_URL = "https://www.symrise.com/investors/financial-results/"
OUTPUT_FILE = "JSONS/symrise_filings.json"

# Calculate the date threshold for the last 5 years
DATE_THRESHOLD = datetime.now() - timedelta(days=5*365)

async def parse_date(date_text):
    """Parses date strings into a standard format."""
    date_text = date_text.strip()
    
    # Common formats to try
    formats = [
        "%B %d, %Y",  # Example: March 6, 2024
        "%d %B %Y",   # Example: 6 March 2024
        "%Y-%m-%d",   # Example: 2024-03-06
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_text, fmt)
        except ValueError:
            continue

    print(f"⚠️ Failed to parse date: {date_text}")
    return None

def classify_filing_by_event(event_title):
    """Classifies an event as 'periodic' or 'non-periodic' based on event title."""
    periodic_forms = r'\b\d+[-]?K\b|\b\d+[-]?Q\b|Annual|Quarterly|Earnings'
    if re.search(periodic_forms, event_title, re.IGNORECASE):
        return "periodic"
    else:
        return "non-periodic"

def determine_file_type(file_url):
    """Determines file type from the URL extension."""
    extension_map = {
        "pdf": "pdf",
        "xls": "xls",
        "xlsx": "xlsx",
        "doc": "doc",
        "docx": "docx",
        "csv": "csv",
        "txt": "txt",
    }
    
    file_extension = file_url.split(".")[-1].lower() if "." in file_url else "unknown"
    return extension_map.get(file_extension, "unknown")

async def extract_data_from_page(page):
    """Extracts filings from the active year's section."""
    filings = []

    await page.wait_for_selector(".tab-titles", timeout=30000)

    # Extract available year tabs
    year_tabs = await page.query_selector_all(".tab-titles a")
    years = {await tab.inner_text(): tab for tab in year_tabs}
    print(f"🗓 Available Years: {list(years.keys())}")

    for year, tab in years.items():
        print(f"\n🔍 Scraping data for {year}...")

        try:
            # Click the year tab
            await tab.click()
            await asyncio.sleep(random.uniform(2, 4))  # Human-like delay
            
            # **Wait for a specific element to update**
            await page.wait_for_selector(".t-table", timeout=10000)

            event_sections = await page.query_selector_all(".t-table")
            if not event_sections:
                print(f"⚠️ No data found for {year}, skipping...")
                continue  # Skip if no data is available

            for section in event_sections:
                try:
                    # Extract date
                    date_element = await section.query_selector("p.news-date")
                    date_text = await date_element.inner_text() if date_element else "Unknown Date"
                    filing_date_parsed = await parse_date(date_text)

                    if not filing_date_parsed or filing_date_parsed < DATE_THRESHOLD:
                        print(f"🛑 Skipping: {date_text} (older than 5 years)")
                        continue
                    
                    filing_date = filing_date_parsed.strftime("%Y/%m/%d")

                    # Extract event title
                    event_title_element = await section.query_selector("h3")
                    event_title = await event_title_element.inner_text() if event_title_element else "Unknown Event"

                    # Determine filing classification
                    filing_frequency = classify_filing_by_event(event_title)

                    file_links = []
                    file_elements = await section.query_selector_all(".t-cell a")
                    for file in file_elements:
                        file_url = await file.get_attribute("href")
                        file_name = file_url.split("/")[-1] if file_url else "unknown"
                        file_type = determine_file_type(file_url)
                        full_url = urljoin(BASE_URL, file_url) if file_url else None

                        if file_url:
                            file_links.append({
                                "file_name": file_name,
                                "file_type": file_type,
                                "date": filing_date,
                                "category": "report" if file_type == "pdf" else "other",
                                "source_url": full_url,
                                "wissen_url": "unknown"
                            })
                    
                    if file_links:
                        filings.append({
                            "equity_ticker": "SY1",
                            "source_type": "company_information",
                            "frequency": filing_frequency,
                            "event_type": "other",
                            "event_name": event_title,
                            "event_date": filing_date,
                            "data": file_links
                        })
                    print(f"📄 Extracted: {event_title} ({len(file_links)} files)")
                except Exception as e:
                    print(f"⚠️ Error processing section: {e}")
        except Exception as e:
            print(f"⚠️ Error scraping {year}: {e}")

    return filings


async def scrape_symrise():
    """Main function to scrape the Symrise financial results page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print(f"🔍 Visiting: {BASE_URL}")
            await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)  # Faster timeout
            await asyncio.sleep(5)  # Ensure page content loads

            filings = await extract_data_from_page(page)

            if filings:
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(filings, f, indent=4)
                print(f"\n✅ Data saved in: {OUTPUT_FILE}")
            else:
                print("\n❌ No data found.")
        
        except Exception as e:
            print(f"⚠️ Error: {e}")

        await browser.close()

# Run the scraper
asyncio.run(scrape_symrise())

import asyncio
import random
import json
import argparse
import traceback
from datetime import datetime
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import re

# Argument Parsing
parser = argparse.ArgumentParser(description="SEC Filings Scraper")
parser.add_argument("url", type=str, help="SEC Filings page URL")
parser.add_argument("ticker", type=str, help="Equity ticker symbol")
parser.add_argument("--output", type=str, default="sec_filings.json", help="Output JSON file name")

args = parser.parse_args()

# Configurations
SEC_FILINGS_URL = args.url
EQUITY_TICKER = args.ticker.upper()  # Convert to uppercase for standardization
JSON_FILENAME = args.output

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

async def parse_date(date_str):
    """Parse various date formats and return a standardized date."""
    date_str = date_str.strip()
    formats = [
        "%m/%d/%y",       # Example: 12/31/24
        "%m/%d/%Y",       # Example: 12/31/2024
        "%b %d, %Y",      # Example: Feb 28, 2025
        "%Y-%m-%d",       # Example: 2025-02-28
        "%d %b %Y"        # Example: 28 Feb 2025 
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    print(f"⚠️ Error parsing date: {date_str}")
    return None

def normalize_headers(headers):
    """Normalize column headers across different companies."""
    mapping = {
        "filing date": "date",
        "date": "date",
        "pdf": "view",
        "view": "view",
        "xbrl": "view",
        "downloads": "view",
        "form": "form",
        "description": "description"
    }
    return {mapping.get(h.lower().strip(), h.lower().strip()): i + 1 for i, h in enumerate(headers)}

def determine_file_type(mime_type, file_text):
    """Determine file type based on MIME type and file name."""
    mime_map = {
        "application/pdf": "pdf",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/csv": "csv",
        "text/plain": "txt",
    }
    
    if mime_type in mime_map:
        return mime_map[mime_type]
    
    if "." in file_text:
        return file_text.split(".")[-1].lower()
    
    return "unknown"

def classify_filing_by_form(form_type):
    """Classifies a filing as 'periodic' or 'non-periodic' based on form type."""
    periodic_forms = r'\b\d+[-]?K\b|\b\d+[-]?Q\b'
    if re.search(periodic_forms, form_type, re.IGNORECASE):
        return "periodic"
    else:
        return "non-periodic"

def classify_filing_by_event(event_name, form_type):
    """Classifies a filing event based on event name and form type."""
    event_name_lower = event_name.lower()

    # Check for earnings report, conference calls, annual meetings, or acquisitions
    if "earnings" in event_name_lower or "results" in event_name_lower:
        return "earnings_call"
    elif "conference" in event_name_lower or "call" in event_name_lower:
        return "conference_call"
    elif "annual meeting" in event_name_lower:
        return "annual_meeting"
    elif "acquisition" in event_name_lower or "merger" in event_name_lower:
        return "acquisition"
    
    
async def extract_files_from_page(page):
    """Extracts filing dates, filing type, descriptions, and file links from the SEC filings table."""
    global stop_scraping
    try:
        await page.wait_for_selector("table", timeout=30000)

        # Get table headers and normalize them
        header_cells = await page.query_selector_all("table thead tr th")
        detected_headers = [await cell.inner_text() for cell in header_cells]
        print(f"\n📝 Detected Headers: {detected_headers}")  # Debug print

        column_indices = normalize_headers(detected_headers)

        # Check for required columns
        required_columns = {"date", "view", "form", "description"}
        missing_columns = required_columns - set(column_indices.keys())
        if missing_columns:
            print(f"⚠️ Missing columns: {missing_columns} (Detected: {list(column_indices.keys())})")
            return

        filing_date_col = column_indices["date"]
        view_col = column_indices["view"]
        form_col = column_indices["form"]
        desc_col = column_indices["description"]

        rows = await page.query_selector_all("table tbody tr")
        if not rows:
            print("⚠️ No rows found in table.")
            return

        for row in rows:
            if stop_scraping:
                return
            
            try:
                # Extract Filing Date
                filing_date_element = await row.query_selector(f"td:nth-child({filing_date_col})")
                filing_date = await filing_date_element.inner_text() if filing_date_element else "UNKNOWN"
                filing_date_parsed = await parse_date(filing_date)
                if not filing_date_parsed:
                    continue
                
                filing_year = filing_date_parsed.year

                if filing_year < 2019:
                    print(f"🛑 Stopping: Found filing from {filing_year}")
                    stop_scraping = True
                    return

                # Extract Filing Type
                filing_type_element = await row.query_selector(f"td:nth-child({form_col})")
                filing_type = await filing_type_element.inner_text() if filing_type_element else "Unknown Form"

                # Classify the filing frequency (periodic/non-periodic)
                filing_frequency = classify_filing_by_form(filing_type)

                # Extract Description (Text + Hyperlink)
                description_element = await row.query_selector(f"td:nth-child({desc_col})")
                description = await description_element.inner_text() if description_element else "No Description"

                # Classify the event type using both event name and form type
                event_type = classify_filing_by_event(description, filing_type)

                description_link_element = await description_element.query_selector("a[href]") if description_element else None
                description_link = await description_link_element.get_attribute("href") if description_link_element else None

                file_links = []

                # Extract File Links from "View"/"XBRL" Column
                view_column = await row.query_selector_all(f"td:nth-child({view_col}) a[href]")

                for link in view_column:
                    file_url = await link.get_attribute("href")
                    file_text = (await link.inner_text()).strip().lower()
                    file_mime = await link.get_attribute("type")  # Extract MIME type
                    
                    if file_url:
                        full_url = urljoin(SEC_FILINGS_URL, file_url)
                        file_ext = determine_file_type(file_mime, file_text)

                        # Determine category based on file type
                        category = "report" if "pdf" in file_ext else "other"

                        file_links.append({
                            "file_name": file_url.split("/")[-1],
                            "file_type": file_ext,
                            "date": filing_date_parsed.strftime("%Y/%m/%d"),
                            "category": category,
                            "source_url": full_url,
                            "wissen_url": "unknown"
                        })

                # Add File Link from Description Column if Available
                if description_link:
                    full_url = urljoin(SEC_FILINGS_URL, description_link)
                    file_links.append({
                        "file_name": description_link.split("/")[-1],
                        "file_type": "unknown",  # Could be HTML, PDF, etc.
                        "date": filing_date_parsed.strftime("%Y/%m/%d"),
                        "category": "description_link",
                        "source_url": full_url,
                        "wissen_url": "unknown"
                    })

                # **Store all files under a single event (instead of multiple events)**
                if file_links:
                    file_links_collected.append({
                        "equity_ticker": EQUITY_TICKER,
                        "source_type": "company_information",
                        "frequency": filing_frequency,  # **Using the classification function**
                        "event_type": event_type,  # **Using the classification function**
                        "event_name": description,
                        "event_date": filing_date_parsed.strftime("%Y/%m/%d"),
                        "data": file_links  # **All files in the same row grouped together**
                    })
                    print(f"📄 [Event Created] {filing_date} -> {len(file_links)} files")
                else:
                    print(f"❌ No valid files found for {filing_date}")

            except Exception as e:
                print(f"⚠️ Error processing row: {e}")
    except Exception as e:
        print(f"⚠️ Error extracting files: {e}")


async def find_next_page(page):
    """Finds the next page button/link and returns the next page URL."""
    try:
        await page.wait_for_selector("a", timeout=10000)
        all_links = await page.query_selector_all("a")

        for link in all_links:
            text = (await link.inner_text()).strip().lower()
            if "next" in text or ">" in text:
                next_page_url = await link.get_attribute("href")
                if next_page_url:
                    return urljoin(SEC_FILINGS_URL, next_page_url)
    except Exception:
        pass
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
        while current_url and current_url not in visited_urls and not stop_scraping:
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

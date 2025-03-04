import asyncio
import json
import random
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from urllib.parse import urljoin

# URL for Symrise Financial Results Page
BASE_URL = "https://www.symrise.com/investors/financial-results/"
OUTPUT_FILE = "JSONS/symrise_filings.json"

# Calculate the date threshold for the last 5 years
DATE_THRESHOLD = datetime.now() - timedelta(days=5*365)

async def extract_data_from_page(page):
    """Extracts filings from the active year's section."""
    filings = []
    
    await page.wait_for_selector(".tab-titles", timeout=30000)
    
    # Extract available year tabs
    year_tabs = await page.query_selector_all(".tab-titles a")
    years = {await tab.inner_text(): tab for tab in year_tabs}
    print(f"Available Years: {list(years.keys())}")
    
    for year, tab in years.items():
        print(f"\n🔍 Scraping data for {year}...")
        await tab.click()
        await asyncio.sleep(random.uniform(2, 4))  # Human-like delay
        
        event_sections = await page.query_selector_all(".t-table")
        for section in event_sections:
            try:
                # Extract date from <p class="news-date">
                date_element = await section.query_selector("p.news-date")
                date_text = await date_element.inner_text() if date_element else "Unknown Date"
                filing_date_parsed = datetime.strptime(date_text, "%B %d, %Y")
                
                # Filter by last 5 years
                if filing_date_parsed < DATE_THRESHOLD:
                    print(f"🛑 Skipping: {date_text} (older than 5 years)")
                    continue
                
                filing_date = filing_date_parsed.strftime("%Y/%m/%d")
                
                # Extract event title
                event_title_element = await section.query_selector("h3")
                event_title = await event_title_element.inner_text() if event_title_element else "Unknown Event"
                
                file_links = []
                file_elements = await section.query_selector_all(".t-cell a")
                for file in file_elements:
                    file_url = await file.get_attribute("href")
                    file_text = (await file.inner_text()).strip().lower()
                    if file_url:
                        file_links.append({
                            "file_name": file_url.split("/")[-1],
                            "file_type": file_text.split(".")[-1],
                            "source_url": urljoin(BASE_URL, file_url)
                        })
                
                if file_links:
                    filings.append({
                        "year": year,
                        "event_date": filing_date,
                        "event_title": event_title,
                        "files": file_links
                    })
                print(f"📄 Extracted: {event_title} ({len(file_links)} files)")
            except Exception as e:
                print(f"⚠️ Error processing section: {e}")
    return filings

async def scrape_symrise():
    """Main function to scrape the Symrise financial results page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(BASE_URL, wait_until="load", timeout=60000)
        
        filings = await extract_data_from_page(page)
        
        if filings:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(filings, f, indent=4)
            print(f"\n✅ Data saved in: {OUTPUT_FILE}")
        else:
            print("\n❌ No data found.")
        
        await browser.close()

# Run the scraper
asyncio.run(scrape_symrise())

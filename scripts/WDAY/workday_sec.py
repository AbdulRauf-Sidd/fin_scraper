import asyncio
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import os
import sys

# Import Utility Functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))
from utils import *

BASE_URL = "https://investor.workday.com/sec-filings?year={year}"
START_YEAR = 2019
END_YEAR = 2025

# MIME Type Mapping for File Extensions

async def extract_document_links(year):
    """Extracts all filing events and document links for a given year."""
    filing_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url = BASE_URL.format(year=year)
        print(f"\n🔍 Visiting: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await utils.accept_cookies(page)  # Handle cookie consent popups
        await page.wait_for_selector("table tbody tr", timeout=10000)

        # Extract pagination links
        pagination_links = await page.query_selector_all("td a")
        pagination_urls = []

        for link in pagination_links:
            href = await link.get_attribute("href")
            if href and "index.php" in href:
                full_url = urljoin(url, href)
                if full_url not in pagination_urls:
                    pagination_urls.append(full_url)

        pagination_urls.insert(0, url)  # Ensure first page is processed
        print(f"🔄 Found {len(pagination_urls)} pages for {year}")

        for page_url in pagination_urls:
            print(f"➡️ Visiting Page: {page_url}")
            await page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            rows = await page.query_selector_all("table tbody tr")
            print(f"📄 Found {len(rows)} rows on page")

            for row in rows:
                date_element = await row.query_selector("td.wd_filing_date")
                desc_element = await row.query_selector("td.wd_description")
                doc_elements = await row.query_selector_all("td.wd_document_format a")  # Capture all document types

                if date_element and desc_element:
                    event_date = (await date_element.inner_text()).strip()
                    event_name = (await desc_element.inner_text()).strip()

                    # ✅ Determine the frequency of the event
                    freq = utils.classify_frequency(event_name, BASE_URL)

                    # ✅ Determine event type based on frequency
                    if freq == "periodic":
                        event_type = utils.classify_periodic_type(event_name, BASE_URL)
                        event_name = utils.format_quarter_string(event_date, event_name)
                    else:
                        event_type = utils.categorize_event(event_name)
                    
                    data_files = []
                    for doc in doc_elements:
                        doc_url = await doc.get_attribute("href")
                        if doc_url:
                            full_url = urljoin(page_url, doc_url)

                            # ✅ Fetch MIME type & map to file extension
                            file_type = utils.get_file_type(full_url)

                            # ✅ Extract file name
                            file_name = await utils.extract_file_name(full_url)

                            # ✅ Classify document category
                            category = utils.classify_document(event_name, full_url)

                            data_files.append({
                                "file_name": file_name,
                                "file_type": file_type,
                                "date": event_date,
                                "category": category,
                                "source_url": full_url,
                                "wissen_url": "NULL"
                            })

                    if data_files:
                        filing_data.append({
                            "equity_ticker": "WDAY",
                            "source_type": "company_information",
                            "frequency": freq,
                            "event_type": event_type,
                            "event_name": event_name,
                            "event_date": event_date,
                            "data": data_files
                        })

        await browser.close()

    print(f"\n✅ Total Documents Found for {year}: {len(filing_data)}")
    return filing_data

async def main():
    all_data = []
    for year in range(END_YEAR, START_YEAR - 1, -1):
        filings = await extract_document_links(year)
        all_data.extend(filings)

    with open("JSONS/workday_filings.json", "w") as f:
        json.dump(all_data, f, indent=4)
    
    print(f"\n🎯 Total JSON Records: {len(all_data)}")

if __name__ == "__main__":
    asyncio.run(main())

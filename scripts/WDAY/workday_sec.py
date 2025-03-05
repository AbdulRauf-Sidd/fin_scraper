import asyncio
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin

BASE_URL = "https://investor.workday.com/sec-filings?year={year}"
START_YEAR = 2019
END_YEAR = 2025

# MIME Type Mapping for File Extensions
MIME_TYPE_MAPPING = {
    "application/pdf": ".pdf",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "text/html": ".html",
    "application/zip": ".zip",
    "application/xml": ".xml",
    "application/json": ".json",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "audio/mpeg": ".mp3",
    "video/mp4": ".mp4",
}

async def get_mime_type(page, url):
    """Fetch MIME type from headers."""
    try:
        response = await page.request.head(url)
        content_type = response.headers.get("content-type", "").split(";")[0]  # Extract MIME type
        return MIME_TYPE_MAPPING.get(content_type, content_type)  # Return mapped extension or raw MIME type
    except Exception as e:
        print(f"⚠️ Error fetching MIME type for {url}: {e}")
        return "unknown"

async def extract_document_links(year):
    """Extracts all filing events and document links for a given year."""
    filing_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = BASE_URL.format(year=year)
        print(f"\n🔍 Visiting: {url}")
        await page.goto(url, wait_until="load", timeout=60000)
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
            await page.goto(page_url, wait_until="load", timeout=60000)
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

                    data_files = []
                    for doc in doc_elements:
                        doc_url = await doc.get_attribute("href")
                        if doc_url:
                            full_url = urljoin(page_url, doc_url)
                            mime_type = await get_mime_type(page, full_url)  # Detect document type
                            file_name = full_url.split("/")[-1]

                            data_files.append({
                                "file_name": file_name,
                                "file_type": mime_type,
                                "date": event_date,
                                "category": "report",
                                "source_url": full_url,
                                "wissen_url": ""
                            })

                    if data_files:
                        filing_data.append({
                            "equity_ticker": "WDAY",
                            "source_type": "company_information",
                            "frequency": "non-periodic",
                            "event_type": "company_filing",
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

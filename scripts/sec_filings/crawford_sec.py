import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

# MIME Type to File Extension Mapping
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

def classify_filing_by_form(form_type):
    """Classifies a filing as 'periodic' or 'non-periodic' based on form type."""
    periodic_forms = r'\b\d+[-]?K\b|\b\d+[-]?Q\b'
    return "periodic" if re.search(periodic_forms, form_type, re.IGNORECASE) else "non-periodic"

def classify_periodic_type(event_name, event_url):
    """Classifies periodic filings into annual or quarterly based on keywords."""
    if re.search(r'annual', event_name, re.IGNORECASE) or re.search(r'annual', event_url, re.IGNORECASE):
        return "annual"
    if re.search(r'(quarterly|quarter|Q[1234])', event_name, re.IGNORECASE) or re.search(r'(quarterly|quarter|Q[1234])', event_url, re.IGNORECASE):
        return "quarterly"
    return 'quarterly'  

def format_quarter_string(event_date, event_name):
    """Formats event date into quarter-year format."""
    try:
        parsed_date = datetime.strptime(event_date, "%m/%d/%Y")  # Convert date string to datetime
        quarter = (parsed_date.month - 1) // 3 + 1
        return f"Q{quarter} {parsed_date.year}"
    except (ValueError, TypeError):
        return re.search(r'(\b\d{4}\b)', event_name).group(0) if re.search(r'(\b\d{4}\b)', event_name) else "Unknown Year"

async def get_mime_type(page, url):
    """Fetches MIME type of a document from headers."""
    try:
        response = await page.request.head(url)
        content_type = response.headers.get("content-type", "").split(";")[0]  # Extract MIME type
        return MIME_TYPE_MAPPING.get(content_type, content_type)  # Return file extension or raw MIME type
    except Exception as e:
        print(f"⚠️ Error fetching MIME type for {url}: {e}")
        return "unknown"

async def scrape_pdfs(url, start_year, end_year):
    pdf_data = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run headless for efficiency
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await asyncio.sleep(3)  # Initial Wait

        for year in range(start_year, end_year + 1):
            print(f"📌 Scraping Year: {year}")

            # Select Year
            await page.select_option("#SecYearSelect", str(year))
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)

            page_number = 1
            while True:
                print(f"🔄 Page {page_number}")

                # Get Rows
                rows = await page.query_selector_all("div.module_item.list--reset:not([aria-hidden='true'])")
                if not rows:
                    print(f"⚠️ No Rows, Retrying Page {page_number}...")
                    await asyncio.sleep(3)
                    continue

                for row in rows:
                    date_element = await row.query_selector("span.module-sec_date-text")
                    desc_element = await row.query_selector("span.module-sec_description-text")
                    filing_element = await row.query_selector("div.module-sec_filing a.module-sec_filing-link")
                    doc_elements = await row.query_selector_all("li.module-sec_download-list-item a")  # All docs
                    
                    event_date = await date_element.inner_text() if date_element else "No Date"
                    description = await desc_element.inner_text() if desc_element else "No Description"
                    filing_text = await filing_element.inner_text() if filing_element else "Unknown"

                    filing_frequency = classify_filing_by_form(filing_text)
                    event_type = classify_periodic_type(description, filing_text) if filing_frequency == "periodic" else "other"
                    event_name = format_quarter_string(event_date.strip(), description) if filing_frequency == "periodic" else description

                    print(f"✅ Year: {year} | Date: {event_date} | Description: {description} | Filing Type: {filing_text}")

                    # ✅ Format JSON correctly
                    event_data = {
                        "equity_ticker": "CRDA",
                        "source_type": "company_information",
                        "frequency": filing_frequency,
                        "event_type": event_type,
                        "event_name": event_name,
                        "event_date": event_date.strip(),
                        "data": []
                    }

                    # Extract ALL document types
                    for doc in doc_elements:
                        doc_url = await doc.get_attribute("href")
                        if doc_url:
                            doc_url = f"https:{doc_url}"
                            mime_type = await get_mime_type(page, doc_url)  # Detect document type
                            file_name = doc_url.split("/")[-1]

                            event_data["data"].append({
                                "file_name": file_name,
                                "file_type": mime_type,
                                "date": event_date.strip(),
                                "category": "report",
                                "source_url": doc_url,
                                "wissen_url": f"https://ourstorage.com/{file_name}"
                            })

                    # ✅ Append event_data instead of separate entries
                    pdf_data.append(event_data)

                # Handle Pagination
                pagination_buttons = await page.query_selector_all("button.pager_button.pager_page")
                next_page_number = page_number + 1
                next_button = None

                for button in pagination_buttons:
                    btn_text = await button.inner_text()
                    if btn_text.isdigit() and int(btn_text) == next_page_number:
                        next_button = button
                        break

                if next_button:
                    await next_button.click()
                    await asyncio.sleep(3)  # Allow page update
                    active_page = await page.query_selector("button.pager_button.pager_page[aria-current='true']")
                    current_page = await active_page.inner_text() if active_page else None
                    if current_page and int(current_page) == next_page_number:
                        page_number += 1
                        continue
                    else:
                        print(f"⚠️ Error: Page did not advance to {next_page_number}, stopping.")
                        break
                else:
                    print(f"✅ Finished Year {year}")
                    break

        await browser.close()

    if pdf_data:
        print(f"✅ Total events found: {len(pdf_data)}")
        with open("JSONS/crawford.json", "w") as f:
            json.dump(pdf_data, f, indent=4)
            print("\n🎯 Data saved to `sec_filings.json`")
    else:
        print("❌ No documents found.")

if __name__ == "__main__":
    url = "https://ir.crawco.com/financials/default.aspx"
    asyncio.run(scrape_pdfs(url, 2019, 2025))

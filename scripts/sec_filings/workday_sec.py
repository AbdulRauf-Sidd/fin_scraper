import asyncio
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin

BASE_URL = "https://investor.workday.com/sec-filings?year={year}"
START_YEAR = 2019
END_YEAR = 2025

async def extract_pdf_links(year):
    pdf_data = []
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

        pagination_urls.insert(0, url)
        print(f"🔄 Found {len(pagination_urls)} pages for {year}")

        for page_url in pagination_urls:
            print(f"➡️ Visiting Page: {page_url}")
            await page.goto(page_url, wait_until="load", timeout=60000)
            await asyncio.sleep(3)

            rows = await page.query_selector_all("table tbody tr")
            print(f"Found {len(rows)} rows on page")

            for row in rows:
                date_element = await row.query_selector("td.wd_filing_date")
                desc_element = await row.query_selector("td.wd_description")
                pdf_elements = await row.query_selector_all("td.wd_document_format a.wd_document_pdf")

                if date_element and desc_element:
                    event_date = (await date_element.inner_text()).strip()
                    event_name = (await desc_element.inner_text()).strip()

                    data_files = []
                    for pdf in pdf_elements:
                        href = await pdf.get_attribute("href")
                        if href:
                            full_url = urljoin(page_url, href)
                            data_files.append({
                                "file_name": href.split("/")[-1],
                                "file_type": ".pdf",
                                "date": event_date,
                                "category": "report",
                                "source_url": full_url,
                                "wissen_url": ""
                            })

                    if data_files:
                        pdf_data.append({
                            "equity_ticker": "WDAY",
                            "source_type": "company_information",
                            "frequency": "non-periodic",
                            "event_type": "company_filing",
                            "event_name": event_name,
                            "event_date": event_date,
                            "data": data_files
                        })

        await browser.close()

    print(f"\n✅ Total PDFs Found for {year}: {len(pdf_data)}")
    return pdf_data

async def main():
    all_data = []
    for year in range(END_YEAR, START_YEAR - 1, -1):
        pdfs = await extract_pdf_links(year)
        all_data.extend(pdfs)

    with open("JSONS/workday_filings.json", "w") as f:
        json.dump(all_data, f, indent=4)
    
    print(f"\n🎯 Total JSON Records: {len(all_data)}")

if __name__ == "__main__":
    asyncio.run(main())
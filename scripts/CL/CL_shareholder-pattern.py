import asyncio
from playwright.async_api import async_playwright
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from scripts.UTILS import utils

async def scrape_documents(url, filename):
    base_url = "https://colgate.com.pk"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": base_url
        })
        page = await context.new_page()
        await enable_stealth(page)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector(".fusion-builder-row")  # Ensure the content is loaded

        data_collection = []

        # Extract links from the table
        rows = await page.query_selector_all(".fusion-builder-row .fusion_builder_column_3_5 table tbody tr")
        for row in rows:
            link = await row.query_selector("td a")
            if link:
                href = await link.get_attribute('href')
                text = await link.text_content()
                date = await extract_date_from_text(text)
                if href.startswith('/'):  # Handling relative URLs if found
                    href = base_url + href
                absolute_url = ensure_absolute_url(base_url, href)


                freq = classify_frequency(text, href)
                if freq == "periodic":
                    event_name = format_quarter_string(date, text)
                    event_type = classify_periodic_type(event_name, href)

                else:
                    event_type = categorize_event(event_name)
                    event_name = text

                category = classify_document(event_name, href) 
                file_type = get_file_type(href)

                file_name = await extract_file_name(href)

                data_entry = {
                    "equity_ticker": "CL",
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": event_name,
                    "event_date": date,
                    "data": [{
                        "file_name": file_name,
                        "file_type": file_type,
                        "date": date,
                        "category": category,
                        "source_url": absolute_url,
                        "wissen_url": "NULL"
                    }]
                }
                data_collection.append(data_entry)

        await browser.close()

        # Save collected data to file
        for data in data_collection:
            save_json(data, filename)

async def main():
    url = 'https://colgate.com.pk/governance/share-holding-pattern/'
    filename = 'JSONS/cl_shareholder-pattern.json'
    await scrape_documents(url, filename)

if __name__ == "__main__":
    asyncio.run(main())

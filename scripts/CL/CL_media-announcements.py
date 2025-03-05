import asyncio
from playwright.async_api import async_playwright
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from utils import *

async def scrape_documents(url, filename):
    base_url = "https://colgate.com.pk"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector("table")  # Ensure the table is loaded

        data_collection = []

        # Extract links from the specified table
        rows = await page.query_selector_all("table tbody tr")
        for row in rows:
            title_element = await row.query_selector("td:nth-child(2) a")
            link_element = await row.query_selector("td:nth-child(3) a")
            if title_element and link_element:
                href = await link_element.get_attribute('href')
                title = await title_element.text_content()
                date = await extract_date_from_text(title)
                if href.startswith('/'):  # Handling relative URLs if found
                    href = base_url + href
                absolute_url = ensure_absolute_url(base_url, href)

                freq = classify_frequency(title, href)
                if freq == "periodic":
                    event_type = classify_periodic_type(event_name, href)
                    event_name = format_quarter_string(date, event_name)
                else:
                    event_type = categorize_event(event_name)

                category = classify_document(event_name, href) 
                file_type = get_file_type(href)
                
                data_entry = {
                    "equity_ticker": "CL",
                    "source_type": "company_information",
                    "frequency": freq,
                    "event_type": event_type,
                    "event_name": title.strip(),
                    "event_date": date,
                    "data": [{
                        "file_name": absolute_url.split('/')[-1],
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
    url = 'https://colgate.com.pk/for-investors/media/'
    filename = 'JSONS/cl_media-announcements.json'
    await scrape_documents(url, filename)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from playwright.async_api import async_playwright
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from utils import *

async def scrape_documents(url, filename):
    base_url = "https://investors.coca-colacompany.com"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await KO_close_cookie_consent(page)
        await asyncio.sleep(3)  # Stabilize the page

        data_collection = []

        # Collect data from the current page and handle pagination
        while True:
            main_content_divs = await page.query_selector_all(".main-content .media-body")
            for div in main_content_divs:
                link_element = await div.query_selector("h2.media-heading a")
                date_element = await div.query_selector("div.date time")
                
                href = await link_element.get_attribute('href')
                event_name = await link_element.text_content()
                event_date = await date_element.get_attribute('datetime')
                absolute_url = ensure_absolute_url(base_url, href)

                data_entry = {
                    "equity_ticker": "KO",
                    "source_type": "company_information",
                    "frequency": classify_frequency(event_name, href),
                    "event_type": "press release",
                    "event_name": event_name.strip(),
                    "event_date": event_date,
                    "data": [{
                        "file_name": absolute_url.split('/')[-1],
                        "file_type": absolute_url.split('.')[-1] if '.' in absolute_url else 'link',
                        "date": event_date,
                        "category": event_name.strip(),
                        "source_url": absolute_url,
                        "wissen_url": "NULL"
                    }]
                }
                data_collection.append(data_entry)

            # Handle pagination
            next_button = await page.query_selector("div.control.next a")
            if next_button and await next_button.is_visible():
                await next_button.click()
                await asyncio.sleep(2)  # Wait for next page to load
            else:
                break  # Exit loop if no next page button is found

        await browser.close()

        # Save to file
        for data in data_collection:
            save_json(data, filename)

async def main():
    url = 'https://investors.coca-colacompany.com/news-events/press-releases'
    filename = 'JSONS/ko_press-release.json'
    await scrape_documents(url, filename)

if __name__ == "__main__":
    asyncio.run(main())

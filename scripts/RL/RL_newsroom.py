import asyncio
from playwright.async_api import async_playwright
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from scripts.UTILS import utils

async def scrape_documents(url, filename):
    base_url = "https://corporate.ralphlauren.com"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector(".newsroom-content")  # Ensure the content is loaded

        data_collection = []

        # Pagination control
        while True:
            news_items = await page.query_selector_all(".newsroom-content .corp-news")
            for news_item in news_items:
                link_element = await news_item.query_selector(".news-copy-title a")
                date_element = await news_item.query_selector(".news-copy-publish")
                
                href = await link_element.get_attribute('href')
                event_name = await link_element.text_content()
                event_date = await date_element.text_content()
                absolute_url = ensure_absolute_url(base_url, href)

                data_entry = {
                    "equity_ticker": "RL",
                    "source_type": "company_information",
                    "frequency": classify_frequency(event_name, href),
                    "event_type": "press release",
                    "event_name": event_name.strip(),
                    "event_date": event_date.strip(),
                    "data": [{
                        "file_name": absolute_url.split('/')[-1],
                        "file_type": absolute_url.split('.')[-1] if '.' in absolute_url else 'link',
                        "date": event_date.strip(),
                        "category": event_name.strip(),
                        "source_url": absolute_url,
                        "wissen_url": "NULL"
                    }]
                }
                data_collection.append(data_entry)

            next_button = await page.query_selector("div.control.next a")
            if next_button:
                await next_button.click()
                await asyncio.sleep(2)  # Delay to ensure the new page content loads
            else:
                break  # Break the loop if there's no next page button

        await browser.close()

        # Save collected data to file
        for data in data_collection:
            save_json(data, filename)

async def main():
    url = 'https://corporate.ralphlauren.com/newsroom'
    filename = 'JSONS/RL_newsroom.json'
    await scrape_documents(url, filename)

if __name__ == "__main__":
    asyncio.run(main())

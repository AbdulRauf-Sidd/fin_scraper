import asyncio
from playwright.async_api import async_playwright
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from scripts.UTILS import utils

async def scrape_news_events(url, filename):
    base_url = "https://www.pvh.com"
    data_collection = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Start with the initial page URL
        await page.goto(url)
        await asyncio.sleep(2)  # Wait for any dynamic content to load

        # Handle pagination
        while True:
            content_divs = await page.query_selector_all("div.row.content__container")
            for div in content_divs:
                link_elements = await div.query_selector_all('a')
                for element in link_elements:
                    href = await element.get_attribute('href')
                    text = await element.text_content()
                    date_element = await div.query_selector('p.list__date')
                    date_text = await date_element.text_content() if date_element else "Unknown Date"

                    if href and not href.startswith('http'):
                        href = base_url + href

                    data_entry = {
                        "equity_ticker": "PVH",
                        "source_type": "company_information",
                        "frequency": classify_frequency(text, href.split('/')[-1]),
                        "event_type": "press_release",
                        "event_name": text.strip(),
                        "event_date": date_text,
                        "data": [{
                            "file_name": href.split('/')[-1],
                            "file_type": "link",
                            "date": date_text,
                            "category": "NULL",
                            "source_url": href,
                            "wissen_url": "NULL"
                        }]
                    }
                    data_collection.append(data_entry)

            # Correct selector and method for the next page button
            next_page_button = await page.query_selector('button:has(i.mdi-chevron-right):not(.v-pagination__navigation--disabled)')
            if next_page_button:
                await next_page_button.click()
                await asyncio.sleep(2)  # Ensure new page loads fully
            else:
                break  # Exit loop if no next page button is found or it is disabled

        await browser.close()

    for data in data_collection:
        save_json(data, filename)

async def main():
    url = 'https://www.pvh.com/news?facets=content_type%3DEvents%7CPress%20Releases%7CStories%26'
    filename = 'JSONS/pvh_news.json'  # Path to the output file
    await scrape_news_events(url, filename)

asyncio.run(main())
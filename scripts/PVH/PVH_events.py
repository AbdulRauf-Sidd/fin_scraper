import asyncio
from playwright.async_api import async_playwright
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from utils import *

async def scrape_file_links_and_data(url, filename):
    base_url = "https://www.pvh.com"
    data_collection = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)

        link_elements = await page.query_selector_all('a[href*=".pdf"], a[href*=".docx"], a[href*=".xlsx"]')
        for element in link_elements:
            href = await element.get_attribute('href')
            text = await element.text_content()
            date = await extract_date_from_text(text)
            eventType = categorize_event(text)    
                
            if href and not href.startswith('http'):
                href = base_url + href
            
            file_type = href.split('.')[-1] if '.' in href else 'unknown'
            data_entry = {
                "equity_ticker": "PVH",
                "source_type": "company_information",
                "frequency": classify_frequency(text,href),
                "event_type": eventType,
                "event_name": text.strip(),
                "event_date": date,
                "data": [{
                    "file_name": href.split('/')[-1],
                    "file_type": file_type,
                    "date": date,
                    "category": "NULL",
                    "source_url": href,
                    "wissen_url": "NULL"
                }]
            }
            data_collection.append(data_entry)

        await browser.close()

    for data in data_collection:
        save_json(data, filename)

async def main():
    url = 'https://www.pvh.com/news?facets=content_type%3DEvents&nofilter=true'
    filename = 'JSONS/pvh_events.json'  # Change this as needed or make it configurable
    await scrape_file_links_and_data(url, filename)

asyncio.run(main())
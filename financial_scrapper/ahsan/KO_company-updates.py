import asyncio
from playwright.async_api import async_playwright
from common_utils import save_json, classify_frequency, ensure_absolute_url, KO_close_cookie_consent

async def scrape_documents(url, filename):
    base_url = "https://www.coca-colacompany.com"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        
        await KO_close_cookie_consent(page)
        
        await asyncio.sleep(3)  # Allow time for any dynamic content to load

        data_collection = []

        # First div structure
        event_blocks = await page.query_selector_all(".ir-cta-event-with-documents")
        for block in event_blocks:
            event_name_element = await block.query_selector("h2")
            event_name = await event_name_element.text_content() if event_name_element else "No Title"
            links = await block.query_selector_all(".result-line a")
            for link in links:
                href = await link.get_attribute('href')
                text = await link.text_content()
                absolute_url = ensure_absolute_url(base_url, href)
                data_entry = {
                    "equity_ticker": "KO",
                    "source_type": "company_information",
                    "frequency": classify_frequency(text, href),
                    "event_type": "NULL",
                    "event_name": event_name,
                    "event_date": "NULL",
                    "data": [{
                        "file_name": absolute_url.split('/')[-1],
                        "file_type": absolute_url.split('.')[-1] if '.' in absolute_url else 'link',
                        "date": "NULL",
                        "category": text.strip(),
                        "source_url": absolute_url,
                        "wissen_url": "NULL"
                    }]
                }
                data_collection.append(data_entry)

        # Second div structure
        update_blocks = await page.query_selector_all(".wrapper.text h2")
        for h2 in update_blocks:
            event_name = await h2.text_content()
            links = await h2.query_selector_all("a")
            for link in links:
                href = await link.get_attribute('href')
                text = await link.text_content()
                absolute_url = ensure_absolute_url(base_url, href)
                data_entry = {
                    "equity_ticker": "KO",
                    "source_type": "company_information",
                    "frequency": classify_frequency(text, href),
                    "event_type": "NULL",
                    "event_name": event_name,
                    "event_date": "NULL",
                    "data": [{
                        "file_name": absolute_url.split('/')[-1],
                        "file_type": absolute_url.split('.')[-1] if '.' in absolute_url else 'link',
                        "date": "NULL",
                        "category": text.strip(),
                        "source_url": absolute_url,
                        "wissen_url": "NULL"
                    }]
                }
                data_collection.append(data_entry)

        await browser.close()

        # Save data to file
        for data in data_collection:
            save_json(data, filename)

async def main():
    url = 'https://investors.coca-colacompany.com/'
    filename = 'data.json'  
    await scrape_documents(url, filename)

if __name__ == "__main__":
    asyncio.run(main())
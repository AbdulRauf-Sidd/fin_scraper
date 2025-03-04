import asyncio
from playwright.async_api import async_playwright
from common_utils import save_json, classify_frequency, ensure_absolute_url, KO_close_cookie_consent

async def scrape_documents(url, filename):
    base_url = "https://www.coca-colacompany.com"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await KO_close_cookie_consent(page)
        await asyncio.sleep(3)  # Stabilize the page

        data_collection = []

        main_container = await page.query_selector("main.container.responsivegrid")
        if main_container:
            links = await main_container.query_selector_all("a")
            for link in links:
                href = await link.get_attribute('href')
                text = await link.text_content()
                if href:
                    absolute_url = ensure_absolute_url(base_url, href)
                    data_entry = {
                        "equity_ticker": "KO",
                        "source_type": "company_information",
                        "frequency": classify_frequency(text, href),
                        "event_type": "NULL",
                        "event_name": text.strip(),
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
        else:
            print("Main container not found")

        await browser.close()

        # Write the collected data to a JSON file
        for data in data_collection:
            save_json(data, filename)

async def main():
    url = 'https://www.coca-colacompany.com/policies-and-practices'
    filename = 'data.json'
    await scrape_documents(url, filename)

if __name__ == "__main__":
    asyncio.run(main())

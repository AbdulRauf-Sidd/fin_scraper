import asyncio
from playwright.async_api import async_playwright
from common_utils import save_json, classify_frequency, ensure_absolute_url

async def scrape_documents(url, filename):
    base_url = "https://colgate.com.pk"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector("div.fusion-text")  # Ensure the div is loaded

        data_collection = []

        # Extract links from the specified div
        links = await page.query_selector_all("div.fusion-text-2 a")
        for link in links:
            href = await link.get_attribute('href')
            text = await link.text_content()
            if href:
                absolute_url = ensure_absolute_url(base_url, href)
                data_entry = {
                    "equity_ticker": "CL",
                    "source_type": "company_information",
                    "frequency": classify_frequency(text, href),
                    "event_type": "annual general meeting",  # Assuming the context
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

        await browser.close()

        # Save collected data to file
        for data in data_collection:
            save_json(data, filename)

async def main():
    url = 'https://colgate.com.pk/for-investors/investor-relations/'
    filename = 'data.json'
    await scrape_documents(url, filename)

if __name__ == "__main__":
    asyncio.run(main())
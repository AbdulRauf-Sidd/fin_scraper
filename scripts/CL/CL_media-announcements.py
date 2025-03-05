import asyncio
from playwright.async_api import async_playwright
from common_utils import save_json, classify_frequency, ensure_absolute_url, extract_date_from_text, categorize_event

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
                eventType = categorize_event(title)
                if href.startswith('/'):  # Handling relative URLs if found
                    href = base_url + href
                absolute_url = ensure_absolute_url(base_url, href)
                data_entry = {
                    "equity_ticker": "CL",
                    "source_type": "company_information",
                    "frequency": classify_frequency(title, href),
                    "event_type": eventType,
                    "event_name": title.strip(),
                    "event_date": date,
                    "data": [{
                        "file_name": absolute_url.split('/')[-1],
                        "file_type": absolute_url.split('.')[-1] if '.' in absolute_url else 'link',
                        "date": date,
                        "category": title.strip(),
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

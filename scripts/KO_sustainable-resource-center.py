import asyncio
from playwright.async_api import async_playwright
from common_utils import save_json, classify_frequency, ensure_absolute_url, extract_date_from_text, categorize_event

async def scrape_ko_documents(url, filename):
    base_url = "https://www.coca-colacompany.com"
    data_collection = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to the page
        await page.goto(url)
        await asyncio.sleep(3)  # Allow more time for the page to load

        # Check and close the cookie consent form if it appears
        cookie_consent = await page.query_selector("#onetrust-pc-sdk")
        if cookie_consent and await cookie_consent.is_visible():
            close_button = await page.query_selector("#close-pc-btn-handler")
            if close_button:
                await close_button.click()
                await asyncio.sleep(1)  # Wait after closing the cookie consent

        # Handle pagination and button clicking in a loop
        while True:
            # Interact with each accordion button
            accordion_buttons = await page.query_selector_all(".cmp-accordion__button")
            for button in accordion_buttons:
                if await button.is_visible():  # Ensure the button is visible
                    await button.scroll_into_view_if_needed()
                    await button.click()
                    await asyncio.sleep(1)  # Allow time for content to expand

            # Scrape links after all sections are expanded
            links = await page.query_selector_all("div.tabs.panelcontainer a")
            for link in links:
                href = await link.get_attribute('href')
                text = await link.text_content()
                absolute_url = ensure_absolute_url(base_url, href)
                date = await extract_date_from_text(text)
                date = await extract_date_from_text(text)
                eventType = categorize_event(text)     
            
                data_entry = {
                    "equity_ticker": "KO",
                    "source_type": "company_information",
                    "frequency": classify_frequency(text,href),
                    "event_type": eventType,
                    "event_name": text.strip(),
                    "event_date": date,
                    "data": [{
                        "file_name": absolute_url.split('/')[-1],
                        "file_type": absolute_url.split('.')[-1] if '.' in absolute_url else 'link',
                        "date": date,
                        "category": "NULL",
                        "source_url": absolute_url,
                        "wissen_url": "NULL"
                    }]
                }
                data_collection.append(data_entry)

            # Check for and click on the next page button if it exists
            next_page_button = await page.query_selector('button[aria-label="Next page"]')
            if next_page_button and await next_page_button.is_visible():
                await next_page_button.click()
                await asyncio.sleep(3)  # Wait for page to load and dynamic content
            else:
                break  # Exit loop if no next page button is found

        await browser.close()

    # Save collected data
    for data in data_collection:
        save_json(data, filename)

async def main():
    url = 'https://www.coca-colacompany.com/sustainability-resource-center#accordion-3b412a7c15-item-78a5345a7d'
    filename = 'JSONS/ko_sustainable-resource-center.json'
    await scrape_ko_documents(url, filename)

asyncio.run(main())
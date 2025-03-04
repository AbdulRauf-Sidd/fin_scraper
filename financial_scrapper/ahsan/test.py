import asyncio
from playwright.async_api import async_playwright

async def scrape_file_links(url):
    file_links = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)

            # Assuming files are linked directly in href attributes
            # We look for typical document file extensions
            link_elements = await page.query_selector_all('a[href*=".pdf"], a[href*=".docx"], a[href*=".xlsx"]')
            for element in link_elements:
                href = await element.get_attribute('href')
                if href:
                    file_links.append(href)
            
            await browser.close()
    except Exception as e:
        print(f"Error occurred: {e}")

    return file_links

async def main():
    url = 'https://www.pvh.com/investor-relations/financials'
    file_links = await scrape_file_links(url)
    print(file_links)

asyncio.run(main())

from utils.date_utils import accept_cookies, enable_stealth
import json
import asyncio
from playwright.async_api import async_playwright

class FlatListScraper:
    def __init__(self, base_url, output_file, selectors, pagination, defaults, cutoff_years_back):
        self.base_url = base_url
        self.output_file = output_file
        self.selectors = selectors
        self.pagination = pagination
        self.defaults = defaults
        self.cutoff_years_back = cutoff_years_back

    async def load_page(self, page, url):
        """Load the page based on the given URL."""
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await accept_cookies(page)  # Accept cookies if present
            await enable_stealth(page)   # Enable stealth mode to evade bot detection
            await asyncio.sleep(5)  # Ensure page content loads
        except Exception as e:
            print(f"⚠️ Error loading page: {e}")

    async def extract_data_from_page(self, page):
        """Extract data from the loaded page."""
        events = []

        # Get event blocks based on the generic selector
        event_blocks = await page.query_selector_all(self.selectors['event_block'])

        # Extract the HTML content of each event block
        for block in event_blocks:
            try:
                # Get the inner HTML of the event block
                event_html = await block.inner_html()

                # Add a separator after each event block
                events.append(event_html)

            except Exception as e:
                print(f"⚠️ Error extracting HTML from event block: {e}")

        return events

    
    # async def extract_text_from_element(self, block, selector):
    #     """Extract text from any tag within the block using the given selector."""
    #     try:
    #         # Look for the element and get its inner text, even if it's inside different tags
    #         element = await block.query_selector(selector)
    #         if element:
    #             return await element.inner_text()
    #         return "Unknown"  # If no text is found
    #     except Exception as e:
    #         print(f"⚠️ Error extracting text for {selector}: {e}")
    #         return "Unknown"

    # async def extract_links_from_element(self, block, selector):
    #     """Extract all the links from a block, based on the given selector."""
    #     links = []
    #     try:
    #         elements = await block.query_selector_all(selector)
    #         for element in elements:
    #             file_url = await element.get_attribute("href")
    #             if file_url:
    #                 absolute_url = ensure_absolute_url(self.base_url, file_url)
    #                 file_links = {
    #                     "url": absolute_url,
    #                     "file_name": await extract_file_name(absolute_url),
    #                     "file_type": get_file_type(absolute_url)
    #                 }
    #                 links.append(file_links)
    #     except Exception as e:
    #         print(f"⚠️ Error extracting links for {selector}: {e}")
    #     return links

    async def scrape(self):
        """Main function to scrape the data."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                print(f"🔍 Visiting: {self.base_url}")
                await self.load_page(page, self.base_url)

                # Extract data from the single page
                events = await self.extract_data_from_page(page)

                if events:
                    # Process and save events
                    with open(self.output_file, "w", encoding="utf-8") as f:
                        json.dump(events, f, indent=4)
                    print(f"\n✅ Data saved in: {self.output_file}")
                else:
                    print("\n❌ No events found.")
            
            except Exception as e:
                print(f"⚠️ Error: {e}")

            await browser.close()
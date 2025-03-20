from playwright.async_api import async_playwright
import json
import asyncio
import datetime

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
            await asyncio.sleep(5)  # Ensure page content loads
        except Exception as e:
            print(f"⚠️ Error loading page: {e}")

    async def extract_data_from_page(self, page):
        """Extract data from the loaded page."""
        events = []

        # Get event blocks based on the generic selector
        event_blocks = await page.query_selector_all(self.selectors['event_block'])

        for block in event_blocks:
            try:
                # Extract event name: Look for any tag inside the event block with the specified class
                event_name = await self.extract_text_from_element(block, self.selectors['event_name'])

                # Extract event date: Look for any tag inside the event block with the specified class
                event_date = await self.extract_text_from_element(block, self.selectors['event_date'])

                # Check if event is within the cutoff years
                event_year = self.get_event_year(event_date)
                if event_year and event_year < (datetime.now().year - self.cutoff_years_back):
                    print(f"🛑 Skipping: {event_name} (older than {self.cutoff_years_back} years)")
                    continue

                # Extract file links (webcast or other links)
                file_links = await self.extract_links_from_element(block, self.selectors['file_links'])

                # Append event to the result list
                events.append({
                    'event_name': event_name,
                    'event_date': event_date,
                    'file_links': file_links,
                    **self.defaults  # Add any default fields from config
                })

            except Exception as e:
                print(f"⚠️ Error extracting data from event block: {e}")

        return events

    async def extract_text_from_element(self, block, selector):
        """Extract text from any tag within the block using the given selector."""
        try:
            # Look for the element and get its inner text, even if it's inside different tags
            element = await block.query_selector(selector)
            if element:
                return await element.inner_text()
            return "Unknown"  # If no text is found
        except Exception as e:
            print(f"⚠️ Error extracting text for {selector}: {e}")
            return "Unknown"

    async def extract_links_from_element(self, block, selector):
        """Extract all the links from a block, based on the given selector."""
        links = []
        try:
            elements = await block.query_selector_all(selector)
            for element in elements:
                file_url = await element.get_attribute("href")
                if file_url:
                    links.append(file_url)
        except Exception as e:
            print(f"⚠️ Error extracting links for {selector}: {e}")
        return links

    def get_event_year(self, event_date):
        """Extract the year from the event date string, if possible."""
        try:
            # Assuming event_date is in format like "Sep 05, 2024"
            date_parts = event_date.split()
            if len(date_parts) > 1:  # Check if date has month, day, and year
                return int(date_parts[-1])  # Return the year part
            return None
        except Exception as e:
            print(f"⚠️ Error extracting year from event date: {event_date}")
            return None

    async def scrape(self):
        """Main function to scrape the data."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                print(f"🔍 Visiting: {self.base_url}")
                await self.load_page(page, self.base_url)

                events = await self.extract_data_from_page(page)
                print(events)
            #     if events:
            #         with open(self.output_file, "w", encoding="utf-8") as f:
            #             json.dump(events, f, indent=4)
            #         print(f"\n✅ Data saved in: {self.output_file}")
            #     else:
            #         print("\n❌ No events found.")
            
            except Exception as e:
                print(f"⚠️ Error: {e}")

            await browser.close()

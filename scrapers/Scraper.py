import json
import asyncio
from playwright.async_api import async_playwright
from utils.utils import accept_cookies, enable_stealth
from utils.outptut_event_JSON_to_file import output_event_JSON_to_file
import yaml
from scrapers.PaginationHandler import PaginationHandler

class Scraper:
    def __init__(self, utils_module, config_path):
        self.utils = utils_module
        self.pagination_handler = PaginationHandler()
        
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            self.config = next(iter(config.values()))

        self.base_url = self.config['url']
        self.base_address = self.config['base_address']
        self.output_file = self.config['output']
        self.output_json = self.config['output_json']
        self.selector = self.config['selectors']['event_block']
        self.pagination = self.config.get('pagination', {})
        self.ticker = self.config['ticker']
        self.geography = self.config['geography']
        self.periodicity = "periodic" if self.config['periodic'] == "true" else "non-periodic"

    async def _extract_inner_html(self, page, selector):
        print(f"🔍 Extracting blocks using selector: '{selector}'")
        blocks = await page.query_selector_all(selector)
        html_blocks = [await block.inner_html() for block in blocks if block]
        print(f"📦 Found {len(html_blocks)} blocks")
        return html_blocks

    async def extract_data_from_page(self, page):
        return await self._extract_inner_html(page, self.selector)

    async def load_page(self, page, url):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await accept_cookies(page)
            await enable_stealth(page)
            await page.wait_for_selector(self.selector, timeout=10000)
            await self.scroll_page(page)  # Scroll after loading

        except Exception as e:
            print(f"⚠️ Error loading page: {e}")
            
    async def scroll_page(self, page):
        """Scrolls to the bottom of the page to trigger lazy loading."""
        last_height = await page.evaluate("document.body.scrollHeight")

        while True:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(5)  # Allow time for loading

            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break  # Stop when no more content is loading
            last_height = new_height

        print("✅ Scrolling complete, all content loaded.")

    async def scrape(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            all_events = []
            page_num = 1

            try:
                print(f"🔍 Visiting: {self.base_url}")
                await self.load_page(page, self.base_url)
                print("✅ Page loaded")
                pag_type = self.pagination.get("type")
                selector = self.pagination.get("next_button")

                if pag_type == "year_tabs":
                    async for year_url in self.pagination_handler.navigate_to_years(page, self.base_url):
                        print(f"\n📄 Scraping year tab: {year_url}")
                        events = await self.extract_data_from_page(page)
                        all_events.extend(events)
                
                elif pag_type == "button" and selector:
                    while True:
                        print(f"\n📄 Scraping page {page_num}")
                        events = await self.extract_data_from_page(page)
                        all_events.extend(events)
                        print(f"✅ Scraped {len(events)} items from page {page_num}")

                        success = await self.pagination_handler.click_next_page(page, selector)
                        if not success:
                            print("✅ No more pages.")
                            break
                        page_num += 1

                elif pag_type == "load_more":
                    load_selector = self.pagination.get("load_more_button")
                    if load_selector:
                        await self.pagination_handler.click_load_more(page, load_selector)
                    events = await self.extract_data_from_page(page)
                    all_events.extend(events)
                elif pag_type == "next_page_url":
                    while True:
                        print(f"\n📄 Scraping page {page_num}")
                        events = await self.extract_data_from_page(page)
                        all_events.extend(events)
                        print(f"✅ Scraped {len(events)} items from page {page_num}")

                        success = await self.pagination_handler.find_and_navigate_next_page(page, self.base_url)
                        if not success:
                            print("✅ No more pages.")
                            break
                        page_num += 1
                else:
                    print("\n📄 Scraping single page")
                    events = await self.extract_data_from_page(page)
                    all_events.extend(events)

                if all_events:
                    print("sdjfksdjfksdjf")
                    with open(self.output_file, "w", encoding="utf-8") as f:
                        json.dump(all_events, f, indent=4)
                    print(f"\n✅ Data saved in: {self.output_file}")
                    
                    await output_event_JSON_to_file(
                        input_json_file=self.output_file,
                        output_json_file=self.output_json,
                        equity_ticker=self.ticker,
                        geography=self.geography,
                        periodicity=self.periodicity,
                        base_url = self.base_address
                        )
                else:
                    print("\n❌ No events found.")

            except Exception as e:
                print(f"⚠️ Error: {e}")

            await browser.close()

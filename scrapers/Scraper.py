import json
import asyncio
from playwright.async_api import async_playwright
from utils.utils import accept_cookies, enable_stealth
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
        self.output_file = self.config['output']
        self.selector = self.config['selectors']['event_block']
        self.pagination = self.config.get('pagination', {})

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
            await asyncio.sleep(3)
        except Exception as e:
            print(f"⚠️ Error loading page: {e}")

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

                pag_type = self.pagination.get("type")
                selector = self.pagination.get("next_button")

                if pag_type == "year_tabs":
                    years = self.pagination.get("years", [])
                    template = self.pagination.get("selector_template")
                    if years and template:
                        async for _ in self.pagination_handler.switch_year_tabs(page, years, template):
                            print(f"\n📄 Scraping year tab")
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

                else:
                    print("\n📄 Scraping single page")
                    events = await self.extract_data_from_page(page)
                    all_events.extend(events)

                if all_events:
                    with open(self.output_file, "w", encoding="utf-8") as f:
                        json.dump(all_events, f, indent=4)
                    print(f"\n✅ Data saved in: {self.output_file}")
                else:
                    print("\n❌ No events found.")

            except Exception as e:
                print(f"⚠️ Error: {e}")

            await browser.close()

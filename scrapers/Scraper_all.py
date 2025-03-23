import json
import asyncio
from playwright.async_api import async_playwright
from utils.utils import accept_cookies, enable_stealth, download_file, join_url
import yaml
from scrapers.PaginationHandler import PaginationHandler
from scrapers.llm_all import llm_all
from utils.create_event import create_event 
from utils.create_file_metadata import create_file_metadata
from utils.upload_to_r2 import upload_file_to_r2
from utils.get_content_type_from_element import get_content_type_from_element

class Scraper:
    def __init__(self, utils_module, config_path, page):
        self.utils = utils_module
        self.pagination_handler = PaginationHandler()

        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            # self.config = next(iter(config.values()))

        self.config = config[page]        

        self.base_url = self.config['url']
        self.output_file = self.config['output']
        self.selector = self.config['selectors']['event_block']
        self.selector_all = self.config['selectors']['parent_event_block']
        self.periodic = self.config['periodic']
        self.ticker = self.config['ticker']
        self.geography = self.config['geography']
        self.category = self.config['']
        # print(self.selector_all)
        self.pagination = self.config.get('pagination', {})

    async def _extract_inner_html(self, page, selector):
        print(f"🔍 Extracting blocks using selector: '{selector}'")
        block = await page.query_selector(selector)
        event_list = []
        if block:
            html_block = await block.inner_html()
            events = llm_all(html_block)
            for event in events:
                if (self.periodic) == True:
                    pass
                else:
                    event_name = event['event_name']
                    date = event['date']
                    equity_ticker = self.ticker
                    geography = self.geography
                    periodicity = 'non_periodic_event'
                    # data = []
                    hrefs = event['files']
                    for href in hrefs:
                        url = join_url(self.base_url, href)
                        if url is not None:
                            file_path, file_name, file_type = download_file(url)
                            if file_path is not None:
                                r2_url = upload_file_to_r2(file_path, f"{equity_ticker}/{date}/{file_name}/{file_name}")
                                if r2_url is not None:
                                    categories = get_content_type_from_element(event_name, )
                                    create_file_metadata(file_name, file_type, date, r2_url)


                        

                


            return events
        else:
            print("⚠️ No blocks found")
            return None

    async def extract_data_from_page(self, page):
        return await self._extract_inner_html(page, self.selector_all)

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
                        print('fsdj,fjsdklfjsdklfjdksljfklsdjfklsdjfkldsjfksdjfkldsjflksdjflksdjflkdsjflksdjflksdjfklds')
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
                    with open(self.output_file, "w", encoding="utf-8") as f:
                        json.dump(all_events, f, indent=4)
                    print(f"\n✅ Data saved in: {self.output_file}")
                else:
                    print("\n❌ No events found.")

            except Exception as e:
                print(f"⚠️ Error: {e}")

            await browser.close()

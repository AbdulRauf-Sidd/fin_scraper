import json
import asyncio
from playwright.async_api import async_playwright
from utils.utils import accept_cookies, enable_stealth

class Scraper:
    def __init__(self, utils_module, base_url=None, output_file=None):
        self.utils = utils_module
        self.base_url = base_url
        self.output_file = output_file

    async def extract_t_row_events(self, page, selector="div.t-row"):
        return await self._extract_inner_html(page, selector)

    async def extract_content_container(self, page, selector="div.row.content__container"):
        return await self._extract_inner_html(page, selector)

    async def extract_uol_cards(self, page, selector=".uol-c-card__content"):
        return await self._extract_inner_html(page, selector)

    async def extract_rl_corp_news(self, page, selector=".corp-news"):
        return await self._extract_inner_html(page, selector)

    async def extract_wd_event_info(self, page, selector=".wd_event_info"):
        return await self._extract_inner_html(page, selector)

    async def extract_wd_press_items(self, page, selector=".wd_item"):
        return await self._extract_inner_html(page, selector)

    async def extract_sec_filings_table(self, page, selector="table tbody tr"):
        return await self._extract_inner_html(page, selector)

    async def extract_static_grid_quarters(self, page, selector=".box.quarterly-results"):
        return await self._extract_inner_html(page, selector)

    async def extract_governance_assets(self, page, selector="div.module-asset-list .asset"):
        return await self._extract_inner_html(page, selector)

    async def extract_list_events_items(self, page, selector="#archiveEvents .ListEvents-items-item"):
        return await self._extract_inner_html(page, selector)

    async def extract_search_result_cards(self, page, selector="li.in-page__card.search-result-tag"):
        return await self._extract_inner_html(page, selector)

    async def _extract_inner_html(self, page, selector):
        blocks = await page.query_selector_all(selector)
        html_blocks = [await block.inner_html() for block in blocks if block]
        return html_blocks

    async def load_page(self, page, url):
        """Load the page based on the given URL."""
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await accept_cookies(page)  # Accept cookies if present
            await enable_stealth(page)  # Enable stealth mode to evade bot detection
            await asyncio.sleep(5)  # Ensure page content loads
        except Exception as e:
            print(f"⚠️ Error loading page: {e}")

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

    async def extract_data_from_page(self, page):
        """Override this method to extract and return structured data from the page."""
        raise NotImplementedError("You must implement 'extract_data_from_page' in a subclass or assign it dynamically.")

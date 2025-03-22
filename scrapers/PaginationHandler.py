import asyncio
from urllib.parse import urljoin

class PaginationHandler:
    async def click_load_more(self, page, selector):
        """Clicks 'Load More' until it disappears."""
        while True:
            try:
                button = await page.query_selector(selector)
                if not button:
                    break
                await button.click()
                await asyncio.sleep(2)
            except Exception:
                break

    async def click_next_page(self, page, next_button_selector):
        """Clicks 'Next Page' button using aria-label or class."""
        try:
            button = await page.query_selector(next_button_selector)
            if button:
                await button.click()
                await asyncio.sleep(2)
                return True
        except Exception:
            pass
        return False

    async def switch_year_tabs(self, page, year_list, selector_template):
        """
        Clicks on each year filter button.
        selector_template = ".tab-titles a[href*='year={year}']"
        """
        for year in year_list:
            try:
                selector = selector_template.format(year=year)
                button = await page.query_selector(selector)
                if button:
                    await button.click()
                    await asyncio.sleep(3)
                    yield year  # Let scraper call the extraction logic
            except Exception:
                continue

    async def handle_multiple_page_urls(self, page, base_url, subpage_selector):
        """Finds page URLs (e.g. index.php?...) and returns all unique URLs."""
        pagination_urls = set()
        links = await page.query_selector_all(subpage_selector)
        for link in links:
            href = await link.get_attribute("href")
            if href and "index.php" in href:
                pagination_urls.add(urljoin(base_url, href))
        return list(pagination_urls)

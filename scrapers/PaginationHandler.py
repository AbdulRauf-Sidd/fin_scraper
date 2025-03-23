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
    
    async def click_paginated_button(self, page, next_button_selector):
        """Clicks the 'Next Page' button while it remains enabled."""
        while True:
            try:
                button = await page.query_selector(next_button_selector)
                if not button:
                    print("✅ No 'Next Page' button found or it is disabled.")
                    break  # Exit if button is not found
                
                button_disabled = await button.get_attribute("class")
                if "v-pagination__navigation--disabled" in button_disabled:
                    print("✅ Pagination complete, next button is disabled.")
                    break  # Exit if button is disabled
                
                print("🔄 Clicking 'Next Page' button...")
                await button.click()
                await asyncio.sleep(2)  # Allow new page to load
            except Exception as e:
                print(f"⚠️ Error clicking pagination button: {e}")
                break  # Stop pagination on error
    
    async def find_and_navigate_next_page(self, page, base_url):
        """Finds the next page URL and navigates to it."""
        try:
            await page.wait_for_selector("a", timeout=5000)
            all_links = await page.query_selector_all("a")
            for link in all_links:
                text = await link.inner_text()
                if "Next" in text or ">" in text:
                    next_page_url = await link.get_attribute("href")
                    if next_page_url:
                        full_url = urljoin(base_url, next_page_url)
                        print(f"🔄 Navigating to next page: {full_url}")
                        await page.goto(full_url, wait_until="domcontentloaded")
                        return True
        except Exception as e:
            print(f"⚠️ Error finding next page: {e}")
        return False
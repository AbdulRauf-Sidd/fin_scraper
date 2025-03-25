import asyncio
from urllib.parse import urljoin

class PaginationHandler:
    async def click_load_more(self, page, selector, event_selector):
        """Clicks 'Load More' until it disappears."""
        while True:
            try:
                button = await page.query_selector(selector)
                if not button:
                    print("✅ No 'Load More' button found.")
                    break  # Exit loop if no button exists
                
                print("🔘 Found 'Load More' button, clicking...")
                await button.click()
                await asyncio.sleep(10)  # Small delay to allow click effect
    
                # Check if button gets removed
                button_after_click = await page.query_selector(selector)
                if not button_after_click:
                    print("✅ 'Load More' button disappeared after clicking.")
    
                # previous_count = len(await page.query_selector_all(event_selector))
                # print(f"📊 Previous items count: {previous_count}")
    
                # max_wait_time = 10
                # elapsed_time = 0
    
                # while elapsed_time < max_wait_time:
                    # await asyncio.sleep(1)
                    # elapsed_time += 1
                    
                    # current_count = len(await page.query_selector_all(event_selector))
                    # print(f"🔄 Checking for new content... Current count: {current_count}")
    
                    # if current_count > previous_count:
                        # print(f"✅ Loaded {current_count - previous_count} new items.")
                        # break  # New content detected, stop waiting
                    
                # if elapsed_time >= max_wait_time:
                    # print("⚠️ Timed out waiting for new content to load.")
    
            except Exception as e:
                print(f"❌ Error in click_load_more: {e}")
                break

    async def click_next_page(self, page, next_button_selector):
        """Clicks 'Next Page' button using aria-label or class."""
        try:
            button = await page.query_selector(next_button_selector)
            if button and await button.is_visible():
                await button.click()
                await asyncio.sleep(2)
                return True
        except Exception:
            pass
        return False

    async def switch_all_tabs(self, page, tab_selector, extract_function, timeout=None, archive_class=None):
        """Switches through all tabs without scraping, handling potential blockers."""
        # Handle consent banner if present
        try:
            consent_button = await page.query_selector("#onetrust-accept-btn-handler")
            if consent_button:
                print("✅ Accepting cookie consent...")
                await consent_button.click()
                await page.wait_for_timeout(1000)  # Small delay to ensure it disappears
        except Exception as e:
            print(f"⚠️ Consent banner not found or error: {e}")

        all_events = []

        # Select all tab elements
        tabs = await page.query_selector_all(tab_selector)

        tabs = await page.query_selector_all(tab_selector)
        num_tabs = len(tabs)

        for i in range(num_tabs):
            tabs = await page.query_selector_all(tab_selector)  # Re-query to avoid stale references
            if i >= len(tabs):  # Check if tabs list is shorter than expected
                break
            
            if archive_class:
                try:
                    archive_tab = await page.query_selector(archive_class) # Modify selector as needed
                    if archive_tab:
                        print("Clicking on the 'archive' tab...")
                        await archive_tab.click()
                        await asyncio.sleep(5)  # Wait for the DOM to update after clicking the 'archive' tab
                except Exception as e:
                    print(f"⚠️ Error accessing 'archive' tab: {e}")
            
            tab = tabs[i]
            year = await tab.inner_text()
            print('Processing tab:', year)

            class_attr = await tab.get_attribute("class") or ""
            if "active" in class_attr:
                print(f"Skipping active tab: {year}")
                continue

            print(f"Switching to tab: {year}")

            try:
                # Click the tab
                await tab.click(force=True)  # `force=True` bypasses overlays if possible
                
                if timeout:
                    await asyncio.sleep(timeout)  # Wait for the DOM to update

                event = await extract_function(page)
                all_events.extend(event)

                # Wait for new content to load (adjust selector)
                await page.wait_for_selector("div.t-table", timeout=5000)

            except Exception as e:
                print(f"⚠️ Error switching to {year}: {e}")
        return all_events

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
    
    async def find_and_navigate_next_page(self, page, base_url, next_button_selector):
        """Finds the next page URL and navigates to it."""
        try:
            await page.wait_for_selector("a", timeout=10000)
            all_links = await page.query_selector_all(next_button_selector)
            for link in all_links:
                text = await link.inner_text()
                if "Next" in text or ">" in text or "next" in text:
                    next_page_url = await link.get_attribute("href")
                    if next_page_url:
                        full_url = urljoin(base_url, next_page_url)
                        print(f"🔄 Navigating to next page: {full_url}")
                        await page.goto(full_url, wait_until="domcontentloaded")
                        return True
        except Exception as e:
            print(f"⚠️ Error finding next page: {e}")
        return False
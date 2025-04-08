import asyncio
from urllib.parse import urljoin

class PaginationHandler:
    async def click_load_more(self, page, selector):
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
    
    async def click_more(self, page):
        """Scrolls to and clicks elements containing 'load more', 'load', or 'more' in their text."""
        try:
            # Search for all clickable elements
            buttons = await page.query_selector_all('button, a, div')  # Searching common clickable elements
            for button in buttons:
                # text_content = await button.inner_text() 
                text_content = await button.evaluate('node => node.innerText') # Get the full text content as a single string
                print('abc', text_content)
                # Check if any of the keywords are found in the text (case insensitive)
                if text_content and any(keyword in text_content.lower() for keyword in ['load more', 'load', 'more']):
                    print(f"🔘 Found button with text: {text_content}")
                    if await button.is_visible():
                        # Scroll the element into view if it's not already visible
                        await button.scroll_into_view_if_needed()
                        # Click the button
                        await button.click()
                        await asyncio.sleep(2)
                        return True
        except Exception as e:
            print(f"Error: {e}")

        return False


    async def switch_all_tabs(self, page, tab_selector, extract_function, timeout=None, archive_class=None, selector=None):
        """Switches through all tabs without scraping, handling potential blockers."""
        all_events = []
        # Handle consent banner if present
        try:
            consent_button = await page.query_selector("#onetrust-accept-btn-handler")
            if consent_button:
                print("✅ Accepting cookie consent...")
                await consent_button.click()
                await page.wait_for_timeout(1000)  # Small delay to ensure it disappears
        except Exception as e:
            print(f"⚠️ Consent banner not found or error: {e}")

        # await self.click_more(page)


        if archive_class:
            try:
                archive_tab = await page.query_selector(archive_class) # Modify selector as needed
                if archive_tab:
                    print("Clicking on the 'archive' tab...")
                    await archive_tab.click()
                    await asyncio.sleep(5)  # Wait for the DOM to update after clicking the 'archive' tab
            except Exception as e:
                print(f"⚠️ Error accessing 'archive' tab: {e}")
    
        # Select all tab elements
        tabs = await page.query_selector_all(tab_selector)
        num_tabs = len(tabs)

        for i in range(num_tabs):
            # Re-query the tabs and select the i-th tab each time
            # await self.click_more(page)
            if archive_class:
                try:
                    archive_tab = await page.query_selector(archive_class) # Modify selector as needed
                    if archive_tab:
                        print("Clicking on the 'archive' tab...")
                        await archive_tab.click()
                        await asyncio.sleep(5)  # Wait for the DOM to update after clicking the 'archive' tab
                except Exception as e:
                    print(f"⚠️ Error accessing 'archive' tab: {e}")

            tabs = await page.query_selector_all(tab_selector)
            tab = tabs[i]
            year = await tab.inner_text()
            print('Processing tab:', year)

            # Check if the tab is already active
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

                # Wait for new content to load (adjust selector)
                await page.wait_for_selector(selector, timeout=5000)

                event = await extract_function(page)
                all_events.extend(event)

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
    
    async def click_expandable_containers(self, page, expand_button_selector):
        """
        Clicks all unexpanded accordion buttons to reveal hidden content.
        Avoids clicking already expanded buttons by checking 'aria-expanded'.
        """
        try:
            buttons = await page.query_selector_all(expand_button_selector)
            print(f"🔘 Found {len(buttons)} expandable containers.")
    
            clicked = 0
            for button in buttons:
                if await button.is_visible():
                    expanded = await button.get_attribute("aria-expanded")
                    if expanded == "false":
                        try:
                            await button.click()
                            await asyncio.sleep(1.5)  # wait for content animation
                            clicked += 1
                        except Exception as e:
                            print(f"⚠️ Failed to click: {e}")
                    else:
                        print("↪️ Already expanded, skipping...")
    
            if clicked == 0:
                print("⚠️ No unexpanded containers were clicked.")
            else:
                print(f"✅ Clicked and expanded {clicked} containers.")
    
            return clicked > 0
    
        except Exception as e:
            print(f"❌ Error in click_expandable_containers: {e}")
            return False
        
    async def scroll_page_until_end(self, page):
        """Scroll the page until no more content is loaded."""
        last_height = await page.evaluate("document.body.scrollHeight")  # Get the initial page height

        while True:
            # Scroll down to the bottom of the page
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # Wait for new content to load (this might vary depending on your page's loading mechanism)
            await asyncio.sleep(2)  # Adjust this based on how long the page needs to load the new content

            # Check the new height of the page
            new_height = await page.evaluate("document.body.scrollHeight")

            # If the height hasn't changed, we assume there's no more content to load
            if new_height == last_height:
                print("✅ No more content to load.")
                break
            
            # Update the last height to the new height
            last_height = new_height

            print("🔄 Scrolling...")

        print("✅ Scrolling finished.")
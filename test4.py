import os
import logging
from playwright.async_api import async_playwright
import asyncio

async def capture_full_page_screenshot(url, base_url="https://www.sec.gov", headless=True):
    url = url.rstrip('/')
    file_name = url.split("/")[-1] + ".png"

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Capturing screenshot from: {url}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()

            # Navigate to the URL
            logging.info(f"Opening page: {url}")
            await page.goto(url)
            await page.wait_for_load_state('load')
            await asyncio.sleep(2)  # Adjust sleep time as necessary

            # Create downloads directory if it does not exist
            os.makedirs('downloads', exist_ok=True)
            file_path = os.path.join('downloads', file_name)

            # Take a full page screenshot
            logging.info("Taking full page screenshot...")
            await page.screenshot(path=file_path, full_page=True)

            absolute_path = os.path.abspath(file_path)
            logging.info(f"Saved screenshot: {absolute_path}")
            return absolute_path, file_name
    except Exception as e:
        logging.error(f"Error capturing screenshot: {e}")
        return None, None



asyncio.run(capture_full_page_screenshot(url='https://www.pvh.com/news/press-releases/PVH-Corp-to-Host-Conference-Call-to-Discuss-Fourth-Quarter-and-YearEnd-2024-Earnings-Results', headless=False, base_url='https://www.pvh.com'))
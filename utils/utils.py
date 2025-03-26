import re
from datetime import datetime
import asyncio
from urllib.parse import urlparse
import os
import mimetypes
import requests
import time 
from playwright.async_api import async_playwright
import csv
import sys
import importlib
from pathlib import Path
from urllib.parse import urljoin, urlparse
# from utils.is_bad_link import is_bad_link


async def accept_cookies(page):
    """Accepts cookies if a consent banner appears."""
    try:
        cookie_button = await page.query_selector("button:has-text('Accept')")
        if cookie_button:
            await cookie_button.click()
            await asyncio.sleep(2)  # Wait to ensure banner disappears
            print("✅ Accepted cookies.")
    except Exception as e:
        print(f"⚠️ No cookie consent banner found or error clicking it: {e}")

async def enable_stealth(page):
    """Inject JavaScript to evade bot detection."""
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    ###############################################
    # UNCOMMENT IF NEW IMPLEMENTATION DOESN'T WORK
    ###############################################
# def download_file(url, download_folder):
#     """Download a file from the given URL and save it to the specified folder.
    
#     Returns:
#         file_path (str): The full path of the downloaded file.
#         filename (str): The name of the file.
#         file_type (str): The file extension (e.g., "pdf", "docx").
#     """
#     filename = os.path.basename(url)
#     file_path = os.path.join(download_folder, filename)

#     # Ensure the folder exists
#     os.makedirs(download_folder, exist_ok=True)

#     attempts = 0
#     while attempts < 3:
#         try:
#             print(f"🔍 Attempt {attempts + 1}: Downloading {url}")

#             # Download the file
#             response = requests.get(url, timeout=10)  # Added timeout for reliability
#             print(f"📡 Response Status: {response.status_code}")

#             if response.status_code == 200:
#                 with open(file_path, 'wb') as f:
#                     f.write(response.content)
#                 print(f"✅ Successfully downloaded: {file_path}")

#                 # Get file type from response headers or infer from filename
#                 file_type = response.headers.get('Content-Type')
#                 print(f"📄 Detected MIME Type: {file_type}")

#                 if file_type:
#                     file_extension = mimetypes.guess_extension(file_type)
#                     if file_extension:
#                         file_type = file_extension.lstrip(".")  # Convert ".pdf" -> "pdf"
#                     else:
#                         file_type = 'html'
#                 else:
#                     file_type = os.path.splitext(filename)[1].lstrip(".")  # Extract from filename

#                 print(f"🗂️ Final File Type: {file_type}")
#                 return file_path, filename, file_type
            
#             else:
#                 print(f"⚠️ Failed to download {url}, HTTP Status: {response.status_code}")
#                 return None, None, None

#         except requests.RequestException as e:
#             attempts += 1
#             print(f"❌ Attempt {attempts}: Request error - {str(e)}")
#             if attempts < 3:
#                 print("🔄 Retrying in 5 seconds...")
#                 time.sleep(5)
#             else:
#                 print("⛔ Maximum retry attempts reached, failed to download.")
#                 return None, None, None

async def download_file(url, output_folder="downloads"):
    """
    Returns:
        file_path (str): The full path of the downloaded file.
        filename (str): The name of the file.
        file_type (str): The file extension (e.g., "pdf", "docx").
    """
    url = url.rstrip('/')
    filename = os.path.basename(url)
    file_path = Path(output_folder) / filename
    abs_path = str(file_path.resolve())

    # Ensure the folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Check for bad link
    # # is_bad_link = await is_bad_link(url)
    # if is_bad_link:
    #     print(f"⛔ Bad link detected: {url}")
    #     return None, None, None

    print(f"🔍 Visiting: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.sec.gov/",
                }
            )
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded")

            content = await page.content()
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)

            await browser.close()
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return None, None, None

    print(f"✅ Successfully downloaded: {abs_path}")

    # Determine file type
    mime_type, _ = mimetypes.guess_type(abs_path)
    if mime_type:
        ext = mimetypes.guess_extension(mime_type)
        file_type = ext.lstrip(".") if ext else file_path.suffix.lstrip(".")
    else:
        file_type = file_path.suffix.lstrip(".")

    print(f"📄 Detected MIME Type: {mime_type}")
    print(f"🗂️ Final File Type: {file_type}")

    return abs_path, filename, file_type

def join_url(base_url, href):
    if href is None:
        return None
    # Check if the href is already an absolute URL
    if urlparse(href).scheme:
        return href  # Return the href directly as it's already absolute
    
    # Otherwise, join the base_url with the href
    return urljoin(base_url, href)


asyncio.run(download_file('https://www.kering.com/en/news/kering-and-les-rencontres-d-arles-to-present-the-2025-women-in-motion-award-for-photography-to-nan-goldin/'))

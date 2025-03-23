import re
from datetime import datetime
import asyncio
from urllib.parse import urlparse
import os
import mimetypes
import requests

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
    
def download_file(url, download_folder):
    """Download a file from the given URL and save it to the specified folder.
    
    Returns:
        file_path (str): The full path of the downloaded file.
        filename (str): The name of the file.
        file_type (str): The file extension (e.g., "pdf", "docx").
    """
    filename = os.path.basename(url)
    file_path = os.path.join(download_folder, filename)

    # Ensure the folder exists
    os.makedirs(download_folder, exist_ok=True)

    # Download the file
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {file_path}")

        # Get file type from response headers or infer from filename
        file_type = response.headers.get('Content-Type')
        if file_type:
            file_extension = mimetypes.guess_extension(file_type)
            if file_extension:
                file_type = file_extension.lstrip(".")  # Convert ".pdf" -> "pdf"
            else:
                file_type = None
        else:
            file_type = os.path.splitext(filename)[1].lstrip(".")  # Extract from filename

        return file_path, filename, file_type
    else:
        print(f"Failed to download: {url}")
        return None, None, None  # Return None values if download fails
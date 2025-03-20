import re
from datetime import datetime
import asyncio
from urllib.parse import urlparse
import os
from dateutil.parser import parse


async def parse_date(date_str):
    """Parse various datetime formats to return only the date in a standardized format."""
    try:
        # Clean up the string by removing unexpected or unrecognized parts
        date_str = date_str.strip()

        # If the date has an invalid month number (like '96'), remove it
        date_str = re.sub(r'(\d{4})\s(\d{2,3})', '', date_str)  # Removing "96" or other unexpected parts

        # Remove "DT", "ST", or other invalid time zone information
        date_str = re.sub(r'\s?[A-Za-z]{2,3}\s?\d*[\s/]*', '', date_str)  # Strip time zone like "DT", "ST", etc.

        # If the string has incomplete date parts like ", 2025" or similar, remove those
        if not re.search(r"\d{1,2},\s?\d{4}", date_str):
            print(f"⚠️ Invalid or incomplete date: {date_str}")
            return None

        # Try parsing the cleaned-up date string using dateutil.parser.parse
        parsed_date = parse(date_str, fuzzy=True)

        # Return the date only (no time)
        return parsed_date.date()
    except Exception as e:
        print(f"⚠️ Error parsing date: {date_str}, Error: {e}")
        return None

async def extract_file_name(file_url):
    """Extracts the file name from a given URL."""
    parsed_url = urlparse(file_url)
    return os.path.basename(parsed_url.path)


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


def get_file_type(url: str) -> str:
    """
    Extracts the file type from a URL.
    
    Recognized types:
    - pdf
    - csv
    - xlsx
    - mp4
    - etv
    - html (default)
    """

    url = url.lower()

    file_patterns = {
        "pdf": r"\.pdf(\?|$)",
        "csv": r"\.csv(\?|$)",
        "xlsx": r"\.xlsx(\?|$)|\.xls(\?|$)",  # Covers .xls and .xlsx
        "mp4": r"\.mp4(\?|$)",
        "etv": r"\.etv(\?|$)",
        "zip": r"\.zip(\?|$)",
        "htm": r"\.htm(\?|$)"
    }

    for file_type, pattern in file_patterns.items():
        if re.search(pattern, url):
            return file_type

    return "html"

def ensure_absolute_url(base_url, url):
    from urllib.parse import urljoin

    # Check if the URL is already absolute
    if url.startswith('http'):
        return url
    else:
        # Combine the base URL with the relative URL to create an absolute URL
        return urljoin(base_url, url)
    
async def enable_stealth(page):
    """Inject JavaScript to evade bot detection."""
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

import re
import json
import os
from urllib.parse import urljoin

def save_json(data, filename):
    file_mode = 'a' if os.path.exists(filename) else 'w'
    with open(filename, file_mode) as f:
        if file_mode == 'a':  # File exists, append to it
            f.seek(0, os.SEEK_END)  # Seek to end of file
            f.seek(f.tell() - 1, os.SEEK_SET)  # Go back one character from the end
            f.truncate()  # Remove the last character (should be a closing bracket ])
            f.write(',\n')  # Prepare for new JSON object
            json.dump(data, f)
            f.write(']')
        else:  # File does not exist, create new
            json.dump([data], f)  # Write data as a list of JSON objects

def classify_frequency(event_name, file_name):
    # Define a regex pattern that matches the keywords indicating a periodic event
    periodic_keywords = r'\b(annual|quarterly|quarter|Q[1234])\b'
    
    # Check if the keywords are in the event name or file name
    if re.search(periodic_keywords, event_name, re.IGNORECASE) or re.search(periodic_keywords, file_name, re.IGNORECASE):
        return "periodic"
    else:
        return "non-periodic"
    
def ensure_absolute_url(base_url, url):
    from urllib.parse import urljoin

    # Check if the URL is already absolute
    if url.startswith('http'):
        return url
    else:
        # Combine the base URL with the relative URL to create an absolute URL
        return urljoin(base_url, url)

async def KO_close_cookie_consent(page):
    # Check if the cookie consent form is visible
    cookie_consent_selector = "#onetrust-pc-sdk"
    close_button_selector = "#close-pc-btn-handler"
    try:
        # Wait for the cookie consent form to appear (up to 5 seconds)
        cookie_consent = await page.wait_for_selector(cookie_consent_selector, state="attached", timeout=5000)
        if cookie_consent:
            print("Cookie consent form found. Attempting to close...")
            await page.click(close_button_selector)
            print("Cookie consent form closed.")
        else:
            print("No cookie consent form found.")
    except Exception as e:
        print(f"No cookie consent form to close or an error occurred: {str(e)}")